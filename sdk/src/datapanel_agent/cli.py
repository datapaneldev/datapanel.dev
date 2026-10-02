"""Runnable offline cookbook. Live mode requires an explicit mode and own API key."""

import argparse
import json
import os
import sys
from pathlib import Path

from .client import APIError, DataPanel, redact, save_json
from .mock import SOURCE, catalog_rows, mock_client
from .workflows import SCENARIOS, WRITE_SCENARIOS, run_scenario


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=["all", *SCENARIOS])
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    parser.add_argument("--work-dir", type=Path, default=Path("work"))
    parser.add_argument(
        "--selection", type=Path, help="JSON with market,data_type,symbol,start,end"
    )
    parser.add_argument("--job-id")
    parser.add_argument("--artifact-id")
    parser.add_argument("--allow-writes", action="store_true")
    args = parser.parse_args(argv)
    if args.mode == "live" and args.scenario == "all":
        parser.error("Run live scenarios individually with explicit inputs")
    if args.mode == "live" and args.scenario in WRITE_SCENARIOS and not args.allow_writes:
        parser.error("This live scenario changes account state; use --allow-writes when authorized")
    if args.mode == "mock":
        client, api = mock_client()
        selection = catalog_rows()[0]
    else:
        key = os.environ.get("DATAPANEL_API_KEY", "")
        if not key:
            parser.error("Set DATAPANEL_API_KEY in the process environment")
        client = DataPanel(
            key,
            os.getenv("DATAPANEL_BASE_URL", "https://datapanel.dev"),
            allow_writes=args.allow_writes,
        )
        selection = None
    if args.selection:
        selection = json.loads(args.selection.read_text(encoding="utf-8"))
    names = list(SCENARIOS) if args.scenario == "all" else [args.scenario]
    failed = False
    with client:
        for name in names:
            job_id, artifact_id = args.job_id, args.artifact_id
            if args.mode == "mock":
                api.execution_enabled = name == "job-lifecycle"
                job_id = "demo_job"
                if name == "private-export":
                    artifact_id = client.upload_source("feature.py", SOURCE)["id"]
            try:
                result = run_scenario(
                    name,
                    client,
                    args.work_dir / args.mode / name,
                    selection=selection,
                    job_id=job_id,
                    artifact_id=artifact_id,
                )
                record = {"scenario": name, "mode": args.mode, "status": "passed", "result": result}
            except (APIError, ValueError, RuntimeError, OSError) as exc:
                failed = True
                record = {
                    "scenario": name,
                    "mode": args.mode,
                    "status": "failed",
                    "error": str(exc),
                }
            save_json(args.work_dir / args.mode / name / "result.json", record)
            print(json.dumps(redact(record), ensure_ascii=False))
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
