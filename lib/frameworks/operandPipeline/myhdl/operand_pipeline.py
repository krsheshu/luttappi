import myhdl

from avalon_buses       import PipelineST
from common_functions   import simple_wire_assign, simple_reg_assign, conditional_wire_assign

class OperandPipeline():

    def __init__( self                       ,
                  NB_PIPELINE_STAGES    =   4,
                  DATAWIDTH             =  32,
                  CHANNEL_WIDTH         =   1,
                  INIT_DATA             =   0):

        self.NB_PIPELINE_STAGES         = NB_PIPELINE_STAGES
        self.DATAWIDTH                  = DATAWIDTH
        self.CHANNEL_WIDTH              = CHANNEL_WIDTH
        self.INIT_DATA                  = INIT_DATA

        # IO Signals
        self.pipeST_i                   = PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH , self.INIT_DATA )

        self.pipeST_stage_o             = [ PipelineST (    self.DATAWIDTH      ,
                                                            self.CHANNEL_WIDTH  ,
                                                            self.INIT_DATA      ) for i in range ( self.NB_PIPELINE_STAGES ) ]


        # Internal signals
        self.reset_val                  = 0.0 if ( isinstance ( self.INIT_DATA, float ) ) else 0

    @myhdl.block
    def top(  self                  ,
              reset                 ,
              clk                   ,
              pipeST_i              ,
              pipeST_stage_o        ):

        # Reset value to incorporate float and intbv formats

        shiftEn     = myhdl.Signal( bool ( 1 ) )

        # initialiting stage 0 outputs
        data    = ( conditional_wire_assign ( pipeST_stage_o[0].data     , shiftEn, pipeST_i.data     , self.reset_val)  )
        sop     = ( conditional_wire_assign ( pipeST_stage_o[0].sop      , shiftEn, pipeST_i.sop      ,              0)  )
        eop     = ( conditional_wire_assign ( pipeST_stage_o[0].eop      , shiftEn, pipeST_i.eop      ,              0)  )
        valid   = ( conditional_wire_assign ( pipeST_stage_o[0].valid    , shiftEn, pipeST_i.valid    ,              0)  )
        channel = ( conditional_wire_assign ( pipeST_stage_o[0].channel  , shiftEn, pipeST_i.channel  ,              0)  )

        reg_stage_data_inst     = []
        reg_stage_sop_inst      = []
        reg_stage_eop_inst      = []
        reg_stage_valid_inst    = []
        reg_stage_channel_inst  = []

        # All other stage outputs
        for i in range ( 1, self.NB_PIPELINE_STAGES ):

          reg_stage_data_inst.append    ( simple_reg_assign ( reset, clk, pipeST_stage_o[i].data     ,     self.reset_val,  pipeST_stage_o[i-1].data     ) )
          reg_stage_sop_inst.append     ( simple_reg_assign ( reset, clk, pipeST_stage_o[i].sop      ,                  0,  pipeST_stage_o[i-1].sop      ) )
          reg_stage_eop_inst.append     ( simple_reg_assign ( reset, clk, pipeST_stage_o[i].eop      ,                  0,  pipeST_stage_o[i-1].eop      ) )
          reg_stage_valid_inst.append   ( simple_reg_assign ( reset, clk, pipeST_stage_o[i].valid    ,                  0,  pipeST_stage_o[i-1].valid    ) )
          reg_stage_channel_inst.append ( simple_reg_assign ( reset, clk, pipeST_stage_o[i].channel  ,                  0,  pipeST_stage_o[i-1].channel  ) )

        return myhdl.instances()






