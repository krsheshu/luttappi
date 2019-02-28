import sys
from myhdl import Signal, delay, always,always_comb, now, Simulation, traceSignals, instances, intbv,StopSimulation
from avalon_buses import PipelineST
from clk_driver import clk_driver

from operand_pipeline import OperandPipeline, OperandPipelinePars, OperandPipelineIo 
from command_pipeline import CommandPipeline, CommandPipelinePars, CommandPipelineIo 

MAX_SIM_TIME = 10000
MAX_NB_TRANSFERS=32
trans_data = []
recv_data = []
ready_pulses=intbv(0)
nb1=0 # A global currently inevitable
nb2=0 # A global currently inevitable


def sim_command_pipeline(pars_obj):

  #------------------ Initializing Pipeline depths ---------------
  
  NB_PIPELINE_STAGES  = 5
  DATAWIDTH           = 32
   
  #------------------------- Initialisations ---------------------
  
  reset = Signal(bool(1))
  clk = Signal(bool(0))
  elapsed_time=Signal(0)
  
  clkgen=clk_driver(elapsed_time,clk,period=20)
  
  #----------------------------------------------------------------
 
  #----------------- Initializing Pipeline Streams ----------------
  
  # --- Pipeline Pars
  pars=OperandPipelinePars()
  pars.NB_PIPELINE_STAGES=NB_PIPELINE_STAGES
  pars.DATAWIDTH=DATAWIDTH
  
  # --- Initializing Pipeline A
  pipe_inpA  = PipelineST(DATAWIDTH) 
  pipe_outA  = PipelineST(DATAWIDTH) 

  operand_a=OperandPipeline()
  ioA=OperandPipelineIo(pars)

  # --- Initializing Pipeline B
  pipe_inpB  = PipelineST(DATAWIDTH) 
  pipe_outB  = PipelineST(DATAWIDTH) 

  operand_b=OperandPipeline()
  ioB=OperandPipelineIo(pars)

  # --- Initializing Command Pipeline
  pipe_outC  = PipelineST(DATAWIDTH) 
  cmdFile='cmd_pipeline.list'
  cmdPipe=CommandPipeline()
  cmdStr=cmdPipe.cmd_convert_to_string(pars,cmdFile)
  ioC=CommandPipelineIo(pars)

  #----------------------------------------------------------------
 
  #----------------- Connecting Pipeline Blocks -------------------
  
  inst=[]
  inst.append(operand_a.block_connect(pars, reset, clk, pipe_inpA, pipe_outA, ioA))
  inst.append(operand_b.block_connect(pars, reset, clk, pipe_inpB, pipe_outB, ioB))
  #----------------------------------------------------------------
 
  #----------------- Connecting Command Pipeline -------------------
  
  inst.append(cmdPipe.block_connect(pars, reset, clk, cmdStr, ioA, ioB, pipe_outC, ioC)   
 
  #----------------------------------------------------------------
  


  mult = Signal(intbv(DATAWIDTH+DATAWIDTH))
  @always(clk.posedge, reset.posedge)
  def mult_process():
    if reset==1:
      mult.next = intbv(0)
    elif (ioA.stage_o[5].valid == 1 and ioB.stage_o[5].valid == 1):
      mult.next = mult + ioA.stage_o[5].data * ioB.stage_o[5].data
      print int(mult.next) 

  shiftEn_i = Signal(bool(0))
  @always(clk.posedge)
  def shift_signal():
    shiftEn_i.next = not shiftEn_i
  
  @always_comb
  def shiftOperand_signal():
    ioB.shiftEn_i.next = shiftEn_i
    ioA.shiftEn_i.next = shiftEn_i
 
  @always(clk.posedge)
  def stimulus():
    if elapsed_time == 40:
      reset.next = 0

  INIT_DATA=1
  data_in=Signal(int(0))
  @always_comb
  def transmit_data_process():
    if (shiftEn_i == 1 and nb1 < MAX_NB_TRANSFERS):
      pipe_inpA.data.next = data_in 
      pipe_inpA.valid.next = 1
      pipe_inpB.data.next = data_in 
      pipe_inpB.valid.next = 1
    else: 
      pipe_inpA.valid.next = 0
      pipe_inpB.valid.next = 0

  #Dataout is just an increment (for next valid data)
  @always(clk.posedge, reset.posedge)
  def transmit_data_clk_process():
    global trans_data,nb1
    if reset==1:
      data_in.next = int(INIT_DATA)
    elif (shiftEn_i == 1 and nb1 < MAX_NB_TRANSFERS):
      nb1+=1
      #print str(nb1) + ". Transmitted data to src bfm:",  ": ", src_bfm_i.data_i 
      trans_data.append(int(data_in))
      data_in.next = data_in + 1
  
  
  @always(clk.posedge)
  def receive_data_process():
    global recv_data,nb2
    if (pipe_outA.valid == 1):
      nb2+=1
      #print str(nb2) + ". Received data from sink bfm:", ": ", src_bfm_o.data_o
      recv_data.append(int(pipe_outA.data))
      sim_time_now=now()
      if (nb2 == MAX_NB_TRANSFERS + NB_PIPELINE_STAGES):
        raise StopSimulation("Simulation Finished in %d clks: In total " %now() + str(MAX_NB_TRANSFERS) + " data words received")  

  @always(clk.posedge)
  def simulation_time_check():
    sim_time_now=now()
    if(sim_time_now>MAX_SIM_TIME):
        raise StopSimulation("Warning! Simulation Exited upon reaching max simulation time of " + str(MAX_SIM_TIME) + " clocks")  

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
      if (trans_data[i] != recv_data[i]):
        print "ERR131: Mismatch found for tx_index %d. tx_data= %d recv_data=%d" % (i,trans_data[i],recv_data[i])
        err_cnt+=1
    if (err_cnt):
      print "ERR134: Results not Matched. Simulation unsuccessful!"
    else:
      print "Receive and transmit data exactly matches..." 
      print "Simulation Successful!"



