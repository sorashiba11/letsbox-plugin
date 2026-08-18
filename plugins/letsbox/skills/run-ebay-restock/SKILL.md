---
name: run-ebay-restock
description: Run Lets Box eBay Restock only through the authenticated Lets Plugin Remote MCP service. Use for OOS detection, supplier re-sourcing, same-item image judgement, competitor checks, deterministic restore decisions, and bounded EPS URL, price, and quantity writes. Restock has no read mode and never invokes the standalone cheapest-price workflow.
---

# Run Lets Box eBay Restock

## Overview

Use only the `letsbox` Remote MCP server bundled with Lets Plugin. Never use a local `ebay-restock` skill folder, the standalone repricer, a staging service, a fixture, or an authentication bypass as fallback.

Restock runs on the same current Research campaign, sourcing, judgement, competitor, profit, evidence, retry, and EPS-writer foundation. Its deterministic differences are limited to active-listing OOS selection and the final Restock action. AI judgement runs only in the current ChatGPT or Codex subscription; the MCP never calls a model API or invents a verdict.

An OOS target is an active eBay listing with sufficient EPS supplier-URL coverage whose registered URLs are all explicitly `out_of_stock`. Unknown, missing, or partially covered stock evidence is not OOS. Restock has no read-only start mode, creates no deletion target, and never calls a standalone cheapest-price update.

## Usage

1. Call `health`, then `preflight`. If either reports a blocker, report the exact reason and leave campaign and eBay state unchanged.
2. Branch on the request before creating anything:
   - For an existing Restock campaign progress or report request, call `get_campaign` with the supplied campaign ID. Use `get_report`, `list_items`, `get_item`, or `list_artifacts` only for bounded status inspection. Status inspection is not a Restock read mode and must not start a replacement campaign.
   - If no campaign ID is supplied for an existing-run request, use bounded Lets Box history or ask for the ID. Never guess.
3. For a new Restock request, call `start_restock` once:
   - If the user did not specify a count, omit `max_items`; the service defaults to 15. Verify `itemCount` is 15.
   - If the user specified 1 to 15, pass that exact `max_items` and verify `itemCount` matches.
   - Never send `mutation_mode`, `read_only`, `dry_run`, a repricer flag, or a deletion option. The public Restock input accepts none of them.
   - The call must fail closed unless the production write deployment, tenant single-writer route, EPS URL registration, Restock price, and quantity gates are all enabled.
4. Continue the single returned campaign. The server follows the canonical source-first path: supplier discovery, stock confirmation, same-item image judgement, packed dimensions, early profit estimate, eBay competitors, competitor judgement, deterministic profit/Restock report, then validation.
5. When `get_campaign` reports `waiting_for_judgement`, call `claim_judgement` once and handle only that mission.
6. Submit the mission through `submit_judgement` with its unchanged mission ID, lease token, prompt hash, candidate ID, and required structured verdict.
7. For `same_item_image`, compare only the attached reference and candidate images. Begin `imageReadSummary` with `Read:` and cite concrete visible evidence. Never decide from title similarity alone.
8. For `competitor`, preserve server price order and return only the prompt-allowed ordered prefix. Do not include unexamined candidates.
9. If evidence, dimensions, supplier identity, stock, or competitor rank remains unresolved, use the server-directed manual-review path. `needs_review` creates no URL, price, quantity, or deletion write.
10. After a validated Restock report, the server records the pre-mutation archive and processes each restore listing in this fixed dependency order: EPS supplier registration, Restock-owned deterministic price, then quantity 1. A rejected or held earlier action blocks all later actions for that listing. A deterministic `qty0` action may set quantity 0 only; it never changes price or supplier URL.
11. Poll `get_campaign` until terminal, then call `get_report`. Use `apply_updates` only as an idempotent retry for already-materialized failed non-deletion operations. Never call `approve_deletions` for Restock.
12. Report terminal state, exact item-count check, OOS selection count, restore/qty0/needs-review counts, hold reasons, and EPS registration/price/quantity mutation counts. Never label waiting, held, cancelled, or partial work complete.

## Mission handling

- `title_triage`: legacy campaign compatibility only. Follow the mission contract exactly.
- `same_item_image`: compare only current mission images and provide concrete visible evidence.
- `competitor`: preserve server order and cutoff rules; unresolved rank becomes a Restock hold, not an automatic restore.
- Never alter tenant IDs, prompts, evidence handles, mission IDs, leases, deterministic prices, OOS state, or server-controlled gates.

## Connection and support

- Production MCP URL: `https://mcp.letsai.team/mcp`.
- The plugin's local stdio bridge reads the EPS account email and SerpApi key from `$CODEX_HOME/plugin-data/letsbox/credentials.json` (or `~/.codex/plugin-data/letsbox/credentials.json`) and forwards them only as request-scoped HTTPS headers. Configure them with `python3 scripts/configure_credentials.py`; never accept or echo either value in chat.
- Customer credentials are never tool arguments and are never stored in the Remote MCP database.
- A failed local credential load, OAuth exchange, entitlement check, or preflight is a closed gate. Do not switch to a local workflow.
- For support, provide only the campaign ID and timestamp. Never include OAuth tokens, EPS credentials, API keys, or raw customer artifacts.

## Intermediate files

No Restock intermediate files are created on the customer device. Campaign inputs, bounded evidence, encrypted in-flight credential envelopes, reports, pre-mutation archives, and mutation receipts remain tenant-scoped. Raw customer credentials are not campaign artifacts or database fields.

## Final output

Return a compact Restock summary with the campaign ID, terminal state, requested/default count check, selected OOS count, restore/qty0/needs-review counts, hold reasons, and EPS registration/price/quantity mutation counts. State explicitly that standalone cheapest-price and deletion workflows were not used.

## Customization guide

Customers may change only the requested item count from 1 to 15. OOS evidence rules, source-first ordering, judgement prompts, packed-dimension requirements, profit thresholds, Restock price calculation, archive/write order, dependency blocking, tenant routes, and deletion prohibition are server-controlled and must not be edited.
