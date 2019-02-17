#----operationPipeline Class 

#----imports
from myhdl import always, always_comb, Signal, instances, block
from avalon_buses import PipelineST
from common_functions import simple_wire_assign, simple_reg_assign, conditional_wire_assign

#---- Class description
class OperationPipelineIo(): 
  def __init__(self):
    """ Initialize OperationPipeline Ios """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH = 32
    self.stage_o    = [PipelineST(self.DATAWIDTH) for i in range(self.NB_PIPELINE_STAGES)]
 
  
  def __call__(self,pars):
    """ Overwrite OperationPipeline Ios """
    self.stage_o    = [PipelineST(pars.DATAWIDTH) for i in range(pars.NB_PIPELINE_STAGES)]

#----Parameters for operationPipeline Class
class OperationPipelinePars(): 
  def __init__(self):
    """ Initialize OperationPipeline parameters """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH          = 32 
  
  def __call__(self,pars):
    """ Overwrite OperationPipeline parameters """
    self.NB_PIPELINE_STAGES = pars.NB_PIPELINE_STAGES
    self.DATAWIDTH          = pars.DATAWIDTH



#-----Class Description
class OperationPipeline():
  
  def __init__(self):
    """ OperationPipeline Init"""

  #@block 
  def cmd_convert_to_string(self, pars, cmdFile):
    """ Convert cmfFile to a cmdStringList of Pipeline operators"""
    cmdStringList=[]
    with open('filename') as f:
      cmdStringList.append(f.readlines()) 
    
    return cmdStringList

  #@block 
  def blk_atomic_oper(self, pars, clk, cmdStr, stage_iA, stage_iB, stage_o):
    """ Atomic Operation block """
    
    @always(clk.posedge)
    def atomic_operation_assign_process():
      if ( cmdStr == "ADD"):     # A+B 
        stage_o.data = stage_iA.data + stage_iB.data
      elif ( cmdStr == "SUB"):   # A-B     
        stage_o.data = stage_iA.data - stage_iB.data
      elif ( cmdStr == "SUBR"):  # B-A       
        stage_o.data = stage_iA.data - stage_iB.data
      elif ( cmdStr == "MULT"):  # A*B       
        stage_o.data = stage_iA.data * stage_iB.data

      if (stage_iA.valid == 1 and stage_iB.valid == 1):
          stage_o.valid = 1
      else:
          stage_o.valid = 0
      
      if (stage_iA.sop == 1 and stage_iB.sop == 1):
          stage_o.sop = 1
      else:
          stage_o.sop = 0
      
      if (stage_iA.eop == 1 and stage_iB.eop == 1):
          stage_o.eop = 1
      else:
          stage_o.eop = 0
 


  #@block 
  def block_connect(self, pars, reset, clk, cmdStringList, pipest_snk1, pipest_snk2, pipest_src, io):
    """ OperationPipeline block """
   
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
    
    
    for i in range(1,pars.NB_PIPELINE_STAGES):
      reg_stage_data_inst[i]  = simple_reg_assign(reset, clk, stage[i].datacommandPipeline, 0, stage[i-1].data)    
      reg_stage_sop_inst[i]   = simple_reg_assign(reset, clk, stage[i].sop, 0, stage[i-1].sop)    
      reg_stage_eop_inst[i]   = simple_reg_assign(reset, clk, stage[i].eop, 0, stage[i-1].eop)    
      reg_stage_valid_inst[i] = simple_reg_assign(reset, clk, stage[i].valid, 0, stage[i-1].valid)    

    return instances() 
  
  def validate(self, ipFile, opFile):
    """ Validation block """
    pass
