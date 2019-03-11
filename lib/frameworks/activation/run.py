#!/usr/bin/env python 
#
import os
import sys
import argparse
from myhdl import toVerilog, traceSignals, Simulation
from myhdl.conversion import analyze
from subprocess import call


#------------Project General Module Imports----------#
#set paths for the required modules
current_dir=os.getcwd()
from scr.set_myhdl_lib_paths import set_myhdl_lib_paths 
# setup paths in myhdl lib
set_myhdl_lib_paths()
from testbench_parameters import pass_testbench, Valid
from myhdl_bridge_lib import MyhdlBridgeLib

#---Creating a myhdl module instance with all dir and set path information to all files----#
inst=MyhdlBridgeLib(current_dir)
valid=Valid()
#----------Project Specific Module Imports------------#
from sim_activation import sim_activation, check_simulation_results
#from activation_convert import activation_convert

#------script parameters------#
DEF_VALID_READY=0xffff
DEFAULT_SIM_TIME=2000
TB_NAME = 'sim_activation'           # test file
SYNTHESIS_TOP = 'syn_activation_top' # synthesis top level

#-------- systemverilog testbench script name.........#
SV_SIM_HDL_SCR = 'nrt01_fixed_valid_ready.sh'


#-------- Set all required file paths .........#
vcd_file="{:s}/{:s}{:s}".format(inst.sim_temp_dir, TB_NAME, inst.sim_vcd_file_ext)
sav_file = "{:s}/{:s}{:s}".format(inst.sim_wave_dirname, TB_NAME, inst.saved_vcd_file_ext)
qpf_file="{:s}/{:s}{:s}".format(inst.synthesis_dirname, SYNTHESIS_TOP, inst.synthesis_proj_file_ext)
sv_sim_scr="{:s}/{:s}/{:s}".format(inst.sim_hdl_dirname, inst.sim_hdl_scr_dirname, SV_SIM_HDL_SCR)

#------Local specific functions------#
def simulate(sim_temp_dir, sim_pattern_dir, valid_pattern, ready_pattern, nb_frames,sim_time=None):
  print "Start Myhdl Simulation...................................."
  cwd=os.getcwd()
  os.chdir(sim_temp_dir)
  inst.sim_defaults(sim_temp_dir)
  pars_obj=pass_testbench(sim_temp_dir,sim_pattern_dir,valid_pattern, ready_pattern, nb_frames,None)
  tb=traceSignals(sim_activation,pars_obj)
  sim=Simulation(tb)
  if (sim_time is None):
    sim.run()
  else:
    sim.run(sim_time)
  print "Simulation finished................................."
  print "Checking Simulation results................................."
  check_simulation_results(pars_obj)
  os.chdir(cwd)

#----------cli---------------#
def myhdl_module_cli():
  module_parser = argparse.ArgumentParser(description='Entry level script for the myhdl module.')
  module_parser.add_argument('--convert', '-c', action='store_true', default=False,
    help='Convert the myhdl module code to verilog')
  module_parser.add_argument('--simulate', '-s', action='store_true', default=False,
    help='Simulate the myhdl module, default scenario with single frame input stimuli')
  module_parser.add_argument('--valid0', '-v', nargs='?',
    help='16 bit hex valid pattern to be used in simulation, default is ffff i.e. no idle cycles from the source')
  module_parser.add_argument('--valid1', '-V', nargs='?',
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
    #activation_convert()
  if args.simulate:
    valid.pattern0 = DEF_VALID_READY
    valid.pattern1= DEF_VALID_READY 
    ready_pattern = DEF_VALID_READY
    sim_time = DEFAULT_SIM_TIME
    inst.remove_temp_files(inst.sim_temp_dir)       # remove previous files
    if args.valid0:
      valid.pattern0 = int(args.valid0,16)
    if args.valid1:
      valid.pattern1 = int(args.valid1,16)
    if args.ready:
      ready_pattern = int(args.ready,16)
    if args.sim_time:
      print "Valid pattern0: ", str(hex(valid.pattern0))
      print "Valid pattern1: ", str(hex(valid.pattern1))
      print "Ready pattern: ", str(hex(ready.pattern))
      sim_time = int(args.sim_time)
      print "Simulation Time: ", str(sim_time)+" clocks"
    simulate(inst.sim_temp_dir, inst.sim_pattern_dirname, valid, ready_pattern, nb_frames, None)
  if args.wave:
    inst.wave(vcd_file,sav_file)
    print " Wave not yet ready"
  if args.synthesize:
    inst.synthesize(qpf_file)
    print " Synthesis not yet ready"
  if args.simulatehdl:
    print sv_sim_scr
    inst.sim_hdl(sv_sim_scr)
  
  return effective_args

#----------main---------------#
if __name__ == "__main__":
  myhdl_module_parser = myhdl_module_cli()
  
  if not myhdl_module_parser:
    sys.exit('ERR124: No argument specified')

