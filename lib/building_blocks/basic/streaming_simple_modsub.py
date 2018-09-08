import myhdl

class StreamingSimpleModSubPars():
  def __init__(self):
    """ simple modsub pars """
    self.SNK0_SYMBOL_WIDTH=32
    self.SNK1_SYMBOL_WIDTH=32
    self.SRC_SYMBOL_WIDTH=32
  def __call__(self, pars):
    self.SNK0_SYMBOL_WIDTH   = pars.SNK0_SYMBOL_WIDTH
    self.SNK1_SYMBOL_WIDTH   = pars.SNK1_SYMBOL_WIDTH
    self.SRC_SYMBOL_WIDTH    = pars.SRC_SYMBOL_WIDTH

class StreamingSimpleModSub():
  """ StreamingSimpleModSub Top """
  def __init__(self):
    pass

  def block_connect(pars, reset, clk, av_snk0, av_snk1, av_src):
    """ streaming_simple modesub block"""

  data_enable_o=Signal(bool(0))

  av_snk0_if = AvalonST_SNK(pars.SNK0_SYMBOL_WIDTH)
  av_snk1_if = AvalonST_SNK(pars.SNK1_SYMBOL_WIDTH)
  av_src_if = AvalonST_SRC(pars.SRC_SYMBOL_WIDTH)


  @always_comb
  def signal_assignments():
    av_snk0_if.valid_i.next=av_snk0.valid_i
    av_snk0.ready_o.next=av_snk0_if.ready_o
    
    av_src.valid_o.next=av_src_if.valid_o
    av_src_if.ready_i.next=av_src.ready_i
    
    av_snk1_if.valid_i.next=av_snk1.valid_i
    av_snk1.ready_o.next=av_snk1_if.ready_o

  streaming_ip_a_2xinp_inst = streaming_ip_a_2xinp(reset, clk, av_snk0_if, av_snk1_if, av_src_if, data_enable_o )

  @always(clk.posedge, reset.posedge)
  def streaming_simple_modesub():
    """ streaming_simple modesub """
    if reset==1:
      av_src.startofpacket_o.next = 0
      av_src.endofpacket_o.next = 0
      av_src.data_o.next = 0
      av_src.channel_o.next = 0
    elif data_enable_o == 1:
      av_src.startofpacket_o.next = av_snk0.startofpacket_i and av_snk1.startofpacket_i 
      av_src.data_o.next = (av_snk0.data_i - av_snk1.data_i) if (av_snk0.data_i >  av_snk1.data_i)
                            else (av_snk1.data_i - av_snk0.data_i) 
      av_src.endofpacket_o.next = av_snk0.endofpacket_i and av_snk1.endofpacket_i
      av_src.channel_o.next = av_snk0.channel_i and av_snk1.channel_i
