# SRST：在 Windows 11 上安装并运行演示

本说明的目的，是让你从 GitHub 下载项目后，自动配置所需环境，并使用附带模型运行 `fitting.ipynb`，查看分子定位、超分辨重建和不确定度筛选结果。演示所需的数据、模型和 PSF 标定文件已随项目提供。

**只需要记住一个启动文件：`start_srst.bat`。首次使用和以后使用，都双击同一个文件。**

## 1. 开始前准备什么

| 项目 | 要求 |
| --- | --- |
| 系统 | Windows 11，x64 电脑 |
| Conda | 已安装 Conda，Miniconda、Anaconda 或 Miniforge 均可 |
| 网络 | 首次启动需要联网下载依赖，能访问 GitHub、Conda 渠道、PyPI 和 PyTorch 下载站 |
| 空间 | 建议至少预留 12 GB，用于独立环境及下载缓存 |
| 显卡 | 可使用兼容的 NVIDIA GPU；没有可用 GPU 时，演示自动使用 CPU，速度会慢一些 |

**请先安装 Conda。** 尚未安装时，推荐从 [Miniconda 官方下载页](https://www.anaconda.com/download/success)选择 **Miniconda > Windows 64-Bit Graphical Installer**，安装完成后继续下面的步骤。已有 Conda 可直接继续。

启动器使用已有 Conda 创建独立环境，并自动安装该环境所需的 Python、Jupyter 等依赖。无需另行安装 Python、Jupyter 或 CUDA Toolkit，也无需先训练模型。没有检测到 Conda 时，启动器会报错停止并给出上述网址，不会自动下载环境管理器。SRST 环境安装通常不需要管理员权限。

## 2. 下载并完整解压项目

打开 [GitHub 项目页](https://github.com/Tailong-Chen/SRST)，选择 **Code > Download ZIP**，或[直接下载 ZIP](https://github.com/Tailong-Chen/SRST/archive/refs/heads/main.zip)。

将 ZIP 完整解压到你能读写的目录，进入 `SRST-main` 文件夹。确认其中有 `start_srst.bat`、`fitting.ipynb` 和 `dataset`、`network`、`psfmod`、`scripts`、`requirements` 等目录，然后继续。

**请先解压，不要直接在压缩包内运行启动文件，也不要只复制启动文件。** 测试另一台电脑的首次安装时，使用新下载并解压的项目，让它自己建立环境。

## 3. 首次启动：等待环境准备完成

双击 **`start_srst.bat`**。终端窗口会自动完成以下步骤：

1. 查找已安装的 Conda，创建名为 `srst_demo` 的独立环境，使用 Python 3.9。
2. 安装编译版 `spline`、PyTorch、科学计算依赖和 Jupyter。
3. 检查依赖，注册 **SRST (srst_demo)** 内核，并验证 Notebook 可以输出图片。
4. 使用附带模型处理 9 帧示例数据，检查定位流程。
5. 启动 Jupyter，在浏览器中打开 **`fitting.ipynb`**。

首次启动时间主要取决于下载速度。CUDA 版 PyTorch 的下载量约为 3.5 GB；终端仍在下载或显示进度时，保持窗口打开并等待。

出现 `Connection timed out` 或 `TLS/SSL ... EOF` 后，如果随后显示 `Resuming download`，且已下载大小继续增加，表示正在自动续传。此时继续等待即可。最终出现 `ERROR` 或失败退出时，再按下面的失败处理步骤操作。

只有全部安装检查通过后，才会保存安装完成记录。安装中途失败时，下次双击仍会执行安装检查，不会直接使用未完成的环境。

## 4. 在 Notebook 中运行演示

浏览器打开 Notebook 后，确认内核为 **SRST (srst_demo)**，然后选择顶部菜单 **Cell > Run All**，依次运行所有单元。

演示已经配置好默认输入，你可以先完整运行一次，无需修改路径：

| 输入 | 文件 |
| --- | --- |
| 示例图像 | `dataset/frame.tif` |
| 预训练模型 | `network/experiment1/model_2.pt` |
| 相机、尺度和处理参数 | `network/experiment1/param_run.yaml` |

运行定位单元时会显示处理进度。后面的单元会显示单帧定位结果、重建图和不确定度筛选结果。CPU 运行较慢，等待当前单元完成后再查看结果。

也可以使用 Shift+Enter 逐个运行代码单元。使用 VS Code 时，打开同一份 `fitting.ipynb`，选择 **SRST (srst_demo)** 内核即可。

## 5. 以后使用和退出

以后仍然双击 **`start_srst.bat`**。已通过检查的环境会被复用，直接打开 Notebook，不会每次重新安装依赖。依赖或安装检查文件更新后，启动器会重新执行准备和检查。

使用 Notebook 时保持启动终端打开。结束后在终端按 **Ctrl+C**，按提示确认停止 Jupyter，再关闭窗口。仅关闭浏览器页面不会自动停止服务器。

## 6. 启动失败时怎么处理

先看终端最后的错误信息；完整安装和启动日志位于项目根目录 **`srst.log`**。

| 现象 | 处理方法 |
| --- | --- |
| 提示未找到 Conda | 从 [Miniconda 官方下载页](https://www.anaconda.com/download/success)安装 Windows 64 位版，然后再次双击启动文件；如已安装到自定义位置，可在 Miniconda / Anaconda Prompt 中运行启动文件 |
| 下载超时，但正在续传 | 保持窗口打开，观察已下载大小是否继续增加 |
| 下载最终失败 | 检查网络对下载站的访问，恢复后再次双击 `start_srst.bat`；已经下载完整的缓存可复用，未完成的大文件不保证保留进度 |
| 提示缺少模型或示例文件 | 重新下载并完整解压项目，确认启动文件和资源都在同一份项目内 |
| 终端显示 Jupyter 已启动，但浏览器没有打开 | 将终端显示的本地访问链接复制到浏览器 |
| Notebook 内核未选中 | 在 Notebook 中选择 **SRST (srst_demo)**；重新启动入口也会刷新内核注册 |
| 已安装后手动改过依赖，出现导入错误 | 使用下面的修复命令，重新安装并执行环境检查 |

修复环境时，在项目文件夹空白处右键，选择 **在终端中打开**，执行：

```powershell
.\start_srst.bat -Repair
```

修复成功后会自动打开 Notebook。如果仍然失败，保留 `srst.log`，根据其中标出的失败阶段继续排查。

## 7. 环境和结果保存在哪里

安装后得到的是名为 **`srst_demo`** 的独立 Conda 环境，与 `base` 和其他环境隔离。环境位于 Conda 能检索的环境目录，通常优先使用用户目录 `%USERPROFILE%\.conda\envs\srst_demo`；实际位置会显示在安装终端中，并记录在项目的 `.runtime/environment.json`。

在 **Miniconda / Anaconda Prompt** 等已配置 Conda 的终端中，可以像自己创建的环境一样检索和激活：

```bat
conda env list
conda activate srst_demo
```

列表中会显示 `srst_demo` 名称和环境路径。日常运行仍然双击 `start_srst.bat`，无需手动激活。启动器不会修改系统 Python、PATH 或终端配置；GPU 使用需要兼容的 NVIDIA 驱动，PyTorch 自带 CUDA 运行库。

旧版本安装在项目内的环境会先克隆到命名环境，再重新检查，旧副本保留。若已存在一个未由本安装器创建的 `srst_demo`，启动器会停止并提示；先为自己的同名环境更名，再重新启动。

首次安装的 9 帧检查结果保存在 **`outputs/installation_check`**。Notebook 的图像结果显示在页面内，可以按需保存 Notebook 或图片。

需要更换自己的数据、修改网络、训练或使用命令行推理时，继续阅读[项目结构与开发说明](project.md)。
