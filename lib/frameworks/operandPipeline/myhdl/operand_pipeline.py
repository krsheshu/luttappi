#----operandPipeline Class 

#----imports
from myhdl import always, always_comb, Signal, instances, block
from avalon_buses import PipelineST
from common_functions import simple_wire_assign, simple_reg_assign, conditional_wire_assign

#---- Class description
class OperandPipelineIo(): 
  def __init__(self):
    """ Initialize OperandPipeline Ios """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH = 32
    self.CHANNEL_WIDTH= 1
    self.INIT_DATA=0

    self.shiftEn_i  = Signal(bool(0))
    self.stage_o    = [PipelineST(self.DATAWIDTH,self.CHANNEL_WIDTH,self.INIT_DATA) for i in range(self.NB_PIPELINE_STAGES)]
 
  def __call__(self,pars):
    """ Overwrite OperandPipeline Ios """
    self.shiftEn_i  = Signal(bool(0))
    self.stage_o    = [PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) for i in range(pars.NB_PIPELINE_STAGES)]

#----Parameters for operandPipeline Class
class OperandPipelinePars(): 
  def __init__(self):
    """ Initialize OperandPipeline parameters """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH          = 32 
    self.CHANNEL_WIDTH      = 1
    self.INIT_DATA          = 0
  
  def __call__(self,pars):
    """ Overwrite OperandPipeline parameters """
    self.NB_PIPELINE_STAGES = pars.NB_PIPELINE_STAGES
    self.DATAWIDTH          = pars.DATAWIDTH
    self.CHANNEL_WIDTH      = pars.CHANNEL_WIDTH
    self.INIT_DATA          = pars.INIT_DATA



#-----Class Description
class OperandPipeline():
  
  def __init__(self):
    """ OperandPipeline Init"""

  #@block 
  def block_connect(self, pars, reset, clk, pipest_snk, pipest_src, io):
    """ OperandPipeline block """

    # Reset value to incorporate float and intbv formats
    reset_val = 0.0 if (isinstance(pars.INIT_DATA,float)) else 0
 
    stage = [PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) for i in range(pars.NB_PIPELINE_STAGES)]

    """ Output pipesrc instance """
    data_out_inst   = simple_wire_assign(pipest_src.data, io.stage_o[pars.NB_PIPELINE_STAGES-1].data)
    sop_out_inst    = simple_wire_assign(pipest_src.sop, io.stage_o[pars.NB_PIPELINE_STAGES-1].sop)
    eop_out_inst    = simple_wire_assign(pipest_src.eop, io.stage_o[pars.NB_PIPELINE_STAGES-1].eop)
    valid_out_inst  = simple_wire_assign(pipest_src.valid, io.stage_o[pars.NB_PIPELINE_STAGES-1].valid)

 
    wire_stage_data_inst   = []
    wire_stage_sop_inst    = []
    wire_stage_eop_inst    = []
    wire_stage_valid_inst  = []
    
    for i in range(pars.NB_PIPELINE_STAGES):
      """ module outputs """
      wire_stage_data_inst.append(simple_wire_assign(io.stage_o[i].data, stage[i].data))
      wire_stage_sop_inst.append(simple_wire_assign(io.stage_o[i].sop, stage[i].sop) )
      wire_stage_eop_inst.append(simple_wire_assign(io.stage_o[i].eop, stage[i].eop) )
      wire_stage_valid_inst.append(simple_wire_assign(io.stage_o[i].valid, stage[i].valid)) 

    """ Stage instance, has extra ready and valid lines """ 
    
    reg_stage_data_inst   = []
    reg_stage_sop_inst    = []
    reg_stage_eop_inst    = []
    reg_stage_valid_inst  = []
    
    reg_stage_data_inst.append(conditional_wire_assign(stage[0].data, io.shiftEn_i, pipest_snk.data, reset_val)) 
    reg_stage_sop_inst.append(conditional_wire_assign(stage[0].sop, io.shiftEn_i, pipest_snk.sop, reset_val)) 
    reg_stage_eop_inst.append(conditional_wire_assign(stage[0].eop, io.shiftEn_i, pipest_snk.eop, reset_val)) 
    reg_stage_valid_inst.append(conditional_wire_assign(stage[0].valid, io.shiftEn_i, pipest_snk.valid, reset_val)) 
    
    for i in range(1,pars.NB_PIPELINE_STAGES):
      reg_stage_data_inst.append(simple_reg_assign(reset, clk, stage[i].data, reset_val, stage[i-1].data) )    
      reg_stage_sop_inst.append(simple_reg_assign(reset, clk, stage[i].sop, reset_val, stage[i-1].sop) )   
      reg_stage_eop_inst.append(simple_reg_assign(reset, clk, stage[i].eop, reset_val, stage[i-1].eop) )   
      reg_stage_valid_inst.append(simple_reg_assign(reset, clk, stage[i].valid, reset_val, stage[i-1].valid) )

    return instances() 
  
  def validate(self, ipFile, opFile):
    """ Validation block """
    pass
