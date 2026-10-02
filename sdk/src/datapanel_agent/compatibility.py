"""Read-only check of the public routes/request fields used by this cookbook."""

import argparse
import hashlib
import json
from pathlib import Path

import httpx

ROUTES = {
    "/v1/plans": ("get",),
    "/v1/me": ("get",),
    "/v1/catalog": ("get",),
    "/v1/compute/profiles": ("get",),
    "/v1/compute/usage": ("get",),
    "/v1/compute/sources": ("post",),
    "/v1/compute/data-selections": ("post",),
    "/v1/compute/quotes": ("post",),
    "/v1/compute/jobs": ("post",),
    "/v1/compute/jobs/{job_id}": ("get",),
    "/v1/compute/jobs/{job_id}/cancel": ("post",),
    "/v1/compute/artifacts": ("get",),
    "/v1/compute/artifacts/{artifact_id}": ("get",),
    "/v1/compute/artifacts/{artifact_id}/exports": ("post",),
    "/v1/compute/exports/{export_id}": ("get",),
    "/v1/compute/exports/{export_id}/content": ("get",),
    "/v1/compute/gpu-template-jobs/inputs": ("post",),
    "/v1/compute/gpu-template-jobs/quotes": ("post",),
    "/v1/compute/gpu-template-jobs": ("post",),
    "/v1/compute/gpu-template-jobs/{job_id}": ("get",),
    "/v1/compute/gpu-template-jobs/{job_id}/cancel": ("post",),
}
FIELDS = {
    "/v1/compute/sources": {"filename", "content"},
    "/v1/compute/data-selections": {"market", "data_type", "symbol", "start", "end"},
    "/v1/compute/quotes": {
        "workspace_id",
        "kind",
        "profile",
        "source_artifact_id",
        "dataset_snapshot_id",
        "max_wall_seconds",
        "max_credits",
    },
    "/v1/compute/jobs": {
        "workspace_id",
        "quote_id",
        "source_artifact_id",
        "dataset_snapshot_id",
        "resource_profile",
        "kind",
        "wall_seconds",
    },
    "/v1/compute/gpu-template-jobs/quotes": {"input_artifact_id", "max_credits"},
    "/v1/compute/gpu-template-jobs": {"quote_id", "input_artifact_id", "input_sha256", "template"},
}
LIMIT = 4 * 1024**2


def check(document):
    problems = []
    paths = document.get("paths", {})
    for path, methods in ROUTES.items():
        for method in methods:
            if method not in paths.get(path, {}):
                problems.append(f"Missing route: {method.upper()} {path}")
    for path, supplied in FIELDS.items():
        try:
            schema = paths[path]["post"]["requestBody"]["content"]["application/json"]["schema"]
            if "$ref" in schema:
                prefix = "#/components/schemas/"
                if not schema["$ref"].startswith(prefix):
                    raise ValueError("Unsupported schema reference")
                schema = document["components"]["schemas"][schema["$ref"][len(prefix) :]]
            required, accepted = set(schema.get("required", [])), set(schema["properties"])
            if required - supplied or supplied - accepted:
                problems.append(f"Request fields changed: {path}")
        except (KeyError, TypeError, ValueError):
            problems.append(f"Cannot verify request schema: {path}")
    return {
        "compatible": not problems,
        "problems": problems,
        "routes_checked": len(ROUTES),
        "scope": "Routes and request field names only; not account access or runtime acceptance",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, help="Use a previously downloaded OpenAPI JSON")
    args = parser.parse_args(argv)
    try:
        if args.schema:
            with args.schema.open("rb") as stream:
                raw = stream.read(LIMIT + 1)
        else:
            raw = bytearray()
            with httpx.stream(
                "GET", "https://datapanel.dev/openapi.json", timeout=30, follow_redirects=False
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_bytes():
                    raw.extend(chunk)
                    if len(raw) > LIMIT:
                        break
        if len(raw) > LIMIT:
            raise ValueError("Schema exceeds 4 MiB")
        result = check(json.loads(raw))
        result["schema_sha256"] = hashlib.sha256(raw).hexdigest()
    except (ValueError, OSError, httpx.HTTPError, TypeError, AttributeError):
        parser.exit(2, "Unable to retrieve or parse the public OpenAPI document\n")
    print(json.dumps(result, indent=2))
    return 0 if result["compatible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
