## OS_LAB4

### 分配并初始化一个进程控制块

内核线程是一种特殊的进程，内核线程与用户进程的区别有两个：

- 内核线程只运行在内核态，而用户进程会在在用户态和内核态交替运行；
- 所有内核线程直接使用共同 `ucore` 内核内存空间，不需为每个内核线程维护单独的内存空间，而用户进程需要维护各自的用户内存空间。

一个内核线程的 PCB，它通常只是内核中的一小段代码或者函数，没有用户空间。而由于在操作系统启动后，已经对整个核心内存空间进行了管理，通过设置页表建立了核心虚拟空间(即 boot_cr3 指向的二级页表描述的空间)。所以内核中的所有线程都不需要再建立各自的页表，只需共享这个核心虚拟空间就可以访问整个物理内存了。

在 `kern/process/proc.h` 中定义了 `PCB`，即进程控制块的结构体 `proc_struct`，如下：

```c
struct proc_struct {             //进程控制块PCB
    enum proc_state state;       //进程状态
    int pid;                     //进程ID
    int runs;                    //运行时间
    uintptr_t kstack;            //内核栈位置
    volatile bool need_resched;  //是否需要调度
    struct proc_struct *parent;  //父进程
    struct mm_struct *mm;        //进程的虚拟内存
    struct context context;      //进程上下文
    struct trapframe *tf;        //当前中断帧的指针
    uintptr_t cr3;               //当前页表地址
    uint32_t flags;              //进程
    char name[PROC_NAME_LEN + 1];//进程名字
    list_entry_t list_link;      //进程链表       
    list_entry_t hash_link;      //进程哈希表            
};

static struct proc_struct *alloc_proc(void) {
    struct proc_struct *proc = kmalloc(sizeof(struct proc_struct));
    if (proc != NULL) {
        proc->state = PROC_UNINIT;  //设置进程为未初始化状态
        proc->pid = -1;             //未初始化的的进程id为-1
        proc->runs = 0;             //初始化时间片
        proc->kstack = 0;           //内存栈的地址
        proc->need_resched = 0;     //是否需要调度设为不需要
        proc->parent = NULL;        //父节点设为空
        proc->mm = NULL;            //虚拟内存设为空
        memset(&(proc->context), 0, sizeof(struct context));//上下文的初始化
        proc->tf = NULL;            //中断帧指针置为空
        proc->cr3 = boot_cr3;       //页目录设为内核页目录表的基址
        proc->flags = 0;            //标志位
        memset(proc->name, 0, PROC_NAME_LEN);//进程名
    }
    return proc;
}
```

`struct context context` 和 `struct trapframe *tf` 成员变量含义和在本实验中的作用

```c
// 在 context 中保存着各种寄存器的内容，主要保存了前一个进程的现场（各个寄存器的状态），是进程切换的上下文内容，这是为了保存进程上下文，用于进程切换，为进程调度做准备。
/*code*/
struct context {
    uint32_t eip;
    uint32_t esp;
    uint32_t ebx;
    uint32_t ecx;
    uint32_t edx;
    uint32_t esi;
    uint32_t edi;
    uint32_t ebp;
};

/* tf 变量的作用在于在构造出了新的线程的时候，如果要将控制权交给这个线程，是使用中断返回的方式进行的（跟lab1中切换特权级类似的技巧），因此需要构造出一个伪造的中断返回现场，也就是 trapframe，使得可以正确地将控制权转交给新的线程；

* 调用switch_to函数。
* 然后在该函数中进行函数返回，直接跳转到 forkret 函数。
* 最终进行中断返回函数 __trapret，之后便可以根据 tf 中构造的中断返回地址，切换到新的线程了。

trapframe 保存着用于特权级转换的栈 esp 寄存器，当进程发生特权级转换的时候，中断帧记录了进入中断时任务的上下文。当退出中断时恢复环境。

tf 是一个中断帧的指针，总是指向内核栈的某个位置：
* 当进程从用户空间跳到内核空间时，中断帧记录了进程在被中断前的状态。
* 当内核需要跳回用户空间时，需要调整中断帧以恢复让进程继续执行的各寄存器值。
* 除此之外，ucore 内核允许嵌套中断，因此为了保证嵌套中断发生时 tf 总是能够指向当前的 trapframe，ucore 在内核栈上维护了 tf 的链。
*/ 

/*code*/
struct trapframe {
    struct pushregs {
        uint32_t reg_edi;
        uint32_t reg_esi;
        uint32_t reg_ebp;
        uint32_t reg_oesp;          /* Useless */
        uint32_t reg_ebx;
        uint32_t reg_edx;
        uint32_t reg_ecx;
        uint32_t reg_eax;
    };
    uint16_t tf_gs;
    uint16_t tf_padding0;
    uint16_t tf_fs;
    uint16_t tf_padding1;
    uint16_t tf_es;
    uint16_t tf_padding2;
    uint16_t tf_ds;
    uint16_t tf_padding3;
    uint32_t tf_trapno;
    /* below here defined by x86 hardware */
    uint32_t tf_err;
    uintptr_t tf_eip;
    uint16_t tf_cs;
    uint16_t tf_padding4;
    uint32_t tf_eflags;
    /* below here only when crossing rings, such as from user to kernel */
    uintptr_t tf_esp;
    uint16_t tf_ss;
    uint16_t tf_padding5;
} __attribute__((packed));
```



