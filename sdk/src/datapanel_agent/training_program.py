"""Single-file training payload. CPU requires only Python's standard library.

DataPanel supplies DP_INPUT_DIR / DP_OUTPUT_DIR. Never downloads dependencies.
The GPU branch requires a platform-provided PyTorch CUDA runtime; no CPU fallback.
"""

import csv
import gzip
import hashlib
import json
import math
import os
from datetime import datetime, timedelta
from pathlib import Path

from .user_features import FEATURE_INPUT_FIELDS, FEATURE_NAMES, build_features

CONFIG = {}  # Replaced with a frozen JSON configuration by the cookbook.
BASE_FIELDS = ("lcTsNs", "Bp1", "Ap1", "Bq1", "Aq1")
FIELDS = BASE_FIELDS + tuple(k for k in FEATURE_INPUT_FIELDS if k not in BASE_FIELDS)
FEATURES = FEATURE_NAMES


def epoch_ns(value):
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None or value.microsecond:
        raise ValueError("Require timezone-aware whole-second selection")
    return int(value.timestamp()) * 1_000_000_000


def read_market(directory, config):
    """Bounded schema discovery; retain all selected rows or reject oversize input."""
    start, end = (epoch_ns(config[k]) for k in ("start", "end"))
    rows, scanned, schemas = [], 0, set()
    for path in sorted(Path(directory).rglob("*")):
        if not path.is_file() or not str(path).endswith((".csv", ".csv.gz")):
            continue
        if path.is_symlink():
            raise ValueError("Input symlinks are not accepted")
        opener = gzip.open if str(path).endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or not set(FIELDS) <= set(reader.fieldnames):
                raise ValueError("Input requires explicit level-one book schema")
            schemas.add(tuple(reader.fieldnames))
            for record in reader:
                scanned += 1
                if scanned > config["max_scan_rows"]:
                    raise ValueError("Input scan cap exceeded; select a smaller snapshot")
                stamp = int(record["lcTsNs"])
                if start <= stamp < end:
                    values = [float(record[k]) for k in FIELDS[1:]]
                    if not all(math.isfinite(x) for x in values):
                        raise ValueError("Non-finite market input")
                    bid, ask, bq, aq = values[:4]
                    if not 0 < bid <= ask or min(bq, aq) < 0 or bq + aq <= 0:
                        raise ValueError("Invalid level-one book")
                    rows.append((stamp, *values))
                    if len(rows) > config["max_rows"]:
                        raise ValueError("Selected row cap exceeded; no silent truncation")
    rows.sort(key=lambda row: row[0])
    if len(rows) < 120 or any(a[0] >= b[0] for a, b in zip(rows, rows[1:], strict=False)):
        raise ValueError("Need at least 120 strictly increasing observations")
    return rows, {"observed_schemas": [list(s) for s in sorted(schemas)], "scanned": scanned}


def samples(rows):
    mids = [(r[1] + r[2]) / 2 for r in rows]
    output = []
    for i in range(1, len(rows) - 1):
        stamp = rows[i][0]
        previous = dict(zip(FIELDS, rows[i - 1], strict=True))
        current = dict(zip(FIELDS, rows[i], strict=True))
        features = list(build_features(previous, current))
        if len(features) != len(FEATURES) or not all(
            isinstance(v, (int, float)) and math.isfinite(v) for v in features
        ):
            raise ValueError("build_features must return one finite number per FEATURE_NAMES entry")
        output.append(
            {
                "at": stamp,
                "label_end": rows[i + 1][0],
                "x": features,
                "y": (mids[i + 1] / mids[i] - 1) * 10000,
            }
        )
    return output


def split_samples(data):
    a, b = int(len(data) * 0.6), int(len(data) * 0.8)
    # A label at the next segment's first observation is unavailable before that segment.
    train = [r for r in data[:a] if r["label_end"] < data[a]["at"]]
    valid = [r for r in data[a:b] if r["label_end"] < data[b]["at"]]
    test = data[b:]
    if min(map(len, (train, valid, test))) < 10:
        raise ValueError("Insufficient samples after boundary purging")
    return train, valid, test


