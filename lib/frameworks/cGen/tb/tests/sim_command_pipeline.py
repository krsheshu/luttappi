import sys
import math

from myhdl import Signal, delay, always, always_comb, now, Simulation, traceSignals, instances, intbv, StopSimulation, block
from avalon_buses import PipelineST
from clk_driver import clk_driver

import subprocess

from operand_pipeline import OperandPipeline, OperandPipelinePars, OperandPipelineIo
from command_pipeline import CommandPipeline, CommandPipelinePars, CommandPipelineIo


# Globals ----------------------------------

line_nb = Signal(0)

i = 0
pipeLog = "pipeline_log,txt"
# -------------------------------------------

# Transmit Receive Parameters---------------

MAX_SIM_TIME = 10000
MAX_NB_TRANSFERS = 10
trans_dataA = []
trans_dataB = []
recv_data = []
nbTA = 0  # A global currently inevitable
nbTB = 0  # A global currently inevitable
nbR = 0  # A global currently inevitable

# -------------------------------------------

# --------------------------------------------


@block
def sim_command_pipeline(pars_obj):

    # ------------------ Initializing Pipeline depths ---------------

    NB_PIPELINE_STAGES = 5
    DATAWIDTH = 32
    # -------------- Simulation Initialisations ---------------------

    reset = Signal(bool(1))
    clk = Signal(bool(0))
    elapsed_time = Signal(0)

    clkgen = clk_driver(elapsed_time, clk, period=20)

    # ----------------------------------------------------------------

    # ----------------- Initializing Pipeline Streams ----------------

    # --- Pipeline Pars
    pars = OperandPipelinePars()
    pars.NB_PIPELINE_STAGES = NB_PIPELINE_STAGES
    pars.DATAWIDTH = DATAWIDTH
    pars.CHANNEL_WIDTH = 2
    pars.INIT_DATA = 0    # requires intbv computation

    # --- Initializing Pipeline A
    pipe_inpA = PipelineST(pars.DATAWIDTH, pars.CHANNEL_WIDTH, pars.INIT_DATA)
    pipe_outA = PipelineST(pars.DATAWIDTH, pars.CHANNEL_WIDTH, pars.INIT_DATA)

    operand_a = OperandPipeline()
    ioA = OperandPipelineIo()
    ioA(pars)

    # --- Initializing Pipeline B
    pipe_inpB = PipelineST(pars.DATAWIDTH, pars.CHANNEL_WIDTH, pars.INIT_DATA)
    pipe_outB = PipelineST(pars.DATAWIDTH, pars.CHANNEL_WIDTH, pars.INIT_DATA)

    operand_b = OperandPipeline()
    ioB = OperandPipelineIo()
    ioB(pars)

    # --- Initializing Command Pipeline
    pipe_multRes = PipelineST(
        pars.DATAWIDTH, pars.CHANNEL_WIDTH, pars.INIT_DATA)
    multcmdFile = '../tests/mult_pipeline.list'
    parsMult = CommandPipelinePars()
    parsMult.DATAWIDTH = pars.DATAWIDTH
    parsMult.CHANNEL_WIDTH = pars.CHANNEL_WIDTH
    parsMult.INIT_DATA = pars.INIT_DATA
    parsMult.STAGE_NB = 3
    parsMult(parsMult, multcmdFile)
    multPipe = CommandPipeline()
    ioMult = CommandPipelineIo()
    ioMult(pars)

    # ----------------------------------------------------------------

    # ----------------- Connecting Pipeline Blocks -------------------

    inst = []
    inst.append(operand_a.block_connect(
        pars, reset, clk, pipe_inpA, pipe_outA, ioA))
    inst.append(operand_b.block_connect(
        pars, reset, clk, pipe_inpB, pipe_outB, ioB))
    # ----------------------------------------------------------------

    # ----------------- Connecting Command Pipeline -------------------
    # Mult Pipeline
    inst.append(multPipe.block_connect(parsMult, reset,
                                       clk, ioA, ioB, pipe_multRes, ioMult))

    # ----------------------------------------------------------------

    # ----------------------- Pipeline Log  --------------------------

    @always(clk.posedge, reset.posedge)
    def pipeLog():
        global i, pipeLog
        if reset:
            pass
        else:
            i += 1
            if pipe_multRes.valid == 1 or pipe_outA.valid == 1 or pipe_outB.valid == 1:
                f = open(pipeLog, "a")
                f.write("\nClk nb: {:3} -> ".format(i))

            if pipe_outA.valid == 1:
                f.write("outA: {:>5} | ".format(str(int(pipe_outA.data))))

            if pipe_outB.valid == 1:
                f.write("outB: {:>5} | ".format(str(int(pipe_outB.data))))

            if pipe_multRes.valid == 1:
                if pipe_outA.valid == 1:
                    f.write("mult: {:>5}".format(str(int(pipe_multRes.data))))
                else:
                    f.write(
                        " "*28 + "mult: {:>5}".format(str(int(pipe_multRes.data))))

            if pipe_multRes.valid == 1 or pipe_outA.valid == 1 or pipe_outB.valid == 1:
                f.close()
    # ----------------------------------------------------------

    # ------------------------- Load List ----------------------------

    pixVal_file = "../tests/pixVal.txt"
    index_file = "../tests/index.txt"

    # --- Loading the two mult list values

    pixVal_list = []
    index_list = []

    # Loading test data
    with open(pixVal_file, 'r') as f:
        for line in f:
            line = line.rstrip()
            pixVal_list.append(int(line))

    # loading theta
    with open(index_file, 'r') as f:
        for line in f:
            line = line.rstrip()
            index_list.append(int(line))

    # print(pixVal_list)
    # print(index_list)
    # ----------------------------------------------------------------

    # ----------------- Shift Enable for pipeData -------------------

    shiftEn_i = Signal(bool(0))
    @always(clk.posedge, reset.posedge)
    def shift_signal():
        if reset:
            shiftEn_i.next = 1
        else:
            shiftEn_i.next = 1  # not shiftEn_i

    # ----------------------------------------------------------------

    # ----------------- Reset For the Module  --------------------

    @always(clk.posedge)
    def stimulus():
        if elapsed_time == 40:
            reset.next = 0

    # ----------------------------------------------------------------

    # ----------------- Input Data for the Modules  --------------------

    @always(clk.posedge, reset.posedge)
    def transmit_data_process():
        global line_nb
        if reset:
            pipe_inpA.valid.next = 0
            pipe_inpB.valid.next = 0
        else:
            if (shiftEn_i == 1 and nbTA == nbTB and nbTA < MAX_NB_TRANSFERS):

                pipe_inpA.data.next = (pixVal_list[line_nb])
                pipe_inpA.valid.next = 1
                pipe_inpB.data.next = (index_list[line_nb])
                pipe_inpB.valid.next = 1
                line_nb.next = line_nb + 1
                ioB.shiftEn_i.next = shiftEn_i
                ioA.shiftEn_i.next = shiftEn_i

            else:
                pipe_inpA.valid.next = 0
                pipe_inpB.valid.next = 0
                ioB.shiftEn_i.next = 0
                ioA.shiftEn_i.next = 0

    # ----------------------------------------------------------------

    # ----------------- Storing Transmitted Data  --------------------

    @always(clk.posedge, reset.posedge)
    def trans_dataA_process():
        global trans_dataA, trans_dataB, nbTA
        if reset == 1:
            pass
        elif (pipe_inpA.valid == 1 and nbTA < MAX_NB_TRANSFERS):
            nbTA += 1
            trans_dataA.append(int(pipe_inpA.data))

    @always(clk.posedge, reset.posedge)
    def trans_dataB_process():
        global trans_dataA, trans_dataB, nbTB
        if reset == 1:
            pass
        elif (pipe_inpB.valid == 1 and nbTB < MAX_NB_TRANSFERS):
            nbTB += 1
            trans_dataB.append(int(pipe_inpB.data))

    # ----------------------------------------------------------------

    # ----------------- Storing Received Data  -----------------------

    @always(clk.posedge)
    def receive_data_process():
        global recv_data, nbR

        # Collecting multiplier data
        if (pipe_multRes.valid == 1):
            mult_out = pipe_multRes.data
            recv_data.append(int(mult_out))

    # ----------------------------------------------------------------

    # ----------------- Max Simulation Time Exit Condition -----------

    @always(clk.posedge)
    def simulation_time_check():
        sim_time_now = now()
        if(sim_time_now > MAX_SIM_TIME):
            raise StopSimulation(
                "Warning! Simulation Exited upon reaching max simulation time of " + str(MAX_SIM_TIME) + " clocks")

    # ----------------------------------------------------------------
    return instances()


def check_simulation_results(pars_obj):
    global trans_dataA, trans_dataB, recv_data
    err_cnt = 0
    trans_l = 0
    rest_l = 0
    recv_l = 0
    print("Transmitted data A: {} ".format(str(trans_dataA)))
    print("Transmitted data B: {}".format(str(trans_dataB)))
    print("Received data: {}".format(str(recv_data)))
