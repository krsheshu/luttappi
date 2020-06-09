import myhdl

from avalon_buses       import PipelineST
from common_functions   import conditional_reg_assign, simple_wire_assign, simple_reg_assign

class Activation():

    def __init__( self                     ,
                  DATAWIDTH           =  32,
                  CHANNEL_WIDTH       =   1,
                  INIT_DATA           =   0):

        self.DATAWIDTH                  = DATAWIDTH
        self.CHANNEL_WIDTH              = CHANNEL_WIDTH
        self.INIT_DATA                  = INIT_DATA

        # Io Signals
        self.pipeST_i                   = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )
        self.pipeST_o                   = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )

        # Internal Signals
        self.classifier                 = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )

        # Reset value to incorporate float and intbv formats
        self.zero                       = 0.0 if ( isinstance ( self.INIT_DATA, float ) ) else 0
        self.one                        = 1.0 if ( isinstance ( self.INIT_DATA, float ) ) else 1

    # Use simple step activation function. if x <= 0, prob=0 else prob=1
    @myhdl.block
    def top(  self        ,
              reset       ,
              clk         ,
              pipeST_i     ,
              pipeST_o    ):


        # Simple Step Activation Function
        @myhdl.always(clk.posedge, reset.posedge)
        def activation_process():
            if reset:  # Synchronous reset_acc
                self.classifier.data.next = self.zero
            elif (pipeST_i.valid == 1):
                # if data > 0, prob= 1 else 0
                self.classifier.data.next = self.one if ( pipeST_i.data > self.zero ) else self.zero
            else:
                self.classifier.data.next = self.classifier.data

        # Outputs
        data        = simple_wire_assign        ( pipeST_o.data , self.classifier.data  )
        sop         = conditional_reg_assign    ( reset         , clk                   , pipeST_o.sop      , 0, pipeST_i.valid      , pipeST_i.sop )
        eop         = conditional_reg_assign    ( reset         , clk                   , pipeST_o.eop      , 0, pipeST_i.valid      , pipeST_i.eop )
        valid       = simple_reg_assign         ( reset         , clk                   , pipeST_o.valid    , 0, pipeST_i.valid      )
        channel     = simple_reg_assign         ( reset         , clk                   , pipeST_o.channel  , 0, pipeST_i.channel    )


        return myhdl.instances()

