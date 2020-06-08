import myhdl

from avalon_buses       import PipelineST
from common_functions   import conditional_reg_assign, simple_wire_assign, simple_reg_assign

class Activation():

  def __init__( self                    ,
                DATAWIDTH          =  32,
                CHANNEL_WIDTH      =   1,
                INIT_DATA          =   0):

    self.DATAWIDTH          = DATAWIDTH
    self.CHANNEL_WIDTH      = CHANNEL_WIDTH
    self.INIT_DATA          = INIT_DATA

    self.classifier = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )


  # Use simple step activation function. if x <= 0, prob=0 else prob=1
  @myhdl.block
  def top(  self        ,
            reset       ,
            clk         ,
            pipe_in     ,
            pipe_out    ):

    # Reset value to incorporate float and intbv formats
    zero    = 0.0 if ( isinstance ( self.INIT_DATA, float ) ) else 0

    one     = 1.0 if ( isinstance ( self.INIT_DATA, float ) ) else 1

    # Simple Step Activation Function
    @myhdl.always(clk.posedge, reset.posedge)
    def activation_process():
      if reset:  # Synchronous reset_acc
        self.classifier.data.next = zero
      elif (pipe_in.valid == 1):
        # if data > 0, prob= 1 else 0
        self.classifier.data.next = one if (pipe_in.data > zero) else zero
      else:
        self.classifier.data.next = self.classifier.data

    # Outputs
    data        = simple_wire_assign        ( pipe_out.data , self.classifier.data  )
    sop         = conditional_reg_assign    ( reset         , clk                   , pipe_out.sop      , 0, pipe_in.valid      , pipe_in.sop )
    eop         = conditional_reg_assign    ( reset         , clk                   , pipe_out.eop      , 0, pipe_in.valid      , pipe_in.eop )
    valid       = simple_reg_assign         ( reset         , clk                   , pipe_out.valid    , 0, pipe_in.valid      )
    channel     = simple_reg_assign         ( reset         , clk                   , pipe_out.channel  , 0, pipe_in.channel    )


    return myhdl.instances()

