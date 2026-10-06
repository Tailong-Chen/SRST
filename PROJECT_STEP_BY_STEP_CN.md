# SRST Windows 11 一键安装与 Notebook 演示

适用于 Windows 11 x64。将完整项目解压到可写目录后即可安装，无需预先配置 Python、Conda 或 Jupyter，也不需要训练模型。首次安装需联网下载数 GB 的依赖，其中 CUDA 版 PyTorch 约 3.5 GB；建议为环境和下载缓存预留至少 12 GB 空间。

从 [GitHub 项目页](https://github.com/Tailong-Chen/SRST) 选择 **Code > Download ZIP**，或直接[下载 main 分支 ZIP](https://github.com/Tailong-Chen/SRST/archive/refs/heads/main.zip)。完整解压后进入 `SRST-main` 文件夹。测试首次安装时请解压到一个新目录，不要复制其他电脑的 `.runtime` 环境；项目会在这个目录下创建自己的环境。

## 1. 一键安装并打开 Notebook

双击 `setup_and_run_demo.bat`。

脚本会自动完成：

1. 查找已有 Conda；没有时下载官方便携 Micromamba，并验证 SHA-256。
2. 在项目的 `.runtime/srst_demo` 创建独立 Python 3.9 环境。
3. 从 TuragaLab Conda 渠道安装预编译的 `spline`，再安装 PyTorch、科学计算及 Jupyter 依赖。
4. 注册 `SRST (srst_demo)` 内核，并用附带模型处理 9 帧，检查定位流程。
5. 在浏览器打开 `fitting.ipynb`。

正常情况下不需要管理员权限，也不修改系统 Python、PATH 或终端配置。GPU 运行需要兼容的 NVIDIA 驱动；PyTorch 自带 CUDA 运行库，无需单独安装 CUDA Toolkit。没有可用 GPU 时自动使用 CPU。

如果只想安装，双击 `install_windows.bat`。安装完成后再双击 `run_notebook_windows.bat` 打开 Notebook。

## 2. 运行 Notebook

确认内核为 **SRST (srst_demo)**，然后选择 **Cell → Run All**，或依次运行代码单元：

`0 → 2 → 3 → 5 → 7 → 9 → 11`

Notebook 使用附带的 `dataset/frame.tif` 和 `network/experiment1/model_2.pt`。第 5 个单元执行定位，后续单元显示单帧结果、重建图和不确定度筛选结果。默认批量为 1，避免 GPU 的大批量显存探测。CPU 处理会较慢。

使用 Jupyter 时保持启动终端打开；结束后在终端按 Ctrl+C 停止服务器。

在 VS Code 中也可以直接打开 `fitting.ipynb`，选择 **SRST (srst_demo)** 内核运行。

## 3. 安装失败时

窗口会保留错误信息，完整安装日志位于 `setup_and_run_demo.log`。修正网络或驱动问题后，可以再次运行安装入口。

- 下载失败：确认能够访问 GitHub、Conda 渠道、PyPI 和 PyTorch 下载站。
- PyTorch 下载较大，出现 `Connection timed out`、`TLS/SSL ... EOF` 后，如果仍显示 `Resuming download` 且已下载大小继续增加，表示正在续传，保持窗口打开即可。新版安装器将下载超时设为 120 秒、连接重试设为 10 次、续传尝试设为 20 次。只有最终出现 `ERROR` 或安装失败退出，才需要处理网络并重试；重新启动安装器不保证保留未完成的大文件进度。
- `spline` 导入失败：保留日志；不要把普通 PyPI 的同名包作为替代品安装到系统 Python。
- GPU 显存不足：先用命令行 `run_demo_windows.bat --device cpu --max-frames 9 --batch-size 1` 检查 CPU 路径。
- Notebook 找不到内核：重新运行 `run_notebook_windows.bat`，它会刷新内核注册。

安装定位检查的结果位于 `outputs/installation_check`。普通命令行 demo 仍可通过 `run_demo_windows.bat` 运行，默认结果位于 `outputs/demo`。

分发时包含完整源码、`scripts/`、Notebook、示例 TIFF、模型和 PSF 标定文件。不要把本机的 `.runtime/`、`outputs/` 或安装日志打包给别人。安装器使用 `requirements-windows-conda.txt` 和 `requirements-windows-demo.txt`，通过 `constraints-windows-demo.txt` 固定已验证的 Python 依赖版本；原来的 `environment.yml` 和 `requirements.txt` 是历史机器导出文件。
