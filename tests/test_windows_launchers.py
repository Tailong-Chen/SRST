"""Exercise the Windows entry points without downloading/installing packages.

Only the external Conda CLI is replaced. The real batch/PowerShell scripts
still resolve the environment, handle failures, and launch the notebook.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "nt", "Windows launchers require Windows")
class WindowsLaunchers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="SRST launcher test ")
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project with spaces"
        self.project.mkdir()
        for pattern in ("*.bat", "*.yml", "requirements-windows-*.txt", "constraints-windows-*.txt"):
            for path in ROOT.glob(pattern):
                shutil.copy2(path, self.project / path.name)
        if (ROOT / "scripts").exists():
            shutil.copytree(ROOT / "scripts", self.project / "scripts")
        for name in (
            "dataset/frame.tif", "network/experiment1/model_2.pt",
            "network/experiment1/param_run.yaml", "psfmod/spline_calibration_3dcal.mat",
            "fitting.ipynb",
        ):
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture", encoding="utf-8")
        self.conda_root = Path(self.tmp.name) / "Conda with spaces"
        self.environment = self.project / ".runtime" / "srst_demo"
        self.environment.mkdir(parents=True)
        (self.environment / "python.exe").write_text("fixture")
        bin_dir = self.conda_root / "condabin"
        bin_dir.mkdir(parents=True)
        self.calls = Path(self.tmp.name) / "calls.txt"
        (bin_dir / "conda.bat").write_text(
            '@echo off\n'
            '>>"%SRST_TEST_CALLS%" echo %*\n'
            'if "%SRST_TEST_FAIL_ENV%"=="1" echo fixture download failed 1>&2\n'
            'if "%~1"=="env" if "%~2"=="list" (\n'
            '  type "%SRST_TEST_ENVS%"\n'
            '  exit /b 0\n'
            ')\n'
            'if "%~1"=="env" if "%SRST_TEST_FAIL_ENV%"=="1" exit /b 42\n'
            'if "%~1"=="create" if "%SRST_TEST_FAIL_ENV%"=="1" exit /b 42\n'
            'if "%~1"=="install" if "%SRST_TEST_FAIL_ENV%"=="1" exit /b 42\n'
            'if "%~1"=="run" if "%SRST_TEST_FAIL_RUN%"=="1" exit /b 43\n'
            'exit /b 0\n',
            encoding="ascii",
        )
        self.env_list = Path(self.tmp.name) / "envs.json"
        self.env_list.write_text(json.dumps({"envs": [str(self.environment)]}))
        self.env = os.environ.copy()
        self.env.update({
            "CONDA_PREFIX": str(self.conda_root),
            "CONDA_EXE": "",
            "SRST_NO_PAUSE": "1",
            "SRST_TEST_CALLS": str(self.calls),
            "SRST_TEST_ENVS": str(self.env_list),
            "SRST_TEST_FAIL_ENV": "0",
            "SRST_TEST_FAIL_RUN": "0",
        })

    def run_launcher(self, name, *args):
        return subprocess.run(
            ["cmd.exe", "/d", "/c", name, *args], cwd=self.project,
            env=self.env, input="\n", text=True, capture_output=True, timeout=60,
        )

    def test_install_failure_keeps_log_and_never_registers_kernel(self):
        self.env["SRST_TEST_FAIL_ENV"] = "1"
        result = self.run_launcher("install_windows.bat")
        self.assertNotEqual(result.returncode, 0)
        log = self.project / "setup_and_run_demo.log"
        self.assertTrue(log.exists(), result.stdout + result.stderr)
        self.assertIn("fixture download failed", log.read_text(encoding="utf-8-sig"))
        self.assertNotIn("ipykernel install", self.calls.read_text())

    def test_one_click_stops_before_notebook_when_installation_fails(self):
        self.env['SRST_TEST_FAIL_ENV'] = '1'
        result = self.run_launcher('setup_and_run_demo.bat')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('-m notebook', self.calls.read_text())

    def test_one_click_installs_and_then_opens_the_notebook(self):
        result = self.run_launcher('setup_and_run_demo.bat')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertLess(calls.index('demo.py'), calls.index('-m notebook'))

    def test_install_checks_localization_before_reporting_success(self):
        result = self.run_launcher("install_windows.bat")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertIn("ipykernel install", calls)
        self.assertIn("--override-channels", calls)
        self.assertIn("demo.py --device auto --max-frames 9 --batch-size 1", calls)
        self.assertIn("run_notebook_windows.bat", result.stdout)

    def test_fresh_install_creates_environment_without_default_packages(self):
        (self.environment / "python.exe").unlink()
        result = self.run_launcher("install_windows.bat")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertTrue(calls.startswith("create "), calls)
        self.assertIn("--no-default-packages", calls)
        self.assertIn("--override-channels", calls)

    def test_install_gives_large_downloads_more_time_and_resume_attempts(self):
        result = self.run_launcher("install_windows.bat")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        pip_call = next(
            line for line in self.calls.read_text().splitlines()
            if "python -m pip install " in line
        )
        self.assertIn("--timeout 120", pip_call)
        self.assertIn("--retries 10", pip_call)
        self.assertIn("--resume-retries 20", pip_call)
        # The Conda package must support the resume flag on a fresh PC too.
        self.assertIn(
            "pip=25.2", (self.project / "requirements-windows-conda.txt").read_text()
        )

    def test_cli_demo_forwards_device_and_bounded_input_arguments(self):
        result = self.run_launcher(
            "run_demo_windows.bat", "--device", "cpu", "--max-frames", "9",
            "--batch-size", "1",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "demo.py --device cpu --max-frames 9 --batch-size 1",
            self.calls.read_text(),
        )

    def test_micromamba_uses_its_own_run_and_create_options(self):
        executable = self.conda_root / 'condabin' / 'micromamba.bat'
        shutil.copy2(self.conda_root / 'condabin' / 'conda.bat', executable)
        self.env['CONDA_EXE'] = str(executable)
        (self.environment / 'python.exe').unlink()
        result = self.run_launcher('install_windows.bat')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertIn('--root-prefix', calls)
        self.assertIn('--no-rc', calls)
        self.assertNotIn('--no-default-packages', calls)
        self.assertNotIn('--no-capture-output', calls)

    def test_failed_environment_check_prevents_notebook_launch(self):
        self.env["SRST_TEST_FAIL_RUN"] = "1"
        result = self.run_launcher("run_notebook_windows.bat")
        self.assertNotEqual(result.returncode, 0)
        calls = self.calls.read_text() if self.calls.exists() else ""
        self.assertNotIn("-m notebook", calls)

    def test_notebook_uses_srst_environment_from_folder_with_spaces(self):
        result = self.run_launcher("run_notebook_windows.bat")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertIn(str(self.environment), calls)
        self.assertIn("python -m notebook", calls)
        self.assertIn("fitting.ipynb", calls)


if __name__ == "__main__":
    unittest.main()
