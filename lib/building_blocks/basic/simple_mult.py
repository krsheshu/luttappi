import myhdl

class SimpleMultPars():
  def __init__(self):
    """ simple mult pars """
    self.IN1_SYMBOL_WIDTH=32
    self.IN2_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=32+32
  def __call__(self, pars):
    self.IN1_SYMBOL_WIDTH       = pars.IN1_SYMBOL_WIDTH
    self.IN2_SYMBOL_WIDTH       = pars.IN2_SYMBOL_WIDTH
    self.OP_SYMBOL_WIDTH        = self.IN1_SYMBOL_WIDTH + self.IN2_SYMBOL_WIDTH

class SimpleMultIo():
  """ simple mult Interface Signals """
  def __init__(self,pars):
    self.in1_i  = Signal(intbv(0)[pars.IN1_SYMBOL_WIDTH:])
    self.in2_i  = Signal(intbv(0)[pars.IN2_SYMBOL_WIDTH:])
    self.op_o   = Signal(intbv(0)[pars.OP_SYMBOL_WIDTH:])

class SimpleMult():
  """ SimpleMult Top """
  def __init__(self):
    pass
  
  def block_connect(pars, reset, clk, simple_mult_io):
    """ simple mult block"""
    @always(clk.posedge, reset.posedge)
    def multiplier():
      """ simple multiplier """
      if (reset == 1):
        simple_mult_io.op_o.next = 0
      else:
        simple_mult_io.op_o.next = simple_mult_io.in1_i *  simple_mult_io.in2_i
   
