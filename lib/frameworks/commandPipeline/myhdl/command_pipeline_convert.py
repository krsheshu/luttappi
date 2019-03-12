
from myhdl import Signal, intbv, toVerilog, instances

from avalon_buses import PipelineST

from operand_pipeline import OperandPipeline, OperandPipelinePars, OperandPipelineIo 
from command_pipeline import CommandPipeline, CommandPipelinePars, CommandPipelineIo 
from accumulator import Accumulator, AccumulatorPars
from activation import Activation, ActivationPars


def lr_top(pars, reset, clk, pipe_inpA, pipe_inpB, pipe_out_activ):
 
  #----------------- Initializing Pipeline Streams ----------------
  
  # --- Initializing Pipeline A
  pipe_outA  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
  
  operand_a=OperandPipeline()
  ioA=OperandPipelineIo()
  ioA(pars)
  
  # --- Initializing Pipeline B
  pipe_outB  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
  
  operand_b=OperandPipeline()
  ioB=OperandPipelineIo()
  ioB(pars)
  
  # --- Initializing Command Pipeline
  pipe_multRes  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)
  multcmdFile='tb/tests/mult_pipeline.list'
  parsMult= CommandPipelinePars()
  parsMult.DATAWIDTH= pars.DATAWIDTH
  parsMult.CHANNEL_WIDTH = pars.CHANNEL_WIDTH
  parsMult.INIT_DATA = pars.INIT_DATA
  parsMult.STAGE_NB = 1
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

def command_pipeline_convert():
  
  reset = Signal(bool(0))
  clk = Signal(bool(0))
  LEN_THETA=3
  NB_PIPELINE_STAGES = 5
  DATAWIDTH=32
  CHANNEL_WIDTH=1
  INIT_DATA=0 #(0 for intbv)

  # --- Pipeline Pars
  pars=OperandPipelinePars()
  pars.NB_PIPELINE_STAGES=NB_PIPELINE_STAGES
  pars.DATAWIDTH=DATAWIDTH
  pars.CHANNEL_WIDTH=CHANNEL_WIDTH
  pars.INIT_DATA=INIT_DATA     
  pars.LEN_THETA=LEN_THETA
  # --- Initializing Pipeline A
  pipe_inpA  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
  
  # --- Initializing Pipeline B
  pipe_inpB  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
  
  # --- Initializing Activation Out 
  pipe_out_activ = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)
  
  toVerilog(lr_top, pars, reset, clk, pipe_inpA, pipe_inpB, pipe_out_activ)
