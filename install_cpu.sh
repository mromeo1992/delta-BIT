#!bin/bash

eval "$(conda shell.bash hook)"

#create a new environment and activate it
conda create -n delta-BIT python==3.9.13
conda deactivate

conda activate delta-BIT
echo $CONDA_PREFIX

#tensorflow and cuda installation
pip install tensorflow==2.10.0

echo $CONDA_PREFIX
#Installation

python setup.py build
python setup.py install
