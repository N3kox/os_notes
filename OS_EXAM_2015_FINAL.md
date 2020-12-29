## OS_EXAM_2015_FINAL

1. 在用`do_execve`启动一个用户态进程时，ucore需要完成很多准备工作，这些工作有的在内核态完成，有的在用户态完成。请判断下列事项是否是ucore在正常完成`do_execve`中所需要的，如果是，指出它完成于内核态还是用户态（通过修改`trapframe`，在`iret`时改变寄存器的过程被认为是在内核态完成）。

   1. 初始化进程所使用的栈 ： 需要，内核态
   2. 在栈上准备argc和argv的内容：需要，内核态
   3. 将argc和argv作为用户main函数的参数放到栈上：不需要，用户态
   4. 设置EIP为用户main函数的地址：不需要，用户态
   5. 设置系统调用的返回值：不需要，用户态

2. 在ucore中`enum proc_state`的定义包含以下四个值：

   - `PROC_UNINIT`
   - `PROC_SLEEPING`
   - `PROC_RUNNABLE`
   - `PROC_ZOMBIE`

   

   - `PROC_UNINIT`：刚申请完进程控制块，进程还未被初始化
   - `PROC_SLEEPING`：进程处于等待状态
   - `PROC_RUNNABLE`：进程处于就绪或运行状态
   - `PROC_ZOMBIE`：僵尸状态，进程已经退出，等待父进程进一步回收资源

   

   Explains:

   - 进程首先在cpu初始化或者`sys_fork`的时候被创建，当为该进程分配了一个进程控制块之后，该进程进入`uninit`态(在`proc.c`中`alloc_proc`)。
   - 当进程完全完成初始化之后，该进程转为`runnable`态。
   - 当到达调度点时，由调度器`sched_class`根据运行队列`rq`的内容来判断一个进程是否应该被运行，即把处于`runnable`态的进程转换成`running`状态，从而占用CPU执行。
   - `running`态的进程通过`wait`等系统调用被阻塞，进入`sleeping`态。
   - `sleeping`态的进程被`wakeup`变成`runnable`态的进程。
   - `running`态的进程主动`exit`变成`zombie`态，然后由其父进程完成对其资源的最后释放，子进程的进程控制块成为`unused`。
   - 所有从`runnable`态变成其他状态的进程都要出运行队列，反之，被放入某个运行队列中。

   

3. 假设在lab6测试stride scheduling的过程中，采用如下默认配置：BigStride为0x7FFFFFFF，CPU时间片为50ms，测试过程包含五个进程，其初始~~stride~~pass均为1，优先级分别为1、2、3、4、5，测试时间为10s。下面给出了五种修改上述配置的方式，试讨论：对于每一种改动，测试结果相比改动之前是否会发生明显的变化？如果是，结果会变得更接近于理想情况，还是远离理想情况？

   1. BigStride改为120：stride最大为120，不会溢出，且能整除12345，接近理想情况
   2. CPU时间片改为5ms：时间片总数增加，而原stride计算不准确，故会偏离理想情况
   3. 五个进程的初始pass改为100：unknown
   4. 五个进程的优先级设为2、4、6、8、10：不变
   5. 测试时间延长到20s：更远离

4. 信号量PV操作的伪代码：这个是十分简单了。

   ```
   P() {
       sem--;
       if (sem < 0) {
           Add this thread t to q;
           block(p);
       }
   }
   
   V() {
       sem++;
       if (sem <= 0) {
           Remove a thread t from q;
           wakeup(t);
       }
   }
   ```

