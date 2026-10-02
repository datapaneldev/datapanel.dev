# Public API contract used by the cookbook


Source of truth for consumers: [DataPanel developer documentation](https://datapanel.dev/developers.html). The adapter contains no admin, storage-node or execution-host configuration.

## Authentication and transport

- User API calls use `X-API-Key` over HTTPS.
- Requests never follow redirects. Signed object links use a separate request without the API key.
- Authenticated content requires the exact API origin, a fixed allowed content path, no query and no fragment.
- Untrusted server error bodies are not echoed into tool output. Errors preserve status and Retry-After.
- Only GETs and requests with an explicit supported idempotency key are automatically retried; attempts are bounded. A Retry-After longer than 30 seconds is returned to the caller instead of hidden sleeping.

## Endpoints

| Method / route | Input | Used by |
|---|---|---|
| `GET /v1/plans` | Public | Python client |
| `GET /v1/me` | User key | Account |
| `GET /v1/catalog` | market, data_type, symbol, limit 1..500, offset | Discovery/audit/plan |
| `GET /v1/compute/profiles` | User key | Capability discovery |
| `GET /v1/compute/usage` | User key with access | Credits/ledger |
| `POST /v1/compute/sources` | filename, content | Private source |
| `POST /v1/compute/data-selections` | Selection | Dataset snapshot |
| `POST /v1/compute/quotes` | Quote request below | Planning |
| `POST /v1/compute/jobs` | Job request + `Idempotency-Key` | Explicit Python method only |
| `GET /v1/compute/jobs/{id}` | Owned job ID | Status |
| `POST /v1/compute/jobs/{id}/cancel` | Owned job ID | Cancel/readback |
| `GET /v1/compute/artifacts` | limit 1..100, offset | Owned metadata |
| `GET /v1/compute/artifacts/{id}` | Owned asset ID | Export preflight |
| `POST /v1/compute/artifacts/{id}/exports` | Owned sealed asset | Private export |
| `GET /v1/compute/exports/{id}` | Owned export ID | Export status |
| `GET /v1/compute/exports/{id}/content` | Key | Private bytes |

## Selection

```python
selection = {
    "market": row["market"],
    "data_type": row["data_type"],
    "symbol": row["symbol"],
    "start": row["start"],
    "end": row["end"],
}
```

Require timezone-aware whole-second times and `start < end`, interval `[start,end)`. Catalog format may be `csv`, `csv.gz`, `parquet` or `opaque`. A `sliceable=false` row should be requested on its full partition boundaries. The server rejects uncovered ranges and ambiguous overlaps.

## Market-data access

Historical market-data exports are retired. Catalog partitions are inputs to platform-side snapshots and compute. Only your own code and research results are eligible for private artifact export. The client rejects retired download paths before sending a request.

## Fixed GPU template API

`POST /v1/compute/gpu-template-jobs/inputs` uploads bounded `mlp-regression-v1` JSON. `POST .../quotes` takes `input_artifact_id` and `max_credits`. Explicit `POST /v1/compute/gpu-template-jobs` takes `quote_id`, `input_artifact_id`, `input_sha256`, `template` and an `Idempotency-Key`. `GET .../{job_id}` and `POST .../{job_id}/cancel` use this separate job namespace. Generic CPU profiles do not determine this endpoint's admission. See [GPU input and quoting](gpu-template.zh-CN.md).

The current API also publishes research sessions, session training/checkpoints/campaigns, reports and AI chat. These are separate capabilities, not automatically enabled by this cookbook's generic training wrapper. Read the current [OpenAPI](https://datapanel.dev/openapi.json) before integrating them.

## Quote versus job

```python
quote_request = {
    "workspace_id": "default",
    "kind": "features",  # features/train/predict/backtest/build/export
    "profile": "cpu-small",  # discover live profiles first
    "source_artifact_id": source_id,
    "dataset_snapshot_id": snapshot_id,
    "max_wall_seconds": 60,
    "max_credits": "1",  # decimal string, not binary float accounting
}
job_request = {
    "workspace_id": "default",
    "quote_id": quote_id,
    "source_artifact_id": source_id,
    "dataset_snapshot_id": snapshot_id,
    "resource_profile": "cpu-small",
    "kind": "features",
    "wall_seconds": 60,
}
```

Field names differ intentionally: `profile/max_wall_seconds` in a quote; `resource_profile/wall_seconds` in a job. Quote responses identify the rate version, expiry and maximum metered/charged credits. Current generic profiles are returned as a map. Inspect the current service before assuming another schema.

## Limits and meaning

- Source: supported filenames, at most 524,288 characters and 1 MiB UTF-8 bytes.
- Private export: both logical and physical size strictly below 1,000,000,000 bytes.
- Dataset snapshot hashes identify service-side selection/manifests. They are not file-content hashes.
- `CANCEL_REQUESTED` is intermediate. Confirm the subsequent status independently.
- `execution_enabled=false` or `execution_open=false` is a real capability boundary. Do not use another endpoint or infrastructure path to bypass it.
- API fields describing success do not establish strategy validity, fill fidelity or OOS performance.

## Sessions and result safety

See [Sessions, jobs and safe result retrieval](security-and-sessions.md) for account-key scope, seven-day session-training defaults, namespace-specific polling, uncertain submissions, export limits and safe handling of downloaded files.
