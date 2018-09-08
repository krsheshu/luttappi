import sys
from random import randrange
from myhdl import Signal, delay, always, now, Simulation, traceSignals, instance, intbv
from snk_bfm import snk_bfm
from clk_driver import clk_driver
from avalon_buses import AvalonST_SNK, AvalonST_SRC

valid_ready_pattern_width = 16
DATA_WIDTH = 8
nb2=int(0) # A global currently inevitable
recv_data = []

valid_i_pattern = int(sys.argv[1],valid_ready_pattern_width)
ready_i_pattern = int(sys.argv[2],valid_ready_pattern_width)

asi_snk = AvalonST_SNK(DATA_WIDTH)
src_bfm_o = AvalonST_SRC(DATA_WIDTH)

def sim_snk_bfm():

  reset= Signal(bool(0))
  clk = Signal(bool(0))
  elapsed_time=Signal(0)
  snk_bfm_inst = snk_bfm(reset, clk, ready_i_pattern, asi_snk, src_bfm_o )

  clkgen=clk_driver(elapsed_time,clk,period=20)

  @always(clk.posedge)
  def stimulus():
    if elapsed_time > 40:
      reset.next = 0
    if elapsed_time > 80:
      asi_snk.valid_i.next = 1
      asi_snk.data_i.next = 0xab
    if elapsed_time > 220:
      asi_snk.valid_i.next  = 0
      asi_snk.data_i.next = 0xab
    if elapsed_time > 320:
      asi_snk.valid_i.next = 1
      asi_snk.data_i.next = 0x1e


  @always(clk.posedge)
  def receive_data_process():
    global nb2
    global recv_data
    if (src_bfm_o.valid_o == 1):
      nb2+=1
      print str(nb2) + ". Received data:", ": ", src_bfm_o.data_o
      recv_data.append(int(src_bfm_o.data_o))

  return snk_bfm_inst, clkgen, stimulus,receive_data_process 


def simulate(timesteps):
  tb = traceSignals(sim_snk_bfm)
  sim = Simulation(tb)
  sim.run(timesteps)

simulate(2000)

