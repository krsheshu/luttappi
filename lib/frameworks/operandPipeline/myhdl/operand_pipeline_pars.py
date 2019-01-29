#----Parameters for operandPipeline Class

class OperandPipelinePars(): 
  def __init__(self):
    """ Initialize OperandPipeline parameters """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH          = 32 
  
  def __call__(self,pars):
    """ Overwrite OperandPipeline parameters """
    self.NB_PIPELINE_STAGES = pars.NB_PIPELINE_STAGES
    self.DATAWIDTH          = pars.DATAWIDTH

