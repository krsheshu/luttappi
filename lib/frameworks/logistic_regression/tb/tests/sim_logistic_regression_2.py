import sys
import math
import myhdl
from avalon_buses import PipelineST
from clk_driver import clk_driver

import subprocess

from logistic_regression import LogisticRegression
from lr2_model import LogisticRegression1vsAllModel

import cv2
import numpy as np
import os

# Global Parameters-------------------------
# These pars control the data format
# floatDataBus = False for simulation in real scenario with myhdl.intbv mult
# floatDataBus = True for simulation with floating point mult
floatDataBus = False

# NB_TRAINING_SAMPLES - Controls the number of training data to be verified
NB_TRAINING_SAMPLES = 16

# When using myhdl.intbv for the data (not the floating point simulation),
# determine the decimal shift needed in the theta and training data parameters
# For example, for training data 32.5, a shift of 1 will use value of 325 for myhdl.intbv representation
#              for theta value of -25.21, a shift of 2 will use -2521 for theta value
test_decimal_shift = 1
theta_decimal_shift = 1

# -------------------------------------------

# Globals ----------------------------------

DEF_ROUND = 1  # Applicable only when float test data is used
line_nb = 0
LEN_THETA = 401

# -------------------------------------------

# Transmit Receive Parameters---------------

MAX_SIM_TIME = LEN_THETA * 10000
MAX_NB_TRANSFERS = NB_TRAINING_SAMPLES * LEN_THETA
trans_dataA = []
trans_dataB = []
recv_data = []
tap_mult = []
tap_data_accu = []
nbTA = 0  # A global currently inevitable
nbTB = 0  # A global currently inevitable
nbR = 0  # A global currently inevitable

# -------------------------------------------

# Global Accumulator Output ----------------

acc_out = 0.0  # PipelineST(pars.DATAWIDTH)
tap_accu = []

# -------------------------------------------

# Other Globals------------------------------

label = np.zeros(NB_TRAINING_SAMPLES, np.uint8)
prediction_res = np.zeros(NB_TRAINING_SAMPLES, np.uint8)

# --------------------------------------------
NB_CLASSIFIERS = 10

resY = np.zeros((NB_TRAINING_SAMPLES, NB_CLASSIFIERS))


def displayAccOut(nbR, accu_in, i):
    # Collecting Accumulator Data
    if accu_in.valid == 1:
        print("{}: nb:{}: accu_out{}: {} ".format(myhdl.now(), nbR, i,
                                                  accu_in.data))
        resY[nbR, i] = accu_in.data


