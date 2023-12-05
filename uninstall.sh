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
        conda activate delta-BIT

        python setup.py install --record files.txt
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
                sed '/^export DELTA_BIT/d' ~/.bashrc -i
            
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