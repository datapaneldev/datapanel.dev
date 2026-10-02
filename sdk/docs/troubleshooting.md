# Troubleshooting

| Observation | Meaning | Next step |
|---|---|---|
| `ModuleNotFoundError: datapanel_agent` | Wrong Python environment | Install `-e .` into the executable actually running the example |
| `No module named mcp` | MCP extra absent | Install `-e ".[mcp]"`; verify absolute executable in Codex |
| MCP starts but tools do not appear | Host/config/startup mismatch | Check configured host, restart the connection and inspect stderr; stdout is protocol-only |
| `DATAPANEL_API_KEY` missing | Live mode has no forwarded key | Set the parent process environment; do not paste the key into chat |
| `PermissionError: read-only` | Live write capability is off | Enable only for the user's authorized stateful workflow |
| HTTP 401/403 | Key/access issue | Check own account and entitlement; do not retry using another identity |
| HTTP 402 | Quota or credit constraint | Read account/usage; stop the stateful workflow |
| HTTP 409 | Coverage gap, conflict, state issue | Inspect selection and existing task; do not blindly resubmit |
| HTTP 422 | Request/schema/limit mismatch | Compare exact field names and published profiles with the contract |
| HTTP 429 | Rate or quota limit | Honor Retry-After; avoid concurrent polling loops |
| HTTP 503 for compute | Execution/service unavailable | Record the capability boundary; do not circumvent it |
| Download remains queued | Export preparation not finished | Resume same manifest; contact service operator if worker is unavailable |
| `.part` exists | Prior incomplete or rejected download | Inspect, explicitly relocate it if retrying; authenticated retries can cost quota |
| SHA256 mismatch | Untrusted/incomplete content | Keep `.part`, no final file, report metadata and task ID without credentials |
| `truncated=true` | The page budget ended | Narrow filters or consciously extend it; do not claim full catalog coverage |
| Cancel response is successful but status is `CANCEL_REQUESTED` | Cancellation is asynchronous | Keep reporting pending; independently read until a terminal state |

For a service issue, provide a minimal sanitized reproduction: method and path template, request fields without credentials, status, timestamps, task/asset ID where appropriate, and expected versus actual behavior. Never post API keys, signed URLs, account email or full private source to a public issue.

The offline mock retains server state only within a single process. Local manifests survive, but restarting a *standalone mock server* resets its synthetic state. For a fresh offline demonstration use a fresh `--work-dir`. Live manifests always refer to real server state.
