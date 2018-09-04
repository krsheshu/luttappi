import myhdl

class simple_load_pars():
  def __init__(self):
    """ simple load pars """
    self.IP_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=32
  def __call__(self,width_1=None,width_2=None):
    if(width_1 != None):
      self.IN_SYMBOL_WIDTH      = width_1 
    self.OP_SYMBOL_WIDTH = self.IN_SYMBOL_WIDTH 

class simple_load_io():
  """ simple load Interface Signals """
  def __init__(self,par):
    self.in_i     = Signal(intbv(0)[par.IN_SYMBOL_WIDTH:])
    self.load_i   = Signal(intbv(0))
    self.op_o     = Signal(intbv(0)[par.OP_SYMBOL_WIDTH:])

def simple_load(pars, reset, clk, simple_load_io):
  """ simple load lib"""

  @always(clk.posedge, reset.posedge)
  def load():
  """ simple load """
    if (reset == 1):
      simple_load_io.op_o.next = 0
    elif (self.load == 1):
      simple_load_io.op_o.next = simple_load_io.in_i
   
