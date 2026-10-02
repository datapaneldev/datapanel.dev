"""Deterministic, in-process API simulator. Every byte and metric is synthetic."""

import hashlib
import json
import time

import httpx

from .client import DataPanel

SOURCE = (
    "def feature(previous_close, current_close):\n    return current_close / previous_close - 1\n"
)
ARCHIVE = b"SYNTHETIC DEMO ARCHIVE\nNo licensed market data.\n"


def catalog_rows():
    return [
        {
            "id": f"demo_partition_{day}",
            "market": "demo-exchange",
            "data_type": "trades",
            "symbol": "BTCUSDT",
            "format": "csv.gz",
            "size_bytes": 1024,
            "start": f"2026-01-0{day}T00:00:00Z",
            "end": f"2026-01-0{day + 1}T00:00:00Z",
            "sliceable": True,
        }
        for day in (1, 2, 4)
    ]


class MockAPI:
    def __init__(self):
        self.calls, self.downloads, self.keys, self.assets, self.exports = [], {}, {}, {}, {}
        self.execution_enabled = False
        self.job = {"job_id": "demo_job", "status": "RUNNING", "billing_state": "PENDING"}

    def response(self, code=200, **body):
        return httpx.Response(code, json=body)

    def __call__(self, request):
        path, method = request.url.path, request.method
        body = json.loads(request.content) if request.content else {}
        self.calls.append((method, path))
        if path == "/v1/plans":
            return self.response(plans=[{"id": "standard", "compute_credits": 500}])
        if request.headers.get("X-API-Key") != "demo-only-not-a-real-key":
            return self.response(401, detail="Missing test credential")
        if path == "/v1/me":
            return self.response(
                plan_id="standard",
                active=True,
                requests_per_minute=60,
                usage={"used_bytes": 1024, "reserved_bytes": 0},
                compute_credits=500,
                access_tier="paid",
            )
        if path == "/v1/catalog":
            rows = catalog_rows()
            for key in ("market", "data_type", "symbol"):
                if key in request.url.params:
                    rows = [r for r in rows if r[key] == request.url.params[key]]
            offset, limit = (
                int(request.url.params.get("offset", 0)),
                int(request.url.params.get("limit", 100)),
            )
            return self.response(items=rows[offset : offset + limit], offset=offset, limit=limit)
        if path == "/v1/compute/profiles":
            return self.response(
                execution_enabled=self.execution_enabled,
                profiles={
                    "cpu-small": {
                        "cpu": 4,
                        "ram_gib": 8,
                        "gpu_count": 0,
                        "gpu_type": None,
                        "max_wall_seconds": 7200,
                    }
                },
            )
        if path == "/v1/compute/usage":
            return self.response(
                execution_enabled=False,
                ledger_unit="microcredit",
                amount=500000000,
                reserved=0,
                charged=0,
                lifetime=[],
            )
        if path in ("/v1/compute/sources", "/v1/compute/data-selections"):
            source = path.endswith("sources")
            content = body["content"].encode() if source else json.dumps(body).encode()
            asset_id = f"demo_asset_{len(self.assets) + 1}"
            asset = {
                "id": asset_id,
                "name": body.get("filename", "dataset-snapshot.json"),
                "kind": "source" if source else "dataset_snapshot",
                "size_bytes": len(content),
                "logical_bytes": len(content),
                "status": "sealed",
                "created": int(time.time()),
                "expires": None,
                "sha256": hashlib.sha256(content).hexdigest(),
            }
            self.assets[asset_id] = (asset, content)
            return self.response(**asset)
        if path == "/v1/compute/quotes":
            for field in ("source_artifact_id", "dataset_snapshot_id"):
                if body[field] not in self.assets:
                    return self.response(404, detail="Not owned")
            return self.response(
                quote_id="demo_quote",
                expires=int(time.time()) + 900,
                billing_mode="credits",
                rate_version="demo-v1",
                maximum_metered_credits="0.066667",
                maximum_charged_credits="0.066667",
                execution_enabled=False,
            )
        if path == "/v1/compute/artifacts":
            return self.response(items=[v[0] for v in self.assets.values()])
        if path.startswith("/v1/compute/artifacts/"):
            asset_id = path.split("/")[4]
            if asset_id not in self.assets:
                return self.response(404, detail="Not found")
            if path.endswith("/exports"):
                export_id = "demo_export_" + asset_id
                self.exports[export_id] = asset_id
                return self.response(
                    export_id=export_id, status="queued", expires=int(time.time()) + 600
                )
            return self.response(**self.assets[asset_id][0])
        if path.startswith("/v1/compute/exports/"):
            export_id = path.split("/")[4]
            if export_id not in self.exports:
                return self.response(404, detail="Not found")
            if path.endswith("/content"):
                return httpx.Response(200, content=self.assets[self.exports[export_id]][1])
            return self.response(
                export_id=export_id, status="ready", expires=int(time.time()) + 600
            )
        if path.startswith("/v1/compute/jobs"):
            if not self.execution_enabled:
                return self.response(503, detail="Execution closed")
            if path.endswith("/cancel"):
                self.job["status"] = "CANCEL_REQUESTED"
            return self.response(**self.job)
        return self.response(404, detail="Unknown mock route")


def mock_client():
    api = MockAPI()
    client = DataPanel(
        "demo-only-not-a-real-key",
        "https://demo.datapanel.invalid",
        transport=httpx.MockTransport(api),
        allow_writes=True,
        sleep=lambda _: None,
    )
    return client, api
