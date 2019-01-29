#----operandPipeline Class 

#----imports
from myhdl import always, always_comb, Signal, instances, block
from avalon_buses import PipelineST
from common_functions import simple_wire_assign, simple_reg_assign, conditional_wire_assign

#-----Class Description
class OperandPipeline():
  
  def __init__(self):
    """ OperandPipeline Init"""

  #@block 
  def block_connect(self, pars, reset, clk, pipest_snk, pipest_src, io):
    """ OperandPipeline block """
   
    stage = [PipelineST(pars.DATAWIDTH) for i in range(pars.NB_PIPELINE_STAGES)]
   

    """ Output pipesrc instance """
    data_out_inst   = simple_wire_assign(pipest_src.data, io.stage_o[pars.NB_PIPELINE_STAGES-1].data)
    sop_out_inst    = simple_wire_assign(pipest_src.sop, io.stage_o[pars.NB_PIPELINE_STAGES-1].sop)
    eop_out_inst    = simple_wire_assign(pipest_src.eop, io.stage_o[pars.NB_PIPELINE_STAGES-1].eop)
    valid_out_inst  = simple_wire_assign(pipest_src.valid, io.stage_o[pars.NB_PIPELINE_STAGES-1].valid)

 
    wire_stage_data_inst   = [None for i in range(pars.NB_PIPELINE_STAGES)]
    wire_stage_sop_inst    = [None for i in range(pars.NB_PIPELINE_STAGES)]
    wire_stage_eop_inst    = [None for i in range(pars.NB_PIPELINE_STAGES)]
    wire_stage_valid_inst  = [None for i in range(pars.NB_PIPELINE_STAGES)]
    
    for i in range(pars.NB_PIPELINE_STAGES):
      """ module outputs """
      wire_stage_data_inst[i]  = simple_wire_assign(io.stage_o[i].data, stage[i].data)
      wire_stage_sop_inst[i]   = simple_wire_assign(io.stage_o[i].sop, stage[i].sop) 
      wire_stage_eop_inst[i]   = simple_wire_assign(io.stage_o[i].eop, stage[i].eop) 
      wire_stage_valid_inst[i] = simple_wire_assign(io.stage_o[i].valid, stage[i].valid) 

    """ Stage instance, has extra ready and valid lines """ 
    
    reg_stage_data_inst   = [None for i in range(pars.NB_PIPELINE_STAGES)]
    reg_stage_sop_inst    = [None for i in range(pars.NB_PIPELINE_STAGES)]
    reg_stage_eop_inst    = [None for i in range(pars.NB_PIPELINE_STAGES)]
    reg_stage_valid_inst  = [None for i in range(pars.NB_PIPELINE_STAGES)]
    
    reg_stage_data_inst[0]  = conditional_wire_assign(stage[0].data, io.shiftEn_i, pipest_snk.data, 0); 
    reg_stage_sop_inst[0]   = conditional_wire_assign(stage[0].sop, io.shiftEn_i, pipest_snk.sop, 0); 
    reg_stage_eop_inst[0]   = conditional_wire_assign(stage[0].eop, io.shiftEn_i, pipest_snk.eop, 0); 
    reg_stage_valid_inst[0] = conditional_wire_assign(stage[0].valid, io.shiftEn_i, pipest_snk.valid, 0); 
    
    for i in range(1,pars.NB_PIPELINE_STAGES):
      reg_stage_data_inst[i]  = simple_reg_assign(reset, clk, stage[i].data, 0, stage[i-1].data)    
      reg_stage_sop_inst[i]   = simple_reg_assign(reset, clk, stage[i].sop, 0, stage[i-1].sop)    
      reg_stage_eop_inst[i]   = simple_reg_assign(reset, clk, stage[i].eop, 0, stage[i-1].eop)    
      reg_stage_valid_inst[i] = simple_reg_assign(reset, clk, stage[i].valid, 0, stage[i-1].valid)    

    return instances() 
  
  def validate(self, ipFile, opFile):
    """ Validation block """
    pass
