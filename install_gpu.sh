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


# Get pretrained models

cd $DELTA_BIT/trained_models
wget -O ./trained_models.zip https://unipa-my.sharepoint.com/:u:/g/personal/mattia_romeo_unipa_it/Ea9L1kLoDpJIsCSwe795QpABF19uJiJ95GOnWygwHOaIVA?download=1
unzip trained_models.zip -d pretrained
rm trained_models.zip

printf "\n%s\n" "installation successful"
