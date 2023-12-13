# Installation

delta-BIT has been developed on Linux (Ubuntu 22.04) and it has been tested on macOS and on Windows installation using [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/) (FSL recomend the same, https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation/Windows). If you are a Windows user we recomand to follow the standard Windows installation.

## Fix FSL-conda conflict
The versions of FSL 6.0.6 or newer assume that in your system ```conda``` is not installed, in fact [fslinstaller.py](https://git.fmrib.ox.ac.uk/fsl/conda/installer) installs miniconda in the FSL directory. Double conda installations or the installation of miniconda and anaconda together should be avoided due to the problems that may arise. We found a conflict which happens with the normal installation of FSL 6.0.6 and 6.0.7 is coupled with the installation of delta-BIT. In general, this issue happens for **ALL CONDA ENVIRONMENTS** in your system. We found a solution which avoid any problems.

### If FSL has already been installed
1. If not present, install conda or miniconda on your pc (we suggest miniconda which is  is a minimal installer for Conda, [here](https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html) the official site).
2. move the FSL directory into a backup folder
    >mv $FSLDIR path/to/the/backup/folder

    so you will be able to restore your old version in case of problems.
3. create the FSL directory in the same path. \
    Even you moved the directory, the FSLDIR variable is still in your bash profile, so you can type:
    >mkdir $FSLDIR

    If FSL was stored in a root directory type:
    >sudo mkdir $FSLDIR
4. Download the environment file of FSL from this url https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/?C=M;O=D . You can choose the version you want, even the last one. When the download is terminated move the file on the FSLDIR

    ```
    # for no root folder
    mv Downloads/name_of_the_file_you_downloaded.yml $FSLDIR/

    #for root folder
    sudo mv Downloads/name_of_the_file_you_downloaded.yml $FSLDIR/
    ```
5. move to the parent folder of FSLDIR and type:
    ```
    #for no root folder
    cd $FSLDIR
    cd ..
    conda update conda
    conda env create -p ./fsl -f name_of_the_file_you_downloaded.yml
    ```
    If FSL was installed in a root directory you need to work as root user, you can do it by typing:
    >sudo su

    In most cases anaconda is not active in root user, so you need to activate it. Take note of your conda or miniconda directory (usually it is $HOME/anaconda3 or $HOME/miniconda3) and type:
    ```
    #for anaconda in $HOME/anaconda3/
    source $HOME/anaconda3/bin/activate

    #for miniconda in $HOME/miniconda3/
    source $HOME/anaconda3/bin/activate
    ```
    You will see the write ```(base)``` on the left in your terminal which is the environment. Now you can install FSL:
    ```
    cd $FSLDIR
    cd ..
    conda update conda
    conda env create -p fsl/ -f name_of_the_file_you_downloaded.yml
    exit
    ```
6. Close and open terminal or type
    >source ~/.bashrc

    and try FSL by typing
    >flirt -version
    
    if the output is something like
    ```
    FLIRT version 6.0
    ```
    Everything is ready for delta-BIT installation. If you found some problem that you cannot fix delete the FSL directory and move back the backup copy.

If you want to avoid this procedure you can install old version of FSL (up to FSL 6.0.5.2) with the old installer which you can find [here](https://git.fmrib.ox.ac.uk/fsl/installer).

### If this is your first installation of FSL
If this is your first installation of FSL you will need to configure the bash variables. To do it you just need to open the profile with a text editor and past in it the lines:
```
# FSL Setup
FSLDIR=#insert here the location of your fsl directory (if you have multiple users a root folder is recomended)
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH
. ${FSLDIR}/etc/fslconf/fsl.sh
```

Example: Suppose your FSL directory is in /usr/local you can opend the profile file with gedit or another text editor:
>gedit ~/.profile

and the you append at the end the following lines:
```
# FSL Setup
FSLDIR=/usr/local/fsl
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH
. ${FSLDIR}/etc/fslconf/fsl.sh
```

You can do this and then you can follow [the above guide](#if-fsl-has-already-been-installed) whitou saving the backup version (point 2).

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
4) Reload bash variables and activate delta-BIT environment
    ```
    #on linux
    source ~/.bashrc
    #on mac
    source ~/.zshrc
    ```

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

## Windows installation
delta-BIT has been developed on Unix platform, so we did not write a Windows version. Anyway, since several years Windows has released the [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/about), wls, which is '''a feature of Windows that allows you to run a Linux environment on your Windows machine, without the need for a separate virtual machine or dual booting. WSL is designed to provide a seamless and productive experience for developers who want to use both Windows and Linux at the same time'''. In this section we offer a guide for a simple installation of wls with Ubuntu 22.04 and miniconda3 inside. After this you will be able to follow the [fast installation guide](#fast-installation).

### Install WLS with Ubuntu 22.04
Open PowerShell or Windows Command Prompt in administrator mode by right-clicking and selecting "Run as administrator", enter: 
>wsl --install

then restart your machine. After login open PowerShell or Windows Command Prompt and type
>wsl --install -d Ubuntu-22.04

after install will be finished you will be able to use a Ubuntu terminal by typing ```wsl```.
### Install miniconda
If you want, you can install GUI apps on WSL (look [here](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)), but delta-BIT does not requires it. 
Download the miniconda script:
>wget -O miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

and install the script by typing
>sh miniconda.sh

After you will be able to install firt FSL (follow [this guide](#fix-fsl-conda-conflict)) and then delta-BIT ([here](#fast-installation) the fast installation)



## Step by step Installation
We strongly recommend that you install delta-BIT in a virtual environment! Here we will show you how to set a conda environment and install delta-BIT in it. We recommend Python version 3.9.13 also, it will work for sure.
### Download repository

Clone the repository with
>git clone https://github.com/mromeo1992/delta-BIT.git

### Setting delta-BIT's folder as system variable

>cd delta-BIT

```
#for linux users
var=$(realpath ./) && printf "\n%s\n" "export DELTA_BIT=$var" >> ~/.bashrc

source ~/.bashrc

#for macOS users
var=$(realpath ./) && printf "\n%s\n" "export DELTA_BIT=$var" >> ~/.zshrc

source ~/.zshrc
```



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