import myhdl

class simple_modsub_pars():
  def __init__(self):
    """ simple modsub pars """
    self.IN1_SYMBOL_WIDTH=32
    self.IN2_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=32
  def __call__(self,width_1=None,width_2=None):
    if(width_1 != None):
      self.IN1_SYMBOL_WIDTH      = width_1 
    if(width_2 != None):
      self.IN2_SYMBOL_WIDTH      = width_2
    if (self.IN1_SYMBOL_WIDTH >  self.IN2_SYMBOL_WIDTH):
      self.OP_SYMBOL_WIDTH = self.IN1_SYMBOL_WIDTH  
    else:
      self.OP_SYMBOL_WIDTH = self.IN2_SYMBOL_WIDTH 

class simple_modsub_io():
  """ simple modsub Interface Signals """
  def __init__(self,par):
    self.in1  = Signal(intbv(0)[par.IN1_SYMBOL_WIDTH:])
    self.in2  = Signal(intbv(0)[par.IN2_SYMBOL_WIDTH:])
    self.op   = Signal(intbv(0)[par.OP_SYMBOL_WIDTH:])

def simple_modsub(pars, reset, clk, simple_modsub_io):
  """ simple modsub lib"""

  modsub = Signal(intbv(0)[par.OP_SYMBOL_WIDTH+1:]
  
  @always(clk.posedge, reset.posedge)
  def modsubtract():
  """ output block """
    if (reset == 1):
      simple_modsub_io.op.next = 0
    else:
      simple_modsub_io.op.next = modsub[self.OP_SYMBOL_WIDTH:]
   
  @always(clk.posedge, reset.posedge)
  def modsubtract():
  """ simple modsubtract """
    if (reset == 1):
      modsub.next = 0
    else:
      modsub.next = simple_modsub_io.in1 - simple_modsub_io.in2
   
