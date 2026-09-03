---
doc: agent-registry
title: Governance-layer agent registry
status: active
owner: Felix (flxk1)
version: 0.1.0
updated: 2026-09-03
---

# Governance-layer agent registry

Append-only. One row per role that acts without per-step human approval. This is the
**governance layer's own** registry — universal, not tied to any vertical. Each row is
**derived** from the role's `governance` block in `roles.md`; the brief lives in
`agents/<id>.md`.

- **Grade** = the block's `grade:` floor (per-action grades raise specific acts above it).
- **Purpose** = the role's own description.
- **Kill switch** = the enforcer's grade gate grounded in real RVND `agent_keys` code —
  `revoke_agent_key(keyid)` (revoke the agent's key → its signed acts stop) and/or flooring
  the granted grade → below-required acts fall to `human`. `prohibited`/`reserved` sever or
  withhold regardless of grade.

| id | name | purpose | grade | owner | kill switch | last-reviewed |
|---|---|---|---|---|---|---|
| `grounder` | Grounder | read-only evidence-at-coordinate + provenance, or ground-or-escalate; serves, never writes | **L2** | Felix (flxk1) | `revoke_agent_key(keyid)` → signed `emit_provenance_receipt` (L3) stops; floor grant → all serve floors to `human`. `graph_write`/`binary_fetch`/`fabricate_citation` **prohibited** (severed) | 2026-09-03 |
| `legal-reasoner` | Legal reasoner | grounded premises → warranted conclusion (apply→in-force→conflict→effect→deontic); calls grounder first, enacts nothing alone | **L2** | Felix (flxk1) | `revoke_agent_key(keyid)` → `emit_lg_patch` (L3) + signed `release_disposition` (L4) stop; floor grant → analysis floors to `human`. `release_disposition` **reserved** to quorum {legal_reviewer, policy_owner}; `self_enact` **prohibited** | 2026-09-03 |
| `knowledge-steward` | Knowledge steward | build/maintain the graph asset: ingest→concepts→placement→**write**→curate; enrich; erase — the one write/erase authority | **L2** | Felix (flxk1) | `revoke_agent_key(keyid)` → signed `graph_write`/`curate_canon` (L3, chain append) + `graph_erase` (L4, tombstone) stop; floor grant → dry-run/propose only. `graph_erase` **reserved** to {DPO, workspace_owner}; `direct_write_bypassing_path`/`invent_node` **prohibited** | 2026-09-03 |

## Rules
- **Start low, earn up** — new roles enter at L0/L1; promotion is earned per the brief's
  criteria, never granted on request.
- **Asymmetric** — hard to promote, one-flip to demote. On failure: demote + fix the failure
  mode, not "add monitoring at the same grade".
- **No row without a brief** — every row has a one-page brief with a `3am worst-case`
  paragraph, budget caps, and a named kill switch. No 3am paragraph → the role isn't ready.

---
*Assisted by Claude (Anthropic); not an author or copyright holder.*
