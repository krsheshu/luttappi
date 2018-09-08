#!/bin/bash


#Getting the project name from the project folder
prj_name=$PWD
prj_name="${prj_name#*blocks_myhdl/}"
prj_name="${prj_name%/tb/*}"

#Getting blocks_myhdl absolute path
myhdl_basedir=$PWD
myhdl_basedir="${myhdl_basedir%blocks_myhdl*}blocks_myhdl"
echo "myhdl_basedir = $myhdl_basedir"
echo "prj_dir = $prj_name"

#paths to different libs relative to myhdl_basedir
prj_dir=$prj_name
clk_lib_dir="smr_clock_driver"
pkg_dir="smr_pkg"
subfolder="myhdl"

#exporting the required libraries for the project
PYTHONPATH="${PYTHONPATH}:${myhdl_basedir}/${prj_dir}/${subfolder}/"
PYTHONPATH="${PYTHONPATH}:${myhdl_basedir}/${clk_lib_dir}/${subfolder}/"
PYTHONPATH="${PYTHONPATH}:${myhdl_basedir}/${pkg_dir}/"
export PYTHONPATH
