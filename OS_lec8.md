## OS_lec8

## SPOC

```
page 6c: e1 b5 a1 c1 b3 e4 a6 bd 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 

page = 32B = 2^5 -> offset = 5b
8KB 虚拟空间 = 2^13 -> length = 13
共计8个页表 -> 页目录中项数 = 8
一级页表 3b
二级页表 5b
offset  5b

4KB 物理空间 = 2^12
物理Frame 2^7

PDBR = 0xd80 = 110110000000
page directory = 0xd80 >> 5 = 110 1100 = page 6c


1) Virtual Address 1e6f:
0x1e6f = 000111 10011 01111
pde index = 00111 = 7
pde content = (0xbd, 10111101, valid = 1, pfn = 0x3d)
page 3d: f6 7f 5d 4d 7f 04 29 7f 1e 7f ef 51 0c 1c 7f 7f 7f 76 d1 16 7f 17 ab 55 9a 65 ba 7f 7f 0b 7f 7f 
pte index = 10011 = 19
pte content = (0x16, 00010110, valid = 0)
disk 16: 00 0a 15 1a 03 00 09 13 1c 0a 18 03 13 07 17 1c 0d 15 0a 1a 0c 12 1e 11 0e 02 1d 10 15 14 07 13 
index = 01111 = 15
disk addr = 0010 1100 1111 = 0x2cf
val = 0x1c


2) Virtual Address 6653
0x6653 = 011001 10010 10011
pde index = 11001 = 25
pde content = (0x7f, 01111111, valid = 0) -> 触发页缺失


3) Virtual Address 1c13
0x1c13 = 000111 00000 10011
pde index = 00111 = 7
pde content = (0xbd, 10111101, valid = 1, pfn = 0x3d)
page 3d: f6 7f 5d 4d 7f 04 29 7f 1e 7f ef 51 0c 1c 7f 7f 7f 76 d1 16 7f 17 ab 55 9a 65 ba 7f 7f 0b 7f 7f 
pte index = 0
pte content = (0xf6, 11110110, valid = 1, pfn = 0x76)
page 76: 1a 1b 1c 10 0c 15 08 19 1a 1b 12 1d 11 0d 14 1e 1c 18 02 12 0f 13 1a 07 16 03 06 18 0a 19 03 04 
physical addr = 0111 0110 10011 = 0xed3
val = 0x12


4) Virtual Address 6890
0x6890 = 011010 00100 10000
pde index = 011010 = 26
pde content = (0x7f, 01111111, valid = 0) -> 触发页缺失

5) Virtual Address 0af6
0x0af6 = 000010 10111 10110
pde index = 000010 = 2
pde content = (0xa1, 10100001, valid = 1, pfn = 0x21)
page 21: 7f 7f 36 8e 7f 33 d5 82 7f 7f 79 2b 7f 7f 7f 7f 7f f1 7f 7f 71 7f 7f 7f 63 7f 2f dd 67 7f f9 32 
pte index = 10111 = 23
pte content = (0x7f, 01111111, valid = 0) -> 情况b：既没有在内存中，页没有在硬盘上，这时页帧号为0x7F
```