def fit_scaler(train):
    mean = [sum(r["x"][j] for r in train) / len(train) for j in range(len(train[0]["x"]))]
    scale = [
        max((sum((r["x"][j] - mean[j]) ** 2 for r in train) / len(train)) ** 0.5, 1e-8)
        for j in range(len(mean))
    ]
    target_mean = sum(r["y"] for r in train) / len(train)
    target_scale = max((sum((r["y"] - target_mean) ** 2 for r in train) / len(train)) ** 0.5, 1e-8)
    return {
        "mean": mean,
        "scale": scale,
        "target_mean": target_mean,
        "target_scale": target_scale,
        "clip": 10.0,
    }


def transform(x, scaler):
    return [
        max(-scaler["clip"], min(scaler["clip"], (v - m) / s))
        for v, m, s in zip(x, scaler["mean"], scaler["scale"], strict=True)
    ]


def predict(model, x):
    z = transform(x, model["scaler"])
    normalized = model["bias"] + sum(w * v for w, v in zip(model["weights"], z, strict=True))
    return normalized * model["scaler"]["target_scale"] + model["scaler"]["target_mean"]


def fit_cpu(x, y, config):
    weights, bias = [0.0] * len(x[0]), 0.0
    for _ in range(config["steps"]):
        residual = [
            bias + sum(w * v for w, v in zip(weights, row, strict=True)) - target
            for row, target in zip(x, y, strict=True)
        ]
        weights = [
            w
            - config["learning_rate"]
            * (
                2 * sum(e * row[j] for e, row in zip(residual, x, strict=True)) / len(x)
                + 2 * config["ridge"] * w
            )
            for j, w in enumerate(weights)
        ]
        bias -= config["learning_rate"] * 2 * sum(residual) / len(x)
    return weights, bias, {"device": "cpu", "implementation": "python-stdlib"}


def fit_gpu(x, y, config):
    # No import, package installation or hardware claim until a real CUDA runtime exists.
    import torch

    if not torch.cuda.is_available() or torch.cuda.device_count() != config["gpu_count"]:
        raise RuntimeError("Required CUDA allocation unavailable; CPU fallback is forbidden")
    if config["gpu_count"] != 1:
        raise RuntimeError("This payload is single-GPU; multi-GPU remains a separate TODO")
    torch.set_num_threads(1)
    torch.manual_seed(2026)
    matrix = torch.tensor(x, dtype=torch.float64, device="cuda")
    targets = torch.tensor(y, dtype=torch.float64, device="cuda")
    model = torch.nn.Linear(len(x[0]), 1, bias=True, dtype=torch.float64, device="cuda")
    with torch.no_grad():
        model.weight.zero_()
        model.bias.zero_()
    optimizer = torch.optim.SGD(model.parameters(), lr=config["learning_rate"])
    for _ in range(config["steps"]):
        optimizer.zero_grad()
        loss = ((model(matrix).flatten() - targets) ** 2).mean()
        loss = loss + config["ridge"] * model.weight.square().sum()
        loss.backward()
        optimizer.step()
    torch.cuda.synchronize()
    return (
        model.weight.detach().cpu().flatten().tolist(),
        model.bias.item(),
        {
            "device": "cuda:0",
            "implementation": "pytorch",
            "torch_version": torch.__version__,
            "cuda_version": torch.version.cuda,
            "visible_gpu_count": torch.cuda.device_count(),
            "gpu_name": torch.cuda.get_device_name(0),
            "multi_gpu": False,
        },
    )


def shard_indices(count, rank, world_size):
    """No sampler padding: every training example appears exactly once."""
    if not 2 <= world_size <= count or not 0 <= rank < world_size:
        raise ValueError("Invalid distributed shard")
    return list(range(rank, count, world_size))


def shard_digest(indices):
    return hashlib.sha256(json.dumps(indices, separators=(",", ":")).encode()).hexdigest()


