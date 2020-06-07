
from myhdl import Signal, intbv, toVerilog
from myhdl.conversion import analyze
from avalon_buses import AvalonST_SNK, AvalonST_SRC
from streaming_ip_b import streaming_ip_b


def streaming_ip_b_convert():

  DATA_WIDTH = 64
  EMPTY_WIDTH = 3
  ERROR_WIDTH = 3
  CHANNEL_WIDTH = 4

  av_snk = AvalonST_SNK(DATA_WIDTH, ERROR_WIDTH, EMPTY_WIDTH, CHANNEL_WIDTH)
  av_src = AvalonST_SRC(DATA_WIDTH, ERROR_WIDTH, EMPTY_WIDTH, CHANNEL_WIDTH)
  reset = Signal(bool(0))
  clk = Signal(bool(0))
  data_enable = Signal(bool(0))

  toVerilog( streaming_ip_b, reset, clk, av_snk, av_src)
  # Following analyze command checks the syntax errors in the converted code as well. Currently, not used as the output can not be geneated/read from a given directory
  #analyze( streaming_ip_b, clk, reset, av_snk, av_src, data_enable)