### 为新创建的内核线程分配资源

- 分配并初始化进程控制块（ alloc_proc 函数）;
- 分配并初始化内核栈，为内核进程（线程）建立栈空间（ setup_stack 函数）;
- 根据 clone_flag 标志复制或共享进程内存管理结构（ copy_mm 函数）;
- 设置进程在内核（将来也包括用户态）正常运行和调度所需的中断帧和执行上下文 （ copy_thread 函数）;
- 为进程分配一个 PID（ get_pid() 函数）;
- 把设置好的进程控制块放入 hash_list 和 proc_list 两个全局进程链表中;
- 自此，进程已经准备好执行了，把进程状态设置为“就绪”态;
- 设置返回码为子进程的 PID 号。

```c
/* do_fork -     parent process for a new child process
 * @clone_flags: used to guide how to clone the child process
 * @stack:       the parent's user stack pointer. if stack==0, It means to fork a kernel thread.
 * @tf:          the trapframe info, which will be copied to child process's proc->tf
 */
int
do_fork(uint32_t clone_flags, uintptr_t stack, struct trapframe *tf) {
    int ret = -E_NO_FREE_PROC;
    struct proc_struct *proc;
    if (nr_process >= MAX_PROCESS) {
        goto fork_out;
    }
    ret = -E_NO_MEM;
    //LAB4:EXERCISE2 2016011446
    /*
     * Some Useful MACROs, Functions and DEFINEs, you can use them in below implementation.
     * MACROs or Functions:
     *   alloc_proc:   create a proc struct and init fields (lab4:exercise1)
     *   setup_kstack: alloc pages with size KSTACKPAGE as process kernel stack
     *   copy_mm:      process "proc" duplicate OR share process "current"'s mm according clone_flags
     *                 if clone_flags & CLONE_VM, then "share" ; else "duplicate"
     *   copy_thread:  setup the trapframe on the  process's kernel stack top and
     *                 setup the kernel entry point and stack of process
     *   hash_proc:    add proc into proc hash_list
     *   get_pid:      alloc a unique pid for process
     *   wakeup_proc:  set proc->state = PROC_RUNNABLE
     * VARIABLES:
     *   proc_list:    the process set's list
     *   nr_process:   the number of process set
     */

  	// 		1. 申请proc_struct，失败则跳fork_out
    if ((proc = alloc_proc()) == NULL) goto fork_out;
  
    //    2. 调用setup_kstack为子进程申请一个内核栈
    if (setup_kstack(proc) != 0) goto bad_fork_cleanup_proc;
  
    //    3. copy_mm根据clone_flag决定复制或共享父子进程的mm空间
    if (copy_mm(clone_flags, proc) != 0) goto bad_fork_cleanup_kstack;
  
    //    4. 调用copy_thread在进程内核栈顶构造一个trapframe和context
    copy_thread(proc, stack, tf);
  
    //    5. insert proc_struct into hash_list && proc_list
    bool intr_flag;
  	// 关中断（通过置intr_flag = 1)
    local_intr_save(intr_flag);
    {
        proc->pid = get_pid();	//获取进程PID
        hash_proc(proc);				//hash映射
        list_add(&proc_list, &(proc->list_link));	//proc_list插入链表
        ++nr_process;	//全局进程记录数加1
    }
  	// 开中断
    local_intr_restore(intr_flag);
  
    //    6. wakeup_proc设置proc_struct->state = PROC_RUNNABLE 唤醒进程
    wakeup_proc(proc);
  
    //    7. 返回子进程pid
    ret = proc->pid;
fork_out:
    return ret;

bad_fork_cleanup_kstack:
    put_kstack(proc);
bad_fork_cleanup_proc:
    kfree(proc);
    goto fork_out;
}
```



> 请说明 ucore 是否做到给每个新 fork 的线程一个唯一的 id？请说明你的分析和理由。

新线程的 `uid` 唯一，因为在调用 `get_pid` 函数之前已经关闭中断确保是原子操作，不会发生竞争。`get_pid`函数对`proc_list`中所记录的全部`proc_struct`的pid进行检查，保证不重复



### 阅读代码，理解 proc_run 函数和它调用的函数如何完成进程切换的。

从 proc_init() 函数开始说起的。由于之前的 proc_init() 函数已经完成了 idleproc 内核线程和 initproc 内核线程的初始化。所以在 kern_init() 最后，它通过 cpu_idle() 唤醒了 0 号 idle 进程，在分析 proc_run 函数之前，我们先分析调度函数 schedule() 。

