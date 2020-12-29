## os_lec6



## SPOC

1. 最优匹配，最差匹配，最先匹配，buddy systemm分配算法的优势和劣势:

   - 最优匹配算法总是把能满足要求的最小空闲分区分配出去。这种分配算法可以让碎片达到最小，但是为了能够快速找到最适合的内存块，需要将所有的空闲内存块管理起来，带来了一定的开销。同时，在内存空间分配一段时间后，会产生很多的小块的难以利用的内存碎片。
   - 最差匹配算法，和最优匹配相反，每次都找到最大的空闲块进行分配。好处是寻找内存块的速度非常快，同时内存碎片往往较大。
   - 最先匹配，该算法按照地址空间找到第一个能够满足要求的内存块。其优势时管理简单，同时倾向于保留高地址空间的内存给后期的大作业。缺点在于低地址部分不断被划分，变成很多小的空闲块，加大了查找的开销。
   - 伙伴算法将内存每次对半分，直到恰好大于需要分配的大小。Buddy System既有外碎片又有内碎片。伙伴算法极大的解决了内存的外碎片问题，但是一个很小的块可能就会阻止一个大块的回收。同时，算法有一定的浪费。对内存块的分配和释放开销也比较大。
   - 为了能够解决伙伴算法中的分配和回收开销问题，引入二级索引，一级索引由2的次幂构成，二级索引是对应的该次幂的线性增长。每个索引用位图中表明是否存在该大小区间的内存块。具体参见TLSF算法。

2. 操作系统中存储管理的目标：**抽象，保护，共享，虚拟化**

3. MMU的工作机理：MMU 通过页表寄存器查找到页表，然后对应页表中存储的虚拟地址空间到物理地址空间的映射关系，将虚拟地址空间映射到物理地址空间。

4. 内碎片、外碎片：内碎片是指分配给任务的内存大小比任务所要求的大小所多出来的内存。外碎片指分配给任务的内存之间无法利用的内存。

5. 最先匹配会越用越慢：总是先找**低地址空间**的内存，到后期低地址空间都是大量小的不连续的内存空间，每次都要扫描低地址空间后到达高地质空间才能得到可用的内存。

6. 最差匹配会的外碎片少：因为每次都找到最大的内存块进行分割，因此分割剩下的内存块也很大，往往还可以再装下一个程序。

7. 分区释放后的合并处理：查看边上是否也有空闲块，如果有，则合并空闲块，然后将空闲块管理数据插入链表中。

8. 紧凑是在内存中搬动进程占用的内存位置，以合并出大块的空闲块；对换是把内存中的进程搬到外存中，以空出更多的内存空闲块

9. 静态分配内存与动态分配内存的区别：静态内存分配发生在程序编译和链接过程中，动态分配则发生在程序调入和执行时。

10. 在隐式链表结构中，如何实现向前的合并操作：在内存块的末尾也放入一个size数据，以此找到前一个内存块的头部，并判断其是否空闲。

11. 如何判断一个函数是库函数还是一个系统调用：用strace可以跟踪所有的系统调用。同时，有些库函数最后也会调用系统调用。

12. 为何要在OS内部和用户态中实现两层动态内存分配？:**OS 才是系统资源的实际管理者，用户态的动态内存分配只是OS 提供给用户的一个资源管理接口，即用户态的的内存分配其实质也是调用OS内部的动态内存分配。但是有时为了能够达到性能等定制目的，也可能想内核申请一大块内存区域，并且在用户态实现一套内存分配机制。**

13. 为何在OS内部没有采用GC分配方式？:GC需要对所有的内存分配和释放进行跟踪，同时在进行内存释放的时候非常消耗资源，可能会导致系统运行速度缓慢。

