import sys
from myhdl import Signal, delay, always,always_comb, now, Simulation, traceSignals, instances, intbv,StopSimulation
from avalon_buses import AvalonMM, AvalonST_SNK, AvalonST_SRC
from streaming_ip_a import streaming_ip_a_top
from src_bfm import src_bfm
from snk_bfm import snk_bfm
from clk_driver import clk_driver
from common_functions import simple_wire_assign, simple_reg_assign, conditional_wire_assign, CLogB2, conditional_reg_assign, conditional_clocked_append

from streaming_chain_adder import StreamingChainAdderPars, StreamingChainAdder


MAX_SIM_TIME = 10000
MAX_NB_TRANSFERS=Signal(int(32))

NB_CHAIN_ADDERS = 2 
 
trans_data  = [ [] for i in range(NB_CHAIN_ADDERS)]
recv_data   = [ [] for i in range(NB_CHAIN_ADDERS)]
ready_pulses=intbv(0)

def sim_streaming_chain_adder(pars_obj):
  PATTERN_WIDTH = 16
  DATA_WIDTH    = 8
 
  reset = Signal(bool(1))
  clk = Signal(bool(0))
  elapsed_time=Signal(0)
  
  nb_transmit=[Signal(int(0)) for i in range(NB_CHAIN_ADDERS)]  # A global currently inevitable
  nb_receive=[Signal(int(0)) for i in range(NB_CHAIN_ADDERS)]  # A global currently inevitable
  
  av_src0_bfm = [AvalonST_SRC(DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  av_src1_bfm = [AvalonST_SRC(DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  av_snk0     = [AvalonST_SNK(DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  av_snk1     = [AvalonST_SNK(DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  av_src      = [AvalonST_SRC(DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  av_snk_bfm  = [AvalonST_SNK(DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  src_bfm_i   = [AvalonST_SNK(DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]
  src_bfm_o   = [AvalonST_SRC(DATA_WIDTH)  for i in range(NB_CHAIN_ADDERS)]

  clkgen=clk_driver(elapsed_time,clk,period=20)



  add_i = [None for i in range(NB_CHAIN_ADDERS)]
  src0_bfm_inst= [None for i in range(NB_CHAIN_ADDERS)]
  src1_bfm_inst= [None for i in range(NB_CHAIN_ADDERS)]
  streaming_chain_adder_inst= None
  snk_bfm_inst= [None for i in range(NB_CHAIN_ADDERS)]


  for i in range(NB_CHAIN_ADDERS):
    src0_bfm_inst[i]  = src_bfm(reset, clk, pars_obj.valid.pattern0, src_bfm_i[i], av_src0_bfm[i])
  
    src1_bfm_inst[i]  = src_bfm(reset, clk, pars_obj.valid.pattern1, src_bfm_i[i], av_src1_bfm[i])
    
    snk_bfm_inst[i] = snk_bfm(reset, clk, pars_obj.ready, av_snk_bfm[i], src_bfm_o[i])
    
  add_pars=StreamingChainAdderPars()
  add_pars.SNK0_DATAWIDTH=DATA_WIDTH
  add_pars.SNK1_DATAWIDTH=DATA_WIDTH
  add_pars.SRCD_ATAWIDTH=DATA_WIDTH
  add_pars.NB_CHAIN_ADDERS=NB_CHAIN_ADDERS
  add_pars(add_pars)
  add_i=StreamingChainAdder()
  
  streaming_chain_adder_inst = add_i.block_connect(add_pars, reset, clk, av_snk0, av_snk1, av_src)


  print "Ready Pattern: ", str(hex(pars_obj.ready))
  print "Valid Pattern0: ", str(hex(pars_obj.valid.pattern0))
  print "Valid Pattern1: ", str(hex(pars_obj.valid.pattern1))
  
  
  snk0_valid_inst = [None for i in range(NB_CHAIN_ADDERS)]
  snk0_data_inst  = [None for i in range(NB_CHAIN_ADDERS)]
  snk0_ready_inst = [None for i in range(NB_CHAIN_ADDERS)]
  snk1_valid_inst = [None for i in range(NB_CHAIN_ADDERS)]
  snk1_data_inst  = [None for i in range(NB_CHAIN_ADDERS)]
  snk1_ready_inst = [None for i in range(NB_CHAIN_ADDERS)]
  src_valid_inst  = [None for i in range(NB_CHAIN_ADDERS)]
  src_data_inst   = [None for i in range(NB_CHAIN_ADDERS)]
  src_ready_inst  = [None for i in range(NB_CHAIN_ADDERS)]
  
  for i in range(NB_CHAIN_ADDERS):
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


  src_bfm_valid_inst=[None for i in range(NB_CHAIN_ADDERS)]
  for i in range(NB_CHAIN_ADDERS): 
    src_bfm_valid_inst[i]= conditional_wire_assign(src_bfm_i[i].valid_i,Signal(nb_transmit[i] < MAX_NB_TRANSFERS), 1, 0) 
  

  INIT_DATA=1
  data_in=[Signal(int(0)) for i in range(NB_CHAIN_ADDERS)]
  
  src_bfm_data_inst=[None for i in range(NB_CHAIN_ADDERS)]
  for i in range(NB_CHAIN_ADDERS): 
    src_bfm_data_inst[i]= conditional_wire_assign(src_bfm_i[i].data_i,(av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o), data_in[i], src_bfm_i[i].data_i) 
 
  data_in_inst=[None for i in range(NB_CHAIN_ADDERS)]
  nb_transmit_inst=[None for i in range(NB_CHAIN_ADDERS)]
  transmit_data_append_inst=[None for i in range(NB_CHAIN_ADDERS)]
  #Dataout is just an increment (for next valid data)
  for i in range(NB_CHAIN_ADDERS):
    data_in_inst[i] = conditional_reg_assign( reset, clk, data_in[i], int(INIT_DATA), (data_in[i]+1), 
                              (av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o and src_bfm_i[i].valid_i ))       
    nb_transmit_inst[i] = conditional_reg_assign( reset, clk, nb_transmit[i], 0, (nb_transmit[i]+1), 
                              (av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o and src_bfm_i[i].valid_i ))       
    transmit_data_append_inst[i] = conditional_clocked_append( reset, clk, trans_data[i], int(data_in[i]), 
                              (av_src0_bfm[i].ready_i and av_src0_bfm[i].valid_o and src_bfm_i[i].valid_i ))


  #@always(clk.posedge, reset.posedge)
  #def transmit_data_clk_process():
  #  global trans_data
  #  if (av_src0_bfm[0].ready_i == 1 and av_src0_bfm[0].valid_o == 1 and src_bfm_i[0].valid_i == 1):
  #    trans_data.append(int(data_in[0]))
  
  #@always(clk.posedge, reset.posedge)
  #def transmit_data_clk_process():
  #  global trans_data
  #  if reset==1:
  #    data_in.next = int(INIT_DATA)
  #    #nb_transmit.next= 0
  #  elif (av_src0_bfm[0].ready_i == 1 and av_src0_bfm[0].valid_o == 1 and src_bfm_i[0].valid_i == 1):
  #    nb_transmit.next= nb_transmit+ 1
  #    #print str(nb_transmit) + ". Transmitted data to src bfm:",  ": ", src_bfm_i[0].data_i 
  #    trans_data.append(int(data_in))
  #    data_in.next = data_in + 1
  
  
  @always(clk.posedge)
  def receive_data_process():
    global recv_data
    if (src_bfm_o[0].valid_o == 1):
      nb_receive[0].next = nb_receive[0] + 1
      print str(nb_receive[0]) + ". Received data from sink bfm:", ": ", src_bfm_o[0].data_o
      recv_data.append(int(src_bfm_o[0].data_o))
      sim_time_now=now()
      if (nb_receive[0] == MAX_NB_TRANSFERS):
        raise StopSimulation("Simulation Finished in %d clks: In total " %now() + str(MAX_NB_TRANSFERS) + " data words received")  

  @always(clk.posedge)
  def simulation_time_check():
    sim_time_now=now()
    if(sim_time_now>MAX_SIM_TIME):
        raise StopSimulation("Warning! Simulation Exited upon reaching max simulation time of " + str(MAX_SIM_TIME) + " clocks")  


  @always(clk.posedge)
  def cnt_ready_pulses():
    global ready_pulses
    if (av_snk_bfm[0].ready_o == 1):
      ready_pulses+=1 
      #print "ready received from bfm" 


  return instances()


def check_simulation_results(pars_obj):
  global trans_data,recv_data,ready_pulses
  err_cnt=0
  trans_l=0
  net_trans_l=0
  rest_l=0
  recv_l=0
  print "Received data: ", str(recv_data)
  print "Num ready pulses: ", str(ready_pulses)
  print "Operation intended: Addition"
  for i in range(NB_CHAIN_ADDERS):
    trans_l=len(trans_data[i])
    print "Length trans: " + str(i) + ": " + str(trans_l) 
    print "Transmitted data: ", str(trans_data[i])
    net_trans_l+=trans_l
  recv_l=len(recv_data)
  rest_l=trans_l-recv_l

  if (len(recv_data) < MAX_NB_TRANSFERS):
    print "ERR123: Expected number of data words not received! Received/Expected datawords: %d/%d " %(len(recv_data),MAX_NB_TRANSFERS) 
    print "ERR124: Simulation unsuccessful!."

  else:
    print "Total num transmitted data= %d" % net_trans_l
    print "Total num received data= %d" % recv_l 
    for i in range(0,len(trans_data)):
      if ((trans_data[i] + trans_data[i] ) != recv_data[i]):
        print "ERR131: Mismatch found for tx_index %d. tx_data= %d recv_data=%d" % (i,trans_data[i],recv_data[i])
        err_cnt+=1
    if (err_cnt):
      print "ERR134: Results not Matched. Simulation unsuccessful!"
    else:
      print "Receive and transmit data exactly matches for addition..." 
      print "Simulation Successful!"



