# 项目结构与开发说明

SRST 的核心流程是：连续 TIFF 帧经过相机校正和裁剪，输入 `CNNBiLSTM` 网络，再将预测转换为分子定位结果。随项目提供的模型使用连续 9 帧信息；首次运行直接使用该模型，无需训练。

## 从哪里开始

| 需求 | 入口 |
| --- | --- |
| 首次安装或日常打开 Notebook | 根目录 `start_srst.bat`，见[中文安装说明](windows_zh.md) |
| 批量推理和导出结果 | `demo.py` / `scripts/run_demo_windows.ps1` |
| 修改网络 | `Net/CNNLSTM.py`、`Net/Unet.py` |
| 修改训练及模拟 | `train.py`、`generic/` |
| 修改安装依赖 | `requirements/` |

## 目录职责

| 路径 | 内容 |
| --- | --- |
| `fitting.ipynb` | 当前 SRST 演示：读取模型与 TIFF，定位，绘制重建与不确定度筛选结果 |
| `demo.py` | 命令行推理，支持设备、帧数、批量、输入和输出路径参数 |
| `train.py` | 训练配置、训练循环及实际使用的 `LossFunc` 实现 |
| `Choose_Device.py` | 旧代码共用的设备状态；Demo 会将其同步到所选 CPU/GPU |
| `Net/` | CNNBiLSTM、U-Net 和网络示意图 |
| `generic/` | 训练使用的自定义发射体、闪烁采样和随机模拟 |
| `decode/` | 基于 DECODE 的仿真、推理、坐标变换、后处理、评价、绘图及文件读写 |
| `decode/test/` | 保留的 DECODE 测试及测试资源 |
| `decode/utils/examples/` | DECODE 自带示例，由 `decode.utils.notebooks.load_examples()` 使用 |
| `dataset/` | 演示 TIFF |
| `network/experiment1/` | 预训练权重和参数 |
| `psfmod/` | PSF spline 标定数据 |
| `scripts/` | `start_windows.ps1` 统一调度安装和 Notebook；其余脚本提供安装、推理、内核检查等内部实现 |
| `requirements/` | Conda 二进制依赖、Python 依赖和已验证版本约束 |
| `tests/` | 本项目的 Windows 安装与启动回归测试 |
| `docs/` | 中英文安装指南和项目说明 |

`.runtime/` 是本机独立环境及下载缓存，`outputs/` 是推理结果与验证产物，均不进入 GitHub 源码包。

## 推理的数据流

1. 从 `network/experiment1/param_run.yaml` 读取相机、尺度和后处理参数。
2. 用 `Net.CNNLSTM.CNNBiLSTM` 加载 `model_2.pt`，同步设备状态。
3. 读取 `dataset/frame.tif`，进行相机反变换、按 8 的倍数裁剪和强度缩放。
4. `decode.neuralfitter.Infer` 按连续 9 帧组织输入并执行网络。
5. 将尺度还原，转换坐标，合并邻近预测，得到 `EmitterSet`。
6. 命令行入口保存 CSV、PT、重建 PNG 和运行摘要；Notebook 继续绘制和筛选。

CSV 的 x/y 使用像素坐标、z 使用 nm；重建预览通过 `xyz_nm` 将坐标转为 nm。替换实验数据时，应同时核对相机参数和像素尺寸。

`decode/neuralfitter/inference/infer.py` 是上游通用模型入口，不对应本项目附带的 CNNBiLSTM 权重。当前模型请使用根目录 Demo 或 Notebook。

## 训练入口

训练使用 `generic.random_simulation` 生成带闪烁的分子和模拟图像，再通过 `train.py` 中的网络、损失和训练循环更新权重。PSF 模拟由 `spline` 的编译模块执行。

运行 `train.py` 前，检查文件末尾的 `param_file`、`calibration_file`、`model_dir`、`ckpt_dir` 和设备设置。当前默认输出是 `network/experiment1`，训练会写参数及轮换模型文件；训练新实验时将输出改到新目录，以保留演示模型。该训练入口保留了原有 CUDA 设置，安装时的 Demo 检查不代表完成了训练验证。

## 依赖与检查

唯一安装配置位于 `requirements/`：

- `windows-conda.txt`：Python 3.9、编译版 `spline` 和 pip。
- `windows-demo.txt`：PyTorch、科学计算和 Notebook 的直接依赖。
- `windows-constraints.txt`：固定已验证的 Python 依赖版本。

`start_srst.bat` 是唯一的 Windows 批处理入口。安装器在依赖检查、真实 Notebook 内核绘图和 9 帧推理全部通过后，写入 `.runtime/srst_demo/.srst-ready.json`。该记录包含环境路径以及依赖和安装检查文件的摘要；缺失、损坏或与当前文件不一致时，启动入口重新执行安装。日常启动刷新内核注册，再打开 Notebook。手动改动环境后可使用 `start_srst.bat -Repair` 强制重新安装和检查。日志统一写入根目录 `srst.log`。

开发时可直接调用内部脚本。以下 CPU 检查仍使用项目独立环境：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run_demo_windows.ps1 --device cpu --max-frames 9 --batch-size 1
```

在 SRST 环境中，从项目根目录运行本项目的启动测试：

```bat
python -m unittest tests.test_windows_launchers -v
```

这些测试使用含空格路径并替换外部环境管理器命令，不下载大型依赖。安装器另外执行依赖检查、真实 Notebook 内核绘图检查及 9 帧模型推理。DECODE 测试属于保留的上游测试集合，部分测试依赖额外资源或历史接口。

清理后保留了模型、数据、PSF、有效源码和被引用的上游示例；移除了 Python 字节码、重复说明和 Notebook、失效的机器环境导出，以及未被任何项目入口引用的旧预测、模拟和损失副本。Notebook 源码保留，已执行输出和计数已清空。
