## os_lec7

## SPOC

1. x84四个特权级，通常使用ring3和ring0，特权指令只能在ring0使用

2. int指令在ring0和ring3的执行行为有什么不同：A.压栈内容是不同的，多了一个SS:ESP的压栈；B.进行了栈切换

3. 如何利用int和iret指令完成不同特权级的切换：人工构造需要的栈结构，然后通过int和iret指令进行切换

4. 页表自映射：**核心点：连续放置**

   快速运算：

   **1.起始地址>>22 = Frame位置**

   **2.起始地址 + Frame << 12 = 自映射页表地址**

   **3.起始地址 + Frame << 12 + Frame << 2 = 自映射页表项虚拟地址**

   ```c
   /*
   假设虚拟地址空间4GB，页面大小4KB（即12位offset），每个页表项4B
   即任何一个页面有1K个页表项，4GB可以被4KB分割成1M个页面
   为映射这个整体，使用二级页表进行映射，页目录可以映射1K个页表，每个页表可以映射1K个物理页面（即4MB物理空间）
   1K * 1K = 1M，故可以完全映射
   此时页目录占空间4KB，二级页表占空间 1K*4KB = 4MB
   
   
   对于一个页目录项，这个页目录项记录了某张二级页表页面虚实转化关系
   对于一个二级页表，其包含1K个页表项，每个表项记录了此项到4KB物理页面的转化关系
   此时二级页表本身也保存在某个物理页面中，即有某一个二级页表，记录了整个二级页表的虚实地址转化关系
   此时为了节省空间，可以直接使用这个特殊的二级页面作为页目录，此时不需要额外的页目录空间（4KB）
   
   */
   ```

   <img src="https://img-blog.csdn.net/20180514153738961?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3UwMTA1MTMwNTk=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70" alt="自映射时的页表结构" style="zoom:30%;" />

   

   A.
   一个32位的虚拟存储系统有两级页表，其逻辑地址中，10位一级页表，10位二级页表，12位offset。
   一个进程的地址空间为4GB，从0x80000000开始映射4MB大小页表空间。

   起始空间0x8000 0000 ，一个Frame 4MB大小，换算为Table Frame:
   $$
   \frac{0x8000\ 0000}{4MB} = 0x8000\ 0000 >> 22 = 0x10 0000 0000 = 0x200
   $$
   即自映射页表位于Table Frame第0x200个即512个frame，则页目录位于table frame 512，页目录地址即第512个页表的地址，一个页表大小为4KB，故：
   $$
   0x8000\ 0000 + (0x200 << 12) = 0x8000\ 0000 + 0x20\ 0000 = 0x8020\ 0000
   $$


   指向第512个tabel的页目录项Entry可以计算（一个页面4B）：
   $$
   0x8020\ 0000 + (0x200 << 2) = 0x8020\ 0800
   $$


   B.

   4KB页面大小、两级页表、页表自映射的虚拟存储系统。如果在虚拟地址空间中，4MB 的页表区域从虚拟地址 0xD0000000 开始，请回答自映射页表项的虚拟地址。

   起始空间0xD000 0000, 一个Table Frame 4MB，换算：
   $$
   0xD000\ 0000 >> 22 = 1101000000 = 0x340 = 512 + 256 + 64 = 832
   $$
   自映射页表即页目录位于第832个Table Frame，页目录地址即第832个页表的地址：
   $$
   0xD000\ 0000 + 0x340 << 12 = 0xD034\ 0000
   $$
   指向第832个table的页目录项Entry（在0xD034 0000所指向的二级页表中指向第832个页表的虚拟地址）：
   $$
   0xD034\ 0000 + (0x340 << 2) = 0xD034\ 0D00
   $$
   <img src="/Users/mac/Library/Application Support/typora-user-images/image-20201122203753003.png" alt="image-20201122203753003" style="zoom:50%;" />

   ![image-20201122203815820](/Users/mac/Library/Application Support/typora-user-images/image-20201122203815820.png)

   