def verify_ddp_evidence(runtime, count, steps=200):
    """Validate process reports, not independent physical allocation proof."""
    records = runtime.get("ranks", [])
    if (
        runtime.get("world_size") != 2
        or runtime.get("backend") != "nccl"
        or runtime.get("visible_gpu_count") != 2
        or len(records) != 2
    ):
        raise ValueError("Missing two-GPU NCCL evidence")
    uuids, pids, hashes = set(), set(), set()
    for rank, record in enumerate(sorted(records, key=lambda r: r["rank"])):
        indices = shard_indices(count, rank, 2)
        if (
            record["rank"] != rank
            or record["device_index"] != rank
            or record["sample_count"] != len(indices)
            or record["sample_index_sha256"] != shard_digest(indices)
            or record["steps"] != steps
        ):
            raise ValueError("Rank participation or disjoint sample coverage mismatch")
        uuid = record.get("device_uuid")
        if not isinstance(uuid, str) or not uuid or record.get("pid", 0) <= 0:
            raise ValueError("Missing process/device identity")
        for field in ("gradient_max_abs_error", "parameter_max_abs_error"):
            error = record.get(field)
            if (
                not isinstance(error, (int, float))
                or not math.isfinite(error)
                or not 0 <= error <= 1e-9
            ):
                raise ValueError("Distributed gradient/parameter synchronization failed")
        digest = record.get("parameter_sha256", "")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Missing parameter digest")
        uuids.add(uuid)
        pids.add(record["pid"])
        hashes.add(digest)
    error = runtime.get("cpu_reference_max_abs_error")
    if not isinstance(error, (int, float)) or not math.isfinite(error) or not 0 <= error <= 1e-8:
        raise ValueError("Distributed result disagrees with the global-batch CPU reference")
    if len(uuids) != 2 or len(pids) != 2 or len(hashes) != 1:
        raise ValueError("Distinct devices/processes and identical weights are required")


def ddp_worker(rank, x, y, config, rendezvous, result_path):
    import torch
    import torch.distributed as dist
    from torch.nn.parallel import DistributedDataParallel

    torch.set_num_threads(1)
    torch.cuda.set_device(rank)
    properties = torch.cuda.get_device_properties(rank)
    device_uuid = getattr(properties, "uuid", None)
    if not device_uuid:
        raise RuntimeError("Runtime must expose CUDA device UUIDs for multi-GPU evidence")
    dist.init_process_group(
        "nccl",
        init_method=Path(rendezvous).as_uri(),
        rank=rank,
        world_size=2,
        timeout=timedelta(seconds=45),
    )
    try:
        indices = shard_indices(len(x), rank, 2)
        device = f"cuda:{rank}"
        matrix = torch.tensor([x[i] for i in indices], dtype=torch.float64, device=device)
        targets = torch.tensor([y[i] for i in indices], dtype=torch.float64, device=device)
        linear = torch.nn.Linear(len(x[0]), 1, bias=True, dtype=torch.float64, device=device)
        with torch.no_grad():
            linear.weight.zero_()
            linear.bias.zero_()
        model = DistributedDataParallel(linear, device_ids=[rank], output_device=rank)
        optimizer = torch.optim.SGD(model.parameters(), lr=config["learning_rate"])
        gradient_error = None
        for step in range(config["steps"]):
            optimizer.zero_grad()
            # DDP averages gradients. Weight sums by world/N, not local shard means;
            # otherwise odd sample counts change the objective between rank sizes.
            loss = (model(matrix).flatten() - targets).square().sum() * 2 / len(x)
            loss = loss + config["ridge"] * linear.weight.square().sum()
            loss.backward()
            if step == 0:
                actual = linear.weight.grad.flatten().tolist() + linear.bias.grad.tolist()
                expected = [
                    -2 * sum(row[j] * target for row, target in zip(x, y, strict=True)) / len(x)
                    for j in range(len(x[0]))
                ] + [-2 * sum(y) / len(y)]
                gradient_error = max(abs(a - b) for a, b in zip(actual, expected, strict=True))
            optimizer.step()
        torch.cuda.synchronize()
        vector = torch.cat([linear.weight.detach().flatten(), linear.bias.detach()])
        peers = [torch.empty_like(vector) for _ in range(2)]
        dist.all_gather(peers, vector)
        parameter_error = max((p - vector).abs().max().item() for p in peers)
        values = vector.tolist()
        record = {
            "rank": rank,
            "pid": os.getpid(),
            "device_index": rank,
            "device_uuid": str(device_uuid),
            "device_name": properties.name,
            "sample_count": len(indices),
            "sample_index_sha256": shard_digest(indices),
            "steps": config["steps"],
            "gradient_max_abs_error": gradient_error,
            "parameter_max_abs_error": parameter_error,
            "parameter_sha256": hashlib.sha256(json.dumps(values).encode()).hexdigest(),
        }
        records = [None, None]
        dist.all_gather_object(records, record)
        if rank == 0:
            weights, bias, _ = fit_cpu(x, y, config)
            error = max(abs(a - b) for a, b in zip(values, weights + [bias], strict=True))
            runtime = {
                "device": "cuda:0,cuda:1",
                "implementation": "pytorch-ddp",
                "world_size": 2,
                "visible_gpu_count": 2,
                "backend": "nccl",
                "torch_version": torch.__version__,
                "cuda_version": torch.version.cuda,
                "ranks": records,
                "cpu_reference_max_abs_error": error,
                "independent_allocation_and_release_attestation": "REQUIRED_EXTERNALLY",
            }
            verify_ddp_evidence(runtime, len(x), config["steps"])
            Path(result_path).write_text(
                json.dumps(
                    {"weights": values[:-1], "bias": values[-1], "runtime": runtime},
                    allow_nan=False,
                )
            )
        dist.barrier()
    finally:
        dist.destroy_process_group()


