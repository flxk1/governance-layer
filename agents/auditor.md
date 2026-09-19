# Auditor

**ID:** auditor
**Skill:** the enforcement host's read-only audit interface (over the signed chain)
**Owner:** Felix (flxk1)
**Autonomy grade:** L2 — reads/verifies run unattended; it mutates nothing enforceable
**Last reviewed:** 2026-09-04

## Purpose
Verify the signed `mutation_log` chain (Ed25519 + SHA-256) and surface discrepancies — integrity,
shadow/uncovered acts, discipline rollups. It **writes no graph or policy content**; the one thing it may
append is an *attributed override record with rationale*. **Reports; never repairs.**

## Scope
**In scope (why):** `verify_chain`, `tail_chain`, `get_event`, `shadow_scan`, `discipline` (all low) — pure
reads over the folder's chain; `record_override` (medium) — the only append: log that a human overrode X,
with actor + field + rationale.
**Out of scope (why):** any knowledge write (`mutate_graph` — that is knowledge-steward); any policy apply
(`mutate_policy` — that is policy-officer); authoring signed content (`sign_content`); fixing a discrepancy
in place (`repair_in_place` — report to a human instead).

## Trigger
Called on demand — verify a chain, run a shadow/discipline scan, log a human override. A periodic
verify can be scheduled, but the auditor performs no remediation.

## Grade — unattended vs held
- **Unattended (L2):** all reads — `verify_chain`, `tail_chain`, `get_event`, `shadow_scan`, `discipline`.
- **Held (host-only, signed):** `record_override` — one attributed override event to the chain; a
  fail-closed HOLD on any offline/bundled path.

## Reserved / Prohibited (from the block)
- **Reserved:** none — pure read + attributed override-logging; nothing enacted.
- **Prohibited:** `mutate_graph`, `mutate_policy`, `sign_content`, `repair_in_place`.
- **On boundary:** report-not-repair — verify fails / a gap found → STOP, surface to a human, do not remediate.

## Budget
`usd: 1`, `iters: 30`.

## Failure modes
1. *Silent repair* — the auditor "fixes" a discrepancy instead of reporting it. Symptom: a chain change
   originating from the auditor beyond an override record. Blast radius: an audit that alters what it audits
   (conflict of interest). Notices: `repair_in_place` + `mutate_graph`/`mutate_policy` prohibited.
2. *Masked finding* — a shadow/discipline finding suppressed. Symptom: a scan reporting clean while events
   are uncovered. Blast radius: false assurance. Notices: `findings_not_masked` obligation.
3. *Assumed-intact chain* — reporting integrity without verifying. Symptom: an integrity claim with no
   `verify_chain` behind it. Notices: `chain_verified_before_report` obligation.

## 3am worst-case
Running amok, it **cannot alter what it audits**: `mutate_graph`, `mutate_policy`, `sign_content` and
`repair_in_place` are **prohibited** (severed — no knowledge write, no policy apply, no authored signature,
no in-place fix). Its one append, `record_override`, is attributed (actor + field + rationale) and a
fail-closed HOLD on any bundled path. The worst it can do unattended is **read** the chain, **verify** its
integrity, and **surface** shadow/discipline findings — assurance, not action. The 3am answer is acceptable
*because* the role is structurally write-nothing (an auditor that could fix things is not an auditor).

## Kill switch
Revoking the role's signing key at the enforcement host stops its signed `record_override` append.
Reads are already non-mutating; flooring the grade changes nothing enforceable. The write-nothing
prohibitions stay **severed** regardless of grade. (A conforming host proves this per
skill-governance-block SPEC §7's load-bearing test.)

## Audit trail
The audit *is* the trail: `verify_chain` results, `tail`/`get_event` reads, `shadow_scan`/`discipline`
rollups, and each attributed `record_override`. Pairs with the egress-lock's own audit log to
complete the per-folder audit story.

## Promotion criteria
Stays L2 by design — an auditor earns no autonomy to *act*; it earns *trust in its reads*. Review confirms
reads are complete, findings unmasked, and `record_override` always attributed. No promotion to any writing
grade — the role's value is that it cannot write.

## Review cadence
90-day. Next review: 2026-12-04.

---
*Assisted by Claude (Anthropic); not an author or copyright holder.*
