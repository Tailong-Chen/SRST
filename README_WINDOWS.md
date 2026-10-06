# SRST on Windows 11: install and run the notebook

For Windows 11 x64. Extract the complete project into a writable folder. Python, Conda and Jupyter do not need to be installed beforehand; no model training is required. The first installation needs internet access and several GB of downloads (the CUDA PyTorch wheel is about 3.5 GB). Allow at least 12 GB of free disk space for the environment and download cache.

Download the project using **Code > Download ZIP** on [GitHub](https://github.com/Tailong-Chen/SRST), or use the [main branch ZIP](https://github.com/Tailong-Chen/SRST/archive/refs/heads/main.zip). Extract it completely and open the `SRST-main` folder. For a first-install test, use a new folder and let the installer create its own `.runtime` environment.

## 1. Install and open the notebook

Double-click `setup_and_run_demo.bat`.

The launcher finds an existing Conda installation or downloads official portable Micromamba with SHA-256 verification, creates an isolated Python 3.9 environment in `.runtime/srst_demo`, installs the compiled TuragaLab `spline` package and Python dependencies, registers **SRST (srst_demo)**, checks localization on nine example frames, and opens `fitting.ipynb` in your browser. No system Python, PATH or shell configuration changes are required.

Administrator privileges are normally unnecessary. GPU use requires a compatible NVIDIA driver. The PyTorch wheel includes its CUDA runtime, so a separate CUDA Toolkit is unnecessary. The demo uses CPU automatically when CUDA is unavailable.

To install without opening Jupyter, double-click `install_windows.bat`. To reopen the notebook later, double-click `run_notebook_windows.bat`.

## 2. Run the notebook

Select the kernel **SRST (srst_demo)**. Use **Cell > Run All**, or execute these code cells in order:

`0 -> 2 -> 3 -> 5 -> 7 -> 9 -> 11`

The notebook uses the bundled `dataset/frame.tif` and `network/experiment1/model_2.pt`. Cell 5 performs localization; later cells show per-frame detections, reconstruction and uncertainty filtering. The demo uses a batch size of one to avoid large GPU memory probes. CPU processing takes longer.

Keep the launcher terminal open while using Jupyter. Press Ctrl+C there when finished. In VS Code, open `fitting.ipynb` and select the same **SRST (srst_demo)** kernel.

## 3. Troubleshooting and distribution

Installation errors remain visible, and the full log is written to `setup_and_run_demo.log`. Rerun the installer after resolving a download or driver problem.

- Downloads require access to GitHub, the Conda channels, PyPI and the PyTorch download site.
- The PyTorch wheel is large. After a timeout or TLS/SSL EOF warning, keep the window open if `Resuming download` appears and the downloaded size increases. The installer allows a 120-second socket timeout, 10 connection retries and 20 resume attempts. If it finally exits with an error, resolve the network issue and rerun; restarting the installer does not guarantee preservation of an incomplete download.
- If `spline` cannot import, retain the log. Do not substitute an unrelated PyPI package into your system Python.
- For a CPU check, run `run_demo_windows.bat --device cpu --max-frames 9 --batch-size 1`.
- Reopen with `run_notebook_windows.bat` to refresh the kernel registration.

The installation check writes `outputs/installation_check`. The separate command-line demo remains available through `run_demo_windows.bat`, with normal outputs in `outputs/demo`.

Distribute the complete source, `scripts/`, notebook, sample TIFF, pretrained model and PSF calibration. Exclude `.runtime/`, `outputs/` and installation logs. The original `environment.yml` and `requirements.txt` are historical machine exports; the installer uses `requirements-windows-conda.txt` for binary dependencies and `requirements-windows-demo.txt` with `constraints-windows-demo.txt` for tested Python package versions.
