## OS_EXAM_2014_FINAL

## 银行家算法

死锁是操作系统中资源共享时面临的一个难题。请回答下列与死锁相关的问题。

### （1）

设系统中有下述解决死锁的方法：

1. 银行家算法；
2. 检测死锁，终止处于死锁状态的进程，释放该进程占有的资源；
3. 资源预分配。
   简述哪种办法允许最大的并发性，即哪种办法允许更多的进程无等待地向前推进？请按“并发性”从大到小对上述三种办法进行排序。

2  > 1 > 3

银行家算法每满足一个资源请求时都会进行安全状态检查。因为安全状态中实际上包含了一部分不会发生死锁的状态，所以它会拒绝一些本来可以接受的请求，所以降低了一点并发性。

检测死锁所有进程都可以无等待地推进，直到真的出现了死锁再进行处理。

资源预分配的并发性比银行家算法更低，因为银行家算法至少保留了一些动态性能，而资源预分配完全牺牲了动态性。



## 七 SFS文件系统（12分）

uCore实现了一个简单的文件系统Simple FS，假设该文件系统现已经装载到一个硬盘中（disk0），该硬盘的大小为20M，目前有三个文件A.txt，B.txt和C.txt存放在该硬盘中，三个文件的大小分别是48K，1M和4M。

### （1）

简要描述SFS文件系统中文件数据的组织结构（即：SFS文件的数据的存放位置组织方式）。

一个Superblock维护基本信息；多个freemap；索引节点inode；目录和文件均由一个inode和具体的数据块组成，其中inode包含文件的基本属性、12个直接索引和一级索引/二级索引表的块地址；目录的数据块存放文件名和inode地址；文件的数据块存放文件内具体内容。

### （2）

请根据Simple FS的设计实现情况，画出该文件系统当前在disk0上的布局情况，需要给出相应结构的名称和起始块号。

0 superblock
1 根目录inode
2 freemap（640K，只需要1块）
3 根目录的数据块（包含A.txt、B.txt、C.txt的inode的地址） （1分）
4 A.txt的inode（包含12个直接索引块的地址）
5-16 A.txt的数据块 （2分）
17 B.txt的inode（包含12个直接索引块和1个一级间接索引）
18-29 B.txt的直接索引数据
30 B.txt的一级间接索引（包含244个数据块地址）
31-274 B.txt的一级间接索引块 （1分）
275 C.txt的inode（包含12个直接索引块和1个一级间接索引）
276-287 C.txt的一级间接索引块
288 C.txt的一级间接索引（包含1012个数据块地址）
289-1300 C.txt的一级间接索引块
