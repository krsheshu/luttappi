# shakti
A project for fpga implementation of neural networks

# Usage

Add the shakti project path to the PYTHONPATH environment variable like below
> export PYTHONPATH=path/to/shakti/lib

Ex: if the shakti project is in /home/user/shakti

add to ~/.bashrc the following lines

export PYTHONPATH=/home/user/shakti/lib

Now one should be able to continue with simulations

# Installation Prerequisities

# Operating System

Ubuntu 16.04 or higher

# Virtual Environment 

This repo recommends python3 to be installed in PC

> sudo apt install python3

It is better to install virtualenv package for a smooth functioning

> pip3 install virtualenv

> virtualenv mypython

To activate virtualenv:

> source mypython/bin/activate

# Install myhdl package

> pip install myhdl

To deactivate virtualenv:

> deactivate

# To Simulate a Logistic regression Example from Coursera

> cd lib/frameworks/logistic_regression/
 
> ./run.py -s 

  
