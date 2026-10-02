import copy
import json

import pytest

from datapanel_agent.gpu_template import LIMIT, decode, encode, export_features


def payload(n=32, width=2):
    return dict(
        template="mlp-regression-v1",
        features=[[0.1] * width for _ in range(n)],
        labels=[0.2] * n,
        hidden=[16],
        epochs=10,
        batch_size=32,
        learning_rate=0.001,
        seed=7,
        wall_seconds=30,
    )


@pytest.mark.parametrize("n,width", [(32, 1), (32, 128), (16384, 1)])
def test_roundtrip(n, width):
    value = payload(n, width)
    assert decode(encode(value)) == value


@pytest.mark.parametrize(
    "key,value",
    [
        ("features", [[0]] * 31),
        ("features", [[0]] * 16385),
        ("features", [[]] * 32),
        ("features", [[0] * 129] * 32),
        ("features", [[0], [0, 1]] * 16),
        ("labels", [True] * 32),
        ("labels", [float("nan")] * 32),
        ("labels", [float("inf")] * 32),
        ("labels", [1e6 + 1] * 32),
        ("labels", [[0]] * 32),
        ("hidden", []),
        ("hidden", [256, 256]),
        ("hidden", [True]),
        ("epochs", 201),
        ("epochs", True),
        ("batch_size", 7),
        ("seed", -1),
        ("wall_seconds", 121),
        ("learning_rate", 0),
        ("python", "print('not allowed')"),
        ("template", "arbitrary-python"),
    ],
)
def test_reject_invalid(key, value):
    request = payload()
    request[key] = value
    with pytest.raises(ValueError):
        encode(request)


def test_bytes_and_duplicate_keys():
    with pytest.raises(ValueError):
        decode(b" " * (LIMIT + 1))
    raw = encode(payload())
    with pytest.raises(ValueError):
        decode(b'{"seed":7,' + raw[1:])
    # Valid dimensions can still exceed the serialized byte budget.
    with pytest.raises(ValueError, match="2 MiB"):
        encode(payload(16384, 128))


def test_export_audit_and_overlap(tmp_path):
    tmp_path = tmp_path / "export"
    request = payload()
    kwargs = dict(
        feature_names=["a", "b"],
        timestamps=list(range(0, 320, 10)),
        label_end=list(range(1, 321, 10)),
    )
    bad = copy.deepcopy(kwargs)
    bad["label_end"][24] = 250
    with pytest.raises(ValueError, match="overlap"):
        export_features(tmp_path, request["features"], request["labels"], **bad)
    assert not tmp_path.exists()
    audit = export_features(tmp_path, request["features"], request["labels"], **kwargs)
    assert audit["train_rows"] == 25
    assert audit["validation_rows"] == 7
    assert json.loads((tmp_path / "audit.json").read_text()) == audit
    assert decode((tmp_path / "input.json").read_bytes())["features"] == request["features"]
    with pytest.raises(FileExistsError):
        export_features(tmp_path, request["features"], request["labels"], **kwargs)


def test_cli_generate_validate_and_refuse_overwrite(tmp_path, capsys):
    from datapanel_agent.gpu_template import main

    output = tmp_path / "new"
    assert main(["--output", str(output)]) == 0
    generated = json.loads(capsys.readouterr().out)
    assert main(["--validate", str(output / "input.json")]) == 0
    checked = json.loads(capsys.readouterr().out)
    assert checked["input_sha256"] == generated["input_sha256"]
    assert checked["status"] == "INPUT_VALID_OFFLINE_ONLY"
    before = (output / "input.json").read_bytes()
    with pytest.raises(SystemExit) as error:
        main(["--output", str(output)])
    assert error.value.code == 2
    assert "choose a new directory" in capsys.readouterr().err
    assert (output / "input.json").read_bytes() == before


@pytest.mark.parametrize("raw", [b"invalid SECRET", b"\xff", b"[" * 2000, b" " * (LIMIT + 1)])
def test_cli_bad_input_is_bounded_and_redacted(tmp_path, capsys, raw):
    from datapanel_agent.gpu_template import main

    source = tmp_path / "bad.json"
    source.write_bytes(raw)
    with pytest.raises(SystemExit) as error:
        main(["--validate", str(source)])
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert "SECRET" not in captured.err
    assert "Traceback" not in captured.err
    assert not captured.out


def gpu_client(handler):
    import httpx

    from datapanel_agent.client import DataPanel

    return DataPanel(
        "test-key",
        "https://api.example",
        allow_writes=True,
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
    )


def test_gpu_quote_uses_separate_routes_and_reuses_input(tmp_path):
    import hashlib

    import httpx

    from datapanel_agent.gpu_template import prepare_quote

    calls = []
    request = payload()

    def handler(req):
        calls.append(req.url.path)
        if req.url.path.endswith("/inputs"):
            assert json.loads(req.content) == request
            return httpx.Response(
                200,
                json={
                    "input_artifact_id": "input1",
                    "input_sha256": hashlib.sha256(encode(request)).hexdigest(),
                    "template": request["template"],
                },
            )
        assert req.url.path == "/v1/compute/gpu-template-jobs/quotes"
        assert json.loads(req.content) == {"input_artifact_id": "input1", "max_credits": "1"}
        return httpx.Response(200, json={"quote_id": "quote1", "maximum_charged_credits": "0.1"})

    with gpu_client(handler) as client:
        result = prepare_quote(client, request, tmp_path)
        assert result == prepare_quote(client, request, tmp_path)
        assert result["submitted"] is False
        with pytest.raises(ValueError, match="another input"):
            prepare_quote(client, request, tmp_path, "2")
    assert len(calls) == 2  # No generic profiles read, no job submission, no duplicate upload.


def test_gpu_lost_upload_response_does_not_duplicate(tmp_path):
    import httpx

    from datapanel_agent.client import APIError
    from datapanel_agent.gpu_template import prepare_quote

    calls = []

    def handler(req):
        calls.append(req)
        raise httpx.ReadTimeout("lost", request=req)

    with gpu_client(handler) as client:
        with pytest.raises(APIError):
            prepare_quote(client, payload(), tmp_path)
        with pytest.raises(ValueError, match="unknown"):
            prepare_quote(client, payload(), tmp_path)
    assert len(calls) == 1


@pytest.mark.parametrize("budget", ["0", "-1", "NaN", "Infinity"])
def test_gpu_quote_invalid_budget_is_local(tmp_path, budget):
    from datapanel_agent.gpu_template import prepare_quote

    with gpu_client(lambda _: pytest.fail("must not upload")) as client:
        with pytest.raises(ValueError):
            prepare_quote(client, payload(), tmp_path, budget)


def test_gpu_input_hash_mismatch_cannot_quote_on_resume(tmp_path):
    import httpx

    from datapanel_agent.gpu_template import prepare_quote

    calls = []

    def handler(req):
        calls.append(req.url.path)
        return httpx.Response(
            200,
            json={
                "input_artifact_id": "wrong",
                "input_sha256": "0" * 64,
                "template": "mlp-regression-v1",
            },
        )

    with gpu_client(handler) as client:
        for _ in range(2):
            with pytest.raises(ValueError, match="mismatch"):
                prepare_quote(client, payload(), tmp_path)
    assert len(calls) == 1
