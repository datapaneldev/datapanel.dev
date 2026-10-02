# Security and privacy

Report security issues privately to the repository maintainer using GitHub's private reporting feature when available. If that facility is not enabled, request a private contact channel without publishing exploit details or credentials.

This is a reference integration, not an audited security boundary. The host process can read its environment key. Use a dedicated account/key with suitable scope and revoke it if exposed. The bridge does not isolate arbitrary user code and provides no execution sandbox.

The client deliberately does not inherit API headers for object-store downloads, does not follow redirects, and restricts authenticated content to the same origin and known gateway paths. It streams with a size limit and verifies SHA256 before finalizing a file. It never auto-extracts or executes downloaded archives.

MCP tool annotations describe expected side effects; authorization still follows the user's request and the host's tool policy. Local `allow_writes` is an additional capability control, not a complete authorization system. A single working directory should have one active writer.

Do not commit generated `work/` outputs: metadata can still contain account details even when credentials are redacted. Error messages intentionally omit raw server bodies. Public issues should contain sanitized minimal examples only.
