

# SRST

![workflow](./Net/workflow.jpg) 

## Introduction

Single-molecule localization microscopy (SMLM) is a powerful imaging technique that surpasses the diffraction limit of light by computationally localizing individual fluorescent molecules. However, achieving sufficient spatial resolution in SMLM requires extensive frame acquisition, limiting temporal resolution. Increasing the density of fluorescent molecules is a common strategy to enhance temporal resolution, but this often results in overlapping point spread functions (PSFs) and computational challenges in distinguishing adjacent molecules.

We developed a deep learning-driven approach, termed super-resolution spatiotemporal information integration (SRST), for the precise three-dimensional localization of ultra-high-density molecules.

## Setup

Clone the repo and build the python environment.

The `environment.yml` file is the original machine-specific lock and should not be used for a new Windows installation. Windows users should follow [README_WINDOWS.md](README_WINDOWS.md) and the [short English guide](PROJECT_STEP_BY_STEP_EN.md), then run `install_windows.bat`.

```
git clone https://github.com/Tailong-Chen/SRST.git
```

## Training

Train model

```
python train.py
```

You can train networks that process different data by modifying the import file link in the python file. The modifiable include : 

- param_file: Set camera parameters, training data parameters and network hyperparameters. 
- calibration_file:  Set the PSF.

## Fitting

Fitting.ipynb provides the function of fitting the original data to generate super-resolution reconstruction. It is necessary to provide a trained network and data to be fitted.

## Windows demo

For a one-click pretrained demo on Windows, see the [Chinese guide](PROJECT_STEP_BY_STEP_CN.md), [README_WINDOWS.md](README_WINDOWS.md) or the [short English guide](PROJECT_STEP_BY_STEP_EN.md). `setup_and_run_demo.bat` installs an isolated Python 3.9 environment and all notebook dependencies, checks the bundled model, and opens `fitting.ipynb` in Jupyter. An existing Conda installation is reused when found; otherwise official portable Micromamba is downloaded automatically. The compiled `spline` package is installed from the TuragaLab channel. The demo selects CUDA or CPU automatically and uses a bounded notebook batch size. Use `install_windows.bat` for installation only, and `run_notebook_windows.bat` to reopen the notebook later.

## Acknowledgements

This implementation is based on code from several repositories.


- [DECODE](https://github.com/TuragaLab/DECODE)
- [SMAP](https://github.com/jries/SMAP)
- [SplinePSF](https://github.com/TuragaLab/SplinePSF)
