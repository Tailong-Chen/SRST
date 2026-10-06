# SRST

Super-resolution spatiotemporal information integration (SRST) uses a CNN with bidirectional ConvLSTM to localize molecules in high-density, three-dimensional single-molecule localization microscopy data.

![workflow](Net/workflow.jpg)

## Windows 11 quick start

**[中文安装与使用说明](docs/windows_zh.md)** · [English guide](docs/windows.md) · [项目结构与开发说明](docs/project.md)

1. [Download the project ZIP](https://github.com/Tailong-Chen/SRST/archive/refs/heads/main.zip) and extract it completely into a writable folder.
2. Double-click **`setup_and_run_demo.bat`**.
3. In the opened `fitting.ipynb`, select **SRST (srst_demo)** and use **Cell > Run All**.

The installer creates an isolated Python 3.9 environment, installs the compiled `spline` package, PyTorch and Jupyter, checks the bundled model, and opens the notebook. It reuses Conda when available or downloads portable Micromamba. No model training is needed; inference uses CUDA when available and otherwise CPU.

The first installation needs internet access and several GB of downloads. Allow at least 12 GB of free disk space. Installation output is saved in `setup_and_run_demo.log`.

## Entry points

| Entry point | Purpose |
| --- | --- |
| `setup_and_run_demo.bat` | Install dependencies, check the model and open the notebook |
| `install_windows.bat` | Install and verify the environment only |
| `run_notebook_windows.bat` | Reopen the notebook after installation |
| `run_demo_windows.bat` | Run command-line inference and save results under `outputs/demo/` |
| `train.py` | Advanced training; configure data, calibration and output paths before running |

For a short CPU inference check:

```bat
run_demo_windows.bat --device cpu --max-frames 9 --batch-size 1
```

The bundled demo uses `dataset/frame.tif`, `network/experiment1/model_2.pt`, `network/experiment1/param_run.yaml` and `psfmod/spline_calibration_3dcal.mat`. The checkpoint belongs to `Net.CNNLSTM.CNNBiLSTM`; use the SRST entry points to load it.

Source modules remain in `Net/`, `generic/` and `decode/`. Installation implementation lives in `scripts/`, dependency manifests in `requirements/`, and guides in `docs/`. Generated environments, caches and results are excluded from Git.

## Acknowledgements

This implementation builds on [DECODE](https://github.com/TuragaLab/DECODE), [SMAP](https://github.com/jries/SMAP) and [SplinePSF](https://github.com/TuragaLab/SplinePSF).
