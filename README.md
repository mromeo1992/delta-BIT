# DELTA-BIT

## Installing
Clone the repository with
>git clone https://github.com/mromeo1992/delta-BIT.git

Instalation

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