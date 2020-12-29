# coding:utf-8
from memory import *
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1][0:2] != "0x":
        print "Usage: virtual_address(in hex, e.g., 0x03df)"
        sys.exit(0)

    virtual_address = int(sys.argv[1][2:], 16)             # 虚拟地址
    print "virtual virtual_address is " + str(hex(virtual_address))

    page_directory_base = 0x11;                         # page_directory_base，页目录表基址
    page_directory_index_mask = 0b111110000000000       # 和虚拟地址向与，即取高5位，得到页表目录中的索引
    page_directory_index = (virtual_address & page_directory_index_mask) >> 10     # 页表目录中的索引
    print str(bin(virtual_address))
    page_directory_entry = mem[page_directory_base][page_directory_index]       # 读出页表目录项
    page_table_base = page_directory_entry & 0b01111111              # 解析出页表基址
    page_table_valid = (page_directory_entry & 0b10000000) >> 7      # 解析标志位
    # 打印页表目录的查询结果
    print "  --> pde index : " + str(hex(page_directory_index)) + \
        "   pde contents : (valid = " + str(page_table_valid)  + \
        " pfn = " + str(hex(page_table_base)) + ")"
    if (page_table_valid == 0):
        print "    --> Fault (page directory entry not valid)"
        sys.exit(0)
    else:
        # 查询页表，流程和对页表目录的查询一致
        page_table_index_mask = 0b1111100000
        page_table_index = (virtual_address & page_table_index_mask) >> 5
        page_table_entry = mem[page_table_base][page_table_index]
        page_frame_number = page_table_entry & 0b01111111
        page_frame_valid = (page_table_entry & 0b10000000) >> 7
        print "    --> pte index : " + str(hex(page_table_index)) + \
            "   pte contents : (valid = " + str(page_frame_valid) + \
            " pfn = " + str(hex(page_frame_number)) + ")"
        if (page_frame_valid == 0):
            print "      --> Fault (page table entry not valid)"
        else:
            offset = virtual_address & 0b11111
            physical_address = (page_frame_number << 5) + offset     # 物理地址为页号加偏移量
            print "      --> Translates to physical address : " + \
                hex(physical_address) + \
                " --> value : " + str(hex(mem[page_frame_number][offset]))        