def fit_multi_gpu(x, y, config):
    import tempfile

    import torch
    import torch.distributed as dist
    import torch.multiprocessing as mp

    if (
        config["gpu_count"] != 2
        or not torch.cuda.is_available()
        or torch.cuda.device_count() != 2
        or not dist.is_nccl_available()
    ):
        raise RuntimeError("Require exactly two visible CUDA devices and NCCL; no fallback")
    # Proposed runtime: single-node spawn + NCCL + FileStore. The platform must
    # approve shared memory, process and collective transport limits before use.
    # FileStore avoids a user-chosen rendezvous TCP port, not all NCCL networking.
    with tempfile.TemporaryDirectory(prefix="ddp-", dir=os.environ["DP_OUTPUT_DIR"]) as directory:
        rendezvous, result = Path(directory) / "store", Path(directory) / "rank0.json"
        mp.spawn(
            ddp_worker,
            args=(x, y, config, str(rendezvous.resolve()), str(result)),
            nprocs=2,
            join=True,
        )
        output = json.loads(result.read_text())
        verify_ddp_evidence(output["runtime"], len(x), config["steps"])
        return output["weights"], output["bias"], output["runtime"]


def train(rows, config, schema):
    data = samples(rows)
    training, validation, oos = split_samples(data)
    scaler = fit_scaler(training)
    x = [transform(r["x"], scaler) for r in training]
    y = [(r["y"] - scaler["target_mean"]) / scaler["target_scale"] for r in training]
    fit = {"cpu": fit_cpu, "gpu": fit_gpu, "multi-gpu": fit_multi_gpu}[config["backend"]]
    weights, bias, runtime = fit(x, y, config)
    model = {
        "architecture": f"linear_{len(FEATURES)}_to_1",
        "feature_order": list(FEATURES),
        "weights": weights,
        "bias": bias,
        "scaler": scaler,
    }
    metrics = {}
    for name, segment in (("train", training), ("validation", validation), ("oos", oos)):
        pred = [predict(model, r["x"]) for r in segment]
        metrics[name] = {
            "count": len(segment),
            "first_ns": segment[0]["at"],
            "last_ns": segment[-1]["at"],
            "label_end_ns": segment[-1]["label_end"],
            "mse_bps2": sum((p - r["y"]) ** 2 for p, r in zip(pred, segment, strict=True))
            / len(segment),
            "zero_baseline_mse_bps2": sum(r["y"] ** 2 for r in segment) / len(segment),
        }
    result = {
        "format": "datapanel-linear-demo-v1",
        "qualification": "RESEARCH_UNQUALIFIED",
        "data_mode": config["data_mode"],
        "config": config,
        "runtime": runtime,
        "input": {
            "rows": len(rows),
            "sha256": hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest(),
            **schema,
        },
        "model": model,
        "metrics": metrics,
        "reload_probes": [{"x": r["x"], "prediction_bps": predict(model, r["x"])} for r in oos[:3]],
        "limitations": [
            "next-observation prediction, not trading PnL",
            "single process sees full input; no platform-isolated OOS",
            "full OOS NPY and paired backtests not implemented",
            "GPU/DDP hardware and resource-release evidence require platform acceptance",
        ],
    }
    json.dumps(result, allow_nan=False)  # Refuse divergent or non-finite results.
    return result


def main():
    rows, schema = read_market(os.environ["DP_INPUT_DIR"], CONFIG)
    result = train(rows, CONFIG, schema)
    target = Path(os.environ["DP_OUTPUT_DIR"]) / "result.json"
    target.write_text(json.dumps(result, allow_nan=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
