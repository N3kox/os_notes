os笔记-2

1. IO子系统

   1. IO结构：

      1. 北桥：内存，显卡，速度为若干个G，北桥连高速设备
      2. 南桥：各类设备，南桥连IO设备<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201027214609934.png" alt="image-20201027214609934" style="zoom:50%;" />
      3. 细化CPU与设备的识别：
         1. 设备上有设备控制器，设备控制器为CPU和IO设备间的接口，向CPU提供特殊指令和寄存器
         2. IO地址：CPU使用IO地址来控制IO硬件，映射为内存地址或IO空间端口
         3. 轮询，设备中断，DMA<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201027214849208.png" alt="image-20201027214849208" style="zoom:50%;" />
      4. IO指令与内存映射IO：
         1. IO指令：通过IO端口号访问设备寄存器，并执行特殊的CPU指令：如直接对指定的端口发出写操作（out 0x21, AL)
         2. 内存映射IO：设备的寄存器/存储被映射到内存物理地址空间中，通过内存load/store指令完成IO操作，MMU设置映射，或硬件跳线或程序在启动时设置地址
      5. 内核IO结构：底层各类设备，上层对应其各自的设备控制器，再上层每一类设备的驱动，再上层IO子系统，最上层内核其他部分<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201027215317343.png" alt="image-20201027215317343" style="zoom:50%;" />
      6. IO请求生命周期：<img src="/Users/mac/Library/Application Support/typora-user-images/image-20201027215513418.png" alt="image-20201027215513418" style="zoom:50%;" />

   2. IO数据传输：

      1. CPU与设备控制器的数据传输：

         1. 程序控制IO(PIO):通过CPU的in/out或者load/store传输所有数据。特点是：硬件简单编程容易，但是消耗的CPU时间与数据量成正比，数据量大占用CPu多，适用于简单小型设备IO(字符设备)
         2. 直接内存访问（DMA)：设备控制器直接访问系统总线，控制器直接与内存互传数据。特点是：设备传输数据不影响CPU，需要CPU参与设置，适用于高吞吐量I/O（块设备）
         3. ![image-20201027220159272](/Users/mac/Library/Application Support/typora-user-images/image-20201027220159272.png)

      2. 设备通知系统：

         1. 轮询：IO设备定义状态和控制寄存器，放置状态和错误信息，OS定期检测状态寄存器，简单但不可预测，开销大延时长

         2. 设备中断：

            <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201027220324481.png" alt="image-20201027220324481" style="zoom:50%;" />

         3. 一些设备两种办法结合：高带宽网络设备，第一个传入前中断，之后轮询

         4. 中断IO处理流程

            <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201027220549600.png" alt="image-20201027220549600" style="zoom:50%;" />

2. 磁盘调度：

   1. 结构：![image-20201027221311585](/Users/mac/Library/Application Support/typora-user-images/image-20201027221311585.png)

   2. 寻道时间：定位到磁道花费的时间（最长）

   3. 旋转延迟：零扇区到指定位置的时间（平均为磁盘旋转一周时间的一半）

   4. 时间计算：$T_a = T_s + 1/2r + b/rN$，Ta访问时间，Ts寻道时间（磁头移动距离相关），1/2r旋转时间（平均），b/rN传输时间，b=传输比特数，N=磁道比特数，r=磁盘转数

   5. 磁盘调度算法：通过优化磁盘访问请求顺序来提高磁盘访问性能，原因为寻道时间最耗时，同时有多个IO请求，而随机处理效果差

   6. 算法：FIFO

      ![image-20201027221751794](/Users/mac/Library/Application Support/typora-user-images/image-20201027221751794.png)

   7. 最短服务时间优先（SSTF）![image-20201027221855053](/Users/mac/Library/Application Support/typora-user-images/image-20201027221855053.png)

   8. 扫描（SCAN）：磁头在一个方向上移动，访问所有未完成的请求，直到达到该方向最后的磁道，然后调换方向，也称为电梯算法。中间访问效果更好而两边访问较少![image-20201027222105150](/Users/mac/Library/Application Support/typora-user-images/image-20201027222105150.png)

   9. 循环扫描（C-SCAN）：限制SCAN只在一个方向上扫描，当最后一个磁道也被访问过后，磁头返回到磁盘的另一端再次进行，保证了两边的公平性

   10. C-LOOK：磁头只走到该方向上最后一个请求处，然后立即反转，而不是一直走到终点，其他与循环相同

   11. N步扫描（N-step-SCAN）：SSTF、SCAN、CSCAN等算法使磁头黏着于某处不动，而另外一些访问便一直没有机会，比如进程反复请求对某一磁道的IO操作。N步扫描将磁盘请求分为长度为N的子队列，按FIFO算法依次处理子队列，子队列中使用SCAN算法。

   12. 双队列扫描（FSCAN）：FSCAN是对N步扫描算法的简化，只将磁盘请求队列分成两个子队列，把磁盘IO请求分成两个子队列，交替使用扫描算法处理两个子队列。在处理一个队列时，所有新的请求放入到另一个队列中。

3. 磁盘缓存：

   1. 磁盘缓存是磁盘放在内存中的磁盘数据的缓存，为了避免对同一块扇区内容进行反复引用时的磁盘访问
   2. 数据双方访问速度差异较大，引入速度匹配中间层。
   3. ![image-20201027222920782](/Users/mac/Library/Application Support/typora-user-images/image-20201027222920782.png)
   4. 单缓存与双缓存：指缓冲区有一个或两个。单缓存互斥使用缓存区，速度受限；双缓存设置两个缓存区，一个缓存区操作时，另一个可以被其他设备访问使用。![image-20201027223048387](/Users/mac/Library/Application Support/typora-user-images/image-20201027223048387.png)
   5. 访问频率置换算法（Frequency-based Replacement）：密集访问磁盘LRU计数无法反应引用情况（即短周期使用LRU，长周期使用LFU）LRU首先淘汰最久未被使用的页面，LFU首先淘汰一定时间内访问频率最少的页面![image-20201027223314291](/Users/mac/Library/Application Support/typora-user-images/image-20201027223314291.png)
   6. ![image-20201027223753045](/Users/mac/Library/Application Support/typora-user-images/image-20201027223753045.png)
   7. 新数据块读入后引用计数至1，访问块同LRU操作一样将其移动至栈顶，从新区域移动引用计数不变，从中间区域和旧区域移动后引用计数加一，删缓存找旧区域中计数最小的数据块置换出![image-20201027223926049](/Users/mac/Library/Application Support/typora-user-images/image-20201027223926049.png)

