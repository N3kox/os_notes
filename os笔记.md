

##os

1. 反置页表：普通的页表将逻辑地址映射为物理地址，提供将页表号（page number）转换为页框（page frame number）的对应（MMU完成）；而反置页表相反，让页表与物理地址空间大小相对应。通过提供页框号来转化为页号。由于页框数量仅取决于实际内存大小/页面大小，当前在64位地址空间下计算机的物理内存远小于虚拟内存，故相对于64位地址下的页表映射，反置页表较小。

   页寄存器：每一个物理帧与寄存器相对应，使用位（此帧是否被进程占用），占用页号p，保护位（约定保护方式r/w/rw)。用逻辑地址进行Hash以减少页表项搜索。

   ![截屏2020-10-06 下午10.21.36](/Users/mac/Desktop/考研/os2019-master/截屏2020-10-06 下午10.21.36.png)

2. 页帧（物理页面，page frame）：把物理地址划分成大小相同的基本分配单位（2的k次幂）。

   页面（逻辑页面，page）：把逻辑地址空间也划分成为大小相同的基本分配单位。

   注意：帧和页大小必须相同；页面偏移=页帧偏移而页号大小！=帧号大小（逻辑地址空间页号连续，帧号不一定相邻）；不是所有的页都有对应的帧。

   页表Page->Frame：页表基址PTBR（Page Table Basic Register），页号作为下标查找页表项，帧号作为页表项字段之一。页表实现了逻辑地址到物理地址的转换。MMU，TLB

   非连续内存分配访问两次内存：获取页表项 + 访问数据。

   处理页表问题：TLB，多级页表。

   页目录表：一级页表，其余则为二级页表

3. 页表项标志:

   1. 存在位：逻辑页号是否有物理帧对应
   2. 修改位：页面是否修改
   3. 引用位：页面存储单元是否被访问过

4. 段选择子：位于段寄存器，RPL位于数据段，CPL位于代码段，两者合在一起和段描述符的DPL进行比较。CPL是当前进程特权级，存于cs寄存器低两位；RPL是对段访问的请求权限；DPL存在段描述符中，规定该段的权限级别（固定）。

   对于中断、陷入、异常称为门情况，要求门的特权级低于等于当前代码段，而可以访问门后的特权级更高的段（如ring 3应用程序系统调用访问ring 0 OS内核服务）。

   访问段当前代码段或数据段请求要求自己本身的特权级高于要访问段的特权级（数值比较上是max<=，实际是倒置即要求当前特权级高于请求访问段特权级）。

   访问门：目的段特权级 >= 当前段CPL >= 门特权级

   访问段：当前段特权级 （取最低）>= 目的段特权级

   没法通过检查则为保护错，是一种异常。

   <img src="/Users/mac/Desktop/考研/os2019-master/截屏2020-10-07 下午1.59.34.png" alt="截屏2020-10-07 下午1.59.34" style="zoom:50%;" />

5. x86特权级切换：

   1. ring 0  to ring 3：从内核态模拟一个应用程序状态的特权级（RPL=3，CPL=3）并压栈，调用IRET指令弹出来切换至应用程序状态。
   2. ring 3 to ring 0：构造软中断，IDT建立中断门，压应用程序此刻的堆栈（SS，ESP删除，CS中CPL=0），然后调用IRET弹出来切换至内核态。
   3. 任务状态段TSS保存了不同特权级使用的各类信息。3to0时，地址、堆栈均变换（由不同硬件机构保存）。全局描述符表中有一项为TSS基址。访问TSS时硬件去找，软件去填写TSS内容。

6. PDE（Page Directory Entry）记录二级页表地址，PTE（Page Table Entry）记录线性地址对应页的起始地址，实现段页式由线性地址(Linear Address)查找物理地址。进入保护模式一定存在段机制，线性地址与虚拟地址此时对等。

   此图中展示的Offset决定了PDE与PTE中每一项查找出来的内容应该左移12位，表项中高20位为下一级查找的基址，后面余下12位为将来需要访问的某一些属性，如R/W，U/Supervisor，A为1表示被接收。

   使能页机制（CR0高31位表示启动页机制，最后一位enable保护模式，内核态访问）。

   <img src="/Users/mac/Desktop/考研/os2019-master/截屏2020-10-07 下午3.03.09.png" alt="截屏2020-10-07 下午3.03.09" style="zoom:50%;" />

