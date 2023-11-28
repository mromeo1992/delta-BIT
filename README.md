# DELTA-BIT
## Requirements
For a standard and easy installation we suggest you to satisfy the below requirements:
1) [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/) installation (required).
2) nvidia drivers and [cuda tool-kit](https://developer.nvidia.com/cuda-toolkit) (for gpu users).
3) [conda](https://conda.io/projects/conda/en/latest/index.html#) installation (strongly recommend).

## Installation
We strongly recommend that you install delta-BIT in a virtual environment! Pip or anaconda are both fine. Python version 3.9.13 will work for sure.

### Downloading

Clone the repository with
>git clone https://github.com/mromeo1992/delta-BIT.git

### Setting delta-BIT's folder as system variable

>cd delta-BIT

>var=$(realpath ./) && printf "\n%s\n" "export DELTA_BIT=$var" >> ~/.bashrc

>source ~/.bashrc

### Upgrade version (for developper)
To get newer version type on terminal in the delt-BIT folder
>git pull

look at [github get started documentation](https://docs.github.com/en/get-started) for more details.

### Conda installation 
1) Create a new enviroment and activate it
    >conda create -n delta-BIT python==3.9.13
    
    >conda activate delta-BIT
2) Tensorflow installation. If you want to use pretrained models we strongly recomand to use the same version of thensorflow we used, tensorflow==2.10.0.
    1. For GPU users:

        >conda install -c conda-forge cudnn==8.1.0.77 cudatoolkit==11.2.2

        >pip install tensorflow[and-cuda]==2.10.0
      
        Sometimes it can happen that you have multiple installation of cuda drivers, for this reason we recomand to set local enviroment variable to avoid issues. In order to do it you can run the below commands in the terminals (ensure you are working in the delta-BIT enviroments):
        
        >cd $CONDA_PREFIX

        >mkdir -p ./etc/conda/activate.d && touch ./etc/conda/activate.d/env_vars.sh

        >mkdir -p ./etc/conda/deactivate.d && touch ./etc/conda/deactivate.d/env_vars.sh

        >printf "\n%s\n" "export PATH=$CONDA_PREFIX:$PATH" >> ./etc/conda/activate.d/env_vars.sh

        >printf "\n%s\n" "export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH" >> ./etc/conda/activate.d/env_vars.sh

        >printf "\n%s\n" "unset PATH" "unset LD_LIBRARY_PATH" >> ./etc/conda/deactivate.d/env_vars.sh

        Deactivate and activate the enviroment:

        >conda deactivate

        >conda activate delta-BIT

        [Check tensorflow-gpu installation](https://www.tensorflow.org/install/pip):

        >python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

        If a list of GPU devices is returned, you've installed TensorFlow successfully.

    2. For only CPU user
        
        >pip install tensorflow==2.10.0
 
    for more tensorflow installation details look at [tensorflow web site](https://www.tensorflow.org/install).



### Get pretrained models
You can download pretrained models and saving in the correct folder throught the commands:

  >cd $DELTA_BIT/trained_models

  >wget -O ./trained_models.zip https://unipa-my.sharepoint.com/:u:/g/personal/mattia_romeo_unipa_it/Ea9L1kLoDpJIsCSwe795QpABF19uJiJ95GOnWygwHOaIVA?download=1

  >unzip trained_models.zip -d pretrained

  >rm trained_models.zip


## Preprocessing Pipeline
To see the usar manual of the preprocessing pipeline for testing click [here](test_pipeline/preprocessing/README.md).
## Testing Pipeline
To see the usar manual of the testing pipeline for testing click [here](test_pipeline/testing/README.md).