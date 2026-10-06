# SRST Windows 11 简明运行说明

这里只保留运行别人最需要的三步：

1. 安装环境；
2. 用 GPU 运行预训练定位 demo；
3. 在 VS Code 运行旧的 `fitting.ipynb`。

不需要重新训练模型。

## 1. 安装一次

1. 解压 `SRST-Windows.zip`。
2. 打开解压后的 `SRST` 文件夹。
3. 如果要用 GPU，先安装或更新 NVIDIA 驱动。如果只有管理员终端能看到 GPU，后面也要用管理员权限运行。
4. 右键 `setup_and_run_demo.bat`，选择**以管理员身份运行**。

脚本会创建 Conda 环境 `srst_demo`，安装项目依赖和 PyTorch CUDA 12.8，检查预训练模型，并注册 `SRST (srst_demo)` Notebook 内核。如果没有 Conda，脚本会尝试用 `winget` 安装 Miniforge；如果没有 `winget`，先安装 Miniconda 或 Miniforge，再重新运行 `install_windows.bat`。

预训练模型是 `network\\experiment1\\model_2.pt`，安装过程不会重新训练模型。

## 2. 运行 GPU 定位

安装完成后，在项目文件夹打开 CMD 或 PowerShell：

```bat
run_demo_windows.bat --device cuda:0 --max-frames 20
```

这会使用第一个 GPU，处理 20 帧。需要兼容没有 GPU 的电脑时，用：

```bat
run_demo_windows.bat --device auto --max-frames 20
```

显存较小时，用：

```bat
run_demo_windows.bat --device cuda:0 --max-frames 20 --batch-size 1
```

结果在 `outputs\\demo`：

- `emitters.csv`：定位出的分子坐标；
- `reconstruction.png`：快速可视化；
- `summary.json`：设备、CUDA、GPU 名称、帧数和耗时。

打开 `summary.json`，GPU 成功运行应看到：

```json
"device": "cuda:0",
"cuda_available": true
```

`cuda_device_name` 会显示实际 GPU 名称。如果 `cuda:0` 报错，先运行 `nvidia-smi`，更新 NVIDIA 驱动；如果 GPU 只在管理员终端可见，请用管理员权限运行安装器和 VS Code。

如果双击后窗口仍然关闭，请在项目文件夹打开终端并运行 `cmd /k setup_and_run_demo.bat`。启动器会保持窗口，并在批处理文件旁边写入 `setup_and_run_demo.log`。

## 3. 在 VS Code 运行旧 Notebook

1. 用 VS Code 打开解压后的项目文件夹。
2. 打开 `fitting.ipynb`。
3. 选择 Python 内核 **SRST (srst_demo)**。
4. 按下面顺序运行代码单元：

   `0 → 2 → 3 → 5 → 7 → 9 → 11`

第 5 个代码单元读取 `dataset/frame.tif` 并完成定位；第 7、9、11 个代码单元显示并筛选预测的分子位置。只要 PyTorch 能看到 CUDA，Notebook 会自动使用 `cuda:0`；否则自动使用 CPU。

## 4. 常见问题

- **找不到 Conda**：安装 Miniconda 或 Miniforge，重新打开终端，再运行 `install_windows.bat`。
- **CUDA 不可用**：检查 `nvidia-smi`，更新 NVIDIA 驱动，必要时用管理员权限运行安装器和 VS Code。
- **GPU 显存不足**：加 `--batch-size 1`，或运行 `run_demo_windows.bat --device cpu`。
- **Notebook 内核错误**：选择 `SRST (srst_demo)`，不要选择系统 Python。

原来的 `environment.yml` 是历史机器导出文件。Windows demo 请使用 `install_windows.bat`。
