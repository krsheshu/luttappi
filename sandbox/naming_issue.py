#!/usr/bin/python3 

from myhdl import Signal, intbv, toVerilog, instances, always_comb, block

class stimulus():
  def __init__(self):
    self.data = Signal(intbv(0)[32:])
    self.valid  = Signal(bool(0))
          
  def __call__(self,data,valid):
     self.data = Signal(intbv(data)[32:])
     self.valid= Signal(bool(valid))

class pipe():
  def __init__(self):
    self.pipeInp=stimulus()
  def __call__(self,stim):
    self.pipeInp=stim

class mainblk():
  def block_connect(self,inpa):
    shift2=Signal(bool(0))  
    
    @always_comb
    def shift2_process():
      shift2.next = 1 if  (inpa.valid == 1) else 0
  
    return instances()

class testblk():
  def test_top(self,inpa):
    shift1=Signal(bool(0))  
    
    @always_comb
    def shift1_process():
      shift1.next = 1 if  (inpa.valid == 1) else 0
   
    testMain=mainblk()
    inpConnect=(testMain.block_connect(inpa))
  
    return instances()

if __name__ == '__main__':
  stim=stimulus()
  stim(100,1)
  pipe_I=pipe()
  pipe_I(stim)
  testMod=testblk()
  filename= "lr_top"
  toVerilog.name= filename 
  toVerilog(testMod.test_top,pipe_I.pipeInp)
