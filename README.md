# DeLTA-BIT

**DeLTA-BIT** is a Docker-based platform for automatic segmentation of the **Ventralis Intermedius (VIM) nucleus** from medical imaging data. It provides an intuitive web interface for performing inference, visualizing results, and fine-tuning the underlying deep learning model on custom datasets.

The platform is built around a three-container architecture:

- **GUI Container** – A web application developed with **NiceGUI** that provides the user interface and orchestrates the processing pipeline.
- **Deep Learning Container** – A **TensorFlow 2.10** environment responsible for model inference and fine-tuning.
- **Tools Container** – A collection of utilities for image preprocessing, image registration, data conversion, import/export, and workflow management.

At its core, DeLTA-BIT implements a **3D U-Net** architecture for automatic segmentation of the Ventralis Intermedius (VIM) nucleus.

---

# Features

## Query Workspace

The **Query** workspace (accessible through the **QUERY** button on the Home page) allows users to perform automatic VIM segmentation on new imaging data.

Main capabilities include:

- Import **DICOM** datasets in **ZIP** format.
- Import **NIfTI** datasets in **ZIP** format.
- Automatic registration of input images to **MNI space** using **ANTs (Advanced Normalization Tools)**.
- Automatic VIM segmentation in:
  - **MNI space**
  - **Native image space**
- Interactive visualization of segmentation results.

After loading and selecting the input data, pressing **Run VIM** automatically executes the complete inference pipeline:

1. Image preprocessing.
2. Registration to MNI space using **ANTs**.
3. VIM segmentation.
4. Projection of the segmentation back to native image space.
5. Interactive visualization of the results.

---

## Fine-Tuning Workspace

The **Fine-Tuning** workspace (accessible through the **FINE-TUNING** button on the Home page) enables transfer learning on user-provided datasets.

The workflow performs a two-stage fine-tuning procedure:

1. Fine-tuning with the U-Net encoder frozen.
2. Fine-tuning with the last two encoder layers unfrozen.

Users can choose between two pretrained starting models:

- A model pretrained using data from the **Human Connectome Project (HCP)**.
- A model obtained by further fine-tuning the HCP model on a private dataset.

The output of the process is a fine-tuned model ready for subsequent inference.

---

# Architecture

DeLTA-BIT consists of three cooperating Docker containers:

- **GUI Container**
  - NiceGUI web interface
  - Workflow orchestration
  - Result visualization
  - User interaction

- **Deep Learning Container**
  - TensorFlow 2.10
  - 3D U-Net inference
  - Model fine-tuning

- **Tools Container**
  - Image preprocessing
  - Registration to MNI space using ANTs
  - Data conversion
  - Dataset import/export

The GUI coordinates all user interactions and delegates image processing and deep learning tasks to the remaining containers.

---

# System Requirements

## Minimum Requirements

- Docker Engine (Linux) or Docker Desktop (Windows)
- Quad-core CPU
- 8 GB RAM
- 20 GB available disk space

## Recommended Requirements

- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit
- CUDA-compatible NVIDIA GPU with at least 8 GB VRAM
- 16 GB RAM or more
- SSD storage

GPU acceleration is optional but strongly recommended, especially when performing model fine-tuning.

---

# Installation

## Linux

DeLTA-BIT requires Docker to be installed and running.

Install Docker by following the official documentation:

https://docs.docker.com/engine/install/

To enable GPU acceleration, install the NVIDIA Container Toolkit:

https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

From the project directory (`./delta-bit/delta-bit`), run:

```bash
sh install_docker.sh
```

---

## Windows

Install Docker Desktop by following the official documentation:

https://docs.docker.com/desktop/install/windows-install/

For GPU acceleration, install the NVIDIA Container Toolkit:

https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

Then execute:

```text
install_docker_for_windows.bat
```

located inside the `./delta-bit/delta-bit` directory.

---

# Running DeLTA-BIT

## Linux

Start the platform with:

```bash
sh run_delta_bit.sh
```

### CPU-only execution

If GPU acceleration is not available, run:

```bash
docker compose -f docker-compose.yml up
```

---

## Windows

Execute:

```text
run_delta_bit_windows.bat
```

---

## Accessing the Web Interface

Once all containers have started successfully, open your web browser and navigate to:

```
http://localhost:8080
```

---

# Remote Deployment

DeLTA-BIT can also be deployed on a remote Linux server.

The installation procedure is identical to the local installation.

To securely access the web interface remotely, ensure that:

- SSH is enabled on the server.
- The firewall allows incoming connections on port **22**.

Create an SSH tunnel using:

```bash
ssh -L 8080:localhost:8080 username@server_ip
```

Then access the application locally from:

```
http://localhost:8080
```

---

# Supported Input Formats

The application accepts compressed **ZIP** archives containing:

- DICOM datasets
- NIfTI images (`.nii`, `.nii.gz`)
- Fine-tuning datasets formatted according to the DeLTA-BIT dataset structure

---

# Output

## Query Workspace

The Query workspace produces:

- VIM segmentation in native image space.
- VIM segmentation in MNI space.
- Interactive visualization of segmentation results.

## Fine-Tuning Workspace

The Fine-Tuning workspace produces:

- A fine-tuned 3D U-Net model ready for inference.

---

# References

1. Van Essen, D. C., Smith, S. M., Barch, D. M., et al. (2013). **The WU-Minn Human Connectome Project: An Overview.** *NeuroImage*, 80, 62–79. https://doi.org/10.1016/j.neuroimage.2013.05.041

2. Human Connectome Project (HCP). https://www.humanconnectome.org/

---

# Citation

If you use **DeLTA-BIT** in your research, please cite:

```bibtex
@misc{romeo2026deltabitopensourceprobabilistictractographybased,
      title={DeLTA-BIT: an open-source probabilistic tractography-based deep learning framework for thalamic targeting in functional neurological disorders}, 
      author={Mattia Romeo and Cesare Gagliardo and Grazia Cottone and Giorgio Collura and Enrico Maggio and Claudio Runfola and Eleonora Bruno and Maria Cristina D'Oca and Massimo Midiri and Francesca Lizzi and Ian Postuma and Marco D'Amelio and Alessandro Lascialfari and Alessandra Retico and Maurizio Marrale},
      year={2026},
      eprint={2312.15462},
      archivePrefix={arXiv},
      primaryClass={physics.med-ph},
      url={https://arxiv.org/abs/2312.15462}, 
}
```

If your work also makes use of the pretrained model, please cite the Human Connectome Project publication listed in the **References** section.

---

# License
Work in progress: license information pending.
