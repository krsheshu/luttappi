from myhdl import always_comb, block

# wire streaming source interface to streaming sink interface
@block
def streaming_src_to_snk_wire(aso_src, asi_snk):

  @always_comb
  def src_to_snk_wire():
    asi_snk.valid_i.next  = aso_src.valid_o
    asi_snk.data_i.next  = aso_src.data_o
    asi_snk.startofpacket_i.next = aso_src.startofpacket_o
    asi_snk.endofpacket_i.next = aso_src.endofpacket_o
    aso_src.ready_i.next  = asi_snk.ready_o

  return src_to_snk_wire