14. 找内存page：

    ```c
    /*
    页大小32B = 2^5 -> 5b offset
    32KB虚拟空间 = 2^15 -> 15b虚拟地址长度
    4KB物理空间 = 2^12 -> 12b物理地址长度
    二级页表
    一级页表物理地址 = 0x220 = 0010 0010 0000 , addr >> 5 为 page基址 = 001 0001 = 0x11 即page 11
    每个页表32B = 2^5 -> 一级页表项 = 二级页表项 = 32个，用5b长度表示
    
    虚拟地址划分：
    | 一级页表项 | 二级页表项 | 物理page offset |
    
    page 11: da f7 f2 a8 96 c5 9d 94 c8 b9 7f c4 98 e5 7f 7f d3 a1 82 8f a6 fb bf f0 7f 84 d2 a0 88 80 c9 92 
    
    A.
    virtual addr = 0x6c74 = 0110 1100 0111 0100 = 11011 | 00011 | 10100
    pde index = 11011 = 0x1b
    pte index = 00011 = 0x03
    offset = 10100
    
    step 1:
    pde index = 11011 = 31 - 4 = 27 -> page 11 下标27，value = 0xA0
    0xA0 = 1010 0000 = 1 | 010 0000
    pde valid = 1
    pfn = 010 0000 = 0x20 -> page 20
    
    page 20: 7f 7f 7f e1 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f db 7f 7f 7f 
    step 2:
    pte index = 00011 = 3 -> page 20 下标3 ，value = 0xE1
    0xE1 = 1110 0001 = 1 | 110 0001
    pte valid = 1
    pfn = 110 0001 = 0x61 -> page 61
    
    page 61: 0f 0d 14 18 02 00 19 0d 17 00 0d 16 07 1d 1b 00 00 10 1d 0b 06 0d 00 06 0d 0f 07 07 06 0e 08 00 
    step 3:
    offset = 10100 = 20
    value = 0x06
    physical addr = (110 0001) << 5 + 10100 = 1100 0011 0100 = 0xC34
    
    
    B.
    virtual addr = 0x6b22 = 011010 11001 00010
    pde index = 11010 = 0x1A = 26
    pte index = 11001 = 0x19 = 25
    offset = 00010
    
    page 11: da f7 f2 a8 96 c5 9d 94 c8 b9 7f c4 98 e5 7f 7f d3 a1 82 8f a6 fb bf f0 7f 84 d2 a0 88 80 c9 92 
    step 1:
    pde index = 0x1A = 26
    val = d2 = 1101 0010
    pde valid = 1
    pfn = 101 0010 = 0x52
    
    page 52: 7f 7f 7f 7f 7f 7f 7f c6 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f c7 7f 7f df d1 7f 7f 
    step 2:
    pte index = 0x19 = 25
    val = 0xc7 = 1100 0111
    pte valid = 1
    pfn = 100 0111 = 0x47
    
    page 47: 05 1e 1a 03 0a 16 16 1d 0d 19 14 09 12 1b 1a 0f 12 01 07 18 0c 05 11 15 14 0b 0d 0f 18 10 0c 0f 
    step 3:
    offset = 00010 = 2
    val = 1a
    physical addr = (100 0111) << 5 + 00010 = 1000 1110 0010 = 0x8e2
    
    
    C.
    virtual addr = 03df = 000000 11110 11111
    pde index = 0
    pte index = 1 1110 = 0x1e
    offset = 11111 = 31
    
    page 11: da f7 f2 a8 96 c5 9d 94 c8 b9 7f c4 98 e5 7f 7f d3 a1 82 8f a6 fb bf f0 7f 84 d2 a0 88 80 c9 92
    step 1:
    val = da = 1 1011010
    pde valid = 1
    pfn = 1011010 = 0x5a
    
    
    page 5a: 7f 7f 7f b1 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 85 7f 
    step 2:
    val = 85 = 1 0000101
    pte valid = 1
    pfn = 0000101 = 0x05
    
    
    page 05: 1e 12 0c 05 0f 1e 17 10 1a 07 0f 1d 11 0e 08 10 1d 00 18 19 1b 16 19 10 11 0d 01 1a 11 06 0f 0f 
    step 3:
    val = 0f
    physical addr = 0000 1011 1111 = 0x0BF
    
    
    D.
    virtual addr = 0x69dc = 011010 01110 11100
    pde index = 11010 = 26
    pte index = 01110 = 14
    offset = 28
    
    page 11: da f7 f2 a8 96 c5 9d 94 c8 b9 7f c4 98 e5 7f 7f d3 a1 82 8f a6 fb bf f0 7f 84 d2 a0 88 80 c9 92 
    pde val = d2 = 1 1010010
    pde valid = 1
    pfn = 0x52
    page 52: 7f 7f 7f 7f 7f 7f 7f c6 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f c7 7f 7f df d1 7f 7f 
    pte val = 7f = 0 1111111
    pte valid = 0
    page table entry not valid
    
    
    E.
    virtual addr = 0x390e = 001110 01000 01110
    pde index = 01110 = 14
    pte index = 01000 = 8
    offset = 01110 = 14
    
    page 11: da f7 f2 a8 96 c5 9d 94 c8 b9 7f c4 98 e5 7f 7f d3 a1 82 8f a6 fb bf f0 7f 84 d2 a0 88 80 c9 92 
    pde val = 7f = 0 1111111
    pde valid = 0
    page directory entry not valid
    
    */
    ```

15. 
