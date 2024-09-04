import os
import sys
import xlrd
from collections import Counter

def main():
    #------------------------- field_check -------------------------#
    def field_check(field_nums,reg_list):
        field_bit_list        = []
        field_name_lsit       = []
        reg_current_name      = reg_list[2]
        reg_reset_value_int   = int(reg_list[3],16)
        field_reset_vlaue_sum = 0
        #---------------- get field_bit list and field_name_list ----------------# 
        for i in range(field_nums):
            if(':' in reg_list[(1+i)*4].strip('[]')):
                field_bit_list.append(reg_list[(1+i)*4].strip('[]').split(':')[0])
                field_bit_list.append(reg_list[(1+i)*4].strip('[]').split(':')[1])
            else:
                field_bit_list.append(reg_list[(1+i)*4].strip('[]')) 
            field_name_lsit.append(reg_list[5+4*i])

        #---------------- check field range and overlap ----------------# 
        for i in range(len(field_bit_list) - 1):
            if(int(field_bit_list[i]) < 0 or int(field_bit_list[i] > 31)):
                print("\033[31m -------[Error] ----> %s <---- REG field bit set error , must set in [0:31] \033[0m"%(reg_current_name))
                sys.exit(1)
            if(int(field_bit_list[i] <= int(field_bit_list[i+1]))):
                print("\033[31m -------[Error] ----> %s <---- REG field bit is overlap , please check that \033[0m"%(reg_current_name))
                sys.exit(1)
        
        #---------------- check reg_reset_value == field_reset_value_sum ----------------# 
        for i in range(field_nums):
            field_reset_value_temp = 0
            field_reset_value_temp = int(reg_list[6+4*i].split("h")[1],16)
            if(':' in reg_list[(1+i)*4].strip('[]')):
                field_reset_value_temp = field_reset_value_temp << int(reg_list[(1+i)*4].strip('[]').split(':')[1])
            else:
                field_reset_value_temp = field_reset_value_temp << int(reg_list[(1+i)*4].strip('[]'))
            
            field_reset_vlaue_sum = field_reset_vlaue_sum + field_reset_value_temp
        
        if(field_reset_vlaue_sum != reg_reset_value_int):
            print("\033[31m -------[Error] ----> %s <---- REG reset_value(%s) != field_reset_value_sum(%s) \033[0m"%(reg_current_name,reg_list[3],hex(field_reset_vlaue_sum)))
            sys.exit(1)

        #---------------- check field name whether exist same ----------------#
        field_name_appear_cnt = Counter(field_name_lsit)#Counter form python collections
        field_name_same_list  =[string for string, count in field_name_appear_cnt.items() if count > 1]
        if("Reserve" in field_name_same_list):
            field_name_same_list.remove("Reserve")
        if("reserve" in field_name_same_list):
            field_name_same_list.remove("reserve")
        
        if field_name_same_list:
            print("\033[31m -------[Error] ----> %s <---- REG have same field_name : %s \033[0m"%(reg_current_name,field_name_same_list[0]))
            sys.exit(1)
        
        #---------------- check field width----------------#
        for i in range(field_nums):
            field_bit = reg_list[4+4*i].strip('[]')
            field_rst_value_width = reg_list[4+4*i].split('\'h')[0]
            field_rst_value_width = int(field_rst_value_width)

            field_width = None
            if(':' in field_bit):
                field_high_bit = field_bit.split(':')[0]
                field_low_bit  = field_bit.split(':')[1]
                field_high_bit = int(field_high_bit)
                field_low_bit  = int(field_low_bit)
                field_width    = field_high_bit - field_low_bit + 1
            else:
                field_width    = 1
            if(field_width != field_rst_value_width):
                print("\033[31m -------[Error] ----> %s <---- REG  %s field set error, the field_bit_width is %d, the rst_value_width is %d  \033[0m"%(reg_current_name,reg_list[5+4*i],field_width,field_rst_value_width))
            sys.exit(1)

    #------------------------- reg name check -------------------------#
    def reg_name_check(reg_nums,reg_list):
        reg_name_list = []
        for i in range(reg_nums):
            reg_name_list.append(reg_list[i][2])
        
        reg_name_appear_cnt = Counter(reg_name_list)
        reg_name_same_list  = [string for string, count in reg_name_appear_cnt.items() if count > 1]

        if reg_name_same_list:
            print("\033[31m -------[Error] ----> %s <---- REG exist same name register  \033[0m"%(reg_name_same_list[0]))
            sys.exit(1)

    #------------------------- get reg excel file -------------------------#
    #get reg file , if no appoint excel file , exit procedure
    if len(sys.argv) > 1 :
        if(os.path.exists(sys.argv[1]) == False):
            print("\033[31m -------[Error] : serch excel file fail  \033[0m")
            sys.exit(1)
        excel_file = xlrd.open_workbook(sys.argv[1])
    else :
        print("\033[31m -------[Error] : NO appoint excel file   \033[0m")
        sys.exit(1)
        
    #get sheet numbers
    sheet_num = excel_file.nsheets
    for i in range(1,sheet_num):
        #get reg sheet , sheet2 ~ last sheet
        reg_sheet       = excel_file.sheet_by_index(i)
        #get module name,base_addr,reg_num
        module_name     = reg_sheet.cell_value(0,1)
        base_addr       = reg_sheet.cell_value(0,3)
        reg_num_str     = reg_sheet.cell_value(0,5)
        reg_num         = int(reg_num_str)

        #initial reg_lsit_all , contain all reg information
        reg_list_all = []
        #initial reg_lsit , only contain current one reg information
        reg_list     = []
        #initial field_nums , indicates that current reg contain field nums
        field_nums   = 1
        #initial current manage excel file row
        current_row     = 3
        #initial current manage excel file column
        current_column  = 0
        #initial reg_name
        reg_name = reg_sheet.cell_value(0,0)

        #last sign check
        last_row_index = reg_sheet.nrows - 1
        if(reg_sheet.cell_value(last_row_index,0) != 'end_reg'):
            print("\033[31m -------[Error] : last sign \"end_reg\" error or no exist \033[0m")
        sys.exit(1)

    #loop get reg information , write it or ralf file
    for i in range(reg_num):
        reg_list         = []
        field_nums       = 1
        #get current reg offset addr .etc , write to reg_list , column ++
        reg_offset_addr  = reg_sheet.cell_value(3,0)
        current_column   = current_column + 1
        reg_list.append(reg_offset_addr)

        reg_name         = reg_sheet.cell_value(current_row,current_column)
        current_column   = current_column + 1
        reg_list.append(reg_name)

        reg_reset_value  = reg_sheet.cell_value(current_row,current_column)
        current_column   = current_column + 1
        reg_list.append(reg_reset_value)

        field_bit        = reg_sheet.cell_value(current_row,current_column)
        current_column   = current_column + 1
        reg_list.append(field_bit)     

        field_name       = reg_sheet.cell_value(current_row,current_column)
        current_column   = current_column + 1
        reg_list.append(field_name)

        field_rst_value  = reg_sheet.cell_value(current_row,current_column)
        current_column   = current_column + 1
        reg_list.append(field_rst_value)

        field_access     = reg_sheet.cell_value(current_row,current_column)
        reg_list.append(field_access)

        current_column   = 0
        current_row      = current_row + 1
        #if this reg have more field , execute under code
        while(reg_sheet.cell_value(current_row,3) != ''):
            current_column = 3
            field_bit        = reg_sheet.cell_value(current_row,current_column)
            current_column   = current_column + 1
            reg_list.append(field_bit)     

            field_name       = reg_sheet.cell_value(current_row,current_column)
            current_column   = current_column + 1
            reg_list.append(field_name)
    
            field_rst_value  = reg_sheet.cell_value(current_row,current_column)
            current_column   = current_column + 1
            reg_list.append(field_rst_value)
    
            field_access     = reg_sheet.cell_value(current_row,current_column)
            reg_list.append(field_access)

            current_column   = 0
            current_row      = current_row + 1
            field_nums       = field_nums + 1

        #check the reg_num is correct
        if(i != reg_num - 1 and reg_sheet.cell_value(current_row,0) == 'end_reg'):
            print("\033[31m -------[Error] : the input reg_nums(%d) is != actual reg_nums(%d) \033[0m"%(reg_num, i + 1))
            sys.exit(1)
        current_row = current_row + 1
        #insert field_nums to reg_list[0], as loop variable
        reg_list.insert(0,field_nums)
        #-debug, print reg list
        if("-debug" in sys.argv):
            print(reg_list)           
        #check field format
        field_check(field_nums,reg_list)
        #add current reg_list to reg_list_all
        reg_list_all.append(reg_list)

    #reg name same check
    reg_name_check(reg_num,reg_list)

    #------------------------------------------------------------------- 
    #open ralf file
    ralf_file = open("%s_reg.ralf"%(module_name),"w")
    ralf_file.write("block %s_reg {\n"%(module_name))
    ralf_file.write("  bytes 4 ;\n")
    #write reg information
    for i in range(reg_num):   
        ralf_file.write("  register %s @%s {\n"%(reg_list_all[i][2],reg_list_all[i][1]))
        ralf_file.write("    bytes 4;\n")
        for j in range(reg_list_all[i][0]):#this range is field nums
            if(reg_list_all[i][5+4*j] != 'Reserve' and reg_list_all[i][5+4*j] != 'reserve'):#only unreserve field write to ralf file, this is ralf format
                current_field_bit           = reg_list_all[i][4+4*j].strip('[]')
                current_field_width         = reg_list_all[i][6+4*j].split('\'h')[0]
                current_field_width         = int(current_field_width)
                current_field_rst_value_str = reg_list_all[i][6+4*j].split('\'h')[1]
                current_field_rst_value_int = int(current_field_rst_value_str,16)
                current_field_access        = reg_list_all[i][7+4*j].lower() 

                if(':' in current_field_bit):
                    field_bit_list  = current_field_bit.split(':')
                    field_high_bit  = field_bit_list[0]
                    field_low_bit   = field_bit_list[1]
                    if(field_low_bit != 0):
                        ralf_file.write("    field %s @%s {\n"%(reg_list_all[i][5+4*j],field_low_bit))
                    else:
                        ralf_file.write("    field %s @0 {\n"%(reg_list_all[i][5+4*j]))
                else:
                    if(int(current_field_bit) != 0):
                        ralf_file.write("    field %s @%s {\n"%(reg_list_all[i][5+4*j],current_field_bit))
                    else:
                        ralf_file.write("    field %s @0 {\n"%(reg_list_all[i][5+4*j]))
                
                if(':' in current_field_bit):
                    ralf_file.write("      bits %s;\n"%(current_field_width))
                else:
                    ralf_file.write("      bit 1;\n")
                
                if(current_field_rst_value_int !=0):
                    ralf_file.write("      reset 'h%s;\n"%(current_field_rst_value_str))
                
                ralf_file.write("      access %s;\n"(current_field_access))
                ralf_file.write("    }\n")
        ralf_file.write("  }\n")
    ralf_file.write("}\n")
    ralf_file.close()

    vcs_ral_result = os.system('ralgen -t %s_reg -full64 -uvm %s_reg.ralf -o %s_regmodel'%(module_name,module_name,module_name))
    if(vcs_ral_result ==0):
        print(("\033[32m -------- [Successful]  the %s_regmodel.sv  %s_reg.ralf is created  --------\033[0m"%(module_name,module_name)))
    else:
        print("\033[31m -------- [Error]  the use vcs ralgen command fail , this error is unexpect, please contact the administrator  --------\033[0m")
        
if __name__=="__main__":
    main()
