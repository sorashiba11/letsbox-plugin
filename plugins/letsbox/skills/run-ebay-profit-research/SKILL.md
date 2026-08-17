---
name: run-ebay-profit-research
description: Run or inspect Lets Box eBay profit research only through the authenticated Lets Plugin Remote MCP service. Use for new reservation-product research, supplier sourcing, same-item image judgement, existing campaign progress checks, profit reports, and tenant monitoring. Use 15 items when the user does not specify a count; honor explicit counts from 1 to 15.
---

# Run Lets Box eBay profit research

## Overview

Use only the `letsbox` Remote MCP server bundled with Lets Plugin. Never use a local `ebay-profit-research` skill folder, the legacy `letsbox-ebay-research` plugin, a staging service, a fixture, or an authentication bypass as fallback.

The service owns campaign state, evidence, retries, tenant authorization, and mutation gates. AI judgement runs only in the current ChatGPT or Codex subscription; never call a model API or invent a verdict for another worker.

## Usage

1. Call `health`, then `preflight`. If either reports a blocker, report the exact reason and leave campaign state unchanged.
2. Branch on the request before creating anything:
   - For an existing campaign progress or report request, call `get_campaign` with the supplied campaign ID. Call `get_report` only when appropriate, and use `list_items`, `get_item`, or `list_artifacts` for bounded inspection. Never start a new campaign for an inspection request.
   - For tenant monitoring, call `get_monitoring_summary` only when the connected user has the required administrator scope. Never start a campaign for monitoring.
   - If an inspection request has no campaign ID, use bounded Lets Box history to identify it or ask the user for the ID; do not guess and do not start a replacement.
3. For a new research request, start one campaign:
   - If the user did not specify a count, omit `max_items`; the service defaults to 15. Verify the returned `itemCount` is 15.
   - If the user specified a count from 1 to 15, pass that exact `max_items` and verify the returned `itemCount` matches.
   - Omit `mutation_mode` for ordinary research. The service applies its safety default without exposing it in the launch prompt.
   - If the user explicitly requests external updates, check `preflight.mutations_enabled` before starting. If false, stop and report that this Remote connection cannot perform the update; never switch to a local workflow. If deletion was requested, also require `preflight.deletions_enabled` before starting.
   - Only when the requested capability is enabled and explicitly requested may `preview` or `write` be selected. All existing authorization, scope, preview, single-writer, and deletion-approval gates still apply.
   - The call creates one bounded campaign. Continue that campaign; never start a replacement because work is slow or waiting.
4. Poll `get_campaign` until terminal. When it reports `waiting_for_judgement`, call `claim_judgement` once and handle only the returned mission.
5. Submit each mission through `submit_judgement` with its unchanged mission ID, lease token, prompt hash, candidate ID, and required structured verdict.
6. For `same_item_image`, compare only the reference and candidate images attached to the mission. Begin `imageReadSummary` with `Read:` and cite concrete visible evidence. Never decide from title similarity alone.
7. For `competitor`, examine the supplied price-ordered batch and return only the ordered prefix allowed by the mission prompt. Do not include unexamined candidates.
8. If a mission cannot be decided within its bounded retry, use the server-directed manual-review path. A held campaign is not complete.
9. After terminal status, call `get_report`. Verify the reported item count, supplier coverage, competitor coverage, profit coverage, hold reasons, and mutation counts. Use `list_items`, `get_item`, and `list_artifacts` for bounded inspection; never assemble the entire raw campaign payload.
10. A campaign using the default safety mode must finish with `externalMutationCount: 0`. For an enabled and explicitly requested preview or write campaign, keep the existing preview and apply gates intact.
11. Treat deletion separately. Present exact targets and the preview hash, then call `approve_deletions` only after a fresh explicit approval containing the required phrase and an unexpired campaign-specific token.
12. Report the terminal status, requested/default count check, completed/held/failed item counts, supplier and profit coverage, hold reasons, and mutation counts. Never label waiting, held, cancelled, or partial work complete.

## Mission handling

- `title_triage`: legacy campaign compatibility only. Follow the mission contract exactly.
- `same_item_image`: compare only current mission images; do not reuse evidence from another candidate or campaign.
- `competitor`: preserve server order and the prompt's cutoff rules.
- Never alter tenant IDs, prompts, evidence handles, mission IDs, leases, or server-controlled gates.

## Connection and support

- Production MCP URL: `https://mcp.letsai.team/mcp`.
- A failed OAuth or preflight is a closed gate. Do not switch to the local version.
- For support, provide only the campaign ID and timestamp. Never include OAuth tokens, EPS credentials, API keys, or raw customer artifacts.

## Intermediate files

No campaign intermediate files are created on the customer device. Large JSON, images, command logs, and handoffs remain in tenant-scoped service storage and are exposed only through authorized bounded handles.

## Final output

Return a compact campaign summary with the campaign ID, terminal state, exact item-count check, adopted supplier count, competitor coverage, profit-report coverage, hold reasons, and mutation counts.

## Customization guide

Customers may change only the requested item count from 1 to 15 and whether approved non-deletion updates should run. Tool order, tenant IDs, judgement prompts, mutation gates, deletion confirmation text, and evidence handles are server-controlled and must not be edited.
