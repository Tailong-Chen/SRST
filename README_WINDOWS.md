# Windows one-click demo

For the full project walkthrough, see [PROJECT_STEP_BY_STEP_EN.md](PROJECT_STEP_BY_STEP_EN.md).

This path runs the bundled pretrained SRST checkpoint. “Pretrained” means the demo uses `network\experiment1\model_2.pt` directly for inference; it does not start a new 500-epoch training job. It is separate from the historical `environment.yml`, which is a machine-specific Windows export with an obsolete absolute prefix and mixed CUDA package pins.
The curated environment supports both the scripted demo and the repaired legacy notebook. Full 500-epoch training remains a separate workflow.

## Requirement

The installer uses an existing Miniconda, Anaconda, or Miniforge installation. If none is found and Windows includes `winget`, it attempts a per-user Miniforge installation automatically. For GPU use, Windows 11 needs a current NVIDIA driver. The environment installs the PyTorch 2.8.0 CUDA 12.8 wheel; a separate CUDA Toolkit installation is not required. The installer prints the CUDA runtime/device and, when `nvidia-smi` is available, runs a 9-frame CUDA smoke test. If CUDA is visible only from an elevated terminal, run the installer and VSCode as Administrator; otherwise `auto` deliberately falls back to CPU. On machines without an NVIDIA GPU, the same environment falls back to CPU.

## Install and run

For a single install-and-run demo action, double-click `setup_and_run_demo.bat`.
You can also install once with `install_windows.bat` and launch the scripted
demo later with `run_demo_windows.bat`.

To use the repaired legacy notebook in VSCode, open the repository folder and
open `fitting.ipynb`. Select the `SRST (srst_demo)` Python kernel. The notebook
selects CPU/GPU automatically and loads the same `CNNBiLSTM` checkpoint as the
scripted demo.

The default run processes the first 20 frames so it finishes quickly. On CUDA, the inference batch size defaults to DECODE's safe automatic probe; on CPU it uses batch size 1. Results are written to `outputs\demo`:

- `emitters.csv`: localized emitters;
- `emitters.pt`: DECODE `EmitterSet`;
- `reconstruction.png`: quick visualization;
- `summary.json`: device, frame count, emitter count, timing, and output paths.

To process the complete TIFF stack:

```bat
run_demo_windows.bat --max-frames 0
```

To force CPU or a specific GPU:

```bat
run_demo_windows.bat --device cpu
run_demo_windows.bat --device cuda:0
```

If a low-memory GPU still runs out of memory, force a smaller batch:

```bat
run_demo_windows.bat --device cuda:0 --batch-size 1
```

The launcher uses `Net.CNNLSTM.CNNBiLSTM`, which matches `network\experiment1\model_2.pt`. The generic DECODE `SigmaMUNet` inference entry point is not compatible with this checkpoint.

## Troubleshooting

- If Conda is not found, install Miniconda and run the installer again.
- If `nvidia-smi` works only in an Administrator terminal, run `install_windows.bat` and VSCode as Administrator so the notebook inherits GPU access.
- If `nvidia-smi` works but the installer reports that PyTorch cannot access CUDA, update the NVIDIA driver and rerun `install_windows.bat`.
- If CUDA is unavailable, omit `--device cuda:0`; `auto` selects CPU automatically.
- If an old `srst_demo` environment is present, rerun `install_windows.bat` to update it.
