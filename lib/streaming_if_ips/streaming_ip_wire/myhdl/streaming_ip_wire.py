from myhdl import always_comb, instances, block
from avalon_buses import AvalonST_SNK, AvalonST_SRC


@block
def streaming_ip_wire( reset, clk, av_snk, av_src ):

  @always_comb
  def streaming_wire_assignments():
      av_snk.ready_o.next = av_src.ready_i 
      av_src.valid_o.next = av_snk.valid_i 
      av_src.data_o.next  = av_snk.data_i
      av_src.startofpacket_o.next = av_snk.startofpacket_i
      av_src.endofpacket_o.next = av_snk.endofpacket_i
      av_src.channel_o.next = av_snk.channel_i
  
  return instances()
