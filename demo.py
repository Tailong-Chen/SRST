"""Run the bundled SRST pretrained demo on a TIFF stack.

This is the supported quick-start path for the checked-in ``model_2.pt``.
That checkpoint contains the custom ``Net.CNNLSTM.CNNBiLSTM`` weights, so it
must not be loaded through the generic SigmaMUNet CLI.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Optional, Union

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

import decode
import decode.utils
import Choose_Device as device_config
import Net.CNNLSTM as cnn_lstm


ROOT = Path(__file__).resolve().parent


def _device(value: str) -> torch.device:
    if value == "auto":
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    device = torch.device(value)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested, but no CUDA device is available.")
    return device


def _build_model(param, model_path: Path, device: torch.device):
    model = cnn_lstm.CNNBiLSTM(
        1,
        10,
        seq_len=param.HyperParameter.channels_in,
        pad_convs=True,
        depth=2,
        initial_features=48,
        norm=None,
        norm_groups=None,
        sigma_eps_default=0.005,
    )
    state = torch.load(model_path, map_location=device)
    model.load_state_dict(state, strict=True)
    return model.to(device).eval()


def run_demo(
    *,
    frame_path: Path,
    model_path: Path,
    param_path: Path,
    output_dir: Path,
    device_name: str,
    max_frames: Optional[int],
    batch_size: Optional[Union[int, str]],
):
    param = decode.utils.param_io.load_params(str(param_path))
    device = _device(device_name)
    # CNNBiLSTM initialises its ConvLSTM state through this legacy module.
    # Keep that global in sync when the user explicitly selects CPU/GPU.
    device_config.device = device

    frames = decode.utils.frames_io.load_tif(frame_path)
    if frames.ndim != 3:
        raise ValueError(f"Expected a TIFF stack with shape [frames, height, width], got {tuple(frames.shape)}")
    if max_frames is not None:
        if max_frames < param.HyperParameter.channels_in:
            raise ValueError("max_frames must be at least channels_in (9) for this model.")
        frames = frames[:max_frames]

    model = _build_model(param, model_path, device)
    camera = decode.simulation.camera.Photon2Camera.parse(param)
    camera.device = "cpu"

    frame_proc = decode.neuralfitter.utils.processing.TransformSequence(
        [
            decode.neuralfitter.utils.processing.wrap_callable(camera.backward),
            decode.neuralfitter.frame_processing.AutoCenterCrop(8),
            decode.neuralfitter.scale_transform.AmplitudeRescale.parse(param),
        ]
    )
    size_processed = decode.neuralfitter.frame_processing.get_frame_extent(
        frames.unsqueeze(1).size(), frame_proc.forward
    )
    # Keep the coordinate convention used by the legacy fitting notebook.
    frame_extent = (
        (0, size_processed[-2]),
        (0, size_processed[-1]),
    )
    post_proc = decode.neuralfitter.utils.processing.TransformSequence(
        [
            decode.neuralfitter.scale_transform.InverseParamListRescale.parse(param),
            decode.neuralfitter.coord_transform.Offset2Coordinate(
                xextent=frame_extent[0],
                yextent=frame_extent[1],
                img_shape=size_processed[-2:],
            ),
            decode.neuralfitter.post_processing.SpatialIntegration(
                raw_th=param.PostProcessingParam.raw_th,
                xy_unit="px",
                px_size=param.Camera.px_size,
            ),
        ]
    )

    if batch_size is None or (batch_size == "auto" and device.type != "cuda"):
        # DECODE probes a safe CUDA batch size; CPU stays at one sample to avoid
        # the library's CPU warning and excessive memory use.
        batch_size = "auto" if device.type == "cuda" else 1
    if isinstance(batch_size, int) and batch_size < 1:
        raise ValueError("batch_size must be positive or 'auto'.")
    started = time.perf_counter()
    infer = decode.neuralfitter.Infer(
        model=model,
        ch_in=param.HyperParameter.channels_in,
        frame_proc=frame_proc,
        post_proc=post_proc,
        device=device,
        num_workers=0,
        pin_memory=False,
        batch_size=batch_size,
    )
    emitters = infer.forward(frames)
    elapsed = time.perf_counter() - started

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "emitters.csv"
    pt_path = output_dir / "emitters.pt"
    png_path = output_dir / "reconstruction.png"
    summary_path = output_dir / "summary.json"
    emitters.save(csv_path)
    emitters.save(pt_path)

    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
    if len(emitters):
        xyz_nm = emitters.xyz_nm.detach().cpu()
        color = xyz_nm[:, 2]
        ax.scatter(xyz_nm[:, 0], xyz_nm[:, 1], c=color, s=3, linewidths=0)
        ax.set_aspect("equal", adjustable="box")
    else:
        ax.text(0.5, 0.5, "No emitters passed the post-processing threshold", ha="center", va="center")
    ax.set_xlabel("x (nm)")
    ax.set_ylabel("y (nm)")
    ax.set_title("SRST demo reconstruction")
    fig.savefig(png_path, dpi=150)
    plt.close(fig)

    summary = {
        "device": str(device),
        "torch_version": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_name": (
            torch.cuda.get_device_name(device) if device.type == "cuda" else None
        ),
        "batch_size": batch_size,
        "frames_used": int(frames.shape[0]),
        "frame_shape": [int(v) for v in frames.shape[1:]],
        "emitters": int(len(emitters)),
        "elapsed_seconds": round(elapsed, 3),
        "model": str(model_path),
        "parameters": str(param_path),
        "outputs": {
            "csv": str(csv_path),
            "pt": str(pt_path),
            "preview": str(png_path),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", type=Path, default=ROOT / "dataset" / "frame.tif")
    parser.add_argument("--model", type=Path, default=ROOT / "network" / "experiment1" / "model_2.pt")
    parser.add_argument("--params", type=Path, default=ROOT / "network" / "experiment1" / "param_run.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "demo")
    parser.add_argument("--device", default="auto", help="auto, cpu, or cuda[:index]")
    parser.add_argument("--max-frames", type=int, default=20, help="Frames to process; use 0 for the full stack")
    parser.add_argument(
        "--batch-size",
        default=None,
        help="Inference batch size; use auto for CUDA (default) or a positive integer.",
    )
    args = parser.parse_args()

    for path in (args.frames, args.model, args.params):
        if not path.exists():
            raise FileNotFoundError(path)
    max_frames = None if args.max_frames == 0 else args.max_frames
    run_demo(
        frame_path=args.frames,
        model_path=args.model,
        param_path=args.params,
        output_dir=args.output,
        device_name=args.device,
        max_frames=max_frames,
        batch_size=(
            None
            if args.batch_size is None
            else (int(args.batch_size) if args.batch_size.lower() != "auto" else "auto")
        ),
    )


if __name__ == "__main__":
    main()
