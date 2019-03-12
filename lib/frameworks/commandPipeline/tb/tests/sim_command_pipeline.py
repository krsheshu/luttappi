import sys
import math

from myhdl import Signal, delay, always,always_comb, now, Simulation, traceSignals, instances, intbv,StopSimulation
from avalon_buses import PipelineST
from clk_driver import clk_driver

import subprocess

from operand_pipeline import OperandPipeline, OperandPipelinePars, OperandPipelineIo 
from command_pipeline import CommandPipeline, CommandPipelinePars, CommandPipelineIo 
from accumulator import Accumulator, AccumulatorPars
from activation import Activation, ActivationPars


# Global Parameters-------------------------
# These pars control the data format
# floatDataBus = False for simulation in real scenario with intbv mult
# floatDataBus = True for simulation with floating point mult
floatDataBus=True

# NB_TRAINING_DATA - Controls the number of training data to be verified 
NB_TRAINING_DATA=100

# When using intbv for the data (not the floating point simulation),
# determine the decimal shift needed in the theta and training data parameters
# For example, for training data 32.5, a shift of 1 will use value of 325 for intbv representation
#              for theta value of -25.21, a shift of 2 will use -2521 for theta value 
test_decimal_shift=1
theta_decimal_shift=1

#-------------------------------------------


# Globals ----------------------------------

DEF_ROUND = 1 # Applicable only when float test data is used
line_nb=0
LEN_THETA=3

#-------------------------------------------

# Transmit Receive Parameters---------------

MAX_SIM_TIME = LEN_THETA*10000
MAX_NB_TRANSFERS=NB_TRAINING_DATA*LEN_THETA
trans_dataA = []
trans_dataB = []
recv_data = []
nbTA=0 # A global currently inevitable
nbTB=0 # A global currently inevitable
nbR=0 # A global currently inevitable

#-------------------------------------------

# Global Accumulator Output ----------------

acc_out = 0.0# PipelineST(pars.DATAWIDTH)
acc_out_list=[]

#-------------------------------------------

# Other Globals------------------------------

label=[]
prediction_res=[]

#--------------------------------------------

