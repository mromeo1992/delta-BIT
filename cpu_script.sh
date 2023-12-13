#!bin/bash


#delta-BIT is a progragram for tractography prediction
#Copyright (C) 2023,  University of Palermo, department of Physics 
#and Chemistry, Palermo, Italy and National Institue of Nuclear Physics (INFN), Italy
#
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.



eval "$(conda shell.bash hook)"

#create a new environment and activate it
conda create -n delta-BIT python==3.9.13
conda deactivate

conda activate delta-BIT
echo $CONDA_PREFIX '\n''\n'

bold=$(tput bold)
normal=$(tput sgr0)
cmd=$(conda info | grep 'active environment')
echo ${bold}$cmd${normal}

echo '\n'
check=true
while $check
do
    echo "Look at the above line, is the active environment delta-BIT? [y]es or [n]o"

    read varname
    if [ "$varname" = "y" ]
    then
        check=false
        #tensorflow and cuda installation
        pip install tensorflow==2.10.0

        echo $CONDA_PREFIX
        #Installation

        python setup.py build
        python setup.py install --record files.txt


        # Get pretrained models
        source ~/.bashrc
        cd $DELTA_BIT/dBIT/trained_models
        wget -O ./trained_models.zip https://unipa-my.sharepoint.com/:u:/g/personal/mattia_romeo_unipa_it/Ea9L1kLoDpJIsCSwe795QpABF19uJiJ95GOnWygwHOaIVA?download=1
        unzip trained_models.zip -d pretrained
        rm trained_models.zip

        printf "\n%s\n" "installation successful"
    elif [ "$varname" = "n" ]
    then
        check=false
        echo Sometimes FSL installation may have conflicts with conda enviroments
        echo Please enter'\n''\n'#'\t'conda deactivate'\n'#'\t'conda activate'\n'
        echo And try again
    fi

done
