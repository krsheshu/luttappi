import myhdl

from avalon_buses       import PipelineST
from common_functions   import simple_wire_assign, simple_reg_assign, conditional_wire_assign


class CommandPipeline():

  def __init__( self                     ,
                NB_PIPELINE_STAGES  =   4,
                DATAWIDTH           =  32,
                CHANNEL_WIDTH       =   1,
                INIT_DATA           =   0,
                CMD_FILE            =  ""):

    self.NB_PIPELINE_STAGES         = NB_PIPELINE_STAGES
    self.DATAWIDTH                  = DATAWIDTH
    self.CHANNEL_WIDTH              = CHANNEL_WIDTH
    self.INIT_DATA                  = INIT_DATA

    self.OPERATION_STAGE            = 1
    self.OPCODE                     = 0x00  # NOP by default
    self.OPCODEBITS                 = 8
    self.CMD_FILE                   = CMD_FILE


    self.stage_o                    = [ PipelineST (    self.DATAWIDTH       ,
                                                        self.CHANNEL_WIDTH   ,
                                                        self.INIT_DATA       ) for i in range ( self.NB_PIPELINE_STAGES ) ]

    """ Convert cmfFile to a cmdStringList of Pipeline operators"""
    cmdStringList   =   None
    f               =   open( self.CMD_FILE )
    cmdStringList   =   f.readlines()
    f.close()

    cmdStr = [ s.rstrip ( ) for s in cmdStringList ]

    for i in range ( len ( cmdStr ) ):

      if ( cmdStr [ i ] != "NOP" ):

        if      ( cmdStr [ i ] == "ADD" ):     # A+B
          self.OPCODE             = 0x31

        elif    ( cmdStr [ i ] == "SUB" ):   # A-B
          self.OPCODE             = 0x32

        elif    ( cmdStr [ i ] == "SUBR" ):  # B-A
          self.OPCODE             = 0x33

        elif    ( cmdStr [ i ] == "MULT" ):  # A*B
          self.OPCODE             = 0x34

        elif    ( cmdStr [ i ] == "NOP" ):   # No Operation
          self.OPCODE             = 0x00
        break

  @myhdl.block
  def block_atomic_oper(    self            ,
                            reset           ,
                            clk             ,
                            cmd             ,
                            stage_iA        ,
                            stage_iB        ,
                            stage_o         ):

    @myhdl.always(clk.posedge)
    def atomic_operation_assign_process():

      if    ( cmd == 0x31 ):   # A+B
        stage_o.data.next = stage_iA.data + stage_iB.data

      elif  ( cmd == 0x32 ):   # A-B
        stage_o.data.next = stage_iA.data - stage_iB.data

      elif  ( cmd == 0x33 ):  # B-A
        stage_o.data.next = stage_iB.data - stage_iA.data

      elif  ( cmd == 0x34 ):  # A*B
        stage_o.data.next = stage_iA.data * stage_iB.data

      elif  ( cmd == 0x00 ):   # No Operation
        stage_o.data.next = stage_o.data

      if (stage_iA.valid == 1 and stage_iB.valid == 1):
          stage_o.valid.next = 1
      else:
          stage_o.valid.next = 0

      if (stage_iA.sop == 1 and stage_iB.sop == 1):
          stage_o.sop.next = 1
      else:
          stage_o.sop.next = 0

      if (stage_iA.eop == 1 and stage_iB.eop == 1):
          stage_o.eop.next = 1
      else:
          stage_o.eop.next = 0

    return myhdl.instances()


  @myhdl.block
  def top(      self            ,
                reset           ,
                clk             ,
                pipe_stageA     ,
                pipe_stageB     ,
                stage_o         ):

    stage = [ PipelineST (  self.DATAWIDTH      ,
                            self.CHANNEL_WIDTH  ,
                            self.INIT_DATA      ) for i in range( self.NB_PIPELINE_STAGES ) ]

    # Reset value to incorporate float and myhdl.intbv formats
    reset_val = 0.0 if (isinstance(self.INIT_DATA,float)) else 0

    wire_stage_data_inst    = []
    wire_stage_sop_inst     = []
    wire_stage_eop_inst     = []
    wire_stage_valid_inst   = []
    wire_stage_channel_inst = []

    for i in range(self.NB_PIPELINE_STAGES):
      """ module outputs """
      wire_stage_data_inst.append       ( simple_wire_assign ( self.stage_o[i].data   , stage[i].data     ) )
      wire_stage_sop_inst.append        ( simple_wire_assign ( self.stage_o[i].sop    , stage[i].sop      ) )
      wire_stage_eop_inst.append        ( simple_wire_assign ( self.stage_o[i].eop    , stage[i].eop      ) )
      wire_stage_valid_inst.append      ( simple_wire_assign ( self.stage_o[i].valid  , stage[i].valid    ) )
      wire_stage_channel_inst.append    ( simple_wire_assign ( self.stage_o[i].channel, stage[i].channel  ) )

    """ Call block atomic operation for the specific stage """

    reg_stage_inst   = []

    cmd=myhdl.Signal ( myhdl.intbv ( self.OPCODE ) [ self.OPCODEBITS: ] )

    reg_stage_inst.append ( self.block_atomic_oper( reset                                   ,
                                                    clk                                     ,
                                                    cmd                                     ,
                                                    pipe_stageA[ self.OPERATION_STAGE ]     ,
                                                    pipe_stageB[ self.OPERATION_STAGE ]     ,
                                                    stage [ 0 ]                             ))

    for j in range(1,self.NB_PIPELINE_STAGES):

      reg_stage_inst.append ( simple_reg_assign ( reset, clk, stage[j].data     ,   reset_val, stage[j-1].data      ) )
      reg_stage_inst.append ( simple_reg_assign ( reset, clk, stage[j].sop      ,           0, stage[j-1].sop       ) )
      reg_stage_inst.append ( simple_reg_assign ( reset, clk, stage[j].eop      ,           0, stage[j-1].eop       ) )
      reg_stage_inst.append ( simple_reg_assign ( reset, clk, stage[j].valid    ,           0, stage[j-1].valid     ) )
      reg_stage_inst.append ( simple_reg_assign ( reset, clk, stage[j].channel  ,           0, stage[j-1].channel   ) )

    return myhdl.instances()

