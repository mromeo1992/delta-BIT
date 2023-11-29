#!bin/bash

eval "$(conda shell.bash hook)"

#create a new environment and activate it
conda create -n delta-BIT python==3.9.13
conda deactivate

conda activate delta-BIT
echo $CONDA_PREFIX

#tensorflow and cuda installation
conda install -c conda-forge cudnn==8.1.0.77 cudatoolkit==11.2.2
pip install tensorflow[and-cuda]==2.10.0

#setting environment variables for cuda drivers
sh $DELTA_BIT/set_environ.sh
conda deactivate
conda activate delta-BIT

echo $CONDA_PREFIX
#Installation

python setup.py build
python setup.py install
