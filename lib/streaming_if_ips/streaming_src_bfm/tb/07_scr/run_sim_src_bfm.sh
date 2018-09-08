#!/bin/bash

if [ $# -lt 2 ]; then
  echo "First, Please make sure if you are in proper myhdl environment"
  echo "Error!. Please provide two arguments"
  echo "Example usage: $0 <valid_pattern> <ready_pattern> <simulation_time>"
  exit 1
fi  

scriptpath="$(dirname $(readlink -f $0))"
cd $scriptpath

#TestBench directories
tb_lib_scr="02_scripts"
tb_work="myhdl_work"
tb_tests="03_tests"
tb_waves="06_waves"
myhdl_src_dir="myhdl"

module_name="src_bfm"
sim_module_name="sim_${module_name}"


#Set all library paths used for the simulation project
source ../${tb_lib_scr}/set_myhdl_lib_paths.sh


#Moving back to the script directory after all the required libpath exports
cd $scriptpath
env |grep PYTHONPATH


rm -f *.vcd* ../../${myhdl_src_dir}/*.pyc* #deleting any old generated files if any
rm -rf ../${tb_work}

# Compile the python simulation script
python ../${tb_tests}/${sim_module_name}.py $1 $2 $3

#Create workspace and move all generated files 
mkdir ../${tb_work}
mv -f *.vcd ../${tb_work}/
mv -f ../../${myhdl_src_dir}/*.pyc ../${tb_work}/

#View waveform
gtkwave ../${tb_work}/${sim_module_name}.vcd ../${tb_waves}/${sim_module_name}.sav
