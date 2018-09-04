import myhdl

class simple_mult_pars():
  def __init__(self):
    """ simple mult pars """
    self.IN1_SYMBOL_WIDTH=32
    self.IN2_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=32+32
  def __call__(self,width_1=None,width_2=None):
    if(width_1 != None):
      self.IN1_SYMBOL_WIDTH      = width_1 
    if(width_2 != None):
      self.IN2_SYMBOL_WIDTH      = width_2
    self.OP_SYMBOL_WIDTH = self.IN1_SYMBOL_WIDTH + self.IN2_SYMBOL_WIDTH

class simple_mult_io():
  """ simple mult Interface Signals """
  def __init__(self,par):
    self.in1_i  = Signal(intbv(0)[par.IN1_SYMBOL_WIDTH:])
    self.in2_i  = Signal(intbv(0)[par.IN2_SYMBOL_WIDTH:])
    self.op_o   = Signal(intbv(0)[par.OP_SYMBOL_WIDTH:])

def simple_mult(pars, reset, clk, simple_mult_io):
  """ simple mult lib"""

  @always(clk.posedge, reset.posedge)
  def multiplier():
  """ simple multiplier """
    if (reset == 1):
      simple_mult_io.op_o.next = 0
    else:
      simple_mult_io.op_o.next = simple_mult_io.in1_i *  simple_mult_io.in2_i
   
