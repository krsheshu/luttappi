
from myhdl import Signal, intbv, toVerilog
from myhdl.conversion import analyze
from avalon_buses import AvalonST_SNK, AvalonST_SRC
from streaming_ip_a import streaming_ip_a_top


def streaming_ip_a_convert():

  DATA_WIDTH = 64
  EMPTY_WIDTH = 3
  ERROR_WIDTH = 3
  CHANNEL_WIDTH = 4

  av_snk = AvalonST_SNK(DATA_WIDTH, ERROR_WIDTH, EMPTY_WIDTH, CHANNEL_WIDTH)
  av_src = AvalonST_SRC(DATA_WIDTH, ERROR_WIDTH, EMPTY_WIDTH, CHANNEL_WIDTH)
  reset = Signal(bool(0))
  clk = Signal(bool(0))

  toVerilog( streaming_ip_a_top, reset, clk, av_snk, av_src)
  # Following analyze command checks the syntax errors in the converted code as well. Currently, not used as the output can not be geneated/read from a given directory
  #analyze( streaming_ip_a, clk, reset, asi_snk, aso_src, data_enable)
