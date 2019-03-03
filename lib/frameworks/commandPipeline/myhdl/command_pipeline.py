#----operationPipeline Class 

#----imports
from myhdl import always, always_comb, Signal, instances, block
from avalon_buses import PipelineST
from common_functions import simple_wire_assign, simple_reg_assign, conditional_wire_assign

#---- Class description
class CommandPipelineIo(): 
  def __init__(self):
    """ Initialize CommandPipeline Ios """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH = 32
    self.stage_o    = [PipelineST(self.DATAWIDTH) for i in range(self.NB_PIPELINE_STAGES)]
 
  
  def __call__(self,pars):
    """ Overwrite CommandPipeline Ios """
    self.stage_o    = [PipelineST(pars.DATAWIDTH) for i in range(pars.NB_PIPELINE_STAGES)]

#----Parameters for operationPipeline Class
class CommandPipelinePars(): 
  def __init__(self):
    """ Initialize CommandPipeline parameters """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH          = 32 
  
  def __call__(self,pars):
    """ Overwrite CommandPipeline parameters """
    self.NB_PIPELINE_STAGES = pars.NB_PIPELINE_STAGES
    self.DATAWIDTH          = pars.DATAWIDTH



#-----Class Description
class CommandPipeline():
  
  def __init__(self):
    """ CommandPipeline Init"""

  #@block 
  def cmd_convert_to_string(self, pars, cmdFile):
    """ Convert cmfFile to a cmdStringList of Pipeline operators"""
    cmdStringList=[]
    with open(cmdFile) as f:
      cmdStringList.append(f.readlines())
       
    return cmdStringList

  #@block 
  def block_atomic_oper(self, pars, clk, cmdStr, stage_iA, stage_iB, stage_o):
    """ Atomic Command block """
    
    #@always(clk.posedge)
    #def atomic_operation_assign_process():
    #  if ( cmdStr == "ADD"):     # A+B 
    #    stage_o.next = stage_iA+ stage_iB
    #  elif ( cmdStr == "SUB"):   # A-B     
    #    stage_o.next = stage_iA- stage_iB
    #  elif ( cmdStr == "SUBR"):  # B-A       
    #    stage_o.next = stage_iB- stage_iA
    #  elif ( cmdStr == "MULT"):  # A*B       
    #    stage_o.next = stage_iA* stage_iB
    #  elif ( cmdStr == "NOP"):   # No Operation       
    #    stage_o.next = stage_o
    #@always(clk.posedge)
    #def atomic_operation_assign_process():
    #  if ( cmdStr == "ADD"):     # A+B 
    #    stage_o.data.next = stage_iA.data + stage_iB.data
    #  elif ( cmdStr == "SUB"):   # A-B     
    #    stage_o.data.next = stage_iA.data - stage_iB.data
    #  elif ( cmdStr == "SUBR"):  # B-A       
    #    stage_o.data.next = stage_iA.data - stage_iB.data
    #  elif ( cmdStr == "MULT"):  # A*B       
    #    stage_o.data.next = stage_iA.data * stage_iB.data
    #  elif ( cmdStr == "NOP"):   # No Operation       
    #    stage_o.data.next = stage_o.data

      #if (stage_iA.valid == 1 and stage_iB.valid == 1):
      #    stage_o.valid.next = 1
      #else:
      #    stage_o.valid.next = 0
     # 
     # if (stage_iA.sop == 1 and stage_iB.sop == 1):
     #     stage_o.sop.next = 1
     # else:
     #     stage_o.sop.next = 0
     # 
     # if (stage_iA.eop == 1 and stage_iB.eop == 1):
     #     stage_o.eop.next = 1
     # else:
     #     stage_o.eop.next = 0
 
    return instances()


  #@block 
  def block_connect(self, pars, reset, clk, cmdStringList, pipe_stageA, pipe_stageB, pipest_src, io):
    """ CommandPipeline block """
   
    stage = [PipelineST(pars.DATAWIDTH) for i in range(pars.NB_PIPELINE_STAGES)]
   

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
      wire_stage_sop_inst.append(simple_wire_assign(io.stage_o[i].sop, stage[i].sop)) 
      wire_stage_eop_inst.append(simple_wire_assign(io.stage_o[i].eop, stage[i].eop))
      wire_stage_valid_inst.append(simple_wire_assign(io.stage_o[i].valid, stage[i].valid)) 

    """ Call block atomic operation on each stage """ 
    
    reg_stage_inst   = []
    
    #for i in range(pars.NB_PIPELINE_STAGES):
    #for i in range(1):
    #  reg_stage_inst.append(self.block_atomic_oper(pars, clk, cmdStringList[i], pipe_stageA[i], pipe_stageB[i], stage[i]))    
    @always(clk.posedge)
    def atomic_operation_assign_process():
      if ( cmdStringList[0][0] == "ADD"):     # A+B 
        stage_o[0].data.next = stage_iA[0].data + stage_iB[0].data
      elif ( cmdStringList[0][0] == "SUB"):   # A-B     
        stage_o[0].data.next = stage_iA[0].data - stage_iB[0].data
      elif ( cmdStringList[0][0] == "SUBR"):  # B-A       
        stage_o[0].data.next = stage_iA[0].data - stage_iB[0].data
      elif ( cmdStringList[0][0] == "MULT"):  # A*B       
        stage_o[0].data.next = stage_iA[0].data * stage_iB[0].data
      elif ( cmdStringList[0][0] == "NOP"):   # No Operation       
        stage_o[0].data.next = stage_o[0].data

      #if (stage_iA[0].valid == 1 and stage_iB[0].valid == 1):
      #stage_o[0].valid.next = 1
      #else:
       #   stage_o[0].valid.next = 0
      
    return instances() 
  
  def validate(self, ipFile, opFile):
    """ Validation block """
    pass
