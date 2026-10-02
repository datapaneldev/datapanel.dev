import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_real_stdio_mcp_session(tmp_path):
    """Exercise protocol initialization, discovery, a prompt, read and write tools."""

    async def run():
        server = StdioServerParameters(
            command=sys.executable,
            args=["-m", "datapanel_agent.mcp_server"],
            env={**os.environ, "DATAPANEL_MODE": "mock", "DATAPANEL_WORK_DIR": str(tmp_path)},
        )
        async with stdio_client(server) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()
            names = {t.name for t in listing.tools}
            assert len(names) == 12
            for name in ("service_info", "account_overview", "search_catalog"):
                result = await session.call_tool(name, {})
                assert not result.isError
            prompt = await session.get_prompt(
                "research_data_brief", {"market": "demo-exchange", "symbol": "BTCUSDT"}
            )
            assert prompt.messages
            assert "download_partition" not in names and "download_status" not in names
            for name in ("data_access_policy", "compute_profiles"):
                assert not (await session.call_tool(name, {})).isError
            for name, arguments in [
                (
                    "audit_coverage",
                    {"market": "demo-exchange", "data_type": "trades", "symbol": "BTCUSDT"},
                ),
                (
                    "plan_incremental",
                    {
                        "market": "demo-exchange",
                        "data_type": "trades",
                        "symbol": "BTCUSDT",
                        "completed_ids": [],
                    },
                ),
                ("list_private_artifacts", {}),
            ]:
                assert not (await session.call_tool(name, arguments)).isError
            quote = await session.call_tool(
                "prepare_compute_quote",
                {
                    "market": "demo-exchange",
                    "data_type": "trades",
                    "symbol": "BTCUSDT",
                    "start": "2026-01-01T00:00:00Z",
                    "end": "2026-01-02T00:00:00Z",
                    "filename": "mcp_feature.py",
                    "source": "def feature(): return 1\n",
                },
            )
            assert not quote.isError
            payload = json.loads(next(c.text for c in quote.content if c.type == "text"))
            exported = await session.call_tool(
                "export_private_artifact",
                {"artifact_id": payload["source"]["id"], "filename": "mcp-private.bin"},
            )
            assert not exported.isError
            # All twelve tools are called; the closed execution tools must return errors.
            for name in ("compute_job_status", "cancel_compute_job"):
                closed = await session.call_tool(name, {"job_id": "demo_job"})
                assert closed.isError
                assert "503" in " ".join(c.text for c in closed.content if c.type == "text")
            rejected = await session.call_tool(
                "export_private_artifact",
                {"artifact_id": payload["source"]["id"], "filename": "../escape"},
            )
            assert rejected.isError

    asyncio.run(run())
