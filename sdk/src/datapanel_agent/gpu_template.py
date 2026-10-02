"""Prepare and validate fixed GPU template input; optionally request a live quote."""

import argparse
import hashlib
import json
import math
import os
from decimal import Decimal
from pathlib import Path

from .client import APIError, DataPanel, save_json

LIMIT = 2 * 1024**2
TEMPLATE = "mlp-regression-v1"
KEYS = {
    "template",
    "features",
    "labels",
    "hidden",
    "epochs",
    "batch_size",
    "learning_rate",
    "seed",
    "wall_seconds",
}


def _bounded(value, low, high, integer=False):
    types = (int,) if integer else (int, float)
    if type(value) not in types or not low <= value <= high or not math.isfinite(value):
        raise ValueError("Expected a finite bounded numeric value")


def validate(request):
    """Validate the closed proposed schema; encode/decode enforce byte size."""
    if type(request) is not dict or set(request) != KEYS:
        raise ValueError("Unexpected or missing template fields")
    if request["template"] != TEMPLATE:
        raise ValueError("Unsupported template")
    x, y, hidden = (request[k] for k in ("features", "labels", "hidden"))
    if type(x) is not list or not 32 <= len(x) <= 16384:
        raise ValueError("Expected 32..16384 samples")
    if type(y) is not list or len(y) != len(x):
        raise ValueError("Labels must match samples")
    width = len(x[0]) if type(x[0]) is list else 0
    _bounded(width, 1, 128, True)
    for row in x:
        if type(row) is not list or len(row) != width:
            raise ValueError("Features must be a rectangular matrix")
        for value in row:
            _bounded(value, -1e6, 1e6)
    for value in y:
        _bounded(value, -1e6, 1e6)
    if type(hidden) is not list or not 1 <= len(hidden) <= 4:
        raise ValueError("Expected 1..4 hidden layers")
    for size in hidden:
        _bounded(size, 1, 256, True)
    dimensions = [width, *hidden, 1]
    if sum((a + 1) * b for a, b in zip(dimensions, dimensions[1:], strict=False)) > 32768:
        raise ValueError("Model exceeds 32768 parameters")
    for name, low, high in (
        ("epochs", 1, 200),
        ("batch_size", 8, 1024),
        ("seed", 0, 2**31 - 1),
        ("wall_seconds", 1, 120),
    ):
        _bounded(request[name], low, high, True)
    _bounded(request["learning_rate"], 1e-6, 0.1)
    return request


