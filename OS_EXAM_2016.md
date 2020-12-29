## OS_EXAM_2016

1. 在进程切换过程中，进程上下文信息的保存与恢复过程必须在内核态完成。（√）

   > context：进程的上下文，用于进程切换（参见switch.S）。在uCore中，所有的进程在内核中也是相对独立的（例如独立的内核堆栈以及上下文等等） 。使用context保存寄存器的目的就在于在内核态中能够进行上下文之间的切换。实际利用context进行上下文切换的函数是在`kern/process/switch.S`中定义的`switch_to`。

2. 信号量机制可实现基于条件变量的管程机制，反之亦然。（√）

   信号量和条件变量是等价的（也就是它们可以互相实现）。

   

3. 循环扫描算法（C-SCAN）对硬盘访问带来的好处在U盘上不存在。（√）

   > 循环扫描算法是对扫描算法的改进。如果对磁道的访问请求是均匀分布的，当磁头到达磁盘的一端，并反向运动时落在磁头之后的访问请求相对较少。这是由于这些磁道刚被处理，而磁盘另一端的请求密度相当高，且这些访问请求等待的时间较长，为了解决这种情况，循环扫描算法规定磁头单向移动。例如，只自里向外移动，当磁头移到最外的被访问磁道时，磁头立即返回到最里的欲访磁道，即将最小磁道号紧接着最大磁道号构成循环，进行扫描。

   > 对于U盘和SSD等随机访问的Flash半导体存储器，采用FCFS（先来先服务）调度策略更高效。 因为Flash的半导体存储器的物理结构不需要考虑寻道时间和旋转延迟，可直接按I/O请求的先后顺序服务。

4. 访问频率置换算法（Frequency-based Replacement）的基本思路是，在短周期中使用LFU算法，而在长周期中使用LRU算法。（×） 短周期用LRU，长周期用LFU

   

5. 在基于x86-32的ucore操作系统中，一般函数调用的参数通过（**1.1**）传递，系统调用的参数通过（**1.2**）传递，将系统调用号存放在（**1.3**），通过（**1.4**）指令进入内核态。此时还应该保存执行现场，需要在`trapframe`里保存（**1.5**）、（**1.6**）、（**1.7**）等信息（填三项即可）。

   栈；寄存器和栈；eax和寄存器；int 0x80；通用寄存器，EFLAGS，EIP，CS（代码段寄存器），SS，ESP

   

6. （**2.1**）是一种将不同文件名链接至同一个文件的机制，它可以使同一文件具有多个不同的名字，而文件系统只存在一个文件内容的副本。（**2.2**）和原文件共享一个相同的inode号（文件在文件系统上的唯一标识）。若原文件删除了，则（**2.3**）不能访问它指向的原文件，而（**2.4**）则是可以的。（**2.5**）可以跨越磁盘分区，但（**2.6**）不具备这个特性。

   链接；硬链接；软连接；硬链接；软连接；硬链接

   

7. RAID是一种机制，即把多块独立的硬盘按某种方式组合，形成硬盘阵列，从而提供比单块硬盘更快的访问性能或更可靠的数据存储能力。组成磁盘阵列的不同方式称为RAID级别，其中，（**3.1**）级别没有数据冗余存储功能，而（**3.2**）的数据可靠性在所有的RAID级别中是最高的。RAID 5是一种存储性能、数据安全和存储成本兼顾的磁盘阵列组成方式。它至少需要（**3.3**）块硬盘。当RAID5的一个磁盘数据发生损坏后，可利用剩下的数据和相应的（**3.4**）信息去恢复被损坏的数据。

   RAID0；RAID6；3；校验

   

8. 信号提供了异步处理事件的一种方式。例如，用户在终端按下“Ctrl-C”键，会产生可使当前进程终止的SIGINT信号。每一个信号对应一个（**4.1**）数，定义在头文件``中。信号处理行为可由三种方式可供选择：（**4.2**）、（**4.3**）、（**4.4**）。

   整数；捕获，忽略，屏蔽

   

9. 通过软件机制可正确实现互斥机制。

   下列二线程互斥机制的伪码实现是否有错？请给出原因分析，如果有错请给出反例。

   ```
   INITIALIZATION:
       shared int turn;
       ...
       turn = i ;
   
   ENTRY PROTOCOL (for Thread i ):
       /* wait until it's our turn */
       while (turn != i ) {
       }
   
   EXIT PROTOCOL (for Thread i ):
       /* pass the turn on */
       turn = j ;
   ```

   #### 注意：忙则等待与！！空闲则入！！

   线程i和j必须轮流访问临界区；如果 i 始终不进入临界区，则 j 无法进入，会发生饥饿。

   

