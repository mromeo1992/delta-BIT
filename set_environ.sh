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



cd $CONDA_PREFIX
mkdir -p ./etc/conda/activate.d && touch ./etc/conda/activate.d/env_vars.sh
mkdir -p ./etc/conda/deactivate.d && touch ./etc/conda/deactivate.d/env_vars.sh
printf "\n%s\n" "export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH" >> ./etc/conda/activate.d/env_vars.sh
printf "\n%s\n" "unset LD_LIBRARY_PATH" >> ./etc/conda/deactivate.d/env_vars.sh
cd $DELTA_BIT


