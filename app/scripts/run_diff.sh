#! /usr/bin/env bash

script_path=$(dirname "$0")
root_path=$script_path/../..

cd $root_path
if [ ! -d python-venv ]
then
    echo "CRITICAL: Virtualenv is missing."
    exit
fi

# Activate virtualenv
source $root_path/python-venv/bin/activate || exit 1

# Running main script
python $script_path/$1 "${@:2}"
