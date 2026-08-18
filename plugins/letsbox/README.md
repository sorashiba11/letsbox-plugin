# Lets Box plugin

Lets Box is a thin Codex client for the Cloudflare Remote MCP at
`https://mcp.letsai.team/mcp`. The plugin registers one MCP server only. It
does not ship, register, or install per-skill `SKILL.md` packages; the
entitlement-filtered catalog and every skill contract are returned by the
Remote MCP after the first-party Auth Core session is established.

## Install

```bash
codex plugin marketplace add https://github.com/sorashiba11/letsbox-plugin
codex plugin add letsbox@letsbox
```

After installation, Codex settings should show one `LetsBox` MCP connection
and zero Lets Box-specific local skills. eBay Research, eBay Restock, CEO
Brain, and other entitled workflows are discovered through the Remote MCP's
server-side `list_skills`/`get_skill` contract and D1 effective entitlements.

## Optional eBay bridge credentials

Only the Remote MCP bridge may read the customer's optional EPS account email
and SerpApi key from `$CODEX_HOME/plugin-data/letsbox/credentials.json` (or
`~/.codex/plugin-data/letsbox/credentials.json`). Configure it once with:

```text
python3 scripts/configure_credentials.py
```

The file is outside the plugin cache, uses mode `0600`, and is never included
in the plugin bundle, MCP arguments, tool arguments, logs, or reports. It is a
request-scoped bridge input, not a local skill package or a catalog source.

## Runtime boundary

- Auth Core (`auth.letsai.team`) is the first-party login/session authority.
- The Remote MCP performs entitlement filtering and exposes production tool
  contracts; Codex uses the single `LetsBox` MCP connection.
- No AWS/S3/CloudFront manifest, Supabase runtime, local per-skill package, or
  localhost Launcher is used by this plugin.
- eBay deletion remains separately gated by the Remote MCP and is never implied
  by installing or connecting this plugin.
