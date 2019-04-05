#!/usr/bin/python3 

from myhdl import Signal, intbv, toVerilog, instances, always_comb

def conditional_wire_assign(dout, condition, din1, din2):
  @always_comb
  def conditional_wire_assign_process():
    dout.next = din1 if (condition == 1) else din2
  return instances() 

class stimulus():
  def __init__(self):
    self.data = Signal(intbv(0)[32:])
    self.valid  = Signal(bool(0))
          
class mainblk():
  def block_connect(self,reset,clk,inpa):
    shift2=Signal(bool(1)) 
    op=stimulus() 
    
    valid=(conditional_wire_assign(op.valid, shift2, inpa.valid, 0)) 
    data=(conditional_wire_assign(op.data, shift2, inpa.data, 0)) 
  
    return instances()

class testblk():
  def test_top(self,reset,clk,inpa):
    shift1=Signal(bool(0))  
    
    @always_comb
    def shift1_process():
      shift1.next = 1 if  (inpa.valid == 1) else 0
   
    testMain=mainblk()
    inpConnect=(testMain.block_connect(reset, clk, inpa))
  
    return instances()

if __name__ == "__main__": 
  reset = Signal(bool(0))
  clk = Signal(bool(0))
  stim=stimulus()
  testMod=testblk()
  
  toVerilog(testMod.test_top,reset,clk,stim)
