#!/bin/bash

#Quit if any error!
set -e

myhdl_env_name="myhdl_env"

function usage {
    echo "usage: $1 [-crh] "
    echo "  -c      Create python3 virtual environment for myhdl"
    echo "  -r      Remove virtual environment for myhdl"
    echo "  -h      display help"
    exit 1
}

function activate_env {
  source $myhdl_env_name/bin/activate
}

function deactivate_env {
  deactivate
}

function create_env {
    echo "Creating python 3 virtual environment"
    python3 -m venv $myhdl_env_name
    echo "Activating new environment"
    activate_env
    pip install wheel
    echo "Installing myhdl"
    pip install myhdl
    echo "Installing myhdl_lib"
    pip install myhdl_lib
    echo "All requirements installed!"
    echo "Deactivating environment! "
    deactivate_env
    echo "To activate the newly created environemt run:  source $myhdl_env_name/bin/activate "

}

function remove_env {
    echo "Removing myhdl virtual environment"
    rm -rf $myhdl_env_name
}

#Using bash builtin getopts option
while getopts ":cadrh" opt; do
  case $opt in
    c)  create_env $0
        ;;

    r)  remove_env $0
        ;;

    h)  usage $0
        ;;

    *)  echo "Invalid option: -$OPTARG" >&2
        usage $0
        ;;
    #\?)
    #  echo "Invalid option: -$OPTARG" >&2
    #  ;;
  esac
done
