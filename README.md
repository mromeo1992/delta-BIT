# delta-BIT
## Get started

* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)

### Requirements
delta-BIT has been developed on Linux (Ubuntu 22.04) and it has been tested on macOS. For Windows installation we suggest to use [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/) (FSL recomend the same, https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation/Windows). 

For a standard and easy installation we suggest you to satisfy the below requirements:
1) [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/) installation (required).*
2) nvidia drivers (for gpu users).
3) [conda](https://conda.io/projects/conda/en/latest/index.html#) installation (strongly recommend).

*FSL last versions (since 6.0.6) maight have conflict with conda environments (not only with delta-BIT) for this reason we suggest to have a look at [fix FSL-conda conflict](./INSTALL.md#fix-fsl-conda-conflict) section.

### Installation
There is a [fast installation](INSTALL.md#fast-installation) section and a [step-by-step](INSTALL.md#step-by-step-installation) section in the [installation guide](INSTALL.md). If you are not a developer we recommend you only follow the first one. In case you encounter any problems you can try following the section step by step to better understand the installation process and find a solution.


### Usage
delta-BIT can be run from terminal, all commands start with ```d-BIT_``` and all of them have a user manual that can be called by adding the -h flag to the end of the command.

At the moment delta-BIT has the following main pipeline:

* Preprocessing Pipeline
To see the usar manual of the preprocessing pipeline for testing click [here](test_pipeline/preprocessing/README.md).
* Testing Pipeline
To see the usar manual of the testing pipeline for testing click [here](test_pipeline/testing/README.md).