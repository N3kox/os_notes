##OS_EXAM_2018

1. 进程执行系统调用，从用户态切换到内核态执行时，将切换页表和栈

   错，用户态到内核态不切换页表，直接使用映射的内核空间；

2. OS在建立页表并使能页机制时，需要特权指令才能最终完成。

   对，X86和MIPS使能页机制的指令都是特权指令

3. 由于栈的原因，在OS内核中不能执行系统调用（syscall）来获得OS内核的服务

   错，系统调用可以在同特权级下进行，此时不进行栈的切换

   

4. 在完成lab 1的过程中，通过分析硬件模拟器工具对CPU状态的输出信息，可了解到基于80386的计算机在加电后执行BIOS代码时处于（**2.1**）模式。而os lab 1中的bootloader通过建立（**2.2**）表可让计算机进入（**2.3**）模式，从而可以充分利用80386 CPU提供的保护能力和32位内存寻址空间。os lab 1中的ucore os为了能够对异常／中断等进行有效管理，需要建立（**2.4**）表，才能使能中断，让ucore os进行进一步的中断处理。在学习80386特权级时，对CPL、RPL和DPL需要满足如下两个公式确保系统安全：访问（**2.5**）时，CPL<=DPL[门] & CPL>=DPL[段]；访问（**2.6**）时，MAX(CPL, RPL)<=DPL。

   实模式（8086）；GDT表（段表）；保护模式；IDT表；中断门；段

   

5. 1.3在完成lab2的过程中，需要了解x86-32的内存大小与布局，页机制，页表结构等。硬件模拟器提供了128MB的内存，并设定页目录表的起始地址存放（**3.1**）寄存器中，页目录表和页表的地址按（**3.2**）字节对齐。在一个页目录表占用（**3.3**）个Byte，一个页表占用（**3.4**）个Byte。ucore
   通过x86-32 CPU中的（**3.5**）寄存器可以获得发生页面访问错误时的线性地址。

   CR3；4K；4K；4K；CR2

   

6. 在完成lab3的过程中，ucore操作系统在页机制基础上，并利用异常机制建立了虚存管理策略与机制。如果一个页（4KB/页）被置换到了硬盘某8个连续扇区（0.5KB/扇区），该页对应的页表项（PTE）的最低位——present（存在位）应该为（**4.1**），表示虚实地址映射关系不存在，而原来用来表示页帧号的高（**4.2**）位，恰好可以用来表示此页在硬盘上的起始扇区的位置（其从第几个扇区开始）。

   0；？

   

7. 在学习进程的概念中，了解到在支持多进程的操作系统（包括ucore)中，每个进程有两个堆栈，分别是（**5.1**）栈和（**5.2**）栈。操作系统通过建立（**5.3**）这个核心数据结构来支持对进程的管理。对于进程的三状态模型，是指进程在执行过程中会具有（**5.4**），（**5.5**），（**5.6**）三种状态。在操作系统具有进程地址空间为单位的swap in/out虚存管理机制，可建立进程的五状态模型，将增加（**5.7**），（**5.8**）。

   内核；用户；PCB；就绪--运行--等待；就绪挂起态；就绪等待态；

   

8. 在Linux环境下，下列程序调用`magic`函数的次数是多少？如果一个程序死循环调用`fork()`系统调用，会出现什么情况？请说明原因。

   ```
   Copy#include <stdio.h>
   #include <unistd.h>
   main()
   {
       int i;
       for (i = 0; i < 10; i++)
           fork();
       magic();
   }
   ```

   共计fork出1024个进程（包含父进程），执行magic 1024次。机器不会死机，但是无法创建新的程序了，因为进程控制块资源耗尽了。这不会导致失去对电脑控制权，仍然可以通过Ctrl+C终止程序。

   

