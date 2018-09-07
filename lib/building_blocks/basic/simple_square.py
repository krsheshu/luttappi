import myhdl

class SimpleSquarePars():
  def __init__(self):
    """ simple square pars """
    self.IN1_SYMBOL_WIDTH=32
    self.IN2_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=64
  def __call__(self, pars):
    self.IN1_SYMBOL_WIDTH       = pars.IN1_SYMBOL_WIDTH
    self.IN2_SYMBOL_WIDTH       = pars.IN2_SYMBOL_WIDTH
    self.OP_SYMBOL_WIDTH        = self.IN1_SYMBOL_WIDTH + self.IN2_SYMBOL_WIDTH 


class SimpleSquareIo():
  """ simple square Interface Signals """
  def __init__(self,pars):
    self.in1_i  = Signal(intbv(0)[pars.IN1_SYMBOL_WIDTH:])
    self.in2_i  = Signal(intbv(0)[pars.IN2_SYMBOL_WIDTH:])
    self.op_o   = Signal(intbv(0)[pars.OP_SYMBOL_WIDTH:])


class SimpleSquare():
  """ SimpleSquare Top """
  def __init__(self):
    pass

  def block_connect(pars, reset, clk, simple_square_io):
    """ simple square block"""
    square = Signal(intbv(0)[par.OP_SYMBOL_WIDTH+1:]
    
    @always(clk.posedge, reset.posedge)
    def square():
      """ output block  without LuTs """
      if (reset == 1):
        simple_square_io.op_o.next = 0
      else:
        simple_square_io.op_o.next= simple_square_io.in1_i * simple_square_io.in2_i
   