10. N线程互斥伪码是否有误：

    ```
    INITIALIZATION:
        typedef char boolean;
        ...
        shared int num[n];
        ...
        for (j=0; j < n; j++) {
            num[j] = 0;
        }
        ...
    
    ENTRY PROTOCOL (for Thread i):
        /* choose a number */
        num[i] = max(num[0], ..., num[n-1]) + 1;
    
        /* for all other Threads */
        for (j=0; j < n; j++) {
            /* wait if the Thread has a number and comes ahead of us */
            if ((num[j] > 0) &&
                ((num[j] < num[i]) || (num[j] == num[i]) && (j < i)) ) {
                while (num[j] > 0) {}
                // 临界区
            }
        }
    
    EXIT PROTOCOL (for Thread i):
        /* clear our number */
        num[i] = 0;
    ```

    这种做法是错误的。

    first : 假设有两个进程，i<j，Ti正在执行`num[i] = max(num[0], ..., num[n-1]) + 1;`时，已计算得`max(num[0], ..., num[n-1])==0`；（即在`num[i]`得出结果前线程切换了）

    second : 此时切换到Tj，也计算得`max(num[0], ..., num[n-1])==0`，随后`num[j]=1`，Tj先进入临界区。

    third : 随后切换到Ti，计算得到`num[i]=1`，检查后Ti也进入临界区，违反互斥。

11. ```
    IMPLEMENTATION:
    monitor mt {
        -----variable in monitor-----------
        semaphore mutex; // the mutex lock for going into the routines in monitor, should be initialized to 1
        semaphore next; // the next is used to down the signaling proc, some proc should wake up the sleeped cv.signaling proc. should be initialized to 0
        int next_count; // the number of of sleeped signaling proc, should be initialized to 0
        condvar {int count, sempahore sem} cv[N]; // the condvars in monitor, count initial value 0, sem initial value 0
        other shared variables in mt; // shared variables should protected by mutex lock
    
        --------condvar wait---------------
        cond_wait (cv) {
            cv.count ++;
            if(mt.next_count>0)
                V(mt.next); // first perform the EXIT PROTOCOL
            else
                V(mt.mutex);
            P(cv.sem); // now wait on the condition waiting queue (cv.sem)
            cv.count --;
        }
    
        --------condvar signal--------------
        cond_signal(cv) {
            if(cv.count>0) { // do nothing unless a process is waiting on condition waiting queue (cv.sem)
                mt.next_count ++;
                V(cv.sem);  // release the waiting process which on condition waiting queue (cv.sem)
                P(mt.next); // wait on the "next" waiting queue for cv.signaling proc
                mt.next_count--;
            }
        }
    
        --------routines in monitor-------------
        routineA_in_mt () {
            P(mt.mutex); // ENTRY PROTOCOL (at the beginning of each monitor routines), wait for exclusive access to the monitor
            ...
            real body of routineA // in here, may access shared variables, call cond_wait OR cond_signal
            ...
            if(next_count>0) // EXIT PROTOCOL (at the end of each monitor function)
                V(mt.next); // if there are processes(sleeped cv.signaling proc) in the "next" queue, release one
            else
                V(mt.mutex); // otherwise, release the monitor
        }
    }
    ```

    (1) 请说明管程的特征。上述管程实现是哪种类型的管程？

    管程的特征：

    - 管程是一种用于多线程互斥访问共享资源的程序结构
    - 采用面向对象方法，简化了线程间的同步控制
    - 任一时刻最多只有一个线程执行管程代码
    - 正在管程中的线程可临时放弃管程的互斥访问，等待事件出现时恢复

    实现的是基于hoare的管程

    

    (2)在上述伪码中，如果有3个线程a，b，c需要访问管程，并会使用管程中的2个条件变量`cv[0]`，`cv[1]`。


    请问`cv[i]->count`的含义是什么？`cv[i]->count`是否可能`<0`，是否可能`>1`？请举例或说明原因。
    
    请问`mt->next_count`的含义是什么？`mt->next_count`是否可能`<0`，是否可能`>1`？请举例或说明原因。


