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


check=true
while $check
do
    echo 'Do you want to uninstall delta-BIT? [y]es [n]o'

    read varname

    if [ "$varname" = y ]
    then
        check=false
        echo Removing delta-BIT
        conda activate delta-BIT

        xargs rm -rf < files.txt
        rm -r build
        rm -r delta_BIT.egg-info
        rm -r dist  
        check2=true
        
        while $check2
        do
            echo "Do you want to remove conda environment? [y]es [n]o"

            read varname
            
            if [ "$varname" = y ]
            then
                check2=false
                echo "Removing conda environment"
                pip uninstall tensorflow
                conda deactivate
                conda activate base
                conda remove --name delta-BIT --all
                conda clean -a
            
            elif [ "$varname" = n ]
            then
                check2=false
      
            fi
        done

        check3=true
        while $check3
        do
            echo "Do you want to remove delta-BIT directory? [y]es [n]o"
            read varname

            if [ "$varname" = y ]
            then
            check3=false
                echo Removing directory
                cd 
                rm -r $DELTA_BIT
                
            elif [ "$varname" = n ]
            then
                check3=false
                break
            fi
        done
        
        check4=true
        while check4
        do
            echo "Linux or MacOS installation? \n1: Linux \n2: MacOS\n"

            read varname

            if [ $varname -eq 1 ]
            then
                sed '/^export DELTA_BIT/d' ~/.bashrc -i
                source ~/.bashrc
                echo DONE!
            
            elif [ $varname -eq 2 ]
            then
                sed '/^export DELTA_BIT/d' ~/.zshrc -i
                source ~/.zshrc
                echo DONE!            
            fi
        done
    
    elif [ "$varname" = n ]
    then
        check=false
        echo Exting
        break




    fi
done