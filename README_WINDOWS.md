# SRST on Windows 11: quick start

This is the shortest supported path for the bundled pretrained localization demo and the repaired `fitting.ipynb` notebook. You do not need to train a model.

## 1. Install

1. Extract the ZIP and open the project folder.
2. If you want GPU localization, install a current NVIDIA driver. If `nvidia-smi` is only available from an Administrator terminal, use an Administrator terminal/VS Code.
3. Right-click `setup_and_run_demo.bat` and select **Run as administrator**.

The installer creates the `srst_demo` Conda environment, installs the PyTorch CUDA 12.8 build, checks the bundled checkpoint, and registers the VS Code/Jupyter kernel. If Conda is missing, it tries to install Miniforge with `winget`; otherwise install Miniconda or Miniforge first and run the installer again.

## 2. Run GPU localization

Open a terminal in the project folder after installation:

```bat
run_demo_windows.bat --device cuda:0 --max-frames 20
```

Use `--device auto` if the same folder must also run on CPU-only machines:

```bat
run_demo_windows.bat --device auto --max-frames 20
```

The result is in `outputs\demo`. Open `outputs\demo\summary.json` and check:

```json
"device": "cuda:0",
"cuda_available": true
```

`cuda_device_name` gives the GPU name. If GPU memory is low, add `--batch-size 1`.

If a double-clicked window still closes, open a terminal in the project folder and run `cmd /k setup_and_run_demo.bat`. The launcher keeps the window open and writes `setup_and_run_demo.log` beside the batch files.

## 3. Run the notebook in VS Code

1. Open the project folder in VS Code and open `fitting.ipynb`.
2. Select the kernel **SRST (srst_demo)**.
3. Run code cells in this order: **0 → 2 → 3 → 5 → 7 → 9 → 11**.

The notebook selects CUDA automatically when PyTorch can see the GPU; otherwise it uses CPU. Cell 5 performs localization; cells 7, 9, and 11 display and filter the predicted molecule positions.

## If something fails

- `conda not found`: install Miniconda/Miniforge, then rerun `install_windows.bat`.
- `CUDA was requested, but no CUDA device is available`: run `nvidia-smi`, update the NVIDIA driver, and run the installer/VS Code as Administrator if required.
- Out of memory: use `--batch-size 1` or run with `--device cpu`.

For the same instructions in English and Chinese, see [PROJECT_STEP_BY_STEP_EN.md](PROJECT_STEP_BY_STEP_EN.md) and [PROJECT_STEP_BY_STEP_CN.md](PROJECT_STEP_BY_STEP_CN.md).
