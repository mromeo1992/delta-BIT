# Preprocessing pipeline

This pipeline needs to prepare your own dataset for testing.

## Dataset structure

Before running the pipeline you should prepare your raw data. The best should be have a data structure like below:
```
Dataset main folder
├── Subject_1
|   ├── T1 image
|   └── DWI image
|   └── bvecs file
|   └── bvals file
├── Subject_2
|   ├── T1 image
|   └── DWI image
|   └── bvecs file
|   └── bvals file
|
|
|
├── Subject_N
|   ├── T1 image
|   └── DWI image
|   └── bvecs file
|   └── bvals file
```

In this way it is possible to map your data in a JSON file.

### Note
**Do not repeat subject name in your data structure!** \
**Inside the Subject folder use only paths equal for all subjects!**

## Map your dataset

The first step un this pipeline is mapping your dataset and its features in a JSON, which can be easyly read. Once your data are ready in accordance with the [dataset structure](#dataset-structure), you can read your data and make a json file with [write_json.py](write_json.py) script. You can create a dataset json by yourself skipping this step, however a file is needed to predict data and we suggest to use this script.
### Usage
The command 

```
d-BIT_initialise -h

```
will output

```
usage: d-BIT_initialise [-h] -n NAME [-m {pretrained}] [--data_type DATA_TYPE] -dir DATASET_DIRECTORY [--T1 T1] [--dwi DWI]
                        [--bvecs BVECS] [--bvals BVALS] [--registration] [-o OUTPUT_DIR]

With this script you can create the dataset json file for your own dataset.The minimum requirements are T1 images and DWI
data placed in the standard Dataset Structure (view Preprocessing user manual).

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Project's name (default: None)
  -m {pretrained}, --models {pretrained}
                        Insert here the name of the models you want to use (default: pretrained)
  --data_type DATA_TYPE
                        Insert here the extention of the disired output data: possibility nii, nii.gz, mgz (default: nii.gz)
  -dir DATASET_DIRECTORY, --dataset_directory DATASET_DIRECTORY
                        indicate here your main folder which cointains your dataset (default: None)
  --T1 T1               file name of the T1 image (default: T1.nii.gz)
  --dwi DWI             file name of the DWI image (default: DWI.nii.gz)
  --bvecs BVECS         file name of the bvecs file (default: DWI.bvec)
  --bvals BVALS         file name of the bvals file (default: DWI.bval)
  --registration        Inser if you data have already been registered on a standard template (default: False)
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        output_directory (default: $HOME/project_name)

```
Flags' explaination:
* -n, --name, require to insert a project name, in this way all successive pipelines can be called throught this name.
* -m, --models, here you insert the models you want to use for predictions. Models have been saved in the [trained models directory](../../trained_models) to be read. To download pretrained models and save in the correct folder look [here](../../README.md#get-pretrained-models).
* --data_type, here you can insert the output format you want to use. Available format are: nii, nii.gz, mgz. Default is nii.gz.
* -dir, --dataset_directory, here you insert the main fold of your dataset (look at [dataset structure](#dataset-structure)).
* --T1 insert here the file name of the T1 image. By default the program will assume that T1 image's name is "T1.nii.gz" and it is located inside the subject's folder.
* --dwi insert here the file name of the  DWI image.  By default the program will assume that DWI image's name is "DWI.nii.gz" and it is located inside the subject's folder.
* --bvecs, insert here the name of the bvecs file. By default the program will assume that the file bves' name is "DWI.bvec" and it is located inside the subject's folder.
* --bvals, insert here the name of the bvecs file. By default the program will assume that the file bvals' name is "DWI.bval" and it is located inside the subject's folder.
* --registration, in general T1 and DWI images stay in different space, in order to make predictions DWI images must be registered on T1 space (look at the [below section](#register-dataset-on-mni152)). In some case it can happen that images have already been registered, if it is your case insert this flag to skip registration step.
* -o, --output_dir, insewr here the output folder where all outputs will be saved on. Default: $HOME/project_name.

### example
```
d-BIT_initialise -n test1 -m pretrained -dir path/to/my/dataset --T1 T1.nii.gz --dwi DWI.nii.gz --bvecs DWI.bvec --bvals DWI.bval -o output/fold/test1
```

## Preprocess DWI images
DWI images are affectded by strong noise due to eddy current and movement artifacts. Even though you are going to use Convolutional Neural Network (CNN) for probabilistic tractography you need to apply some correction to DWI images. The dataset we use for pretrained models, the Human Connectome Project ([HCP](https://www.humanconnectome.org/)) dataset, has already DWI preprocessed data. In HCP dataset DWI images have been processed using the commands of FSL [topup](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup) and [eddy](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy). However this processing requires *b_lip_up* and *b_lip_down* acquisitions which normaly are not performed, for this reason we chose to implement an old version of the command eddy called *eddy_correct*. If you want to use your own DWI preprocessing you can modify by your self the [preprocessing file](./preprocessing_dwi.py) keeping the output structure exactly the same:

```
Project output folder
├── dataset.json
└── preprocessing
|    └── dwi_preprocessing
|        └── Subject1 
|        |    ├── FA.nii.gz fractionary anisotropy image
|        |    ├── L1.nii.gz first eigeinvalue image
|        |    ├── L2.nii.gz
|        |    ├── L3.nii.gz
|        |    ├── V1.nii.gz first eigeinvector image
|        |    ├── V2.nii.gz
|        |    └── V3.nii.gz
|        └── Subject2 
|        |    ├── FA.nii.gz 
|        |    ├── L1.nii.gz 
|        |    ├── L2.nii.gz 
|        |    ├── L3.nii.gz 
|        |    ├── V1.nii.gz 
|        |    ├── V2.nii.gz 
|        |    └── V3.nii.gz         
|        |
|        |
|        |
|        |
|        └── SubjectN
|        |    ├── FA.nii.gz 
|        |    ├── L1.nii.gz 
|        |    ├── L2.nii.gz 
|        |    ├── L3.nii.gz 
|        |    ├── V1.nii.gz 
|        |    ├── V2.nii.gz 
|        |    └── V3.nii.gz  
```
In addiction you need to map your processed data in the json file. We suggest to try a normal preprocessing and then try to modify the preprocessing step.

### Usage
Typing on the terminal the command
```
d-BIT_preprocessDWI -h
```
it will output
```
usage: d-BIT_preprocessDWI [-h] -n NAME [--tmp]

With this script you can preprocess your dwi files.The minimum requirements
dataset json file produced by write_json.py.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Project's name (default: None)
  --tmp                 Insert if you want to keep temporary files (default:
                        False)
```
This means that after you map your dataset the preprocessing can be done giving just the project name. If you inser the flag *--tmp* you can keep in memory temporary file needed for processing purpose.



## Register dataset on MNI152

The networks has been trained to work on a small portion of the image which is called bounding box. This box was evaluated through statistical analysis performed on the [MNI152 1mm space](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Atlases), where all images have same reference system. So, in order to cut the correct box it is necessary first register your native T1 on the standard, and then apply a 2 step registration for your DTI images. In addiction, since neurologists prefer having image in ACPC alignment [[1](#1)-[2](#2)], an extra spatial trasformation is applied during T1 registration. \
T1 registration is performed using the [ACPC Alignment script](https://github.com/Washington-University/HCPpipelines/blob/master/PreFreeSurfer/scripts/ACPCAlignment.sh) taken by the [HCP pipeline](https://github.com/Washington-University/HCPpipelines) of the University of Washington. At the end of this registration a trasformation matrix is saved for DTI image registration. \
DTI registration is more coplicated than that performed on T1 images.In general, this is because DWI (and therefore DTI) images usually have a lower resolution. Furthermore, the T1 image is not preprocessed, it does not have a normalized gray level distribution, so normal registration pipelines as [flirt](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT) cannot find the correct transformation in one step. Our registration pipeline works following the below steps:
* 2D registration of the FA image on the T1 native image (slice by slice);
* 3D registration of the above result on the T1 native image;
* concatenation of the above transformations and the T1 to standard registration;
* application of the resulting trasformation matrix to FA and other DTI images.

This pipeline has been developed taking inspiration from [FSL/FLIR/FAQ](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT/FAQ), in particular looking at [How do I do 2D (or limited DOF) registration with FLIRT?](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT/FAQ#How_do_I_do_2D_.28or_limited_DOF.29_registration_with_FLIRT.3F) and [How do I do a two-stage registration using the command line?](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT/FAQ#How_do_I_do_a_two-stage_registration_using_the_command_line.3F).


### Usage

Typing on the terminal the command:
```
d-BIT_regDataset -h
```
it will output

```
usage: d-BIT_regDataset [-h] -n NAME
                        [-t {MNI152_T1_1mm.nii.gz,MNI152_T1_2mm.nii.gz}]
                        [--tmp]

With this script you can register your dataset.The minimum requirements
dataset json file produced by write_json.py and DWI preprocessing.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Project's name (default: None)
  -t {MNI152_T1_1mm.nii.gz,MNI152_T1_2mm.nii.gz}, --template {MNI152_T1_1mm.nii.gz,MNI152_T1_2mm.nii.gz}
                        choose a template for registration (for testing
                        pretrained models only MNI152_T1_1mm.nii.gz) (default:
                        MNI152_T1_1mm.nii.gz)
  --tmp                 Insert this flag if you want to keep temporary files
                        (default: False)
```
In the same way as [preprocessing DWI images](#preprocess-dwi-images) you just need to specify the name of the initialised project.



## References
<a id="1">[1]</a> J. Talairach and P. Tournoux, "Co-planar Stereotaxic Atlas of the Human Brain: 3-Dimensional Proportional System - an Approach to Cerebral Imaging", Thieme Medical Publishers, New York, NY, 1988. \
<a id="2">[2]</a> H.M. Duvernoy, "The Human Brain: Surface, Blood Supply, and Three Dimensional Sectional Anatomy", second edition, Springer, Vienna, 1999.
