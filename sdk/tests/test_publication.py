"""Reject publication hazards regardless of the document extension."""

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "publication_policy", Path(__file__).parents[1] / "scripts/publication_policy.py"
)
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


@pytest.mark.parametrize("suffix", [".md", ".json", ".html", ".py", ".yaml"])
@pytest.mark.parametrize(
    "payload",
    [
        "dp_" + "Z" * 48,
        "/mnt/" + "c/Users/private/source",
        "192.168." + "20.30",
        "-----BEGIN " + "PRIVATE KEY-----",
        "https://" + "user:password@service.example",
    ],
)
def test_sensitive_content_is_rejected(suffix, payload):
    with pytest.raises(ValueError, match="private content"):
        policy.validate_content(Path("docs/example" + suffix), payload.encode())


@pytest.mark.parametrize(
    "name", [".env", ".env.local", "weights.pkl", "payload.zip", "key.pem", "RESEARCH_STATE.md"]
)
def test_unreviewed_files_are_rejected(name):
    with pytest.raises(ValueError):
        policy.validate_content(Path("docs") / name, b"innocent-looking text")


def test_binary_disguised_as_text_is_rejected():
    with pytest.raises(ValueError, match="binary"):
        policy.validate_content(Path("docs/result.json"), b"data\x00payload")


def test_symlink_to_private_content_is_rejected(tmp_path):
    (tmp_path / "docs").mkdir()
    secret = tmp_path / "secret"
    secret.write_text("private")
    (tmp_path / "docs/guide.md").symlink_to(secret)
    with pytest.raises(ValueError, match="Symlink"):
        policy.collect(tmp_path)


def test_collected_bytes_are_immutable_and_history_is_excluded(tmp_path):
    (tmp_path / "docs").mkdir()
    source = tmp_path / "docs/guide.md"
    source.write_text("public tutorial")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/private.md").write_text("private")
    files = policy.collect(tmp_path)
    source.write_text("changed after validation")
    assert files == {Path("docs/guide.md"): b"public tutorial"}
