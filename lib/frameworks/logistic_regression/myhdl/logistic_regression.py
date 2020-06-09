import myhdl

from avalon_buses       import PipelineST

from operand_pipeline   import OperandPipeline
from command_pipeline   import CommandPipeline
from accumulator        import Accumulator
from activation         import Activation


class LogisticRegression():

  def __init__( self                     ,
                NB_PIPELINE_STAGES  =   4,
                DATAWIDTH           =  32,
                CHANNEL_WIDTH       =   1,
                INIT_DATA           =   0,
                LEN_THETA           =   3,
                CMD_FILE            =  ""):

    self.NB_PIPELINE_STAGES         = NB_PIPELINE_STAGES
    self.DATAWIDTH                  = DATAWIDTH
    self.CHANNEL_WIDTH              = CHANNEL_WIDTH
    self.INIT_DATA                  = INIT_DATA
    self.LEN_THETA                  = LEN_THETA
    self.CMD_FILE                   = CMD_FILE

    # IO Signals
    self.pipeST_A_i                 = PipelineST( self.DATAWIDTH, self.CHANNEL_WIDTH , self.INIT_DATA )
    self.pipeST_B_i                 = PipelineST( self.DATAWIDTH, self.CHANNEL_WIDTH , self.INIT_DATA )
    self.pipeST_o                   = PipelineST( self.DATAWIDTH, self.CHANNEL_WIDTH , self.INIT_DATA )


    # Internal Signals
    self.pipe_out_acc               = PipelineST( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )

    #----------------- Initializing Pipeline Streams ----------------

    self.operand_a   =   OperandPipeline(   self.NB_PIPELINE_STAGES ,
                                            self.DATAWIDTH          ,
                                            self.CHANNEL_WIDTH      ,
                                            self.INIT_DATA          )

    self.pipeA_stage =   self.operand_a.pipeST_stage_o

    self.operand_b   =   OperandPipeline(   self.NB_PIPELINE_STAGES ,
                                            self.DATAWIDTH          ,
                                            self.CHANNEL_WIDTH      ,
                                            self.INIT_DATA          )

    self.pipeB_stage =   self.operand_b.pipeST_stage_o

    # --- Initializing Command Pipeline
    self.multPipe    =   CommandPipeline(   self.NB_PIPELINE_STAGES ,
                                            self.DATAWIDTH          ,
                                            self.CHANNEL_WIDTH      ,
                                            self.INIT_DATA          ,
                                            self.CMD_FILE           )

    self.multC_stage =   self.multPipe.stage_o

    # ---- Initializing Accumulator Block

    self.accuPipe    =   Accumulator(       self.DATAWIDTH          ,
                                            self.CHANNEL_WIDTH      ,
                                            self.INIT_DATA          ,
                                            self.LEN_THETA          )

    # ---- Initializing Activation Block

    ACT_DATAWIDTH= 3    # 0 or 1 for classification
    self.activPipe   =   Activation(        ACT_DATAWIDTH           ,
                                            self.CHANNEL_WIDTH      ,
                                            self.INIT_DATA          )

  @myhdl.block
  def top(  self            ,
            reset           ,
            clk             ,
            pipeST_A_i      ,
            pipeST_B_i      ,
            pipeST_o        ):

    #----------------------------------------------------------------

    inferenceData   =   ( self.operand_a.top ( reset, clk, pipeST_A_i, self.pipeA_stage ) )

    theta           =   ( self.operand_b.top ( reset, clk, pipeST_B_i, self.pipeB_stage ) )

    #----------------------------------------------------------------

    #----------------- Connecting Command Pipeline -------------------
    # Mult Pipeline
    command     =   ( self.multPipe.top ( reset, clk, self.pipeA_stage, self.pipeB_stage, self.multC_stage ) )

    #----------------------------------------------------------------

    #----------------- Connecting Accumulator  --------------
    # Accu
    acc_reset   =   myhdl.Signal(bool(0))

    accumulator =   ( self.accuPipe.top ( reset, clk, acc_reset, self.multC_stage [ 0 ] , self.pipe_out_acc ) )

    #----------------------------------------------------------------

    #----------------- Connecting Activation  --------------
    # Simple Step Activation function

    activation  =   ( self.activPipe.top ( reset, clk, self.pipe_out_acc, pipeST_o ) )

    #----------------------------------------------------------------

    return myhdl.instances()
