## OS_LAB3



### 给未被映射的地址映射上物理页

 `do_pgfault` 函数，给未被映射的地址映射上物理页。

 `do_pgfault` 函数的思路：`do_pgfault()` 函数从 `CR2` 寄存器中获取页错误异常的虚拟地址，根据 `error code` 来查找这个虚拟地址是否在某一个 `VMA` 的地址范围内，在就给它分配一个物理页。

page_fault 函数不知道哪些是“合法”的虚拟页，原因是 `ucore` 还缺少一定的数据结构来描述这种不在物理内存中的“合法”虚拟页。为此 `ucore` 通过建立 `mm_struct` 和 `vma_struct` 数据结构，描述了 `ucore` 模拟应用程序运行所需的合法内存空间。当访问内存产生 page fault 异常时，可获得访问的内存的方式（读或写）以及具体的虚拟内存地址，这样 `ucore` 就可以查询此地址，看是否属于 `vma_struct` 数据结构中描述的合法地址范围中，如果在，则可根据具体情况进行请求调页/页换入换出处理；如果不在，则报错。

```c
struct mm_struct {  
    list_entry_t mmap_list;  //双向链表头，链接了所有属于同一页目录表的虚拟内存空间
    struct vma_struct *mmap_cache;  //指向当前正在使用的虚拟内存空间
    pde_t *pgdir; //指向的就是 mm_struct数据结构所维护的页表
    int map_count; //记录 mmap_list 里面链接的 vma_struct 的个数
    void *sm_priv; //指向用来链接记录页访问情况的链表头
};  

struct vma_struct {  
    struct mm_struct *vm_mm;  //指向一个比 vma_struct 更高的抽象层次的数据结构 mm_struct 
    uintptr_t vm_start;      //vma 的开始地址
    uintptr_t vm_end;      // vma 的结束地址
    uint32_t vm_flags;     // 虚拟内存空间的属性
    list_entry_t list_link;  //双向链表，按照从小到大的顺序把虚拟内存空间链接起来
}; 

// vm_flags
define VM_READ 0x00000001 //只读
define VM_WRITE 0x00000002 //可读写
define VM_EXEC 0x00000004 //可执行v
  
```



```c
int do_pgfault(struct mm_struct *mm, uint32_t error_code, uintptr_t addr) {
    int ret = -E_INVAL;
    //try to find a vma which include addr
    struct vma_struct *vma = find_vma(mm, addr);//查询 vma

    pgfault_num++;
    //If the addr is in the range of a mm's vma?
    if (vma == NULL || vma->vm_start > addr) {
        cprintf("not valid addr %x, and  can not find it in vma\n", addr);
        goto failed;
    }
    //check the error_code
    switch (error_code & 3) {//错误处理
    default:
            /* error code flag : default is 3 ( W/R=1, P=1): write, present */
    case 2: /* error code flag : (W/R=1, P=0): write, not present */
        if (!(vma->vm_flags & VM_WRITE)) {
            cprintf("do_pgfault failed: error code flag = write AND not present, but the addr's vma cannot write\n");
            goto failed;
        }
        break;
    case 1: /* error code flag : (W/R=0, P=1): read, present */
        cprintf("do_pgfault failed: error code flag = read AND present\n");
        goto failed;
    case 0: /* error code flag : (W/R=0, P=0): read, not present */
        if (!(vma->vm_flags & (VM_READ | VM_EXEC))) {
            cprintf("do_pgfault failed: error code flag = read AND not present, but the addr's vma cannot read or exec\n");
            goto failed;
        }
    }
    /* IF (write an existed addr ) OR
     *    (write an non_existed addr && addr is writable) OR
     *    (read  an non_existed addr && addr is readable)
     * THEN
     *    continue process
     */
    uint32_t perm = PTE_U;
    if (vma->vm_flags & VM_WRITE) {
        perm |= PTE_W;
    }
    addr = ROUNDDOWN(addr, PGSIZE);

    ret = -E_NO_MEM;

    pte_t *ptep=NULL;
    /*LAB3 EXERCISE 1: YOUR CODE
    * Maybe you want help comment, BELOW comments can help you finish the code
    *
    * Some Useful MACROs and DEFINEs, you can use them in below implementation.
    * MACROs or Functions:
    *   get_pte : get an pte and return the kernel virtual address of this pte for la
    *             if the PT contians this pte didn't exist, alloc a page for PT (notice the 3th parameter '1')
    *   pgdir_alloc_page : call alloc_page & page_insert functions to allocate a page size memory & setup
    *             an addr map pa<--->la with linear address la and the PDT pgdir
    * DEFINES:
    *   VM_WRITE  : If vma->vm_flags & VM_WRITE == 1/0, then the vma is writable/non writable
    *   PTE_W           0x002                   // page table/directory entry flags bit : Writeable
    *   PTE_U           0x004                   // page table/directory entry flags bit : User can access
    * VARIABLES:
    *   mm->pgdir : the PDT of these vma
    *
    */
--------------------------------------------------------------------------------------------
* 设计思路：
    首先检查页表中是否有相应的表项，如果表项为空，那么说明没有映射过；
    然后使用 pgdir_alloc_page 获取一个物理页，同时进行错误检查即可。
  
/*LAB3 EXERCISE 1: YOUR CODE*/
    // try to find a pte, if pte's PT(Page Table) isn't existed, then create a PT.
    // (notice the 3th parameter '1') : 检查 create 是否为 1
    if ((ptep = get_pte(mm->pgdir, addr, 1)) == NULL) {
        cprintf("get_pte in do_pgfault failed\n");
        goto failed;
    }
    //如果页表不存在，尝试分配一空闲页，匹配物理地址与逻辑地址，建立对应关系
    if (*ptep == 0) { // if the phy addr isn't exist, then alloc a page & map the phy addr with logical addr
        if (pgdir_alloc_page(mm->pgdir, addr, perm) == NULL) { //失败内存不够退出
            cprintf("pgdir_alloc_page in do_pgfault failed\n");
            goto failed;
        }
    }
--------------------------------------------------------------------------------------------
    /*LAB3 EXERCISE 2: YOUR CODE
    * Now we think this pte is a  swap entry, we should load data from disk to a page with phy addr,
    * and map the phy addr with logical addr, trigger swap manager to record the access situation of this page.
    *
    *  Some Useful MACROs and DEFINEs, you can use them in below implementation.
    *  MACROs or Functions:
    *    swap_in(mm, addr, &page) : alloc a memory page, then according to the swap entry in PTE for addr,
    *                               find the addr of disk page, read the content of disk page into this memroy page
    *    page_insert ： build the map of phy addr of an Page with the linear addr la
    *    swap_map_swappable ： set the page swappable
    */
--------------------------------------------------------------------------------------------
* 设计思路：
    如果 PTE 存在，那么说明这一页已经映射过了但是被保存在磁盘中，需要将这一页内存交换出来：
      1.调用 swap_in 将内存页从磁盘中载入内存；
      2.调用 page_insert 建立物理地址与线性地址之间的映射；
      3.设置页对应的虚拟地址，方便交换出内存时将正确的内存数据保存在正确的磁盘位置；
      4.调用 swap_map_swappable 将物理页框加入 FIFO。
/*LAB3 EXERCISE 2: YOUR CODE*/
    //页表项非空，尝试换入页面
    else { // if this pte is a swap entry, then load data from disk to a page with phy addr
           // and call page_insert to map the phy addr with logical addr
        if(swap_init_ok) {
            struct Page *page=NULL;//根据 mm 结构和 addr 地址，尝试将硬盘中的内容换入至 page 中
            if ((ret = swap_in(mm, addr, &page)) != 0) {
                cprintf("swap_in in do_pgfault failed\n");
                goto failed;
            }    
            page_insert(mm->pgdir, page, addr, perm);//建立虚拟地址和物理地址之间的对应关系
            swap_map_swappable(mm, addr, page, 1);//将此页面设置为可交换的
            page->pra_vaddr = addr;
        }
        else {
            cprintf("no swap_init_ok but ptep is %x, failed\n",*ptep);
            goto failed;
        }
   }
   ret = 0;
failed:
    return ret;
}
```



