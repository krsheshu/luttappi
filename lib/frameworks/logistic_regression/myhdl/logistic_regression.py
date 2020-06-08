import myhdl

from avalon_buses       import PipelineST

from operand_pipeline   import OperandPipeline
from command_pipeline   import CommandPipeline
from accumulator        import Accumulator
from activation         import Activation

class LogisticRegressionIo():
  def __init__( self                    ,
                DATAWIDTH          =  32,
                CHANNEL_WIDTH      =   1,
                INIT_DATA          =   0):

    self.pipe_inpA      = PipelineST    ( DATAWIDTH, CHANNEL_WIDTH , INIT_DATA )
    self.pipe_inpB      = PipelineST    ( DATAWIDTH, CHANNEL_WIDTH , INIT_DATA )
    self.pipe_out_activ = PipelineST    ( DATAWIDTH, CHANNEL_WIDTH , INIT_DATA )


class LogisticRegression():

  def __init__( self                    ,
                NB_PIPELINE_STAGES =   4,
                DATAWIDTH          =  32,
                CHANNEL_WIDTH      =   1,
                INIT_DATA          =   0,
                LEN_THETA          =   3,
                CMD_FILE           =  ""):

    self.NB_PIPELINE_STAGES = NB_PIPELINE_STAGES
    self.DATAWIDTH          = DATAWIDTH
    self.CHANNEL_WIDTH      = CHANNEL_WIDTH
    self.INIT_DATA          = INIT_DATA
    self.LEN_THETA          = LEN_THETA
    self.CMD_FILE           = CMD_FILE

    self.Io                 = LogisticRegressionIo ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA)

    # Internal Signals
    self.pipe_multRes       = PipelineST(   self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )
    self.pipe_out_acc       = PipelineST(   self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )

  @myhdl.block
  def top(  self            ,
            reset           ,
            clk             ,
            pipe_inpA       ,
            pipe_inpB       ,
            pipe_out_activ  ):

    #------ Wrapping the interfaces due to conversion issues!
    pipe_inpA_if        = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )
    pipe_inpB_if        = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )
    pipe_out_active_if  = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )

    @myhdl.always_comb
    def interface_wrap_process():
      pipe_inpA_if.valid.next = pipe_inpA.valid
      pipe_inpA_if.data.next  = pipe_inpA.data
      pipe_inpA_if.sop.next   = pipe_inpA.sop
      pipe_inpA_if.eop.next   = pipe_inpA.eop
      pipe_inpA_if.channel.next = pipe_inpA.channel

      pipe_inpB_if.valid.next = pipe_inpB.valid
      pipe_inpB_if.data.next  = pipe_inpB.data
      pipe_inpB_if.sop.next   = pipe_inpB.sop
      pipe_inpB_if.eop.next   = pipe_inpB.eop
      pipe_inpB_if.channel.next = pipe_inpB.channel

      pipe_out_activ.valid.next = pipe_out_active_if.valid
      pipe_out_activ.data.next  = pipe_out_active_if.data
      pipe_out_activ.sop.next   = pipe_out_active_if.sop
      pipe_out_activ.eop.next   = pipe_out_active_if.eop
      pipe_out_activ.channel.next = pipe_out_active_if.channel


    #----------------- Initializing Pipeline Streams ----------------

    operand_a=OperandPipeline( self.NB_PIPELINE_STAGES, self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )
    pipeA_stage=operand_a.stage_o

    operand_b=OperandPipeline( self.NB_PIPELINE_STAGES, self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )
    pipeB_stage=operand_b.stage_o

    # --- Initializing Command Pipeline
    multPipe=CommandPipeline( self.NB_PIPELINE_STAGES, self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA, self.CMD_FILE )
    multC_stage=multPipe.stage_o

    # ---- Initializing Accumulator Block

    accuPipe= Accumulator( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA, self.LEN_THETA )

    # ---- Initializing Activation Block

    ACT_DATAWIDTH= 3    # 0 or 1 for classification
    activPipe       =   Activation(  ACT_DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )
    #----------------------------------------------------------------

    trainingData    =   ( operand_a.top ( reset, clk, pipe_inpA_if, pipeA_stage ) )
    theta           =   ( operand_b.top ( reset, clk, pipe_inpB_if, pipeB_stage ) )
    #----------------------------------------------------------------

    #----------------- Connecting Command Pipeline -------------------
    # Mult Pipeline
    command     =   ( multPipe.top ( reset, clk, pipeA_stage, pipeB_stage, multC_stage ) )
    #----------------------------------------------------------------

    #----------------- Connecting Accumulator  --------------
    # Accu
    acc_reset   =   myhdl.Signal(bool(0))
    accumulator =   ( accuPipe.top ( reset, clk, acc_reset, multC_stage [ 0 ] , self.pipe_out_acc ) )

    #----------------------------------------------------------------

    #----------------- Connecting Activation  --------------
    # Simple Step Activation function
    activation  =   ( activPipe.top ( reset, clk, self.pipe_out_acc, pipe_out_active_if ) )

    #----------------------------------------------------------------

    return myhdl.instances()
