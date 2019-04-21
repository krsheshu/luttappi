import sys
import math

from myhdl import Signal, delay, always,always_comb, now, Simulation, traceSignals, instances, intbv,StopSimulation, block
from avalon_buses import PipelineST
from clk_driver import clk_driver

import subprocess


from logistic_regression import LogisticRegression, LogisticRegressionIo, LogisticRegressionPars


import scipy.io as sio
import cv2
import numpy as np
import random as rnd
import os

# Global Parameters-------------------------
# These pars control the data format
# floatDataBus = False for simulation in real scenario with intbv mult
# floatDataBus = True for simulation with floating point mult
floatDataBus=True

# NB_TRAINING_DATA - Controls the number of training data to be verified 
NB_TRAINING_DATA=5

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
LEN_THETA=401

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

label=np.zeros(NB_TRAINING_DATA)
prediction_res=np.zeros(NB_TRAINING_DATA)

#--------------------------------------------
NB_CLASSIFIERS=10

resY=np.zeros((NB_TRAINING_DATA,NB_CLASSIFIERS))
def displayAccOut(nbR,accu_in,i):
    # Collecting Accumulator Data 
    if(accu_in.valid == 1):  
      print("{}: nb:{}: accu_out{}: {} ".format(now(), nbR, i,accu_in.data))
      resY[nbR,i]=accu_in.data
      
  