7. 覆盖-手动，交换-自动；覆盖发生在程序内没有调用关系的模块间，交换以进程为单位，不需要程序模块结构。虚拟存储：以页为单位自动装入更大的程序，不连续-大空间-部分交换。

8. 时间局部性，空间局部性，分支局部性

9. 虚拟页表项：

   1. 驻留位P：该页是否在内存。
   2. 修改位D：在内存中的该页是否被修改过（回收时写回策略）。
   3. 访问位A：是否被访问过（读或写），用于页面置换算法。
   4. 保护位：该页允许访问的方式（r/w/rw）

10. 外存某一页如何去找：Linux选择一个分区为对换区；或用一个特殊格式的文件存未被映射的文件。代码段和动态加载的共享库程序段不会修改，其他段可以放在对换区。

11. EAT计算，5ms * p * (1 + q)，其中因为修改页需要访磁盘两次，故为1+q

    <img src="/Users/mac/Desktop/考研/os2019-master/截屏2020-10-10 下午4.43.03.png" alt="截屏2020-10-10 下午4.43.03" style="zoom:50%;" />

12. 时钟置换进来新页访问位置1，指针指向下一项

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201010221631559.png" alt="image-20201010221631559" style="zoom:50%;" />

    改进的clock增加修改位，修改过的页面（未写入）指针经过时重置为0，访问位和修改位均为0才换出。

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201010221928850.png" alt="image-20201010221928850" style="zoom:50%;" />

    工作集置换：在访存时开销大，缺页时只需要将此页放入即可

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201011144647930.png" alt="image-20201011144647930" style="zoom:50%;" />

    缺页率置换算法：

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201011150921962.png" alt="image-20201011150921962" style="zoom:50%;" />

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201011150843659.png" alt="image-20201011150843659" style="zoom:50%;" />

13. 进程是一个具有一定#独立功能#的#程序#在一个#数据集合#上的一次#动态执行过程#，包含了一个运行的程序的全体信息。

    进程=执行中的程序=程序+执行，即进程为动程序为静，进程暂时程序永久，进程包括程序+数据信息+控制块。

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201011220003692.png" alt="image-20201011220003692" style="zoom:50%;" />

14. fork和exec

    1. fork()创建一个继承的子进程，复制父进程的所有变量和内存、复制父进程的所有cpu寄存器，只有pid不同。
    2. 子进程folk()返回0；父进程folk()返回子进程标识符，失败返回小于0。folk返回值可方便后续使用，子进程可以通过getpid获取pid
    3. fork执行过程是相对于父进程地址空间的复制。
    4. exec加载新的可执行文件来替代当前进程，废弃原数据站和堆栈，只留下进程号pid。
    5. vfork轻量级复制，现在使用Copy on Write写时复制技术，延迟到需要使用时才复制。
    6. fork()函数会将父进程的物理内存共享给子进程，！！即将父进程多级页表的内容复制到子进程新建立的多级页表中！！。然而在这种机制下，对于父进程中那些原本可读可写的页，一旦被共享给子进程之后，两个进程中任何一个对该物理页内容进行了修改，将会影响另外一个进程的正常使用，于是，内核解决此问题的方法是：在将父进程的多级页表复制到子进程的多级页表中时，会将之前对于父进程来说可写的物理页对应的页表项，在父子进程的多级页表中都设置为只读，因此，一旦两个进程中的任何一个对某个写保护（只读）的物理页发生了写操作，就会导致pagefault，相应的内核函数会处理并识别出这种写时拷贝机制导致的错误，并复制该物理页的内容到一个新的物理页，并将新的物理页链接到发生写操作的进程的多级页表中，最后恢复该物理页对应表项的写权限，恢复进程对该物理页的写操作，做到进程无感知的处理。

15. Wait-exit:

    1. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201012183439313.png" alt="image-20201012183439313" style="zoom:50%;" />

       <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201012183645795.png" alt="image-20201012183645795" style="zoom:50%;" />

       fork进入创建状态，wait会导致进程从运行态变为等待态，子进程exit可以使wait进入等待状态的父进程进入就绪状态，父进程exit进入退出状态。

