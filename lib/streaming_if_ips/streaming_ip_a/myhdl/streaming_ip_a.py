from myhdl import always, always_comb, Signal, instances, block

@block
def streaming_ip_a(reset, clk, av_snk, av_src, data_enable_o):

  src_valid,snk_ready = [Signal(bool(0)) for i in range(2)]

  @always_comb
  def output_gen_wires():
    av_src.valid_o.next = src_valid
    av_snk.ready_o.next = snk_ready 
    
  @always_comb
  def snk_ready_process():
    if (src_valid == 1 and av_src.ready_i == 0):
      snk_ready.next = 0 
    else:
      snk_ready.next = 1 
  
  #Registering valid
  @always(clk.posedge, reset.posedge)
  def src_valid_reg_process():
    if reset==1:
      src_valid.next = 0
    elif av_snk.valid_i == 1 and av_src.ready_i == 1:
      src_valid.next = 1
    elif av_snk.valid_i == 0 and av_src.ready_i == 1 and src_valid == 1:
      src_valid.next = 0
    elif av_snk.valid_i == 1 and av_src.ready_i == 0 and src_valid == 0:
      src_valid.next = 1
  

  #Dataenable as output
  @always_comb
  def data_enable_process():
    if reset==1:
      data_enable_o.next = 0
    elif snk_ready == 1 and av_snk.valid_i == 1:
      data_enable_o.next = 1
    else:
      data_enable_o.next = 0

  return instances()


from avalon_buses import AvalonST_SNK, AvalonST_SRC

@block
def streaming_ip_a_top(reset, clk, av_snk, av_src):
 
  data_enable_o=Signal(bool(0))

  av_snk_if = AvalonST_SNK(len(av_snk.data_i))
  av_src_if = AvalonST_SRC(len(av_src.data_o))

  @always_comb
  def signal_assignments():
    av_snk_if.valid_i.next=av_snk.valid_i
    av_snk.ready_o.next=av_snk_if.ready_o
    av_src.valid_o.next=av_src_if.valid_o
    av_src_if.ready_i.next=av_src.ready_i

  streaming_ip_a_inst = streaming_ip_a(reset, clk, av_snk_if, av_src_if,data_enable_o )

  @always(clk.posedge, reset.posedge)
  def av_signals_process():
    if reset==1:
      av_src.startofpacket_o.next = 0
      av_src.endofpacket_o.next = 0
      av_src.data_o.next = 0
      av_src.channel_o.next = 0
    elif data_enable_o == 1:
      av_src.startofpacket_o.next = av_snk.startofpacket_i
      av_src.data_o.next = av_snk.data_i
      av_src.endofpacket_o.next = av_snk.endofpacket_i
      av_src.channel_o.next = av_snk.channel_i

  return instances()
      
    
    