5. 下面是关于ucore中用户程序的生命历程的代码。请完成下面填空和代码补全。

   (1) 在`sh`的命令行上输入`args 1`启动用户程序`args`，则`sh`会调用（**1**）创建新进程并调用（**2**）将`args`加载到该进程的地址空间中。（回答系统调用名称即可）

   **SYS_fork；SYS_exec**

   (2)将`args`从硬盘加载主要由`load_icode`完成，请补全以下代码。

   ```c
   // load_icode - called by sys_exec-->do_execve
   
   static int
   load_icode(int fd, int argc, char **kargv) {
       /* LAB8:EXERCISE2 YOUR CODE HINT:how to load the file with handler fd in to process's memory? how to setup argc/argv?
       * MACROs or Functions:
       * mm_create - create a mm
       * setup_pgdir - setup pgdir in mm
       * load_icode_read - read raw data content of program file
       * mm_map - build new vma
       * pgdir_alloc_page - allocate new memory for TEXT/DATA/BSS/stack parts
       * lcr3 - update Page Directory Addr Register -- CR3
       */
       /* (1) create a new mm for current process
       * (2) create a new PDT, and mm->pgdir= kernel virtual addr of PDT
       * (3) copy TEXT/DATA/BSS parts in binary to memory space of process
       * (3.1) read raw data content in file and resolve elfhdr
       * (3.2) read raw data content in file and resolve proghdr based on info in elfhdr
       * (3.3) call mm_map to build vma related to TEXT/DATA
       * (3.4) callpgdir_alloc_page to allocate page for TEXT/DATA, read contents in file
       * and copy them into the new allocated pages
       * (3.5) callpgdir_alloc_page to allocate pages for BSS, memset zero in these pages
       * (4) call mm_map to setup user stack, and put parameters into user stack
       * (5) setup current process's mm, cr3, reset pgidr (using lcr3 MARCO)
       * (6) setup uargc and uargv in user stacks
       * (7) setup trapframe for user environment
       * (8) if up steps failed, you should cleanup the env.
       */
       assert(argc >= 0 && argc <= EXEC_MAX_ARG_NUM);
   
       if (current->mm != NULL) {
           panic("load_icode: current->mm must be empty.\n");
       }
   
       int ret = -E_NO_MEM;
       struct mm_struct *mm;
       if ((mm = mm_create()) == NULL) {
           goto bad_mm;
       }
       if (setup_pgdir(mm) != 0) {
           goto bad_pgdir_cleanup_mm;
       }
   
       struct Page *page;
   
       struct elfhdr __elf, *elf = &__elf;
       /* 2a */
       if ((ret = load_icode_read(fd, elf, _(2a)_, 0)) != 0) {
           goto bad_elf_cleanup_pgdir;
       }
   
       if (elf->e_magic != ELF_MAGIC) {
           ret = -E_INVAL_ELF;
           goto bad_elf_cleanup_pgdir;
       }
   
       struct proghdr __ph, *ph = &__ph;
       uint32_t vm_flags, perm, phnum;
       for (phnum = 0; phnum < elf->e_phnum; phnum ++) {
           off_t phoff = elf->e_phoff + sizeof(struct proghdr) * phnum;
           if ((ret = load_icode_read(fd, ph, sizeof(struct proghdr), phoff)) != 0) {
               goto bad_cleanup_mmap;
           }
           if (ph->p_type != ELF_PT_LOAD) {
               /* 2b */
               _(2b)_
           }
           if (ph->p_filesz > ph->p_memsz) {
               ret = -E_INVAL_ELF;
               goto bad_cleanup_mmap;
           }
           if (ph->p_filesz == 0) {
               continue ;
           }
           vm_flags = 0, perm = PTE_U;
           if (ph->p_flags & ELF_PF_X) vm_flags |= VM_EXEC;
           if (ph->p_flags & ELF_PF_W) vm_flags |= VM_WRITE;
           if (ph->p_flags & ELF_PF_R) vm_flags |= VM_READ;
           if (vm_flags & VM_WRITE) perm |= PTE_W;
           if ((ret = mm_map(mm, ph->p_va, ph->p_memsz, vm_flags, NULL)) != 0) {
               goto bad_cleanup_mmap;
           }
           off_t offset = ph->p_offset;
           size_t off, size;
           uintptr_t start = ph->p_va, end, la = ROUNDDOWN(start, PGSIZE);
   
           ret = -E_NO_MEM;
   
           end = ph->p_va + ph->p_filesz;
           while (start < end) {
               if ((page = pgdir_alloc_page(mm->pgdir, la, perm)) == NULL) {
                   ret = -E_NO_MEM;
                   goto bad_cleanup_mmap;
               }
               off = start - la, size = PGSIZE - off, la += PGSIZE;
               if (end < la) {
                   size -= la - end;
               }
               if ((ret = load_icode_read(fd, page2kva(page) + off, size, offset)) != 0) {
                   goto bad_cleanup_mmap;
               }
               start += size, offset += size;
           }
           end = ph->p_va + ph->p_memsz;
   
           if (start < la) {
               /* ph->p_memsz == ph->p_filesz */
               if (start == end) {
                   continue ;
               }
               off = start + PGSIZE - la, size = PGSIZE - off;
               if (end < la) {
                   size -= la - end;
               }
               memset(page2kva(page) + off, 0, size);
               start += size;
               assert((end < la && start == end) || (end >= la && start == la));
           }
           while (start < end) {
               if ((page = pgdir_alloc_page(mm->pgdir, la, perm)) == NULL) {
                   ret = -E_NO_MEM;
                   goto bad_cleanup_mmap;
               }
               off = start - la, size = PGSIZE - off, la += PGSIZE;
               if (end < la) {
                   size -= la - end;
               }
               memset(page2kva(page) + off, 0, size);
               start += size;
           }
       }
       sysfile_close(fd);
   
       vm_flags = VM_READ | VM_WRITE | VM_STACK;
       /* 2c */
       if ((ret = mm_map(mm, _(2c)_, USTACKSIZE, vm_flags, NULL)) != 0) {
           goto bad_cleanup_mmap;
       }
       assert(pgdir_alloc_page(mm->pgdir, USTACKTOP-PGSIZE , PTE_USER) != NULL);
       assert(pgdir_alloc_page(mm->pgdir, USTACKTOP-2*PGSIZE , PTE_USER) != NULL);
       assert(pgdir_alloc_page(mm->pgdir, USTACKTOP-3*PGSIZE , PTE_USER) != NULL);
       assert(pgdir_alloc_page(mm->pgdir, USTACKTOP-4*PGSIZE , PTE_USER) != NULL);
   
       mm_count_inc(mm);
       current->mm = mm;
       current->cr3 = PADDR(mm->pgdir);
       lcr3(PADDR(mm->pgdir));
   
       //setup argc, argv
       uint32_t argv_size=0, i;
       for (i = 0; i < argc; i ++) {
           argv_size += strnlen(kargv[i],EXEC_MAX_ARG_LEN + 1)+1;
       }
   
       uintptr_t stacktop = USTACKTOP - (argv_size/sizeof(long)+1)*sizeof(long);
       char** uargv=(char **)(stacktop - argc * sizeof(char *));
   
       argv_size = 0;
       for (i = 0; i < argc; i ++) {
           uargv[i] = strcpy((char *)(stacktop + argv_size ), kargv[i]);
           /* 2d */
           _(2d)_
       }
   
       stacktop = (uintptr_t)uargv - sizeof(int);
       /* 2e */
       *(int *)stacktop = _(2e)_;
   
       struct trapframe *tf = current->tf;
       memset(tf, 0, sizeof(struct trapframe));
       tf->tf_cs = USER_CS;
       tf->tf_ds = tf->tf_es = tf->tf_ss = USER_DS;
       tf->tf_esp = stacktop;
       tf->tf_eip = elf->e_entry;
       tf->tf_eflags = FL_IF;
       ret = 0;
   out:
       return ret;
   bad_cleanup_mmap:
       exit_mmap(mm);
   bad_elf_cleanup_pgdir:
       put_pgdir(mm);
   bad_pgdir_cleanup_mm:
       mm_destroy(mm);
   bad_mm:
       goto out;
   }
   ```