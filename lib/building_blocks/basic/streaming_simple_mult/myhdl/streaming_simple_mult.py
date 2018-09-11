from myhdl import always, always_comb, Signal, instances
from avalon_buses import AvalonST_SNK, AvalonST_SRC
from streaming_ip_a_2xinp import streaming_ip_a_2xinp

class StreamingSimpleMultPars():
  def __init__(self):
    """ streaming simple mult pars """
    self.SNK0_DATAWIDTH=32
    self.SNK1_DATAWIDTH=32
    self.SRC_DATAWIDTH=32+32
  def __call__(self, pars):
    self.SNK0_DATAWIDTH   = pars.SNK0_DATAWIDTH
    self.SNK1_DATAWIDTH   = pars.SNK1_DATAWIDTH
    self.SRC_DATAWIDTH    = pars.SNK0_DATAWIDTH + pars.SNK1_DATAWIDTH

class StreamingSimpleMult():
  """ StreamingSimpleMult Top """
  def __init__(self):
    pass
  
  def block_connect(self, pars, reset, clk, av_snk0, av_snk1, av_src):
    """ simple mult block"""

    data_enable_o=Signal(bool(0))
 
    av_snk0_if = AvalonST_SNK(pars.SNK0_DATAWIDTH)
    av_snk1_if = AvalonST_SNK(pars.SNK1_DATAWIDTH)
    av_src_if = AvalonST_SRC(pars.SRC_DATAWIDTH)
 
 
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
    def simple_mult():
      """ streaming simple mult """
      if reset==1:
        av_src.startofpacket_o.next = 0
        av_src.endofpacket_o.next = 0
        av_src.data_o.next = 0
        av_src.channel_o.next = 0
      elif data_enable_o == 1:
        av_src.startofpacket_o.next = av_snk0.startofpacket_i and av_snk1.startofpacket_i 
        av_src.data_o.next = av_snk0.data_i * av_snk1.data_i
        av_src.endofpacket_o.next = av_snk0.endofpacket_i and av_snk1.endofpacket_i
        av_src.channel_o.next = av_snk0.channel_i and av_snk1.channel_i
   
    return instances()  
