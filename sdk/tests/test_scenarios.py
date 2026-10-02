import json

import pytest

from datapanel_agent.cli import main
from datapanel_agent.mock import SOURCE, catalog_rows, mock_client
from datapanel_agent.workflows import SCENARIOS, coverage, incremental_plan, run_scenario


@pytest.mark.parametrize("scenario", list(SCENARIOS))
def test_each_scenario(scenario, tmp_path):
    client, api = mock_client()
    api.execution_enabled = scenario == "job-lifecycle"
    with client:
        asset_id = (
            client.upload_source("feature.py", SOURCE)["id"]
            if scenario == "private-export"
            else None
        )
        result = run_scenario(
            scenario,
            client,
            tmp_path,
            selection=catalog_rows()[0],
            job_id="demo_job",
            artifact_id=asset_id,
        )
    assert result
    if scenario == "data-access":
        assert result["market_data_export"] == "retired"
    elif scenario == "coverage":
        assert len(result["coverage"][0]["gaps"]) == 1
    elif scenario == "execution-gate":
        assert result["submitted"] is False and result["decision"] == "execution_closed"
    elif scenario == "job-lifecycle":
        assert result["readback"]["status"] == "CANCEL_REQUESTED"
        assert result["cancelled"] is False
    elif scenario == "research-brief":
        assert result["qualification"] == "RESEARCH_UNQUALIFIED"
        assert (tmp_path / "research-brief.md").exists()


def test_all_cli_scenarios(tmp_path, capsys):
    assert main(["all", "--work-dir", str(tmp_path)]) == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert len(rows) == len(SCENARIOS) and all(r["status"] == "passed" for r in rows)
    assert all(r["mode"] == "mock" for r in rows)


def test_catalog_truncation_is_visible():
    client, _ = mock_client()
    with client:
        result = client.catalog_pages(page_size=1, max_pages=1)
    assert result["truncated"] is True and len(result["items"]) == 1


def test_coverage_and_incremental_do_not_hide_gaps():
    rows = catalog_rows()
    audited = coverage(rows)
    assert len(audited[0]["gaps"]) == 1
    assert not audited[0]["overlaps"]
    assert len(coverage(rows + [rows[0]])[0]["overlaps"]) == 1
    assert len(incremental_plan(rows, [rows[0]["id"]])["pending"]) == 2


def test_live_all_is_rejected_without_requests():
    with pytest.raises(SystemExit):
        main(["all", "--mode", "live"])
