#----IOs for operandPipeline Class

#----imports
from myhdl import Signal
from avalon_buses import PipelineST


#---- Class description
class OperandPipelineIo(): 
  def __init__(self):
    """ Initialize OperandPipeline Ios """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH = 32
    self.shiftEn_i  = Signal(bool(0))
    self.stage_o    = [PipelineST(self.DATAWIDTH) for i in range(self.NB_PIPELINE_STAGES)]
 
  
  def __call__(self,pars):
    """ Overwrite OperandPipeline Ios """
    self.shiftEn_i  = Signal(bool(0))
    self.stage_o    = [PipelineST(pars.DATAWIDTH) for i in range(pars.NB_PIPELINE_STAGES)]

