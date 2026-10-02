"""Reusable workflows shared by the CLI, standalone examples and MCP tools."""

import json
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from .client import APIError, ExecutionClosed, file_sha256, selection_body
from .mock import SOURCE


def coverage(items):
    """Audit published partitions per exact market/type/symbol; never invent availability."""
    groups = {}
    for row in items:
        key = (row["market"], row["data_type"], row["symbol"])
        groups.setdefault(key, []).append(row)
    report = []
    for key, rows in sorted(groups.items()):
        rows.sort(key=lambda r: datetime.fromisoformat(r["start"].replace("Z", "+00:00")))
        gaps, overlaps, cursor = [], [], None
        for row in rows:
            start = datetime.fromisoformat(row["start"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(row["end"].replace("Z", "+00:00"))
            if cursor is not None and start > cursor:
                gaps.append({"start": cursor.isoformat(), "end": start.isoformat()})
            if cursor is not None and start < cursor:
                overlaps.append(row["id"])
            cursor = max(cursor, end) if cursor else end
        report.append(
            {
                "market": key[0],
                "data_type": key[1],
                "symbol": key[2],
                "partitions": len(rows),
                "gaps": gaps,
                "overlaps": overlaps,
                "catalog_bytes": sum(r["size_bytes"] for r in rows),
            }
        )
    return report


def incremental_plan(items, completed_ids):
    return {
        "pending": [r for r in items if r["id"] not in set(completed_ids)],
        "rule": "Plan only. Mark an ID complete only after size and SHA256 verification.",
    }


def download(client, selection, work, **kwargs):
    """Compatibility error for the retired market-data export workflow."""
    raise APIError(410, "Market-data exports retired; use data-access, snapshot and private-export")


def prepare_quote(
    client,
    selection,
    *,
    content=SOURCE,
    filename="feature.py",
    profile="cpu-small",
    wall_seconds=60,
    max_credits="1",
    kind="features",
):
    budget = Decimal(max_credits)
    if not budget.is_finite() or budget <= 0:
        raise ValueError("Credit budget must be finite and positive")
    if type(wall_seconds) is not int or not 1 <= wall_seconds <= 43200:
        raise ValueError("Wall time must be 1..43200 integer seconds")
    if kind not in {"features", "train", "predict", "backtest", "build", "export"}:
        raise ValueError("Unknown compute planning kind")
    selection = selection_body(selection)
    profiles = client.profiles()
    if profile not in profiles["profiles"]:
        raise ValueError("Requested profile is not published")
    if wall_seconds > profiles["profiles"][profile]["max_wall_seconds"]:
        raise ValueError("Wall time exceeds the published profile limit")
    source = client.upload_source(filename, content)
    snapshot = client.snapshot(selection)
    body = {
        "workspace_id": "default",
        "kind": kind,
        "profile": profile,
        "source_artifact_id": source["id"],
        "dataset_snapshot_id": snapshot["id"],
        "max_wall_seconds": wall_seconds,
        "max_credits": str(max_credits),
    }
    quote = client.quote(body)
    # Enforce the caller's budget even if a server has an unlimited billing mode.
    if Decimal(quote["maximum_charged_credits"]) > Decimal(max_credits):
        raise ValueError("Quote exceeds the explicit charge budget")
    job = {
        "workspace_id": "default",
        "quote_id": quote["quote_id"],
        "source_artifact_id": source["id"],
        "dataset_snapshot_id": snapshot["id"],
        "resource_profile": profile,
        "kind": kind,
        "wall_seconds": wall_seconds,
    }
    return {
        "source": source,
        "snapshot": snapshot,
        "quote": quote,
        "job_request": job,
        "qualification": "RESEARCH_UNQUALIFIED",
    }


SCENARIOS = {
    "account": "Inspect subscription, quota and compute balance",
    "catalog": "Discover published partitions with bounded pagination",
    "coverage": "Find gaps and overlaps before requesting data",
    "data-access": "Inspect platform-side data access; market-data exports are retired",
    "incremental": "Plan missing partitions from a verified checkpoint",
    "source": "Upload a small private source module and verify its hash",
    "snapshot": "Freeze an authorized dataset selection",
    "quote": "Prepare an immutable resource quote with a hard credit cap",
    "execution-gate": "Respect the execution flag without submitting a job",
    "job-lifecycle": "Inspect a job; request cancellation and read it back",
    "private-export": "Export an owned artifact through the authenticated gateway",
    "research-brief": "Build an evidence-led research brief without claiming alpha",
}
WRITE_SCENARIOS = {"source", "snapshot", "quote", "private-export", "job-lifecycle"}


def run_scenario(name, client, work, *, selection=None, job_id=None, artifact_id=None):
    work = Path(work)
    if name == "data-access":
        return {
            "market_data_export": "retired",
            "data_location": "platform_compute",
            "next_steps": ["catalog", "snapshot", "quote", "private-export"],
            "profiles": client.profiles(),
        }
    if name == "account":
        return {"account": client.me(), "compute": client.usage()}
    if name == "job-lifecycle":
        if not job_id:
            raise ValueError("Supply an existing job_id owned by this account")
        before = client.job_status(job_id)
        requested = client.cancel_job(job_id)
        after = client.job_status(job_id)
        return {
            "before": before,
            "cancel_response": requested,
            "readback": after,
            "cancelled": after["status"] == "CANCELLED",
        }
    if name == "execution-gate":
        profiles = client.profiles()
        return {
            "profiles": profiles,
            "submitted": False,
            "decision": "execution_available"
            if profiles.get("execution_enabled") is True or profiles.get("execution_open") is True
            else "execution_closed",
        }
    if name == "private-export":
        if not artifact_id:
            raise ValueError("Supply an exportable artifact_id owned by this account")
        target = client.export_private(artifact_id, work / "private-artifact.bin")
        return {"path": str(target), "sha256": file_sha256(target), "status": "verified"}
    if name == "source":
        import hashlib

        asset = client.upload_source("feature.py", SOURCE)
        if asset["sha256"] != hashlib.sha256(SOURCE.encode()).hexdigest():
            raise ValueError("Uploaded source hash mismatch")
        return asset
    listing = client.catalog_pages(page_size=2, max_pages=10)
    if name == "catalog":
        return listing
    if name == "coverage":
        return {"coverage": coverage(listing["items"]), "truncated": listing["truncated"]}
    if name == "incremental":
        checkpoint = work / "completed.json"
        done = json.loads(checkpoint.read_text()) if checkpoint.exists() else []
        return {**incremental_plan(listing["items"], done), "truncated": listing["truncated"]}
    if name == "research-brief":
        result = {
            "qualification": "RESEARCH_UNQUALIFIED",
            "catalog": listing,
            "coverage": coverage(listing["items"]),
            "market_counts": dict(Counter(r["market"] for r in listing["items"])),
            "profiles": client.profiles(),
            "evidence": "Published metadata, not executed trades",
            "next_steps": [
                "Freeze held-out dates before model selection",
                "Test causal timestamps, fills, fees and funding",
                "Compare independent engines before promotion",
            ],
        }
        work.mkdir(parents=True, exist_ok=True)
        (work / "research-brief.md").write_text(
            "# Research brief\n\nStatus: RESEARCH_UNQUALIFIED\n\n"
            + f"Observed {len(listing['items'])} catalog partitions; truncated={listing['truncated']}.\n\n"
            + "No strategy was trained, backtested or qualified by this metadata workflow.\n\n"
            + "\n".join("- " + s for s in result["next_steps"])
            + "\n",
            encoding="utf-8",
        )
        return result
    if selection is None:
        raise ValueError("Choose an explicit selection from the published catalog")
    if name == "download":
        return download(client, selection, work)
    if name == "snapshot":
        return client.snapshot(selection)
    if name == "quote":
        return prepare_quote(client, selection)
    raise ValueError("Unknown scenario")


def guarded_submit(client, prepared, key):
    """Kept separate from quote preparation; no implicit remote execution."""
    try:
        return client.submit_job(prepared["job_request"], key)
    except ExecutionClosed:
        return {"submitted": False, "reason": "execution_closed"}