9. 用户线程是指由一组用户线程管理库函数来完成线程的管理功能，包括线程的创建、终止、同步和调度等。假设处于仅通过用户线程管理库管理用户线程的操作系统环境，请回答下列问题：

   1. 操作系统内核是否需要知道用户线程的存在？请说明理由。
   2. 用户线程管理库实现的线程切换是否需要进入内核态，通过操作系统内核来完成？请说明理由。
   3. 用户态线程管理库是否可以随时打断用户态线程，完成线程调度与切换？请阐述理由或方法。

   ------

   1. OS内核不需要知道用户库维护的线程的存在，如果它知道，也就没有用户线程的意义了，变成了内核线程。

   2. 线程切换不需要进入内核态，因为线程的页表是共享的，其他现场信息不需要特权指令来保存，所以可以在用户态切换。

   3. 能，因为OS可以通知线程管理库发生中断（发出软件中断）。也可以回答不能，因为在用户态不能实现中断。重点是自圆其说。

      

10. 在一个只有一级页表的请求页式存储管理系统中，假定页表内容如下表：

    | 页号 | 页框（Page Frame）号 | 有效位（存在位） |
    | :--: | :------------------: | :--------------: |
    |  0   |         123H         |        1         |
    |  1   |         N/A          |        0         |
    |  2   |         254H         |        1         |

    页面大小为4KB，一次内存的访问时间是100ns，一次快表（TLB）的访问时间是10ns，处理一次缺页的平均时间为1e7ns（己经包含更新TLB和页表的时间），进程的驻留集大小固定为2，采用最近最少使用置换算法(LRU)和局部淘汰策略。假设：

    - TLB初始为空；
    - 地址转换时先访问TLB，若TLB没有命中，再访问页表（忽略访问页表之后的TLB更新时间）；
    - 有效位为0表示页面不在内存，产生缺页中断，缺页中断处理后，返回到产生缺页中断的指令处重新执行。

    设有虚地址访问序列2362H，1565H，25A5H，请问：

    1. 依次访问上述三个虚地址，各需要多少时间？给出计算过程？
    2. 基于上述访问序列，虚地址1565H的物理地址是多少？请说明理由。

    ------

    访问2362H：页号为2，偏移量为362H。查找TLB未命中（10ns），查找页表得到页框号为254H（100ns），更新TLB不耗时，物理地址为254362H，访存(100ns)，总耗时210ns。

    访问1565H：页号为1，offset = 362H，查找TLB未命中（10ns），查找页表未命中（100ns），缺页中断（1e7ns），根据LRU将第0页换出置存在位为0，将第1页换入页号为123H的页框中，有效位至1，更新TLB和页表，返回到缺页中断的指令再执行，查找TLB命中（10ns），访存（100ns），物理地址123565H，总耗时1e7ns

    访问25A5H：页号为2，offset = 5A5H，查找TLB命中（访问2362H写回TLB，10ns），访存（100ns），物理地址2545A5H，总耗时110ns

    虚地址1565H在上述访问序列完成后：页号1，查找TLB命中（1565H），物理地址123565H

    

