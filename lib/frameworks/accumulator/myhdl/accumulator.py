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

        # Io Signals
        self.reset_acc                  = myhdl.Signal ( bool ( 0 ) )
        self.pipeST_i                   = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )
        self.pipeST_o                   = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )

        # Internal Signals
        self.accu                       = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA )

        # Reset value to incorporate float and myhdl.intbv formats
        self.zero = 0.0 if ( isinstance ( self.INIT_DATA,float ) ) else 0


    @myhdl.block
    def top(  self            ,
              reset           ,
              clk             ,
              reset_acc       ,
              pipeST_i         ,
              pipeST_o        ):


        acc_cnt     = myhdl.Signal ( myhdl.intbv ( 0 ) [ CLogB2 ( self.NB_ACCUMULATIONS ): ] )
        acc_valid   = myhdl.Signal ( bool ( 0 ) )

        # Counter to count nb accumulations
        @myhdl.always ( clk.posedge, reset.posedge )
        def acc_cnt_process():
            if reset:
                acc_cnt.next = 0
            elif reset_acc:
                acc_cnt.next = 0
            elif (pipeST_i.valid == 1):
                if(acc_cnt == (self.NB_ACCUMULATIONS-1)):
                    acc_cnt.next = 0
                else:
                    acc_cnt.next = acc_cnt + 1
            else:
                acc_cnt.next = acc_cnt

        # Accumulate data when valid data present till valid nb counts
        @myhdl.always( clk.posedge, reset.posedge )
        def accumulator_process():
            if reset:
                self.accu.data.next = self.zero
            elif reset_acc:
                self.accu.data.next = self.zero
            elif (pipeST_i.valid == 1):
                if (acc_cnt == 0):  # If valid, accumulate data
                    self.accu.data.next = pipeST_i.data
                else:
                    self.accu.data.next = self.accu.data + pipeST_i.data
            else:
                self.accu.data.next = self.accu.data

        # Accumulate Valid myhdl.Signal
        @myhdl.always ( clk.posedge, reset.posedge )
        def acc_valid_process():
            if reset:
                acc_valid.next = 0
            elif reset_acc:
                acc_valid.next = 0
            elif (pipeST_i.valid == 1 and acc_cnt == self.NB_ACCUMULATIONS-1):
                acc_valid.next = 1
            else:
                acc_valid.next = 0

        # Outputs
        valid_out_inst      = simple_wire_assign        ( pipeST_o.valid,   acc_valid       )
        data_out_inst       = simple_wire_assign        ( pipeST_o.data ,   self.accu.data  )
        sop_out_inst        = conditional_reg_assign    ( reset         ,   clk             , pipeST_o.sop      , 0, pipeST_i.valid, pipeST_i.sop     )
        eop_out_inst        = conditional_reg_assign    ( reset         ,   clk             , pipeST_o.eop      , 0, pipeST_i.valid, pipeST_i.eop     )
        channel_out_inst    = conditional_reg_assign    ( reset         ,   clk             , pipeST_o.channel  , 0, pipeST_i.valid, pipeST_i.channel )


        return myhdl.instances()









