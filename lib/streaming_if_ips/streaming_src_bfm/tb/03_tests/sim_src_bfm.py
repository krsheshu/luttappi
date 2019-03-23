import sys
from random import randrange
from myhdl import Signal, delay, always, now, Simulation, traceSignals, instance, intbv
from src_bfm import src_bfm
from clk_driver import clk_driver
from avalon_buses import AvalonST_SRC, AvalonST_SNK

valid_ready_pattern_width = 16
DATA_WIDTH = 8

valid_i_pattern = int(sys.argv[1],valid_ready_pattern_width)
ready_i_pattern = int(sys.argv[2],valid_ready_pattern_width)

aso_src = AvalonST_SRC(DATA_WIDTH)
src_bfm_i = AvalonST_SNK(DATA_WIDTH)

def sim_src_bfm():

  reset = Signal(bool(1))
  clk = Signal(bool(0))
  src_bfm_i.data_i = Signal(intbv(0x0a)[DATA_WIDTH:])
  elapsed_time=Signal(0)
  src_bfm_inst = src_bfm(reset, clk,
                         valid_i_pattern,
                         src_bfm_i,
                         aso_src)
  class num_counter:
    nb = 0

  clkgen=clk_driver(elapsed_time,clk,period=20)

  @always(clk.posedge)
  def stimulus():
    if elapsed_time > 40:
      reset.next = 0
    if elapsed_time > 100:
      aso_src.ready_i.next = 1
    if elapsed_time > 140:
      aso_src.ready_i.next = 0
    if elapsed_time > 220:
      aso_src.ready_i.next = 1
    if elapsed_time > 240:
      aso_src.ready_i.next = 0
    if elapsed_time > 400:
      aso_src.ready_i.next = 1

  @always(clk.posedge)
  def data_increment():
    if aso_src.ready_i==1 and  aso_src.valid_o == 1:
      src_bfm_i.data_i.next = src_bfm_i.data_i + 1
      num_counter.nb+=1
      print(str(num_counter.nb) + ". Prepared data:", hex(src_bfm_i.data_i), ": ",src_bfm_i.data_i) 
  
  return src_bfm_inst, clkgen, stimulus, data_increment


def simulate(timesteps):
  tb = traceSignals(sim_src_bfm)
  sim = Simulation(tb)
  sim.run(timesteps)

simulate(2000)

