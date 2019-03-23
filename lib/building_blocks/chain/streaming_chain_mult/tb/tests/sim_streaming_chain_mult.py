import sys, os
from myhdl import Signal, delay, always,always_comb, now, Simulation, traceSignals, instances, intbv,StopSimulation
from avalon_buses import AvalonMM, AvalonST_SNK, AvalonST_SRC
from streaming_ip_a import streaming_ip_a_top
from src_bfm import src_bfm
from snk_bfm import snk_bfm
from clk_driver import clk_driver
from common_functions import simple_wire_assign, simple_reg_assign, conditional_wire_assign, conditional_clocked_appendfile, conditional_wire_assign_lt
from common_functions import CLogB2, conditional_reg_assign, conditional_clocked_append, conditional_reg_counter,Reset, conditional_random_generator

from streaming_chain_mult import StreamingChainMultPars, StreamingChainMult

import random # for randomized test
#from __future__ import print_function


MAX_SIM_TIME = 10000
MAX_NB_TRANSFERS=50

NB_CHAIN_MULTIPLIERS = 10
STREAM_DATA_WIDTH = 32
RANDRANGE=pow(2,4)-1 # Maximum value allowed is 2^15-1 for avoiding overflow
 
txdata0_filename  = [ "" for i in range(NB_CHAIN_MULTIPLIERS)]
txdata1_filename  = [ "" for i in range(NB_CHAIN_MULTIPLIERS)]
rxdata_filename   = [ "" for i in range(NB_CHAIN_MULTIPLIERS)]
ready_pulses=[Signal(int(0))  for i in range(NB_CHAIN_MULTIPLIERS)]
ready_pulses0=[Signal(int(0))  for i in range(NB_CHAIN_MULTIPLIERS)]
ready_pulses1=[Signal(int(0))  for i in range(NB_CHAIN_MULTIPLIERS)]


