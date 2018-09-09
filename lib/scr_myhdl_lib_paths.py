#!/usr/bin/env python
#

import os
import sys

def set_myhdl_lib_paths():
  print "setting the path to simulation library"
  sys.path.append(os.path.join(os.path.dirname(__file__), "bridge_libs/"))
  print "setting the paths of the myhdl library"
  sys.path.append(os.path.join(os.path.dirname(__file__), "packages/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "packages/clock_driver/myhdl"))
  print "setting the paths of the building blocks"
  sys.path.append(os.path.join(os.path.dirname(__file__), "building_blocks/basic"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "building_blocks/level_1"))
  print "setting the paths of the streaming if ips"
  sys.path.append(os.path.join(os.path.dirname(__file__), "streaming_if_ips/streaming_ip_a/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "streaming_if_ips/streaming_ip_b/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "streaming_if_ips/streaming_ip_comb/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "streaming_if_ips/streaming_ip_wire/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "streaming_if_ips/streaming_src_bfm/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "streaming_if_ips/streaming_snk_bfm/myhdl/"))


if __name__ == "__main__":
  obj = set_myhdl_lib_paths()
