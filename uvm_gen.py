import os
import sys
   
global_tb_directory = ''
module_name = ''
reg_model   = ''

def cd_tb_directory():
    os.chdir(global_tb_directory)

def create_dir(dir):
    if os.path.exists(dir):
        os.system("rm -rf %s" % dir)
    os.mkdir(dir)

def get_cmd():
    # If there are more than 2 command-line arguments, then get the list of arguments
    if len(sys.argv) > 2 :
        cmd_line_args = sys.argv[1:]
        # Iterate through the list of arguments and get the module name and register model
        if not any('module=' in s for s in cmd_line_args):
            print("\033[31m  [Error] : uvm_gen.py 22 line \033[0m")
            print("\033[31m -------[Error] : 'module=' not set \033[0m")
            sys.exit(1) 

        if not any('reg_model=' in s for s in cmd_line_args):
            print("\033[31m  [Error] : uvm_gen.py 27 line \033[0m")
            print("\033[31m -------[Error] : 'reg_model=' not set \033[0m")
            sys.exit(1) 

        for arg in cmd_line_args:
            if arg.startswith("module="):
                if arg == "module=":
                    print("\033[31m  [Error] : uvm_gen.py 34 line \033[0m")
                    print("\033[31m -------[Error] : module format error ,please check format   \033[0m")
                    sys.exit(1)                         
                global module_name
                module_name = arg.split("=")[1]  
            elif arg.startswith("reg_model="):
                global reg_model
                reg_model = arg.split("=")[1]              
                #Check if the reg_model is set to either ahb or apb
                if(reg_model != 'ahb' and reg_model != 'apb'):
                    #Print an error message if the reg_model is not set to ahb or apb
                    print("\033[31m  [Error] : uvm_gen.py 51 line \033[0m")
                    print("\033[31m  [Error] : reg_model not set or set != ahb/apb , reg_model = %s\033[0m"%(reg_model))
                    #Exit the program
                    sys.exit(1)
            else:
                print("\033[31m  [Error] : uvm_gen.py 56 line \033[0m")
                print("\033[31m -------[Error] : command-line arguments input error,please use correct format \033[0m")
                sys.exit(1)                  
        # If the module name or register model is not set, then raise an error and exit
        if module_name is None or reg_model is None:
            print("\033[31m  [Error] : uvm_gen.py 61 line \033[0m")
            print("\033[31m -------[Error] : module or reg_model not set   \033[0m")
            sys.exit(1)
    else:
        # If there are not enough command-line arguments, then raise an error and exit
        print("\033[31m  [Error] : uvm_gen.py 66 line \033[0m")
        print("\033[31m -------[Error] : there are not enough command-line arguments \033[0m")
        sys.exit(1)

