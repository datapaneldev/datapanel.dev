"""Offline admission/mathematical/evidence checks; no CUDA execution or GPU claim."""

import copy
import json

import httpx
import pytest

from datapanel_agent import training_program as model
from datapanel_agent.client import DataPanel, ExecutionClosed, require_execution
from datapanel_agent.training import configuration, render_source, require_profile


@pytest.mark.parametrize(
    "field,value",
    [
        ("enabled_profiles", []),
        ("enabled_kinds", []),
        ("enabled_profiles", ["cpu-large"]),
        ("enabled_kinds", ["features"]),
        ("enabled_profiles", "cpu-small"),
        ("enabled_kinds", None),
    ],
)
def test_account_allowlists_block_before_submission(field, value):
    calls = []

    def api(request):
        calls.append((request.method, request.url.path))
        if request.url.path == "/v1/compute/profiles":
            return httpx.Response(200, json={"execution_enabled": True, field: value})
        pytest.fail("Disallowed job must never be submitted")

    with DataPanel(
        "test", "https://test.example", transport=httpx.MockTransport(api), allow_writes=True
    ) as client:
        with pytest.raises(ExecutionClosed):
            client.submit_job({"resource_profile": "cpu-small", "kind": "train"}, "example-key")
    assert calls == [("GET", "/v1/compute/profiles")]


def test_published_gpu_count_is_not_account_permission():
    profiles = {
        "execution_enabled": True,
        "enabled_profiles": [],
        "enabled_kinds": ["train"],
        "profiles": {"fixture-two-gpu": {"gpu_count": 2}},
    }
    require_profile(profiles, "fixture-two-gpu", "multi-gpu")
    with pytest.raises(ExecutionClosed):
        require_execution(profiles, "fixture-two-gpu", "train")
    profiles["enabled_profiles"] = ["fixture-two-gpu"]
    require_execution(profiles, "fixture-two-gpu", "train")


@pytest.mark.parametrize("count", [0, 1, 4, True])
def test_multigpu_never_substitutes_another_allocation(count):
    with pytest.raises(ExecutionClosed):
        require_profile({"profiles": {"test": {"gpu_count": count}}}, "test", "multi-gpu")


def test_uneven_shard_gradient_matches_global_objective():
    # Five observations across two ranks makes naive averaging of shard means wrong.
    xs, ys, weight, bias, ridge = [1, 2, 5, 9, 11], [3, -2, 4, 1, 7], 0.3, -0.2, 0.001
    gradients, samples = [], []
    for rank in range(2):
        indices = model.shard_indices(len(xs), rank, 2)
        samples.extend(indices)
        gradients.append(
            2 * 2 / len(xs) * sum((weight * xs[i] + bias - ys[i]) * xs[i] for i in indices)
            + 2 * ridge * weight
        )
    expected = (
        2 / len(xs) * sum((weight * x + bias - y) * x for x, y in zip(xs, ys, strict=True))
        + 2 * ridge * weight
    )
    assert sorted(samples) == list(range(len(xs))) and len(set(samples)) == len(xs)
    assert sum(gradients) / 2 == pytest.approx(expected)


def evidence():
    # Synthetic validator inputs, not runtime reports.
    return {
        "world_size": 2,
        "visible_gpu_count": 2,
        "backend": "nccl",
        "cpu_reference_max_abs_error": 0.0,
        "ranks": [
            {
                "rank": rank,
                "device_index": rank,
                "device_uuid": f"SYNTHETIC-{rank}",
                "pid": rank + 100,
                "steps": 200,
                "sample_count": len(model.shard_indices(357, rank, 2)),
                "sample_index_sha256": model.shard_digest(model.shard_indices(357, rank, 2)),
                "gradient_max_abs_error": 0.0,
                "parameter_max_abs_error": 0.0,
                "parameter_sha256": "a" * 64,
            }
            for rank in range(2)
        ],
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("device_uuid", "SYNTHETIC-0"),
        ("pid", 100),
        ("rank", 0),
        ("device_index", 0),
        ("steps", 0),
        ("sample_count", 179),
        ("sample_index_sha256", "wrong"),
        ("gradient_max_abs_error", 0.1),
        ("parameter_max_abs_error", float("nan")),
        ("parameter_sha256", "b" * 64),
    ],
)
def test_rejects_fake_or_inconsistent_two_rank_evidence(field, value):
    report = evidence()
    model.verify_ddp_evidence(report, 357)
    changed = copy.deepcopy(report)
    changed["ranks"][1][field] = value
    with pytest.raises(ValueError):
        model.verify_ddp_evidence(changed, 357)


def test_rejects_wrong_cpu_reference_and_missing_rank():
    report = evidence()
    report["cpu_reference_max_abs_error"] = 0.01
    with pytest.raises(ValueError):
        model.verify_ddp_evidence(report, 357)
    report["ranks"].pop()
    with pytest.raises(ValueError):
        model.verify_ddp_evidence(report, 357)


def test_two_gpu_payload_is_standalone_but_not_hardware_validated():
    cfg = configuration(
        {
            "market": "fixture",
            "data_type": "MBP-20",
            "symbol": "demo",
            "start": "2026-01-01T00:00:00Z",
            "end": "2026-01-01T00:10:00Z",
        },
        "multi-gpu",
    )
    assert cfg["gpu_count"] == 2
    source = render_source(cfg)
    compile(source, "conditional_two_gpu.py", "exec")
    assert "from datapanel_agent" not in source
    assert "REQUIRED_EXTERNALLY" in source
    assert json.loads(json.dumps(evidence()))["world_size"] == 2
