import myhdl

from simple_adder import SimpleAdderPars, SimpleAdderIo, SimpleAdder 

from avalon_buses import AvalonST_SNK, AvalonST_SRC
from streaming_ip_a import streaming_ip_a_top


class StreamingSimpleAdderPars():
  def __init__(self):
    """ simple add pars """
    self.STREAMING_IF_A_INP_ENABLE=1
    self.STREAMING_IF_B_INP_ENABLE=1
    self.STREAMING_IF_A_OP_ENABLE=1
    self.STREAMING_IF_B_OP_ENABLE=1
    
    self.simple_adder_pars=SimpleAdderPars()

  def __call__(self, pars):
    
    self.STREAMING_IF_A_INP_ENABLE=pars.STREAMING_IF_A_INP_ENABLE
    self.STREAMING_IF_B_INP_ENABLE=pars.STREAMING_IF_B_INP_ENABLE
    self.STREAMING_IF_A_OP_ENABLE=pars.STREAMING_IF_A_OP_ENABLE
    self.STREAMING_IF_B_OP_ENABLE=pars.STREAMING_IF_B_OP_ENABLE

    self.simple_adder_pars(pars.simple_adder_pars)


class StreamingSimpleAdderIo():
  """ simple add Interface Signals """
  def __init__(self,pars):
    self.simple_adder_io=SimpleAdderIo(pars.simple_adder_pars)


class StreamingSimpleAdder():
  """ SimpleAdder Top """
  def __init__(self):
    pass

  def block_connect(self, pars, reset, clk, simple_add_io):
    """ simple adder block"""
    
    """ Configuring the inp and op streaming ifs """
    if (pars.STREAMING_IF_A_INP_ENABLE==1):
      streaming_ip_a_top_inst = streaming_ip_a_top(reset, clk, av_snk, av_src) 

    elif (pars.STREAMING_IF_B_INP_ENABLE==1):
      streaming_ip_a_top_inst = streaming_ip_a_top(reset, clk, av_snk, av_src) 

    elif (pars.STREAMING_IF_A_OP_ENABLE==1):
      streaming_ip_a_top_inst = streaming_ip_a_top(reset, clk, av_snk, av_src) 

    elif (pars.STREAMING_IF_B_OP_ENABLE==1):
      streaming_ip_a_top_inst = streaming_ip_a_top(reset, clk, av_snk, av_src) 
    

    
   
