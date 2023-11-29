#!bin/bash

#create a new environment and activate it
conda create -n delta-BIT python==3.9.13
conda activate delta-BIT

#tensorflow and cuda installation
conda install -c conda-forge cudnn==8.1.0.77 cudatoolkit==11.2.2
pip install tensorflow[and-cuda]==2.10.0

#dowloading repository
#git clone https://github.com/mromeo1992/delta-BIT.git

#Setting delta-BIT's directory as system variable
#cd delta-BIT
#var=$(realpath ./) && printf "\n%s\n" "export DELTA_BIT=$var" >> ~/.bashrc
#source ~/.bashrc

#setting environment variables for cuda drivers
sh set_environ.sh
conda deactivate
conda activate delta-BIT

#Installation

python setup.py build
python setup.py install