@myhdl.block
def sim_logistic_regression_2(pars_obj):

    global test_decimal_shift, theta_decimal_shift

    # ------------------ Initializing Pipeline depths ---------------

    NB_PIPELINE_STAGES = 5
    DATAWIDTH = 32
    # -------------- Simulation Initialisations ---------------------

    reset = myhdl.Signal(bool(1))
    clk = myhdl.Signal(bool(0))
    elapsed_time = myhdl.Signal(0)

    clkgen = clk_driver(elapsed_time, clk, period=20)

    # ----------------------------------------------------------------

    # ----------------- Initializing Pipeline Streams ----------------

    # --- Pipeline Pars
    CHANNEL_WIDTH = 2
    FLOAT_INIT_DATA = 0.0
    INT_INIT_DATA = 0
    global floatDataBus
    if True == floatDataBus:
        INIT_DATA = FLOAT_INIT_DATA  # requires floating point computation
    else:
        INIT_DATA = INT_INIT_DATA  # requires myhdl.intbv computation

    CMD_FILE = "../tests/mult_pipeline.list"

    moduleLR0 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)
    moduleLR1 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)
    moduleLR2 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)
    moduleLR3 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)
    moduleLR4 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)
    moduleLR5 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)
    moduleLR6 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)
    moduleLR7 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)
    moduleLR8 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)
    moduleLR9 = LogisticRegression(NB_PIPELINE_STAGES, DATAWIDTH,
                                   CHANNEL_WIDTH, INIT_DATA, LEN_THETA,
                                   CMD_FILE)

    # --- Initializing Pipeline A
    pipe_inpA = moduleLR0.pipeST_A_i

    # --- Initializing Pipeline B
    pipe_theta0 = moduleLR0.pipeST_B_i
    pipe_theta1 = moduleLR1.pipeST_B_i
    pipe_theta2 = moduleLR2.pipeST_B_i
    pipe_theta3 = moduleLR3.pipeST_B_i
    pipe_theta4 = moduleLR4.pipeST_B_i
    pipe_theta5 = moduleLR5.pipeST_B_i
    pipe_theta6 = moduleLR6.pipeST_B_i
    pipe_theta7 = moduleLR7.pipeST_B_i
    pipe_theta8 = moduleLR8.pipeST_B_i
    pipe_theta9 = moduleLR9.pipeST_B_i

    # --- Initializing Activation Out
    pipe_out_activ0 = moduleLR0.pipeST_o
    pipe_out_activ1 = moduleLR1.pipeST_o
    pipe_out_activ2 = moduleLR2.pipeST_o
    pipe_out_activ3 = moduleLR3.pipeST_o
    pipe_out_activ4 = moduleLR4.pipeST_o
    pipe_out_activ5 = moduleLR5.pipeST_o
    pipe_out_activ6 = moduleLR6.pipeST_o
    pipe_out_activ7 = moduleLR7.pipeST_o
    pipe_out_activ8 = moduleLR8.pipeST_o
    pipe_out_activ9 = moduleLR9.pipeST_o

    # ----------------- Connecting Logistic Regression Block--------------
    # Simple Step Activation function
    inst0 = moduleLR0.top(reset, clk, pipe_inpA, pipe_theta0, pipe_out_activ0)
    inst1 = moduleLR1.top(reset, clk, pipe_inpA, pipe_theta1, pipe_out_activ1)
    inst2 = moduleLR2.top(reset, clk, pipe_inpA, pipe_theta2, pipe_out_activ2)
    inst3 = moduleLR3.top(reset, clk, pipe_inpA, pipe_theta3, pipe_out_activ3)
    inst4 = moduleLR4.top(reset, clk, pipe_inpA, pipe_theta4, pipe_out_activ4)
    inst5 = moduleLR5.top(reset, clk, pipe_inpA, pipe_theta5, pipe_out_activ5)
    inst6 = moduleLR6.top(reset, clk, pipe_inpA, pipe_theta6, pipe_out_activ6)
    inst7 = moduleLR7.top(reset, clk, pipe_inpA, pipe_theta7, pipe_out_activ7)
    inst8 = moduleLR8.top(reset, clk, pipe_inpA, pipe_theta8, pipe_out_activ8)
    inst9 = moduleLR9.top(reset, clk, pipe_inpA, pipe_theta9, pipe_out_activ9)

    # ----------------------------------------------------------------

    # ----------------- Logistic Regression Test File -------------------

    lr_test_file = "../../model/ex3data1.mat"
    lr_theta_file = "../../model/lR_weights.mat"

    model = LogisticRegression1vsAllModel()
    imgArray, label, theta, modelPredict = model.get(
        nbClassifyImages=NB_TRAINING_SAMPLES)

    # --- Loading Test and Theta Values

    test_file_list = (imgArray.flatten()
                      )  # Flattenning all the rows for pipelines operation

    # exp10 shifts done for theta and test data as per requirements when myhdl.intbv used
    if False == floatDataBus:
        test_file_list *= 10**test_decimal_shift
        theta *= 10**theta_decimal_shift
        test_file_list = test_file_list.astype(int)
        theta = theta.astype(int)

    theta_file0_list = []
    theta_file1_list = []
    theta_file2_list = []
    theta_file3_list = []
    theta_file4_list = []
    theta_file5_list = []
    theta_file6_list = []
    theta_file7_list = []
    theta_file8_list = []
    theta_file9_list = []

    for i in range(NB_TRAINING_SAMPLES):
        theta_file0_list.extend(theta[0, :])
        theta_file1_list.extend(theta[1, :])
        theta_file2_list.extend(theta[2, :])
        theta_file3_list.extend(theta[3, :])
        theta_file4_list.extend(theta[4, :])
        theta_file5_list.extend(theta[5, :])
        theta_file6_list.extend(theta[6, :])
        theta_file7_list.extend(theta[7, :])
        theta_file8_list.extend(theta[8, :])
        theta_file9_list.extend(theta[9, :])

    # print test_file_list
    # print theta_file_list
    # ----------------------------------------------------------------

    # ----------------- Shift Enable for pipeData -------------------

    shiftEn_i = myhdl.Signal(bool(1))

    @myhdl.always(clk.posedge, reset.posedge)
    def shift_Signal():
        if reset:
            shiftEn_i.next = 1
        else:
            shiftEn_i.next = not shiftEn_i

    # ----------------------------------------------------------------

    # ----------------- Reset For the Module  --------------------

    @myhdl.always(clk.posedge)
    def stimulus():
        if elapsed_time == 40:
            reset.next = 0

    # ----------------------------------------------------------------

    # ----------------- Input Data for the Modules  --------------------

    @myhdl.always_comb
    def transmit_data_process():
        global line_nb
        if shiftEn_i == 1 and nbTA == nbTB and nbTA < MAX_NB_TRANSFERS:

            pipe_inpA.data.next = test_file_list[line_nb] if floatDataBus == True else int(test_file_list[line_nb])
            pipe_inpA.valid.next = 1
            pipe_theta0.data.next = theta_file0_list[line_nb] if floatDataBus == True else int(theta_file0_list[line_nb])
            pipe_theta0.valid.next = 1
            pipe_theta1.data.next = theta_file1_list[line_nb] if floatDataBus == True else int(theta_file1_list[line_nb])
            pipe_theta1.valid.next = 1
            pipe_theta2.data.next = theta_file2_list[line_nb] if floatDataBus == True else int(theta_file2_list[line_nb])
            pipe_theta2.valid.next = 1
            pipe_theta3.data.next = theta_file3_list[line_nb] if floatDataBus == True else int(theta_file3_list[line_nb])
            pipe_theta3.valid.next = 1
            pipe_theta4.data.next = theta_file4_list[line_nb] if floatDataBus == True else int(theta_file4_list[line_nb])
            pipe_theta4.valid.next = 1
            pipe_theta5.data.next = theta_file5_list[line_nb] if floatDataBus == True else int(theta_file5_list[line_nb])
            pipe_theta5.valid.next = 1
            pipe_theta6.data.next = theta_file6_list[line_nb] if floatDataBus == True else int(theta_file6_list[line_nb])
            pipe_theta6.valid.next = 1
            pipe_theta7.data.next = theta_file7_list[line_nb] if floatDataBus == True else int(theta_file7_list[line_nb])
            pipe_theta7.valid.next = 1
            pipe_theta8.data.next = theta_file8_list[line_nb] if floatDataBus == True else int(theta_file8_list[line_nb])
            pipe_theta8.valid.next = 1
            pipe_theta9.data.next = theta_file9_list[line_nb] if floatDataBus == True else int(theta_file9_list[line_nb])
            pipe_theta9.valid.next = 1
            line_nb += 1

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

    # ----------------------------------------------------------------

    # ----------------- Storing Transmitted Data  --------------------

    @myhdl.always(clk.posedge, reset.posedge)
    def trans_dataA_process():
        global trans_dataA, trans_dataB, nbTA
        if reset == 1:
            pass
        elif pipe_inpA.valid == 1 and nbTA < MAX_NB_TRANSFERS:
            nbTA += 1
            trans_dataA.extend([pipe_inpA.data])

    @myhdl.always(clk.posedge, reset.posedge)
    def trans_dataB_process():
        global trans_dataA, trans_dataB, nbTB
        if reset == 1:
            pass
        elif pipe_theta0.valid == 1 and nbTB < MAX_NB_TRANSFERS:
            nbTB += 1
            trans_dataB.extend([pipe_theta0.data])

    # ----------------------------------------------------------------

    # ----------------- Storing Received Data  -----------------------

    @myhdl.always(clk.posedge)
    def receive_data_process():
        global recv_data, tap_data_mmult, nbR, acc_out, prediction_res

        ## Collecting multiplier data
        # if (moduleLR0.pipe_multRes.valid == 1):
        #  if (False == floatDataBus):
        #    pipe_multRes= moduleLR0.pipe_multRes.data
        #  else:
        #    pipe_multRes= (round(float(moduleLR0.pipe_multRes.data),DEF_ROUND))
        #  tap_mult.extend([pipe_multRes])

        displayAccOut(nbR, moduleLR0.pipe_out_acc, 0)
        displayAccOut(nbR, moduleLR1.pipe_out_acc, 1)
        displayAccOut(nbR, moduleLR2.pipe_out_acc, 2)
        displayAccOut(nbR, moduleLR3.pipe_out_acc, 3)
        displayAccOut(nbR, moduleLR4.pipe_out_acc, 4)
        displayAccOut(nbR, moduleLR5.pipe_out_acc, 5)
        displayAccOut(nbR, moduleLR6.pipe_out_acc, 6)
        displayAccOut(nbR, moduleLR7.pipe_out_acc, 7)
        displayAccOut(nbR, moduleLR8.pipe_out_acc, 8)
        displayAccOut(nbR, moduleLR9.pipe_out_acc, 9)

        if moduleLR9.pipe_out_acc.valid == 1:
            nbR += 1
            if nbR == NB_TRAINING_SAMPLES:
                prediction_res = (
                    np.argmax(resY, axis=1) + 1
                )  # +1 to correct indexing due to speciality of the example. See docs ex3.pdf
                for i in range(len(prediction_res)):
                    prediction_res[i] = (0 if prediction_res[i] == 10 else
                                         prediction_res[i])
                print("label: {} prediction: {}".format(label, prediction_res))
                raise myhdl.StopSimulation(
                    "Simulation Finished in %d clks: In total " % myhdl.now() +
                    str(MAX_NB_TRANSFERS) + " data words transfered")

    # ----------------------------------------------------------------

    # ----------------- Max Simulation Time Exit Condition -----------

    @myhdl.always(clk.posedge)
    def simulation_time_check():

        sim_time_now = myhdl.now()
        if sim_time_now > MAX_SIM_TIME:
            raise myhdl.StopSimulation(
                "Warning! Simulation Exited upon reaching max simulation time of "
                + str(MAX_SIM_TIME) + " clocks")

    # ----------------------------------------------------------------
    return myhdl.instances()


