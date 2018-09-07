import myhdl
from avalon_buses import AvalonST_SNK, AvalonST_SRC

class SimpleAdderPars():
  def __init__(self):
    """ simple add pars """
    self.IN1_SYMBOL_WIDTH=32
    self.IN2_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=32
  def __call__(self, pars):
    self.IN1_SYMBOL_WIDTH   = pars.IN1_SYMBOL_WIDTH
    self.IN2_SYMBOL_WIDTH   = pars.IN2_SYMBOL_WIDTH
    self.OP_SYMBOL_WIDTH    = pars.OP_SYMBOL_WIDTH

class SimpleAdderIo():
  """ simple add Interface Signals """
  def __init__(self,pars):
    self.in1_i  = Signal(intbv(0)[pars.IN1_SYMBOL_WIDTH:])
    self.in2_i  = Signal(intbv(0)[pars.IN2_SYMBOL_WIDTH:])
    self.op_o   = Signal(intbv(0)[pars.OP_SYMBOL_WIDTH:])


class SimpleAdder():
  """ SimpleAdder Top """
  def __init__(self):
    pass

  def block_connect(pars, reset, clk, av_snk0, av_snk1, av_src, data_enable_o):
    """ simple adder block"""
    @always(clk.posedge, reset.posedge)
    def adder():
      """ simple adder """
      if (reset == 1):
        av_src.data_o.next = 0
        av_snk0.ready_o.next = 0 
        av_snk1.ready_o.next = 0 
      elif (av_snk0.valid_i == 1 and av_snk1.valid_i == 1 and av_src.ready_i == 1):
        av_src.data_o.next = av_snk0.data_i + av_snk1.data_i
        av_src.valid_o.next = 1
        av_snk0.ready_o.next = 1 
        av_snk1.ready_o.next = 1 
   
    @always_comb
    def output_gen_wires():
      av_src.valid_o.next = src_valid
      av_snk0.ready_o.next = snk_ready 
      av_snk1.ready_o.next = snk_ready 
    
    #Registering valid
    @always(clk.posedge, reset.posedge)
    def src_valid_reg_process():
      if reset==1:
        src_valid.next = 0
      elif av_snk0.valid_i == 1 and av_snk1.valid_i== 1 and av_src.ready_i == 1:
        src_valid.next = 1
      elif (av_snk0.valid_i == 0 or av_snk1.valid_i == 0) and av_src.ready_i == 1 and src_valid == 1:
        src_valid.next = 0
      elif av_snk0.valid_i == 1 and av_snk1.valid_i== 1 and av_src.ready_i == 0 and src_valid == 0:
        src_valid.next = 1
    
    @always_comb
    def snk_ready_process():
      if (src_valid == 1 and av_src.ready_i == 0):
        snk_ready.next = 0 
      elif ( av_snk0.valid_i == 1 and av_snk1.valid_i== 1):
        snk_ready.next = 1
      else: 
        snk_ready.next = 0 
    
    #Dataenable as output
    @always_comb
    def data_enable_process():
      if reset==1:
        data_enable_o.next = 0
      elif snk_ready == 1 and av_snk0.valid_i == 1 and av_snk1.valid_i == 1:
        data_enable_o.next = 1
      else:
        data_enable_o.next = 0
  
