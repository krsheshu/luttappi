import sys, os
from myhdl import Signal, delay, always,always_comb, now, Simulation, traceSignals, instances, intbv,StopSimulation
from avalon_buses import AvalonMM, AvalonST_SNK, AvalonST_SRC
from streaming_ip_a import streaming_ip_a_top
from src_bfm import src_bfm
from snk_bfm import snk_bfm
from clk_driver import clk_driver
from common_functions import simple_wire_assign, simple_reg_assign, conditional_wire_assign, conditional_clocked_appendfile, conditional_wire_assign_lt
from common_functions import CLogB2, conditional_reg_assign, conditional_clocked_append, conditional_reg_counter,Reset, conditional_random_generator

from streaming_chain_adder import StreamingChainAdderPars, StreamingChainAdder

import random # for randomized test
#from __future__ import print_function


MAX_NB_TRANSFERS=100
NB_CHAIN_ADDERS = 100
STREAM_DATA_WIDTH = 16

RANDRANGE=pow(2,STREAM_DATA_WIDTH-8)-1 # Maximum value allowed is 2^15-1 for avoiding overflow
MAX_SIM_TIME = 100000
 
txdata0_filename  = [ "" for i in range(NB_CHAIN_ADDERS)]
txdata1_filename  = [ "" for i in range(NB_CHAIN_ADDERS)]
rxdata_filename   = "receive_data.log"
ready_pulses=[Signal(int(0))  for i in range(NB_CHAIN_ADDERS)]
ready_pulses0=[Signal(int(0))  for i in range(NB_CHAIN_ADDERS)]
ready_pulses1=[Signal(int(0))  for i in range(NB_CHAIN_ADDERS)]
ready_pulses=Signal(int(0))


