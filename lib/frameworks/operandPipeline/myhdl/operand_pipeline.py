from myhdl import always, always_comb, Signal, instances
from avalon_buses import PipelineST
from common_functions import simple_wire_assign, simple_reg_assign, conditional_wire_assign

class Pars(): 
  def __init__(self):
    """ Initialize OperandPipeline parameters """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH          = 32 
  
  def __call__(self,pars):
    """ Overwrite OperandPipeline parameters """
    self.NB_PIPELINE_STAGES = pars.NB_PIPELINE_STAGES
    self.DATAWIDTH          = pars.DATAWIDTH


class OperandPipeline():
  
  def __init__(self):
    """ OperandPipeline Init"""
    self.pars=Pars()
 
  def block_connect(self, reset, clk, pipest_snk, pipest_src, shiftEn_i, stage_o):
    """ OperandPipeline block """
   
    stage = [PipelineST(self.pars.DATAWIDTH) for i in range(self.pars.NB_PIPELINE_STAGES)]
   

    """ Output pipesrc instance """
    data_out_inst   = simple_wire_assign(pipest_src.data, stage_o[self.pars.NB_PIPELINE_STAGES-1].data)
    sop_out_inst    = simple_wire_assign(pipest_src.sop, stage_o[self.pars.NB_PIPELINE_STAGES-1].sop)
    eop_out_inst    = simple_wire_assign(pipest_src.eop, stage_o[self.pars.NB_PIPELINE_STAGES-1].eop)
    valid_out_inst  = simple_wire_assign(pipest_src.valid, stage_o[self.pars.NB_PIPELINE_STAGES-1].valid)

 
    wire_stage_data_inst   = [None for i in range(self.pars.NB_PIPELINE_STAGES)]
    wire_stage_sop_inst    = [None for i in range(self.pars.NB_PIPELINE_STAGES)]
    wire_stage_eop_inst    = [None for i in range(self.pars.NB_PIPELINE_STAGES)]
    wire_stage_valid_inst  = [None for i in range(self.pars.NB_PIPELINE_STAGES)]
    
    for i in range(self.pars.NB_PIPELINE_STAGES):
      """ module outputs """
      wire_stage_data_inst[i]  = simple_wire_assign(stage_o[i].data, stage[i].data)
      wire_stage_sop_inst[i]   = simple_wire_assign(stage_o[i].sop, stage[i].sop) 
      wire_stage_eop_inst[i]   = simple_wire_assign(stage_o[i].eop, stage[i].eop) 
      wire_stage_valid_inst[i] = simple_wire_assign(stage_o[i].valid, stage[i].valid) 

    """ Stage instance, has extra ready and valid lines """ 
    
    reg_stage_data_inst   = [None for i in range(self.pars.NB_PIPELINE_STAGES)]
    reg_stage_sop_inst    = [None for i in range(self.pars.NB_PIPELINE_STAGES)]
    reg_stage_eop_inst    = [None for i in range(self.pars.NB_PIPELINE_STAGES)]
    reg_stage_valid_inst  = [None for i in range(self.pars.NB_PIPELINE_STAGES)]
    
    reg_stage_data_inst[0]  = conditional_wire_assign(stage[0].data, shiftEn_i, pipest_snk.data, 0); 
    reg_stage_sop_inst[0]   = conditional_wire_assign(stage[0].sop, shiftEn_i, pipest_snk.sop, 0); 
    reg_stage_eop_inst[0]   = conditional_wire_assign(stage[0].eop, shiftEn_i, pipest_snk.eop, 0); 
    reg_stage_valid_inst[0] = conditional_wire_assign(stage[0].valid, shiftEn_i, pipest_snk.valid, 0); 
    
    for i in range(1,self.pars.NB_PIPELINE_STAGES):
      reg_stage_data_inst[i]  = simple_reg_assign(reset, clk, stage[i].data, 0, stage[i-1].data)    
      reg_stage_sop_inst[i]   = simple_reg_assign(reset, clk, stage[i].sop, 0, stage[i-1].sop)    
      reg_stage_eop_inst[i]   = simple_reg_assign(reset, clk, stage[i].eop, 0, stage[i-1].eop)    
      reg_stage_valid_inst[i] = simple_reg_assign(reset, clk, stage[i].valid, 0, stage[i-1].valid)    

    return instances() 