16. 关于实验四内核线程：

    1. 内核线程只运行在内核态
    2. 用户进程会在在用户态和内核态交替运行
    3. 所有内核线程共用ucore内核内存空间，不需为每个内核线程维护单独的内存空间
    4. 而用户进程需要维护各自的用户内存空间

17. 处理机调度

    1. 短进程优先具有最优平均周转时间，可能导致饥饿；可以通过上次运行时间进行衰减获得拟合曲线。
    2. HRRN最高响应比优先：R=（等待时间+执行时间）/执行时间，防止饥饿，不可抢占。
    3. 硬时限：错过任务后果严重，必须验证在最坏情况下满足时限；软时限：通常满足任务时限，不能满足是降低要求，尽力完成。
    4. ![image-20201014165151667](/Users/mac/Library/Application Support/typora-user-images/image-20201014165151667.png)
    5. 优先级反置：高优先级进程等待低优先级进程所占资源而无法进行调度的情况，基于优先级的可抢占调度算法存在优先级反置。处理方法：
       1. 优先级继承：T3优先级低，在t4时刻T1请求资源s而s被T3占用，故为防止T3被T2锁，T3优先级提升至T1，继续执行至t6释放资源s并使特权级返回初始状态，继而使T1继续进行。在等待使才发生提高优先级。<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201014175427884.png" alt="image-20201014175427884" style="zoom:50%;" />
       2. 优先级天花板：提升至当前优先级集合中的最大值。<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201014175642287.png" alt="image-20201014175642287" style="zoom:50%;" />

18. 软件同步：

    1. Peterson：turn表示谁进入临界区，flag表示进程准备好进入临界区。进入区代码先设置标志，修改turn，最后做判断同时检查flag和turn，均满足自身时才可以进入。退出区flag=false。
    2. 拓展：turn共享，n个进程有n个flag。线程修改flag=true，修改turn后turn只允许某一个线程（最后一个）运行，完成后turn按照环顺序一直向后行动。![image-20201015203059987](/Users/mac/Library/Application Support/typora-user-images/image-20201015203059987.png)

19. 原子操作指令锁：<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201015204603987.png" alt="image-20201015204603987" style="zoom:50%;" />

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201015204850137.png" alt="image-20201015204850137" style="zoom:50%;" />

20. 信号量，生产者消费者互斥问题：

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201016162920625.png" alt="image-20201016162920625" style="zoom:50%;" />

    信号量机制的问题：

     	1. 读/开发代码困难
     	2. 容易出错：信号量被另外一个线程占用；忘记释放信号量。
     	3. 不能处理死锁问题

21. 管程：多线程互斥访问共享资源的程序结构，中途可以放弃互斥资源的访问权限。

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201016163743737.png" alt="image-20201016163743737" style="zoom:50%;" />

    条件变量：管程内部的等待机制

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201016163932435.png" alt="image-20201016163932435" style="zoom:50%;" />

    lock:管程互斥访问的锁，full，empty两个条件变量。

    lock->acquire & release：为管程进入的申请和释放，为构成管程内部的代码

    count==n：表示n个缓冲区都有数据了，等待notfull条件变量

    管程在内部检查时如果不成功可以放弃权限，而信号量不可以按如下方法在锁的内部检查。

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201016164316413.png" alt="image-20201016164316413" style="zoom:50%;" />

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201016164600301.png" alt="image-20201016164600301" style="zoom:50%;" />

    Hansen在OS与Java中使用，while中条件变量的wait仅仅为一种提示，继续执行时需要重新检查，再次检查时相当于重新排队，因为释放之后会继续执行，状态可能发生改变。当前正在执行的线程优先级更高

    Hoare教科书做法：条件变量立即释放且放弃管程的使用权。

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201016164746935.png" alt="image-20201016164746935" style="zoom:50%;" />

22. 读写者问题：

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201016191008125.png" alt="image-20201016191008125" style="zoom:50%;" />

    管程解决读写者问题：维护AR，AW，WR，WW，正在读正在写只有一个大于零。

    ![image-20201016192659909](/Users/mac/Library/Application Support/typora-user-images/image-20201016192659909.png)

    读者优先：

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201016192921591.png" alt="image-20201016192921591" style="zoom:50%;" />

    写者优先：

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201016193153824.png" alt="image-20201016193153824" style="zoom:50%;" />

