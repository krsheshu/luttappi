import myhdl

class SimpleAdderPars():
  def __init__(self):
    """ simple add pars """
    self.IN1_SYMBOL_WIDTH=32
    self.IN2_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=33
  def __call__(self, pars):
    self.IN1_SYMBOL_WIDTH      = pars.IN1_SYMBOL_WIDTH
    self.IN2_SYMBOL_WIDTH      = pars.IN2_SYMBOL_WIDTH
    if (self.IN1_SYMBOL_WIDTH >  self.IN2_SYMBOL_WIDTH):
      self.OP_SYMBOL_WIDTH = self.IN1_SYMBOL_WIDTH + 1
    else:
      self.OP_SYMBOL_WIDTH = self.IN2_SYMBOL_WIDTH + 1

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

  def block_connect(pars, reset, clk, simple_add_io):
    """ simple adder block"""
    @always(clk.posedge, reset.posedge)
    def adder():
      """ simple adder """
      if (reset == 1):
        simple_add_io.op_o.next = 0
      else:
        simple_add_io.op_o.next = simple_add_io.in1_i +  simple_add_io.in2_i
   
