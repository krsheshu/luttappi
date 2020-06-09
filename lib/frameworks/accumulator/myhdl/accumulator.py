import myhdl
from avalon_buses       import PipelineST
from common_functions   import conditional_reg_assign, CLogB2, simple_wire_assign, simple_reg_assign

class Accumulator():

  def __init__( self                     ,
                DATAWIDTH           =  32,
                CHANNEL_WIDTH       =   1,
                INIT_DATA           =   0,
                NB_ACCUMULATIONS    =   3):

    self.DATAWIDTH                  = DATAWIDTH
    self.CHANNEL_WIDTH              = CHANNEL_WIDTH
    self.INIT_DATA                  = INIT_DATA
    self.NB_ACCUMULATIONS           = NB_ACCUMULATIONS

    self.accu                       = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )

  @myhdl.block
  def top(  self            ,
            reset           ,
            clk             ,
            reset_acc       ,
            pipe_in         ,
            pipe_out        ):

    # Reset value to incorporate float and myhdl.intbv formats
    zero = 0.0 if ( isinstance ( self.INIT_DATA,float ) ) else 0

    acc_cnt     = myhdl.Signal ( myhdl.intbv ( 0 ) [ CLogB2 ( self.NB_ACCUMULATIONS ): ] )
    acc_valid   = myhdl.Signal ( bool ( 0 ) )

    # Counter to count nb accumulations
    @myhdl.always ( clk.posedge, reset.posedge )
    def acc_cnt_process():
      if reset:  # Synchronous reset_acc
        acc_cnt.next = 0
      elif reset_acc:
        acc_cnt.next = 0
      elif (pipe_in.valid == 1):
        if(acc_cnt == (self.NB_ACCUMULATIONS-1)):
          acc_cnt.next = 0
        else:
          acc_cnt.next = acc_cnt + 1
      else:
        acc_cnt.next = acc_cnt

    # Accumulate data when valid data present till valid nb counts
    @myhdl.always( clk.posedge, reset.posedge )
    def accumulator_process():
      if reset:  # Synchronous reset_acc
        self.accu.data.next = zero
      elif reset_acc:
        self.accu.data.next = zero
      elif (pipe_in.valid == 1):
        if (acc_cnt == 0):  # If valid, accumulate data
          self.accu.data.next = pipe_in.data
        else:
          self.accu.data.next = self.accu.data + pipe_in.data
      else:
          self.accu.data.next = self.accu.data

    # Accumulate Valid myhdl.Signal
    @myhdl.always ( clk.posedge, reset.posedge )
    def acc_valid_process():
      if reset:
        acc_valid.next = 0
      elif reset_acc:
        acc_valid.next = 0
      elif (pipe_in.valid == 1 and acc_cnt == self.NB_ACCUMULATIONS-1):
          acc_valid.next = 1
      else:
          acc_valid.next = 0

    # Outputs
    data_out_inst       = simple_wire_assign        ( pipe_out.data ,   self.accu.data  )
    sop_out_inst        = conditional_reg_assign    ( reset         ,   clk             , pipe_out.sop      , 0, pipe_in.valid, pipe_in.sop     )
    eop_out_inst        = conditional_reg_assign    ( reset         ,   clk             , pipe_out.eop      , 0, pipe_in.valid, pipe_in.eop     )
    valid_out_inst      = simple_wire_assign        ( pipe_out.valid,   acc_valid       )
    channel_out_inst    = conditional_reg_assign    ( reset         ,   clk             , pipe_out.channel  , 0, pipe_in.valid, pipe_in.channel )


    return myhdl.instances()