23. stride调度：

    1. 算法策略选择stride最小的进程执行，执行时间为stride+pass。
    2. 算法是基于优先级的算法，调度选择是固定的
    3. skew heap斜堆进行插入删除查找
    4. pass与priority：pass = BIG_VALUE / lab6_priority（即pass = 最大STRIDE 除以优先级）
    5. ！！！stride溢出处理：
       1. STRIDE_MAX - STRIDE_MIN <= PASS_MAX
       2. stride和pass是无符号整数
       3. 如此使得在比较时使用有符号数比较 if ((int32_t)(p->lab6_stride - q->lab6_stride) > 0)时可以正确得出结果：Stride 调度算法的思路是每次找 stride 步进值最小的进程，每个进程每次执行完以后，都要在 stride步进 += pass步长，一直相加会导致溢出，因此设置的步长可以

24. **资源分配图有环路也不一定有死锁**

25. 出现死锁的四个**必要条件**：

    1. 互斥：资源任何时刻只有一个进程使用
    2. 持有并等待：保持资源并等待获取其他进程占用的资源
    3. 非抢占：资源在进程使用后自动放弃
    4. 循环等待：等待进程集合构成环路

26. 死锁处理：

    1. 死锁预防：确保系统永远不会进入死锁。使任何时刻都不满足死锁的必要条件。

       1. 互斥：互斥的共享资源封装为可同时访问
       2. 持有并等待：进程请求资源时，要求他不持有任何资源（一次申请全部需要）；仅允许在开始时申请全部资源。此时效率低。
       3. 非抢占：若不能立即分配资源，则释放已经占有的所有资源；如能够获得全部资源才分配（类似与持有并等待）。
       4. 循环等待：资源排序，要求按照固定的顺序申请资源。

    2. 死锁避免：使用前进入判断，只允许不会出现死锁的进程申请资源。需要额外先验信息进行判断。要求提供资源的最大需求；限定提供与分配的资源数量，保证满足进程最大需求；动态检查资源分配，防止环路。

       ###安全一定不会死锁；不安全可能死锁；死锁一定不安全。

    3. 死锁检测与恢复：检测到死锁状态后进行恢复

       1. O(m*(n^2))：m资源类型，n进程数量
       2. 终止所有进程
       3. 一次终止一个
       4. 终止顺序：进程优先级>进程已运行时间与需要运行时间>进程已占用资源>进程完成所需要的资源>终止进程数目>进程交互还是批处理
       5. 资源抢占：选择被强占进程-进程回退-可能出现饥饿（同一进程可以一直被抢占）

    4. 由应用进程处理死锁，操作系统忽略死锁。

27. 进程间通信IPC：

    1. 发送send，接收receive

    2. 通信流程：进程间建立通信链路，通过s/r交换消息。物理/逻辑链路

    3. 间接通信：基于操作系统内核，使用消息队列缓存消息（多对多），进程生命周期可以不同。消息的发送只在乎消息队列是谁，不在乎接收方是谁。

       <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020215740075.png" alt="image-20201020215740075" style="zoom:50%;" />

    4. 直接通信：共享信道，两个进程必须同时存在，使用一个消息队列进行交流

       <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020215630704.png" alt="image-20201020215630704" style="zoom:50%;" />

    5. 阻塞与非阻塞通信

       1. 阻塞发送：发送方发送消息后等待直到接收方收到

          阻塞接收：接收方请求接收消息后等待直到收到消息

       2. 非阻塞通信：发送者在消息发送后可执行其他操作

          非阻塞接收：请求消息后可以执行其他操作

    6. 通信链路缓冲：

       1. 0容量：发送方等待接收方
       2. 有限容量：队满发送方等待
       3. 无限容量：发送方不需要等待

28. 信号与管道：

    1. 信号：

       1. 进程间的软件中断通知和处理机制(default信号处理例程：ctrl+c)：如SIGKILL，SIGSTOP，SIGCONT等

       2. 信号接收和处理：

          <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020220715798.png" alt="image-20201020220715798" style="zoom:50%;" />

       3. 信号实现：<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020220816188.png" alt="image-20201020220816188" style="zoom:50%;" />

       4. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020220853574.png" alt="image-20201020220853574" style="zoom:50%;" />

    2. 管道：进程间基于内存文件的通信机制，间接通信。建立的是内存区域而不是磁盘文件系统的真实文件。

       1. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020221316239.png" alt="image-20201020221316239" style="zoom:50%;" />
       2. 读管道read(fd, buffer, nbytes)：scanf基于read；
       3. 写管道write(fd, buffer, nbytes)：printf基于write；
       4. 创建管道pipe(rgfd)：创建文件描述符数组，rgfd是两个文件描述符组成的数组，rgfd[0]读文件描述符，rgfd[1]写文件描述符
       5. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020221627804.png" alt="image-20201020221627804" style="zoom:50%;" />

