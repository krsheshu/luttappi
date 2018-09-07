import myhdl

class SimpleLoadPars():
  def __init__(self):
    """ simple load pars """
    self.IP_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=32
  def __call__(self,pars):
    self.IN_SYMBOL_WIDTH  = pars.IN_SYMBOL_WIDTH 
    self.OP_SYMBOL_WIDTH  = pars.IN_SYMBOL_WIDTH 

class SimpleLoadIo():
  """ simple load Interface Signals """
  def __init__(self,pars):
    self.in_i     = Signal(intbv(0)[pars.IN_SYMBOL_WIDTH:])
    self.load_i   = Signal(intbv(0))
    self.op_o     = Signal(intbv(0)[pars.OP_SYMBOL_WIDTH:])

class SimpleLoad():
  """ SimpleLoad Top """
  def __init__(self):
    pass
  
  def block_connect(pars, reset, clk, simple_load_io):
    """ simple load block"""
    @always(clk.posedge, reset.posedge)
    def load():
      """ simple load """
      if (reset == 1):
        simple_load_io.op_o.next = 0
      elif (simple_load_io.load == 1):
        simple_load_io.op_o.next = simple_load_io.in_i
   