def sim_command_pipeline(pars_obj):

  global test_decimal_shift, theta_decimal_shift

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
  pars.CHANNEL_WIDTH=1
  global floatDataBus
  if (True == floatDataBus):  
    pars.INIT_DATA=0.0  # requires floating point computation 
  else:
    pars.INIT_DATA=0    # requires intbv computation 
 
  # --- Initializing Pipeline A
  pipe_inpA  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
  pipe_outA  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 

  operand_a=OperandPipeline()
  ioA=OperandPipelineIo()
  ioA(pars)

  # --- Initializing Pipeline B
  pipe_inpB  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 
  pipe_outB  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA) 

  operand_b=OperandPipeline()
  ioB=OperandPipelineIo()
  ioB(pars)

  # --- Initializing Command Pipeline
  pipe_multRes  = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)
  multcmdFile='../tests/mult_pipeline.list'
  parsMult= CommandPipelinePars()
  parsMult.DATAWIDTH= pars.DATAWIDTH
  parsMult.CHANNEL_WIDTH = pars.CHANNEL_WIDTH
  parsMult.INIT_DATA = pars.INIT_DATA
  parsMult.STAGE_NB = 1
  parsMult(parsMult,multcmdFile) 
  multPipe=CommandPipeline()
  ioMult=CommandPipelineIo()
  ioMult(pars)

  # ---- Initializing Accumulator Block
  
  pipe_out_acc = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)
  parsAcc= AccumulatorPars()
  parsAcc.DATAWIDTH= pars.DATAWIDTH
  parsAcc.CHANNEL_WIDTH = pars.CHANNEL_WIDTH
  parsAcc.INIT_DATA = pars.INIT_DATA
  global LEN_THETA
  parsAcc.NB_ACCUMULATIONS = LEN_THETA  
  accuPipe= Accumulator() 
  accuPipe(parsAcc) 
  
  # ---- Initializing Activation Block
  
  parsActiv= ActivationPars()
  parsActiv.DATAWIDTH= 3    # 0 or 1 for classification
  parsActiv.CHANNEL_WIDTH = pars.CHANNEL_WIDTH
  parsActiv.INIT_DATA = pars.INIT_DATA
  pipe_out_activ = PipelineST(pars.DATAWIDTH,pars.CHANNEL_WIDTH,pars.INIT_DATA)
  activPipe= Activation() 
  activPipe(parsActiv) 
  #----------------------------------------------------------------
 
  #----------------- Connecting Pipeline Blocks -------------------
  
  inst=[]
  inst.append(operand_a.block_connect(pars, reset, clk, pipe_inpA, pipe_outA, ioA))
  inst.append(operand_b.block_connect(pars, reset, clk, pipe_inpB, pipe_outB, ioB))
  #----------------------------------------------------------------
 
  #----------------- Connecting Command Pipeline -------------------
  # Mult Pipeline 
  inst.append(multPipe.block_connect(parsMult, reset, clk, ioA, ioB, pipe_multRes, ioMult))   
 
  #----------------------------------------------------------------
  
  #----------------- Connecting Accumulator  --------------
  # Accu  
  inst.append(accuPipe.block_connect(parsAcc, reset, clk, 0, pipe_multRes, pipe_out_acc))   
 
  #----------------------------------------------------------------
  
  #----------------- Connecting Activation  --------------
  # Simple Step Activation function  
  inst.append(activPipe.block_step_connect(parsActiv, reset, clk, pipe_out_acc, pipe_out_activ ))   
 
  #----------------------------------------------------------------
 
  #----------------- Logistic Regression Test File -------------------
  
  lr_test_file="../tests/ex2data1.txt"
  lr_theta_file="../tests/theta1.txt"

  #--- Loading Test and Theta Values 
  
  test_file_list=[]
  theta_file_list=[]

  nb_training_examples=0
  # Loading test data
  with open(lr_test_file, 'r') as f:
    d0=1.0        # Always first element is 1
    
    for line in f:
      #print line
      d1,d2,y=line.split(',')
      d0=round(float(d0),DEF_ROUND)
      d1=round(float(d1),DEF_ROUND)
      d2=round(float(d2),DEF_ROUND)
      test_file_list.extend([d0,d1,d2])
      label.extend([int(y)])
      nb_training_examples+=1
    
  #loading theta
  with open(lr_theta_file, 'r') as f:
   t0,t1,t2=(f.read().split('\n')[0]).split(',')
   t0=round(float(t0),DEF_ROUND)
   t1=round(float(t1),DEF_ROUND)
   t2=round(float(t2),DEF_ROUND)
   for i in range(nb_training_examples): 
    theta_file_list.extend([t0,t1,t2])
  
  # exp10 shifts done for theta and test data as per requirements when intbv used 
  if (False == floatDataBus):
    test_file_list = [int(i*(10**test_decimal_shift)) for i in test_file_list] 
    theta_file_list = [int(i*(10**theta_decimal_shift)) for i in theta_file_list] 
  
  #print test_file_list      
  #print theta_file_list
  #----------------------------------------------------------------
  
  

  #----------------- Shift Enable for pipeData -------------------
  
  shiftEn_i = Signal(bool(0))
  @always(clk.posedge,reset.posedge)
  def shift_signal():
    if reset:
      shiftEn_i.next = 1
    else:
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
  
  @always_comb
  def transmit_data_process():
    global line_nb
    if (shiftEn_i == 1 and nbTA == nbTB and nbTA < MAX_NB_TRANSFERS):
      
      pipe_inpA.data.next = (test_file_list[line_nb])
      pipe_inpA.valid.next = 1
      pipe_inpB.data.next = (theta_file_list[line_nb])
      pipe_inpB.valid.next = 1
      line_nb+=1

    else: 
      pipe_inpA.valid.next = 0
      pipe_inpB.valid.next = 0
  
  #----------------------------------------------------------------

  #----------------- Storing Transmitted Data  --------------------
  
  @always(clk.posedge, reset.posedge)
  def trans_dataA_process():
    global trans_dataA,trans_dataB,nbTA
    if reset==1:
      pass
    elif (pipe_inpA.valid == 1 and nbTA < MAX_NB_TRANSFERS):
      nbTA+=1
      if (False == floatDataBus):
        trans_dataA.extend([pipe_inpA.data])
      else:
        trans_dataA.extend([pipe_inpA.data.next])

  
  @always(clk.posedge, reset.posedge)
  def trans_dataB_process():
    global trans_dataA,trans_dataB,nbTB
    if reset==1:
      pass
    elif (pipe_inpB.valid == 1 and nbTB < MAX_NB_TRANSFERS):
      nbTB+=1
      if (False == floatDataBus):
        trans_dataB.extend([pipe_inpB.data])
      else:
        trans_dataB.extend([pipe_inpB.data.next])
  
  #----------------------------------------------------------------
  
  #----------------- Storing Received Data  -----------------------
  
  @always(clk.posedge)
  def receive_data_process():
    global recv_data,nbR,acc_out
    
    # Collecting multiplier data
    if (pipe_multRes.valid == 1):
      if (False == floatDataBus):
        mult_out= pipe_multRes.data
      else:
        mult_out= (round(pipe_multRes.data,DEF_ROUND))
      recv_data.extend([mult_out])
   
    # Collecting Activation Data 
    if(pipe_out_activ.valid == 1):  
      nbR+=LEN_THETA
      predict = int(pipe_out_activ.data)                    
      prediction_res.extend([predict])
      if __debug__:
          print(" prediction: {:d}".format(predict) )
      if (nbR == MAX_NB_TRANSFERS):
        raise StopSimulation("Simulation Finished in %d clks: In total " %now() + str(MAX_NB_TRANSFERS) + " data words received")  

    
    # Collecting Accumulator Data 
    if(pipe_out_acc.valid == 1):  
      acc_out = pipe_out_acc.data
      #prob=(1.0/(1+ (math.exp(-1.0*acc_out) )))        # Sigmoid activation Function
      if __debug__:
        if (False == floatDataBus):
          print("{0:d} Acc: {1:d} ".format(nbR/LEN_THETA+1, int(acc_out), i=DEF_ROUND)),
        else:
          print("{0:d} Acc: {1:0.{i}f}".format(nbR/LEN_THETA+1, float(acc_out), i=DEF_ROUND)),
      if (False == floatDataBus):
        acc_out_list.extend([int(acc_out)])
      else:
        acc_out_list.extend([round(acc_out,DEF_ROUND)])
      #print "nbR:" + str(nbR) 
      sim_time_now=now()

  
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
  global trans_dataA, trans_dataB, recv_data,floatDataBus
  err_cnt=0
  trans_l=0
  rest_l=0
  recv_l=0 
  #print "Transmitted data A: ", str(trans_dataA)
  #print "Transmitted data B: ", str(trans_dataB)
  #print "Received data: ", str(recv_data)
  trans_lA=len(trans_dataA)
  trans_lB=len(trans_dataB)
  if trans_lA != trans_lB :
    print("ERR240: trans_lA does not match trans_lB. Quitting!")
    sys.exit()  
  recv_l=len(recv_data)
  rest_l=(trans_lA+trans_lB)/2-recv_l
  if (len(recv_data) < MAX_NB_TRANSFERS):
    print "ERR123: Expected number of data words not received! Received/Expected datawords: %d/%d " %(len(recv_data),MAX_NB_TRANSFERS) 
    print "ERR124: Simulation unsuccessful!."

  else:
    print "Total num transmitted data A= %d" % trans_lA  
    print "Total num transmitted data B= %d" % trans_lB  
    print "Total num received data= %d" % recv_l 
    for i in range(0,trans_lA):
      mismatch = True 
      if (False == floatDataBus):
        txA=trans_dataA[i]
        txB=trans_dataB[i]
        rx=recv_data[i]
        mismatch=True if (txA*txB != rx) else False
        if (True == mismatch):
          print "ERR309: i:{:d} Mult Mismatch! tx_dataA  {:d} tx_dataB= {:d} recv_data={:d}".format(i,int(txA),int(txB),int(rx))
          err_cnt+=1
      else:
        txA=round(trans_dataA[i],DEF_ROUND)
        txB=round(trans_dataB[i],DEF_ROUND)
        rx=round(recv_data[i],DEF_ROUND)
        mismatch=True if (round(txA*txB,DEF_ROUND) != rx) else False
        if (True == mismatch):
          print "ERR131: i:{:d} Mult Mismatch! tx_dataA  {:0.2f} tx_dataB= {:0.2f} recv_data={:0.2f}".format(i,txA,txB,rx)
          err_cnt+=1
    if (err_cnt):
      print "ERR134: Results not Matched. Simulation unsuccessful!"
    else:
      print "Mult Pipeline exactly matches..."
      nb_correct=0
      for i in range(len(prediction_res)):
        if(label[i] == prediction_res[i]):
          nb_correct+=1
      #print label,prediction_res,nb_correct
      tAcc=(100.0*nb_correct)/(len(prediction_res))   
      print("Predicted examples: {:d}".format(len(prediction_res))) 
      print("Expected Training Accuracy: 89.00% Measured: {:0.2f}% approx".format(tAcc)) 
      #print acc_out_list,max(acc_out_list),min(acc_out_list)
      if __debug__: 
        if (False == floatDataBus):
          print("Max acc_out_list: {:d} Min acc_out_list: {:d}" .format(max(acc_out_list),min(acc_out_list)))
        else:
          print("Max acc_out_list: {:0.{i}f} Min acc_out_list: {:0.{i}f}" .format(max(acc_out_list),min(acc_out_list),i=2))
        #print "Acc_out" + str(acc_out_list)
      print "Simulation Successful!"