29. 消息队列与共享内存：

    1. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020222053530.png" alt="image-20201020222053530" style="zoom:50%;" />

       <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020222133757.png" alt="image-20201020222133757" style="zoom:50%;" />

       Msgctl消息队列控制：实现生命周期不同的进程对消息队列的控制。

    2. 共享内存：

       <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020222302760.png" alt="image-20201020222302760" style="zoom:50%;" />

       <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020222359331.png" alt="image-20201020222359331" style="zoom:50%;" />

       页表项映射的物理地址相同，逻辑地址不同。

       <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201020222416288.png" alt="image-20201020222416288" style="zoom:50%;" />

       需要信号量机制协调共享内存的访问冲突。

30. 文件:

    1. 文件系统功能：管理文件块（位置+顺序），管理空闲空间（位置），分配算法（策略）
    2. 管理文件集合：定位、命名、文件系统结构
    3. 数据可靠和安全：多层次保护数据安全，可靠性（持久保存，避免系统崩溃等）
    4. 文件属性：命名、类型、位置、大小、保护、创建者。。。
    5. 文件头：文件系统元数据中的文件信息，含文件属性、文件存储位置和顺序

31. 打开文件和文件描述符

    1. 文件访问模式：访问数据前先打开

    2. 内核追踪进程打开的所有文件：os为每个进程维护一个打开文件表，文件描述符为打开文件的标识，注意区分文件的标识和文件标识符不同（打开文件的数目和文件系统中的文件数目数量级有差别）。

    3. 文件描述符：打开文件状态和信息

       1. 文件指针：最近读写位置，每个进程维护自己的打开文件指针（不随其他进程改变）
       2. 文件打开计数：最后一个进程关闭文件中，可以将其从打开文件表中移除
       3. 文件的磁盘位置：缓存数据访问信息
       4. 访问权限：每个进程的文件访问模式信息

    4. 文件的用户视图和系统视图：

       1. 用户视图：持久的数据结构

       2. 系统视图-系统访问接口：字节序列的集合（UNIX），系统不关系存储在磁盘上的数据结构

       3. os的文件视图：数据块的集合

       4. 数据块是逻辑存储单元，扇区是物理存储单元；数据块大小和扇区大小不同（可能几个扇区构成一个数据块）

       5. 用户视图到系统视图：

          1. 进程读文件：读字节所在的块（读取最小单位是块），返回数据块内对应部分
          2. 进程写文件：获取数据块，修改块对应内容，整块写回
          3. ！！！文件系统中的基本操作单位是数据块！！！getc和putc访问1字节，缓存4096字节

       6. 进程访问模式

          1. 顺序访问：按字节依次读取（大多数文件访问）
          2. 随机访问：从中间读写（不常用，但虚拟存储中把内存页存储在对换文件中）
          3. 索引访问：依据数据特征的索引
             1. os不完全提供索引访问
             2. 数据库建立在索引内容的磁盘访问（os可以视为小数据库）
             3. 对相应内容进行抽象，进行快速查找访问

       7. 文件内部结构：

          1. 无结构
          2. 简单记录：分列，固定长度或可变长度
          3. 复杂结构：格式化文档（xml，pdf），可执行文件。操作系统层面不关心，仅提供一定程度支持

       8. 文件共享与访问控制

          1. 多用户系统中的文件共享
          2. 访问控制：
             1. 用户-访问权限：读写执行，删除、列表等
             2. ACL文件访问控制列表：<文件实体，权限>，对每个文件，每个用户有什么权限
                1. UNIX:<用户|组|所有人 ，读|写|可执行>
                2. 识别用户：用户标识ID，用户组标识ID
          3. 共享导致的语义一致性：
             1. 规定多进程如何同时访问文件：同步算法相似
             2. Unix UFS语义：写入文件内容其他用户立即可见；共享文件指针允许多用户同时读写；一致性问题交给应用程序处理
             3. 会话语义：写入内容只有当文件关闭时可见
             4. 读写锁：os和文件系统提供互斥锁

       9. 文件系统：

          1. 分层目录：目录内容是索引表 <文件名, 指向文件的指针>，树形结构。

             <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022203715302.png" alt="image-20201022203715302" style="zoom:50%;" />

          2. 操作系统应只允许内核修改目录，保证映射完整性，通过系统调用访问目录

          3. 目录实现：线性列表 or 哈希表

          4. 文件别名（两个或多个文件关联同一个文件），方便共享，节省存储空间。硬链接删到最后一个才会删除源文件，软连接删除别名不影响源文件，删除源文件则软连接不可用![image-20201022203940928](/Users/mac/Library/Application Support/typora-user-images/image-20201022203940928.png)

          5. 文件目录的循环：

             1. 只允许到文件的链接，不允许子目录链接
             2. 增加链接时，用循环检测算法确定是否合理
             3. 实际：限制可遍历文件目录的数量

          6. 名字解析（路径解析）：根据路径找到实际文件位置。根目录在磁盘固定位置，按每一集读取全体数据块。pwd当前工作目录（default解析）

          7. 文件系统挂载：文件系统需要挂载才可以被访问，<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022204421163.png" alt="image-20201022204421163" style="zoom:50%;" />

          8. 文件系统种类：

             1. 磁盘文件系统：FAT，NTFS，ext2/3，ISO9660等，多次读写修改
             2. 数据库文件系统：基于文件特征被检索（WinFS）
             3. 日志文件系统：记录文件系统的修改和事件，防止损坏与丢失
             4. 网络/分布式文件系统:NFS,SMB,AFS
             5. 特殊的文件系统

          9. 分布式：文件可以网络共享，文件位于远程服务器，客户端挂载远程服务器文件系统。NFS for Unix，CIFS for windows，NFS不安全，一致性问题，错误处理更复杂。

       10. 虚拟文件系统VFS：

          1. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022211036074.png" alt="image-20201022211036074" style="zoom:50%;" />

          2. 目标：针对所有不同文件系统的抽象

          3. 功能：

             1. 提供相同的文件和文件系统的接口
             2. 管理所有文件和文件系统关联的数据结构
             3. 高效查询例程，遍历文件系统
             4. 对特定的文件系统模块的交互

          4. 基本数据结构：

             1. 文件卷控制块（超级块superblock）：每个文件系统有一个，描述文件系统详细信息（块，块大小，空余，计数等）

             2. 文件控制块（vnode or inode）：每个文件一个，描述文件详细信息

             3. 目录项（dentry）：每个目录项一个，将目录项数据结构及树形布局编码成树型数据结构，指向文件控制块，父目录子目录等

             4. vol文件卷控制块，dir目录项，file文件（控制块），实际数据块。卷控制块位置固定。![image-20201022211443445](/Users/mac/Library/Application Support/typora-user-images/image-20201022211443445.png)

                <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022211605967.png" alt="image-20201022211605967" style="zoom:50%;" />

             5. 存储视图：![image-20201022211711667](/Users/mac/Library/Application Support/typora-user-images/image-20201022211711667.png)

          5. 文件缓存和打开文件：

             1. 磁盘控制器完成磁盘扇区读写，内存数据块缓存和内存虚拟盘（虚拟逻辑磁盘），打开文件表每一项对应一个文件。![image-20201022212105769](/Users/mac/Library/Application Support/typora-user-images/image-20201022212105769.png)
             2. 数据块的缓存：反向于内存换出
             3. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022212212964.png" alt="image-20201022212212964" style="zoom:50%;" />
             4. ![image-20201022212320266](/Users/mac/Library/Application Support/typora-user-images/image-20201022212320266.png)
             5. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022212430575.png" alt="image-20201022212430575" style="zoom:50%;" />
             6. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022212459605.png" alt="image-20201022212459605" style="zoom:50%;" />
             7. 维护相关的数据结构：
                1. 文件描述符：每一个文件都有
                2. 保存相关文件信息（目录项，当前文件指针，文件操作设置等）
                3. 打开文件表：每个进程一个打开文件表，os有一个系统打开文件表，如果某一文件卷文件被打开，则文件卷不能被卸载。进程中相同的打开文件表项映射到系统的打开文件表的同一项中
                4. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022212713403.png" alt="image-20201022212713403" style="zoom:50%;" />
             8. 打开文件锁：多个进程共享一个文件时的协调
                1. 强制：访问文件时通过锁和访问请求决定如何操作
                2. 劝告：进程查找锁后决定如何做

          6. 文件大小：

             1. 大多数文件很少：块空间不能太大，需要对小文件提供较好的支持
             2. 一些文件很大：必须支持大文件（64b偏移），大文件访问需要高效

          7. 文件分配：如何表示分配一个文件数据块的位置和顺序，分配方式：连续，链式，索引。指标：存储效率（外部碎片等），读写性能（访问速度）。

          8. ![image-20201022215509696](/Users/mac/Library/Application Support/typora-user-images/image-20201022215509696.png)

          9. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022215955924.png" alt="image-20201022215955924" style="zoom:50%;" />

          10. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022220329402.png" alt="image-20201022220329402" style="zoom:50%;" />

          11. ![image-20201022220417846](/Users/mac/Library/Application Support/typora-user-images/image-20201022220417846.png)

          12. unix file system（UFS）：<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022220603333.png" alt="image-20201022220603333" style="zoom:50%;" />

          13. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022220736132.png" alt="image-20201022220736132" style="zoom:50%;" />

          14. 空闲空间管理

              1. 空闲空间组织：位图，大向量表
              2. 链表法，链式索引

          15. RAID：

              1. 磁盘分区（磁盘通过分区最大限度减少寻道时间），分区是一组柱面的集合，每个分区都可以视为逻辑上独立的磁盘。

              2. 文件卷：一个拥有完整文件系统实例的外存空间，通常常驻在磁盘的单个分区上，不能提高读写性能和可靠性

                 <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022222419648.png" alt="image-20201022222419648" style="zoom:50%;" />

              3. 多磁盘管理：多磁盘来改善吞吐量，可靠性，可用性

              4. 冗余实现：软件（os内核的文件卷管理），硬件（RAID硬件控制器（I/O））

              5. RAID-0：磁盘条带化（独立，逻辑分区不起作用）<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022222645705.png" alt="image-20201022222645705" style="zoom:50%;" />

              6. RAID-1：向两个磁盘写入，从任何一个读取<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022222722693.png" alt="image-20201022222722693" style="zoom:50%;" />

              7. RAID-4：可靠性提高，不如RAID-1可靠性高：<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022222804763.png" alt="image-20201022222804763" style="zoom:50%;" />

              8. RAID-5：校验和存放分布<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022222857848.png" alt="image-20201022222857848" style="zoom:50%;" />

              9. ![image-20201022222956289](/Users/mac/Library/Application Support/typora-user-images/image-20201022222956289.png)

              10. <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022223012209.png" alt="image-20201022223012209" style="zoom:50%;" />

              11. RAID嵌套：<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201022223112667.png" alt="image-20201022223112667" style="zoom:50%;" />

