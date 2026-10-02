"""Run every public standalone example in a fresh directory; no network or credentials."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    examples = sorted((root / "examples").glob("[0-9][0-9]_*.py"))
    results = []
    with tempfile.TemporaryDirectory(prefix="datapanel-examples-") as directory:
        for script in examples:
            run = subprocess.run(
                [sys.executable, str(script), "--work-dir", directory],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=60,
            )
            try:
                record = json.loads(run.stdout)
                passed = (
                    run.returncode == 0
                    and record["status"] == "passed"
                    and record["mode"] == "mock"
                )
            except (ValueError, KeyError):
                passed = False
            results.append(passed)
            print(f"{'PASS' if passed else 'FAIL'} {script.name}")
            if not passed:
                print(run.stderr[-1500:], file=sys.stderr)
        # Verify the data-access entry remains read-only across processes.
        repeat = subprocess.run(
            [sys.executable, str(root / "examples/04_data_access.py"), "--work-dir", directory],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        results.append(repeat.returncode == 0)
        print(f"{'PASS' if results[-1] else 'FAIL'} repeat read-only data-access policy")
        training = subprocess.run(
            [
                sys.executable,
                str(root / "examples/training/cpu_model.py"),
                "--work-dir",
                str(Path(directory) / "training"),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        try:
            record = json.loads(training.stdout)
            passed = (
                training.returncode == 0
                and record["status"] == "verified"
                and record["runtime"]["device"] == "cpu"
                and not record["remote_compute"]
            )
        except (ValueError, KeyError):
            passed = False
        results.append(passed)
        print(f"{'PASS' if passed else 'FAIL'} CPU synthetic training and model reload")
        custom_work = Path(directory) / "custom-training"
        custom = subprocess.run(
            [
                sys.executable,
                str(root / "examples/training/cpu_model.py"),
                "--work-dir",
                str(custom_work),
                "--features",
                str(root / "examples/training/custom_features.py"),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        try:
            result = json.loads((custom_work / "outputs/result.json").read_text())
            passed = (
                custom.returncode == 0
                and len(result["model"]["weights"]) == 4
                and abs(result["model"]["weights"][-1]) > 1e-6
            )
        except (ValueError, KeyError, OSError):
            passed = False
        results.append(passed)
        print(f"{'PASS' if passed else 'FAIL'} custom second-level feature enters training")
        gpu = subprocess.run(
            [sys.executable, str(root / "examples/training/gpu_model.py")],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        try:
            passed = gpu.returncode == 2 and json.loads(gpu.stdout)["status"] == "blocked"
        except (ValueError, KeyError):
            passed = False
        results.append(passed)
        print(f"{'PASS' if passed else 'FAIL'} GPU unavailable guard (no GPU execution)")
        multi = subprocess.run(
            [sys.executable, str(root / "examples/training/multi_gpu_model.py")],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        try:
            passed = multi.returncode == 2 and json.loads(multi.stdout)["status"] == "blocked"
        except (ValueError, KeyError):
            passed = False
        results.append(passed)
        print(f"{'PASS' if passed else 'FAIL'} multi-GPU unavailable guard (no DDP execution)")
        gpu_input = Path(directory) / "gpu-input"
        for arguments, label in [
            (["--output", str(gpu_input)], "fixed GPU input generation"),
            (["--validate", str(gpu_input / "input.json")], "fixed GPU input validation"),
        ]:
            run = subprocess.run(
                [
                    sys.executable,
                    str(root / "examples/training/prepare_gpu_template.py"),
                    *arguments,
                ],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=60,
            )
            results.append(run.returncode == 0)
            print(f"{'PASS' if results[-1] else 'FAIL'} {label}")
    print(f"{sum(results)}/{len(results)} checks passed; offline fixtures, no remote compute")
    return 0 if len(examples) == 12 and all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
