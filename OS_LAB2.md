## OS_LAB2

### 1.First Fit

default_init_memmap:`用来初始化空闲页链表，初始化每一个空闲页，然后计算空闲页的总数。

```c
/*
头Page保存property信息
Like this:
Page base->property = 3
Page base+1->property = 0
Page base+2->property = 0
Page base+3->property = 2
Page base+4->property = 0
Page base+s5->property = 1
*/
/*
default_init_memmap:  CALL GRAPH: kern_init --> pmm_init-->page_init-->init_memmap--> pmm_manager->init_memmap
 *              This fun is used to init a free block (with parameter: addr_base, page_number).
 *              First you should init each page (in memlayout.h) in this free block, include:
 *                  p->flags should be set bit PG_property (means this page is valid. In pmm_init fun (in pmm.c),
 *                  the bit PG_reserved is setted in p->flags)
 *                  if this page  is free and is not the first page of free block, p->property should be set to 0.
 *                  if this page  is free and is the first page of free block, p->property should be set to total num of block.
 *                  p->ref should be 0, because now p is free and no reference.
 *                  We can use p->page_link to link this page to free_list, (such as: list_add_before(&free_list, &(p->page_link)); )
 *              Finally, we should sum the number of free mem block: nr_free+=n
**/
// 初始化n个空闲页块
static void default_init_memmap(struct Page *base, size_t n) {
    assert(n > 0);
    struct Page *p = base;
    for (; p != base + n; p ++) {
        assert(PageReserved(p));//确认本页是否为保留页
        //设置标志位
        p->flags = p->property = 0;
        set_page_ref(p, 0);//清空引用
        
    }
    base->property = n; //连续内存空闲块的大小为n，属于物理页管理链表，头一个空闲页块 要设置数量
    SetPageProperty(base);
    nr_free += n;  //说明连续有n个空闲块，属于空闲链表
    list_add_before(&free_list, &(p->page_link));//插入空闲页的链表里面，初始化完每个空闲页后，将其要插入到链表每次都插入到节点前面，因为是按地址排序
}
```



`default_alloc_pages`: 从空闲页块的链表中去遍历，找到第一块大小大于 `n` 的块，然后分配出来，把它从空闲页链表中除去，然后如果有多余的，把分完剩下的部分再次加入会空闲页链表中即可。

```c
static struct Page * default_alloc_pages(size_t n) {
    assert(n > 0);
    if (n > nr_free) { //如果所有的空闲页的加起来的大小都不够，那直接返回NULL
        return NULL;
    }
    struct Page *page = NULL;
    list_entry_t *le = &free_list;//从空闲块链表的头指针开始
    // 查找 n 个或以上 空闲页块 若找到 则判断是否大过 n 则将其拆分 并将拆分后的剩下的空闲页块加回到链表中
    while ((le = list_next(le)) != &free_list) {//依次往下寻找直到回到头指针处,即已经遍历一次
        // 此处 le2page 就是将 le 的地址 - page_link 在 Page 的偏移 从而找到 Page 的地址
        struct Page *p = le2page(le, page_link);//将地址转换成页的结构
        if (p->property >= n) {//由于是first-fit，则遇到的第一个大于N的块就选中即可
            page = p;	//记录为page
            break;
        }
    }
		//找到可放入的页
    if (page != NULL) {
        if (page->property > n) {
            struct Page *p = page + n;				// 按照指针偏移，找到按序后面第n个Page结构p
            p->property = page->property - n;	//如果选中的第一个连续的块大于n，只取其中的大小为n的块
            SetPageProperty(p);
            // 将多出来的插入到 被分配掉的页块 后面
            list_add(&(page->page_link), &(p->page_link));
        }
        // 最后在空闲页链表中删除掉原来的空闲页
        list_del(&(page->page_link));
        nr_free -= n;//当前空闲页的数目减n
        ClearPageProperty(page);
    }
    return page;		//return 放入页 or NULL
}
```

`default_free_pages`，将需要释放的空间标记为空之后，需要找到空闲表中合适的位置。由于空闲表中的记录都是按照物理页地址排序的，所以如果插入位置的前驱或者后继刚好和释放后的空间邻接，那么需要将新的空间与前后邻接的空间合并形成更大的空间。

```c
/**
 * 释放掉自base起始的连续n个物理页,n必须为正整数
 * */
