#----Activation Class 

#----imports
from myhdl import always, always_comb, Signal, instances, block,intbv
from avalon_buses import PipelineST
from common_functions import conditional_reg_assign,CLogB2, simple_wire_assign, simple_reg_assign

#---- Class description
#----Parameters for Activation Class
class ActivationPars(): 
  def __init__(self):
    """ Initialize Activation parameters """
    self.DATAWIDTH          = 1 
    self.CHANNEL_WIDTH      = 2
    self.INIT_DATA          = 0
  
  def __call__(self,pars):
    """ Overwrite Activation parameters """
    self.DATAWIDTH          = pars.DATAWIDTH
    self.CHANNEL_WIDTH      = pars.CHANNEL_WIDTH
    self.INIT_DATA          = pars.INIT_DATA


#-----Class Description
class Activation():
  
  def __init__(self):
    """ Activation Init"""
    self.DATAWIDTH = 2
    self.CHANNEL_WIDTH= 1
    self.INIT_DATA=0
    
    self.classifier= PipelineST(self.DATAWIDTH,self.CHANNEL_WIDTH,self.INIT_DATA)

  def __call__(self,pars):
    """ Overwrite Activation Ios """
    self.classifier= PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)
  
  # Use simple step activation function. if x <= 0, prob=0 else prob=1
  #@block 
  def block_step_connect(self, pars, reset, clk, pipe_in, pipe_out):
    """ Activation block """
   
    # Reset value to incorporate float and intbv formats
    zero = 0.0 if (isinstance(pars.INIT_DATA,float)) else 0
    one = 1.0 if (isinstance(pars.INIT_DATA,float)) else 1
    
    # Simple Step Activation Function 
    @always(clk.posedge, reset.posedge)
    def activation_process():
      if reset:  # Synchronous reset_acc
        self.classifier.data.next = zero
      elif (pipe_in.valid == 1):
        # if data > 0, prob= 1 else 0
        self.classifier.data.next = one if (pipe_in.data > zero) else zero
       

    """ Output pipesrc instance """
    data= simple_wire_assign(pipe_out.data, self.classifier.data)
    sop= conditional_reg_assign(reset, clk, pipe_out.sop, 0, pipe_in.valid, pipe_in.sop)
    eop= conditional_reg_assign(reset, clk, pipe_out.eop, 0, pipe_in.valid, pipe_in.eop)
    valid= simple_reg_assign(reset, clk, pipe_out.valid, 0, pipe_in.valid)
    channel= simple_reg_assign(reset, clk, pipe_out.channel, 0, pipe_in.channel)

     
    return instances() 
  
  def validate(self, ipFile, opFile):
    """ Validation block """
    pass
