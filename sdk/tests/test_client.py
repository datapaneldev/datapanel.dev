import hashlib

import httpx
import pytest

from datapanel_agent.client import APIError, DataPanel, ExecutionClosed, redact, selection_body
from datapanel_agent.mock import ARCHIVE, catalog_rows, mock_client
from datapanel_agent.workflows import download


def client_for(handler, **kwargs):
    return DataPanel(
        "private-test-key",
        "https://api.example",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
        **kwargs,
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://api.example",
        "https://" + "a:b@api.example",
        "https://api.example/x",
        "https://api.example?key=x",
        "https://api.example#fragment",
    ],
)
def test_base_origin_rejects_ambiguous_urls(url):
    with pytest.raises(ValueError):
        DataPanel(base_url=url)


def test_reads_retry_but_unkeyed_writes_do_not():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(503, json={"detail": "private-test-key"})

    with client_for(handler, allow_writes=True) as client:
        with pytest.raises(APIError) as error:
            client.me()
        assert len(calls) == 3
        assert "private-test-key" not in str(error.value)
        calls.clear()
        with pytest.raises(APIError):
            client.upload_source("x.py", "pass")
        assert len(calls) == 1


def test_keyed_post_retries_same_key_and_body():
    seen = []

    def handler(request):
        seen.append((request.headers["Idempotency-Key"], request.content))
        return httpx.Response(503 if len(seen) == 1 else 200, json={"id": "ok"})

    with client_for(handler, allow_writes=True) as client:
        assert (
            client.request(
                "POST", "/v1/compute/jobs", {"test": True}, idempotency_key="stable-request-1"
            )["id"]
            == "ok"
        )
    assert len(seen) == 2 and seen[0] == seen[1]


@pytest.mark.parametrize("header", ["3600", "Wed, 01 Jan 2031 00:00:00 GMT"])
def test_long_retry_after_is_returned_without_sleeping(header):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(429, headers={"Retry-After": header})

    with client_for(handler) as client:
        with pytest.raises(APIError) as error:
            client.me()
    assert len(calls) == 1 and error.value.retry_after > 30


def test_readonly_blocks_mutation_before_network():
    with client_for(lambda _: pytest.fail("network must not be called")) as client:
        with pytest.raises(PermissionError):
            client.upload_source("x.py", "pass")


def artifact(url="https://objects.example/file?signature=private", auth=False, data=ARCHIVE):
    return {
        "url": url,
        "requires_api_key": auth,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def test_unsigned_object_get_never_inherits_api_key(tmp_path):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, content=ARCHIVE)

    with client_for(handler) as client:
        target = client.save(artifact(), tmp_path / "data.bin")
        # Verified local resume must not consume another content GET.
        client.save(artifact(), target)
    assert target.read_bytes() == ARCHIVE and len(seen) == 1
    assert "X-API-Key" not in seen[0].headers


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example/v1/compute/exports/a/content",
        "https://api.example/v1/compute/exports/a/content?token=x",
        "https://api.example/anything",
        "http://api.example/v1/downloads/a/files/b",
    ],
)
def test_authenticated_url_rejected_before_network(url, tmp_path):
    with client_for(lambda _: pytest.fail("must not leak key")) as client:
        with pytest.raises(ValueError):
            client.save(artifact(url, True), tmp_path / "x")


def test_authenticated_redirect_is_not_followed(tmp_path):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(302, headers={"Location": "https://evil.example/leak"})

    with client_for(handler) as client:
        with pytest.raises(APIError):
            client.save(
                artifact("https://api.example/v1/compute/exports/a/content", True), tmp_path / "x"
            )
    assert len(seen) == 1 and seen[0].url.host == "api.example"


@pytest.mark.parametrize("data", [b"short", ARCHIVE + b"extra", b"x" * len(ARCHIVE)])
def test_integrity_mismatch_never_publishes_final_file(data, tmp_path):
    with client_for(lambda _: httpx.Response(200, content=data)) as client:
        with pytest.raises(ValueError):
            client.save(artifact(), tmp_path / "x")
    assert not (tmp_path / "x").exists() and (tmp_path / "x.part").exists()


def test_budget_is_enforced_before_content_get(tmp_path):
    with client_for(lambda _: pytest.fail("budget must be checked first")) as client:
        with pytest.raises(ValueError):
            client.save(artifact(), tmp_path / "x", max_bytes=1)


def test_execution_gate_never_posts():
    client, api = mock_client()
    with client, pytest.raises(ExecutionClosed):
        client.submit_job({}, "request-1")
    assert ("POST", "/v1/compute/jobs") not in api.calls


@pytest.mark.parametrize(
    "changes",
    [
        {"start": "2026-01-01T00:00:00"},
        {"end": "2025-01-01T00:00:00Z"},
        {"start": "2026-01-01T00:00:00.001Z"},
    ],
)
def test_invalid_selection_is_local_error(changes):
    with pytest.raises(ValueError):
        selection_body(catalog_rows()[0] | changes)


def test_redaction():
    assert redact({"api_key": "hidden", "items": [{"url": "https://x?signature=hidden"}]}) == {
        "api_key": "[redacted]",
        "items": [{"url": "[redacted]"}],
    }


@pytest.mark.parametrize("budget", ["0", "-1", "NaN", "Infinity"])
def test_invalid_quote_budget_rejected_before_upload(budget):
    from datapanel_agent.workflows import prepare_quote

    with client_for(lambda _: pytest.fail("invalid budget must not create assets")) as client:
        with pytest.raises(ValueError):
            prepare_quote(client, catalog_rows()[0], max_credits=budget)


def test_source_limit_rejected_before_upload():
    with client_for(lambda _: pytest.fail("must validate locally"), allow_writes=True) as client:
        with pytest.raises(ValueError):
            client.upload_source("secret.env", "do not upload")
        with pytest.raises(ValueError):
            client.upload_source("x.py", "x" * 524289)


def test_private_export_size_boundary(tmp_path):
    seen = []

    def handler(request):
        seen.append(request.method)
        return httpx.Response(200, json={"size_bytes": 1_000_000_000, "logical_bytes": 1})

    with client_for(handler, allow_writes=True) as client, pytest.raises(ValueError):
        client.export_private("asset", tmp_path / "x")
    assert seen == ["GET"]


@pytest.mark.parametrize("path", ["/v1/downloads", "/v1/downloads/old/links"])
def test_retired_download_routes_never_reach_network(path):
    with client_for(
        lambda _: pytest.fail("retired routes must fail locally"), allow_writes=True
    ) as client:
        with pytest.raises(APIError) as error:
            client.request("GET", path)
        assert error.value.status == 410


def test_old_download_workflow_reports_migration(tmp_path):
    with client_for(lambda _: pytest.fail("retired workflow must fail locally")) as client:
        with pytest.raises(APIError, match="retired"):
            download(client, catalog_rows()[0], tmp_path)
        assert not list(tmp_path.iterdir())
