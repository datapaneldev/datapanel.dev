"""Explicit, resumable model demo orchestration using only public DataPanel APIs."""

import argparse
import ast
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import uuid
from decimal import Decimal
from pathlib import Path

from . import training_program, user_features
from .client import (
    APIError,
    DataPanel,
    ExecutionClosed,
    file_sha256,
    require_execution,
    save_json,
    selection_body,
)

TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT", "EXPIRED"}


def feature_contract(source=None):
    """Read literal declarations without importing/executing user code on the client."""
    source = (
        source if source is not None else Path(user_features.__file__).read_text(encoding="utf-8")
    )
    if len(source.encode()) > 65536:
        raise ValueError("Feature source must be <=64 KiB")
    tree = ast.parse(source)
    declarations = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {
                    "FEATURE_NAMES",
                    "FEATURE_INPUT_FIELDS",
                }:
                    if target.id in declarations:
                        raise ValueError("Duplicate feature contract declaration")
                    declarations[target.id] = ast.literal_eval(node.value)
    for name in ("FEATURE_NAMES", "FEATURE_INPUT_FIELDS"):
        values = declarations.get(name)
        if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= 80:
            raise ValueError("Declare literal FEATURE_NAMES and FEATURE_INPUT_FIELDS")
        if not all(
            isinstance(v, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", v) for v in values
        ):
            raise ValueError("Invalid feature name/field")
        if len(set(values)) != len(values):
            raise ValueError("Duplicate feature names/fields")
    if len(declarations["FEATURE_NAMES"]) > 32:
        raise ValueError("This bounded demo supports at most 32 features")
    allowed = {"lcTsNs"} | {
        f"{side}{kind}{level}" for side in "BA" for kind in "pq" for level in range(1, 21)
    }
    if not set(declarations["FEATURE_INPUT_FIELDS"]) <= allowed:
        raise ValueError(
            "Feature field is not in the supported MBP-20 contract; exSeq semantics unconfirmed"
        )
    if not any(isinstance(n, ast.FunctionDef) and n.name == "build_features" for n in tree.body):
        raise ValueError("Define build_features(previous, current)")
    return source, list(declarations["FEATURE_NAMES"]), list(declarations["FEATURE_INPUT_FIELDS"])


def configuration(selection, backend="cpu", *, data_mode="market", feature_source=None):
    selected = selection_body(selection)
    feature_source, names, fields = feature_contract(feature_source)
    if backend not in {"cpu", "gpu", "multi-gpu"}:
        raise ValueError("Unknown training backend")
    return {
        "backend": backend,
        "data_mode": data_mode,
        "start": selected["start"],
        "end": selected["end"],
        "max_rows": 5000,
        "max_scan_rows": 500000,
        "steps": 200,
        "learning_rate": 0.03,
        "ridge": 0.001,
        "gpu_count": {"cpu": 0, "gpu": 1, "multi-gpu": 2}[backend],
        "feature_names": names,
        "feature_input_fields": fields,
        "feature_source_sha256": hashlib.sha256(feature_source.encode()).hexdigest(),
    }


def render_source(config, feature_source=None):
    template = Path(training_program.__file__).read_text(encoding="utf-8")
    marker = "CONFIG = {}  # Replaced with a frozen JSON configuration by the cookbook."
    if template.count(marker) != 1:
        raise ValueError("Payload template marker missing")
    feature_source, names, fields = feature_contract(feature_source)
    if (
        config["feature_names"] != names
        or config["feature_input_fields"] != fields
        or config["feature_source_sha256"] != hashlib.sha256(feature_source.encode()).hexdigest()
    ):
        raise ValueError("Feature source does not match the frozen configuration")
    feature_import = (
        "from .user_features import FEATURE_INPUT_FIELDS, FEATURE_NAMES, build_features"
    )
    if template.count(feature_import) != 1:
        raise ValueError("Feature inline marker missing")
    rendered = template.replace(feature_import, feature_source).replace(
        marker, "CONFIG = json.loads(" + repr(json.dumps(config)) + ")"
    )
    compile(rendered, "train_model.py", "exec")
    return rendered


def require_profile(profiles, profile, backend):
    entries = profiles.get("profiles", {})
    if not isinstance(entries, dict) or profile not in entries:
        raise ExecutionClosed("Requested resource profile is not published")
    item = entries[profile]
    gpus = item.get("gpu_count", item.get("gpus", 0))
    expected = {"cpu": 0, "gpu": 1, "multi-gpu": 2}[backend]
    if type(gpus) is not int or gpus != expected:
        raise ExecutionClosed("Profile does not match the exact requested GPU count")
    return item


def verify_model(path):
    """Load JSON as data, recompute predictions without executing downloaded code."""
    if Path(path).stat().st_size > 2 * 1024 * 1024:
        raise ValueError("Result exceeds the documented JSON output cap")
    result = json.loads(Path(path).read_text(encoding="utf-8"))
    if result.get("format") != "datapanel-linear-demo-v1":
        raise ValueError("Unknown model format")
    model = result["model"]
    if model["feature_order"] != result["config"]["feature_names"]:
        raise ValueError("Model feature order mismatch")
    if len(model["weights"]) != len(model["feature_order"]) or not result.get("reload_probes"):
        raise ValueError("Incomplete model or missing reload probes")
    json.dumps(result, allow_nan=False)
    if result.get("config", {}).get("backend") == "multi-gpu":
        training_program.verify_ddp_evidence(
            result["runtime"], result["metrics"]["train"]["count"], result["config"]["steps"]
        )
        digest = hashlib.sha256(json.dumps(model["weights"] + [model["bias"]]).encode()).hexdigest()
        if any(r["parameter_sha256"] != digest for r in result["runtime"]["ranks"]):
            raise ValueError("Exported weights do not match distributed rank evidence")
    errors = []
    for probe in result["reload_probes"]:
        actual = training_program.predict(model, probe["x"])
        if not math.isfinite(actual) or not math.isclose(
            actual, probe["prediction_bps"], rel_tol=1e-9, abs_tol=1e-9
        ):
            raise ValueError("Reloaded model prediction mismatch")
        errors.append(abs(actual - probe["prediction_bps"]))
    return {
        "status": "verified",
        "sha256": file_sha256(path),
        "probe_count": len(errors),
        "max_absolute_error_bps": max(errors),
        "runtime": result["runtime"],
        "metrics": result["metrics"],
        "qualification": result["qualification"],
    }


def fixture(work, feature_source=None):
    """A small deterministic engineering fixture; never used as remote market data."""
    work = Path(work)
    inputs, outputs = work / "inputs", work / "outputs"
    inputs.mkdir(parents=True, exist_ok=True)
    outputs.mkdir(parents=True, exist_ok=True)
    selection = {
        "market": "synthetic",
        "data_type": "MBP-20",
        "symbol": "DEMO",
        "start": "2026-01-01T00:00:00Z",
        "end": "2026-01-01T00:10:00Z",
    }
    config = configuration(selection, data_mode="synthetic", feature_source=feature_source)
    stamp, mid = training_program.epoch_ns(selection["start"]), 100.0
    with (inputs / "fixture.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["lcTsNs", "exSeq"] + [
            f"{side}{kind}{level}" for side in "BA" for level in range(1, 21) for kind in "pq"
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for i in range(600):
            mid *= 1 + (0.8 * math.sin(i / 11) + 0.1 * math.cos(i / 3)) / 10000
            record = {"lcTsNs": stamp + i * 10**9, "exSeq": i}
            for level in range(1, 21):
                record.update(
                    {
                        f"Bp{level}": mid - 0.005 * level,
                        f"Ap{level}": mid + 0.005 * level,
                        f"Bq{level}": 12 + math.sin(i / 11 + level - 1),
                        f"Aq{level}": 12 - math.sin(i / 11 + level - 1),
                    }
                )
            writer.writerow(record)
    source = work / "source.py"
    source.write_text(render_source(config, feature_source), encoding="utf-8")
    # Our own generated payload, not a downloaded source artifact.
    subprocess.run(
        [sys.executable, "-I", "-B", str(source.resolve())],
        check=True,
        env={
            **os.environ,
            "DP_INPUT_DIR": str(inputs.resolve()),
            "DP_OUTPUT_DIR": str(outputs.resolve()),
        },
        timeout=30,
        capture_output=True,
    )
    verification = verify_model(outputs / "result.json")
    save_json(work / "verification.json", verification)
    return {"mode": "fixture", "status": "passed", "remote_compute": False, **verification}


def live_training(
    client,
    selection,
    work,
    *,
    backend="cpu",
    profile="cpu-small",
    max_credits="1",
    wall_seconds=120,
    submit=False,
    max_polls=12,
    interval=5,
    feature_source=None,
):
    budget = Decimal(max_credits)
    if not budget.is_finite() or budget <= 0:
        raise ValueError("Credit cap must be finite and positive")
    if type(wall_seconds) is not int or not 1 <= wall_seconds <= 43200:
        raise ValueError("Wall seconds must be an integer in 1..43200")
    if type(max_polls) is not int or not 1 <= max_polls <= 120:
        raise ValueError("Polling count must be in 1..120")
    selected = selection_body(selection)
    config = configuration(selected, backend, feature_source=feature_source)
    source = render_source(config, feature_source)
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    path = work / "run.json"
    account = client.me()
    identity = account.get("email") or account.get("user_id")
    if not identity:
        raise ValueError("Cannot bind the run to a known account")
    spec = {
        "origin": client.base,
        "account_fingerprint": hashlib.sha256(identity.encode()).hexdigest(),
        "selection": selected,
        "config": config,
        "profile": profile,
        "wall_seconds": wall_seconds,
        "max_credits": str(budget),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
    }
    state = json.loads(path.read_text()) if path.exists() else {"spec": spec}
    if state["spec"] != spec:
        raise ValueError("Run directory belongs to different source/config/account; do not reuse")
    profiles = client.profiles()
    resource = require_profile(profiles, profile, backend)
    if wall_seconds > resource["max_wall_seconds"]:
        raise ValueError("Wall limit exceeds the published profile")
    if submit and "job_id" not in state:
        require_execution(profiles, profile, "train")
    if "source" not in state:
        state["source"] = client.upload_source("train_model.py", source)
        save_json(path, state)
    if state["source"]["sha256"] != spec["source_sha256"]:
        raise ValueError("Uploaded training source hash mismatch")
    if "snapshot" not in state:
        state["snapshot"] = client.snapshot(selected)
        save_json(path, state)
    if "quote" not in state:
        state["quote"] = client.quote(
            {
                "workspace_id": "default",
                "kind": "train",
                "profile": profile,
                "source_artifact_id": state["source"]["id"],
                "dataset_snapshot_id": state["snapshot"]["id"],
                "max_wall_seconds": wall_seconds,
                "max_credits": str(budget),
            }
        )
        save_json(path, state)
    charged = Decimal(state["quote"]["maximum_charged_credits"])
    if not charged.is_finite() or charged < 0 or charged > budget:
        raise ValueError("Server quote exceeds the explicit credit cap")
    if not submit and "job_id" not in state:
        return {"status": "quoted", "submitted": False, "maximum_credits": str(charged)}
    if "job_id" not in state:
        if "idempotency_key" not in state:
            state["idempotency_key"] = str(uuid.uuid4())
            state["job_request"] = {
                "workspace_id": "default",
                "kind": "train",
                "quote_id": state["quote"]["quote_id"],
                "source_artifact_id": state["source"]["id"],
                "dataset_snapshot_id": state["snapshot"]["id"],
                "resource_profile": profile,
                "wall_seconds": wall_seconds,
            }
            save_json(path, state)  # Persist before any potentially ambiguous POST.
        reply = client.submit_job(state["job_request"], state["idempotency_key"])
        state["job_id"] = reply["job_id"]
        save_json(path, state)
    for poll in range(max_polls):
        status = client.job_status(state["job_id"])
        state["last_status"] = status
        save_json(path, state)
        if status["status"] in TERMINAL:
            break
        if poll + 1 < max_polls:
            recommended = status.get("next_poll_seconds", interval)
            delay = (
                recommended
                if type(recommended) in (int, float)
                and math.isfinite(recommended)
                and 0 <= recommended <= 300
                else interval
            )
            client.sleep(max(interval, delay))
    if status["status"] != "SUCCEEDED":
        return {
            "job_id": state["job_id"],
            "status": status["status"],
            "resume": "Repeat the same command and run directory; no resubmission",
            "terminal": status["status"] in TERMINAL,
        }
    artifact_id = status.get("result_artifact_id")
    if not artifact_id or artifact_id not in status.get("output_artifact_ids", []):
        raise ValueError("Successful job lacks explicit result ownership mapping; do not guess")
    target = work / "result.json"
    client.export_private(artifact_id, target, max_polls=max_polls, interval=interval)
    verification = verify_model(target)
    result = json.loads(target.read_text())
    if result["config"] != config:
        raise ValueError("Downloaded model belongs to a different training configuration")
    if (backend != "cpu") != result["runtime"]["device"].startswith("cuda"):
        raise ValueError("Result device does not match requested backend")
    if backend == "multi-gpu":
        training_program.verify_ddp_evidence(result["runtime"], result["metrics"]["train"]["count"])
    state["verification"] = verification
    save_json(path, state)
    return {
        "job_id": state["job_id"],
        "status": "verified",
        "result": str(target),
        "billing_state": status.get("billing_state"),
        **verification,
    }


def main(default_backend="cpu"):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("fixture", "live"), default="fixture")
    parser.add_argument("--backend", choices=("cpu", "gpu", "multi-gpu"), default=default_backend)
    parser.add_argument("--profile")
    parser.add_argument("--selection", type=Path)
    parser.add_argument(
        "--features", type=Path, help="User feature Python file, inlined into guest source"
    )
    parser.add_argument("--work-dir", type=Path, default=Path("work/training"))
    parser.add_argument("--allow-writes", action="store_true")
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--max-credits", default="1")
    parser.add_argument("--wall-seconds", type=int, default=120)
    parser.add_argument("--max-polls", type=int, default=12)
    args = parser.parse_args()
    feature_source = args.features.read_text(encoding="utf-8") if args.features else None
    try:
        if args.mode == "fixture":
            if args.backend != "cpu":
                raise ExecutionClosed(
                    "GPU fixture is not GPU validation; use a published CUDA profile"
                )
            result = fixture(args.work_dir, feature_source)
        else:
            if not args.selection or not args.allow_writes:
                parser.error("Live planning needs --selection and --allow-writes")
            if args.backend != "cpu" and not args.profile:
                parser.error("GPU mode needs the exact published --profile; no default or fallback")
            key = os.environ.get("DATAPANEL_API_KEY")
            if not key:
                parser.error("Set DATAPANEL_API_KEY in the parent process")
            with DataPanel(
                key, os.getenv("DATAPANEL_BASE_URL", "https://datapanel.dev"), allow_writes=True
            ) as client:
                result = live_training(
                    client,
                    json.loads(args.selection.read_text()),
                    args.work_dir,
                    backend=args.backend,
                    profile=args.profile or "cpu-small",
                    max_credits=args.max_credits,
                    wall_seconds=args.wall_seconds,
                    submit=args.submit,
                    max_polls=args.max_polls,
                    feature_source=feature_source,
                )
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 1 if result.get("terminal") else 0
    except ExecutionClosed as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc), "submitted": False}))
        return 2
    except TimeoutError:
        print(
            json.dumps(
                {
                    "status": "pending",
                    "resume": "Repeat the same command and work directory; keep existing task state",
                }
            )
        )
        return 2
    except APIError as exc:
        print(json.dumps({"status": "api_error", "reason": str(exc), "http_status": exc.status}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
