import sys

class Valid():
  def __init__(self):
    self.pattern0=0xabcd
    self.pattern1=0x1234
    self.pattern2=0xa1b4
    self.pattern3=0x1f6b

class TestbenchParameters(object):
  output_dir = ""
  pattern_dir = ""
  valid = Valid()
  ready = 0
  nb_frames = 0
  config_file = ""
  # The class "constructor" - It's actually an initializer
  def __init__(self, output_dir, pattern_dir, valid, ready, nb_frames, config_file):
    self.output_dir = output_dir
    self.pattern_dir = pattern_dir
    self.valid = valid
    self.ready = ready
    self.nb_frames = nb_frames
    self.config_file= config_file

def pass_testbench(output_dir, pattern_dir, valid, ready, nb_frames,config_file):
    tb_obj = TestbenchParameters(output_dir, pattern_dir, valid, ready, nb_frames, config_file)
    return tb_obj

