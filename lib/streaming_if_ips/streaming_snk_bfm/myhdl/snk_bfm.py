from myhdl import always, always_comb, always_seq, Signal, ResetSignal, intbv, concat
from array import *

def snk_bfm(  reset, clk, ready_i_pattern, av_snk, av_src ):


  shift=Signal(intbv(ready_i_pattern)[16:])
  data = Signal(intbv(0)[len(av_snk.data_i):])
  en_shift = 1

  class num_counter:
    nb = 0

  #For Generating asi_st2_ready_o logic
  #Generating ready_o according to shift register pattern 15th bit
  @always_comb
  def beh_o_logic():
    if reset==1:
      av_snk.ready_o.next = 0
    elif shift[15] == 1:
      av_snk.ready_o.next = 1
    else:
      av_snk.ready_o.next = 0

  #Circular Shifter for ready_o
  @always(clk.posedge, reset.posedge)
  def beh_shift():
    if reset==1:
      shift.next=0
    if en_shift == 1:
      shift.next[16:] = concat(shift[15:0], shift[15])


  #print "Captured data at snk bfm:"
  #Capturing data on snk bfm
  @always(clk.posedge, reset.posedge)
  def beh_data_capture():
    if reset==1:
      av_src.data_o.next=0
      av_src.valid_o.next=0
      data.next=0
      av_src.startofpacket_o.next=0
      av_src.endofpacket_o.next=0
    if (av_snk.valid_i == 1) and (av_snk.ready_o == 1):
      av_src.data_o.next = av_snk.data_i
      av_src.valid_o.next=1
      av_src.startofpacket_o.next=av_snk.startofpacket_i
      av_src.endofpacket_o.next=av_snk.endofpacket_i
      data.next = av_snk.data_i
      num_counter.nb+=1
      #print str(num_counter.nb)+". SnkBfm: received data:", data.next, ": ", data.next
    else:
      av_src.valid_o.next=0


  return beh_o_logic, beh_shift, beh_data_capture
