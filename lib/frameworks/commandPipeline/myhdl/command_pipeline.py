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
    self.DATAWIDTH          = 32
    self.CHANNEL_WIDTH      = 1
    self.INIT_DATA          = 0

    self.stage_o    = [PipelineST(self.DATAWIDTH,self.CHANNEL_WIDTH,self.INIT_DATA) for i in range(self.NB_PIPELINE_STAGES)]
 
  
  def __call__(self,pars):
    """ Overwrite CommandPipeline Ios """
    self.stage_o    = [PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) for i in range(pars.NB_PIPELINE_STAGES)]

#----Parameters for operationPipeline Class
class CommandPipelinePars(): 
  def __init__(self):
    """ Initialize CommandPipeline parameters """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH          = 32
    self.CHANNEL_WIDTH      = 1
    self.INIT_DATA          = 0 
  
  def __call__(self,pars):
    """ Overwrite CommandPipeline parameters """
    self.NB_PIPELINE_STAGES = pars.NB_PIPELINE_STAGES
    self.DATAWIDTH          = pars.DATAWIDTH
    self.CHANNEL_WIDTH      = pars.CHANNEL_WIDTH
    self.INIT_DATA          = pars.INIT_DATA



#-----Class Description
class CommandPipeline():
  
  def __init__(self):
    """ CommandPipeline Init"""

  #@block 
  def cmd_convert_to_string(self, pars, cmdFile):
    """ Convert cmfFile to a cmdStringList of Pipeline operators"""
    cmdStringList=None
    try:
      f=open(cmdFile)
      cmdStringList=f.readlines()
    except FileNotFoundError as fnfE:
      print(fnfE)
    cmdStr = [s.rstrip() for s in cmdStringList]
    return cmdStr

  #@block 
  def block_atomic_oper(self, pars, clk, cmdStr, stage_iA, stage_iB, stage_o):
    """ Atomic Command block """

    print(__name__)
    print(cmdStr) 
    @always(clk.posedge)
    def atomic_operation_assign_process():
      if ( cmdStr == "ADD"):     # A+B 
        stage_o.data.next = stage_iA.data + stage_iB.data
      elif ( cmdStr == "SUB"):   # A-B        
        stage_o.data.next = stage_iA.data - stage_iB.data
      elif ( cmdStr == "SUBR"):  # B-A          
        stage_o.data.next = stage_iB.data - stage_iA.data
      elif ( cmdStr == "MULT"):  # A*B          
        stage_o.data.next = stage_iA.data * stage_iB.data
      elif ( cmdStr == "ACC"):  # Accumulate          
        stage_o.data.next =  stage_o.data + stage_iA.data + stage_iB.data
      elif ( cmdStr == "NOP"):   # No Operation       
        stage_o.data.next = stage_o.data

      if (stage_iA.valid == 1 and stage_iB.valid == 1):
          stage_o.valid.next = 1
      else:
          stage_o.valid.next = 0
      
      if (stage_iA.sop == 1 and stage_iB.sop == 1):
          stage_o.sop.next = 1
      else:
          stage_o.sop.next = 0
      
      if (stage_iA.eop == 1 and stage_iB.eop == 1):
          stage_o.eop.next = 1
      else:
          stage_o.eop.next = 0
 
    return instances()


  #@block 
  def block_connect(self, pars, reset, clk, cmdStringList, pipe_stageA, pipe_stageB, pipest_src, io):
    """ CommandPipeline block """
   
    stage = [PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) for i in range(pars.NB_PIPELINE_STAGES)]
   
    # Reset value to incorporate float and intbv formats
    reset_val = 0.0 if (isinstance(pars.INIT_DATA,float)) else 0

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
   
    for i in range(len(cmdStringList)):
      if (cmdStringList[i] != "NOP"):
        index=i 
    reg_stage_inst.append(self.block_atomic_oper(pars, clk, cmdStringList[index], pipe_stageA.stage_o[index], pipe_stageB.stage_o[index], stage[0]))    
    for j in range(1,pars.NB_PIPELINE_STAGES):
      reg_stage_inst.append(simple_reg_assign(reset, clk, stage[j].data, reset_val, stage[j-1].data) )    
      reg_stage_inst.append(simple_reg_assign(reset, clk, stage[j].sop, reset_val, stage[j-1].sop) )   
      reg_stage_inst.append(simple_reg_assign(reset, clk, stage[j].eop, reset_val, stage[j-1].eop) )   
      reg_stage_inst.append(simple_reg_assign(reset, clk, stage[j].valid, reset_val, stage[j-1].valid) )
      
    return instances() 
  
  def validate(self, ipFile, opFile):
    """ Validation block """
    pass
