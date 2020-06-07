
from myhdl import Signal, intbv, toVerilog, toVHDL, instances, block

from avalon_buses           import PipelineST

from operand_pipeline       import OperandPipeline
from command_pipeline       import CommandPipeline
from accumulator            import Accumulator
from activation             import Activation
from logistic_regression    import LogisticRegression, LogisticRegressionPars, LogisticRegressionIo

def logistic_regression_convert():

  reset = Signal(bool(0))
  clk = Signal(bool(0))
  LEN_THETA=3
  NB_PIPELINE_STAGES = 5
  DATAWIDTH=32
  CHANNEL_WIDTH=1
  INIT_DATA=0 #(0 for intbv)

  # --- Pipeline Pars
  pars=LogisticRegressionPars()
  pars.NB_PIPELINE_STAGES=NB_PIPELINE_STAGES
  pars.DATAWIDTH=DATAWIDTH
  pars.CHANNEL_WIDTH=CHANNEL_WIDTH
  pars.INIT_DATA=INIT_DATA
  pars.LEN_THETA=LEN_THETA
  pars.CMD_FILE='tb/tests/mult_pipeline.list'

  lRIO=LogisticRegressionIo()
  lRIO(pars)

  lRModule=LogisticRegression()
  lRInst=lRModule.block_connect(pars, reset, clk, lRIO.pipe_inpA, lRIO.pipe_inpB, lRIO.pipe_out_activ )

  lRInst.convert(hdl='Verilog', path = "converted_hdl", name="logistic_regression")
  lRInst.convert(hdl='VHDL', path = "converted_hdl", name="logistic_regression")
