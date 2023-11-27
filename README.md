# DELTA-BIT

## System preparation
We strongly recommend that you install delta-BIT in a virtual environment! Pip or anaconda are both fine. Python version 3.9.13 will work for sure.

1) Create a new enviroment and activate it
    >conda create -n delta-BIT python==3.9.13
    
    >conda activate delta-BIT
2) Tensorflow installation. If you want to use pretrained models we strongly recomand to use the same version of thensorflow we used, tensorflow==2.10.0.

    >pip install tensorflow==2.10.0
 
    for more tensorflow installation details look at [tensorflow web site](https://www.tensorflow.org/install).

## Downloading

Clone the repository with
>git clone https://github.com/mromeo1992/delta-BIT.git

Setting delta-BIT's folder as system variable (required for syste,)

>cd delta-BIT

>var=$(realpath ./) && printf "\n%s\n" "export DELTA_BIT=$var" >> ~/.bashrc

>source ~/.bashrc

### Upgrade version (for developper)
To get newer version type on terminal in the delt-BIT folder
>git pull

look at [github get started documentation](https://docs.github.com/en/get-started) for more details.

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