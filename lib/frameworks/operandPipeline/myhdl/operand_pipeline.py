import myhdl

from avalon_buses       import PipelineST
from common_functions   import simple_wire_assign, simple_reg_assign, conditional_wire_assign

class OperandPipeline():

    def __init__( self                    ,
                  NB_PIPELINE_STAGES =   4,
                  DATAWIDTH          =  32,
                  CHANNEL_WIDTH      =   1,
                  INIT_DATA          =   0):

        self.NB_PIPELINE_STAGES = NB_PIPELINE_STAGES
        self.DATAWIDTH          = DATAWIDTH
        self.CHANNEL_WIDTH      = CHANNEL_WIDTH
        self.INIT_DATA          = INIT_DATA

        self.stage_o            = [ PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA ) for i in range ( self.NB_PIPELINE_STAGES ) ]
        self.shiftEn_i          = myhdl.Signal( bool ( 1 ) )

    @myhdl.block
    def top(  self        ,
              reset       ,
              clk         ,
              pipest_snk  ,
              stage_o     ):

        # Reset value to incorporate float and intbv formats
        reset_val = 0.0 if ( isinstance ( self.INIT_DATA, float ) ) else 0

        stage = [ PipelineST ( self.DATAWIDTH, self.CHANNEL_WIDTH, self.INIT_DATA ) for i in range( self.NB_PIPELINE_STAGES ) ]

        wire_stage_data_inst        = []
        wire_stage_sop_inst         = []
        wire_stage_eop_inst         = []
        wire_stage_valid_inst       = []
        wire_stage_channel_inst     = []

        for i in range( self.NB_PIPELINE_STAGES ):
          """ module outputs """
          wire_stage_data_inst.append       ( simple_wire_assign ( self.stage_o[i].data   , stage[i].data     )   )
          wire_stage_sop_inst.append        ( simple_wire_assign ( self.stage_o[i].sop    , stage[i].sop      )   )
          wire_stage_eop_inst.append        ( simple_wire_assign ( self.stage_o[i].eop    , stage[i].eop      )   )
          wire_stage_valid_inst.append      ( simple_wire_assign ( self.stage_o[i].valid  , stage[i].valid    )   )
          wire_stage_channel_inst.append    ( simple_wire_assign ( self.stage_o[i].channel, stage[i].channel  )   )

        """ Stage instance, has extra ready and valid lines """

        data    = ( conditional_wire_assign ( stage[0].data     , self.shiftEn_i, pipest_snk.data     ,   reset_val)  )
        sop     = ( conditional_wire_assign ( stage[0].sop      , self.shiftEn_i, pipest_snk.sop      ,           0)  )
        eop     = ( conditional_wire_assign ( stage[0].eop      , self.shiftEn_i, pipest_snk.eop      ,           0)  )
        valid   = ( conditional_wire_assign ( stage[0].valid    , self.shiftEn_i, pipest_snk.valid    ,           0)  )
        channel = ( conditional_wire_assign ( stage[0].channel  , self.shiftEn_i, pipest_snk.channel  ,           0)  )

        reg_stage_data_inst     = []
        reg_stage_sop_inst      = []
        reg_stage_eop_inst      = []
        reg_stage_valid_inst    = []
        reg_stage_channel_inst  = []

        for i in range ( 1, self.NB_PIPELINE_STAGES ):

          reg_stage_data_inst.append    ( simple_reg_assign ( reset, clk, stage[i].data     ,   reset_val,  stage[i-1].data     ) )
          reg_stage_sop_inst.append     ( simple_reg_assign ( reset, clk, stage[i].sop      ,           0,  stage[i-1].sop      ) )
          reg_stage_eop_inst.append     ( simple_reg_assign ( reset, clk, stage[i].eop      ,           0,  stage[i-1].eop      ) )
          reg_stage_valid_inst.append   ( simple_reg_assign ( reset, clk, stage[i].valid    ,           0,  stage[i-1].valid    ) )
          reg_stage_channel_inst.append ( simple_reg_assign ( reset, clk, stage[i].channel  ,           0,  stage[i-1].channel  ) )

        return myhdl.instances()






