#!/usr/bin/python3 

from myhdl import Signal, intbv, toVerilog, instances, always_comb, block

class stimulus():
  def __init__(self):
    self.data = Signal(bool(0))
    self.valid  = Signal(bool(0))
          
  def __call__(self,data,valid):
     self.data = Signal(bool(data))
     self.valid= Signal(bool(valid))

def block_connect(inpa):
  shift=Signal(bool(0))  
  
  @always_comb
  def shift2_process():
    shift.next = 1 if  (inpa.valid == 1) else 0
  pass

def test_top(inpa):
  shift=Signal(bool(0))  
  
  @always_comb
  def shift_process():
    shift.next = 1 if  (inpa.valid == 1) else 0

  inpConnect=block_connect(inpa)

  return instances()

if __name__ == '__main__':
  inpa=stimulus()
  inpa(1,1)
  toVerilog(test_top,inpa)
