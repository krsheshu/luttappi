#----operationPipeline Class 

#----imports
from myhdl import always, always_comb, Signal, instances, block, intbv
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

    self.STAGE_NB           = 2
    self.OPCODE             = 0x00  # NOP by default
    self.OPCODEBITS         = 8 
  
  def __call__(self,pars, cmdFile):
    """ Overwrite CommandPipeline parameters """
    self.NB_PIPELINE_STAGES = pars.NB_PIPELINE_STAGES
    self.DATAWIDTH          = pars.DATAWIDTH
    self.CHANNEL_WIDTH      = pars.CHANNEL_WIDTH
    self.INIT_DATA          = pars.INIT_DATA

    self.STAGE_NB           = pars.STAGE_NB

    """ Convert cmfFile to a cmdStringList of Pipeline operators"""
    cmdStringList=None
    f=open(cmdFile)
    cmdStringList=f.readlines()
    f.close()
    cmdStr = [s.rstrip() for s in cmdStringList]
    
    for i in range(len(cmdStr)):
      if (cmdStr[i] != "NOP"):
        if ( cmdStr[i] == "ADD"):     # A+B 
          self.OPCODE             = 0x31 
        elif ( cmdStr[i] == "SUB"):   # A-B        
          self.OPCODE             = 0x32 
        elif ( cmdStr[i] == "SUBR"):  # B-A          
          self.OPCODE             = 0x33 
        elif ( cmdStr[i] == "MULT"):  # A*B          
          self.OPCODE             = 0x34 
        elif ( cmdStr[i] == "NOP"):   # No Operation       
          self.OPCODE             = 0x00
        break 



#-----Class Description
class CommandPipeline():
  
  def __init__(self):
    """ CommandPipeline Init"""

  #@block 
  def block_atomic_oper(self, pars, reset, clk, cmd, stage_iA, stage_iB, stage_o):
    """ Atomic Command block """

    @always(clk.posedge)
    def atomic_operation_assign_process():
      if ( cmd == 0x31):     # A+B 
        stage_o.data.next = stage_iA.data + stage_iB.data
      elif ( cmd == 0x32):   # A-B        
        stage_o.data.next = stage_iA.data - stage_iB.data
      elif ( cmd == 0x33):  # B-A          
        stage_o.data.next = stage_iB.data - stage_iA.data
      elif ( cmd == 0x34):  # A*B          
        stage_o.data.next = stage_iA.data * stage_iB.data
      elif ( cmd == 0x00):   # No Operation       
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
  def block_connect(self, pars, reset, clk, pipe_stageA, pipe_stageB, pipest_src, io):
    """ CommandPipeline block """
   
    stage = [PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) for i in range(pars.NB_PIPELINE_STAGES)]
   
    # Reset value to incorporate float and intbv formats
    reset_val = 0.0 if (isinstance(pars.INIT_DATA,float)) else 0

    """ Output pipesrc instance """
    data_out_inst   = simple_wire_assign(pipest_src.data, io.stage_o[pars.NB_PIPELINE_STAGES-1].data)
    sop_out_inst    = simple_wire_assign(pipest_src.sop, io.stage_o[pars.NB_PIPELINE_STAGES-1].sop)
    eop_out_inst    = simple_wire_assign(pipest_src.eop, io.stage_o[pars.NB_PIPELINE_STAGES-1].eop)
    valid_out_inst  = simple_wire_assign(pipest_src.valid, io.stage_o[pars.NB_PIPELINE_STAGES-1].valid)
    channel_out_inst  = simple_wire_assign(pipest_src.channel, io.stage_o[pars.NB_PIPELINE_STAGES-1].channel)

 
    wire_stage_data_inst   = []
    wire_stage_sop_inst    = []
    wire_stage_eop_inst    = []
    wire_stage_valid_inst  = []
    wire_stage_channel_inst  = []
    
    for i in range(pars.NB_PIPELINE_STAGES):
      """ module outputs """
      wire_stage_data_inst.append(simple_wire_assign(io.stage_o[i].data, stage[i].data))
      wire_stage_sop_inst.append(simple_wire_assign(io.stage_o[i].sop, stage[i].sop)) 
      wire_stage_eop_inst.append(simple_wire_assign(io.stage_o[i].eop, stage[i].eop))
      wire_stage_valid_inst.append(simple_wire_assign(io.stage_o[i].valid, stage[i].valid)) 
      wire_stage_channel_inst.append(simple_wire_assign(io.stage_o[i].channel, stage[i].channel)) 

    """ Call block atomic operation on each stage """ 
    
    reg_stage_inst   = []
    cmd=Signal(intbv(pars.OPCODE)[pars.OPCODEBITS:]) 
    reg_stage_inst.append(self.block_atomic_oper(pars, reset, clk, cmd, pipe_stageA.stage_o[pars.STAGE_NB], pipe_stageB.stage_o[pars.STAGE_NB], stage[0]))    
    for j in range(1,pars.NB_PIPELINE_STAGES):
      reg_stage_inst.append(simple_reg_assign(reset, clk, stage[j].data, reset_val, stage[j-1].data) )    
      reg_stage_inst.append(simple_reg_assign(reset, clk, stage[j].sop, 0, stage[j-1].sop) )   
      reg_stage_inst.append(simple_reg_assign(reset, clk, stage[j].eop, 0, stage[j-1].eop) )   
      reg_stage_inst.append(simple_reg_assign(reset, clk, stage[j].valid, 0, stage[j-1].valid) )
      reg_stage_inst.append(simple_reg_assign(reset, clk, stage[j].channel, 0, stage[j-1].channel) )
      
    return instances() 
  
  def validate(self, ipFile, opFile):
    """ Validation block """
    pass
