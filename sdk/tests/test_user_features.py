import json
from pathlib import Path

import pytest

from datapanel_agent.training import configuration, feature_contract, fixture, render_source

CUSTOM = Path(__file__).resolve().parents[1] / "examples/training/custom_features.py"
SELECTION = {
    "market": "fixture",
    "symbol": "demo",
    "data_type": "MBP-20",
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-01T00:10:00Z",
}


def test_custom_second_level_feature_really_enters_standalone_training(tmp_path):
    source = CUSTOM.read_text()
    result = fixture(tmp_path, source)
    model = json.loads((tmp_path / "outputs/result.json").read_text())
    assert result["status"] == "verified"
    assert model["model"]["architecture"] == "linear_4_to_1"
    assert model["model"]["feature_order"][-1] == "level2_imbalance"
    assert len(model["model"]["weights"]) == 4 and abs(model["model"]["weights"][-1]) > 1e-6
    assert len(model["model"]["scaler"]["mean"]) == 4
    assert all(len(p["x"]) == 4 for p in model["reload_probes"])
    assert "Bq2" in model["input"]["observed_schemas"][0]
    assert ".user_features import" not in (tmp_path / "source.py").read_text()


def test_custom_feature_changes_model_predictions(tmp_path):
    fixture(tmp_path / "default")
    fixture(tmp_path / "custom", CUSTOM.read_text())
    a = json.loads((tmp_path / "default/outputs/result.json").read_text())
    b = json.loads((tmp_path / "custom/outputs/result.json").read_text())
    assert a["reload_probes"][0]["prediction_bps"] != b["reload_probes"][0]["prediction_bps"]
    assert a["config"]["feature_source_sha256"] != b["config"]["feature_source_sha256"]


def test_feature_contract_parsing_does_not_execute_user_module():
    source = "raise RuntimeError('should not execute during planning')\n" + CUSTOM.read_text()
    config = configuration(SELECTION, feature_source=source)
    assert len(config["feature_names"]) == 4
    compile(render_source(config, source), "guest.py", "exec")


def test_modified_feature_source_cannot_reuse_frozen_config():
    source = CUSTOM.read_text()
    config = configuration(SELECTION, feature_source=source)
    with pytest.raises(ValueError, match="frozen configuration"):
        render_source(config, source + "\n# edited\n")


@pytest.mark.parametrize(
    "old,new",
    [
        ('"Bq2", "Aq2"', '"exSeq", "Aq2"'),
        ('"level2_imbalance")', '"level1_imbalance")'),
        ("def build_features(", "def wrong_name("),
    ],
)
def test_invalid_feature_contracts_fail_before_upload(old, new):
    source = CUSTOM.read_text()
    assert old in source
    with pytest.raises(ValueError):
        feature_contract(source.replace(old, new))
