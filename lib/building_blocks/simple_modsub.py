import myhdl

class SimpleModSubPars():
  def __init__(self):
    """ simple modsub pars """
    self.IN1_SYMBOL_WIDTH=32
    self.IN2_SYMBOL_WIDTH=32
    self.OP_SYMBOL_WIDTH=32
  def __call__(self,pars):
    self.IN1_SYMBOL_WIDTH      = pars.IN1_SYMBOL_WIDTH
    self.IN2_SYMBOL_WIDTH      = pars.IN2_SYMBOL_WIDTH
    if (self.IN1_SYMBOL_WIDTH >  self.IN2_SYMBOL_WIDTH):
      self.OP_SYMBOL_WIDTH = self.IN1_SYMBOL_WIDTH 
    else:
      self.OP_SYMBOL_WIDTH = self.IN2_SYMBOL_WIDTH 

class SimpleModSubIo():
  """ simple modsub Interface Signals """
  def __init__(self,pars):
    self.in1_i  = Signal(intbv(0)[pars.IN1_SYMBOL_WIDTH:])
    self.in2_i  = Signal(intbv(0)[pars.IN2_SYMBOL_WIDTH:])
    self.op_o   = Signal(intbv(0)[pars.OP_SYMBOL_WIDTH:])

class SimpleModSub():
  """ SimpleModSub Top """
  def __init__(self):
    pass

  def block_connect(pars, reset, clk, simple_modsub_io):
    """ simple modsub block"""
    modsub = Signal(intbv(0)[pars.OP_SYMBOL_WIDTH+1:]
    
    @always(clk.posedge, reset.posedge)
    def modsubtract():
      """ output block """
      if (reset == 1):
        simple_modsub_io.op_o.next = 0
      else:
        simple_modsub_io.op_o.next = modsub[pars.OP_SYMBOL_WIDTH:]
     
    @always(clk.posedge, reset.posedge)
    def modsubtract():
      """ simple modsubtract """
      if (reset == 1):
        modsub.next = 0
      else:
        modsub.next = simple_modsub_io.in1_i - simple_modsub_io.in2_i
   
