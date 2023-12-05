#!bin/bash

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
        conda deactivate
        conda activate base

        python setup.py --record files.txt
        xargs rm -rf < files.txt
        check2=true
        
        while $check2
        do
            echo "Do you want to remove conda environment? [y]es [n]o"

            read varname
            
            if [ "$varname" = y ]
            then
                check2=false
                echo "Removing conda environment: conda remove --name delta-BIT --all"
                conda remove --name delta-BIT --all
                conda clean -a
            
            elif [ "$varname" = n ]
            then
                check2=false
                break
      
            fi
        done
    
    elif [ "$varname" = n ]
    then
        check=false
        echo Exting
        break




    fi
done