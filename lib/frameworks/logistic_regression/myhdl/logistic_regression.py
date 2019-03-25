#----logisticRegression Class 
from myhdl import Signal, intbv, toVerilog, toVHDL, instances

from avalon_buses import PipelineST

from operand_pipeline import OperandPipeline, OperandPipelinePars, OperandPipelineIo 
from command_pipeline import CommandPipeline, CommandPipelinePars, CommandPipelineIo 
from accumulator import Accumulator, AccumulatorPars
from activation import Activation, ActivationPars

#---- Class LogisticRegressionIo
class LogisticRegressionIo(): 
  def __init__(self):
    """ Initialize LogisticRegression Ios """
    self.DATAWIDTH          = 32
    self.CHANNEL_WIDTH      = 1
    self.INIT_DATA          = 0 #(0 for intbv)

    # --- Initializing Pipeline A
    self.pipe_inpA  = PipelineST(self.DATAWIDTH,self.CHANNEL_WIDTH,self.INIT_DATA) 
    # --- Initializing Pipeline B
    self.pipe_inpB  = PipelineST(self.DATAWIDTH,self.CHANNEL_WIDTH,self.INIT_DATA) 
    # --- Initializing Activation Out 
    self.pipe_out_activ = PipelineST(self.DATAWIDTH,self.CHANNEL_WIDTH,self.INIT_DATA)
  
  def __call__(self,pars):
    """ Overwrite LogisticRegression Ios """
    self.pipe_inpA  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
    self.pipe_inpB  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
    self.pipe_out_activ = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)


#----Parameters for LogisticRegression Class
class LogisticRegressionPars(): 
  def __init__(self):
    """ Initialize CommandPipeline parameters """
    self.NB_PIPELINE_STAGES = 4
    self.DATAWIDTH          = 32
    self.CHANNEL_WIDTH      = 1
    self.INIT_DATA          = 0 #(0 for intbv)
    self.LEN_THETA          = 3
    self.CMD_FILE           = ""
  
  def __call__(self,pars):
    """ Overwrite CommandPipeline parameters """
    self.NB_PIPELINE_STAGES = pars.NB_PIPELINE_STAGES
    self.DATAWIDTH          = pars.DATAWIDTH
    self.CHANNEL_WIDTH      = pars.CHANNEL_WIDTH
    self.INIT_DATA          = pars.INIT_DATA  #(0 for intbv)
    self.LEN_THETA          = pars.LEN_THETA 
    self.CMD_FILE           = pars.CMD_FILE


#-----Class LogisticRegression 
class LogisticRegression():
  
  def __init__(self):
    """ LogisticRegression Init"""


  def block_connect(pars, reset, clk, pipe_inpA, pipe_inpB, pipe_out_activ):
 
    #----------------- Initializing Pipeline Streams ----------------
    
    # --- Initializing Pipeline A
    pipe_outA  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
    
    operand_a=OperandPipeline()
    ioA=OperandPipelineIo()
    ioA(pars)
    #block_connect.ioA=ioA 
    #block_connect.ioB=ioB 
    # --- Initializing Pipeline B
    pipe_outB  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
    
    operand_b=OperandPipeline()
    ioB=OperandPipelineIo()
    ioB(pars)
    
    # --- Initializing Command Pipeline
    pipe_multRes  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)
    multcmdFile=pars.CMD_FILE
    parsMult= CommandPipelinePars()
    parsMult.DATAWIDTH= pars.DATAWIDTH
    parsMult.CHANNEL_WIDTH = pars.CHANNEL_WIDTH
    parsMult.INIT_DATA = pars.INIT_DATA
    parsMult(parsMult,multcmdFile) 
    multPipe=CommandPipeline()
    ioMult=CommandPipelineIo()
    ioMult(pars)
    
    # ---- Initializing Accumulator Block
    
    pipe_out_acc = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)
    parsAcc= AccumulatorPars()
    parsAcc.DATAWIDTH= pars.DATAWIDTH
    parsAcc.CHANNEL_WIDTH = pars.CHANNEL_WIDTH
    parsAcc.INIT_DATA = pars.INIT_DATA
    parsAcc.NB_ACCUMULATIONS = pars.LEN_THETA  
    accuPipe= Accumulator() 
    accuPipe(parsAcc) 
    
    # ---- Initializing Activation Block
    
    parsActiv= ActivationPars()
    parsActiv.DATAWIDTH= 3    # 0 or 1 for classification
    parsActiv.CHANNEL_WIDTH = pars.CHANNEL_WIDTH
    parsActiv.INIT_DATA = pars.INIT_DATA
    activPipe= Activation() 
    activPipe(parsActiv) 
    #----------------------------------------------------------------
    
    #----------------- Connecting Pipeline Blocks -------------------
   
    trainingData=(operand_a.block_connect(pars, reset, clk, pipe_inpA, pipe_outA, ioA))
    theta=(operand_b.block_connect(pars, reset, clk, pipe_inpB, pipe_outB, ioB))
    #----------------------------------------------------------------
    
    #----------------- Connecting Command Pipeline -------------------
    # Mult Pipeline
    command=(multPipe.block_connect(parsMult, reset, clk, ioA, ioB, pipe_multRes, ioMult))   
    #----------------------------------------------------------------
    
    #----------------- Connecting Accumulator  --------------
    # Accu
    acc_reset=Signal(bool(0)) 
    accumulator=(accuPipe.block_connect(parsAcc, reset, clk, acc_reset, pipe_multRes, pipe_out_acc))   
    
    #----------------------------------------------------------------
    
    #----------------- Connecting Activation  --------------
    # Simple Step Activation function  
    activation=(activPipe.block_step_connect(parsActiv, reset, clk, pipe_out_acc, pipe_out_activ ))   
   
    #----------------------------------------------------------------
  
    return instances()
