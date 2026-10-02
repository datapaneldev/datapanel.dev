import copy
import csv
import hashlib
import json
import math
import sys
from types import SimpleNamespace

import pytest

from datapanel_agent import training_program as model
from datapanel_agent.client import ExecutionClosed
from datapanel_agent.training import (
    configuration,
    fixture,
    live_training,
    render_source,
    require_profile,
    verify_model,
)

SELECTION = {
    "market": "synthetic",
    "symbol": "DEMO",
    "data_type": "MBP-20",
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-01T00:10:00Z",
}


def rows():
    start, mid, data = model.epoch_ns(SELECTION["start"]), 100.0, []
    for i in range(600):
        mid *= 1 + math.sin(i / 11) / 10000
        data.append(
            (
                start + i * 10**9,
                mid - 0.005,
                mid + 0.005,
                12 + math.sin(i / 11),
                12 - math.sin(i / 11),
            )
        )
    return data


def test_standalone_cpu_payload_and_json_reload(tmp_path):
    result = fixture(tmp_path)
    assert result["runtime"]["device"] == "cpu"
    assert result["max_absolute_error_bps"] == 0
    assert result["metrics"]["oos"]["mse_bps2"] < result["metrics"]["oos"]["zero_baseline_mse_bps2"]
    assert result["remote_compute"] is False


def test_future_changes_cannot_change_training_scaler_model_or_past_features():
    data = rows()
    changed = copy.deepcopy(data)
    for i in range(500, len(changed)):
        t, bid, ask, bq, aq = changed[i]
        changed[i] = (t, bid * 1.1, ask * 1.1, bq * 2, aq)
    config = configuration(SELECTION)
    first, second = (model.train(x, config, {}) for x in (data, changed))
    assert first["model"] == second["model"]
    assert first["metrics"]["train"] == second["metrics"]["train"]
    assert first["metrics"]["oos"] != second["metrics"]["oos"]
    assert [r["x"] for r in model.samples(data)[:499]] == [
        r["x"] for r in model.samples(changed)[:499]
    ]


def test_split_removes_labels_touching_next_segment():
    train, valid, oos = model.split_samples(model.samples(rows()))
    assert train[-1]["label_end"] < valid[0]["at"]
    assert valid[-1]["label_end"] < oos[0]["at"]
    assert len(train) + len(valid) + len(oos) == len(rows()) - 4


def test_schema_time_selection_and_oversize_rejection(tmp_path):
    data = rows()
    with (tmp_path / "data.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(model.FIELDS)
        writer.writerows(data)
    cfg = configuration({**SELECTION, "start": "2026-01-01T00:02:00Z"})
    selected, schema = model.read_market(tmp_path, cfg)
    assert len(selected) == 480 and schema["scanned"] == 600
    with pytest.raises(ValueError, match="no silent truncation"):
        model.read_market(tmp_path, {**cfg, "max_rows": 200})
    (tmp_path / "data.csv").write_text("unknown\n1\n")
    with pytest.raises(ValueError, match="schema"):
        model.read_market(tmp_path, cfg)


def test_json_model_tamper_rejected(tmp_path):
    fixture(tmp_path)
    path = tmp_path / "outputs/result.json"
    result = json.loads(path.read_text())
    result["model"]["bias"] += 1
    path.write_text(json.dumps(result))
    with pytest.raises(ValueError, match="prediction mismatch"):
        verify_model(path)


def test_gpu_does_not_fall_back_to_cpu(monkeypatch):
    monkeypatch.setitem(
        sys.modules, "torch", SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False))
    )
    with pytest.raises(RuntimeError, match="fallback is forbidden"):
        model.fit_gpu([[0, 0, 0]], [0], configuration(SELECTION, "gpu"))
    profiles = {"profiles": {"cpu-small": {"gpu_count": 0}}}
    with pytest.raises(ExecutionClosed):
        require_profile(profiles, "cpu-small", "gpu")
    with pytest.raises(ExecutionClosed):
        require_profile(profiles, "gpu-invented", "gpu")


