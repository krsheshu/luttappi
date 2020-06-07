import myhdl
from avalon_buses import AvalonST_SNK, AvalonST_SRC
from streaming_ip_a import streaming_ip_a_top

class StreamingSimpleLoadPars():
  def __init__(self):
    """ simple load pars """
    self.SNK_DATAWIDTH=32
    self.SRC_DATAWIDTH=32
  def __call__(self, pars):
    self.SNK_DATAWIDTH   = pars.SNK_DATAWIDTH
    self.SRC_DATAWIDTH   = pars.SRC_DATAWIDTH

class StreamingSimpleLoad():
  """ StreamingSimpleLoad Top """
  def __init__(self):
    pass

  def block_connect(pars, reset, clk, av_snk, av_src ):
    """ simple load block"""

    av_snk_if = AvalonST_SNK(pars.SNK_DATAWIDTH)
    av_src_if = AvalonST_SRC(pars.SRC_DATAWIDTH)

    @always_comb
    def signal_assignments():
      av_snk_if.valid_i.next=av_snk.valid_i
      av_snk.ready_o.next=av_snk_if.ready_o

      av_src.valid_o.next=av_src_if.valid_o
      av_src_if.ready_i.next=av_src.ready_i


    streaming_ip_a_top_inst = streaming_ip_a_top(reset, clk, av_snk_if, av_src_if)

