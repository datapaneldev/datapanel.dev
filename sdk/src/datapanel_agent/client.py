"""Public API client. Credentials never enter URLs, saved manifests, or errors."""

import hashlib
import json
import math
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote, urlsplit

import httpx


class APIError(RuntimeError):
    def __init__(self, status, message, retry_after=None):
        self.status, self.retry_after = status, retry_after
        super().__init__(f"HTTP {status}: {message}")


class ExecutionClosed(RuntimeError):
    pass


def require_execution(profiles, profile, kind):
    """Honor explicit account allowlists; older APIs may omit these fields."""
    if not (profiles.get("execution_enabled") is True or profiles.get("execution_open") is True):
        raise ExecutionClosed("Service reports execution closed; do not submit")
    for field, value in (("enabled_profiles", profile), ("enabled_kinds", kind)):
        if field in profiles:
            enabled = profiles[field]
            if not isinstance(enabled, list) or value not in enabled:
                raise ExecutionClosed(f"Account does not enable the requested {field}")


def identifier(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", value):
        raise ValueError("Invalid identifier")
    return quote(value, safe="")


def selection_body(selection):
    keys = ("market", "data_type", "symbol", "start", "end")
    result = {key: selection[key] for key in keys}
    for key in keys[:3]:
        if not isinstance(result[key], str) or not 1 <= len(result[key]) <= 80:
            raise ValueError(f"Invalid {key}")
    dates = [datetime.fromisoformat(result[k].replace("Z", "+00:00")) for k in keys[3:]]
    if any(d.tzinfo is None or d.microsecond for d in dates) or dates[0] >= dates[1]:
        raise ValueError("Require timezone-aware whole-second [start,end), start < end")
    return result


def redact(value):
    """Remove credentials and signed links before tool output or persistence."""
    if isinstance(value, dict):
        return {
            k: (
                "[redacted]"
                if any(
                    s in k.lower()
                    for s in ("api_key", "token", "password", "secret", "signature", "url")
                )
                else redact(v)
            )
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


class DataPanel:
    def __init__(
        self,
        api_key="",
        base_url="https://datapanel.dev",
        *,
        transport=None,
        allow_writes=False,
        sleep=time.sleep,
        attempts=3,
    ):
        parsed = urlsplit(base_url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in ("", "/")
        ):
            raise ValueError("Base URL must be an HTTPS origin")
        self.base = base_url.rstrip("/")
        self._key = api_key
        self.allow_writes, self.sleep, self.attempts = allow_writes, sleep, attempts
        # No default key header: object-store downloads must never inherit it.
        self.http = httpx.Client(transport=transport, timeout=30, follow_redirects=False)

    def close(self):
        self.http.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def request(self, method, path, body=None, *, params=None, idempotency_key=None):
        if path == "/v1/downloads" or path.startswith("/v1/downloads/"):
            raise APIError(
                410, "Market-data exports retired; use compute snapshots and private results"
            )
        if not path.startswith("/v1/") or "?" in path or "#" in path or ".." in path:
            raise ValueError("Use a public /v1/ path and separate query parameters")
        if method != "GET" and not self.allow_writes:
            raise PermissionError(
                "This client is read-only; authorize the workflow before enabling writes"
            )
        headers = {"Accept": "application/json"}
        if self._key:
            headers["X-API-Key"] = self._key
        if idempotency_key:
            if not re.fullmatch(r"[A-Za-z0-9_-]{8,100}", idempotency_key):
                raise ValueError("Idempotency key must be 8..100 safe characters")
            headers["Idempotency-Key"] = idempotency_key
        can_retry = method == "GET" or bool(idempotency_key)
        for attempt in range(self.attempts):
            try:
                response = self.http.request(
                    method, self.base + path, json=body, params=params, headers=headers
                )
            except httpx.TransportError:
                if can_retry and attempt + 1 < self.attempts:
                    self.sleep(2**attempt)
                    continue
                raise APIError(
                    0, "Transport failed; retain your request manifest and idempotency key"
                ) from None
            if 200 <= response.status_code < 300:
                try:
                    return response.json()
                except ValueError:
                    raise APIError(response.status_code, "Expected JSON response") from None
            delay = self._retry_after(response.headers.get("Retry-After"))
            if (
                can_retry
                and response.status_code in (429, 502, 503, 504)
                and attempt + 1 < self.attempts
                and (delay is None or delay <= 30)
            ):
                self.sleep(delay if delay is not None else 2**attempt)
                continue
            messages = {
                401: "Invalid or missing API key",
                402: "Insufficient quota or credits",
                403: "Access denied",
                404: "Resource unavailable for this account",
                409: "Conflict; inspect coverage or current task state",
                410: "Resource expired",
                413: "Request exceeds service limits",
                422: "Request does not match the current API contract",
                429: "Rate or quota limit; honor Retry-After",
                503: "Service or execution is unavailable",
            }
            # Do not reflect upstream bodies: proxies may echo a key or signed URL.
            raise APIError(
                response.status_code,
                messages.get(response.status_code, "Request failed; inspect the service status"),
                delay,
            )
        raise AssertionError("Unreachable")

    @staticmethod
    def _retry_after(value):
        if not value:
            return None
        try:
            delay = float(value)
        except ValueError:
            try:
                delay = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
            except (ValueError, TypeError, OverflowError):
                return None
        return max(0, delay) if math.isfinite(delay) else None

    def me(self):
        return self.request("GET", "/v1/me")

    def plans(self):
        return self.request("GET", "/v1/plans")

    def catalog(self, *, limit=100, offset=0, **filters):
        if not 1 <= limit <= 500 or offset < 0 or set(filters) - {"market", "data_type", "symbol"}:
            raise ValueError("Invalid catalog pagination or filters")
        return self.request(
            "GET", "/v1/catalog", params={"limit": limit, "offset": offset, **filters}
        )

    def catalog_pages(self, *, max_pages=10, page_size=100, **filters):
        items = []
        for page in range(max_pages):
            rows = self.catalog(limit=page_size, offset=page * page_size, **filters)["items"]
            items.extend(rows)
            if len(rows) < page_size:
                return {"items": items, "truncated": False, "pages": page + 1}
        return {"items": items, "truncated": True, "pages": max_pages}

    def submit_download(self, selection, key):
        return self.request("POST", "/v1/downloads", selection_body(selection), idempotency_key=key)

    def download_status(self, task_id):
        return self.request("GET", f"/v1/downloads/{identifier(task_id)}")

    def download_links(self, task_id):
        return self.request("GET", f"/v1/downloads/{identifier(task_id)}/links")

    def wait_download(self, task_id, *, max_polls=60, interval=5):
        for poll in range(max_polls):
            task = self.download_status(task_id)
            if task["status"] == "ready":
                return task
            if task["status"] in {"failed", "cancelled", "expired"}:
                raise RuntimeError("Download ended: " + task["status"])
            if poll + 1 < max_polls:
                self.sleep(interval)
        raise TimeoutError("Poll budget exhausted; resume the same task_id without resubmitting")

    def save(self, artifact, target, *, max_bytes=1_000_000_000):
        """Stream, bound, verify, atomically rename. Never auto-extract an archive."""
        size, digest = artifact["size_bytes"], artifact["sha256"]
        if (
            type(size) is not int
            or not 0 <= size <= max_bytes
            or not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
        ):
            raise ValueError("Valid SHA256 and size within the local byte budget are required")
        url = urlsplit(artifact["url"])
        if (
            url.scheme != "https"
            or not url.hostname
            or url.username
            or url.password
            or url.fragment
        ):
            raise ValueError("Artifact URL must use HTTPS without userinfo or fragment")
        headers = {}
        if artifact.get("requires_api_key"):
            base = urlsplit(self.base)
            if (
                (url.scheme, url.netloc) != (base.scheme, base.netloc)
                or url.query
                or not re.fullmatch(
                    r"/v1/compute/exports/[A-Za-z0-9_-]+/content",
                    url.path,
                )
            ):
                raise ValueError(
                    "Refusing to send API key outside the authenticated content gateway"
                )
            headers["X-API-Key"] = self._key
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.stat().st_size == size and file_sha256(target) == digest:
                return target
            raise FileExistsError("Destination differs; choose a new local filename")
        part = target.with_name(target.name + ".part")
        sha, received = hashlib.sha256(), 0
        try:
            # Exclusive creation also stops accidental concurrent downloads to the same path.
            with (
                part.open("xb") as output,
                self.http.stream("GET", artifact["url"], headers=headers) as r,
            ):
                if r.status_code != 200:
                    raise APIError(
                        r.status_code, "Content download refused; redirects are not followed"
                    )
                for chunk in r.iter_bytes(65536):
                    received += len(chunk)
                    if received > size:
                        raise ValueError("Response exceeds declared size")
                    sha.update(chunk)
                    output.write(chunk)
        except httpx.TransportError:
            raise APIError(
                0, "Download interrupted; .part retained; a new GET may consume quota again"
            ) from None
        if received != size or sha.hexdigest() != digest:
            raise ValueError("Content integrity mismatch; .part retained for inspection")
        part.replace(target)
        return target

    def gpu_input(self, payload):
        from .gpu_template import decode, encode

        return self.request("POST", "/v1/compute/gpu-template-jobs/inputs", decode(encode(payload)))

    def gpu_quote(self, input_artifact_id, max_credits):
        return self.request(
            "POST",
            "/v1/compute/gpu-template-jobs/quotes",
            {
                "input_artifact_id": identifier(input_artifact_id),
                "max_credits": str(max_credits),
            },
        )

    def gpu_submit(self, body, key):
        """Explicit fixed-template submission; admission is separate from generic CPU profiles."""
        return self.request("POST", "/v1/compute/gpu-template-jobs", body, idempotency_key=key)

    def gpu_status(self, job_id):
        return self.request("GET", f"/v1/compute/gpu-template-jobs/{identifier(job_id)}")

    def gpu_cancel(self, job_id):
        return self.request("POST", f"/v1/compute/gpu-template-jobs/{identifier(job_id)}/cancel")

    def profiles(self):
        return self.request("GET", "/v1/compute/profiles")

    def usage(self):
        return self.request("GET", "/v1/compute/usage")

    def upload_source(self, filename, content):
        if (
            not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}\.(py|cpp|h|hpp|json|csv|txt)", filename)
            or not content
            or len(content) > 524288
            or len(content.encode()) > 1048576
        ):
            raise ValueError("Source filename/content exceeds the API contract")
        return self.request(
            "POST", "/v1/compute/sources", {"filename": filename, "content": content}
        )

    def snapshot(self, selection):
        return self.request("POST", "/v1/compute/data-selections", selection_body(selection))

    def quote(self, body):
        return self.request("POST", "/v1/compute/quotes", body)

    def submit_job(self, body, key):
        profiles = self.profiles()
        require_execution(profiles, body.get("resource_profile"), body.get("kind"))
        return self.request("POST", "/v1/compute/jobs", body, idempotency_key=key)

    def job_status(self, job_id):
        return self.request("GET", f"/v1/compute/jobs/{identifier(job_id)}")

    def cancel_job(self, job_id):
        return self.request("POST", f"/v1/compute/jobs/{identifier(job_id)}/cancel")

    def artifacts(self, limit=20, offset=0):
        return self.request(
            "GET", "/v1/compute/artifacts", params={"limit": limit, "offset": offset}
        )

    def export_private(self, asset_id, target, *, max_polls=60, interval=5):
        path = f"/v1/compute/artifacts/{identifier(asset_id)}"
        asset = self.request("GET", path)
        if max(asset["size_bytes"], asset["logical_bytes"]) >= 1_000_000_000:
            raise ValueError("Private export must be strictly smaller than 1 GB")
        export = self.request("POST", path + "/exports")
        path = f"/v1/compute/exports/{identifier(export['export_id'])}"
        for poll in range(max_polls):
            status = self.request("GET", path)
            if status["status"] == "ready":
                return self.save(
                    {**asset, "url": self.base + path + "/content", "requires_api_key": True},
                    target,
                )
            if status["status"] in {"failed", "expired"}:
                raise RuntimeError("Private export ended: " + status["status"])
            if poll + 1 < max_polls:
                self.sleep(interval)
        raise TimeoutError("Export still preparing; retry reuses the active server-side export")


def file_sha256(path):
    sha = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def save_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(redact(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    tmp.replace(path)
