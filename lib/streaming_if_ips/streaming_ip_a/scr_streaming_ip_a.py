#!/usr/bin/env python3 
#
import os
import sys
import argparse
from myhdl import toVerilog, traceSignals, Simulation
from myhdl.conversion import analyze
from subprocess import call
#set paths for the required modules


#------------Project General Module Imports----------#
current_dir=os.getcwd()
myhdl_base=os.path.join(current_dir,"..")     #path to myhdl_base
sys.path.append(myhdl_base)
#import myhdl library
from scr.set_myhdl_lib_paths import set_myhdl_lib_paths 
# setup paths in myhdl lib
set_myhdl_lib_paths()
from testbench_parameters import pass_testbench, Valid
from myhdl_design_flow_libs import myhdl_module

#---Creating a myhdl module instance with all dir and set path information to all files----#
inst=myhdl_module(current_dir)

#----------Project Specific Module Imports------------#
from sim_streaming_ip_a import sim_streaming_ip_a, check_simulation_results
from streaming_ip_a_convert import streaming_ip_a_convert

#------script parameters------#
DEF_VALID_READY=0xffff
DEFAULT_SIM_TIME=2000
TB_NAME = 'sim_streaming_ip_a'           # test file
SYNTHESIS_TOP = 'syn_streaming_ip_a_top' # synthesis top level

#-------- systemverilog testbench script name.........#
SV_SIM_HDL_SCR = 'nrt01_fixed_valid_ready.sh'


#-------- Set all required file paths .........#
vcd_file="{:s}/{:s}{:s}".format(inst.sim_temp_dir, TB_NAME, inst.sim_vcd_file_ext)
sav_file = "{:s}/{:s}{:s}".format(inst.sim_wave_dirname, TB_NAME, inst.saved_vcd_file_ext)
qpf_file="{:s}/{:s}{:s}".format(inst.synthesis_dirname, SYNTHESIS_TOP, inst.synthesis_proj_file_ext)
sv_sim_scr="{:s}/{:s}/{:s}".format(inst.sim_hdl_dirname, inst.sim_hdl_scr_dirname, SV_SIM_HDL_SCR)


#------Local specific functions------#
def simulate(sim_temp_dir, sim_pattern_dir, valid_pattern, ready_pattern, nb_frames,sim_time=None):
  print("Start Myhdl Simulation....................................")
  cwd=os.getcwd()
  os.chdir(sim_temp_dir)
  inst.sim_defaults(sim_temp_dir)
  pars_obj=pass_testbench(sim_temp_dir,sim_pattern_dir,valid_pattern, ready_pattern, nb_frames,None)
  tb=traceSignals(sim_streaming_ip_a,pars_obj)
  sim=Simulation(tb)
  if (sim_time is None):
    sim.run()
  else:
    sim.run(sim_time)
  print("Simulation finished.................................")
  print("Checking Simulation results.................................")
  check_simulation_results(pars_obj)
  os.chdir(cwd)

#----------cli---------------#
def myhdl_module_cli():
  module_parser = argparse.ArgumentParser(description='Entry level script for the myhdl module.')
  module_parser.add_argument('--convert', '-c', action='store_true', default=False,
    help='Convert the myhdl module code to verilog')
  module_parser.add_argument('--simulate', '-s', action='store_true', default=False,
    help='Simulate the myhdl module, default scenario with single frame input stimuli')
  module_parser.add_argument('--valid', '-v', nargs='?',
    help='16 bit hex valid pattern to be used in simulation, default is ffff i.e. no idle cycles from the source')
  module_parser.add_argument('--ready', '-r', nargs='?',
    help='16 bit hex ready pattern to be used in simulation, default is ffff i.e. no back pressure from the sink')
  module_parser.add_argument('--sim_time', '-t', nargs='?',
    help='Time for which the simulation needs to run')
  module_parser.add_argument('--wave', '-w', action='store_true', default=False,
    help='Display the waveform')
  module_parser.add_argument('--synthesize', '-sy', action='store_true', default=False,
    help='Open the synthesize project for compiling and FPGA resources estimation')
  module_parser.add_argument('--simulatehdl', '-sh', action='store_true', default=False,
    help='Simulate the converted hdl code with systemverilog testbench')
  effective_args = sys.argv[1:]                           # all arguments after script name
  args = module_parser.parse_args(effective_args)
  nb_frames=1
  if args.convert:
    inst.convert_settings_defaults(inst.converted_hdl_dir)
    streaming_ip_a_convert()
  if args.simulate:
    valid_pattern = DEF_VALID_READY
    ready_pattern = DEF_VALID_READY
    sim_time = DEFAULT_SIM_TIME
    inst.remove_temp_files(inst.sim_temp_dir)       # remove previous files
    if args.valid:
      valid_pattern = int(args.valid,16)
    if args.ready:
      ready_pattern = int(args.ready,16)
    if args.sim_time:
      sim_time = int(args.sim_time)
      print("Valid pattern: ", str(hex(valid_pattern)))
      print("Ready pattern: ", str(hex(ready_pattern)))
      print("Simulation Time: ", str(sim_time)+" clocks")
    simulate(inst.sim_temp_dir, inst.sim_pattern_dirname, valid_pattern, ready_pattern, nb_frames, None)
  if args.wave:
    inst.wave(vcd_file,sav_file)
    print(" Wave not yet ready")
  if args.synthesize:
    inst.synthesize(qpf_file)
    print(" Synthesis not yet ready")
  if args.simulatehdl:
    print(sv_sim_scr)
    inst.sim_hdl(sv_sim_scr)
  
  return effective_args

#----------main---------------#
if __name__ == "__main__":
  myhdl_module_parser = myhdl_module_cli()
  
  if not myhdl_module_parser:
    sys.exit('No argument specified')

