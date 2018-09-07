from myhdl import always, always_comb, Signal, intbv, instances


def streaming_ip_b( reset, clk, av_snk, av_src ):

  ready_reg = Signal(bool(0))
  valid_reg = Signal(bool(0))
  sop_reg = Signal(bool(0))
  eop_reg = Signal(bool(0))
  data_reg = Signal(intbv(0)[len(av_snk.data_i):])
  channel_reg = Signal(intbv(0)[len(av_snk.channel_i):])
  
  valid_comb = Signal(bool(0))
  sop_comb = Signal(bool(0))
  eop_comb = Signal(bool(0))
  data_comb = Signal(intbv(0)[len(av_snk.data_i):])
  channel_comb = Signal(intbv(0)[len(av_snk.channel_i):])
  
  @always_comb
  def output_process():
    if (ready_reg):
      av_src.valid_o.next = valid_comb  
      av_src.data_o.next = data_comb  
      av_src.startofpacket_o.next = sop_comb  
      av_src.endofpacket_o.next = eop_comb
      av_src.channel_o.next = channel_comb
    else:
      av_src.valid_o.next = valid_reg  
      av_src.data_o.next = data_reg 
      av_src.startofpacket_o.next = sop_reg  
      av_src.endofpacket_o.next = eop_reg 
      av_src.channel_o.next = channel_reg
    av_snk.ready_o.next = ready_reg
 

  @always(clk.posedge, reset.posedge)
  def sequential_process1():
    if reset==1:
      ready_reg.next= 0
    else:
      ready_reg.next = av_src.ready_i
 
  @always(clk.posedge, reset.posedge)
  def sequential_process2():
    if reset==1:
      valid_reg.next= 0
      sop_reg.next = 0
      eop_reg.next = 0
      data_reg.next = 0
      channel_reg.next = 0
    elif (ready_reg == 1):
      valid_reg.next =  av_snk.valid_i 
      sop_reg.next =  av_snk.startofpacket_i
      eop_reg.next =  av_snk.endofpacket_i
      data_reg.next = av_snk.data_i
      channel_reg.next = av_snk.channel_i 
 
  @always_comb
  def comb_process():
    valid_comb.next = av_snk.valid_i if (ready_reg == 1) else 0  
    sop_comb.next = av_snk.startofpacket_i if (ready_reg == 1) else 0  
    eop_comb.next = av_snk.endofpacket_i if (ready_reg == 1) else 0  
    data_comb.next = av_snk.data_i if (ready_reg == 1) else 0 
    channel_comb.next = av_snk.channel_i if (ready_reg == 1) else 0 


 
   
  return instances()