def sim_streaming_chain_mult(pars_obj):
  # removing the files if already available 
  for i in range(NB_CHAIN_MULTIPLIERS):
    txdata0_filename[i]="transmit_data_inpA_mult{:d}.log".format(i) 
    if (os.path.exists(txdata0_filename[i])):
      os.remove(txdata0_filename[i]) 
    txdata1_filename[i]="transmit_data_inpB_mult{:d}.log".format(i) 
    if (os.path.exists(txdata1_filename[i])):
      os.remove(txdata1_filename[i]) 
    rxdata_filename[i]="receive_data_mult{:d}.log".format(i) 
    if (os.path.exists(rxdata_filename[i])):
      os.remove(rxdata_filename[i]) 
 
  reset = Signal(bool(1))
  clk = Signal(bool(0))
  elapsed_time=Signal(0)
  
  nb_transmit=[Signal(int(0)) for i in range(NB_CHAIN_MULTIPLIERS)] 
  nb_transmit0=[Signal(int(0)) for i in range(NB_CHAIN_MULTIPLIERS)] 
  nb_transmit1=[Signal(int(0)) for i in range(NB_CHAIN_MULTIPLIERS)] 
  nb_receive=[Signal(int(0)) for i in range(NB_CHAIN_MULTIPLIERS)]  
  
  av_src0_bfm = [AvalonST_SRC(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]
  av_src1_bfm = [AvalonST_SRC(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]
  av_snk0     = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]
  av_snk1     = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]
  av_src      = [AvalonST_SRC(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]
  av_snk_bfm  = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]
  src_bfm_i   = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]
  src_bfm_0   = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]
  src_bfm_1   = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]
  src_bfm_o   = [AvalonST_SRC(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_MULTIPLIERS)]

  clkgen=clk_driver(elapsed_time,clk,period=20)

  add_i = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  src0_bfm_inst= [None for i in range(NB_CHAIN_MULTIPLIERS)]
  src1_bfm_inst= [None for i in range(NB_CHAIN_MULTIPLIERS)]
  streaming_chain_mult_inst= None
  snk_bfm_inst= [None for i in range(NB_CHAIN_MULTIPLIERS)]
  
  VALID_PATTERN0=[random.randint(0x0100,0xffff) for i in range(NB_CHAIN_MULTIPLIERS)]
  VALID_PATTERN1=[random.randint(0x0100,0xffff) for i in range(NB_CHAIN_MULTIPLIERS)]
  READY_PATTERN=[random.randint(0x0100,0xffff) for i in range(NB_CHAIN_MULTIPLIERS)]

  for i in range(NB_CHAIN_MULTIPLIERS):
    print("Chain Mult: " + str(i) + " Valid0: " +str(VALID_PATTERN0[i]) + " Valid1: " +str(VALID_PATTERN1[i]) +" Ready: " +str(READY_PATTERN[i]))
    src0_bfm_inst[i]  = src_bfm(reset, clk, VALID_PATTERN0[i], src_bfm_0[i], av_src0_bfm[i])
  
    src1_bfm_inst[i]  = src_bfm(reset, clk, VALID_PATTERN1[i], src_bfm_1[i], av_src1_bfm[i])
    
    snk_bfm_inst[i] = snk_bfm(reset, clk, READY_PATTERN[i], av_snk_bfm[i], src_bfm_o[i])
    
  add_pars=StreamingChainMultPars()
  add_pars.SNK0_DATAWIDTH=STREAM_DATA_WIDTH
  add_pars.SNK1_DATAWIDTH=STREAM_DATA_WIDTH
  add_pars.SRCD_ATAWIDTH=STREAM_DATA_WIDTH
  add_pars.NB_CHAIN_MULTIPLIERS=NB_CHAIN_MULTIPLIERS
  add_pars(add_pars)
  add_i=StreamingChainMult()
  
  streaming_chain_mult_inst = add_i.block_connect(add_pars, reset, clk, av_snk0, av_snk1, av_src)

  snk0_valid_inst = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  snk0_data_inst  = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  snk0_ready_inst = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  snk1_valid_inst = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  snk1_data_inst  = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  snk1_ready_inst = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  src_valid_inst  = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  src_data_inst   = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  src_ready_inst  = [None for i in range(NB_CHAIN_MULTIPLIERS)]
  
  for i in range(NB_CHAIN_MULTIPLIERS):
    snk0_valid_inst[i]  = simple_wire_assign(av_snk0[i].valid_i, av_src0_bfm[i].valid_o)
    snk0_data_inst[i]   = simple_wire_assign(av_snk0[i].data_i, av_src0_bfm[i].data_o)
    snk0_ready_inst[i]  = simple_wire_assign(av_src0_bfm[i].ready_i, av_snk0[i].ready_o)

    snk1_valid_inst[i]  = simple_wire_assign(av_snk1[i].valid_i, av_src1_bfm[i].valid_o)
    snk1_data_inst[i]   = simple_wire_assign(av_snk1[i].data_i, av_src1_bfm[i].data_o)
    snk1_ready_inst[i]  = simple_wire_assign(av_src1_bfm[i].ready_i, av_snk1[i].ready_o)

    src_valid_inst[i]  = simple_wire_assign(av_snk_bfm[i].valid_i, av_src[i].valid_o)
    src_data_inst[i]   = simple_wire_assign(av_snk_bfm[i].data_i, av_src[i].data_o)
    src_ready_inst[i]  = simple_wire_assign(av_src[i].ready_i, av_snk_bfm[i].ready_o)
   
  
  @always(clk.posedge)
  def stimulus():
    if elapsed_time == 40:
      reset.next = 0


  INIT_DATA0=[random.randint(1,RANDRANGE) for i in range(NB_CHAIN_MULTIPLIERS)]
  INIT_DATA1=[random.randint(1,RANDRANGE) for i in range(NB_CHAIN_MULTIPLIERS)]
  
  data_in0=[Signal(int(0)) for i in range(NB_CHAIN_MULTIPLIERS)]
  data_in1=[Signal(int(0)) for i in range(NB_CHAIN_MULTIPLIERS)]
  src_bfm_0_valid_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  src_bfm_1_valid_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  src_bfm_0_data_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  src_bfm_1_data_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  
  for i in range(NB_CHAIN_MULTIPLIERS): 
    src_bfm_0_data_inst[i]= conditional_wire_assign(src_bfm_0[i].data_i,(av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o), 
                                                        data_in0[i], src_bfm_0[i].data_i) 
    src_bfm_1_data_inst[i]= conditional_wire_assign(src_bfm_1[i].data_i,(av_src1_bfm[i].ready_i and av_src1_bfm[i].valid_o), 
                                                        data_in1[i], src_bfm_1[i].data_i) 

  for i in range(NB_CHAIN_MULTIPLIERS): 
    src_bfm_0_valid_inst[i]= conditional_wire_assign_lt(src_bfm_0[i].valid_i, nb_transmit0[i], Signal(MAX_NB_TRANSFERS), 1, 0) 
    src_bfm_1_valid_inst[i]= conditional_wire_assign_lt(src_bfm_1[i].valid_i, nb_transmit1[i], Signal(MAX_NB_TRANSFERS), 1, 0) 
 
  data_in0_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  data_in1_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  nb_transmit0_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  nb_transmit1_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  transmit_data0_append_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  transmit_data1_append_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  receive_data_append_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]

  
  #Datain is randomized values (for next valid data)
  for i in range(NB_CHAIN_MULTIPLIERS):
    data_in0_inst[i] = conditional_random_generator( reset, clk, data_in0[i], int(INIT_DATA0[i]),  
                              (av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o and src_bfm_0[i].valid_i ), RANDRANGE)       
    data_in1_inst[i] = conditional_random_generator( reset, clk, data_in1[i], int(INIT_DATA1[i]),  
                              (av_src1_bfm[i].ready_i and av_src1_bfm[i].valid_o and src_bfm_1[i].valid_i ), RANDRANGE)      
 
    nb_transmit0_inst[i] = conditional_reg_counter( reset, clk, nb_transmit0[i], Reset.LOW, 
                              (av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o and src_bfm_0[i].valid_i ))       
    nb_transmit1_inst[i] = conditional_reg_counter( reset, clk, nb_transmit1[i], Reset.LOW, 
                              (av_src1_bfm[i].ready_i and av_src1_bfm[i].valid_o and src_bfm_1[i].valid_i ))       

    transmit_data0_append_inst[i] = conditional_clocked_appendfile( reset, clk, 
                              (av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o and src_bfm_0[i].valid_i ),  
                                data_in0[i], txdata0_filename[i])
    transmit_data1_append_inst[i] = conditional_clocked_appendfile( reset, clk, 
                              (av_src1_bfm[i].ready_i and av_src1_bfm[i].valid_o and src_bfm_1[i].valid_i ),  
                                data_in1[i], txdata1_filename[i])

    receive_data_append_inst[i] = conditional_clocked_appendfile( reset, clk, 
                              (src_bfm_o[i].valid_o),  src_bfm_o[i].data_o, rxdata_filename[i])
  

 
  recv_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  for i in range(NB_CHAIN_MULTIPLIERS):
    recv_inst[i]=conditional_reg_counter(reset, clk, nb_receive[i], Reset.LOW, src_bfm_o[i].valid_o)  
 
  @always(clk.posedge)
  def receive_data_process():
    TIME_SHUTDOWN=5000
    nb_recv=0
    sim_time_now=now()
    for i in range(NB_CHAIN_MULTIPLIERS):
      nb_recv+=nb_receive[i]
    if(nb_recv == NB_CHAIN_MULTIPLIERS* (MAX_NB_TRANSFERS)): 
      for i in range(NB_CHAIN_MULTIPLIERS):
        print("INF242: mult: " +str(i)+ " Num ready pulses: "+ str(int(ready_pulses[i]))) 
      raise StopSimulation("Simulation Finished in %d clks: In total " %now() + str(nb_recv) + " data words received")  

  @always(clk.posedge)
  def simulation_time_check():
    sim_time_now=now()
    if(sim_time_now>MAX_SIM_TIME):
        raise StopSimulation("Warning! Simulation Exited upon reaching max simulation time of " + str(MAX_SIM_TIME) + " clocks")  


  ready_pulse_cnt_inst=[None for i in range(NB_CHAIN_MULTIPLIERS)]
  for i in range(NB_CHAIN_MULTIPLIERS):
    ready_pulse_cnt_inst[i]=conditional_reg_counter(reset, clk, ready_pulses[i], Reset.LOW, ( av_snk_bfm[i].ready_o) )


  return instances()


