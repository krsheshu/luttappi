#----Accumulator Class 

#----imports
from myhdl import always, always_comb, Signal, instances, block,intbv
from avalon_buses import PipelineST
from common_functions import conditional_reg_assign,CLogB2, simple_wire_assign, simple_reg_assign

#---- Class description
#----Parameters for operandPipeline Class
class AccumulatorPars(): 
  def __init__(self):
    """ Initialize Accumulator parameters """
    self.DATAWIDTH          = 32 
    self.CHANNEL_WIDTH      = 1
    self.INIT_DATA          = 0
    self.NB_ACCUMULATIONS   = 3
  
  def __call__(self,pars):
    """ Overwrite Accumulator parameters """
    self.DATAWIDTH          = pars.DATAWIDTH
    self.CHANNEL_WIDTH      = pars.CHANNEL_WIDTH
    self.INIT_DATA          = pars.INIT_DATA
    self.NB_ACCUMULATIONS   = pars.NB_ACCUMULATIONS


#-----Class Description
class Accumulator():
  
  def __init__(self):
    """ Accumulator Init"""
    self.DATAWIDTH = 32
    self.CHANNEL_WIDTH= 1
    self.INIT_DATA=0
    
    self.accu= PipelineST(self.DATAWIDTH,self.CHANNEL_WIDTH,self.INIT_DATA)

  def __call__(self,pars):
    """ Overwrite Accumulator Ios """
    self.accu= PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)
  
  #@block 
  def block_connect(self, pars, reset, clk, reset_acc, pipe_in, pipe_out):
    """ Accumulator block """
   
    # Reset value to incorporate float and intbv formats
    zero = 0.0 if (isinstance(pars.INIT_DATA,float)) else 0
    
    acc_cnt=Signal(intbv(0)[CLogB2(pars.NB_ACCUMULATIONS):])
    acc_valid = Signal(bool(0))
    
    # Counter to count nb accumulations 
    @always(clk.posedge, reset.posedge)
    def acc_cnt_process():
      if reset:  # Synchronous reset_acc
        acc_cnt.next = 0
      elif reset_acc: 
        acc_cnt.next = 0
      elif (pipe_in.valid == 1):
        if(acc_cnt == (pars.NB_ACCUMULATIONS-1)):
          acc_cnt.next = 0
        else:
          acc_cnt.next = acc_cnt + 1
      else:
        acc_cnt.next = acc_cnt
 
    # Accumulate data when valid data present till valid nb counts 
    @always(clk.posedge, reset.posedge)
    def accumulator_process():
      if reset:  # Synchronous reset_acc
        self.accu.data.next = zero
      elif reset_acc: 
        self.accu.data.next = zero
      elif (pipe_in.valid == 1):
        if (acc_cnt == 0):  # If valid, accumulate data
          self.accu.data.next = pipe_in.data 
        else: 
          self.accu.data.next = self.accu.data + pipe_in.data
      else:
          self.accu.data.next = self.accu.data 
      
    # Accumulate Valid Signal
    @always(clk.posedge, reset.posedge)
    def acc_valid_process():
      if reset:
        acc_valid.next = 0
      elif reset_acc:
        acc_valid.next = 0
      elif (pipe_in.valid == 1 and acc_cnt == pars.NB_ACCUMULATIONS-1):
          acc_valid.next = 1
      else:
          acc_valid.next = 0
     

    """ Output pipesrc instance """
    data_out_inst   = simple_wire_assign(pipe_out.data, self.accu.data)
    sop_out_inst    = conditional_reg_assign(reset, clk, pipe_out.sop, 0, pipe_in.valid, pipe_in.sop)
    eop_out_inst    = conditional_reg_assign(reset, clk, pipe_out.eop, 0, pipe_in.valid, pipe_in.eop)
    valid_out_inst  = simple_wire_assign(pipe_out.valid, acc_valid)
    channel_out_inst  = conditional_reg_assign(reset, clk, pipe_out.channel, 0, pipe_in.valid, pipe_in.channel)

     
    return instances() 
  
  def validate(self, ipFile, opFile):
    """ Validation block """
    pass
