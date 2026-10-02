# Codex + DataPanel

The stdio bridge exposes twelve narrowly scoped tools and one prompt. Start with mock mode, which is credential-free. The bridge is local; it calls DataPanel's HTTPS API only when explicitly configured as live.

## Install and connect

```bash
python -m pip install -e ".[mcp]"
```

Add this configuration to your Codex MCP settings. Use absolute paths to the Python executable and repository; the executable must belong to the environment where you installed this package.

```toml
[mcp_servers.datapanel]
command = "/absolute/path/to/repo/.venv/bin/python"
args = ["-m", "datapanel_agent.mcp_server"]
cwd = "/absolute/path/to/repo"
env_vars = ["DATAPANEL_API_KEY"]
startup_timeout_sec = 15
tool_timeout_sec = 120

[mcp_servers.datapanel.env]
DATAPANEL_MODE = "mock"
DATAPANEL_ALLOW_WRITES = "0"
DATAPANEL_WORK_DIR = "/absolute/path/to/repo/work/mcp"
```

For Windows TOML, use literal strings such as `command = 'C:\path\repo\.venv\Scripts\python.exe'`. Keep the host consistent: a WSL executable needs a WSL Codex host. Do not paste a key into `env`, command arguments or chat. `env_vars` forwards the named value from the host process environment. Restart/reload the MCP connection after changing its environment.

Official setup sources: [Codex MCP](https://developers.openai.com/codex/mcp), [Codex skills](https://developers.openai.com/codex/skills), [MCP Python SDK v1](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x). This repo deliberately bounds `mcp<2` because its bridge uses the v1 FastMCP interface; the tested exact dependency set is in `requirements-lock.txt`.

## Tools

| Tool | Purpose | Side effect |
|---|---|---|
| `service_info` | Mode, write flag, published profiles | Read |
| `account_overview` | Account and compute ledger | Read |
| `search_catalog` | One filtered page | Read |
| `audit_coverage` | Bounded partition audit | Read |
| `plan_incremental` | Compare catalog IDs to verified IDs | Read |
| `data_access_policy` | Explain platform-side data access | Read |
| `compute_profiles` | Current profiles and allowlists | Read |
| `prepare_compute_quote` | Upload source, snapshot, capped quote | Creates private planning assets |
| `compute_job_status` | Read an owned job | Read |
| `cancel_compute_job` | Cancel selected job and read back | Cancellation request |
| `list_private_artifacts` | Owned metadata only | Read |
| `export_private_artifact` | Verify owned content through gateway | Export/content quota; local file |

The `research_data_brief` MCP prompt takes `market` and `symbol`. A repository skill is provided under `.agents/skills/datapanel-workflows/`. You can invoke it explicitly as `$datapanel-workflows` when working in this repository.

## Live operation

Change `DATAPANEL_MODE` to `live` and provide your own `DATAPANEL_API_KEY` in the host environment. Keep `DATAPANEL_ALLOW_WRITES=0` for account/catalog/coverage exploration. Set it to `1` when enabling authorized stateful workflows. These are adapter capabilities, not a substitute for the user's stated scope.

Call `service_info` first. Do not assume an enabled MCP means compute execution is enabled. No job-submit tool is exposed; the Python client includes an explicit, separately gated submit method for future integration.

Private exports poll at most three times per call. If still preparing, retry the same asset export. Inspect a retained `.part` before retrying interrupted content transfers. Market-data download tools have been removed; use snapshots for platform-side research and private exports for your results.

## Testing the integration

`tests/test_mcp.py` starts a separate MCP process and checks initialization, tool discovery, prompt retrieval, account/catalog reads, a verified private export and rejection of an escaping path. This is an actual protocol test, not a direct Python call pretending to be MCP. It does not claim a specific Codex model has been benchmarked.
