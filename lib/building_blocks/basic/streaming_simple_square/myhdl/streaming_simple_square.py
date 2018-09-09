import myhdl
from avalon_buses import AvalonST_SNK, AvalonST_SRC
from streaming_ip_a import streaming_ip_a

class StreamingSimpleSquarePars():
  def __init__(self):
    """ simple square pars """
    self.SNK_DATAWIDTH=32
    self.SRC_DATAWIDTH=32+32
  def __call__(self, pars):
    self.SNK_DATAWIDTH   = pars.SNK_DATAWIDTH
    self.SRC_DATAWIDTH   = pars.SRC_DATAWIDTH

class StreamingSimpleSquare():
  """ StreamingSimpleSquare Top """
  def __init__(self):
    pass

  def block_connect(pars, reset, clk, av_snk, av_src):
    """ streaming_simple square block"""

  data_enable_o=Signal(bool(0))

  av_snk_if = AvalonST_SNK(pars.SNK_DATAWIDTH)
  av_src_if = AvalonST_SRC(pars.SRC_DATAWIDTH)


  @always_comb
  def signal_assignments():
    av_snk_if.valid_i.next=av_snk.valid_i
    av_snk.ready_o.next=av_snk_if.ready_o
    
    av_src.valid_o.next=av_src_if.valid_o
    av_src_if.ready_i.next=av_src.ready_i
    

  streaming_ip_a_inst = streaming_ip_a(reset, clk, av_snk_if, av_src_if, data_enable_o )

  @always(clk.posedge, reset.posedge)
  def streaming_simple_square():
    """ streaming_simple square """
    if reset==1:
      av_src.startofpacket_o.next = 0
      av_src.endofpacket_o.next = 0
      av_src.data_o.next = 0
      av_src.channel_o.next = 0
    elif data_enable_o == 1:
      av_src.startofpacket_o.next = av_snk.startofpacket_i  
      av_src.data_o.next = av_snk.data_i * av_snk.data_i
      av_src.endofpacket_o.next = av_snk.endofpacket_i 
      av_src.channel_o.next = av_snk.channel_i