def encode(request):
    raw = json.dumps(
        validate(request), sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    if len(raw) > LIMIT:
        raise ValueError("Input exceeds 2 MiB; reduce the explicit selection")
    return raw


def decode(raw):
    if not 0 < len(raw) <= LIMIT:
        raise ValueError("Input must be between 1 byte and 2 MiB")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    return validate(json.loads(raw, object_pairs_hook=unique))


def export_features(
    directory,
    features,
    labels,
    *,
    feature_names,
    timestamps,
    label_end,
    hidden=None,
    epochs=10,
    batch_size=32,
    learning_rate=0.001,
    seed=7,
    wall_seconds=30,
):
    """Export CPU-produced arrays and a separate causal audit sidecar.

    Times must be integer ticks in a caller-defined common clock. No rows are
    silently dropped. The caller must purge overlaps before calling this function.
    """
    request = dict(
        template=TEMPLATE,
        features=features,
        labels=labels,
        hidden=[16] if hidden is None else hidden,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        seed=seed,
        wall_seconds=wall_seconds,
    )
    raw = encode(request)
    n, width = len(features), len(features[0])
    if (
        type(feature_names) is not list
        or len(feature_names) != width
        or any(type(name) is not str or not name for name in feature_names)
        or len(set(feature_names)) != width
    ):
        raise ValueError("Unique feature names must match matrix columns")
    if len(timestamps) != n or len(label_end) != n:
        raise ValueError("Timeline must match samples")
    if any(type(t) is not int for t in [*timestamps, *label_end]):
        raise ValueError("Timeline requires integer ticks")
    if any(a >= b for a, b in zip(timestamps, timestamps[1:], strict=False)):
        raise ValueError("Timestamps must strictly increase")
    if any(end <= start for start, end in zip(timestamps, label_end, strict=True)):
        raise ValueError("Labels must end after feature time")
    split = n * 4 // 5
    if max(label_end[:split]) >= timestamps[split]:
        raise ValueError("Training labels overlap validation; purge and recheck actual 80/20 split")
    sidecar = dict(
        status="OFFLINE_INPUT_PREPARED",
        qualification="RESEARCH_UNQUALIFIED",
        input_sha256=hashlib.sha256(raw).hexdigest(),
        input_bytes=len(raw),
        feature_names=feature_names,
        train_rows=split,
        validation_rows=n - split,
        timestamps=timestamps,
        label_end=label_end,
        limitation="Validation is not OOS; timestamps alone do not prove feature causality",
    )
    directory = Path(directory)
    # Claim a fresh directory atomically; competing exports cannot overwrite it.
    directory.parent.mkdir(parents=True, exist_ok=True)
    directory.mkdir(exist_ok=False)
    (directory / "input.json").write_bytes(raw)
    (directory / "audit.json").write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    return sidecar


def prepare_quote(client, payload, directory, max_credits="1"):
    """Upload bounded input and quote only. Preserve ambiguous POSTs for reconciliation."""
    budget = Decimal(max_credits)
    if not budget.is_finite() or budget <= 0:
        raise ValueError("Credit cap must be finite and positive")
    raw = encode(payload)
    binding = dict(
        origin=client.base,
        input_sha256=hashlib.sha256(raw).hexdigest(),
        account=hashlib.sha256(client._key.encode()).hexdigest(),
        max_credits=str(budget),
    )
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "gpu-plan.json"
    state = json.loads(path.read_text()) if path.exists() else {"binding": binding}
    if state["binding"] != binding:
        raise ValueError("Plan belongs to another input/account/budget; use a new directory")
    for step in ("input", "quote"):
        if "input" in state and (
            state["input"].get("input_sha256") != binding["input_sha256"]
            or state["input"].get("template") != TEMPLATE
        ):
            raise ValueError("Saved input hash/template mismatch")
        if step in state:
            continue
        if state.get("pending"):
            raise ValueError(
                "Previous POST outcome is unknown; inspect owned artifacts before retrying"
            )
        state["pending"] = step
        save_json(path, state)
        try:
            reply = (
                client.gpu_input(payload)
                if step == "input"
                else client.gpu_quote(state["input"]["input_artifact_id"], str(budget))
            )
        except APIError as exc:
            if 400 <= exc.status < 500:
                state.pop("pending")
                save_json(path, state)
            raise
        state[step] = reply
        state.pop("pending")
        save_json(path, state)
        if step == "input" and (
            reply.get("input_sha256") != binding["input_sha256"]
            or reply.get("template") != TEMPLATE
        ):
            raise ValueError("Server input hash/template mismatch")
    if state["input"].get("input_sha256") != binding["input_sha256"]:
        raise ValueError("Saved input hash mismatch")
    amount = Decimal(state["quote"]["maximum_charged_credits"])
    if not amount.is_finite() or amount < 0 or amount > budget:
        raise ValueError("Quote exceeds your credit cap")
    return {
        "status": "quoted",
        "submitted": False,
        "quote": state["quote"],
        "input_artifact_id": state["input"]["input_artifact_id"],
        "limitation": "Quote only; execution and model quality are not verified",
    }


def main(argv=None):
    """Prepare synthetic input or validate an existing file, entirely offline."""
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path, help="Create synthetic input in a NEW directory")
    action.add_argument("--validate", type=Path, help="Validate a local template input JSON")
    action.add_argument(
        "--quote", type=Path, help="Upload this input and request a LIVE quote only"
    )
    parser.add_argument("--allow-writes", action="store_true")
    parser.add_argument("--max-credits", default="1")
    parser.add_argument("--work-dir", type=Path, default=Path("work/gpu-quote"))
    args = parser.parse_args(argv)
    if args.quote and not args.allow_writes:
        parser.error("Live input upload and quote require --allow-writes")
    try:
        if args.quote is not None:
            key = os.environ.get("DATAPANEL_API_KEY")
            if not key:
                parser.error("Set DATAPANEL_API_KEY in your environment")
            with args.quote.open("rb") as stream:
                payload = decode(stream.read(LIMIT + 1))
            with DataPanel(
                key, os.getenv("DATAPANEL_BASE_URL", "https://datapanel.dev"), allow_writes=True
            ) as client:
                result = prepare_quote(client, payload, args.work_dir, args.max_credits)
        elif args.validate is not None:
            # Bound the read even if the file grows while it is being read.
            with args.validate.open("rb") as stream:
                raw = stream.read(LIMIT + 1)
            request = decode(raw)
            result = dict(
                status="INPUT_VALID_OFFLINE_ONLY",
                input_bytes=len(raw),
                input_sha256=hashlib.sha256(raw).hexdigest(),
                samples=len(request["features"]),
                features=len(request["features"][0]),
                limitation="Schema only; no timeline, GPU execution or API availability verified",
            )
        else:
            result = export_features(
                args.output,
                [[i / 64, (i % 7) / 7] for i in range(64)],
                [i / 128 for i in range(64)],
                feature_names=["synthetic_trend", "synthetic_cycle"],
                timestamps=[10 * i for i in range(64)],
                label_end=[10 * i + 1 for i in range(64)],
            )
            result = {k: v for k, v in result.items() if k not in ("timestamps", "label_end")}
    except (APIError, ValueError, OSError, RecursionError) as exc:
        # Never echo input values or file contents in validation errors.
        if isinstance(exc, FileExistsError):
            message = "Output directory exists; choose a new directory"
        elif isinstance(exc, OSError):
            message = "Unable to read input or create output; check paths and permissions"
        elif isinstance(exc, (json.JSONDecodeError, UnicodeError, RecursionError)):
            message = "Input is not a supported JSON document"
        else:
            message = str(exc)
        parser.exit(2, f"error: {message}\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
