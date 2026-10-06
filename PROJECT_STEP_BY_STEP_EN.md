# SRST Windows 11 quick guide

This guide covers only the three actions needed for the demo:

1. install the environment;
2. run pretrained GPU localization;
3. run the old `fitting.ipynb` notebook in VS Code.

No training is required.

## 1. Install once

1. Extract `SRST-Windows.zip`.
2. Open the extracted `SRST` folder.
3. For GPU use, install/update the NVIDIA driver. If the driver is visible only from an elevated shell, run the next step as Administrator.
4. Right-click `setup_and_run_demo.bat` and choose **Run as administrator**.

The script creates a Conda environment named `srst_demo`, installs the project dependencies and PyTorch CUDA 12.8, checks the checkpoint, and registers the kernel named `SRST (srst_demo)`. If no Conda installation is found, it tries `winget` Miniforge. Without `winget`, install Miniconda or Miniforge and run `install_windows.bat` again.

The bundled pretrained model is `network\\experiment1\\model_2.pt`. The installer does not train a model.

## 2. Run GPU localization

After installation, open Command Prompt or PowerShell in the project folder:

```bat
run_demo_windows.bat --device cuda:0 --max-frames 20
```

This uses the first GPU and processes 20 frames. For a machine that may not have a GPU, use:

```bat
run_demo_windows.bat --device auto --max-frames 20
```

For a low-memory GPU:

```bat
run_demo_windows.bat --device cuda:0 --max-frames 20 --batch-size 1
```

Results are written to `outputs\\demo`:

- `emitters.csv`: localized molecule coordinates;
- `reconstruction.png`: quick visualization;
- `summary.json`: device, CUDA status, GPU name, frame count, and timing.

Open `summary.json`. A successful GPU run contains:

```json
"device": "cuda:0",
"cuda_available": true
```

`cuda_device_name` identifies the selected GPU. If `cuda:0` fails, run `nvidia-smi`, update the NVIDIA driver, and rerun the installer from an Administrator terminal when necessary.

If the window closes before you can read the message, run `cmd /k setup_and_run_demo.bat` from the project folder. The launcher keeps the window open and writes `setup_and_run_demo.log` beside the batch files.

## 3. Run the old notebook in VS Code

1. Open the extracted project folder in VS Code.
2. Open `fitting.ipynb`.
3. Select the Python kernel **SRST (srst_demo)**.
4. Run these code cells in order:

   `0 → 2 → 3 → 5 → 7 → 9 → 11`

Cell 5 loads `dataset/frame.tif` and performs localization. Cells 7, 9, and 11 display and filter the predicted molecule positions. `Choose_Device.py` selects `cuda:0` automatically when PyTorch reports CUDA; otherwise it selects CPU.

## 4. Common fixes

- **Conda is missing**: install Miniconda or Miniforge, reopen the terminal, and run `install_windows.bat`.
- **CUDA is unavailable**: check `nvidia-smi`, update the NVIDIA driver, and run the installer/VS Code as Administrator if GPU access is restricted.
- **GPU out of memory**: add `--batch-size 1`; the CPU fallback is `run_demo_windows.bat --device cpu`.
- **Wrong notebook kernel**: select `SRST (srst_demo)` instead of the system Python environment.

The original `environment.yml` is a historical machine-specific export. Use `install_windows.bat` for this Windows demo.