def sim_streaming_chain_adder(pars_obj):
  # removing the files if already available 
  global  rxdata_filename
  global  txdata0_filename
  global  txdata1_filename
  
  for i in range(NB_CHAIN_ADDERS):
    txdata0_filename[i]="transmit_data_inpA_adder{:d}.log".format(i) 
    if (os.path.exists(txdata0_filename[i])):
      os.remove(txdata0_filename[i]) 
    txdata1_filename[i]="transmit_data_inpB_adder{:d}.log".format(i) 
    if (os.path.exists(txdata1_filename[i])):
      os.remove(txdata1_filename[i]) 
  
  if (os.path.exists(rxdata_filename)):
    os.remove(rxdata_filename) 
  
  reset = Signal(bool(1))
  clk = Signal(bool(0))
  elapsed_time=Signal(0)
  
  nb_transmit=[Signal(int(0)) for i in range(NB_CHAIN_ADDERS)] 
  nb_transmit0=[Signal(int(0)) for i in range(NB_CHAIN_ADDERS)] 
  nb_transmit1=[Signal(int(0)) for i in range(NB_CHAIN_ADDERS)] 
  nb_receive=Signal(int(0))  
  
  av_src0_bfm = [AvalonST_SRC(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  av_src1_bfm = [AvalonST_SRC(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  av_snk0     = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  av_snk1     = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  av_snk_bfm  = AvalonST_SNK(STREAM_DATA_WIDTH)
  src_bfm_i   = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  src_bfm_0   = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  src_bfm_1   = [AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  src_bfm_o   = AvalonST_SRC(STREAM_DATA_WIDTH)

  clkgen=clk_driver(elapsed_time,clk,period=20)

  src0_bfm_inst= [None for i in range(NB_CHAIN_ADDERS)]
  src1_bfm_inst= [None for i in range(NB_CHAIN_ADDERS)]
  snk_bfm_inst= None
  
  VALID_PATTERN0=[random.randint(0x0100,0xffff) for i in range(NB_CHAIN_ADDERS)]
  VALID_PATTERN1=[random.randint(0x0100,0xffff) for i in range(NB_CHAIN_ADDERS)]
  READY_PATTERN=[random.randint(0x0100,0xffff) for i in range(NB_CHAIN_ADDERS)]

  for i in range(NB_CHAIN_ADDERS):
    print "Chain Adder: " + str(i) + " Valid0: " +str(VALID_PATTERN0[i]) + " Valid1: " +str(VALID_PATTERN1[i]) +" Ready: " +str(READY_PATTERN[i])
    src0_bfm_inst[i]  = src_bfm(reset, clk, VALID_PATTERN0[i], src_bfm_0[i], av_src0_bfm[i])
  
    src1_bfm_inst[i]  = src_bfm(reset, clk, VALID_PATTERN1[i], src_bfm_1[i], av_src1_bfm[i])
    
  snk_bfm_inst = snk_bfm(reset, clk, READY_PATTERN[0], av_snk_bfm, src_bfm_o)
   

  i=NB_CHAIN_ADDERS*2
  
  nb_chain_adders=0
  nb_chain_adders_list=[]
  mod_list=[]
  nb_adder_stages=0
  while i>1: 
    mod_val = 0 if (i%2 == 0 or i == 1) else 1
    mod_list.append(mod_val)
    i = i/2 if (i%2 == 0) else i/2+1
    nb_chain_adders+=i
    nb_chain_adders_list.append(i)
    nb_adder_stages+=1

  print "nb_chain_adders: " + str(nb_chain_adders)
  print "nb_adder_stages: " + str(nb_adder_stages)
  print "mod_list: " + str(mod_list)
  print "nb_chain_adders_list: " + str(nb_chain_adders_list)

    
  av_snk0_cmb = [[AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)] for j in range(nb_adder_stages)]
  av_snk1_cmb = [[AvalonST_SNK(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)] for j in range(nb_adder_stages)]
  av_src      = [[AvalonST_SRC(STREAM_DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)] for j in range(nb_adder_stages)]
  
  snk0_valid_inst = [None for i in range(NB_CHAIN_ADDERS)]
  snk0_data_inst  = [None for i in range(NB_CHAIN_ADDERS)]
  snk0_ready_inst = [None for i in range(NB_CHAIN_ADDERS)]
  snk1_valid_inst = [None for i in range(NB_CHAIN_ADDERS)]
  snk1_data_inst  = [None for i in range(NB_CHAIN_ADDERS)]
  snk1_ready_inst = [None for i in range(NB_CHAIN_ADDERS)]
  src_valid_inst  = None 
  src_data_inst   = None 
  src_ready_inst  = None 
  
  streaming_chain_adder_inst= [None for i in range(nb_adder_stages)]
  add_i = [None for i in range(nb_adder_stages)]  
  add_pars=[None for i in range(nb_adder_stages)]
  snk0_inst=[]
  snk1_inst=[]

  for i in range(nb_adder_stages): 
    add_pars[i]=StreamingChainAdderPars()
    add_pars[i].SNK0_DATAWIDTH=STREAM_DATA_WIDTH
    add_pars[i].SNK1_DATAWIDTH=STREAM_DATA_WIDTH
    add_pars[i].SRC_DATAWIDTH=STREAM_DATA_WIDTH
    add_pars[i].NB_CHAIN_ADDERS=NB_CHAIN_ADDERS
    add_pars[i](add_pars[i])
    add_i[i]=StreamingChainAdder()
 
    if (i!=0 and i<=nb_adder_stages-1):
      for j in range(nb_chain_adders_list[i]):
        k=j*2
        snk0_inst.append(simple_wire_assign(av_snk0_cmb[i][j].valid_i, av_src[i-1][k].valid_o))
        snk0_inst.append(simple_wire_assign(av_snk0_cmb[i][j].data_i, av_src[i-1][k].data_o))
        snk0_inst.append(simple_wire_assign(av_src[i-1][k].ready_i, av_snk0_cmb[i][j].ready_o))
      
        if (mod_list[i]==1 and j==(nb_chain_adders_list[i])-1):
          snk1_inst.append(simple_wire_assign(av_snk1_cmb[i][j].valid_i, Signal(1)))
          snk1_inst.append(simple_wire_assign(av_snk1_cmb[i][j].data_i, Signal(0)))
          snk1_inst.append(simple_wire_assign(Signal(1), av_snk1_cmb[i][j].ready_o))
          
        else: 
          snk1_inst.append(simple_wire_assign(av_snk1_cmb[i][j].valid_i, av_src[i-1][k+1].valid_o))
          snk1_inst.append(simple_wire_assign(av_snk1_cmb[i][j].data_i, av_src[i-1][k+1].data_o))
          snk1_inst.append(simple_wire_assign(av_src[i-1][k+1].ready_i, av_snk1_cmb[i][j].ready_o))
        
    elif (i==0):
      for k in range(NB_CHAIN_ADDERS):
        snk0_valid_inst[k]  = simple_wire_assign(av_snk0_cmb[0][k].valid_i, av_src0_bfm[k].valid_o)
        snk0_data_inst[k]   = simple_wire_assign(av_snk0_cmb[0][k].data_i, av_src0_bfm[k].data_o)
        snk0_ready_inst[k]  = simple_wire_assign(av_src0_bfm[k].ready_i, av_snk0_cmb[0][k].ready_o)
       
        snk1_valid_inst[k]  = simple_wire_assign(av_snk1_cmb[0][k].valid_i, av_src1_bfm[k].valid_o)
        snk1_data_inst[k]   = simple_wire_assign(av_snk1_cmb[0][k].data_i, av_src1_bfm[k].data_o)
        snk1_ready_inst[k]  = simple_wire_assign(av_src1_bfm[k].ready_i, av_snk1_cmb[0][k].ready_o)
       
        
    streaming_chain_adder_inst[i] = add_i[i].block_connect(add_pars[i], reset, clk, av_snk0_cmb[i], av_snk1_cmb[i], av_src[i])

  src_valid_inst  = simple_wire_assign(av_snk_bfm.valid_i, av_src[nb_adder_stages-1][0].valid_o)
  src_data_inst   = simple_wire_assign(av_snk_bfm.data_i, av_src[nb_adder_stages-1][0].data_o)
  src_ready_inst  = simple_wire_assign(av_src[nb_adder_stages-1][0].ready_i, av_snk_bfm.ready_o)
  
  @always(clk.posedge)
  def stimulus():
    if elapsed_time == 40:
      reset.next = 0


  INIT_DATA0=[random.randint(1,RANDRANGE) for i in range(NB_CHAIN_ADDERS)]
  INIT_DATA1=[random.randint(1,RANDRANGE) for i in range(NB_CHAIN_ADDERS)]
  
  data_in0=[Signal(int(0)) for i in range(NB_CHAIN_ADDERS)]
  data_in1=[Signal(int(0)) for i in range(NB_CHAIN_ADDERS)]
  src_bfm_0_valid_inst=[]
  src_bfm_1_valid_inst=[]
  src_bfm_0_data_inst=[]
  src_bfm_1_data_inst=[]
  
  for i in range(NB_CHAIN_ADDERS): 
      src_bfm_0_data_inst.append(conditional_wire_assign(src_bfm_0[i].data_i,(av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o), 
                                                          data_in0[i], src_bfm_0[i].data_i)) 
      src_bfm_1_data_inst.append(conditional_wire_assign(src_bfm_1[i].data_i,(av_src1_bfm[i].ready_i and av_src1_bfm[i].valid_o), 
                                                          data_in1[i], src_bfm_1[i].data_i)) 

  for i in range(NB_CHAIN_ADDERS): 
      src_bfm_0_valid_inst.append(conditional_wire_assign_lt(src_bfm_0[i].valid_i, nb_transmit0[i], Signal(MAX_NB_TRANSFERS), 1, 0))
      src_bfm_1_valid_inst.append(conditional_wire_assign_lt(src_bfm_1[i].valid_i, nb_transmit1[i], Signal(MAX_NB_TRANSFERS), 1, 0))
 
  data_in0_inst=[]
  data_in1_inst=[]
  nb_transmit0_inst=[]
  nb_transmit1_inst=[]
  transmit_data0_append_inst=[]
  transmit_data1_append_inst=[]
  receive_data_append_inst=[]

  
  for i in range(NB_CHAIN_ADDERS): 
      data_in0_inst.append(conditional_random_generator( reset, clk, data_in0[i], int(INIT_DATA0[i]),  
                                (av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o and src_bfm_0[i].valid_i ), RANDRANGE))       
      data_in1_inst.append(conditional_random_generator( reset, clk, data_in1[i], int(INIT_DATA1[i]),  
                                (av_src1_bfm[i].ready_i and av_src1_bfm[i].valid_o and src_bfm_1[i].valid_i ), RANDRANGE))      
  
      nb_transmit0_inst.append(conditional_reg_counter( reset, clk, nb_transmit0[i], Reset.LOW, 
                                (av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o and src_bfm_0[i].valid_i )))       
      nb_transmit1_inst.append(conditional_reg_counter( reset, clk, nb_transmit1[i], Reset.LOW, 
                                (av_src1_bfm[i].ready_i and av_src1_bfm[i].valid_o and src_bfm_1[i].valid_i )))       
 
      transmit_data0_append_inst.append(conditional_clocked_appendfile( reset, clk, 
                                (av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o and src_bfm_0[i].valid_i ),  
                                  data_in0[i], txdata0_filename[i]))
      transmit_data1_append_inst.append(conditional_clocked_appendfile( reset, clk, 
                                (av_src1_bfm[i].ready_i and av_src1_bfm[i].valid_o and src_bfm_1[i].valid_i ),  
                                  data_in1[i], txdata1_filename[i]))
 
  receive_data_append_inst.append(conditional_clocked_appendfile( reset, clk, 
                                    (src_bfm_o.valid_o),  src_bfm_o.data_o, rxdata_filename))
  

 
  
  recv_inst=None
  recv_inst=conditional_reg_counter(reset, clk, nb_receive, Reset.LOW, src_bfm_o.valid_o)  
 
  @always(clk.posedge)
  def receive_data_process():
    TIME_SHUTDOWN=5000
    nb_recv=0
    sim_time_now=now()
    nb_recv+=nb_receive
    if(nb_recv == (MAX_NB_TRANSFERS)): 
      print "INF242: Num ready pulses: "+ str(int(ready_pulses)) 
      raise StopSimulation("Simulation Finished in %d clks: In total " %now() + str(nb_recv) + " data words received")  

  @always(clk.posedge)
  def simulation_time_check():
    sim_time_now=now()
    if(sim_time_now>MAX_SIM_TIME):
        raise StopSimulation("Warning! Simulation Exited upon reaching max simulation time of " + str(MAX_SIM_TIME) + " clocks")  


  ready_pulse_cnt_inst=None
  ready_pulse_cnt_inst=conditional_reg_counter(reset, clk, ready_pulses, Reset.LOW, ( av_snk_bfm.ready_o) )


  return instances()


def check_simulation_results(pars_obj):
  global  rxdata_filename
  global  txdata0_filename
  global  txdata1_filename
  trans_data0  = [ [] for i in range(NB_CHAIN_ADDERS)]
  trans_data1  = [ [] for i in range(NB_CHAIN_ADDERS)]
  recv_data   = [] 
  
  for i in range(NB_CHAIN_ADDERS):
    if (os.path.exists(txdata0_filename[i]) == False):
      print "ERR186: Error finding file!: " + txdata0_filename[i] 
    if (os.path.exists(txdata1_filename[i]) == False):
      print "ERR186: Error finding file!: " + txdata1_filename[i] 

  for i in range(NB_CHAIN_ADDERS):
    add1 = open(txdata0_filename[i], 'r')
    add2 = open(txdata1_filename[i], 'r')
    for line in add1.readlines():
      trans_data0[i].append(int(line))
    print "INF204: Read transmit file: " + txdata0_filename[i] 
    for line in add2.readlines():
      trans_data1[i].append(int(line))
    print "INF207: Read transmit file: " + txdata1_filename[i] 
    add1.close()
    add2.close()
 
  if (os.path.exists(rxdata_filename) == False):
    print "ERR186: Error finding file!: " + rxdata_filename 
  
  result = open(rxdata_filename, 'r')
  for line in result.readlines():
    recv_data.append(int(line))
  print "INF207: Read  receive file: " + rxdata_filename
  result.close()
  
  err_cnt=0
  trans_l0=0
  trans_l1=0
  #print "Received data: ", str(recv_data)
  #print "Transmitted data: ", str(trans_data[i])
  
  print "Operation intended: Reduction Chain Addition"
  
  for i in range(NB_CHAIN_ADDERS):
    trans_l0=len(trans_data0[i])
    trans_l1=len(trans_data1[i])
    if (trans_l0 != trans_l1) or (trans_l0 != MAX_NB_TRANSFERS  or trans_l1 != MAX_NB_TRANSFERS):
      print "ERR242: Transmitted data lengths does not match. Tx Len0: " + str(trans_l0) + ", Tx Len1: " + str(trans_l1) + ", Rx len: " + str(MAX_NB_TRANSFERS)+" Quitting..."
      sys.exit(2) 

  if (len(recv_data) != MAX_NB_TRANSFERS):
    print "ERR251: Expected number of data words not received! Received/Expected datawords: %d/%d " %(len(recv_data),MAX_NB_TRANSFERS) 
    print "ERR252: Simulation unsuccessful!."
    sys.exit(2)

  print "INF207: Comparing the addition results for " + str(NB_CHAIN_ADDERS) + " chain adders" 
  for j in range(MAX_NB_TRANSFERS):
    reduction_adder=0
    for i in range(NB_CHAIN_ADDERS):
      reduction_adder+=(trans_data0[i][j] + trans_data1[i][j])
    if (reduction_adder != recv_data[j]):
      print "ERR257: Error in reduction chain addition! nb_transmit: " + str(j) + " reduction result: "+str(reduction_adder) + " recv data:  " + str(recv_data[j]) 
      err_cnt+=1
  if (err_cnt):
    print "ERR260: Results not Matched. Simulation unsuccessful!"
    sys.exit(2)
  else:
    print "Reduction Chain adder operation successfully matched." + " Received/Expected datawords: %d/%d " %(len(recv_data),MAX_NB_TRANSFERS) 
  print "INF217: All Reduction Chain addition results comparisons successful. Simulations successful!" 



