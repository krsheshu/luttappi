#!/usr/bin/env python
#

import os
import sys

def set_myhdl_lib_paths():
  print("setting the path to simulation library")
  sys.path.append(os.path.join(os.path.dirname(__file__), "../bridge_libs/"))
  print("setting the paths of the myhdl library")
  sys.path.append(os.path.join(os.path.dirname(__file__), "../packages/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../packages/clock_driver/myhdl"))
  print("setting the paths of the building blocks")
  sys.path.append(os.path.join(os.path.dirname(__file__), "../building_blocks/simple"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../building_blocks/chain"))

  print("setting the paths of the building blocks simple lib")
  sys.path.append(os.path.join(os.path.dirname(__file__), "../building_blocks/simple/streaming_simple_adder/myhdl"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../building_blocks/simple/streaming_simple_mult/myhdl"))

  print("setting the paths of the building blocks chain lib")
  sys.path.append(os.path.join(os.path.dirname(__file__), "../building_blocks/chain/streaming_chain_adder/myhdl"))

  print("setting the paths of the streaming if ips")
  sys.path.append(os.path.join(os.path.dirname(__file__), "../streaming_if_ips/streaming_ip_a/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../streaming_if_ips/streaming_ip_b/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../streaming_if_ips/streaming_ip_comb/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../streaming_if_ips/streaming_ip_wire/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../streaming_if_ips/streaming_src_bfm/myhdl/"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../streaming_if_ips/streaming_snk_bfm/myhdl/"))

  print("setting the paths of the pipeline frameworks")
  sys.path.append(os.path.join(os.path.dirname(__file__), "../frameworks/commandPipeline/myhdl"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../frameworks/logistic_regression/myhdl"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../frameworks/logistic_regression/model"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../frameworks/operandPipeline/myhdl"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../frameworks/accumulator/myhdl"))
  sys.path.append(os.path.join(os.path.dirname(__file__), "../frameworks/activation/myhdl"))

if __name__ == "__main__":
  obj = set_myhdl_lib_paths()
