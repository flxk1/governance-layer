# Knowledge steward

**ID:** knowledge-steward
**Skill:** loomground `knowledge-management`
**Owner:** Felix (flxk1)
**Autonomy grade:** L2 — dry-run/propose runs unattended; write held to L3, erase to L4
**Last reviewed:** 2026-09-03

## Purpose
Build and maintain the graph asset: ingest (dry-run) → concepts → placement → **write** →
curate; enrich; capture-session; **erase**. The one write/erase authority in this layer.

## Scope
**In scope (why):** `ingest_dryrun`, `extract_concepts` (risk low), `propose_placement`
(risk medium) — the propose/dry-run stages, all recoverable.
**Out of scope (why):** any write that bypasses the single governed path
(`loomground-versum:loomground-knowledge-write` is the only executor); binary fetch in session;
inventing a node (invent-nothing — missing context is recorded incomplete, never false);
unlogged mutation (every write is a chain event).

## Trigger
Called on demand — ingest an artifact, curate the canon, run an erasure. No cron.

## Grade — unattended vs held
- **Unattended (L2):** `ingest_dryrun`, `extract_concepts`, `propose_placement`.
- **Held (L3, host-only signed):** `graph_write`, `curate_canon` (the canon run IS a write) →
  the host's hash-chained mutation log (SHA-256 `prev_hash` chain) + an Ed25519 signature.
- **Held (L4, host-only signed):** `graph_erase` → the host's erasure sweep → one signed
  composite tombstone.
  On any offline/bundled door every write/curate/erase is a **fail-closed HOLD**.

## Reserved / Prohibited (from the block)
- **Reserved:** `graph_erase` to **distinct parties** {data_protection_officer, workspace_owner};
  `curate_canon` to `curator`.
- **Prohibited:** `direct_write_bypassing_path`, `binary_fetch_in_session`, `invent_node`,
  `unlogged_mutation`.
- **On boundary:** quarantine-or-review-queue — ingest quarantines; organise leaves
  novel/low-overlap unfiled; never guess a home.

## Budget
`usd: 5`, `iters: 40`.

## Failure modes
1. *Path bypass* — a write that skips the single governed executor. Symptom: a node with no
   canonical URN + dedup + house stub + sidecar. Blast radius: an unverifiable graph mutation.
   Notices: `single_write_path` + `dedup_urn_sidecar` obligations.
2. *Invented node* — writes context the source does not support. Symptom: a node with no
   provenance/timestamp. Blast radius: graph pollution. Notices: `invent_node` prohibited +
   `dry_run_then_confirm` (human confirms placements).
3. *Unauthorised erase* — a tombstone without the distinct-party pair. Symptom: erase with one
   or no sign-off / no legal basis. Blast radius: irreversible data loss. Notices: the reserved
   pair gate + `legal_basis_recorded` obligation.

## 3am worst-case
Running amok, the block bounds the blast radius by construction: `direct_write_bypassing_path`,
`invent_node`, `binary_fetch_in_session` and `unlogged_mutation` are **prohibited** (severed —
no ungoverned write, no invented node, no unlogged change); `graph_write`/`curate_canon` are
**L3** (a granted-L2 actor is floored to `human`) and on any bundled path a fail-closed HOLD;
`graph_erase` is **L4** *and* **reserved** to a distinct-party human pair (DPO + workspace_owner)
with `legal_basis_recorded`. The worst it can do unattended is produce **dry-run** ingests,
concept extractions, and placement **proposals** — nothing lands in the graph, nothing is
erased. Every mutation still requires a signed append to the host's hash-chained mutation log;
every erase requires two distinct humans and a signed tombstone. The 3am answer is acceptable
*because* write and erase are gated and reserved, not because the role is trusted.

## Kill switch
Revoking the role's signing key at the enforcement host stops its signed `graph_write` /
`curate_canon` (chain append) and `graph_erase` (tombstone) acts — a signed append can no longer
be attributed to it. And/or **floor the granted grade** → the role is reduced to dry-run/propose;
L3/L4 writes and erases cannot run. `graph_erase`/`curate_canon` stay **reserved** and the
write-path prohibitions stay **severed** regardless of grade. A conforming host proves this with
a load-bearing test (skill-governance-block SPEC §7).

## Audit trail
The host's hash-chained mutation log + its signed receipts (writes); the signed composite
tombstone (erase); the run's log (dry-runs/proposals).

## Promotion criteria
L2 → L3: ≥4 clean ingest/curate cycles with every write on the single path and <20% review-queue
rework, a tested notification path, an exercised revocation, two kill switches in different
layers. Erase (L4) stays reserved to the DPO + owner pair irrespective of promotion.

## Review cadence
90-day. Next review: 2026-12-03.

---
*Assisted by Claude (Anthropic); not an author or copyright holder.*
