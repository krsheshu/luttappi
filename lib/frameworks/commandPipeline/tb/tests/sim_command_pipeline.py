import sys
from myhdl import Signal, delay, always,always_comb, now, Simulation, traceSignals, instances, intbv,StopSimulation
from avalon_buses import PipelineST
from clk_driver import clk_driver

import subprocess

from operand_pipeline import OperandPipeline, OperandPipelinePars, OperandPipelineIo 
from command_pipeline import CommandPipeline, CommandPipelinePars, CommandPipelineIo 

#------------------ Globals ---------------

MAX_SIM_TIME = 10000
MAX_NB_TRANSFERS=4
trans_data = []
recv_data = []
nb1=0 # A global currently inevitable
nb2=0 # A global currently inevitable

line_nb=0

def sim_command_pipeline(pars_obj):

  #------------------ Initializing Pipeline depths ---------------
  
  NB_PIPELINE_STAGES  = 5
  DATAWIDTH           = 32
   
  #-------------- Simulation Initialisations ---------------------
  
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
  pipe_inpA  = PipelineST(pars.DATAWIDTH) 
  pipe_outA  = PipelineST(pars.DATAWIDTH) 

  operand_a=OperandPipeline()
  ioA=OperandPipelineIo()
  ioA(pars)

  # --- Initializing Pipeline B
  pipe_inpB  = PipelineST(pars.DATAWIDTH) 
  pipe_outB  = PipelineST(pars.DATAWIDTH) 

  operand_b=OperandPipeline()
  ioB=OperandPipelineIo()
  ioB(pars)

  # --- Initializing Command Pipeline
  pipe_out_mult  = PipelineST(pars.DATAWIDTH)
  multcmdFile='../tests/mult_pipeline.list'
  multPipe=CommandPipeline()
  multCmdStr=multPipe.cmd_convert_to_string(pars,multcmdFile)
  ioMult=CommandPipelineIo()
  ioMult(pars)

  # Accumulator Output
  acc_out = PipelineST(pars.DATAWIDTH)
  #----------------------------------------------------------------
 
  #----------------- Connecting Pipeline Blocks -------------------
  
  inst=[]
  inst.append(operand_a.block_connect(pars, reset, clk, pipe_inpA, pipe_outA, ioA))
  inst.append(operand_b.block_connect(pars, reset, clk, pipe_inpB, pipe_outB, ioB))
  #----------------------------------------------------------------
 
  #----------------- Connecting Command Pipeline -------------------
  # Mult Pipeline 
  inst.append(multPipe.block_connect(pars, reset, clk, multCmdStr, ioA, ioB, pipe_out_mult, ioMult))   
 
  #----------------------------------------------------------------
 
  #----------------- Logistic Regression Test File -------------------
  
  lr_test_file="../tests/ex2data1.txt"
  lr_theta_file="../tests/theta1.txt"

  #----------------------------------------------------------------
  

  #----------------- Shift Enable for pipeData -------------------
  
  shiftEn_i = Signal(bool(0))
  @always(clk.posedge)
  def shift_signal():
    shiftEn_i.next = not shiftEn_i
  
  @always_comb
  def shiftOperand_signal():
    ioB.shiftEn_i.next = shiftEn_i
    ioA.shiftEn_i.next = shiftEn_i
 
  #----------------------------------------------------------------
  
  #----------------- Reset For the Module  --------------------
  
  @always(clk.posedge)
  def stimulus():
    if elapsed_time == 40:
      reset.next = 0

  #----------------------------------------------------------------
  
  #----------------- Input Data for the Modules  --------------------
  
  INIT_DATA=20
  data_in=Signal(int(0))
  

  @always_comb
  def transmit_data_process():
    global line_nb
    if (shiftEn_i == 1 and nb1 < MAX_NB_TRANSFERS):
      
      #---- Splitting values in the line and assigning to float nbs----
      
      # Loading test data
      with open(lr_test_file, 'r') as f:
        d0=1.0        # Always first element is 1
        d1,d2,y=(f.read().split('\n')[line_nb]).split(',')
      line_nb+=1  
      print d0,d1,d2
      
      #loading theta
      with open(lr_theta_file, 'r') as f:
        t0,t1,t2=(f.read().split('\n')[0]).split(',')
      
      print(t0,t1,t2)
      #----------------------------------------------------------------

      #pipe_inpA.data.next = intbv(int(float(d0))) 
      pipe_inpA.data.next = round(float(d0))
      print(pipe_inpA.data.next)
      pipe_inpA.valid.next = 1
      #pipe_inpB.data.next = intbv(int(float(d1))) 
      pipe_inpB.data.next = round(float(t0))
      print(pipe_inpB.data.next)
      pipe_inpB.valid.next = 1
    else: 
      pipe_inpA.valid.next = 0
      pipe_inpB.valid.next = 0
  
  #----------------------------------------------------------------

  #----------------- Storing Transmitted Data  --------------------
  
  #Dataout is just an increment (for next valid data)
  @always(clk.posedge, reset.posedge)
  def transmit_data_clk_process():
    global trans_data,nb1
    if reset==1:
      pass
    elif (shiftEn_i == 1 and nb1 < MAX_NB_TRANSFERS):
      nb1+=1
      #print str(nb1) + ". Transmitted data to src bfm:",  ": ", src_bfm_i.data_i 
      trans_data.append(pipe_inpA.data.next)
      trans_data.append(pipe_inpB.data.next)
  
  #----------------------------------------------------------------
  
  #----------------- Storing Received Data  -----------------------
  
  @always(clk.posedge)
  def receive_data_process():
    global recv_data,nb2
    exp=2.718
    if (pipe_out_mult.valid == 1):
      nb2+=1
      #print str(nb2) + ". Received data from multPipe:", ": ", int(pipe_out_mult.data)
      acc_out.data.next = acc_out.data + pipe_out_mult.data
      recv_data.append(int(pipe_out_mult.data))
      sim_time_now=now()
      if (nb2 == MAX_NB_TRANSFERS):
        print ". Accumulated Output: ", ": ", int(acc_out.data.next), " g(z) : ",  (1.0/(1+ (2**2)))#acc_out.data.next)))
        raise StopSimulation("Simulation Finished in %d clks: In total " %now() + str(MAX_NB_TRANSFERS) + " data words received")  
  
  #----------------------------------------------------------------

  #----------------- Max Simulation Time Exit Condition -----------
  
  @always(clk.posedge)
  def simulation_time_check():
    sim_time_now=now()
    if(sim_time_now>MAX_SIM_TIME):
        raise StopSimulation("Warning! Simulation Exited upon reaching max simulation time of " + str(MAX_SIM_TIME) + " clocks")  

  #----------------------------------------------------------------
  return instances()


def check_simulation_results(pars_obj):
  global trans_data,recv_data
  err_cnt=0
  trans_l=0
  rest_l=0
  recv_l=0 
  print "Transmitted data: ", str(trans_data)
  print "Received data: ", str(recv_data)
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
      if (trans_data[i]*(trans_data[i]+1) != recv_data[i]):
        print "ERR131: Mismatch found for tx_index %d. tx_data= %d recv_data=%d" % (i,trans_data[i],recv_data[i])
        err_cnt+=1
    if (err_cnt):
      print "ERR134: Results not Matched. Simulation unsuccessful!"
    else:
      print "Receive and transmit data exactly matches..." 
      print "Simulation Successful!"



