## OS_lec13

## SPOC

1. do_execve：完成更新用户进程context，代码内容和数据内容，不改变页表基址

2. do_icode：完成设置用户堆栈，修改页表，根据ELF执行文件的格式描述分配内存并填写内容，设置用户态的EFLAG寄存器不可屏蔽中断

3. COW（Copy On Write）：父进程创建子进程需要创建子进程的页表，但是不复制父进程的内存空间

4. 中断处理例程的段表在GDT（全局描述符表）

5. vma_struct是合法的连续虚拟地址区域，mm_struct是整个进程的地址空间

6. 程序：对实现预期目的一系列动作的执行过程的描述，由一系列操作指令的序列组成。

   进程：具有一定独立功能的程序在一个数据集合上的一次动态执行过程

   联系：程序是进程的组成之一；同一个程序可对应多个不同进程；

   区别：进程是动态的过程，程序是静态的代码序列；进程是暂时的，程序是永久的；

7. 用户线程：用户线程是以用户函数库形式提供的线程实现机制

   用户线程是由函数库在用户态实现的线程机制；

   内核线程是由内核通过系统调用调用实现的线程机制；

   区别：实现方式、TCB的保存位置、运行开销、线程阻塞的影响范围

