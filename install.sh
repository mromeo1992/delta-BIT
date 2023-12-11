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


sed '/^export DELTA_BIT/d' ~/.bashrc -i
var=$(realpath ./) && printf "\n%s\n" "export DELTA_BIT=$var" >> ~/.bashrc
source ~/.bashrc
check0=true
while $check0
do 
echo "Linux or MacOS installation? \n1: Linux \n2: MacOS\n"

read varname
if [ $varname -eq 1 ]
then
	check0=false
	echo Linux installation
	check1=true
	while $check1
	do
	echo "Would you like GPU installation? [y]es/[n]o"

	read varname



	if [ "$varname" = "y" ]
	then
		check1=false
		echo you chose GPU installation
		nvidia-smi

		check2=true
		while $check2
		do
		echo "Do you see nvidia-smi output? [y]es/[n]o"

		read varname

		if [ "$varname" = "y" ]
		then
			check2=false
			echo "\n"nvidia drivers check succesful! "\n"
			echo running installation script
			sh ./gpu_script.sh

		elif [ "$varname" = "n" ]
		then
			echo "\n"There is a problem in nvidia-smi driver!
			echo Tensorflow might not found GPU devices
			echo "\n"Check your nvidia installation or install CPU version"\n"
			check2=false
			check3=true
			while $check3
			do
			echo "Do you want to install CPU version? [y]es/[n]o"
			read varname

			if [ "$varname" = "y" ]
			then
				check3=false
				echo "\n"you chose CPU installation"\n"
				echo Running installation script
				sh ./cpu_script.sh
			elif [ "$varname" = "n" ]
			then
				check3=false
				echo Exiting!
				break
			fi
			done
		fi
		done

	elif [ "$varname" = "n" ]
	then
		check1=false
		echo you chose CPU installation
		echo running installation script
		sh ./cpu_script.sh
	fi
	done

elif [ $varname -eq 2 ]
then
	check0=false
	echo MacOS installation: CPU version
	sh ./macOS_script.sh	
fi
done

