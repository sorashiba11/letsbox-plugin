# Lets Box plugin

Lets Box is a thin Codex client for the Cloudflare Remote MCP at
`https://mcp.letsai.team/mcp`. The plugin registers one **native remote MCP
server**: the host manages OAuth itself (the "authenticate" button /
first-connection browser login), and no local process, node runtime, or
credential file is involved. Business skills are never packaged locally; the
entitlement-filtered catalog and every skill contract are returned by the
Remote MCP after the first-party Auth Core session is established.

The plugin ships exactly two local guidance skills (visible in the host's
skill list):

- `letsbox-connection-check` — 接続・アカウント診断（どのアカウントでログイン
  しているか、権限・認証情報の状態、復旧手順の案内）
- `letsbox-setup` — 初回セットアップ（ログイン確認と、eBayスキル用の
  EPSメール/SerpApiキーの一度きりの登録）

## Install

```bash
codex plugin marketplace add https://github.com/sorashiba11/letsbox-plugin
codex plugin add letsbox@letsbox
```

After installation, Codex settings should show one `LetsBox` MCP connection
and zero Lets Box-specific local skills. eBay Research, eBay Restock, CEO
Brain, and other entitled workflows are discovered through the Remote MCP's
server-side `list_skills`/`get_skill` contract and D1 effective entitlements.

## Runtime credentials (eBay skills only)

The eBay research/restock skills need the customer's EPS account email and
SerpApi key. They are stored **server-side per tenant** in one encrypted
envelope via the `set_runtime_credentials` tool — call it once (or on key
rotation); `get_runtime_credentials_status` reports the non-secret state.
CEO Brain and other skills need no runtime credentials at all.

## Runtime boundary

- Auth Core (`auth.letsai.team`) is the first-party login/session authority.
- The Remote MCP performs entitlement filtering and exposes production tool
  contracts; Codex uses the single `LetsBox` MCP connection.
- No AWS/S3/CloudFront manifest, Supabase runtime, local per-skill package, or
  localhost Launcher is used by this plugin.
- eBay deletion remains separately gated by the Remote MCP and is never implied
  by installing or connecting this plugin.
