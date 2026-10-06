"""Exercise the Windows entry points without downloading/installing packages.

Only the external environment-manager CLI is replaced. The real single entry
and PowerShell scripts still decide when to install, handle failures and launch.
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
        for path in ROOT.glob("*.bat"):
            shutil.copy2(path, self.project / path.name)
        shutil.copytree(ROOT / "requirements", self.project / "requirements")
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
        self.environment = self.conda_root / "envs" / "srst_demo"
        self.environment.mkdir(parents=True)
        (self.environment / "python.exe").write_text("fixture")
        bin_dir = self.conda_root / "condabin"
        bin_dir.mkdir(parents=True)
        self.calls = Path(self.tmp.name) / "calls.txt"
        (bin_dir / "conda.bat").write_text(
            '@echo off\n'
            '>>"%SRST_TEST_CALLS%" echo %*\n'
            'if "%~1"=="info" (\n'
            '  type "%SRST_TEST_INFO%"\n'
            '  exit /b 0\n'
            ')\n'
            'if "%SRST_TEST_FAIL_ENV%"=="1" echo fixture download failed 1>&2\n'
            'if "%~1"=="create" if "%SRST_TEST_FAIL_ENV%"=="1" exit /b 42\n'
            'if "%~1"=="install" if "%SRST_TEST_FAIL_ENV%"=="1" exit /b 42\n'
            'if "%~1"=="create" (\n'
            '  if not exist "%SRST_TEST_ENV%" mkdir "%SRST_TEST_ENV%"\n'
            '  type nul > "%SRST_TEST_PYTHON%"\n'
            ')\n'
            'if "%~1"=="run" if "%SRST_TEST_FAIL_RUN%"=="1" exit /b 43\n'
            ':scan\n'
            'if "%~1"=="" exit /b 0\n'
            'if "%SRST_TEST_FAIL_KERNEL%"=="1" if "%~nx1"=="check_notebook_kernel.py" exit /b 44\n'
            'if "%SRST_TEST_FAIL_MODEL%"=="1" if "%~nx1"=="demo.py" exit /b 45\n'
            'shift\n'
            'goto scan\n',
            encoding="ascii",
        )
        self.info = Path(self.tmp.name) / 'conda-info.json'
        self.info.write_text(json.dumps({
            'root_prefix': str(self.conda_root),
            'envs_dirs': [str(self.conda_root / 'envs')],
            'envs': [str(self.environment)],
        }), encoding='utf-8')
        self.state_file = self.project / '.runtime' / 'environment.json'
        self.state_file.parent.mkdir()
        self.state_file.write_text(json.dumps({
            'schema': 1, 'application': 'SRST', 'name': 'srst_demo',
            'manager': str(bin_dir / 'conda.bat'),
            'environment': str(self.environment),
        }), encoding='utf-8')
        self.env = os.environ.copy()
        self.env.update({
            "CONDA_PREFIX": str(self.conda_root),
            "CONDA_EXE": "",
            "SRST_NO_PAUSE": "1",
            "SRST_TEST_CALLS": str(self.calls),
            "SRST_TEST_INFO": str(self.info),
            "SRST_TEST_ENV": str(self.environment),
            "SRST_TEST_PYTHON": str(self.environment / "python.exe"),
            "SRST_TEST_FAIL_ENV": "0",
            "SRST_TEST_FAIL_RUN": "0",
            "SRST_TEST_FAIL_KERNEL": "0",
            "SRST_TEST_FAIL_MODEL": "0",
            "USERPROFILE": str(Path(self.tmp.name) / 'user profile'),
            "CONDA_ENVS_PATH": "",
        })

    def run_launcher(self, name, *args):
        return subprocess.run(
            ["cmd.exe", "/d", "/c", name, *args], cwd=self.project,
            env=self.env, input="\n", text=True, capture_output=True, timeout=60,
        )

    def run_script(self, name, *args):
        return subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(self.project / "scripts" / name), *args],
            cwd=self.project, env=self.env, input="\n", text=True,
            capture_output=True, timeout=60,
        )

    @property
    def ready_file(self):
        return self.environment / ".srst-ready.json"

    def prepare_verified_environment(self):
        result = self.run_script("install_windows.ps1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.ready_file.exists())
        self.calls.unlink()

    def test_install_failure_keeps_log_and_never_registers_kernel(self):
        self.env["SRST_TEST_FAIL_ENV"] = "1"
        result = self.run_script("install_windows.ps1")
        self.assertNotEqual(result.returncode, 0)
        log = self.project / "srst.log"
        self.assertTrue(log.exists(), result.stdout + result.stderr)
        self.assertIn("fixture download failed", log.read_text(encoding="utf-8-sig"))
        self.assertNotIn("ipykernel install", self.calls.read_text())

    def test_one_click_stops_before_notebook_when_installation_fails(self):
        self.env['SRST_TEST_FAIL_ENV'] = '1'
        result = self.run_launcher('start_srst.bat')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('-m notebook', self.calls.read_text())

    def test_one_click_installs_and_then_opens_the_notebook(self):
        result = self.run_launcher('start_srst.bat')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertLess(calls.index('demo.py'), calls.index('-m notebook'))

    def test_install_checks_localization_before_reporting_success(self):
        result = self.run_script("install_windows.ps1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertIn("ipykernel install", calls)
        self.assertIn("--override-channels", calls)
        self.assertIn("demo.py --device auto --max-frames 9 --batch-size 1", calls)
        self.assertIn("start_srst.bat", result.stdout)
        self.assertTrue(self.ready_file.exists())

    def test_fresh_install_creates_environment_without_default_packages(self):
        (self.environment / "python.exe").unlink()
        result = self.run_script("install_windows.ps1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertTrue(any(line.startswith('create ') for line in calls.splitlines()), calls)
        self.assertIn("--no-default-packages", calls)
        self.assertIn("--override-channels", calls)

    def test_installer_uses_manifests_from_requirements_directory(self):
        result = self.run_script("install_windows.ps1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertIn(str(self.project / "requirements" / "windows-conda.txt"), calls)
        self.assertIn(str(self.project / "requirements" / "windows-demo.txt"), calls)

    def test_install_gives_large_downloads_more_time_and_resume_attempts(self):
        result = self.run_script("install_windows.ps1")
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
            "pip=25.2", (self.project / "requirements" / "windows-conda.txt").read_text()
        )

    def test_cli_demo_forwards_device_and_bounded_input_arguments(self):
        result = self.run_script(
            "run_demo_windows.ps1", "--device", "cpu", "--max-frames", "9",
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
        self.state_file.unlink()
        self.environment = Path(self.env['USERPROFILE']) / '.conda' / 'envs' / 'srst_demo'
        self.env['SRST_TEST_ENV'] = str(self.environment)
        self.env['SRST_TEST_PYTHON'] = str(self.environment / 'python.exe')
        result = self.run_script('install_windows.ps1')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertIn('--root-prefix', calls)
        self.assertIn('--no-rc', calls)
        self.assertNotIn('--no-default-packages', calls)
        self.assertNotIn('--no-capture-output', calls)
        self.assertIn('--name srst_demo', calls)
        self.assertTrue((self.environment / 'python.exe').exists())
        self.assertTrue(self.ready_file.exists())

    def test_failed_environment_check_prevents_notebook_launch(self):
        self.env["SRST_TEST_FAIL_RUN"] = "1"
        result = self.run_script("run_notebook_windows.ps1")
        self.assertNotEqual(result.returncode, 0)
        calls = self.calls.read_text() if self.calls.exists() else ""
        self.assertNotIn("-m notebook", calls)

    def test_notebook_uses_srst_environment_from_folder_with_spaces(self):
        result = self.run_script("run_notebook_windows.ps1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertIn("--name srst_demo", calls)
        self.assertIn("python -m notebook", calls)
        self.assertIn("fitting.ipynb", calls)

    def test_single_entry_reuses_a_verified_environment_on_second_launch(self):
        first = self.run_launcher("start_srst.bat")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.calls.unlink()
        second = self.run_launcher("start_srst.bat")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        calls = self.calls.read_text()
        self.assertIn("-m notebook", calls)
        self.assertNotIn("pip install", calls)
        self.assertNotIn("demo.py", calls)

    def test_only_one_batch_entry_is_distributed(self):
        self.assertEqual([path.name for path in ROOT.glob("*.bat")], ["start_srst.bat"])

    def test_existing_python_without_success_record_runs_setup(self):
        self.assertTrue((self.environment / "python.exe").exists())
        result = self.run_launcher("start_srst.bat")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(any(line.startswith('install ') for line in self.calls.read_text().splitlines()))
        self.assertTrue(self.ready_file.exists())

    def test_failed_setup_never_marks_environment_ready(self):
        self.env["SRST_TEST_FAIL_ENV"] = "1"
        result = self.run_launcher("start_srst.bat")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.ready_file.exists())
        self.assertNotIn("-m notebook", self.calls.read_text())

    def test_kernel_failure_does_not_mark_ready_or_open_notebook(self):
        self.env["SRST_TEST_FAIL_KERNEL"] = "1"
        result = self.run_launcher("start_srst.bat")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.ready_file.exists())
        self.assertNotIn("-m notebook", self.calls.read_text())

    def test_model_failure_does_not_mark_ready_or_open_notebook(self):
        self.env["SRST_TEST_FAIL_MODEL"] = "1"
        result = self.run_launcher("start_srst.bat")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.ready_file.exists())
        self.assertNotIn("-m notebook", self.calls.read_text())

    def test_skipped_model_check_does_not_mark_ready(self):
        result = self.run_script("install_windows.ps1", "-SkipSmokeTest")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.ready_file.exists())

    def test_changed_dependencies_trigger_setup_again(self):
        self.prepare_verified_environment()
        manifest = self.project / "requirements" / "windows-demo.txt"
        with manifest.open("a") as output:
            output.write("\n# new dependency configuration\n")
        result = self.run_launcher("start_srst.bat")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("pip install", self.calls.read_text())

    def test_malformed_ready_record_triggers_setup_again(self):
        self.ready_file.write_text("incomplete JSON", encoding="utf-8")
        result = self.run_launcher("start_srst.bat")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("pip install", self.calls.read_text())

    def test_ready_record_from_another_folder_triggers_setup(self):
        self.prepare_verified_environment()
        ready = json.loads(self.ready_file.read_text(encoding="utf-8-sig"))
        ready["environment"] = str(self.project / "old folder")
        self.ready_file.write_text(json.dumps(ready), encoding="utf-8")
        result = self.run_launcher("start_srst.bat")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("pip install", self.calls.read_text())

    def test_repair_rechecks_environment_and_discards_old_success_on_failure(self):
        self.prepare_verified_environment()
        self.env["SRST_TEST_FAIL_ENV"] = "1"
        result = self.run_launcher("start_srst.bat", "-Repair")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.ready_file.exists())
        self.assertNotIn("-m notebook", self.calls.read_text())

    def test_missing_demo_asset_stops_before_installation(self):
        (self.project / "network" / "experiment1" / "model_2.pt").unlink()
        result = self.run_launcher("start_srst.bat")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.calls.exists())
        self.assertFalse(self.ready_file.exists())
        self.assertIn("Extract the complete SRST folder", result.stdout)

    def test_fresh_install_creates_and_uses_a_named_conda_environment(self):
        shutil.rmtree(self.environment)
        self.state_file.unlink()
        result = self.run_script('install_windows.ps1')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        create = next(line for line in calls.splitlines() if line.startswith('create '))
        self.assertIn('--name srst_demo', create)
        self.assertNotIn('--prefix', create)
        self.assertIn('run --no-capture-output --name srst_demo python', calls)
        self.assertTrue(self.ready_file.exists())
        state = json.loads(self.state_file.read_text(encoding='utf-8-sig'))
        self.assertEqual(state['environment'], str(self.environment))

    def test_unrelated_named_environment_is_left_untouched(self):
        self.state_file.unlink()
        original = (self.environment / 'python.exe').read_bytes()
        result = self.run_launcher('start_srst.bat')
        self.assertNotEqual(result.returncode, 0)
        calls = self.calls.read_text()
        self.assertNotIn('pip install', calls)
        self.assertFalse(any(line.startswith(('create ', 'install ')) for line in calls.splitlines()))
        self.assertEqual((self.environment / 'python.exe').read_bytes(), original)
        self.assertFalse(self.state_file.exists())

    def test_old_project_environment_is_cloned_to_the_named_environment(self):
        shutil.rmtree(self.environment)
        self.state_file.unlink()
        legacy = self.project / '.runtime' / 'srst_demo'
        legacy.mkdir()
        (legacy / 'python.exe').write_text('old environment')
        (legacy / '.srst-ready.json').write_text(json.dumps({
            'schema': 1, 'environment': str(legacy), 'signature': 'old setup',
        }), encoding='utf-8')
        result = self.run_script('install_windows.ps1')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls.read_text()
        self.assertIn('--clone "' + str(legacy) + '"', calls)
        self.assertIn('--name srst_demo', calls)
        self.assertIn('--offline', calls)
        self.assertTrue(self.ready_file.exists())
        self.assertTrue((legacy / 'python.exe').exists())


if __name__ == "__main__":
    unittest.main()