class FakeControl:
    """Simulation for submission/recovery behavior, not runtime evidence."""

    base = "https://test.example"

    def __init__(self, work):
        self.work, self.posts, self.keys = work, [], []
        self.open, self.drop, self.status = True, False, "RUNNING"
        self.identity = "test@example.invalid"
        self.mapping = True

    def me(self):
        return {"email": self.identity}

    def profiles(self):
        return {
            "execution_enabled": self.open,
            "profiles": {"cpu-small": {"gpu_count": 0, "max_wall_seconds": 7200}},
        }

    def upload_source(self, name, source):
        self.posts.append("source")
        return {"id": "source1", "sha256": hashlib.sha256(source.encode()).hexdigest()}

    def snapshot(self, selected):
        self.posts.append("snapshot")
        return {"id": "snapshot1"}

    def quote(self, body):
        self.posts.append("quote")
        return {"quote_id": "quote1", "maximum_charged_credits": ".2"}

    def submit_job(self, body, key):
        manifest = json.loads((self.work / "run.json").read_text())
        assert manifest["idempotency_key"] == key and manifest["job_request"] == body
        self.keys.append(key)
        if self.drop:
            self.drop = False
            raise TimeoutError("response lost")
        return {"job_id": "job1"}

    def job_status(self, job_id):
        result = {"status": self.status, "job_id": job_id}
        if self.mapping:
            result.update(result_artifact_id="result1", output_artifact_ids=["result1"])
        return result

    def sleep(self, interval):
        pass

    def export_private(self, asset, target, **kwargs):
        result = model.train(rows(), configuration(SELECTION), {})
        target.write_text(json.dumps(result))


def test_ambiguous_submit_reuses_frozen_body_and_key(tmp_path):
    client = FakeControl(tmp_path)
    client.drop = True
    with pytest.raises(TimeoutError):
        live_training(client, SELECTION, tmp_path, submit=True, max_polls=1)
    result = live_training(client, SELECTION, tmp_path, submit=True, max_polls=1)
    assert result["status"] == "RUNNING"
    assert len(set(client.keys)) == 1
    assert client.posts == ["source", "snapshot", "quote"]
    client.status = "SUCCEEDED"
    assert live_training(client, SELECTION, tmp_path, max_polls=1)["status"] == "verified"
    assert len(client.keys) == 2  # one ambiguous call and one retry; never a third submit


def test_closed_execution_does_not_create_assets(tmp_path):
    client = FakeControl(tmp_path)
    client.open = False
    with pytest.raises(ExecutionClosed):
        live_training(client, SELECTION, tmp_path, submit=True)
    assert not client.posts and not client.keys


def test_quote_does_not_submit_and_resume_rejects_changed_owner(tmp_path):
    client = FakeControl(tmp_path)
    assert live_training(client, SELECTION, tmp_path)["status"] == "quoted"
    assert client.keys == []
    client.identity = "other@example.invalid"
    with pytest.raises(ValueError, match="different source/config/account"):
        live_training(client, SELECTION, tmp_path, submit=True)


def test_missing_result_mapping_is_not_replaced_by_latest_asset(tmp_path):
    client = FakeControl(tmp_path)
    client.status, client.mapping = "SUCCEEDED", False
    with pytest.raises(ValueError, match="ownership mapping"):
        live_training(client, SELECTION, tmp_path, submit=True, max_polls=1)


def test_failure_remains_failure(tmp_path):
    client = FakeControl(tmp_path)
    client.status = "FAILED"
    result = live_training(client, SELECTION, tmp_path, submit=True, max_polls=1)
    assert result["terminal"] is True and result["status"] == "FAILED"
    assert not (tmp_path / "result.json").exists()


def test_render_freezes_configuration_and_stays_standalone():
    cfg = configuration(SELECTION)
    source = render_source(cfg)
    compile(source, "train_model.py", "exec")
    assert "from datapanel_agent" not in source
    assert str(cfg["steps"]) in source


def test_training_honors_next_poll_seconds(tmp_path):
    client = FakeControl(tmp_path)
    delays = []
    client.job_status = lambda job_id: {
        "job_id": job_id,
        "status": "PENDING",
        "next_poll_seconds": 15,
    }
    client.sleep = delays.append
    result = live_training(client, SELECTION, tmp_path, submit=True, max_polls=2, interval=1)
    assert delays == [15]
    assert result["status"] == "PENDING"
    assert len(client.keys) == 1
