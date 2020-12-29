##ucore_lab1:

1. 硬盘主引导扇区大小512B，空余用0填充，文件内容不超过510b，最后2b为 `0x55`和`0xAA`

2. 加电后干了什么：

   1. 加载bin/kernel（符号信息）
   2. 刚开始BIOS为8086的16位实模式
   3. 0x7c00为主引导程序入口地址，与bootasm.S一致

3. BootLoader进入保护模式（开启32位地址空间，即寻址方式产生变化）

   1. 开启A20：开启A20后用来表示内存地址的位数增多，不开启前只能寻址到1M，1M以上会变为$address \% 1M$。

   2. 初始化GDT表（全局描述符表）：保护模式含有段模式和页模式，GDT为段模式下各个段的描述符![img](https://img2020.cnblogs.com/blog/1424296/202004/1424296-20200422204555394-1475376681.png)

      | G    | 粒度位，                         | G位为0时，段界限以字节为单位，段的扩展范围1B~1MB;G位为1时，段界限以4KB为单位，段的扩展范围4KB~4GB. |
      | ---- | -------------------------------- | ------------------------------------------------------------ |
      | S    | 指定描述符的类型                 | S位为0时，表示系统段；S位为1时，表示代码段或数据段，栈段也是特殊的数据段。 |
      | DPL  | 特权级别                         | 共有4种处理器支持的特权级别，0，1，2，3；0是最高级别，3是最低级别；描述符的特权级用于指定访问该段所必须的最低特权级别，如果这里的数值为2，那么只有特权级别为0，1，2的程序才能访问该段，特权级别为3的程序访问该段时，将会被阻止。<br />Ring0：内核，Ring3：用户 |
      | P    | 段存在位                         |                                                              |
      | D/B  | 默认的操作数大小                 |                                                              |
      | L    | 64位代码段标志                   | 保留此位留给64位处理器使用                                   |
      | TYPE | 指示描述符的子类型，或者说是类别 | 对于数据段，这4位分别是X，E，W，A；对于代码段，这4位分别是X，C，R，A；TYPE中最高位为1表示代码段，最高位为0表示数据段。 |
      | AVL  | 软件可以使用的位                 | 操作系统来用，处理器并不使用它                               |

   3. 段选择子：在实模式下, 逻辑地址由段选择子和段选择子偏移量组成. 其中, 段选择子16bit, 段选择子偏移量是32bit。在段选择子中，其中的INDEX[15:3]是GDT的索引。TI[2:2]用于选择表格的类型，1是LDT，0是GDT。RPL[1:0]用于选择请求者的特权级，00最高，11最低。![selector](https://img2018.cnblogs.com/blog/1100338/201908/1100338-20190801141938292-315771677.png)

   4. lgdt固定保存GDT入口地址：将全局描述符表描述符加载到全局描述符表寄存器`lgdt gdtdesc`

   5. 使能进入保护模式：

      ```
      * bootloader开始运行在实模式，物理地址为0x7c00,且是16位模式
      * bootloader关闭所有中断，方向标志位复位，ds，es，ss段寄存器清零
      * 打开A20使之能够使用高位地址线
      * 由实模式进入保护模式，使用lgdt指令把GDT描述符表的大小和起始地址存入gdt寄存器，修改寄存器CR0的最低位（orl $CR0_PE_ON, %eax）完成从实模式到保护模式的转换，使用ljmp指令跳转到32位指令模式
      * 进入保护模式后，设置ds，es，fs，gs，ss段寄存器，堆栈指针，便可以进入c程序bootmain
      ```

4. bootloader如何读取硬盘扇区的

   ```markdown
   * bootloader进入保护模式并载入c程序bootmain
   * bootmain中readsect函数完成读取磁盘扇区的工作，函数传入一个指针和一个uint_32类型secno，函数将secno对应的扇区内容拷贝至指针处
   * 调用waitdisk函数等待地址0x1F7中低8、7位变为0,1，准备好磁盘
   * 向0x1F2输出1，表示读1个扇区，0x1F3输出secno低8位，0x1F4输出secno的8~15位，0x1F5输出secno的16~23位，0x1F6输出0xe+secno的24~27位，第四位0表示主盘，第六位1表示LBA模式，0x1F7输出0x20
   * 调用waitdisk函数等待磁盘准备好
   * 调用insl函数把磁盘扇区数据读到指定内存
   ```

5. bootloader是如何加载ELF格式的OS

   ```markdown
   bootloader通过bootmain函数完成ELF格式OS的加载。
   
   * 调用readseg函数从kernel头读取8个扇区得到elfher
   * 判断elfher的成员变量magic是否等于ELF_MAGIC，不等则进入bad死循环
   * 相等表明是符合格式的ELF文件，循环调用readseg函数加载每一个程序段
   * 调用elfher的入口指针进入OS
   ```

6. 中断描述符表（也可简称为保护模式下的中断向量表）中一个表项占多少字节？其中哪几位代表中断处理代码的入口？

   从 `kern/mm/mmu.h` 的50-60行可以看出：IDT为8B的描述符数组，0-15位为段偏移的0-15位，16-31位为段选择子，48-63位为段偏移的16-31位，共同决定代码入口。中断处理代码的入口为第一字节和最后一个字节组成的地址。

   SETGATE(gate, istrap, sel, off, dpl)

   ```c
    extern uintptr_t __vectors[];
       int i;
       for(i = 0;  i < 256; ++i){
           SETGATE(idt[i],0,GD_KTEXT,__vectors[i],DPL_KERNEL);
       }   
       SETGATE(idt[T_SWITCH_TOK],0,GD_KTEXT,__vectors[T_SWITCH_TOK],DPL_USER);
       lidt(&idt_pd); 
   /*
       传入的第一个参数gate是中断的描述符表
       传入的第二个参数istrap用来判断是中断还是trap
       传入的第三个参数sel的作用是进行段的选择
       传入的第四个参数off表示偏移
       传入的第五个参数dpl表示这个中断的优先级
   */
   ```

   ![img](http://images.51cto.com/files/uploadimg/20081225/132725480.jpg)



## SPOC

1. 完成对`时钟，串口，并口，CGA`键盘-外设的访问

2. cprintf通过`串口-并口-CGA`完成对字符串的输出

   1. c可变参数：va:variable-argument可变参数

   ```c
   /*
   va_list:用来保存宏va_start、va_arg和va_end所需信息的一种类型。为了访问变长参数列表中的参数，必须声明va_list类型的一个对象       
   */
   typedef struct {
           char *a0;       /* pointer to first homed integer argument */
           int offset;     /* byte offset of next parameter */
   } va_list;
   
   
   /*
   va_start:访问变长参数列表中的参数之前使用的宏，它初始化用va_list声明的对象，初始化结果供宏va_arg和va_end使用；
   ap初始化，第一个参数为ap，第二个参数prev_param为参数表第一个参数地址
   */
   #define va_start(ap,v)  ( ap = (va_list)&v + _INTSIZEOF(v) )
   void va_start( va_list arg_ptr, prev_param );
   
   
   /*
   va_arg: 展开成一个表达式的宏，该表达式具有变长参数列表中下一个参数的值和类型。每次调用va_arg都会修改用va_list声明的对象，从而使该对象指向参数列表中的下一个参数；
   第一个参数是ap，第二个参数是要获取的参数的指定类型，并返回这个指定类型的值，
   */
   #define va_arg(ap,t)    ( *(t *)((ap += _INTSIZEOF(t)) - _INTSIZEOF(t)) )
   type va_arg( va_list arg_ptr, type );
   
   
   /*
   va_end:该宏使程序能够从变长参数列表用宏va_start引用的函数中正常返回。
   置ap为NULL
   */
   #define va_end(ap)      ( ap = (va_list)0 )
   void va_end( va_list arg_ptr );
   
   ```

3. 用户态ring3，内核态ring0

4. ```
   CR0 是系统内的控制寄存器之一。控制寄存器是一些特殊的寄存器，它们可以控制CPU的一些重要特性。
        0位是保护允许位PE(Protedted Enable)，用于启动保护模式，如果PE位置1，则保护模式启动，如果PE=0，则在实模式下运行。
        1位是监控协处理位MP(Moniter coprocessor)，它与第3位一起决定：当TS=1时操作码WAIT是否产生一个“协处理器不能使用”的出错信号。第3位是任务转换位(Task Switch)，当一个任务转换完成之后，自动将它置1。随着TS=1，就不能使用协处理器。
        2位是模拟协处理器位 EM (Emulate coprocessor)，如果EM=1，则不能使用协处理器，如果EM=0，则允许使用协处理器。
        4位是微处理器的扩展类型位 ET(Processor Extension Type)，其内保存着处理器扩展类型的信息，如果ET=0，则标识系统使用的是287协处理器，如果 ET=1，则表示系统使用的是387浮点协处理器。
        31位是分页允许位(Paging Enable)，它表示芯片上的分页部件是否允许工作。
        16位是写保护未即WP位(486系列之后)，只要将这一位置0就可以禁用写保护，置1则可将其恢复。
   
   
   CR1是未定义的控制寄存器，供将来的处理器使用。
   
   CR2是页故障线性地址寄存器，保存最后一次出现页故障的全32位线性地址。
   
   CR3是页目录基址寄存器，保存页目录表的物理地址，页目录表总是放在以4K字节为单位的存储器边界上，因此，它的地址的低12位总为0，不起作用，即使写上内容，也不会被理会。
   ```

5. ```
   段选择
   DPL：描述符特权（Descriptor Privilege Level）
   RPL：请求特权级RPL(Request Privilege Level)
   CPL：当前任务特权（Current Privilege Level）
   
   特权级数值与特权级大小成反比
   
   访问门：CPL <= DPL[门] && CPL >= DPL[段]
   中断、陷入、异常称为门，访问要求门的特权级低于当前代码段（才能访问），以便访问门后特权级更高的段
   
   访问段：MAX(CPL, RPL) <= DPL[段]
   访问段要求当前代码段特权级高于待访问段（段保护）
   ```

   

6. x86特权级切换：

   1. ring 0  to ring 3：从内核态模拟一个应用程序状态的特权级（RPL=3，CPL=3）并压栈，调用IRET指令弹出来切换至应用程序状态。
   2. ring 3 to ring 0：构造软中断，IDT建立中断门，压应用程序此刻的堆栈（SS，ESP删除，CS中CPL=0），然后调用IRET弹出来切换至内核态。
   3. 任务状态段TSS保存了不同特权级使用的各类信息。3to0时，地址、堆栈均变换（由不同硬件机构保存）。全局描述符表中有一项为TSS基址。访问TSS时硬件去找，软件去填写TSS内容。