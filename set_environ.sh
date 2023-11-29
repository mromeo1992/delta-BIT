#!bin/bash

cd $CONDA_PREFIX
mkdir -p ./etc/conda/activate.d && touch ./etc/conda/activate.d/env_vars.sh
mkdir -p ./etc/conda/deactivate.d && touch ./etc/conda/deactivate.d/env_vars.sh
printf "\n%s\n" "export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH" >> ./etc/conda/activate.d/env_vars.sh
printf "\n%s\n" "unset LD_LIBRARY_PATH" >> ./etc/conda/deactivate.d/env_vars.sh
cd $DELTA_BIT


