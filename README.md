# SRST

Super-resolution spatiotemporal information integration (SRST) uses a CNN with bidirectional ConvLSTM to localize molecules in high-density, three-dimensional single-molecule localization microscopy data.

![workflow](Net/workflow.jpg)

## Windows 11 quick start

**[中文安装与使用说明](docs/windows_zh.md)** · [English guide](docs/windows.md) · [项目结构与开发说明](docs/project.md)

1. [Download the project ZIP](https://github.com/Tailong-Chen/SRST/archive/refs/heads/main.zip) and extract it completely into a writable folder.
2. Double-click **`start_srst.bat`**. Use the same file on every launch.
3. In the opened `fitting.ipynb`, select **SRST (srst_demo)** and use **Cell > Run All**.

On the first launch, SRST creates an isolated Conda environment named `srst_demo` with Python 3.9, installs `spline`, PyTorch and Jupyter, verifies the notebook kernel and bundled model, and opens the notebook. Later launches reuse the verified environment and open the notebook directly. Incomplete setup or updated dependency configuration triggers setup again.

The launcher uses an existing Conda installation or downloads portable Micromamba automatically. The environment lives in a standard Conda environment directory, so an existing Conda terminal can find and activate it with `conda env list` and `conda activate srst_demo`. No model training is needed; inference uses CUDA when available and otherwise CPU.

The first installation needs internet access and several GB of downloads. Allow at least 12 GB of free disk space. Installation and launch output is saved in `srst.log`.

## Using SRST

| Entry point | Purpose |
| --- | --- |
| `start_srst.bat` | The single Windows entry: install when needed and open the notebook |
| `demo.py` | Advanced command-line inference; see the [project guide](docs/project.md) |
| `train.py` | Advanced training; configure data, calibration and output paths before running |

To repair an environment after manually changing its packages, open a terminal in the project folder and run:

```bat
.\start_srst.bat -Repair
```

The bundled demo uses `dataset/frame.tif`, `network/experiment1/model_2.pt`, `network/experiment1/param_run.yaml` and `psfmod/spline_calibration_3dcal.mat`. The checkpoint belongs to `Net.CNNLSTM.CNNBiLSTM`; use the SRST entry points to load it.

Source modules remain in `Net/`, `generic/` and `decode/`. Installation implementation lives in `scripts/`, dependency manifests in `requirements/`, and guides in `docs/`. Generated environments, caches and results are excluded from Git.

## Acknowledgements

This implementation builds on [DECODE](https://github.com/TuragaLab/DECODE), [SMAP](https://github.com/jries/SMAP) and [SplinePSF](https://github.com/TuragaLab/SplinePSF).
