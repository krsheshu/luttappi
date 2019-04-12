
![Luttappi NN](docs/luttappi.jpg)


# Luttappi NN
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

# Getting Started

1) Create a virtualenvironment for myhdl like below

> cd shakti

> ./run_venv.sh -c

Now a virtual environment is created with all required packages installed

To activate virtualenv:

> source myhdl_env/bin/activate


# To Simulate a Logistic regression Example from Coursera

> cd lib/frameworks/logistic_regression/

> ./run.py -s 


To deactivate virtualenv:

> deactivate