static void
default_free_pages(struct Page *base, size_t n) {
    assert(n > 0);
    struct Page *p = base;

    // 遍历这N个连续的Page页，将其相关属性设置为空闲
    for (; p != base + n; p ++) {
        assert(!PageReserved(p) && !PageProperty(p));
        p->flags = 0;
        set_page_ref(p, 0);
    }

    // 由于被释放了N个空闲物理页，base头Page的property设置为n
    base->property = n;
    SetPageProperty(base);

    // 下面进行空闲链表相关操作
    list_entry_t *le = list_next(&free_list);
    // 迭代空闲链表中的每一个节点
    while (le != &free_list) {
        // 获得节点对应的Page结构
        p = le2page(le, page_link);
        le = list_next(le);
        // TODO: optimize
        if (base + base->property == p) {
          	// base在前p在后，两者相连
            // 如果当前base释放了N个物理页后，尾部正好能和Page p连上，则进行两个空闲块的合并
            base->property += p->property;
            ClearPageProperty(p);
            list_del(&(p->page_link));
        }
        else if (p + p->property == base) {
          	// p在前base在后，两者相连
            // 如果当前Page p能和base头连上，则进行两个空闲块的合并
            p->property += base->property;
            ClearPageProperty(base);
            base = p;		//更新一下base
            list_del(&(p->page_link));
        }
    }
    // 空闲链表整体空闲页数量自增n
    nr_free += n;
    le = list_next(&free_list);

    // 再次迭代空闲链表中的每一个节点
    while (le != &free_list) {
        // 转为Page结构
        p = le2page(le, page_link);
        if (base + base->property <= p) {
          	// 找到base节点在list中的插入位置
            assert(base + base->property != p);
            break;
        }
        le = list_next(le);
    }
    // 将base加入到空闲链表之中
    list_add_before(le, &(base->page_link));
}
```



### 2.实现寻找虚拟地址对应的页表项

需要实现的是 `get_pte` 函数，函数找到一个虚地址对应的二级页表项的内核虚地址，如果此二级页表项不存在，则分配一个包含此项的二级页表。

```c
/*
提供一个虚拟地址，然后根据这个虚拟地址的高 10 位，找到页目录表中的 PDE 项。前20位是页表项 (二级页表) 的线性地址，后 12 位为属性，然后判断一下 PDE 是否存在(就是判断 P 位)。不存在，则获取一个物理页，然后将这个物理页的线性地址写入到 PDE 中，最后返回 PTE 项。简而言之就是根据所给的虚拟地址，构造一个 PTE 项。
*/
// 目录表中目录项的起始地址 pdep
// 目录表中目录项的值 *pdep
// 页表的起始物理地址 (*pdep & ~0xFFF) 即 PDE_ADDR(*pdep)
// 页表的起始内核虚拟地址 KADDR((*pdep & ~0xFFF))
// la在页表项的偏移量为 PTX(la)
// 页表项的起始物理地址为 (pte_t *)KADDR((*pdep & ~0xFFF)) + PTX(la)

pte_t *get_pte(pde_t *pgdir, uintptr_t la, bool create) {
  	// PDX(la) 根据la的高10位获得对应的页目录项(一级页表中的某一项)索引(页目录项)
  	// &pgdir[PDX(la)] 根据一级页表项索引从一级页表中找到对应的页目录项指针
    pde_t *pdep = &pgdir[PDX(la)]; 	// 找到 PDE 地址
    if (!(*pdep & PTE_P)) {         // 看看 PDE 指向的页表是否存在
        struct Page* page = alloc_page(); // 不存在就申请一页物理页
        /* 通过 default_alloc_pages() 分配的页 的地址 并不是真正的页分配的地址实际上只是 Page 这个结构体所在的地址而已 故而需要 通过使用 page2pa() 将 Page 这个结构体的地址 转换成真正的物理页地址的线性地址 然后需要注意的是 无论是 * 或是 memset 都是对虚拟地址进行操作的，所以需要将真正的物理页地址再转换成内核虚拟地址*/
        if (!create || page == NULL) { //不存在或alloc失败，返回NULL
            return NULL;
        }
        set_page_ref(page, 1); //设置此页被引用一次
        uintptr_t pa = page2pa(page); //得到 page 管理的那一页的物理地址
      	// KADDR将物理地址转换为内核虚拟地址
        memset(KADDR(pa), 0, PGSIZE); // 将这一页清空 此时将线性地址转换为内核虚拟地址
      	// la对应的一级页目录项进行赋值，使其指向新创建的二级页表(页表中的数据被MMU直接处理，为了映射效率存放的都是物理地址)
        *pdep = pa | PTE_U | PTE_W | PTE_P; // 设置 PDE 权限
    }
  	// 要想通过C语言中的数组来访问对应数据，需要的是数组基址(虚拟地址),而*pdep中页目录表项中存放了对应二级页表的一个物理地址
    // PDE_ADDR将*pdep的低12位抹零对齐(指向二级页表的起始基地址)，再通过KADDR转为内核虚拟地址，进行数组访问
    // PTX(la)获得la线性地址的中间10位部分，即二级页表中对应页表项的索引下标。这样便能得到la对应的二级页表项了
  	// 1.PDE_ADDR获取页目录表项地址
  	// 2.(pte_t *)KADDR(PDE_ADDR(*pdep))获取pte指针
		// 3.PTX获取线性地址中间10位，得到二级页表项索引
  	// 4.&((pte_t *)KADDR(PDE_ADDR(*pdep)))[PTX(la)] 返回二级页表虚拟地址
    return &((pte_t *)KADDR(PDE_ADDR(*pdep)))[PTX(la)];
}
```



### 释放某虚地址所在的页并取消对应二级页表项的映射

思路主要就是先判断该页被引用的次数，如果只被引用了一次，那么直接释放掉这页， 否则就删掉二级页表的该表项，即该页的入口。取消页表映射过程如下：

- 将物理页的引用数目减一，如果变为零，那么释放页面；
- 将页目录项清零；
- 刷新TLB。

```c
static inline void page_remove_pte(pde_t *pgdir, uintptr_t la, pte_t *ptep) {
    if ((*ptep & PTE_P)) { //判断页表中该表项是否存在
        struct Page *page = pte2page(*ptep);// 将页表项转换为页数据结构
        if (page_ref_dec(page) == 0) { // 判断是否只被引用了一次，若引用计数减一后为0，则释放该物理页
            free_page(page);
        }
        *ptep = 0; // //如果被多次引用，则不能释放此页，只用释放二级页表的表项，清空 PTE
        tlb_invalidate(pgdir, la); // 刷新 tlb
    }
}
```

