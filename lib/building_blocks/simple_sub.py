import myhdl

class SimpleSubPars():
  def __init__(self):
    """ simple sub pars """
    self.IN1_SYMBOL_WIDTH=32
    self.IN2_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=32
  def __call__(self, pars):
    self.IN1_SYMBOL_WIDTH      = pars.IN1_SYMBOL_WIDTH
    self.IN2_SYMBOL_WIDTH      = pars.IN2_SYMBOL_WIDTH
    if (self.IN1_SYMBOL_WIDTH >  self.IN2_SYMBOL_WIDTH):
      self.OP_SYMBOL_WIDTH = self.IN1_SYMBOL_WIDTH 
    else:
      self.OP_SYMBOL_WIDTH = self.IN2_SYMBOL_WIDTH

class SimpleSubIo():
  """ simple sub Interface Signals """
  def __init__(self,par):
    self.in1_i  = Signal(intbv(0)[par.IN1_SYMBOL_WIDTH:])
    self.in2_i  = Signal(intbv(0)[par.IN2_SYMBOL_WIDTH:])
    self.op_o   = Signal(intbv(0)[par.OP_SYMBOL_WIDTH:])


class SimpleSub():
  """ SimpleSub Top """
  def __init__(self):
    pass


  def block_connect(pars, reset, clk, simple_sub_io):
    """ simple sub lib"""
    @always(clk.posedge, reset.posedge)
    def subtract():
      """ simple subtract """
      if (reset == 1):
        simple_sub_io.op_o.next = 0
      else:
        simple_sub_io.op_o.next = simple_sub_io.in1_i -  simple_sub_io.in2_i
   
