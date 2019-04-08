from myhdl import always_comb, block

@block
def streaming_ip_comb( reset, clk, av_snk, av_src, data_enable ):

  @always_comb
  def valid_o_logic():
    if av_src.ready_i == 1 and av_snk.valid_i == 1:
      av_snk.ready_o.next = 1 
      av_src.valid_o.next = 1 
      data_enable.next = 1 
    else:
      av_snk.ready_o.next = 0 
      av_src.valid_o.next = 0 
      data_enable.next = 0
 
  return valid_o_logic
