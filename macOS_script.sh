#!bin/bash

eval "$(conda shell.bash hook)"

#create a new environment and activate it
conda create -n delta-BIT python==3.9.13
conda deactivate

conda activate delta-BIT
echo $CONDA_PREFIX

#tensorflow and cuda installation
pip install tensorflow-macos==2.10.0

echo $CONDA_PREFIX
#Installation

python setup_mac.py build
python setup_mac.py install


# Get pretrained models

cd $DELTA_BIT/trained_models
wget -O ./trained_models.zip https://unipa-my.sharepoint.com/:u:/g/personal/mattia_romeo_unipa_it/Ea9L1kLoDpJIsCSwe795QpABF19uJiJ95GOnWygwHOaIVA?download=1
unzip trained_models.zip -d pretrained
rm trained_models.zip

printf "\n%s\n" "installation successful"