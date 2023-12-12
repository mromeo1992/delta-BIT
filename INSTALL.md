# GET STARTED
## Fast installation 
1) Download repository:
    ```
    #use git clone
    git clone https://github.com/mromeo1992/delta-BIT.git
    
    #or download it from the link and then unzip it
    https://github.com/mromeo1992/delta-BIT/archive/refs/heads/main.zip
    #when you unzip the folder change the name in 'delta-BIT' (remove -main from the name)
    ```
2) Navigate to delta-BIT's folder
    >cd delta-BIT

3) Run installation script
    >sh install.sh
4) Activate delta-BIT environment
    >conda activate delta-BIT
5) Test installation
    >d-BIT_regDataset -h

    if you show this message:

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
    
    **the installation was successful!**

    The installation is now complete and you will be able to run the commands of delta-BIT. Each command has usage guide as the above output, for more information you can have a look at the readme files of the pipelines.

6) (only for GPU user) Test tensorflow installation
    >python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
    
    If a list of GPU devices is returned, you've installed TensorFlow successfully.

## For MacOS installer
Installing on Mac is quite similar to installing on Linux, however you may encounter some issues, such as tensorflow versions not being available for M1 or M2 architectures. For more details on the tensorflow version for MacOS we suggest taking a look at the [tensorflow web site](https://www.tensorflow.org/install/pip#macos). Moreover, tensorflow has no GPU support for Mac installer, [here](https://github.com/deganza/Install-TensorFlow-on-Mac-M1-GPU/blob/main/Install-TensorFlow-on-Mac-M1-GPU.ipynb) you might find a solution.
### Fast installation for CPU users

1) Download repository:
    ```
    #use git clone
    git clone https://github.com/mromeo1992/delta-BIT.git
    
    #or download it from the link and then unzip it
    https://github.com/mromeo1992/delta-BIT/archive/refs/heads/main.zip
    ```
2) Setting delta-BIT's folder as system variable
    >cd delta-BIT
    
    >var=$(realpath ./) && printf "\n%s\n" "export DELTA_BIT=$var" >> ~/.zshrc

    >source ~/.zshrc


3) Run installation script
    >sh install.sh
    
    entry 2 for macOS installation

4) Activate delta-BIT environment
    >conda activate delta-BIT
5) Test installation
    >d-BIT_regDataset -h

    if you show this message:

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
    
    **the installation was successful!**

    The installation is now complete and you will be able to run the commands of delta-BIT. Each command has usage guide as the above output, for more information you can have a look at the readme files of the pipelines.

## Step by step Installation
We strongly recommend that you install delta-BIT in a virtual environment! Here we will show you how to set a conda environment and install delta-BIT in it. We recommend Python version 3.9.13 also, it will work for sure.
### Download repository

Clone the repository with
>git clone https://github.com/mromeo1992/delta-BIT.git

### Setting delta-BIT's folder as system variable

>cd delta-BIT

>var=$(realpath ./) && printf "\n%s\n" "export DELTA_BIT=$var" >> ~/.bashrc

>source ~/.bashrc



### Preparing and setting up the Conda environment
1) Create a new enviroment and activate it
    >conda create -n delta-BIT python==3.9.13
    
    >conda activate delta-BIT
2) Tensorflow installation. If you want to use pretrained models we strongly recomand to use the same version of thensorflow we used, tensorflow==2.10.0.
    1. For GPU users:

        >conda install -c conda-forge cudnn==8.1.0.77 cudatoolkit==11.2.2

        >pip install tensorflow==2.10.0
      
        Sometimes it can happen that you have multiple installation of cuda drivers, for this reason we recomand to set local enviroment variable to avoid issues. In order to do it you can run the [set_environ.sh script](set_environ.sh) (ensure you are working in the delta-BIT enviroments):
        
        >cd $DELTA_BIT #only if you changed directory

        >sh set_environ.sh

        Deactivate and activate the enviroment:

        >conda deactivate

        >conda activate delta-BIT

        [Check tensorflow-gpu installation](https://www.tensorflow.org/install/pip):

        >python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

        If a list of GPU devices is returned, you've installed TensorFlow successfully.

    2. For only CPU user
        
        >pip install tensorflow==2.10.0
 
    for more details about tensorflow installation look at [tensorflow web site](https://www.tensorflow.org/install).




### Upgrade version (for developper)
To get newer version type on terminal in the delt-BIT folder
>git pull

look at [github get started documentation](https://docs.github.com/en/get-started) for more details.

### Installation
1. Open a new terminal (<kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>T</kbd>) and activate the delta-BIT environment:
    >conda activate delta-BIT

2. navigate to the delta-BIT directory
    >cd $DELTA_BIT

3. Buil the package 
    >python setup.py build

4. Install the package
    >python setup.py install

5. Test installation
    >d-BIT_regDataset -h

    if you show this message:
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
    **the installation was successful!**

The installation is now complete and you will be able to run the commands of delta-BIT. Each command has usage guide as the above output, for more information you can have a look at the readme files of the pipelines.






### Get pretrained models
You can download pretrained models and saving in the correct folder throught the commands:

  >cd $DELTA_BIT/trained_models

  >wget -O ./trained_models.zip https://unipa-my.sharepoint.com/:u:/g/personal/mattia_romeo_unipa_it/Ea9L1kLoDpJIsCSwe795QpABF19uJiJ95GOnWygwHOaIVA?download=1

  >unzip trained_models.zip -d pretrained

  >rm trained_models.zip