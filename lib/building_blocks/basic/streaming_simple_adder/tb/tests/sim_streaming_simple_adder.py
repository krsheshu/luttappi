import sys
from myhdl import Signal, delay, always,always_comb, now, Simulation, traceSignals, instances, intbv,StopSimulation
from avalon_buses import AvalonMM, AvalonST_SNK, AvalonST_SRC
from streaming_ip_a import streaming_ip_a_top
from src_bfm import src_bfm
from snk_bfm import snk_bfm
from clk_driver import clk_driver

from streaming_simple_adder import StreamingSimpleAdderPars, StreamingSimpleAdder


MAX_SIM_TIME = 10000
MAX_NB_TRANSFERS=32
trans_data = []
recv_data = []
ready_pulses=intbv(0)
nb1=0 # A global currently inevitable
nb2=0 # A global currently inevitable

def sim_streaming_simple_adder(pars_obj):
  PATTERN_WIDTH = 16
  DATA_WIDTH = 8
   
  reset = Signal(bool(1))
  clk = Signal(bool(0))
  elapsed_time=Signal(0)
  
  av_src0_bfm = AvalonST_SRC(DATA_WIDTH)
  av_src1_bfm = AvalonST_SRC(DATA_WIDTH)
  av_snk0 = AvalonST_SNK(DATA_WIDTH)
  av_snk1 = AvalonST_SNK(DATA_WIDTH)
  av_src = AvalonST_SRC(DATA_WIDTH)
  av_snk_bfm = AvalonST_SNK(DATA_WIDTH)
  src_bfm_i = AvalonST_SNK(DATA_WIDTH)
  src_bfm_o = AvalonST_SRC(DATA_WIDTH)
  
  
  clkgen=clk_driver(elapsed_time,clk,period=20)

  add_pars=StreamingSimpleAdderPars()
  add_pars.SNK0_DATA_WIDTH=DATA_WIDTH
  add_pars.SNK1_DATA_WIDTH=DATA_WIDTH
  add_pars.SRC_DATA_WIDTH=DATA_WIDTH
  add_pars(add_pars)
  add_i=StreamingSimpleAdder()
  src0_bfm_inst = src_bfm(reset, clk, pars_obj.valid.pattern0, src_bfm_i, av_src0_bfm)
  
  src1_bfm_inst = src_bfm(reset, clk, pars_obj.valid.pattern1, src_bfm_i, av_src1_bfm)

  streaming_simple_adder_inst = add_i.block_connect(add_pars, reset, clk, av_snk0, av_snk1, av_src)

  snk_bfm_inst = snk_bfm(reset, clk, pars_obj.ready, av_snk_bfm, src_bfm_o)


  print "Ready Pattern: ", str(hex(pars_obj.ready))
  print "Valid Pattern0: ", str(hex(pars_obj.valid.pattern0))
  print "Valid Pattern1: ", str(hex(pars_obj.valid.pattern1))
  @always_comb
  def beh_comb_logic():
    # Streaming Input Interface
    av_snk0.valid_i.next  = av_src0_bfm.valid_o
    av_snk0.data_i.next  = av_src0_bfm.data_o
    av_src0_bfm.ready_i.next  = av_snk0.ready_o
    av_snk1.valid_i.next  = av_src1_bfm.valid_o
    av_snk1.data_i.next  = av_src1_bfm.data_o
    av_src1_bfm.ready_i.next  = av_snk1.ready_o
    #Streaming Output interface
    av_snk_bfm.valid_i.next = av_src.valid_o
    av_snk_bfm.data_i.next = av_src.data_o
    av_src.ready_i.next = av_snk_bfm.ready_o
    src_bfm_i.valid_i.next = 1 if (nb1 < MAX_NB_TRANSFERS) else 0

  @always(clk.posedge)
  def stimulus():
    if elapsed_time == 40:
      reset.next = 0

  INIT_DATA=1
  data_in=Signal(int(0))
  @always_comb
  def transmit_data_process():
    if (av_src0_bfm.ready_i == 1 and av_src0_bfm.valid_o == 1):
      src_bfm_i.data_i.next = data_in 

  #Dataout is just an increment (for next valid data)
  @always(clk.posedge, reset.posedge)
  def transmit_data_clk_process():
    global trans_data,nb1
    if reset==1:
      data_in.next = int(INIT_DATA)
    elif (av_src0_bfm.ready_i == 1 and av_src0_bfm.valid_o == 1 and src_bfm_i.valid_i == 1):
      nb1+=1
      #print str(nb1) + ". Transmitted data to src bfm:",  ": ", src_bfm_i.data_i 
      trans_data.append(int(data_in))
      data_in.next = data_in + 1
  
  
  @always(clk.posedge)
  def receive_data_process():
    global recv_data,nb2
    if (src_bfm_o.valid_o == 1):
      nb2+=1
      #print str(nb2) + ". Received data from sink bfm:", ": ", src_bfm_o.data_o
      recv_data.append(int(src_bfm_o.data_o))
      sim_time_now=now()
      if (nb2 == MAX_NB_TRANSFERS):
        raise StopSimulation("Simulation Finished in %d clks: In total " %now() + str(MAX_NB_TRANSFERS) + " data words received")  

  @always(clk.posedge)
  def simulation_time_check():
    sim_time_now=now()
    if(sim_time_now>MAX_SIM_TIME):
        raise StopSimulation("Warning! Simulation Exited upon reaching max simulation time of " + str(MAX_SIM_TIME) + " clocks")  



  @always(clk.posedge)
  def cnt_ready_pulses():
    global ready_pulses
    if (av_snk_bfm.ready_o == 1):
      ready_pulses+=1 
      #print "ready received from bfm" 


  return instances()


def check_simulation_results(pars_obj):
  global trans_data,recv_data,ready_pulses
  err_cnt=0
  trans_l=0
  rest_l=0
  recv_l=0 
  print "Transmitted data: ", str(trans_data)
  print "Received data: ", str(recv_data)
  print "Num ready pulses: ", str(ready_pulses)
  print "Operation intended: Addition"
  trans_l=len(trans_data)
  recv_l=len(recv_data)
  rest_l=trans_l-recv_l
  if (len(recv_data) < MAX_NB_TRANSFERS):
    print "ERR123: Expected number of data words not received! Received/Expected datawords: %d/%d " %(len(recv_data),MAX_NB_TRANSFERS) 
    print "ERR124: Simulation unsuccessful!."

  else:
    print "Total num transmitted data= %d" % trans_l  
    print "Total num received data= %d" % recv_l 
    for i in range(0,len(trans_data)):
      if ((trans_data[i]*2) != recv_data[i]):
        print "ERR131: Mismatch found for tx_index %d. tx_data= %d recv_data=%d" % (i,trans_data[i],recv_data[i])
        err_cnt+=1
    if (err_cnt):
      print "ERR134: Results not Matched. Simulation unsuccessful!"
    else:
      print "Receive and transmit data exactly matches for addition..." 
      print "Simulation Successful!"



