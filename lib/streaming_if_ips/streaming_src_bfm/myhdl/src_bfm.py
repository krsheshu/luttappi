from myhdl import always, always_comb, always_seq, Signal, ResetSignal, intbv, concat, instances
from array import *

def src_bfm(  reset, clk, valid_i_pattern, src_bfm_i, av_src ):


  en_shift_vld=Signal(bool(0))
  shift_vld_pattern=Signal(intbv(valid_i_pattern)[16:])
  class num_counter:
    nb = 0
  # For Generating src_bfm_aso_valid_o
  #Generating valid_o according to shift_vld register pattern 15th bit
  @always_comb
  def beh_valid_o_logic():
    if reset==1:
      av_src.valid_o.next = 0
    elif shift_vld_pattern[15] == 1 and src_bfm_i.valid_i == 1:
      av_src.valid_o.next = 1
    else:
      av_src.valid_o.next = 0

  #Printing the src bfm data
  @always(clk.posedge)
  def print_bfm_op():
    if av_src.valid_o == 1 and av_src.ready_i == 1:
      num_counter.nb+=1
      #print str(num_counter.nb) + ". SrcBfm: transmitted data:", av_src.data_o

  #Generating condition when  to start shift_vld
  @always_comb
  def beh_shift_vld_en_valid():
    if reset==1:
      en_shift_vld.next=0
    elif (av_src.ready_i == 1 and av_src.valid_o == 1) or (shift_vld_pattern[15] == 0):
      en_shift_vld.next = 1
    else:
      en_shift_vld.next = 0

  #Circular Shifter
  @always(clk.posedge, reset.posedge)
  def beh_shift_vld_pattern():
    if en_shift_vld == 1:
      shift_vld_pattern.next[16:] = concat(shift_vld_pattern[15:0], shift_vld_pattern[15])

  @always_comb
  def beh_data_o():
    if reset==1:
      av_src.data_o.next = 0
      av_src.startofpacket_o.next = 0
      av_src.endofpacket_o.next = 0
    elif av_src.valid_o == 1:
      av_src.data_o.next = src_bfm_i.data_i
      av_src.startofpacket_o.next = src_bfm_i.startofpacket_i
      av_src.endofpacket_o.next = src_bfm_i.endofpacket_i
    else:
      av_src.data_o.next = 0
      av_src.startofpacket_o.next = 0
      av_src.endofpacket_o.next = 0

  return instances()
