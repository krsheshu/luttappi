from avalon_buses import AvalonMM, AvalonST_SNK, AvalonST_SRC
from myhdl import Signal, toVerilog
from streaming_ip_wire import streaming_ip_wire

def streaming_ip_wire_convert():


  SYMBOL_WIDTH = 8
  NR_OF_SYMBOLS = 8
  
  reset = Signal(bool(0))
  clk = Signal(bool(0))
  av_snk =  AvalonST_SNK(SYMBOL_WIDTH*NR_OF_SYMBOLS)
  av_src = AvalonST_SRC(SYMBOL_WIDTH*NR_OF_SYMBOLS)
  
  toVerilog (streaming_ip_wire, reset, clk , av_snk, av_src)