​    

    `cv[i]->count`的含义是在该条件变量上等待的线程数。显然这个数不可能`<0`。如果有多于1个线程执行了`cond_wait(cv[i])`操作且还未被唤醒，这个数是可能`>1`的。
    
    `mt->next_count`的含义是发出signal后暂时进入等待状态的线程的个数。显然，这个数不可能`<0`。假设b执行`cond_wait(cv[0])`开始等待，c也执行`cond_wait(cv[0])`开始等待。a进入管程，执行`cond_signal(cv[0])`，唤醒b，a进入signal队列；b被唤醒后，立即执行`cond_signal(cv[0])`，唤醒c，b也进入signal队列。此时`mt->next_count=2`。


​    

12. 请描述stride调度算法的思路？stride算法的特征是什么？stride调度算法是如何避免stride溢出问题的？

    思路：

    - 每个进程有两个属性：
      - pass：当前位置
      - stride：一次要前进的步数
      - stride ∝ 1 / priority
    - 选择进程的方法：
      - 执行当前pass最小的进程
      - 该进程的pass += stride
      - 重复该过程

    特征：

    - stride越小（优先级越高），被调度的次数会越多
    - 基于优先级（priority-based）
    - 调度选择是确定的（deterministic）

    避免stride溢出（无符号溢出）的方法：

    - uint32存储、int32相减比较
    - 最大步进值-最小步进值 < 无符号整数 / 2

    

    无符号整数ab作为两个stride
    假设开始的时候a=b，之后b先增加。如果b没有溢出的话，此时a-b<0，之后应该轮到a增加，此时是成功的。

    如果b溢出了话：
    首先看到schedule/default_sched.c中有一句 #define BIG_STRIDE 0x7FFFFFFF
    因为stride每次的增量都是 BIG_STRIDE / priority，所以stride每次最大的增量不会超过BIG_STRIDE
    那么因为b溢出了，所以b在溢出之前，ab相等，且无符号大于0x7FFFFFFF
                    **在b溢出之后，a仍然保持原来大于0x7FFFFFFF，b小于0x7FFFFFFF**
                    **且a-b无符号大于0x7FFFFFFF（因为b的步进值小于0x7FFFFFFF），也就是有符号小于0，仍然是成功的**

    所以问题的关键就在于#define BIG_STRIDE 0x7FFFFFFF
    这个值必须是有符号整数的最大值，这个是保证stride不会出错的原因
    举个例子，把BIG_STRIDE增大，BIG_STRIDE=0xE0000000
    那么初始令a=b=0xE0000000，b先前进0xE0000000，b变为0xC0000000，此时就有a-b>0，stride算法就错了

    

13. 试以图示描述ucore操作系统中的SFS文件系统的文件组织方式。

14. 下面是SFS的磁盘索引节点数据结构定义。

    ```
    struct sfs_disk_inode {
        uint32_t size; // 如果inode表示常规文件，则size是文件大小
        uint16_t type; // inode的文件类型
        uint16_t nlinks; // 此inode的硬链接数
        uint32_t blocks; // 此inode的数据块数的个数
        uint32_t direct[SFS_NDIRECT]; // 此inode的直接数据块索引值（ 有SFS_NDIRECT个）
        uint32_t indirect; // 此inode的一级间接数据块索引值
    };
    ```

    假定ucore里SFS_NDIRECT的取值是16，而磁盘上数据块大小为1KB。请计算这时ucore支持的最大文件大小。请给出计算过程。（这样可给步骤分）

    

    SFS使用索引分配

    SFS中的磁盘索引节点代表了一个实际位于磁盘上的文件

    通过上表可以看出，如果inode表示的是文件，则成员变量direct[]直接指向了保存文件内容数据的数据块索引值。indirect间接指向了保存文件内容数据的数据块，indirect指向的是间接数据块（indirect block），此数据块实际存放的全部是数据块索引，这些数据块索引指向的数据块才被用来存放文件内容数据。

    

    **x86页4KB，页表项4B**

    默认的，ucore里SFS_NDIRECT是12，即直接索引的数据页大小为12 * 4k = 48k；当使用一级间接数据块索引时，ucore 支持最大的文件大小为 12 * 4k + 1024 * 4k = 48k + 4m。数据索引表内，0表示一个无效的索引，inode里blocks表示该文件或者目录占用的磁盘的block的个数。indiret为0时，表示不使用一级索引块。（因为 block 0用来保存super block，它不可能被其他任何文件或目录使用，所以这么设计也是合理的）

    

    数据块1KB，页表项4B

    在题设中，最大可能的文件大小为使用一级间接数据块索引时，为(16 + 1KB/4B) * 1KB = 272KB。