> 请描述页目录项（Page Directory Entry）和页表项（Page Table Entry）中组成部分对 ucore 实现页替换算法的潜在用处。

表项中 `PTE_A` 表示内存页是否被访问过，`PTE_D` 表示内存页是否被修改过，借助着两位标志位可以实现 Enhanced Clock 算法。

> 如果 ucore 的缺页服务例程在执行过程中访问内存，出现了页访问异常，请问硬件要做哪些事情？

如果出现了页访问异常，那么硬件将引发页访问异常的地址将被保存在 `cr2` 寄存器中，设置错误代码，然后触发 `Page Fault` 异常。



### 补充完成基于 FIFO 的页面替换算法



```c
/*
 * (3)_fifo_map_swappable: According FIFO PRA, we should link the most recent arrival page at the back of pra_list_head qeueue
 */
// 作用: 将最近被用到的页面添加到算法所维护的次序队列。
static int _fifo_map_swappable(struct mm_struct *mm, uintptr_t addr, struct Page *page, int swap_in)
{
    list_entry_t *head=(list_entry_t*) mm->sm_priv;
    list_entry_t *entry=&(page->pra_page_link);
 
    assert(entry != NULL && head != NULL);
    //record the page access situlation
    /*LAB3 EXERCISE 2: YOUR CODE*/ 
    //(1)link the most recent arrival page at the back of the pra_list_head qeueue.
    list_add(head, entry);//将最近用到的页面添加到次序的队尾
    return 0;
}


/*
 *  (4)_fifo_swap_out_victim: According FIFO PRA, we should unlink the  earliest arrival page in front of pra_list_head qeueue,
 *                            then assign the value of *ptr_page to the addr of this page.
 */
// 作用: 用来查询哪个页面需要被换出。
static int _fifo_swap_out_victim(struct mm_struct *mm, struct Page ** ptr_page, int in_tick)
{
     list_entry_t *head=(list_entry_t*) mm->sm_priv;
         assert(head != NULL);
     assert(in_tick==0);
     /* Select the victim */
     /*LAB3 EXERCISE 2: YOUR CODE*/ 
     //(1)  unlink the  earliest arrival page in front of pra_list_head qeueue
     //(2)  assign the value of *ptr_page to the addr of this page
     /* Select the tail */
     list_entry_t *le = head->prev;//指出需要被换出的页
     assert(head!=le);
     struct Page *p = le2page(le, pra_page_link);//le2page 宏可以根据链表元素，获得对应 page 的指针p
     list_del(le);//将进来最早的页面从队列中删除
     assert(p !=NULL);
     *ptr_page = p;//将这一页的地址存储在ptr_page中
     return 0;
}
```