11. 2017年图灵奖得主John L. Hennessy和David A. Patterson提出了RISC-V架构的32位小端序CPU设计，它有34位地址总线，使用32位页式存储管理。该计算机的页面大小为4KiB，一个页表大小为4KiB，其中每一个页表项(Page Table Entry，PTE)大小为4B，虚拟地址、物理地址和PTE的结构如下图所示。

    32-bit的RISC-V架构CPU使用34位物理地址而不是32位物理地址，这样做的好处是什么？

    34位物理地址可以寻址16G的内存。

    

    设页目录基址为0x90000000，部分物理内存的内容如下图所示，试给出虚拟地址0x3A69A4D2和0x3A8EB00C所对应的物理地址和它们所在页的类型。请写出计算过程。

    ![虚拟地址、页表项和物理地址结构](https://zhanghuimeng.github.io/post/os-mooc-2018-midterm-summary/page_table_structure.png)

    如上图所示，一个虚拟地址由虚拟页号(Virtual Page Number，VPN)和页内偏移组成，物理地址由物理页号(Physical Page Number，PPN)和页内偏移组成，PTE由PPN和一些控制位组成，其中R/W/X三个域分别表示对应页的读/写/执行权限，它们的不同组合可以表示不同的属性，如下表所示：

    | X    | W    | R    | Meaning                                      |
    | ---- | ---- | ---- | -------------------------------------------- |
    | 0    | 0    | 0    | This PTE points to next level of page table. |
    | 0    | 0    | 1    | Read-only page.                              |
    | 0    | 1    | 0    | Reserved for future use.                     |
    | 0    | 1    | 1    | Read-write page.                             |
    | 1    | 0    | 0    | Execute-only page.                           |
    | 1    | 0    | 1    | Read-execute page.                           |
    | 1    | 1    | 0    | Reserved for future use.                     |
    | 1    | 1    | 1    | Read-write-execute page.                     |

    <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201122212256265.png" alt="image-20201122212256265" style="zoom:50%;" />

    PDE = 0x90000000

    页表项大小4B = 2^2

    **小端序**

    A.

    虚拟地址0x3A69A4D2：0011 1010 0110 1001 1010 0100 1101 0010

    VPN[1]: 00 1110 1001 = E9H

    VPN[0]: 10 1001 1010 = 29AH

    offset = 0100 1101 0010 = 4D2H

    pde addr = 0x90000000 + E9 << 2 = 1001 0000 0000 0000 0000 0011 1010 0100 = 0x900003A4

    index 4到7，小端反置val：28 00 00 01 H

    00 0000 0001 -> XWR = 000 PTE指向二级页表

    

    二级页表的物理地址（34位）由PPN[1]PPN[0]还有VPN[0](VPN[0}同样需要左移两位）

    0010 1000 0000 | 0000 0000 00 | VPN[0] << 2 = 1010 0110 1000 -> 0x0A0000A68

    37 AB 6C 09 

    控制位0000001001，XWR = 100，指向一个可执行的页面

    0011 0111 1010 | 1011 0110 11 | 0100 1101 0010 = 0xDEADB4D2 真实物理地址

    

    B.

    虚拟地址0x3A8EB00C：00 1110 1010 | 00 1110 1011 | 0000 0000 1100

    VPN[1] = 0x0EA

    VPN[0] = 0x0EB

    offset = 0x00C

    pde addr = 0x9000 0000 + EA << 2 = 0x9000 03A8

    index 8到B,小端反置val：3E B0 00 0F

    PFN[1] = 0011 1110 1011

    PFN[0] = 0000 0000 00

    FLAG = 00 0000 1111

    XWR = 111，可读可写执行页

    物理地址：PPN[1] | VPN[0] | offset

    00 1111 1010 11 | 00 1110 1011 | 0000 0000 1100

    物理地址：0xFACE B00C

    

    

    第二题就比较复杂了。首先计算出两个虚拟地址对应的各项。由于单个页表项的大小是4B，可以通过VPN[1]计算出页表项所在的地址为`0x90000000+4*VPN[1]`，并读出页表项（注意是**小端**存储）。

    | 虚拟地址   | VPN[1] | VPN[0] | offset | PDE地址    | PDE VAL    |
    | ---------- | ------ | ------ | ------ | ---------- | ---------- |
    | 0x3A69A4D2 | 0xE9   | 0x29A  | 0x4D2  | 0x900003A4 | 0x28000001 |
    | 0x3A8EB00C | 0xEA   | 0xEB   | 0x00C  | 0x900003A8 | 0x3EB0000F |

    可以发现，0x28000001的XWR=000，因此它是一个一级页表项，指向的是一个二级页表，它的基地址是0xA0000000。二级页表项的地址`=0xA0000000+4*VPN[0]=0xA0000A68`，读出二级页表项为0x37AB6C09，它指向一个可执行的页，页的基地址为0xDEADB000。物理地址=页基地址+偏移量=0xDEADB000+0x4D2=0xDEADB4D2。

    而0x3EB0000F的XWR=111，也就是说，它指向一个可写可读可执行的页。不妨进行大胆的猜测：这个页的大小是4MB，虚拟地址中的`VPN[0]`和offset共同作为页内的偏移量；而页表项中的`PPN[1]`就是页基址的高12位。由此可得，页基址`=0xFAC00000`，物理地址=页基址+偏移量`=0xFAC00000+0xEB00C=0xFACEB00C`。

    

