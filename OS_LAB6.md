os_lab6:

1. Stride Scheduling:

   1. 步长Stride：当前执行的程度；Pass：当前可执行的长度
   2. 算法策略选择步长Stride最小的进程，执行时间为Stride+pass，谁的pass值最小，被调用次数最多
   3. Stride基于优先级调度（pass与优先级成反比，优先级越高意味着pass越小，进程运行时间更短，运行机会更多）。实验中 pass = BIG_VALUE/priority 且 priority > 1，调度的选择固定
   4. 为每一个runnable进程设置一个当前状态 stride，表示该进程当前的调度权。另外定义其对应的 pass 值，表示对应进程在调度后，stride 需要进行的累加值。
   5. 每次需要调度时，从当前 runnable 态的进程中选择 **stride最小**的进程调度。对于获得调度的进程 P，将对应的 stride 加上其对应的步长 pass（只与进程的优先权有关系）。
   6. 执行约束的时间后，回到步骤 2，重新调度当前 stride 最小的进程。

   ```c
   //proc_stride_comp_f：优先队列的比较函数，主要思路就是通过步数相减，然后根据其正负比较大小关系
   static int proc_stride_comp_f(void *a, void *b)
   {
        struct proc_struct *p = le2proc(a, lab6_run_pool);//通过进程控制块指针取得进程 a
        struct proc_struct *q = le2proc(b, lab6_run_pool);//通过进程控制块指针取得进程 b
        int32_t c = p->lab6_stride - q->lab6_stride;//步数相减，通过正负比较大小关系
     	 //步数无符号整数存储，有符号计算比较
        if (c > 0) return 1;
        else if (c == 0) return 0;
        else return -1;
   }
   ```

2. 避免Stride溢出：**STRIDE_MAX - STRIDE_MIN <= PASS_MAX**；**stride，pass是无符号整数；用有符号数进行比较。**如16位无符号整数上限65535，A在执行前后如图1，2所示

   ![image](https://chyyuu.gitbooks.io/ucore_os_docs/content/lab6_figs/image001.png)

   ![image](https://chyyuu.gitbooks.io/ucore_os_docs/content/lab6_figs/image002.png)

   65534 + 2 = 0，65534+100 = 98，，保证两个stride的差在机器整数表示范围内，98 - 65535以有符号的16位整数表示结果为99，99 > 0，因此在这种意义下98 > 65535，故也能够得到最小的Stride（即当前应调度进程B）。

3. 如何**证明STRIDE_MAX – STRIDE_MIN <= PASS_MAX**？

   假如该命题不成立，则就绪队列中在上一次找出可执行进程时选择进程P，此时存在另一个进程P'，且P'的stride值严格小于P的stride，说明上一次调度出现了问题，反证说明上述命题成立。

4. 在 ucore 中，目前 Stride 是采用无符号的32位整数表示。则 BigStride 应该取多少，才能保证比较的正确性？BIG_STRIDE 的值是怎么来的?

   保证BigStride = 0x7fffffff（即$(2^{32}-1)/2$)，在 ucore 中，BIG_STRIDE 的值是采用无符号 32 位整数表示，而 stride 也是无符号 32 位整数。也就是说，最大值只能为$2^{32}-1$。如果stride已经为BIGSTRIDE，再加上pass一定溢出，此时需要约定一个最大的pass，使得两个stride即使有一个溢出也可以比较。

   1. $pass = BIGSTRIDE / priority <= BIGSTRIDE$
   2. $passmax <= BIGSTRIDE$
   3. $maxstride - minstride <= BIGSTRIDE$
   4. $BIGSTRIDE = (2^{32} - 1)/2 = 0x7fffffff$

5. 优先级队列-斜堆

