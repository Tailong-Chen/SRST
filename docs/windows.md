# SRST: install and run the demo on Windows 11

This guide takes you from a GitHub download to a working environment and the bundled `fitting.ipynb` demo. The demo uses the supplied model and TIFF to show localization, reconstruction and uncertainty filtering. No model training is needed.

**Use one file for both the first launch and later launches: `start_srst.bat`.**

## 1. What you need

| Item | Requirement |
| --- | --- |
| System | Windows 11 on an x64 computer |
| Conda | An existing Conda installation: Miniconda, Anaconda or Miniforge |
| Internet | First-launch access to GitHub, the Conda channels, PyPI and the PyTorch download site |
| Disk space | At least 12 GB recommended for the environment and download cache |
| GPU | A compatible NVIDIA GPU is optional; the demo uses CPU when CUDA is unavailable |

**Install Conda first.** If it is missing, use the [official Miniconda download page](https://www.anaconda.com/download/success) and choose **Miniconda > Windows 64-Bit Graphical Installer**. If Conda is already installed, continue below.

SRST uses the existing Conda installation to create its own environment and installs Python, Jupyter and the other dependencies there. Separate Python, Jupyter and CUDA Toolkit installations and model training are unnecessary. If Conda cannot be found, startup stops with an error and the download URL; no environment manager is downloaded automatically. Administrator privileges are normally unnecessary for the SRST environment setup.

## 2. Download and extract the project

On the [GitHub project page](https://github.com/Tailong-Chen/SRST), choose **Code > Download ZIP**, or [download the ZIP directly](https://github.com/Tailong-Chen/SRST/archive/refs/heads/main.zip).

Extract the complete archive into a writable folder and open `SRST-main`. Check that it contains `start_srst.bat`, `fitting.ipynb` and the `dataset`, `network`, `psfmod`, `scripts` and `requirements` folders.

Run the launcher from the extracted folder. Do not run it inside the ZIP or copy only the launcher. To test first installation on another computer, download and extract a new copy and let it create its own environment.

## 3. First launch: let setup finish

Double-click **`start_srst.bat`**. The terminal automatically:

1. Finds the installed Conda and creates an isolated environment named `srst_demo` with Python 3.9.
2. Installs the compiled `spline` package, PyTorch, scientific dependencies and Jupyter.
3. Checks dependencies, registers **SRST (srst_demo)** and tests inline plotting in the real notebook kernel.
4. Runs the supplied model on nine example frames to check localization.
5. Starts Jupyter and opens **`fitting.ipynb`** in your browser.

The first launch depends mainly on download speed. The CUDA PyTorch wheel is about 3.5 GB. Keep the terminal open while progress continues.

After a timeout or TLS/SSL EOF warning, `Resuming download` with an increasing downloaded size means the transfer is continuing. Wait for completion. Only act on a final error or failed exit.

A successful setup record is saved only after all checks pass. An interrupted setup is checked again on the next launch rather than treated as a ready environment.

## 4. Run the notebook

Select **SRST (srst_demo)** as the kernel, then choose **Cell > Run All**. The default inputs are already configured:

| Input | File |
| --- | --- |
| Example TIFF | `dataset/frame.tif` |
| Pretrained model | `network/experiment1/model_2.pt` |
| Camera, scale and processing parameters | `network/experiment1/param_run.yaml` |

The localization cell displays processing progress. Later cells show per-frame detections, reconstruction and uncertainty filtering. CPU execution takes longer; let the active cell finish before inspecting its results.

You can also run cells sequentially with Shift+Enter. In VS Code, open the same notebook and select **SRST (srst_demo)**.

## 5. Later launches and shutdown

Double-click **`start_srst.bat`** again. A verified environment is reused and the notebook opens directly. Setup runs again when dependencies or setup checks change.

Keep the launcher terminal open while using Jupyter. To finish, press **Ctrl+C** there and confirm shutdown when prompted. Closing the browser tab alone does not stop the server.

## 6. If startup fails

Read the last terminal error. The full installation and launch log is **`srst.log`** in the project folder.

| Symptom | Action |
| --- | --- |
| Conda not found | Install Windows 64-bit Miniconda from the [official download page](https://www.anaconda.com/download/success), then launch again; if Conda is already installed in a custom location, run the launcher from Miniconda / Anaconda Prompt |
| Download interrupted but resuming | Leave the window open while the downloaded size increases |
| Download finally failed | Restore access to the download sites and launch again; completed downloads can be cached, but incomplete progress is not guaranteed across restarts |
| Model or example file missing | Download and fully extract the project again |
| Jupyter started but the browser did not open | Copy the local URL shown in the terminal into your browser |
| Notebook kernel not selected | Select **SRST (srst_demo)**; launching again also refreshes registration |
| Imports fail after manual package changes | Run the repair command below to reinstall and verify the environment |

Open a terminal in the project folder and run:

```powershell
.\start_srst.bat -Repair
```

A successful repair opens the notebook. If it still fails, retain `srst.log` and check the reported failure stage.

## 7. Environment and results

The isolated Conda environment is named **`srst_demo`**. It lives in a directory searched by Conda, preferably `%USERPROFILE%\.conda\envs\srst_demo`. The terminal shows the selected path, and `.runtime/environment.json` records it for this project.

In an initialized Conda terminal, such as Miniconda / Anaconda Prompt, use:

```bat
conda env list
conda activate srst_demo
```

The list shows its name and path. For everyday use, double-click `start_srst.bat`; manual activation is unnecessary. Setup does not change system Python, PATH or shell configuration. GPU use requires a compatible NVIDIA driver; PyTorch includes its CUDA runtime.

An environment installed by the old project-local setup is cloned to the named environment and checked again. The original remains available. Setup stops if an unrelated `srst_demo` environment already exists; rename that environment before running this installer.

The nine-frame installation check writes **`outputs/installation_check`**. Notebook plots appear in the page and can be saved as needed.

For custom data, network changes, training and command-line inference, see the [project guide](project.md).