```c
/* 
宏定义:
   #define le2proc(le, member)         \
    to_struct((le), struct proc_struct, member)
*/
void schedule(void) {
    bool intr_flag; //定义中断变量
    list_entry_t *le, *last; //当前list，下一list
    struct proc_struct *next = NULL; //下一进程
    local_intr_save(intr_flag); //中断禁止函数
    {
        current->need_resched = 0; //设置当前进程不需要调度
      //last是否是idle进程(第一个创建的进程),如果是，则从表头开始搜索
      //否则获取下一链表
        last = (current == idleproc) ? &proc_list : &(current->list_link);
        le = last; 
        do { //一直循环，直到找到可以调度的进程
            if ((le = list_next(le)) != &proc_list) {
                next = le2proc(le, list_link);//获取下一进程
                if (next->state == PROC_RUNNABLE) {
                    break; //找到一个可以调度的进程，break
                }
            }
        } while (le != last); //循环查找整个链表
        if (next == NULL || next->state != PROC_RUNNABLE) {
            next = idleproc; //未找到可以调度的进程
        }
        next->runs ++; //运行次数加一
        if (next != current) {
            proc_run(next); //运行新进程,调用proc_run函数
        }
    }
    local_intr_restore(intr_flag); //允许中断
}
```



**switch_to**

```c
.text
.globl switch_to
switch_to:                      # switch_to(from, to)
  	# esp指向下一个压栈的顶（逻辑上为空）
		# 前半段保存，后半段恢复
    # switch_to请求来源进程（from proc）的context的完整保存
  	# esp向上四个字节存的是from process的context地址
    movl 4(%esp), %eax          # eax保存from process的context地址
    popl 0(%eax)                # save eip !popl
  	# popl 完成将from proc的 eip（pc）保存到swap_context里
    
  
  	movl %esp, 4(%eax)					# 保存esp内容到from process的context中，下面同理
    movl %ebx, 8(%eax)
    movl %ecx, 12(%eax)
    movl %edx, 16(%eax)
    movl %esi, 20(%eax)
    movl %edi, 24(%eax)
    movl %ebp, 28(%eax)

    # restore to's registers
  	# 恢复进入运行状态的进行的寄存器中的值
    movl 4(%esp), %eax          # not 8(%esp): popped return address already
                                # eax now points to to
  	# 取出目的进程(to proc)的context的指针
  	# 将内存里的信息逐一导入寄存器
    movl 28(%eax), %ebp
    movl 24(%eax), %edi
    movl 20(%eax), %esi
    movl 16(%eax), %edx
    movl 12(%eax), %ecx
    movl 8(%eax), %ebx
    movl 4(%eax), %esp
		
  	# push内容为eax存储的eip（pc）
    pushl 0(%eax)               # push eip
  	
		# 使用ret，从栈中取出地址从而完成切换
  	# eip = fork ret的地址
    ret

```

`proc_run` 的执行过程为：

- 关中断；
- 将 current 指针指向将要执行的进程；
- 更新 TSS 中的栈顶指针；
- 加载新的页表；
- 调用 switch_to 进行上下文切换；
- 恢复IF位开中断

```c
// proc_run - make process "proc" running on cpu
// NOTE: before call switch_to, should load  base addr of "proc"'s new PDT
void
proc_run(struct proc_struct *proc) {
    if (proc != current) {	//调度对象不应是当前正在执行的进程
        bool intr_flag;			
        struct proc_struct *prev = current, *next = proc;
        local_intr_save(intr_flag);	//关中断
        {
            current = proc;	//切换
						
          	// 设置任务状态段 tss 中的特权级 0 下的 esp0 指针为 next 内核线程 的内核栈的栈顶
            load_esp0(next->kstack + KSTACKSIZE);
          	
          	// 切换进程页表
            lcr3(next->cr3);
          	
          	// 调用switch_to进行上下文切换
            switch_to(&(prev->context), &(next->context));
        }
        local_intr_restore(intr_flag);
    }
}
```

> 在本实验的执行过程中，创建且运行了几个内核线程？

总共创建了两个内核线程，分别为：

- idle_proc，为第 0 个内核线程，在完成新的内核线程的创建以及各种初始化工作之后，进入死循环，用于调度其他进程或线程；
- init_proc，被创建用于打印 "Hello World" 的线程。本次实验的内核线程，只用来打印字符串。

> 语句 `local_intr_save(intr_flag);....local_intr_restore(intr_flag);` 在这里有何作用？请说明理由。

在进行进程切换的时候，需要避免出现中断干扰这个过程，所以需要在上下文切换期间清除 IF 位屏蔽中断，并且在进程恢复执行后恢复 IF 位。

- Save/restore对应关/开中断，语句间内容不会被中断打断
- 比如说在 proc_run 函数中，将 current 指向了要切换到的线程，但是此时还没有真正将控制权转移过去，如果在这个时候出现中断打断这些操作，就会出现 current 中保存的并不是正在运行的线程的中断控制块，从而出现错误；