#Define a function to create a top file for the given module name and register model
def create_top_file(module_name,reg_model):
    #Open the top.sv file in write mode
    top_file = open('%s_top.sv'%(module_name), "w")
    #Write a comment to the top file
    top_file.write('`ifndef %s_TOP__SV\n'%(module_name.upper()))
    top_file.write('`define %s_TOP__SV\n'%(module_name.upper()))   
    top_file.write('`include "uvm_macros.svh"\n')
    top_file.write('`include "%s_regmodel.sv"\n'%(module_name))
    top_file.write('import uvm_pkg::*;')
    top_file.write('\n')     
    top_file.write('module top;\n')
    top_file.write('\n')    
    #Write the clock and reset signals to the top file
    if reg_model == 'ahb':
        top_file.write('    logic hclk;\n')
        top_file.write('    logic hrstn;\n')
    elif reg_model == 'apb':
        top_file.write('    logic pclk;\n')
        top_file.write('    logic prstn;\n')

    top_file.write('    logic [15:0] rst_period;\n')
    top_file.write('\n')
    top_file.write('    %s_if  %s_if();\n'%(module_name,module_name))
    if reg_model == 'ahb':
        top_file.write('    %s_if  %s_if(hclk,hrstn);\n'%(reg_model,reg_model))
    elif reg_model == 'apb':
        top_file.write('    %s_if  %s_if(pclk,prstn);\n'%(reg_model,reg_model))
    top_file.write('    ral_block_%s_reg reg_model;\n'%(module_name))
    top_file.write('\n') 
    top_file.write('\n') 
    top_file.write('\n') 
    top_file.write('\n') 
    top_file.write('\n')   
    #Write the initialization code for the clock and reset signals
    top_file.write('    initial begin\n')
    top_file.write('        reg_model = new("reg_model");\n')
    top_file.write('        uvm_config_db#(ral_block_%s_reg)::set(null, "*","reg_model",reg_model);\n'%(module_name))
    top_file.write('        uvm_config_db#(virtual %s_if)::set(null, "*","%s_if",%s_if);\n'%(module_name,module_name,module_name))
    top_file.write('        uvm_config_db#(virtual %s_if)::set(null, "*","%s_if",%s_if);\n'%(reg_model,reg_model,reg_model))
    top_file.write('    end\n')
    top_file.write('\n')   
    top_file.write('    //============ Generate Clock ============\n')
    top_file.write('    initial begin\n')
    if reg_model == 'ahb':
        top_file.write('        hclk = 0;\n')
    elif reg_model == 'apb':
        top_file.write('        pclk = 0;\n')    
    top_file.write('        %s_if.clk = 0;\n'%(module_name))
    top_file.write('        while(1)\n')
    top_file.write('        begin\n')
    top_file.write('            #100;\n')
    if reg_model == 'ahb':
        top_file.write('            hclk = ~hclk;\n')    
    elif reg_model == 'apb':    
        top_file.write('            pclk = ~pclk;\n')
    top_file.write('            %s_if.clk = ~%s_if.clk;\n'%(module_name,module_name))
    top_file.write('        end\n')
    top_file.write('    end\n')    
    top_file.write('\n')
    top_file.write('    //============ Generate Reset ============\n')
    top_file.write('    initial begin\n')
    if reg_model == 'ahb':
        top_file.write('        hrstn = 0;\n')    
    elif reg_model == 'apb':    
        top_file.write('        prstn = 0;\n')
    top_file.write('        %s_if.rstn = 0;\n'%(module_name))
    top_file.write('        rst_period = $urandom_range(200,2000);\n')
    top_file.write('        #rst_period;\n')
    top_file.write('        @(posedge %s_if.clk)\n'%(module_name))
    top_file.write('        %s_if.rstn <= 1;\n'%(module_name))
    if reg_model == 'ahb':
        top_file.write('        @(posedge hclk)\n')
        top_file.write('        hrstn <= 1;\n')
    elif reg_model == 'apb':  
        top_file.write('        @(posedge pclk)\n')
        top_file.write('        prstn <= 1;\n')    
    top_file.write('    end\n')    
    top_file.write('\n')
    top_file.write('    initial begin\n')
    top_file.write('        run_test();\n')
    top_file.write('    end\n')
    top_file.write('\n')
    top_file.write('    //dump fsdb\n')
    top_file.write('    initial begin\n')
    top_file.write('        $fsdbDumpfile("top.fsdb");\n')
    top_file.write('        $fsdbDumpvars();\n')
    top_file.write('        $fsdbDumpon();\n')
    top_file.write('    end\n')
    top_file.write('\n')
    top_file.write('    initial begin\n')
    top_file.write('        timeformat(-9, 0, "ns", 10);// set print time format, 1ns unit, 10^(-3) precision, ns suffix, 20 character length\n')
    top_file.write('    end\n')
    top_file.write('\n')
    top_file.write('    //============ Instantiate DUT ============\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('    //============ Instantiate VIP ============\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('\n')
    top_file.write('endmodule\n')
    top_file.write('`endif //%s_TOP__SV'%(module_name.upper()))
    top_file.close()

                
def create_if_file(module_name):
    #Define a function to create a user interface file
    def create_user_if_file(module_name):
        #Open the user interface file
        user_if_file = open('%s_if.sv'%(module_name),'w')
        #Write the preprocessor directive to the user interface file
        user_if_file.write('`ifndef %s_IF__SV\n'%(module_name.upper()))
        user_if_file.write('`define %s_IF__SV\n'%(module_name.upper()))
        user_if_file.write('\n')
        #Write the interface code to the user interface file
        user_if_file.write('interface %s_if;\n'%(module_name))
        user_if_file.write('\n')
        user_if_file.write('    //Signals\n')
        user_if_file.write('    logic         clk;\n')
        user_if_file.write('    logic         rstn;\n')
        user_if_file.write('    logic [31:0]  data;\n')
        user_if_file.write('\n')
        user_if_file.write('endinterface\n')
        user_if_file.write('`endif')
        #Close the user interface file
        user_if_file.close()

    #Define a function to create an APB interface file
    def create_apb_if_file():
        #Define the APB interface code
        apb_if_code = '''
`ifndef APB_IF__SV
`define APB_IF__SV

interface apb_if(input pclk,input prstn);

    logic           psel;
    logic           penable;
    logic           pwrite;
    logic           pready;
    logic [31:0]    paddr;
    logic [31:0]    pwdata;
    logic [31:0]    prdata;

endinterface
`endif
'''
        #Open the APB interface file
        apb_if_file = open('apb_if.sv','w')
        #Write the APB interface code to the APB interface file
        apb_if_file.write(apb_if_code)
        #Close the APB interface file
        apb_if_file.close()
    
    #Define a function to create an AHB interface file
    def create_ahb_if_file():
        #Define the AHB interface code
        ahb_if_code = '''
`ifndef AHB_IF__SV
`define AHB_IF__SV

interface ahb_if(input hclk,input hrstn);

    logic           hsel;
    logic           hready_in;
    logic           hready_out;

    logic           hwrite;
    logic [31:0]    haddr;
    logic [31:0]    hwdata;
    logic [31:0]    hrdata;
    logic [1:0]     htrans;
    logic [2:0]     hsize;
    logic [2:0]     hburst;
    logic [1:0]     hresp;

endinterface
`endif
'''

#Define a function called create_user_if_file that takes one argument called module_name
#Open a file called ahb_if.sv in write mode and assign it to the variable ahb_if_file
#Write the code in the function to the file
#Close the file
        ahb_if_file = open('ahb_if.sv','w')
        ahb_if_file.write(ahb_if_code)
        ahb_if_file.close() 

#Define a function called create_apb_if_file
#Open a file called apb_if.sv in write mode and assign it to the variable apb_if_file
#Write the code in the function to the file
#Close the file
    create_user_if_file(module_name)
    create_apb_if_file()
    create_ahb_if_file()

#Define a function to create a base test file for a given module name
def create_base_test_file(module_name):
    #Open a file with the given module name and write the code to it
    test_file = open('%s_base_test.sv'%(module_name),'w')
    #Write the defines for the test file
    test_file.write('`ifndef %s_BASE_TEST__SV\n'%(module_name.upper()))
    test_file.write('`define %s_BASE_TEST__SV\n'%(module_name.upper()))
    test_file.write('\n')
    #Write the class for the test file
    test_file.write('class %s_base_test extends uvm_test;\n'%(module_name))
    test_file.write('    %s_env env;\n'%(module_name))
    test_file.write('    `uvm_component_utils(%s_base_test)\n'%(module_name))
    test_file.write('\n')
    #Write the constructor for the test file
    test_file.write('    function new(string name = "%s_base_test", uvm_component parent = null);\n'%(module_name))
    test_file.write('        super.new(name,parent);\n')
    test_file.write('    endfunction\n')
    test_file.write('\n')
    #Write the build_phase function for the test file

    test_file.write('    virtual function void build_phase(uvm_phase phase);\n')
    test_file.write('        `uvm_info(get_type_name(), " ---------- Build Phase ----------", UVM_LOW)\n')
    test_file.write('        super.build_phase(phase);\n')
    test_file.write('        env = %s_env::type_id::create("env", this);\n'%(module_name))
    test_file.write('    endfunction\n')
    test_file.write('\n')

    test_file.write('    virtual task main_phase(uvm_phase phase);\n')
    test_file.write('        `uvm_info(get_type_name(), " ----------  Main Phase ----------", UVM_LOW)\n')
    test_file.write('        super.main_phase(phase);\n')
    test_file.write('        phase.phase_done.set_drain_time(this,1000);\n')
    test_file.write('    endtask\n')
    test_file.write('\n')

    #Write the report_phase function for the test file
    test_file.write('    virtual function void report_phase(uvm_phase phase);\n')

    #Write the test code to the test file
    test_code = '''
        uvm_report_server server;
        int err_num;

        `uvm_info(get_type_name(), " ---------- Base_test Report Phase ----------", UVM_LOW)
        super.report_phase(phase);

        server = uvm_report_server::get_server();
        err_num = server.get_severity_count(UVM_ERROR);

        if(err_num == 0)begin
            $display("\\n");
            $display("          \\033[32m ppppppp      AAA        SSSS        SSSS     \\033[0m");
            $display("          \\033[32m pp    pp    AA AA     SS    SS    SS    SS   \\033[0m");
            $display("          \\033[32m pp    pp   AA   AA    SS          SS         \\033[0m");
            $display("          \\033[32m ppppppp   AA     AA      SS          SS      \\033[0m");
            $display("          \\033[32m pp        AAAAAAAAA        SS          SS    \\033[0m");
            $display("          \\033[32m pp        AA     AA          SS          SS  \\033[0m");
            $display("          \\033[32m pp        AA     AA    SS    SS    SS    SS  \\033[0m");
            $display("          \\033[32m pp        AA     AA      SSSS        SSSS    \\033[0m");
            $display("\\n");
        end
        else begin
            $display("\\n");
            $display("          \\033[31m FFFFFFFF     AAA         IIII    LL           \\033[0m");
            $display("          \\033[31m FF          AA AA         II     LL           \\033[0m");
            $display("          \\033[31m FF         AA   AA        II     LL           \\033[0m");
            $display("          \\033[31m FFFFFFFF  AA     AA       II     LL           \\033[0m");
            $display("          \\033[31m FF        AAAAAAAAA       II     LL           \\033[0m");
            $display("          \\033[31m FF        AA     AA       II     LL           \\033[0m");
            $display("          \\033[31m FF        AA     AA       II     LL           \\033[0m");
            $display("          \\033[31m FF        AA     AA      IIII    LLLLLLLLLL   \\033[0m");
            $display("\\n");
        end
    endfunction
endclass
`endif
'''
    test_file.write(test_code)
    #Close the test file
    test_file.close()

def create_example_test_file(module_name):
    example_test_file = open('%s_example_test.sv'%(module_name),'w')
    example_test_file.write('`ifndef %s_EXAMPLE_TEST__SV\n'%(module_name.upper()))
    example_test_file.write('`define %s_EXAMPLE_TEST__SV\n'%(module_name.upper()))
    example_test_file.write('\n')
    example_test_file.write('class %s_example_test extends %s_base_test;\n'%(module_name,module_name))
    example_test_file.write('    `uvm_component_utils(%s_example_test)\n'%(module_name))
    example_test_file.write('\n')
    example_test_file.write('    function new(string name = "%s_example_test", uvm_component parent);\n'%(module_name))
    example_test_file.write('        super.new(name,parent);\n')
    example_test_file.write('    endfunction\n')
    example_test_file.write('\n')
    example_test_file.write('    virtual function void build_phase(uvm_phase phase);\n')
    example_test_file.write('        super.build_phase(phase);\n')
    example_test_file.write('        uvm_config_db#(uvm_object_wrapper)::set(this,\n')
    example_test_file.write('                                                "env.i_agt.sqr.main_phase",\n')
    example_test_file.write('                                                "default_sequence",\n')
    example_test_file.write('                                                %s_example_seq::type_id::get());\n'%(module_name))
    example_test_file.write('    endfunction\n')
    example_test_file.write('endclass\n')
    example_test_file.write('`endif\n')
    example_test_file.write('\n')
    example_test_file.close()

#Define a function to create a base sequence file
def create_base_seq_file(module_name):
    #Open the sequence file
    seq_file = open('%s_base_seq.sv'%(module_name),'w')
    #Write the defines for the sequence file
    seq_file.write('`ifndef %s_BASE_SEQ__SV\n'%(module_name.upper()))
    seq_file.write('`define %s_BASE_SEQ__SV\n'%(module_name.upper()))
    seq_file.write('\n')    
    #Write the sequence class
    seq_file.write('class %s_base_seq extends uvm_sequence#(%s_transaction);\n'%(module_name,module_name))
    seq_file.write('\n')
    #Write the transaction
    seq_file.write('    %s_transaction %s_tr;\n'%(module_name,module_name))
    seq_file.write('\n')
    #Write the interface
    seq_file.write('    virtual %s_if %s_if;\n'%(module_name,module_name))
    seq_file.write('\n')
    #Write the register model
    seq_file.write('    ral_block_%s_reg reg_model;\n'%(module_name))
    seq_file.write('    //Add Control Interface\n')
    seq_file.write('\n')
    seq_file.write('\n')
    seq_file.write('\n')
    seq_file.write('\n')
    #Write the status and rdata variables
    seq_file.write('    uvm_status_e status;\n')
    seq_file.write('    uvm_reg_data_t rdata;\n')
    seq_file.write('\n')    
    #Write the uvm_object_utils
    seq_file.write('    `uvm_object_utils(%s_base_seq)\n'%(module_name))
    seq_file.write('    `uvm_declare_p_sequencer(%s_sequencer)\n'%(module_name))  
    seq_file.write('\n')      
    #Write the new function
    seq_file.write('    function new(string name = "%s_base_seq");\n'%(module_name))
    seq_file.write('        super.new(name);\n')
    seq_file.write('        set_automatic_phase_objection(1);\n')
    seq_file.write('    endfunction\n')
    seq_file.write('\n')
    #Write the get_config_db function
    seq_file.write('    task get_config_db();\n')
    seq_file.write('        if(!uvm_config_db#(virtual %s_if)::get(null, "", "%s_if", %s_if))\n'%(module_name,module_name,module_name))
    seq_file.write('            `uvm_fatal(get_name(),"  Cannot get %s_if from top");\n'%(module_name))
    seq_file.write('        if(!uvm_config_db#(ral_block_%s_reg)::get(null, "","reg_model",reg_model))\n'%(module_name))
    seq_file.write('            `uvm_fatal(get_name()," Cannot get reg_model from top ");\n
    seq_file.write('        //Add Other Config_db')
    seq_file.write('\n')
    seq_file.write('\n')
    seq_file.write('\n')
    seq_file.write('\n')
    seq_file.write('    endtask\n')
    seq_file.write('\n')
    #Write the body function
    seq_file.write('    virtual task body();\n')
    seq_file.write('        `uvm_info(get_name(), "Starting the sequence", UVM_LOW)\n')
    seq_file.write('        get_config_db();\n')
    seq_file.write('        //wait rstn end\n')
    seq_file.write('        #2000;')
    seq_file.write('        //Add sequence body')
    seq_file.write('\n')
    seq_file.write('\n')
    seq_file.write('\n')
    seq_file.write('\n')
    seq_file.write('    endtask\n')   
    seq_file.write('endclass\n')
    seq_file.write('`endif')
    seq_file.close()

def create_example_seq_file(module_name):
    example_seq_file = open('%s_example_seq.sv'%(module_name),'w')
    example_seq_file.write('`ifndef %s_EXAMPLE_SEQ__SV\n'%(module_name.upper()))
    example_seq_file.write('`define %s_EXAMPLE_SEQ__SV\n'%(module_name.upper()))
    example_seq_file.write('\n')    
    example_seq_file.write('class %s_example_seq extends %s_base_seq#(%s_transaction);\n'%(module_name,module_name,module_name))
    example_seq_file.write('\n')     
    example_seq_file.write('    `uvm_object_utils(%s_example_seq)\n'%(module_name))
    example_seq_file.write('\n')      
    example_seq_file.write('    function new(string name = "%s_example_seq");\n'%(module_name))
    
    #example_seq_file.write('        super.new(name);\n')
    example_seq_file.write('    endfunction\n')
    example_seq_file.write('\n')
    example_seq_file.write('    virtual task body();\n')
    example_seq_file.write('        super.body();\n')  
    example_seq_file.write('        //Add Your Code')
    example_seq_file.write('\n')
    example_seq_file.write('\n')
    example_seq_file.write('\n')
    example_seq_file.write('\n')
    example_seq_file.write('        `uvm_info(get_name(), "---------- ending the %s_example_seq ----------", UVM_LOW)\n'%(module_name))   
    example_seq_file.write('    endtask\n')   
    example_seq_file.write('endclass\n')
    example_seq_file.write('`endif')
    example_seq_file.close()

#Define a function called create_env_file that takes two parameters, module_name and reg_model
def create_env_file(module_name,reg_model):
    #Open a file called %s_env.sv in write mode and store it in the variable env_file
    env_file = open('%s_env.sv'%(module_name),'w')
    env_file.write('`ifndef %s_ENV__SV\n'%(module_name.upper()))
    env_file.write('`define %s_ENV__SV\n'%(module_name.upper()))
    env_file.write('\n')
    env_file.write('class %s_env extends uvm_env;\n'%(module_name))
    env_file.write('\n')
    env_file.write('    `uvm_component_utils(%s_env)\n'%(module_name))
    env_file.write('\n')
    env_file.write('    %s_scoreboard  scb;\n'%(module_name))
    env_file.write('    %s_i_agent     i_agt;\n'%(module_name))
    env_file.write('    %s_o_agent     o_agt;\n'%(module_name))
    env_file.write('    %s_ref_model   ref_model;\n'%(module_name))  
    env_file.write('\n')
    if(reg_model == 'apb'):
        env_file.write('    apb_agent       apb_agt;\n')  
        env_file.write('    apb_adapter     apb_adap;\n')
    elif(reg_model == 'ahb'):
        env_file.write('    ahb_agent       ahb_agt;\n')   
        env_file.write('    ahb_adapter     ahb_adap;\n') 
    env_file.write('\n')
    env_file.write('    ral_block_%s_reg reg_model;\n'%(module_name))
    env_file.write('\n')
    env_file.write('    uvm_tlm_analysis_fifo#(%s_transaction) i_mon_to_scb_fifo;\n'%(module_name))
    env_file.write('    uvm_tlm_analysis_fifo#(%s_transaction) o_mon_to_scb_fifo;\n'%(module_name))
    env_file.write('\n')
    env_file.write('    function new(string name = "%s_env", uvm_component parent);\n'%(module_name))
    env_file.write('        super.new(name, parent);\n')
    env_file.write('    endfunction\n')
    env_file.write('\n')
    env_file.write('    function void build_phase(uvm_phase phase);\n')
    env_file.write('        super.build_phase(phase);\n')
    env_file.write('        `uvm_info(get_type_name(), " ---------- Env Build Phase ----------", UVM_LOW)\n')
    env_file.write('        if(!uvm_config_db#(ral_block_%s_reg)::get(this, "","reg_model",reg_model))\n'%(module_name))
    env_file.write('            `uvm_fatal(get_full_name(),$sformatf("Cannot get reg_model from config db"))\n')
    env_file.write('\n')
    env_file.write('        i_mon_to_scb_fifo = new("i_mon_to_scb_fifo", this);\n')
    env_file.write('        o_mon_to_scb_fifo = new("o_mon_to_scb_fifo", this);\n')
    env_file.write('\n')
    env_file.write('        scb       = %s_scoreboard::type_id::create("scb", this);\n'%(module_name))
    if(reg_model == 'apb'):
        env_file.write('        apb_agt   = apb_agent::type_id::create("apb_agt", this);\n')
    elif(reg_model == 'ahb'):
        env_file.write('        ahb_agt   = ahb_agent::type_id::create("ahb_agt", this);\n')
    env_file.write('        i_agt     = %s_i_agent::type_id::create("i_agt", this);\n'%(module_name))
    env_file.write('        o_agt     = %s_o_agent::type_id::create("o_agt", this);\n'%(module_name))                   
    env_file.write('\n')
    env_file.write('        ref_model = %s_ref_model::type_id::create("ref_model", this);\n'%(module_name))
    env_file.write('\n')    
    if(reg_model == 'apb'):
        env_file.write('        apb_adap  = apb_adapter::type_id::create("apb_adap", this);\n')
        env_file.write('        apb_adap.provides_responses = 1;\n')
    elif(reg_model == 'ahb'):
        env_file.write('        ahb_adap  = ahb_adapter::type_id::create("ahb_adap", this);\n')
        env_file.write('        ahb_adap.provides_responses = 1;\n')
    env_file.write('\n')
    if(reg_model == 'apb'):
        env_file.write('        reg_model.build();\n')
        env_file.write('        reg_model.lock_model;\n')
        env_file.write('        reg_model.reset();\n')
        env_file.write('\n')
    elif(reg_model == 'ahb'):   
        env_file.write('        reg_model.build();\n')
        env_file.write('        reg_model.lock_model;\n')
        env_file.write('        reg_model.reset();\n')
        env_file.write('    endfunction\n')
        env_file.write('\n')
    env_file.write('    virtual function void connect_phase(uvm_phase phase);\n')
    env_file.write('        `uvm_info(get_type_name(), " ---------- Env Connect Phase ----------", UVM_LOW)\n')
    env_file.write('        super.connect_phase(phase);\n')
    env_file.write('\n')
    env_file.write('        i_agt.i_mon_ap.connect(i_mon_to_scb_fifo.analysis_export);\n')
    env_file.write('        scb.i_mon_port.connect(i_mon_to_scb_fifo.blocking_get_export);\n')
    env_file.write('\n')
    env_file.write('        o_agt.o_mon_ap.connect(o_mon_to_scb_fifo.analysis_export);\n')
    env_file.write('        scb.o_mon_port.connect(o_mon_to_scb_fifo.blocking_get_export);\n')
    env_file.write('\n')
    if(reg_model == 'apb'):
        env_file.write('        reg_model.default_map.set_sequencer(apb_agt.sqr,apb_adap);\n')
        env_file.write('        reg_model.default_map.set_auto_predict(1);\n')
    elif(reg_model == 'ahb'):
        env_file.write('        reg_model.default_map.set_sequencer(ahb_agt.sqr,ahb_adap);\n')
        env_file.write('        reg_model.default_map.set_auto_predict(1);\n')
    else:
        print("\033[31m  [Error] : uvm_gen.py 484 line")
        print("\033[31m -------[Error] :  reg_model not set or set != ahb/apb  \033[0m")
        sys.exit(1)

    env_file.write('    endfunction\n')
    env_file.write('endclass\n')
    env_file.write('`endif')
    env_file.close()

def create_scb_file(module_name):
    scb_file = open('%s_scoreboard.sv'%(module_name),'w')
    scb_file.write('`ifndef %s_SCOREBOARD__SV\n'%(module_name.upper()))
    scb_file.write('`define %s_SCOREBOARD__SV\n'%(module_name.upper()))
    scb_file.write('\n')
    scb_file.write('class %s_scoreboard extends uvm_scoreboard;\n'%(module_name))
    scb_file.write('\n')
    scb_file.write('    `uvm_component_utils(%s_scoreboard)\n'%(module_name))
    scb_file.write('\n')
    scb_file.write('    ral_block_%s_reg reg_model;\n'%(module_name))
    scb_file.write('    uvm_status_e    status;\n')
    scb_file.write('    uvm_reg_data_t  rdata;\n')
    scb_file.write('\n')
    scb_file.write('    virtual %s_if %s_if;\n'%(module_name,module_name))
    scb_file.write('    //Blocking Get Port\n')
    scb_file.write('    uvm_blocking_get_port #(%s_transaction) i_mon_port;\n'%(module_name))
    scb_file.write('    uvm_blocking_get_port #(%s_transaction) o_mon_port;\n'%(module_name))
    scb_file.write('\n')
    scb_file.write('    function new(string name = "%s_scoreboard", uvm_component parent);\n'%(module_name))
    scb_file.write('        super.new(name, parent);\n')
    scb_file.write('    endfunction\n')
    scb_file.write('\n')

    scb_file.write('    function void build_phase(uvm_phase phase);\n')
    scb_file.write('        `uvm_info(get_type_name(), " ---------- Scb Build Phase ----------", UVM_LOW)\n')
    scb_file.write('        super.build_phase(phase);\n')
    scb_file.write('\n')
    scb_file.write('        if(!uvm_config_db#(virtual %s_if)::get(this, "","%s_if",%s_if))\n'%(module_name,module_name,module_name))
    scb_file.write('            `uvm_fatal(get_full_name(),"Failed to get interface");\n')
    scb_file.write('        if(!uvm_config_db#(ral_block_%s_reg)::get(this, "","reg_model",reg_model))\n'%(module_name))
    scb_file.write('            `uvm_fatal(get_full_name(),"Failed to get reg_model");\n')
    scb_file.write('\n')
    scb_file.write('        //Add Other Config_db Get')
    scb_file.write('\n')
    scb_file.write('\n')
    scb_file.write('\n')
    scb_file.write('\n')
    scb_file.write('        i_mon_port = new("i_mon_port", this);\n')
    scb_file.write('        o_mon_port = new("o_mon_port", this);\n')
    scb_file.write('    endfunction\n')
    scb_file.write('\n')
    scb_file.write('    virtual task main_phase(uvm_phase phase);\n')
    scb_file.write('        `uvm_info(get_type_name(), " ---------- Scb Main Phase ----------", UVM_LOW)\n')
    scb_file.write('        super.main_phase(phase);\n')
    scb_file.write('        //Add Your Code\n')
    scb_file.write('        #1000;\n') 
    scb_file.write('\n')
    scb_file.write('\n')
    scb_file.write('\n')
    scb_file.write('    endtask\n')
    scb_file.write('endclass\n')
    scb_file.write('`endif')
    scb_file.close()

def create_ref_model_file(module_name):
    ref_model_file = open('%s_ref_model.sv'%(module_name),'w')
    ref_model_file.write('`ifndef %s_REF_MODEL__SV\n'%(module_name.upper()))
    ref_model_file.write('`define %s_REF_MODEL__SV\n'%(module_name.upper()))
    ref_model_file.write('\n')
    ref_model_file.write('class %s_ref_model extends uvm_component;\n'%(module_name))
    ref_model_file.write('\n')
    ref_model_file.write('    `uvm_component_utils(%s_ref_model)\n'%(module_name))
    ref_model_file.write('    //Add Your Code\n')
    ref_model_file.write('\n')
    ref_model_file.write('\n')
    ref_model_file.write('\n')
    ref_model_file.write('\n')
    ref_model_file.write('    function new(string name = "%s_ref_model", uvm_component parent);\n'%(module_name))
    ref_model_file.write('        super.new(name,parent);\n')
    ref_model_file.write('    endfunction\n')
    ref_model_file.write('\n')
    ref_model_file.write('    function void build_phase(uvm_phase phase);\n')
    ref_model_file.write('        `uvm_info(get_type_name(), " ---------- Ref_model Build Phase ----------", UVM_LOW)\n')
    ref_model_file.write('        super.build_phase(phase);\n')
    ref_model_file.write('        //Add Your Code\n')
    ref_model_file.write('\n')
    ref_model_file.write('\n')
    ref_model_file.write('\n')
    ref_model_file.write('\n')
    ref_model_file.write('    endfunction\n')
    ref_model_file.write('\n')
    ref_model_file.write('    virtual task main_phase(uvm_phase phase);\n')
    ref_model_file.write('        `uvm_info(get_type_name(), " ---------- Ref_model Main Phase ----------", UVM_LOW)\n')
    ref_model_file.write('    //Add Your Code\n')
    ref_model_file.write('        #1000;\n') 
    ref_model_file.write('\n')
    ref_model_file.write('\n')
    ref_model_file.write('\n')
    ref_model_file.write('\n')
    ref_model_file.write('    endtask\n')
    ref_model_file.write('endclass\n')
    ref_model_file.write('`endif')
    ref_model_file.close()

def create_tr_file(module_name):
    tr_file = open('%s_transaction.sv'%(module_name),'w')
    tr_file.write('`ifndef %s_TRANSACTION__SV\n'%(module_name.upper()))
    tr_file.write('`define %s_TRANSACTION__SV\n'%(module_name.upper()))   
    tr_file.write('\n')     
    tr_file.write('class %s_transaction extends uvm_sequence_item;\n'%(module_name))    
    tr_file.write('\n')    
    tr_file.write('    // Add transaction fields here\n')
    tr_file.write('    // Example:\n')
    tr_file.write('    // rand bit [7:0] %s_data;\n'%(module_name))
    tr_file.write('    // rand bit [1:0] %s_addr;\n'%(module_name))
    tr_file.write('    constraint %s_const{\n'%(module_name))
    tr_file.write('    // Add constraints here\n')
    tr_file.write('\n')
    tr_file.write('\n')
    tr_file.write('\n')
    tr_file.write('    }\n')
    tr_file.write('\n')
    tr_file.write('`uvm_object_utils(%s_transaction)\n'%(module_name))
    tr_file.write('\n')
    tr_file.write('    function new(string name = "%s_transaction");\n'%(module_name))
    tr_file.write('        super.new(name);\n')
    tr_file.write('    endfunction\n')
    tr_file.write('endclass\n')
    tr_file.write('`endif //%s_TRANSACTION__SV'%(module_name.upper()))
    tr_file.close()

def create_i_agt_file(module_name):
    i_agt_file = open('%s_i_agent.sv'%(module_name),'w')
    i_agt_file.write('`ifndef %s_I_AGENT__SV\n'%(module_name.upper()))
    i_agt_file.write('`define %s_I_AGENT__SV\n'%(module_name.upper()))
    i_agt_file.write('\n')
    i_agt_file.write('class %s_i_agent extends uvm_agent;\n'%(module_name))
    i_agt_file.write('    %s_driver     drv;\n'%(module_name))
    i_agt_file.write('    %s_i_monitor  i_mon;\n'%(module_name))
    i_agt_file.write('    %s_sequencer  sqr;\n'%(module_name))
    i_agt_file.write('    uvm_analysis_port#(%s_transaction) i_mon_ap;\n'%(module_name))
    i_agt_file.write('\n')
    i_agt_file.write('    `uvm_component_utils(%s_i_agent)\n'%(module_name))                                              
    i_agt_file.write('\n')                                       
    i_agt_file.write('    function new(string name = "%s_i_agent", uvm_component parent);\n'%(module_name))
    i_agt_file.write('        super.new(name, parent);\n')
    i_agt_file.write('    endfunction\n')
    i_agt_file.write('\n')
    i_agt_file.write('    function void build_phase(uvm_phase phase);\n')
    i_agt_file.write('        `uvm_info(get_type_name(), " ---------- I_agent Build Phase ----------", UVM_LOW)\n')
    i_agt_file.write('        super.build_phase(phase);\n')
    i_agt_file.write('        drv   = %s_driver::type_id::create("drv", this);\n'%(module_name))
    i_agt_file.write('        i_mon = %s_i_monitor::type_id::create("i_mon", this);\n'%(module_name))
    i_agt_file.write('        sqr   = %s_sequencer::type_id::create("sqr", this);\n'%(module_name))
    i_agt_file.write('    endfunction\n')
    i_agt_file.write('\n')   
    i_agt_file.write('    function void connect_phase(uvm_phase phase);\n')
    i_agt_file.write('        `uvm_info(get_type_name(), " ---------- I_agent Connect Phase ----------", UVM_LOW)\n')
    i_agt_file.write('        super.connect_phase(phase);\n')
    i_agt_file.write('        drv.seq_item_port.connect(sqr.seq_item_export);\n')
    i_agt_file.write('        i_mon_ap = i_mon.i_mon_ap;\n')
    i_agt_file.write('    endfunction\n')
    i_agt_file.write('endclass\n')
    i_agt_file.write('`endif')
    i_agt_file.close()

def create_driver_file(module_name):
    driver_file = open('%s_driver.sv'%(module_name),'w')
    driver_file.write('`ifndef %s_DRIVER__SV\n'%(module_name.upper()))
    driver_file.write('`define %s_DRIVER__SV\n'%(module_name.upper()))
    driver_file.write('\n')
    driver_file.write('class %s_driver extends uvm_driver#(%s_transaction);\n'%(module_name,module_name))
    driver_file.write('\n')
    driver_file.write('    //Add Your Variable\n')
    driver_file.write('\n')
    driver_file.write('\n')
    driver_file.write('\n')
    driver_file.write('\n')
    driver_file.write('\n')
    driver_file.write('    virtual %s_if %s_if;\n'%(module_name,module_name))
    driver_file.write('\n')
    driver_file.write('    function new(string name = "%s_driver", uvm_component parent);\n'%(module_name))
    driver_file.write('        super.new(name, parent);\n')
    driver_file.write('    endfunction\n')
    driver_file.write('    `uvm_component_utils(%s_driver)\n'%(module_name))    
    driver_file.write('\n')
    driver_file.write('    function void build_phase(uvm_phase phase);\n')
    driver_file.write('        `uvm_info(get_type_name(), " ---------- Driver Build Phase ----------", UVM_LOW)\n')
    driver_file.write('        super.build_phase(phase);\n')
    driver_file.write('        if(!uvm_config_db#(virtual %s_if)::get(this, "", "%s_if", %s_if))\n'%(module_name,module_name,module_name))
    driver_file.write('            `uvm_fatal(get_full_name(), "Could not get vif")\n')
    driver_file.write('    endfunction\n')
    driver_file.write('\n')
    driver_file.write('    virtual task main_phase(uvm_phase phase);\n')
    driver_file.write('        `uvm_info(get_type_name(), " ---------- Driver Main Phase ----------", UVM_LOW)\n')
    driver_file.write('        super.main_phase(phase);\n')
    driver_file.write('        while(1)begin\n')
    driver_file.write('            if(!%s_if.rstn)begin\n'%(module_name))
    driver_file.write('                %s_if.data <= 0;\n'%(module_name))
    driver_file.write('                //Reset Your Signal Here\n')
    driver_file.write('\n')
    driver_file.write('\n')
    driver_file.write('\n')
    driver_file.write('\n')
    driver_file.write('                @(posedge %s_if.clk);\n'%(module_name))
    driver_file.write('            end\n')
    driver_file.write('            else begin\n')  
    driver_file.write('                seq_item_port.get_next_item(req);\n')
    driver_file.write('                drive_one_pkt(req);\n')
    driver_file.write('                seq_item_port.item_done();\n')
    driver_file.write('            end\n')
    driver_file.write('        end\n')
    driver_file.write('    endtask\n')
    driver_file.write('\n')

    driver_file.write('    virtual task drive_one_pkt(%s_transaction tr);\n'%(module_name))
    driver_file.write('        //Drive Your Signal Here\n')
    driver_file.write('        #1000;\n') 
    driver_file.write('\n')   
    driver_file.write('\n')
    driver_file.write('\n')
    driver_file.write('\n')
    driver_file.write('    endtask\n')
    driver_file.write('endclass\n')
    driver_file.write('`endif')
    driver_file.close()

def create_i_mon_file(module_name):
    i_mon_file = open('%s_i_monitor.sv'%(module_name),'w')
    i_mon_file.write('`ifndef %s_I_MONITOR__SV\n'%(module_name.upper()))
    i_mon_file.write('`define %s_I_MONITOR__SV\n'%(module_name.upper()))
    i_mon_file.write('\n')
    i_mon_file.write('class %s_i_monitor extends uvm_monitor;\n'%(module_name))
    i_mon_file.write('\n')
    i_mon_file.write('    `uvm_component_utils(%s_i_monitor)\n'%(module_name))
    i_mon_file.write('\n')
    i_mon_file.write('    virtual %s_if %s_if;\n'%(module_name,module_name))
    i_mon_file.write('    uvm_analysis_port#(%s_transaction) i_mon_ap;\n'%(module_name))
    i_mon_file.write('\n')
    i_mon_file.write('    function new(string name = "%s_i_monitor", uvm_component parent);\n'%(module_name))
    i_mon_file.write('        super.new(name, parent);\n')
    i_mon_file.write('    endfunction\n')
    i_mon_file.write('\n')
    i_mon_file.write('    function void build_phase(uvm_phase phase);\n')
    i_mon_file.write('        `uvm_info(get_type_name(), " ---------- I_monitor Build Phase ----------", UVM_LOW)\n')
    i_mon_file.write('        super.build_phase(phase);\n')
    i_mon_file.write('        if(!uvm_config_db#(virtual %s_if)::get(this, "", "%s_if", %s_if))\n'%(module_name,module_name,module_name))
    i_mon_file.write('            `uvm_fatal(get_full_name(), "Could not get vif")\n')
    i_mon_file.write('        i_mon_ap = new("i_mon_ap", this);\n')
    i_mon_file.write('\n')
    i_mon_file.write('    endfunction\n')
    i_mon_file.write('\n')
    i_mon_file.write('    virtual task main_phase(uvm_phase phase);\n')
    i_mon_file.write('        `uvm_info(get_type_name(), " ---------- I_monitor Main Phase ----------", UVM_LOW)\n')
    i_mon_file.write('        super.main_phase(phase);\n')
    i_mon_file.write('        //Add Your Code Here')
    i_mon_file.write('        #1000;\n')    
    i_mon_file.write('\n')
    i_mon_file.write('\n')
    i_mon_file.write('\n')
    i_mon_file.write('\n')
    i_mon_file.write('    endtask\n')
    i_mon_file.write('endclass\n')
    i_mon_file.write('`endif')
    i_mon_file.close()

def create_sqr_file(module_name):
    sqr_file = open('%s_sequencer.sv'%(module_name),'w')
    sqr_file.write('`ifndef %s_SEQUENCER__SV\n'%(module_name.upper()))
    sqr_file.write('`define %s_SEQUENCER__SV\n'%(module_name.upper()))
    sqr_file.write('\n')
    sqr_file.write('class %s_sequencer extends uvm_sequencer#(%s_transaction);\n'%(module_name,module_name))
    sqr_file.write('\n')
    sqr_file.write('    `uvm_component_utils(%s_sequencer)\n'%(module_name))
    sqr_file.write('\n')
    sqr_file.write('    function new(string name = "%s_sequencer", uvm_component parent);\n'%(module_name))
    sqr_file.write('        super.new(name, parent);\n')
    sqr_file.write('    endfunction\n')
    sqr_file.write('\n')
    sqr_file.write('endclass\n')
    sqr_file.write('`endif')
    sqr_file.close()

def create_o_agent_file(module_name):
    o_agent_file = open('%s_o_agent.sv'%(module_name),'w')
    o_agent_file.write('`ifndef %s_O_AGENT__SV\n'%(module_name.upper()))
    o_agent_file.write('`define %s_O_AGENT__SV\n'%(module_name.upper()))
    o_agent_file.write('\n')
    o_agent_file.write('class %s_o_agent extends uvm_agent;\n'%(module_name))
    o_agent_file.write('\n')
    o_agent_file.write('    `uvm_component_utils(%s_o_agent)\n'%(module_name))
    o_agent_file.write('\n')   
    o_agent_file.write('    %s_o_monitor o_mon;\n'%(module_name))
    o_agent_file.write('    uvm_analysis_port#(%s_transaction) o_mon_ap;\n'%(module_name))
    o_agent_file.write('\n')  
    o_agent_file.write('    function new(string name = "%s_o_monitor", uvm_component parent);\n')   
    o_agent_file.write('      super.new(name, parent);\n')
    o_agent_file.write('    endfunction\n')
    o_agent_file.write('\n')  
    o_agent_file.write('    function void build_phase(uvm_phase phase);\n')
    o_agent_file.write('        `uvm_info(get_type_name(), " ---------- O_agent Build Phase ----------", UVM_LOW)\n')
    o_agent_file.write('      super.build_phase(phase);\n')
    o_agent_file.write('      o_mon = %s_o_monitor::type_id::create("o_mon", this);\n'%(module_name))
    o_agent_file.write('    endfunction\n')
    o_agent_file.write('\n')  
    o_agent_file.write('    function void connect_phase(uvm_phase phase);\n')
    o_agent_file.write('        `uvm_info(get_type_name(), " ---------- O_agent Connect Phase ----------", UVM_LOW)\n')    
    o_agent_file.write('        super.connect_phase(phase);\n')
    o_agent_file.write('        o_mon_ap = o_mon.o_mon_ap;\n')
    o_agent_file.write('    endfunction\n')
    o_agent_file.write('\n')    
    o_agent_file.write('endclass\n')
    o_agent_file.write('`endif')
    o_agent_file.close()

def create_o_mon_file(module_name):
    o_mon_file = open('%s_o_monitor.sv'%(module_name),'w')   
    o_mon_file.write('`ifndef %s_O_MONITOR__SV\n'%(module_name.upper()))   
    o_mon_file.write('`define %s_O_MONITOR__SV\n'%(module_name.upper()))   
    o_mon_file.write('\n')
    o_mon_file.write('class %s_o_monitor extends uvm_monitor;\n'%(module_name))
    o_mon_file.write('\n')
    o_mon_file.write('  `uvm_component_utils(%s_o_monitor)\n'%(module_name))
    o_mon_file.write('\n')
    o_mon_file.write('    uvm_analysis_port#(%s_transaction) o_mon_ap;\n'%(module_name))    
    o_mon_file.write('\n')
    o_mon_file.write('    virtual %s_if %s_if;\n'%(module_name,module_name))
    o_mon_file.write('\n')
    o_mon_file.write('    function new(string name = "%s_o_monitor", uvm_component parent);\n'%(module_name))
    o_mon_file.write('        super.new(name, parent);\n')
    o_mon_file.write('    endfunction\n')
    o_mon_file.write('\n')
    o_mon_file.write('    function void build_phase(uvm_phase phase);\n')
    o_mon_file.write('        `uvm_info(get_type_name(), " ---------- O_monitor Build Phase ----------", UVM_LOW)\n')
    o_mon_file.write('        super.build_phase(phase);\n')
    o_mon_file.write('        if(!uvm_config_db#(virtual %s_if)::get(this, "", "%s_if", %s_if))\n'%(module_name,module_name,module_name))
    o_mon_file.write('            `uvm_fatal(get_full_name(), "Could not get vif")\n')   
    o_mon_file.write('        o_mon_ap = new("o_mon_ap", this);\n')
    o_mon_file.write('    endfunction\n')
    o_mon_file.write('\n')
    o_mon_file.write('    virtual task main_phase(uvm_phase phase);\n') 
    o_mon_file.write('        %s_transaction tr;\n'%(module_name))
    o_mon_file.write('        `uvm_info(get_type_name(), " ---------- O_monitor Main Phase ----------", UVM_LOW)\n')   
    o_mon_file.write('        super.main_phase(phase);\n')
    o_mon_file.write('        while(1) begin\n')
    o_mon_file.write('            tr = new("tr");\n')
    o_mon_file.write('            sampling_tr(tr);\n')
    o_mon_file.write('            o_mon_ap.write(tr);\n')
    o_mon_file.write('        end\n')
    o_mon_file.write('    endtask\n')
    o_mon_file.write('\n')
    o_mon_file.write('    virtual task sampling_tr(%s_transaction tr);\n'%(module_name))
    o_mon_file.write('        //Add Your Sampling Code Here\n')
    o_mon_file.write('        #1000;\n')     
    o_mon_file.write('\n')
    o_mon_file.write('\n')
    o_mon_file.write('\n')
    o_mon_file.write('\n')
    o_mon_file.write('    endtask\n')
    o_mon_file.write('endclass\n')
    o_mon_file.write('`endif')

def create_ralgen_file():
    ralgen_code = '''
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
            if(int(field_bit_list[i]) < 0 or int(field_bit_list[i]) > 31):
                print("\\033[31m -------[Error] ----> %s <---- REG field bit set error , must set in [0:31] \\033[0m"%(reg_current_name))
                sys.exit(1)
            if(int(field_bit_list[i]) <= int(field_bit_list[i+1])):
                print("\\033[31m -------[Error] ----> %s <---- REG field bit is overlap , please check that \\033[0m"%(reg_current_name))
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
            print("\\033[31m -------[Error] ----> %s <---- REG reset_value(%s) != field_reset_value_sum(%s) \\033[0m"%(reg_current_name,reg_list[3],hex(field_reset_vlaue_sum)))
            sys.exit(1)

        #---------------- check field name whether exist same ----------------#
        field_name_appear_cnt = Counter(field_name_lsit)#Counter form python collections
        field_name_same_list  =[string for string, count in field_name_appear_cnt.items() if count > 1]
        if("Reserve" in field_name_same_list):
            field_name_same_list.remove("Reserve")
        if("reserve" in field_name_same_list):
            field_name_same_list.remove("reserve")
        
        if field_name_same_list:
            print("\\033[31m -------[Error] ----> %s <---- REG have same field_name : %s \\033[0m"%(reg_current_name,field_name_same_list[0]))
            sys.exit(1)
        
        #---------------- check field width----------------#
        for i in range(field_nums):
            field_bit = reg_list[4+4*i].strip('[]')
            field_rst_value_width = reg_list[6+4*i].split('\\'h')[0]
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
                print("\\033[31m -------[Error] ----> %s <---- REG  %s field set error, the field_bit_width is %d, the rst_value_width is %d  \\033[0m"%(reg_current_name,reg_list[5+4*i],field_width,field_rst_value_width))
                sys.exit(1)

    #------------------------- reg name check -------------------------#
    def reg_name_check(reg_nums,reg_list):
        reg_name_list = []
        for i in range(reg_nums):
            reg_name_list.append(reg_list[i][2])
        
        reg_name_appear_cnt = Counter(reg_name_list)
        reg_name_same_list  = [string for string, count in reg_name_appear_cnt.items() if count > 1]

        if reg_name_same_list:
            print("\\033[31m -------[Error] ----> %s <---- REG exist same name register  \\033[0m"%(reg_name_same_list[0]))
            sys.exit(1)

    #------------------------- get reg excel file -------------------------#
    #get reg file , if no appoint excel file , exit procedure
    if len(sys.argv) > 1 :
        if(os.path.exists(sys.argv[1]) == False):
            print("\\033[31m -------[Error] : serch excel file fail  \\033[0m")
            sys.exit(1)
        excel_file = xlrd.open_workbook(sys.argv[1])
    else :
        print("\\033[31m -------[Error] : NO appoint excel file   \\033[0m")
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
            print("\\033[31m -------[Error] : last sign \\"end_reg\\" error or no exist \\033[0m")
            sys.exit(1)

        #loop get reg information , write it or ralf file
        for i in range(reg_num):
            reg_list         = []
            field_nums       = 1
            #get current reg offset addr .etc , write to reg_list , column ++
            reg_offset_addr  = reg_sheet.cell_value(current_row,current_column)
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
                print("\\033[31m -------[Error] : the input reg_nums(%d) is != actual reg_nums(%d) \\033[0m"%(reg_num, i + 1))
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
        reg_name_check(reg_num,reg_list_all)
    
        #------------------------------------------------------------------- 
        #open ralf file
        ralf_file = open("%s_reg.ralf"%(module_name),"w")
        ralf_file.write("block %s_reg_model {\\n"%(module_name))
        ralf_file.write("  bytes 4 ;\\n")
        #write reg information
        for i in range(reg_num):   
            ralf_file.write("  register %s @%s {\\n"%(reg_list_all[i][2],reg_list_all[i][1]))
            ralf_file.write("    bytes 4;\\n")
            for j in range(reg_list_all[i][0]):#this range is field nums
                if(reg_list_all[i][5+4*j] != 'Reserve' and reg_list_all[i][5+4*j] != 'reserve'):#only unreserve field write to ralf file, this is ralf format
                    current_field_bit           = reg_list_all[i][4+4*j].strip('[]')
                    current_field_width         = reg_list_all[i][6+4*j].split('\\'h')[0]
                    current_field_width         = int(current_field_width)
                    current_field_rst_value_str = reg_list_all[i][6+4*j].split('\\'h')[1]
                    current_field_rst_value_int = int(current_field_rst_value_str,16)
                    current_field_access        = reg_list_all[i][7+4*j].lower() 
    
                    if(':' in current_field_bit):
                        field_bit_list  = current_field_bit.split(':')
                        field_high_bit  = field_bit_list[0]
                        field_low_bit   = field_bit_list[1]
                        if(field_low_bit != 0):
                            ralf_file.write("    field %s @%s {\\n"%(reg_list_all[i][5+4*j],field_low_bit))
                        else:
                            ralf_file.write("    field %s @0 {\\n"%(reg_list_all[i][5+4*j]))
                    else:
                        if(int(current_field_bit) != 0):
                            ralf_file.write("    field %s @%s {\\n"%(reg_list_all[i][5+4*j],current_field_bit))
                        else:
                            ralf_file.write("    field %s @0 {\\n"%(reg_list_all[i][5+4*j]))
                    
                    if(':' in current_field_bit):
                        ralf_file.write("      bits %s;\\n"%(current_field_width))
                    else:
                        ralf_file.write("      bits 1;\\n")
                    
                    if(current_field_rst_value_int !=0):
                        ralf_file.write("      reset 'h%s;\\n"%(current_field_rst_value_str))
                    
                    ralf_file.write("      access %s;\\n"%(current_field_access))
                    ralf_file.write("    }\\n")
            ralf_file.write("  }\\n")
        ralf_file.write("}\\n")
        ralf_file.close()
    
        vcs_ral_result = os.system('ralgen -t %s_reg_model -uvm %s_reg.ralf -o %s_regmodel'%(module_name,module_name,module_name))
        if(vcs_ral_result ==0):
            print("\\033[32m -------- [Successful]  %s_regmodel.sv  %s_reg.ralf is created  --------\\033[0m"%(module_name,module_name))
        else:
            print("\\033[31m -------- [Error]  the use vcs ralgen command fail , this error is unexpect, please contact the administrator  --------\\033[0m")
        
if __name__=="__main__":
    main()

'''
    ralgen_file = open("ralgen.py", "w")
    ralgen_file.write(ralgen_code)
    ralgen_file.close()

def create_apb_ral_file():
    apb_tr_code = '''
`ifndef APB_TRANSACTION__SV
`define APB_TRANSACTION__SV

typedef enum{READ,WRITE} trans_kind_e;

class apb_tr extends uvm_sequence_item;

    randc bit[31:0] rdata;
    randc bit[31:0] wdata;
    randc bit[31:0] addr;
    randc trans_kind_e trans_kind;

    `uvm_object_utils_begin(apb_tr)
        `uvm_field_int(rdata,UVM_ALL_ON)
        `uvm_field_int(wdata,UVM_ALL_ON)
        `uvm_field_int(addr, UVM_ALL_ON)   
        `uvm_field_enum(trans_kind_e,trans_kind,UVM_ALL_ON)
    `uvm_object_utils_end

    function new(string name = "apb_tr");
       super.new();
   endfunction
endclass
`endif
'''
    apb_tr_file = open("apb_transaction.sv", "w")
    apb_tr_file.write(apb_tr_code)
    apb_tr_file.close()

    apb_agent_code = '''
`ifdnef APB_AGENT__SV
`define APB_AGENT__SV
class apb_agent extends uvm_agent;

    apb_sequencer   sqr;
    apb_driver      drv;

    `uvm_component_utils(apb_agent)

    function new(string name = "apb_agent", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        sqr = apb_sequencer::type_id::create("sqr", this);
        drv = apb_driver::type_id::create("drv", this);
    endfunction

    virtual function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        drv.seq_item_port.connect(sqr.seq_item_export);
    endfunction
endclass
`endif
'''

    apb_agent_file = open("apb_agent.sv", "w")
    apb_agent_file.write(apb_agent_code)
    apb_agent_file.close()

    apb_driver_code = '''
`ifdnef APB_DRIVER__SV
`define APB_DRIVER__SV

class apb_driver extends uvm_driver#(apb_tr);

    virtual apb_if vif;

    `uvm_component_utils(apb_driver)

    function new(string name = "apb_ariver", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if(!uvm_config_db#(virtual apb_if)::get(this, "", "apb_if", vif))
            `uvm_fatal("apb_driver", "    apb_if can't get  ")
    endfunction
    
    task main_phase(uvm_phase phase);
        while(1)begin
            if(!vif.prstn)begin
                vif.paddr    <= 32'b0;       
                vif.pwdata   <= 32'b0;    
                vif.psel     <= 1'b0;       
                vif.pwrite   <= 1'b0;       
                vif.penable  <= 1'b0;       
                @(posedge vif.pclk);
            end
            else begin
                seq_item_port.get_next_item(req);
                
                `ifdef UVM_DISABLE_AUTO_ITEM_RECORDING
                    begin_tr(req);
                `endif
                
                drive_one_pkt(req);

                `ifdef UVM_DISABLE_AUTO_ITEM_RECORDING
                    end_tr(req);
                `endif
                
                void'($cast(rsp,req.clone())));
                rsp.set_id_info(req);
                seq_item_port.item_done(rsp);
            end
        end
    endtask

    task drive_one_pkt(apb_tr tr);
        @(posedge vif.pclk)
        if(tr.trans_kind == WRITE)begin
            vif.paddr       <= tr.addr;    
            vif.psel        <= 1'b1;
            vif.pwrite      <= 1'b1;   
            vif.pwdata      <= tr.wdata;
            
            @(posedge vif.pclk)
            vif.penable     <= 1'b1;
            
            @(posedge vif.pclk)
            while(vif.pready !== 1'b1)begin
                @(posedge vif.pclk);
            end
            vif.penable     <= 1'b0;
            vif.psel        <= 1'b0;
            vif.pwdata      <= 32'b0;
        end
        else begin
            vif.paddr      <= tr.addr;
            vif.psel       <= 1'b1;
            vif.pwrite     <= 1'b0;
            
            @(posedge vif.pclk)
            vif.penable    <= 1'b1;

            @(posedge vif.pclk)
            while(vif.pready !== 1'b1)begin
                @(posedge vif.pclk);
            end
            vif.penable    <= 1'b0;
            vif.psel       <= 1'b0;
            tr.rdata       <= vif.prdata;
        end
    endtask
endclass
`endif
'''

    apb_driver_file = open("apb_driver.sv", "w")
    apb_driver_file.write(apb_driver_code)
    apb_driver_file.close()

    apb_sqr_code = '''
`ifndef APB_sqr__SV
`define APB_sqr__SV

class apb_sequencer extends uvm_sequencer#(apb_tr);

    function new(string name = "apb_sequencer", uvm_component parent);
        super.new(name, parent);
    endfunction

    `uvm_component_utils(apb_sequencer)
endclass
`endif
'''
    apb_sqr_file = open("apb_sqr.sv", "w")
    apb_sqr_file.write(apb_sqr_code)
    apb_sqr_file.close()

    apb_adapter_code = '''
`ifndef APB_ADAPTER__SV
`define APB_ADAPTER__SV

class apb_adapter extends uvm_reg_adapter;

    `uvm_object_utils(apb_adapter)

    string tID = get_type_name();

    function new(string name = "apb_adapter");
        super.new(name, parent);
    endfunction
    
    function uvm_sequence_item reg2bus(const ref uvm_reg_bus_op rw);
        apb_tr tr;
        tr = apb_tr::type_id::create("tr");
        tr.trans_kind = (rw.kind == UVM_WRITE) ? WRITE : READ;
        tr.addr = rw.addr;
        if(tr.trans_kind == WRITE)
            tr.wdata = rw.data;
        return tr;
    endfcuntion

    function void bus2reg(uvm_sequence_item bus_item, ref uvm_reg_bus_op rw);
        apb_tr tr;
        if(!$cast(tr,bus_item))begin
            `uvm_fatal("apb_adapter", " apb_adapter bus_item type cast fail ")
            return;
        end

        rw.kind = (tr.trans_kind == READ) ? UVM_READ : UVM_WRITE;
        rw.addr = tr.addr;
        rw.data = (tr.trans_kind == READ) ? tr.rdata : tr.wdata;
        rw.status = UVM_IS_OK;
    endfunction
endclass
`endif
'''
    apb_adapter_file = open("apb_adapter.sv", "w")
    apb_adapter_file.write(apb_adapter_code)
    apb_adapter_file.close()

def create_ahb_ral_file():
    ahb_tr_code = '''
`ifndef AHB_TRANSACTION__SV
`define AHB_TRANSACTION__SV

typedef enum{READ,WRITE} trans_kind_e;

class ahb_tr extends uvm_sequence_item;

    randc bit[31:0] rdata;
    randc bit[31:0] wdata;
    randc bit[31:0] addr;
    randc trans_kind_e trans_kind;

    `uvm_object_utils_begin(ahb_tr)
        `uvm_field_int(rdata,UVM_ALL_ON)
        `uvm_field_int(wdata,UVM_ALL_ON)
        `uvm_field_int(addr, UVM_ALL_ON)   
        `uvm_field_enum(trans_kind_e,trans_kind,UVM_ALL_ON)
    `uvm_object_utils_end

    function new(string name = "ahb_tr");
       super.new();
   endfunction

endclass
`endif
'''
    ahb_tr_file = open("ahb_transaction.sv", "w")
    ahb_tr_file.write(ahb_tr_code)
    ahb_tr_file.close()

    ahb_sqr_code = '''
`ifndef AHB_sqr__SV
`define AHB_sqr__SV

class ahb_sequencer extends uvm_sequencer#(ahb_tr);

    function new(string name = "ahb_sequencer", uvm_component parent);
        super.new(name, parent);
    endfunction

    `uvm_component_utils(ahb_sequencer)
endclass
`endif
'''
    ahb_sqr_file = open("ahb_sqr.sv", "w")
    ahb_sqr_file.write(ahb_sqr_code)
    ahb_sqr_file.close()

    ahb_driver_code ='''
`ifndef AHB_DRIVER__SV
`define AHB_DRIVER__SV

class ahb_driver extends uvm_driver#(ahb_tr);

    virtual ahb_if vif;

    `uvm_component_utils(ahb_driver)

    function new(string name = "ahb_ariver", uvm_component parent);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if(!uvm_config_db#(virtual ahb_if)::get(this, "", "ahb_if", vif))
            `uvm_fatal("ahb_driver", "    ahb_if can't get  ")
    endfunction

    task main_phase(uvm_phase phase);
        while(1)begin
            if(!vif.hrstn)begin
                vif.haddr    <= 32'b0;       
                vif.hwdata   <= 32'b0;   
                vif.hsel     <= 1'b0;
                vif.hsize    <= 3'b010;       
                vif.hwrite   <= 1'b1;       
                vif.htrans   <= 2'b0;
                vif.hburst   <= 3'b0;       
                @(posedge vif.hclk);
            end
            else begin
                seq_item_port.get_next_item(req);

                `ifdef UVM_DISABLE_AUTO_ITEM_RECORDING
                    begin_tr(req);
                `endif
                
                drive_one_pkt(req);

                `ifdef UVM_DISABLE_AUTO_ITEM_RECORDING
                    end_tr(req);
                `endif
                
                void'($cast(rsp,req.clone()));
                rsp.set_id_info(req);
                seq_item_port.item_done(rsp);
            end
        end
    endtask

    task drive_one_pkt(ahb_tr tr);
        //ahb master write
        if(tr.trans_kind === WRITE)begin
            @(posedge vif.hclk)
            vif.hwrite  <= 1'b1;
            vif.haddr   <= tr.addr;
            vif.htrans  <= 2'b10;  //NOSEQ
            vif.hsize   <= 3'b010; //szie == 32bit 
            vif.hburst  <= 3'b0;   //single transmit
            vif.hsel    <= 1'b1;            

            while(vif.hready_in !== 1'b1)begin
                @(posedge vif.hclk);
            end
            vif.htrans  <= 2'b0;
            vif.hwdata  <= tr.wdata;
            vif.hwrite  <= 1'b0;
            vif.hsel    <= 1'b0;
            end
        end
        //ahb master read
        else begin
            @(posedge vif.hclk)
            vif.hwrite  <= 1'b0;
            vif.haddr   <= tr.addr;
            vif.htrans  <= 2'b10;  //NOSEQ
            vif.hsize   <= 3'b010; //szie == 32bit 
            vif.hburst  <= 3'b0;   //single transmit
            vif.hsel    <= 1'b1;

            while(vif.hready_in !== 1'b1)begin
                @(posedge vif.hclk);
            end
            vif.htrans  <= 2'b0; //IDLE

            while(vif.hready_in !== 1'b1)begin
                @(posedge vif.hclk);
            end
            tr.rdata    <= vif.hrdata;
            vif.haddr   <= 32'b0;
            vif.hsel    <= 1'b0;
        end
    endtask
endclass
`endif
'''
    ahb_driver_file = open("ahb_driver.sv", "w")
    ahb_driver_file.write(ahb_driver_code)
    ahb_driver_file.close()

    ahb_agent_code = '''
`ifndef AHB_AGENT__SV
`define AHB_AGENT__SV
class ahb_agent extends uvm_agent;

    ahb_sequencer   sqr;
    ahb_driver      drv;

    `uvm_component_utils(ahb_agent)

    function new(string name = "ahb_agent", uvm_component parent);
        super.new(name, parent);
    endfunction


    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        sqr = ahb_sequencer::type_id::create("sqr", this);
        drv = ahb_driver::type_id::create("drv", this);
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        drv.seq_item_port.connect(sqr.seq_item_export);
    endfunction
endclass
`endif
'''
    ahb_agent_file = open("ahb_agent.sv", "w")
    ahb_agent_file.write(ahb_agent_code)
    ahb_agent_file.close()

    ahb_adapter_code = '''
`ifndef AHB_ADAPTER__SV
`define AHB_ADAPTER__SV

class ahb_adapter extends uvm_reg_adapter;

    `uvm_object_utils(ahb_adapter)

    string tID = get_type_name();

    function new(string name = "ahb_adapter");
        super.new(name);
    endfunction
    
    function uvm_sequence_item reg2bus(const ref uvm_reg_bus_op rw);
        ahb_tr tr;
        tr = ahb_tr::type_id::create("tr");
        tr.trans_kind = (rw.kind == UVM_WRITE) ? WRITE : READ;
        tr.addr = rw.addr;
        if(tr.trans_kind == WRITE)
            tr.wdata = rw.data;
        return tr;
    endfunction

    function void bus2reg(uvm_sequence_item bus_item, ref uvm_reg_bus_op rw);
        ahb_tr tr;
        if(!$cast(tr,bus_item))begin
            `uvm_fatal("ahb_adapter", " ahb_adapter bus_item type cast fail ")
            return;
        end

        rw.kind = (tr.trans_kind == READ) ? UVM_READ : UVM_WRITE;
        rw.addr = tr.addr;
        rw.data = (tr.trans_kind == READ) ? tr.rdata : tr.wdata;
        rw.status = UVM_IS_OK;
    endfunction
endclass
`endif
'''
    ahb_adapter_file = open("ahb_adapter.sv", "w")
    ahb_adapter_file.write(ahb_adapter_code)
    ahb_adapter_file.close()

def create_makefile():
    makefile = open("Makefile","w") 
    makefile_code = '''
.PTHONY: clean verdi

case_name := $(word 2, $(MAKECMDGOALS))
seed := 0
other_file := *.h simv.* *.log csrc *.key *.vpd DVEfiles* coverage *.vdb verdiLog novas* *fsdb* _vcs* *signal* *tmp* core* nova* ver*

ifeq ($(words $(MAKECMDGOALS)),3)
'''
    makefile.write(makefile_code)
    makefile.write('\tseed := $(word 3, $(MAKECMDGOALS))\n')
    makefile.write('else\n')
    makefile.write('\tseed := `date "+%Y%m0%H%M%S"`\n')
    makefile.write('endif\n')
    makefile.write('\n')
    makefile.write('\n')
    makefile.write('run : comp sim\n')
    makefile.write('\n')
    makefile.write('comp: create_dir\n')
    makefile.write('\tvcs -sverilog +v2k -ntb_opts uvm-1.2 -debug_access+all +plusarg_save $(VCS_HOME)/etc/uvm/src/uvm_macros.svh \\\n')
    makefile.write('\t-full64 -f filelist.f -l ./log/$(case_name)_log/$(case_name)_comp.log +UVM_TESTNAME=$(case_name) +define+UVM_NO_DEPRECATED \\\n')
    makefile.write('\t+fsdbfile+./wave/$(case_name)_wave/$(case_name).fsdb\n')
    makefile.write('\t@echo "---------- ntb_random_seed = $(seed)" >> ./log/$(case_name)_log/$(case_name)_comp.log\n')
    makefile.write('\n')
    makefile.write('create_dir:\n')
    makefile.write('\tmkdir -p log log/$(case_name)_log wave wave/$(case_name)_wave other\n')
    makefile.write('\n')
    makefile.write('sim:\n')
    makefile.write('\t./simv -l ./log/$(case_name)_log/$(case_name)_simv.log +vcs+loopreport +UVM_TESTNAME=$(case_name) +ntb_random_seed=$(seed) \\\n')
    makefile.write('\t+define+UVM_NO_DEPRECATED \n')
    makefile.write('\t@make mv_other_file\n')
    makefile.write('\t@echo "---------- ntb_random_seed = $(seed)" >> ./log/$(case_name)_log/$(case_name)_simv.log\n')
    makefile.write('\n')
    makefile.write('mv_other_file:\n')
    makefile.write('\t@for file in $(wildcard $(other_file)); do \\\n')
    makefile.write('\t\tif [ -e "$$file" ]; then \\\n')
    makefile.write('\t\t\trsync -a $$file ./other/; \\\n')
    makefile.write('\t\t\trm -rf $$file; \\\n')
    makefile.write('\t\tfi; \\\n')
    makefile.write('\tdone\n')
    makefile.write('\n')
    makefile.write('clean:\n')
    makefile.write('\trm -rf *.log csrc simv* *.h *.key *.vpd DVEfiles* coverage *.vdb verdiLog *.fsdb novas* *fsdb* _vcs* *signal* *tmp* core* ./log/* ./wave/* ./other/*\n')
    makefile.write('\n')
    makefile.write('verdi:\n')
    makefile.write('\tverdi -f filelist.f -ssf ./wave/$(case_name)_wave/*$(case_name).fsdb -sv -nologo &\n')
    makefile.close()

def create_filelist(module_name):
    filelist_code = '''
+incdir+./../../rtl
//Rtl
//Add Your Rtl File Here   





+incdir+./../vip
//Add Your Vip File Here   



//Tb
+incdir+./../top
+incdir+./../if
+incdir+./../test
+incdir+./../seq
+incdir+./../vip
+incdir+./../env
+incdir+./../env/i_agent
+incdir+./../env/o_agent
+incdir+./../env/i_agent/driver
+incdir+./../env/i_agent/monitor
+incdir+./../env/i_agent/ser
+incdir+./../env/ref_model
+incdir+./../env/reg_model
+incdir+./../env/scb
+incdir+./../env/tr
+incdir+./../env/reg_model/ralgen
'''
    filelist = open("filelist.f","w")
    filelist.write(filelist_code)
    if(reg_model == 'apb'):
        filelist.write('+incdir+./../env/reg_model/apb_ral\n')
    elif(reg_model == 'ahb'):
        filelist.write('+incdir+./../env/reg_model/ahb_ral\n')
    filelist.write('\n')
    filelist.write('//If\n')
    filelist.write('./../if/%s_if.sv\n'%(module_name))
    filelist.write('./../if/apb_if.sv\n')
    filelist.write('./../if/ahb_if.sv\n')
    filelist.write('\n')
    filelist.write('\n')
    filelist.write('\n')
    filelist.write('\n')
    filelist.write('//Top\n')
    filelist.write('./../top/%s_top.sv\n'%(module_name))
    filelist.write('\n')
    filelist.write('//Reg_model\n')
    if(reg_model == 'apb'):
        filelist.write('./../env/reg_model/apb_ral/apb_transaction.sv\n')
        filelist.write('./../env/reg_model/apb_ral/apb_sqr.sv\n')
        filelist.write('./../env/reg_model/apb_ral/apb_adapter.sv\n')
        filelist.write('./../env/reg_model/apb_ral/apb_driver.sv\n')
        filelist.write('./../env/reg_model/apb_ral/apb_agent.sv\n')
        filelist.write('./../env/reg_model/ralgen/%s_regmodel.sv\n'%(module_name))
        filelist.write('\n')    
    elif(reg_model == 'ahb'):
        filelist.write('./../env/reg_model/ahb_ral/ahb_transaction.sv\n')
        filelist.write('./../env/reg_model/ahb_ral/ahb_sqr.sv\n')
        filelist.write('./../env/reg_model/ahb_ral/ahb_adapter.sv\n')
        filelist.write('./../env/reg_model/ahb_ral/ahb_driver.sv\n')
        filelist.write('./../env/reg_model/ahb_ral/ahb_agent.sv\n')
        filelist.write('./../env/reg_model/ralgen/%s_regmodel.sv\n'%(module_name))
        filelist.write('\n')   
    filelist.write('//Tr\n')
    filelist.write('./../env/tr/%s_transaction.sv\n'%(module_name))
    filelist.write('\n')
    filelist.write('//Sequencer\n') 
    filelist.write('./../env/i_agent/sqr/%s_sequencer.sv\n'%(module_name))
    filelist.write('\n')   
    filelist.write('//Driver\n')  
    filelist.write('./../env/i_agent/driver/%s_driver.sv\n'%(module_name))
    filelist.write('\n')   
    filelist.write('//Monitor\n') 
    filelist.write('./../env/i_agent/monitor/%s_i_monitor.sv\n'%(module_name))   
    filelist.write('./../env/o_agent/monitor/%s_o_monitor.sv\n'%(module_name)) 
    filelist.write('\n') 
    filelist.write('//Agent\n') 
    filelist.write('./../env/i_agent/%s_i_agent.sv\n'%(module_name))
    filelist.write('./../env/o_agent/%s_o_agent.sv\n'%(module_name))
    filelist.write('\n') 
    filelist.write('//Scoreboard\n')
    filelist.write('./../env/scb/%s_scoreboard.sv\n'%(module_name))
    filelist.write('\n')
    filelist.write('//Ref_model\n')
    filelist.write('./../env/ref_model/%s_ref_model.sv\n'%(module_name))
    filelist.write('\n')
    filelist.write('//Environment\n')
    filelist.write('./../env/%s_env.sv\n'%(module_name))
    filelist.write('//Sequence\n')
    filelist.write('./../seq/%s_base_seq.sv\n'%(module_name))
    filelist.write('./../seq/%s_example_seq.sv\n'%(module_name))
    filelist.write('\n')
    filelist.write('\n')
    filelist.write('\n')
    filelist.write('\n')
    filelist.write('//Test\n')
    filelist.write('./../test/%s_base_test.sv\n'%(module_name))
    filelist.write('./../test/%s_example_test.sv\n'%(module_name))    
    filelist.write('\n')
    filelist.write('\n')
    filelist.write('\n')
    filelist.write('\n')
    filelist.close()

def create_uvm_directory(module_name,reg_model):
    # Create the tb /rtl directory 
    create_dir('tb')
    if not os.path.exists('rtl'):
        create_dir('rtl')

    # Change to the tb directory 
    os.chdir("tb")
    # store tb directory local
    global global_tb_directory
    global_tb_directory = os.getcwd()
    # Create the directory structure
    dir_structure = ["env", "test", "top", "seq", "sim","if","vip"]
    # Iterate through the directory structure and create the directory 
    for directory in dir_structure:
        create_dir(directory)

    #cd xxx/tb/env
    os.chdir("env")
    #Create a list of directories to create
    dir_structure = ["i_agent", "o_agent","ref_model", "reg_model", "scb", "tr"]
    #Loop through the list of directories
    for directory in dir_structure:
        create_dir(directory)
    # cd xxx/tb    
    cd_tb_directory()
    os.chdir("./env/i_agent")
    #Create a list of directories to be created
    dir_structure = ["driver", "monitor","sqr"]
    #Loop through the list of directories
    for directory in dir_structure:
        create_dir(directory)

    # Create a directory called monitor in the out_agent directory
    cd_tb_directory()    
    os.chdir("./env/o_agent")
    create_dir("monitor")

    #Change the directory to the reg_model directory
    cd_tb_directory()
    os.chdir("./env/reg_model")
    #Create a directory called ralgen
    create_dir('ralgen')
    if(reg_model == 'apb'):
        #Create a directory called ahb_ral
        create_dir('apb_ral')
    elif(reg_model == 'ahb'):
        #Create a directory called apb_ral
        create_dir('ahb_ral')

def create_uvm_file(module_name,reg_model):
    cd_tb_directory()
    os.chdir("./top")
    create_top_file(module_name,reg_model)

    cd_tb_directory()
    os.chdir("./if")
    create_if_file(module_name)

    cd_tb_directory()
    os.chdir("./test")
    create_base_test_file(module_name)
    create_example_test_file(module_name)
    
    cd_tb_directory()
    os.chdir("./seq")
    create_base_seq_file(module_name)
    create_example_seq_file(module_name)

    cd_tb_directory()
    os.chdir("./env")
    create_env_file(module_name,reg_model) 

    cd_tb_directory()
    os.chdir("./env/scb")
    create_scb_file(module_name) 

    cd_tb_directory()
    os.chdir("./env/ref_model")
    create_ref_model_file(module_name) 

    cd_tb_directory()
    os.chdir("./env/tr")
    create_tr_file(module_name)

    cd_tb_directory()
    os.chdir("./env/i_agent")
    create_i_agt_file(module_name)

    cd_tb_directory()
    os.chdir("./env/i_agent/driver")
    create_driver_file(module_name)   

    cd_tb_directory()
    os.chdir("./env/i_agent/monitor")
    create_i_mon_file(module_name)  

    cd_tb_directory()
    os.chdir("./env/i_agent/sqr")
    create_sqr_file(module_name) 

    cd_tb_directory()
    os.chdir("./env/o_agent")
    create_o_agent_file(module_name)  

    cd_tb_directory()
    os.chdir("./env/o_agent/monitor")
    create_o_mon_file(module_name)  

    cd_tb_directory()
    os.chdir("./env/reg_model/ralgen")
    create_ralgen_file()

    if(reg_model == 'apb'):
        cd_tb_directory()
        os.chdir("./env/reg_model/apb_ral")
        create_apb_ral_file()
    elif(reg_model == 'ahb'):
        cd_tb_directory()
        os.chdir("./env/reg_model/ahb_ral")
        create_ahb_ral_file()

    cd_tb_directory()
    os.chdir("./sim")
    create_makefile()
    create_filelist(module_name)

def main():
    get_cmd()
    create_uvm_directory(module_name,reg_model)
    create_uvm_file(module_name,reg_model)

    print("\n")
    print("\033[32m -------- [Successful]  the %s_uvm_code is created  --------\033[0m"%(module_name))
    print("\n")

if __name__=="__main__":
    main()
