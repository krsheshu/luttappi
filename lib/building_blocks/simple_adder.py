import myhdl

class simple_add_pars():
  def __init__(self):
    """ simple add pars """
    self.IN1_SYMBOL_WIDTH=32
    self.IN2_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=33
  def __call__(self,width_1=None,width_2=None):
    if(width_1 != None):
      self.IN1_SYMBOL_WIDTH      = width_1 
    if(width_2 != None):
      self.IN2_SYMBOL_WIDTH      = width_2
    if (self.IN1_SYMBOL_WIDTH >  self.IN2_SYMBOL_WIDTH):
      self.OP_SYMBOL_WIDTH = self.IN1_SYMBOL_WIDTH + 1
    else:
      self.OP_SYMBOL_WIDTH = self.IN2_SYMBOL_WIDTH + 1

class simple_add_io():
  """ simple add Interface Signals """
  def __init__(self,par):
    self.in1_i  = Signal(intbv(0)[par.IN1_SYMBOL_WIDTH:])
    self.in2_i  = Signal(intbv(0)[par.IN2_SYMBOL_WIDTH:])
    self.op_o   = Signal(intbv(0)[par.OP_SYMBOL_WIDTH:])

def simple_add(pars, reset, clk, simple_add_io):
  """ simple add lib"""

  @always(clk.posedge, reset.posedge)
  def adder():
  """ simple adder """
    if (reset == 1):
      simple_add_io.op_o.next = 0
    else:
      simple_add_io.op_o.next = simple_add_io.in1_i +  simple_add_io.in2_i
   
