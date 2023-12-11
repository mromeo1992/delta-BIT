# Testing pipeline
In this pipeline are contained all files for thalamus and tractography predictions. A full prediction means following the below workflow:
- prepare your data (look at the [preprocessing pipeline](../preprocessing/README.md));
- predict the binary mask of the thalamus of the left hemisphere;
- prepare the inputs for the regression networks;
- predict one or more tractographies.

Anyway, we implemeted a pipeline for [only thalamus prediction](#only-thalamus-prediction) which needs only T1 files' location to work.


## Only thalamus prediction
This pipeline permit to get the binary mask of the thalamus of the left hemispere. It can work using pretrained models or your own model (after you perform a training). It is indipendent of the full prediction work flow and the [preprocessing pipeline](../preprocessing/README.md). It requires just a dataset of T1 images which respects the [dataset structure](../preprocessing/README.md#dataset-structure) **without DWI files**. If your data are already registered on the [MNI152_1mm template](../../utils/templates/MNI152_T1_1mm.nii.gz) you can directly predict binary masks just using the --registration flag, otherwise the pipeline will performe automatically the regitration on the standard.

### Usage

Typing on the terminal the command

```
d-BIT_only_thalamus_pred -h
```

it will output
```
usage: d-BIT_only_thalamus_pred [-h] -n NAME [-m {pretrained}]
                                [--data_type DATA_TYPE] -dir DATASET_DIRECTORY
                                [--T1_path T1_PATH] [--registration]
                                [-o OUTPUT_DIR]

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
* -m, --models, here you insert the models you want to use for predictions. Models have been saved in the [trained models directory](../../trained_models) to be read. To download pretrained models and save in the correct folder look [here](../../README.md#get-pretrained-models).
* --data_type, here you can insert the output format you want to use. Available format are: nii, nii.gz, mgz. Default is nii.gz.
* -dir, --dataset_directory, here you insert the main fold of your dataset (look at [dataset structure](#dataset-structure)).
* --T1_path insert here T1 images' relative paths, starting from the subject's folder and in accordance with the [dataset structure](#dataset-structure). By default the program will assume that T1 image's name is "T1.nii.gz" and it is located inside the subject's folder.
* --registration, in general T1 is not registered on the [standard](../../utils/templates/MNI152_T1_1mm.nii.gz) so it is necessary to do it before predict thalamus mask. In some case it can happen that images have already been registered, if it is your case insert this flag to skip registration step.
* -o, --output_dir, insewr here the output folder where all outputs will be saved on. Default: $HOME/project_name.


## Thalamus prediction

If you are following the full prediction work flow, before you get tractography prediction you need the binary mask of the thalamus of the left hemisphere. In order to get thalamus mask we implemented a pipeline which can use pretrained or own (after a training) models. You can use this script only if you have done the preprocessing pipeline and you make the dataset json file (otherwise, if you only want to predict thalamus binary mask you can use the [only thalamus prediction pipeline](#only-thalamus-prediction)). In particular, you need to initialise your project and preprocess your data (look at [Preprocessing pipelin](../preprocessing/README.md) for major details). \
Once your data have been preprocessed, the pipeline uses the [data_loader](../../utils/data_loader.py) script to load, cut and pack images and then predict the binary mask using the selected model and save the output using affine and header information taken from the T1 images. The results are binary masks which can be overlaped to the T1 image and give shape to the thalamus of the left hemisphere. \
The pretrained models work in a small portion of the image, the bounding box. A default box is defined for pretrained models, if you want to use an own box you can specify in this script its location. \
The bounding box file is a npz file and contains the array coordinates. The keywords of the npz file are: 'x_min', 'x_max', y_min', y_max', 'z_min' and 'z_max'.

### Usage
Typing on the terminal the command

```
d-BIT_predict_thalamus -h
```

it will output

```
usage: d-BIT_predict_thalamus [-h] -n NAME [--box BOX]

With this script you can predict thalamus mask.The minimum requirements
dataset json file produced by write_json.py, DWI preprocessing and
registration.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Project's name (default: None)
  --box BOX             If you want to use another bounding box insert here
                        the path of the file (default: default)
```

So, if you are working with the default box, the only parameter you need to specify is the project's name.

## Make network input
Before predict tractography you need to pack all processed data in a specific tensor structure, a 4D image whose volumes are:
- the binary mask of the thalamus;
- the FA image;
- the 9 images obtained by multipling the eigenvectors of the difusion tensor for their eigenvalues (3 vectors of dimension 3, $3\times3=9$ volumes ).

The script outputs a dataset, of size of the lenght of the dataset, of 4D images of size $38\times60\times48\times11$.

### Usage
Typing on the terminal the command

```
d-BIT_make_net_input -h
```

it will output
```
usage: d-BIT_make_net_input [-h] -n NAME

With this script you can cut your dataset.The minimum requirements dataset
json file produced by write_json.py, DWI preprocessing and registration.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Project's name (default: None)
```

## Tractographies prediction
This is the final step of the test pipeline for probabilistic tractography prediction. In order to be more specific, delta-BIT was trained in predicting [voxel by ROI connectivity](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT/UserGuide#voxel_by_ROI_connectivity). In brief, probabilistic tractographies are random walks which use DWI images to get structural connectivity information. After a diffusion model has been build up and a fiber Orientation Distribution Function (fODF) for each voxcel has been evaluated, it is possible to run several sample streamlines by starting from some seed and then taking steps in random directions chosen according to the fODF. The result of the streamlines can be used to represent the structural connectivity of the seed voxels with certain ROIs in the brain, such as areas of the cortex.

In delta-BIT we implemented models for the voxels by ROI connectivity fast estimation using deep Neural Network. In particular we considered the connectivity of the voxel of the thalamus with the below cortex areas:
- frontal cortex;
- occipital cortex;
- parietal cortex;
- postcentral gyrus;
- precentral gyrus;
- temporal cortex.

When you run this pipeline you can choose to get one, more than one or all connectivity maps.

### Usage
Typing on the terminal the command
```
d-BIT_pred_tract -h
```
it will output
```
usage: d-BIT_pred_tract [-h] -n NAME [--cortex_area CORTEX_AREA [CORTEX_AREA ...]]

With this script you can predict probabilistic tractographies.The minimum requirements dataset json file produced by
write_json.py, DWI preprocessing, registration and make network input.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Project's name (default: None)
  --cortex_area CORTEX_AREA [CORTEX_AREA ...]
                        Insert here the cortex area you want to predict choose between ['frontal', 'occipital', 'parietal',
                        'postcentral', 'precentral', 'temporal', 'all'] (default: all)

```
with the flag --cortex_area you can choose the maps to predict, by default delta-BIT predicts all maps.