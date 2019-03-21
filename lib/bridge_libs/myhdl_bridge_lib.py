
import os
import sys
from myhdl import traceSignals
import shutil
from subprocess import call
from myhdl import toVerilog, toVHDL
from myhdl.conversion import analyze


class RelPaths:
  algo_model_base_dirname = '../../almo/pcog_gen/'
  test_image_gen_base_dirname = '../../almo/image_generation_pgm/'
  algo_model_config_dirname = 'config_files'

  # local directories
  src_code_dirname='myhdl'
  converted_hdl_dirname='converted_hdl'
  sim_tb_dirname = 'tb/tests'
  sim_temp_dirname = 'tb/myhdl_work'
  sim_wave_dirname = 'tb/waves'
  sim_pattern_dirname='tb_pattern'
  synthesis_dirname = 'syn'
  sim_hdl_dirname = 'tb_hdl'
  sim_hdl_scr_dirname = '07_scr'
  # waveform files
  sim_vcd_file_ext = '.vcd'
  saved_vcd_file_ext = '.sav'
  # quartus project file
  synthesis_proj_file_ext = '.qpf'


class AbsPaths:
  src_code_dir=''
  sim_tb_dir=''
  converted_hdl_dir=''
  sim_temp_dir=''
  sim_pattern_dir=''
  sim_wave_dir=''
  config_file=''


class MyhdlBridgeLib(RelPaths,AbsPaths):

  def sim_defaults(self,simulation_temp_dir_abs):
    traceSignals.directory = simulation_temp_dir_abs
    traceSignals.timescale = "1ps"

  def remove_temp_files(self,folder):
    for the_file in os.listdir(folder):
      file_path = os.path.join(folder, the_file)
      try:
        if os.path.isfile(file_path):
          os.unlink(file_path)
      except Exception as e:
        print(e)

  def convert_settings_defaults(self,converted_hdl_dir_abs):
    toVerilog.directory = converted_hdl_dir_abs
    toVerilog.no_testbench = True
    toVHDL.directory = converted_hdl_dir_abs
    analyze.simulator = "vlog"
    analyze._analyzeOnly = True

  def wave(self,vcd_file_path,sav_file_path):
    print "Open the signal waveform"
    call(['gtkwave', "{:s}".format(vcd_file_path), "{:s}".format(sav_file_path)])

  def synthesize(self,qpf_file):
    print "Open the synthesis project"
    call(['quartus', "{:s}".format(qpf_file )])

  def sim_hdl(self,filename):
    print "Run the systemverilog test"
    print filename
    call(["{:s}".format(filename)])

  def test_image_generate(self, script_path,file_path, testbench_dir_path):
    print "Generate the test image"
    call(['sh', "{:s}".format(script_path), "{:s}".format(file_path)])
    call(['mv', "gen_img.txt", "{:s}".format(testbench_dir_path)])

  def __init__(self,base_dir):
    #local module paths
    self.src_code_dir = os.path.join(base_dir, "{:s}".format(self.src_code_dirname))
    sys.path.append(self.src_code_dir)
    self.sim_tb_dir=os.path.join(base_dir, "{:s}".format(self.sim_tb_dirname))
    sys.path.append(self.sim_tb_dir)
    self.converted_hdl_dir = os.path.join(base_dir, "{:s}".format(self.converted_hdl_dirname))
    if not os.path.exists(self.converted_hdl_dir):
      os.makedirs(self.converted_hdl_dir)
    self.sim_temp_dir = os.path.join(base_dir, "{:s}".format(self.sim_temp_dirname))
    if not os.path.exists(self.sim_temp_dir):
      os.makedirs(self.sim_temp_dir)
    self.sim_pattern_dir=os.path.join(base_dir, "{:s}/{:s}".format(self.sim_temp_dirname,self.sim_pattern_dirname))
    if not os.path.exists(self.sim_pattern_dir):
      os.makedirs(self.sim_pattern_dir)
    self.sim_wave_dir=os.path.join(base_dir, "{:s}".format(self.sim_wave_dirname))
    if not os.path.exists(self.sim_wave_dir):
      os.makedirs(self.sim_wave_dir)

  #print sys.path

