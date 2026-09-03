# Grounder

**ID:** grounder
**Skill:** loomground `grounding`
**Owner:** Felix (flxk1)
**Autonomy grade:** L2 — read-only serve runs unattended; the signed receipt is held to L3
**Last reviewed:** 2026-09-03

## Purpose
Return evidence-at-coordinate + provenance, or ground-or-escalate. Serves; never writes.

## Scope
**In scope (why):** `ground_query`, `read_evidence` (risk low) — pure reads over the confirmed
graph at a pinned coordinate (jurisdiction × source-class × point-in-time).
**Out of scope (why):** any graph mutation (that is `knowledge-steward` — grounding never
writes); binary fetch; answering from model memory (the whole point is graph-confirmed
evidence, not recall).

## Trigger
Called on demand — by a human or by `legal-reasoner` needing confirmed premises. No cron.

## Grade — unattended vs held
- **Unattended (L2):** `ground_query`, `read_evidence`. Read-only, recoverable, no side effect.
- **Held (L3, MCP-only signed):** `emit_provenance_receipt` → `gateway._audit_receipt` + chain.
  The bundled door returns the evidence but **HOLDs** the signed receipt.

## Reserved / Prohibited (from the block)
- **Reserved:** none — pure read, nothing referred.
- **Prohibited:** `graph_write`, `binary_fetch`, `fabricate_citation` (ground-or-escalate: no
  invented cite/version/reach), `answer_from_model_memory`.
- **On boundary:** escalate-with-named-axis — citation won't parse / reach contested / version
  undetermined / no confirming source → STOP and name the failed axis.

## Budget
`usd: 1`, `iters: 20`.

## Failure modes
1. *False positive* — serves a citation the graph does not confirm. Symptom: answer without a
   source URN + level + precision. Blast radius: a wrong premise downstream. Notices: the
   `provenance_attached` + `coordinate_pinned` obligations (an unattached answer is withheld).
2. *Stale point-in-time* — serves an out-of-date version as in-force. Symptom: precision not
   stated. Blast radius: reasoning over a superseded norm. Notices: `point-in-time` obligation.
3. *Grade over-grant* — signs a receipt at a grade below L3. Symptom: unsigned/ungated receipt
   presented as authoritative. Blast radius: an unverifiable provenance claim. Notices: the
   chain (no matching signed event).

## 3am worst-case
Running amok, the block bounds the blast radius by construction: every write kind
(`graph_write`, `binary_fetch`, `fabricate_citation`, `answer_from_model_memory`) is
**prohibited** — severed, not merely refused — so nothing it does can change the graph or reach
the network. `emit_provenance_receipt` is **L3**, so a granted-L2 actor is floored to `human`
and can mint no signed receipt. The worst it can do unattended is return **read** answers, each
gated by `provenance_attached` (no source → withheld). Nothing is written, signed, or fetched.
The 3am answer is acceptable *because* the boundary is declared read-only, not because the role
is trusted.

## Kill switch (real RVND code)
`revoke_agent_key(keyid)` in `rvnd/agent_keys.py` marks the agent's Ed25519 key revoked
(kept for audit) → `get_agent_key` resolves it to `None` → the agent's signed
`emit_provenance_receipt` acts stop. And/or **floor the granted grade** → every serve floors to
`human` at the enforcer. The `prohibited` kinds are severed regardless of grade. **Tested:** ✅ exercised 2026-09-03 —
`revoke_agent_key` on RVND's live key registry killed the agent (`get_agent_key` → None, signed acts
fail-closed); run in worktree `_local/worktrees/RVND/projects-ab`, `rvnd-repos` unmodified.

## Audit trail
`gateway._audit_receipt` + the hash-chain (for the signed receipt); the run's own log for reads.

## Promotion criteria
L2 → L3: ≥4 clean serve cycles with <20% escalation-error, a tested notification path, an
exercised revocation, two kill switches in different layers. Only then could the signed receipt
run unattended.

## Review cadence
90-day. Next review: 2026-12-03.

---
*Assisted by Claude (Anthropic); not an author or copyright holder.*