def check_simulation_results(pars_obj):
  trans_data0  = [ [] for i in range(NB_CHAIN_MULTIPLIERS)]
  trans_data1  = [ [] for i in range(NB_CHAIN_MULTIPLIERS)]
  recv_data   = [ [] for i in range(NB_CHAIN_MULTIPLIERS)]
  
  for i in range(NB_CHAIN_MULTIPLIERS):
    if (os.path.exists(txdata0_filename[i]) == False):
      print("ERR186: Error finding file!: " + txdata0_filename[i]) 
    if (os.path.exists(txdata1_filename[i]) == False):
      print("ERR186: Error finding file!: " + txdata1_filename[i]) 
    if (os.path.exists(rxdata_filename[i]) == False):
      print("ERR186: Error finding file!: " + rxdata_filename[i]) 

  for i in range(NB_CHAIN_MULTIPLIERS):
    add1 = open(txdata0_filename[i], 'r')
    add2 = open(txdata1_filename[i], 'r')
    result = open(rxdata_filename[i], 'r')
    for line in add1.readlines():
      trans_data0[i].append(int(line))
    print("INF204: Read transmit file: " + txdata0_filename[i]) 
    for line in add2.readlines():
      trans_data1[i].append(int(line))
    print("INF207: Read transmit file: " + txdata1_filename[i]) 
    for line in result.readlines():
      recv_data[i].append(int(line))
    print("INF207: Read  receive file: " + rxdata_filename[i]) 
    add1.close()
    add2.close()
    result.close()
  
  err_cnt=0
  trans_l0=0
  trans_l1=0
  #print "Received data: ", str(recv_data)
  #print "Transmitted data: ", str(trans_data[i])
  
  print("Operation intended: Chain Addition")
  
  for i in range(NB_CHAIN_MULTIPLIERS):
    trans_l0=len(trans_data0[i])
    trans_l1=len(trans_data1[i])
    if (trans_l0 != trans_l1) or (trans_l0 != MAX_NB_TRANSFERS  or trans_l1 != MAX_NB_TRANSFERS):
      print("ERR242: Transmitted data lengths does not match. Tx Len0: " + str(trans_l0) + ", Tx Len1: " + str(trans_l1) + ", Rx len: " + str(MAX_NB_TRANSFERS)+" Quitting...")
      sys.exit(2) 

  for i in range(NB_CHAIN_MULTIPLIERS):
    if (len(recv_data[i]) != MAX_NB_TRANSFERS):
      print("ERR251: Expected number of data words not received! Received/Expected datawords: %d/%d " %(len(recv_data[i]),MAX_NB_TRANSFERS)) 
      print("ERR252: Simulation unsuccessful!.")
      sys.exit(2)

  print("INF207: Comparing the addition results for " + str(NB_CHAIN_MULTIPLIERS) + " chain mults") 
  for i in range(NB_CHAIN_MULTIPLIERS):
    for j in range(MAX_NB_TRANSFERS):
      if ((trans_data0[i][j] * trans_data1[i][j] ) != recv_data[i][j]):
        print("ERR257: Error in chain addition! " + str(trans_data0[i][j]) + " + " + str(trans_data1[i][j]) + " != " + str(recv_data[i][j])) 
        err_cnt+=1
    if (err_cnt):
      print("ERR260: Results not Matched. Simulation unsuccessful!")
      sys.exit(2)
    else:
      print("Receive and transmit data exactly matches for chain mult: " + str(i) + " Received/Expected datawords: %d/%d " %(len(recv_data[i]),MAX_NB_TRANSFERS)) 
  print("INF217: All Chain addition results comparisons successful. Simulations successful!") 



