import sys
import math

from myhdl import Signal, delay, always,always_comb, now, Simulation, traceSignals, instances, intbv,StopSimulation, block
from avalon_buses import PipelineST
from clk_driver import clk_driver

import subprocess

from logistic_regression import LogisticRegression, LogisticRegressionIo, LogisticRegressionPars


# Global Parameters-------------------------
# These pars control the data format
# floatDataBus = False for simulation in real scenario with intbv mult
# floatDataBus = True for simulation with floating point mult
floatDataBus=False

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
tap_mult = []
tap_data_accu = []
nbTA=0 # A global currently inevitable
nbTB=0 # A global currently inevitable
nbR=0 # A global currently inevitable

#-------------------------------------------

# Global Accumulator Output ----------------

acc_out = 0.0# PipelineST(pars.DATAWIDTH)
tap_accu=[]

#-------------------------------------------

# Other Globals------------------------------

label=[]
prediction_res=[]

#--------------------------------------------

@block
def sim_logistic_regression(pars_obj):

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
  pars=LogisticRegressionPars()
  pars.NB_PIPELINE_STAGES=NB_PIPELINE_STAGES
  pars.DATAWIDTH=DATAWIDTH
  pars.CHANNEL_WIDTH=2
  global floatDataBus
  if (True == floatDataBus):
    pars.INIT_DATA=0.0  # requires floating point computation
  else:
    pars.INIT_DATA=0    # requires intbv computation

  pars.CMD_FILE =  '../tests/mult_pipeline.list'
  pars.LEN_THETA  = LEN_THETA

  ioLR = LogisticRegressionIo()
  ioLR(pars)
  moduleLR=LogisticRegression()

  # --- Initializing Pipeline A
  pipe_inpA  = ioLR.pipe_inpA

  # --- Initializing Pipeline B
  pipe_inpB  = ioLR.pipe_inpB

  # --- Initializing Activation Out
  pipe_out_activ = ioLR.pipe_out_activ

  inst=[]
  #----------------- Connecting Logistic Regression Block--------------
  # Simple Step Activation function
  inst.append(moduleLR.block_connect(pars, reset, clk, pipe_inpA, pipe_inpB, pipe_out_activ ))

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

  shiftEn_i = Signal(bool(1))
  @always(clk.posedge,reset.posedge)
  def shift_signal():
    if reset:
      shiftEn_i.next = 1
    else:
      shiftEn_i.next = not shiftEn_i

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
      trans_dataA.extend([pipe_inpA.data])


  @always(clk.posedge, reset.posedge)
  def trans_dataB_process():
    global trans_dataA,trans_dataB,nbTB
    if reset==1:
      pass
    elif (pipe_inpB.valid == 1 and nbTB < MAX_NB_TRANSFERS):
      nbTB+=1
      trans_dataB.extend([pipe_inpB.data])

  #----------------------------------------------------------------

  #----------------- Storing Received Data  -----------------------

  @always(clk.posedge)
  def receive_data_process():
    global recv_data,tap_data_mmult,nbR,acc_out

    # Collecting multiplier data
    if (moduleLR.mult_out.valid == 1):
      if (False == floatDataBus):
        mult_out= moduleLR.mult_out.data
      else:
        mult_out= (round(float(moduleLR.mult_out.data),DEF_ROUND))
      tap_mult.extend([mult_out])

    # Collecting Accumulator Data
    if(moduleLR.accu_out.valid == 1):
      acc_out = moduleLR.accu_out.data
      #prob=(1.0/(1+ (math.exp(-1.0*acc_out) )))        # Sigmoid activation Function
      if __debug__:
        if (False == floatDataBus):
          print("{0:d} acc_out: {1:d} ".format(int(nbR/LEN_THETA+1), int(acc_out), i=DEF_ROUND))
        else:
          print("{0:d} acc_out: {1:0.{i}f}".format(int(nbR/LEN_THETA+1), float(acc_out), i=DEF_ROUND))
      if (False == floatDataBus):
        tap_accu.extend([int(acc_out)])
      else:
        tap_accu.extend([round(float(acc_out),DEF_ROUND)])


    # Collecting Activation Data
    if(pipe_out_activ.valid == 1):
      nbR+=LEN_THETA
      predict = int(pipe_out_activ.data)
      recv_data.extend([predict])
      fp=open("predict_op.log",'a')
      fp.write("{:d}\n".format(predict))
      fp.close()
      if __debug__:
          print("Prediction: {:d}".format(predict) )

      if (nbR == MAX_NB_TRANSFERS):
        raise StopSimulation("Simulation Finished in %d clks: In total " %now() + str(MAX_NB_TRANSFERS) + " data words transfered")


  #----------------------------------------------------------------

  #----------------- Max Simulation Time Exit Condition -----------

  @always(clk.posedge)
  def simulation_time_check():
    sim_time_now=now()
    if(sim_time_now>MAX_SIM_TIME):
        raise StopSimulation("Warning! Simulation Exited upon reaching max simulation time of " + str(MAX_SIM_TIME) + " clocks")

  #----------------------------------------------------------------
  return instances()

#@block
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
  nb_training_examples=(MAX_NB_TRANSFERS/LEN_THETA)
  if (len(recv_data) < nb_training_examples):
    print("ERR123: Expected number of data words not received! Received/Expected datawords: %d/%d " %(len(recv_data),nb_training_examples))
    print("ERR124: Simulation unsuccessful!.")

  else:
    print("Total num transmitted data A= %d" % trans_lA)
    print("Total num transmitted data B= %d" % trans_lB)
    print("Total num received data= {:d}, Length of one Training example = {:d}".format(recv_l,LEN_THETA))
    prediction_res=recv_data
    nb_correct=0
    for i in range(len(prediction_res)):
      if(label[i] == prediction_res[i]):
        nb_correct+=1
    #print label,prediction_res,nb_correct
    tAcc=(100.0*nb_correct)/(len(prediction_res))
    print("Predicted examples: {:d}".format(len(prediction_res)))
    print("Expected Training Accuracy: 89.00% Measured: {:0.2f}% approx".format(tAcc))
    if __debug__:
      if (False == floatDataBus):
        print("Max tap_accu: {:d} Min tap_accu: {:d}" .format(max(tap_accu),min(tap_accu)))
      else:
        print("Max tap_accu: {:0.{i}f} Min tap_accu: {:0.{i}f}" .format(max(tap_accu),min(tap_accu),i=2))
    print("Simulation Successful!")

