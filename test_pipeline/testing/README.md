# Testing pipeline
In this pipeline are contained all files for thalamus and tractography predictions. A full prediction means following the below workflow:
- prepare your data (look at the [preprocessing pipeline](../preprocessing/README.md));
- predict the binary mask of the thalamus of the left hemisphere;
- prepare the inputs for the regression networks;
- predict one or more tractographies.

Anyway, we implemeted a pipeline for [only thalamus prediction](./only_thalamus_prediction.py) which needs only T1 files' location to work.

## Only thalamus prediction
This pipeline permit to get the binary mask of the thalamus of the left hemispere. It can work using pretrained models or your own model (after you perform a training). It is indipendent of the full prediction work flow and the [preprocessing pipeline](../preprocessing/). It requires just a dataset of T1 images which respects the [dataset structure](../preprocessing/README.md#dataset-structure) **without DWI files**. If your data are already registered on the [MNI152_1mm template](../../utils/templates/MNI152_T1_1mm.nii.gz) you can directly predict binary masks just using the --registration flag, otherwise the pipeline will performe automatically the regitration on the standard.

### Usage

Typing on the terminal the command

```
python $DELTA_BIT/test_pipeline/testing/only_thalamus_prediction.py -h
```

it will output
```
usage: only_thalamus_prediction.py [-h] -n NAME [-m {pretrained}]
                                   [--data_type DATA_TYPE] -dir
                                   DATASET_DIRECTORY [--T1_path T1_PATH]
                                   [--registration] [-o OUTPUT_DIR]

With this script you can directly predict the binary mask of the thalamus of
the left hemisphere.The minimum requirements are T1 images in the standard
Dataset Structure (view Testing user manual).

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Project's name (default: None)
  -m {pretrained}, --models {pretrained}
                        Insert here the name of the models you want to use
                        (default: pretrained)
  --data_type DATA_TYPE
                        Insert here the extention of the disired output data:
                        possibility nii, nii.gz, mgz (default: nii.gz)
  -dir DATASET_DIRECTORY, --dataset_directory DATASET_DIRECTORY
                        indicate here your main folder which cointains your
                        dataset (default: None)
  --T1_path T1_PATH     indicate here the T1 image's relative pathname
                        (starting from the subject's folder) (default:
                        T1.nii.gz)
  --registration        Inser if you data have already been registered on a
                        standard template (default: False)
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        output_directory (default: /home/pcuser1/project_name)
```
Flags' explaination:
* -n, --name, require to insert a project name, in this way all successive pipelines can be called throught this name.
* -m, --models, here you insert the models you want to use for predictions. Models have been saved in the [trained models directory](../../trained_models) to be read. You can download pretrained models and saving in the correct folder throught the commands:

  >cd $DELTA_BIT/trained_models

  >wget -O ./trained_models.zip https://unipa-my.sharepoint.com/:u:/g/personal/mattia_romeo_unipa_it/Ea9L1kLoDpJIsCSwe795QpABF19uJiJ95GOnWygwHOaIVA?download=1

  >unzip trained_models.zip -d pretrained

  >rm trained_models.zip
* --data_type, here you can insert the output format you want to use. Available format are: nii, nii.gz, mgz. Default is nii.gz.
* -dir, --dataset_directory, here you insert the main fold of your dataset (look at [dataset structure](#dataset-structure)).
* --T1_path insert here T1 images' relative paths, starting from the subject's folder and in accordance with the [dataset structure](#dataset-structure). By default the program will assume that T1 image's name is "T1.nii.gz" and it is located inside the subject's folder.
* --registration, in general T1 is not registered on the [standard](../../utils/templates/MNI152_T1_1mm.nii.gz) so it is necessary to do it before predict thalamus mask. In some case it can happen that images have already been registered, if it is your case insert this flag to skip registration step.
* -o, --output_dir, insewr here the output folder where all outputs will be saved on. Default: $HOME/project_name.