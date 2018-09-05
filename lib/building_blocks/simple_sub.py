import myhdl

class SimpleSub():

  class Pars():
    def __init__(self):
      """ simple sub pars """
      self.IN1_SYMBOL_WIDTH=32
      self.IN2_SYMBOL_WIDTH=32
      self.OP_SYMBOL_WIDTH=31
    def __call__(self,width_1=None,width_2=None):
      if(width_1 != None):
        self.IN1_SYMBOL_WIDTH      = width_1 
      if(width_2 != None):
        self.IN2_SYMBOL_WIDTH      = width_2
      if (self.IN1_SYMBOL_WIDTH >  self.IN2_SYMBOL_WIDTH):
        self.OP_SYMBOL_WIDTH = self.IN1_SYMBOL_WIDTH - 1
      else:
        self.OP_SYMBOL_WIDTH = self.IN2_SYMBOL_WIDTH - 1

  class Io():
    """ simple sub Interface Signals """
    def __init__(self,par):
      self.in1_i  = Signal(intbv(0)[par.IN1_SYMBOL_WIDTH:])
      self.in2_i  = Signal(intbv(0)[par.IN2_SYMBOL_WIDTH:])
      self.op_o   = Signal(intbv(0)[par.OP_SYMBOL_WIDTH:])

  def block(pars, reset, clk, simple_sub_io):
    """ simple sub lib"""
 
    @always(clk.posedge, reset.posedge)
    def subtract():
    """ simple subtract """
      if (reset == 1):
        simple_sub_io.op_o.next = 0
      else:
        simple_sub_io.op_o.next = simple_sub_io.in1_i -  simple_sub_io.in2_i
   
