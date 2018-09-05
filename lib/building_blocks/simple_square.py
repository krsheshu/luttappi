import myhdl

class SimpleSquare():

  class Pars():
    def __init__(self):
      """ simple square pars """
      self.IN1_SYMBOL_WIDTH=32
      self.IN2_SYMBOL_WIDTH=32
      self.OP_SYMBOL_WIDTH=64
    def __call__(self,width_1=None,width_2=None):
      if(width_1 != None):
        self.IN1_SYMBOL_WIDTH      = width_1 
      if(width_2 != None):
        self.IN2_SYMBOL_WIDTH      = width_2
      self.OP_SYMBOL_WIDTH = self.IN1_SYMBOL_WIDTH + self.IN2_SYMBOL_WIDTH 

  class Io():
    """ simple square Interface Signals """
    def __init__(self,par):
      self.in1_i  = Signal(intbv(0)[par.IN1_SYMBOL_WIDTH:])
      self.in2_i  = Signal(intbv(0)[par.IN2_SYMBOL_WIDTH:])
      self.op_o   = Signal(intbv(0)[par.OP_SYMBOL_WIDTH:])

  def block(pars, reset, clk, simple_square_io):
    """ simple square block"""
 
    square = Signal(intbv(0)[par.OP_SYMBOL_WIDTH+1:]
    
    @always(clk.posedge, reset.posedge)
    def square():
    """ output block  without LuTs """
      if (reset == 1):
        simple_square_io.op_o.next = 0
      else:
        simple_square_io.op_o.next= simple_square_io.in1_i * simple_square_io.in2_i
   