32. IO子系统

    1. IO设备：

       1. 字符设备（慢，键盘鼠标串口）：字节为单位，顺序访问；IO命令get(), put()，使用文件访问接口和语义
       2. 块设备（磁盘驱动器，磁带驱动器，光驱）：以数据块为单位，访问均匀且数据量较大，使用原始IO接口或文件接口，也可以将磁盘映射到内存中。
       3. 网络设备（以太网、无线、蓝牙）：格式化报文交换，send/receive网络报文，通过网络接口支持多种协议

    2. 同步与异步I/O：

       1. 用户IO请求 -> 设备驱动 -> 硬件控制 -> 中断 -> 返回

       2. 阻塞I/O：“wait”直到返回，请求时绕过中断阶段，返回时通过中断进行系统调用返回。<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201027203423081.png" alt="image-20201027203423081" style="zoom:50%;" />

       3. 非阻塞I/O：不等待，对于读写操作立即返回读或写字节数（可能失败为0）![image-20201027203554139](/Users/mac/Library/Application Support/typora-user-images/image-20201027203554139.png)

       4. 异步I/O：系统调用通知设备驱动，设备驱动控制硬件设备操作，不等待结果直接返回，设备完成操作后中断通知应用程序。

          <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201027203725758.png" alt="image-20201027203725758" style="zoom:50%;" />

       5. 

cr