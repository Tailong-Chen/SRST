"""Check the registered SRST kernel and its inline plot output."""

from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient


def main():
    root = Path(__file__).resolve().parents[1]
    source = (
        "%matplotlib inline\n"
        "import sys, pathlib, numpy, spline, torch, decode\n"
        f"assert pathlib.Path(sys.executable).resolve() == pathlib.Path({sys.executable!r}).resolve()\n"
        "import matplotlib.pyplot as plt\n"
        "plt.plot([0, 1], [0, 1]); plt.show(); plt.close()\n"
    )
    notebook = nbformat.v4.new_notebook(
        cells=[nbformat.v4.new_code_cell(source)]
    )
    NotebookClient(
        notebook, kernel_name="srst_demo", timeout=120,
        resources={"metadata": {"path": str(root)}},
    ).execute()
    if not any(
        "image/png" in output.get("data", {})
        for output in notebook.cells[0].outputs
    ):
        raise RuntimeError("The SRST kernel did not produce an inline plot.")
    print("SRST notebook kernel and inline plotting OK")


if __name__ == "__main__":
    main()