@block
def sim_logistic_regression_2(pars_obj):

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

  ioLR0 = LogisticRegressionIo()
  ioLR0(pars)
  ioLR1 = LogisticRegressionIo()
  ioLR1(pars)
  ioLR2 = LogisticRegressionIo()
  ioLR2(pars)
  ioLR3 = LogisticRegressionIo()
  ioLR3(pars)
  ioLR4 = LogisticRegressionIo()
  ioLR4(pars)
  ioLR5 = LogisticRegressionIo()
  ioLR5(pars)
  ioLR6 = LogisticRegressionIo()
  ioLR6(pars)
  ioLR7 = LogisticRegressionIo()
  ioLR7(pars)
  ioLR8 = LogisticRegressionIo()
  ioLR8(pars)
  ioLR9 = LogisticRegressionIo()
  ioLR9(pars)

  moduleLR0=LogisticRegression()
  moduleLR1=LogisticRegression()
  moduleLR2=LogisticRegression()
  moduleLR3=LogisticRegression()
  moduleLR4=LogisticRegression()
  moduleLR5=LogisticRegression()
  moduleLR6=LogisticRegression()
  moduleLR7=LogisticRegression()
  moduleLR8=LogisticRegression()
  moduleLR9=LogisticRegression()

  # --- Initializing Pipeline A
  pipe_inpA  = ioLR0.pipe_inpA 
  
  # --- Initializing Pipeline B
  pipe_theta0  = ioLR0.pipe_inpB
  pipe_theta1  = ioLR1.pipe_inpB
  pipe_theta2  = ioLR2.pipe_inpB
  pipe_theta3  = ioLR3.pipe_inpB
  pipe_theta4  = ioLR4.pipe_inpB
  pipe_theta5  = ioLR5.pipe_inpB
  pipe_theta6  = ioLR6.pipe_inpB
  pipe_theta7  = ioLR7.pipe_inpB
  pipe_theta8  = ioLR8.pipe_inpB
  pipe_theta9  = ioLR9.pipe_inpB
  
  # --- Initializing Activation Out 
  pipe_out_activ0 = ioLR0.pipe_out_activ
  pipe_out_activ1 = ioLR1.pipe_out_activ
  pipe_out_activ2 = ioLR2.pipe_out_activ
  pipe_out_activ3 = ioLR3.pipe_out_activ
  pipe_out_activ4 = ioLR4.pipe_out_activ
  pipe_out_activ5 = ioLR5.pipe_out_activ
  pipe_out_activ6 = ioLR6.pipe_out_activ
  pipe_out_activ7 = ioLR7.pipe_out_activ
  pipe_out_activ8 = ioLR8.pipe_out_activ
  pipe_out_activ9 = ioLR9.pipe_out_activ

  #----------------- Connecting Logistic Regression Block--------------
  # Simple Step Activation function  
  inst0=(moduleLR0.block_connect(pars, reset, clk, pipe_inpA, pipe_theta0, pipe_out_activ0 ))   
  inst1=(moduleLR1.block_connect(pars, reset, clk, pipe_inpA, pipe_theta1, pipe_out_activ1 ))   
  inst2=(moduleLR2.block_connect(pars, reset, clk, pipe_inpA, pipe_theta2, pipe_out_activ2 ))   
  inst3=(moduleLR3.block_connect(pars, reset, clk, pipe_inpA, pipe_theta3, pipe_out_activ3 ))   
  inst4=(moduleLR4.block_connect(pars, reset, clk, pipe_inpA, pipe_theta4, pipe_out_activ4 ))   
  inst5=(moduleLR5.block_connect(pars, reset, clk, pipe_inpA, pipe_theta5, pipe_out_activ5 ))   
  inst6=(moduleLR6.block_connect(pars, reset, clk, pipe_inpA, pipe_theta6, pipe_out_activ6 ))   
  inst7=(moduleLR7.block_connect(pars, reset, clk, pipe_inpA, pipe_theta7, pipe_out_activ7 ))   
  inst8=(moduleLR8.block_connect(pars, reset, clk, pipe_inpA, pipe_theta8, pipe_out_activ8 ))   
  inst9=(moduleLR9.block_connect(pars, reset, clk, pipe_inpA, pipe_theta9, pipe_out_activ9 ))   
 
  #----------------------------------------------------------------
 
  #----------------- Logistic Regression Test File -------------------
  
  lr_test_file="../../model/ex3data1.mat"
  lr_theta_file="../../model/lR_weights.mat"

  pattern = sio.loadmat(lr_test_file)
  img=pattern['X']    # A numpy array 
  label=pattern['y'][:,0]   # A numpy array
  # Insert column of 1's for the input data for prediction / LR calculation
  imgRev=np.insert(img,0,1,axis=1)

  weights = sio.loadmat(lr_theta_file)   
  theta=weights['all_theta']      # A numpy array
  
  #--- Loading Test and Theta Values 
  
  test_file_list=imgRev.flatten()  # Flattenning all the rows for pipelines operation
  
  # exp10 shifts done for theta and test data as per requirements when intbv used 
  if (False == floatDataBus):
    test_file_list *= (10**test_decimal_shift)
    theta *= (10**theta_decimal_shift)
    test_file_list=test_file_list.astype(int)
    theta=theta.astype(int)
  
  theta_file0_list=[]
  theta_file1_list=[]
  theta_file2_list=[]
  theta_file3_list=[]
  theta_file4_list=[]
  theta_file5_list=[]
  theta_file6_list=[]
  theta_file7_list=[]
  theta_file8_list=[]
  theta_file9_list=[]
  for i in range(NB_TRAINING_DATA):
    theta_file0_list.extend(theta[0,:])
    theta_file1_list.extend(theta[1,:])
    theta_file2_list.extend(theta[2,:])
    theta_file3_list.extend(theta[3,:])
    theta_file4_list.extend(theta[4,:])
    theta_file5_list.extend(theta[5,:])
    theta_file6_list.extend(theta[6,:])
    theta_file7_list.extend(theta[7,:])
    theta_file8_list.extend(theta[8,:])
    theta_file9_list.extend(theta[9,:])

  
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
      pipe_theta0.data.next = (theta_file0_list[line_nb])
      pipe_theta0.valid.next = 1
      pipe_theta1.data.next = (theta_file1_list[line_nb])
      pipe_theta1.valid.next = 1
      pipe_theta2.data.next = (theta_file2_list[line_nb])
      pipe_theta2.valid.next = 1
      pipe_theta3.data.next = (theta_file3_list[line_nb])
      pipe_theta3.valid.next = 1
      pipe_theta4.data.next = (theta_file4_list[line_nb])
      pipe_theta4.valid.next = 1
      pipe_theta5.data.next = (theta_file5_list[line_nb])
      pipe_theta5.valid.next = 1
      pipe_theta6.data.next = (theta_file6_list[line_nb])
      pipe_theta6.valid.next = 1
      pipe_theta7.data.next = (theta_file7_list[line_nb])
      pipe_theta7.valid.next = 1
      pipe_theta8.data.next = (theta_file8_list[line_nb])
      pipe_theta8.valid.next = 1
      pipe_theta9.data.next = (theta_file9_list[line_nb])
      pipe_theta9.valid.next = 1
      line_nb+=1

    else: 
      pipe_inpA.valid.next = 0
      pipe_theta0.valid.next = 0
      pipe_theta1.valid.next = 0
      pipe_theta2.valid.next = 0
      pipe_theta3.valid.next = 0
      pipe_theta4.valid.next = 0
      pipe_theta5.valid.next = 0
      pipe_theta6.valid.next = 0
      pipe_theta7.valid.next = 0
      pipe_theta8.valid.next = 0
      pipe_theta9.valid.next = 0
  
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
    elif (pipe_theta0.valid == 1 and nbTB < MAX_NB_TRANSFERS):
      nbTB+=1
      trans_dataB.extend([pipe_theta0.data])
  
  #----------------------------------------------------------------
  
  #----------------- Storing Received Data  -----------------------
  
  @always(clk.posedge)
  def receive_data_process():
    global recv_data,tap_data_mmult,nbR,acc_out
    
    # Collecting multiplier data
    if (moduleLR0.mult_out.valid == 1):
      if (False == floatDataBus):
        mult_out= moduleLR0.mult_out.data
      else:
        mult_out= (round(float(moduleLR0.mult_out.data),DEF_ROUND))
      tap_mult.extend([mult_out])

    displayAccOut(nbR,moduleLR0.accu_out,0)
    displayAccOut(nbR,moduleLR1.accu_out,1)
    displayAccOut(nbR,moduleLR2.accu_out,2)
    displayAccOut(nbR,moduleLR3.accu_out,3)
    displayAccOut(nbR,moduleLR4.accu_out,4)
    displayAccOut(nbR,moduleLR5.accu_out,5)
    displayAccOut(nbR,moduleLR6.accu_out,6)
    displayAccOut(nbR,moduleLR7.accu_out,7)
    displayAccOut(nbR,moduleLR8.accu_out,8)
    displayAccOut(nbR,moduleLR9.accu_out,9)

    if (moduleLR9.accu_out.valid == 1):  
      nbR += 1
      if (nbR == NB_TRAINING_DATA):
        prediction_res=np.argmax(resY,axis=1) + 1 # +1 to correct indexing due to speciality of the example. See docs ex3.pdf 
        print(label,prediction_res)
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
def check_simulation_results_2(pars_obj):
  nb_correct=0
  for i in range(len(prediction_res)):
    if(label[i] == prediction_res[i]):
      nb_correct+=1
  print(label,prediction_res,nb_correct)
  tAcc=(100.0*nb_correct)/(len(prediction_res))   
  print("Predicted examples: {:d}".format(len(prediction_res)))
  print("Expected Training Accuracy: 94.90% Measured: {:0.2f}% approx".format(tAcc))
  print("Simulation Successful!")