# @myhdl.block
def check_simulation_results_2(pars_obj, display=False):
    global prediction_res

    assert (math.sqrt(NB_TRAINING_SAMPLES) %
            1 == 0), "ERR377: nb Classify images not power of 2!"

    nbImages1Row = int(math.sqrt(NB_TRAINING_SAMPLES))
    nbImages1Col = int(math.sqrt(NB_TRAINING_SAMPLES))

    print(prediction_res)
    fpgaPredictImgName = "fpgaPrediction.png"
    predictFullImg = LogisticRegression1vsAllModel.nbArray2Image_convert(
        None, prediction_res, nbImages1Col, nbImages1Row, fpgaPredictImgName)
    print("FPGA Prediction image saved as {}".format(fpgaPredictImgName))

    nb_correct = 0
    for i in range(len(prediction_res)):
        if label[i] == prediction_res[i]:
            nb_correct += 1
    # print(label,prediction_res,nb_correct)
    tAcc = (100.0 * nb_correct) / (len(prediction_res))
    print("Predicted examples: {:d}".format(len(prediction_res)))
    print(
        "Expected Training Accuracy: 94.90% Measured: {:0.2f}% approx. nb_samples: {}"
        .format(tAcc, len(prediction_res)))
    print("Simulation Successful!")

    if display == True:
        fpgaPredictI = cv2.imread("../myhdl_work/fpgaPrediction.png",
                                  cv2.IMREAD_UNCHANGED)
        sampleI = cv2.imread("../../model/sampleImages.tif",
                             cv2.IMREAD_UNCHANGED)
        modelPredictI = cv2.imread("../../model/modelPrediction.tif",
                                   cv2.IMREAD_UNCHANGED)
        cv2.imshow("Sample Images", sampleI)
        cv2.imshow("Predicted Model", modelPredictI)
        cv2.imshow("FPGA Prediction Result", fpgaPredictI)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
