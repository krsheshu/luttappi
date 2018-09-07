import re, sys

class testbench_parameters(object):
  output_dir = ""
  pattern_dir = ""
  valid = 0
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
    tb_obj = testbench_parameters(output_dir, pattern_dir, valid, ready, nb_frames, config_file)
    return tb_obj

# Following functions should be part of algo_model lib for analyzing patterns
# get the full_bus data
def get_video_stream(file_pointer, data_width):
  i = 0
  bits_per_char = 4
  streaming_flags = 3
  pixel_stream_len = data_width/bits_per_char + streaming_flags
  full_data = []
  pixel_array = []
  sop_array = []
  eop_array = []
  for lwic in file_pointer.split("\n"):
    i += 1
    lwoc = re.sub("#.*$", "", lwic)
    full_bus = re.sub("\s+", "", lwoc)
    if(len(full_bus)>0): # check if it is an empty line
      if(len(full_bus)!=pixel_stream_len):
        print("ERROR, the bus-width has an unexpected number of characters {:d} versus {:d} at line {:d}".format(len(full_bus), pixel_stream_len, i))
        sys.exit(2)
      full_data.append(full_bus)
    file_length=i
  for i in range (file_length-1): #last line is also taken which should not be considered
    pixel_array.append(int(full_data[i],16) >> (streaming_flags*bits_per_char))
    sop_array.append(int(full_data[i],16) >> ((streaming_flags-1)*bits_per_char) & 0xF)
    eop_array.append(int(full_data[i],16) >> ((streaming_flags-2)*bits_per_char) & 0xF)
  return pixel_array, sop_array, eop_array, file_length-1

  return pixel_array, sop_array, eop_array, file_length-1

