import myhdl

from avalon_buses       import PipelineST
from common_functions   import simple_wire_assign, simple_reg_assign, conditional_wire_assign
import os

class OpCode():

    def __init__ ( self  ):
        self.ADD    = 0x31
        self.SUB    = 0x32
        self.SUBR   = 0x33
        self.MULT   = 0x34
        self.NOP    = 0x00

        self.opcode = self.NOP

    def get ( self, opcode_str ):

        if      ( opcode_str == "ADD" ):       # A+B
            self.opcode             = 0x31

        elif    ( opcode_str == "SUB" ):       # A-B
            self.opcode             = 0x32

        elif    ( opcode_str == "SUBR" ):      # B-A
            self.opcode             = 0x33

        elif    ( opcode_str == "MULT" ):      # A*B
            self.opcode             = 0x34

        elif    ( opcode_str == "NOP" ):       # No Operation
            self.opcode             = 0x00

        else:
            print(" Opcode Not Valid! ")
            os.exit()

        return (self.opcode)



class CommandPipeline():

    def __init__( self                         ,
                  NB_PIPELINE_STAGES  =       4,
                  DATAWIDTH           =      32,
                  CHANNEL_WIDTH       =       1,
                  INIT_DATA           =       0,
                  OPCODE              =   "NOP",
                  OPSTAGE             =       0):

        self.NB_PIPELINE_STAGES         = NB_PIPELINE_STAGES
        self.DATAWIDTH                  = DATAWIDTH
        self.CHANNEL_WIDTH              = CHANNEL_WIDTH
        self.INIT_DATA                  = INIT_DATA

        self.OPSTAGE                    = OPSTAGE
        self.OPCODE                     =  OPCODE     # NOP by default
        self.OPCODEBITS                 =       8

        # Io Signals
        self.pipeST_A_stage_i           = [ PipelineST (    self.DATAWIDTH       ,
                                                            self.CHANNEL_WIDTH   ,
                                                            self.INIT_DATA       ) for i in range ( self.NB_PIPELINE_STAGES ) ]

        self.pipeST_B_stage_i           = [ PipelineST (    self.DATAWIDTH       ,
                                                            self.CHANNEL_WIDTH   ,
                                                            self.INIT_DATA       ) for i in range ( self.NB_PIPELINE_STAGES ) ]

        self.pipeST_stage_o             = [ PipelineST (    self.DATAWIDTH       ,
                                                            self.CHANNEL_WIDTH   ,
                                                            self.INIT_DATA       ) for i in range ( self.NB_PIPELINE_STAGES ) ]

        # Internal Signals
        self.objOpcode                  = OpCode ()
        self.OPCODE_HEX                 = self.objOpcode.get ( self.OPCODE )
        self.reset_val                  = 0.0 if (isinstance(self.INIT_DATA,float)) else 0


    @myhdl.block
    def block_atomic_oper(    self                    ,
                              reset                   ,
                              clk                     ,
                              pipeST_A_i              ,
                              pipeST_B_i              ,
                              pipeST_o                ):

        @myhdl.always(clk.posedge)
        def atomic_operation():


            if    ( self.OPCODE_HEX == self.objOpcode.ADD     ):  # A+B

                  pipeST_o.data.next = pipeST_A_i.data + pipeST_B_i.data

            elif  ( self.OPCODE_HEX == self.objOpcode.SUB     ):  # A-B

                  pipeST_o.data.next = pipeST_A_i.data - pipeST_B_i.data

            elif  ( self.OPCODE_HEX == self.objOpcode.SUBR    ):  # B-A

                  pipeST_o.data.next = pipeST_B_i.data - pipeST_A_i.data

            elif  ( self.OPCODE_HEX == self.objOpcode.MULT    ):  # A*B

                  pipeST_o.data.next = pipeST_A_i.data * pipeST_B_i.data

            elif  ( self.OPCODE_HEX == self.objOpcode.NOP     ):  # No Operation

                  pipeST_o.data.next = pipeST_o.data

            if (pipeST_A_i.valid == 1 and pipeST_B_i.valid == 1):
                pipeST_o.valid.next = 1
            else:
                pipeST_o.valid.next = 0

            if (pipeST_A_i.sop == 1 and pipeST_B_i.sop == 1):
                pipeST_o.sop.next = 1
            else:
                pipeST_o.sop.next = 0

            if (pipeST_A_i.eop == 1 and pipeST_B_i.eop == 1):
                pipeST_o.eop.next = 1
            else:
                pipeST_o.eop.next = 0

        return myhdl.instances()


    @myhdl.block
    def top(      self                    ,
                  reset                   ,
                  clk                     ,
                  pipeST_A_stage_i        ,
                  pipeST_B_stage_i        ,
                  pipeST_stage_o         ):

        # Operation happenning at the required stage inputs
        reg_stage_inst  = []

        reg_stage_inst.append ( self.block_atomic_oper( reset                                   ,
                                                        clk                                     ,
                                                        pipeST_A_stage_i[ self.OPSTAGE ]        ,
                                                        pipeST_B_stage_i[ self.OPSTAGE ]        ,
                                                        pipeST_stage_o[ 0 ]                     ))

        for j in range(1,self.NB_PIPELINE_STAGES):

            reg_stage_inst.append ( simple_reg_assign ( reset, clk, pipeST_stage_o[j].data     ,  self.reset_val, pipeST_stage_o[j-1].data      ) )
            reg_stage_inst.append ( simple_reg_assign ( reset, clk, pipeST_stage_o[j].sop      ,               0, pipeST_stage_o[j-1].sop       ) )
            reg_stage_inst.append ( simple_reg_assign ( reset, clk, pipeST_stage_o[j].eop      ,               0, pipeST_stage_o[j-1].eop       ) )
            reg_stage_inst.append ( simple_reg_assign ( reset, clk, pipeST_stage_o[j].valid    ,               0, pipeST_stage_o[j-1].valid     ) )
            reg_stage_inst.append ( simple_reg_assign ( reset, clk, pipeST_stage_o[j].channel  ,               0, pipeST_stage_o[j-1].channel   ) )

        return myhdl.instances()
