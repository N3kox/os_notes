```c
.text
.globl switch_to
switch_to:                      # switch_to(from, to)
  	# esp指向下一个压栈的顶（逻辑上为空）
		# 前半段保存，后半段恢复
    # switch_to请求来源进程（from proc）的context的完整保存
  	# esp向上四个字节存的是from process的context地址
    movl 4(%esp), %eax          # eax保存from process的context地址
    popl 0(%eax)                # save eip !popl
  	# popl 完成将from proc的eip（pc）保存到swap_context里
    
  
  	movl %esp, 4(%eax)					# 保存esp内容到from process的context中，下面同理
    movl %ebx, 8(%eax)
    movl %ecx, 12(%eax)
    movl %edx, 16(%eax)
    movl %esi, 20(%eax)
    movl %edi, 24(%eax)
    movl %ebp, 28(%eax)

    # restore to's registers
  	# 恢复进入运行状态的进行的寄存器中的值
    movl 4(%esp), %eax          # not 8(%esp): popped return address already
                                # eax now points to to
  	# 取出目的进程(to proc)的context的指针
  	# 将内存里的信息逐一导入寄存器
    movl 28(%eax), %ebp
    movl 24(%eax), %edi
    movl 20(%eax), %esi
    movl 16(%eax), %edx
    movl 12(%eax), %ecx
    movl 8(%eax), %ebx
    movl 4(%eax), %esp
		
  	# push内容为eax存储的eip（pc）
    pushl 0(%eax)               # push eip
  	
		# 使用ret，从栈中取出地址从而完成切换
  	# eip = fork ret的地址
    ret


```

