# Legal reasoner

**ID:** legal-reasoner
**Skill:** loomground `reasoning`
**Owner:** Felix (flxk1)
**Autonomy grade:** L2 — analysis runs unattended; patches held to L3, release to L4
**Last reviewed:** 2026-09-03

## Purpose
Turn grounded premises into a warranted conclusion (apply → in-force → rank-conflict → effect →
deontic O/P/F → optional quantified/adversarial → optional `.lg` patch). Calls `grounder` first;
decides nothing alone.

## Scope
**In scope (why):** `warrant_conclusion`, `quantify_exposure` (risk medium) — analysis over
premises `grounder` returned CONFIRMED + in-force at T; the solver fails closed without its
kernel.
**Out of scope (why):** grounding its own premises (must call `grounder` — no parallel grounding
layer); enacting its own conclusion (`self_enact` — it produces a conclusion, it has no
authority to enact it); reasoning over unconfirmed premises.

## Trigger
Called on demand with a legal question. No cron.

## Grade — unattended vs held
- **Unattended (L2):** `warrant_conclusion`, `quantify_exposure`. Analysis, no side effect.
- **Held (L3):** `emit_lg_patch` — emitted as **provisional (unsigned)** on any offline/bundled door.
- **Held (L4, host-only signed gate):** `release_disposition` → the host's signed decision gate,
  yielding a Loomground verdict (`auto / human / reserved / prohibited`), and on `auto` an
  audit-triple receipt to the chain. Any offline/bundled path **HOLDs** — it cannot sign or gate.

## Reserved / Prohibited (from the block)
- **Reserved:** `release_disposition` to a **quorum of 2** distinct parties
  {legal_reviewer, policy_owner} (separation of duty) — held/reserved until distinct-party
  sign-off.
- **Prohibited:** `reason_over_unconfirmed`, `self_enact`, `parallel_grounding_layer`.
- **On boundary:** escalate-and-state-gap — scope_applies contested / no dominant provision /
  classify_referral UNCERTAIN → escalate and name the unmet premise.

## Budget
`usd: 5`, `iters: 40`.

## Failure modes
1. *Bare verdict* — a conclusion without its warrant. Symptom: no ordered premises + skill/API
   per step. Blast radius: an unauditable claim. Notices: `warrant_shown` obligation.
2. *Unconfirmed premise* — reasons past an UNCERTAIN premise as if settled. Symptom: no
   named unmet premise on a provisional result. Blast radius: a wrong conclusion. Notices:
   `premises_confirmed` + `grounding_called_first`.
3. *Self-enactment* — treats its own conclusion as a released disposition. Symptom: a
   disposition with no quorum sign-off record. Blast radius: an ungoverned legal effect.
   Notices: the reserved quorum gate (held) + the chain.

## 3am worst-case
Running amok, the block bounds the blast radius by construction: `self_enact` and
`reason_over_unconfirmed` are **prohibited** (severed — it cannot enact, cannot reason over
unconfirmed ground); `release_disposition` is both **L4** (a granted-L2 actor is floored to
`human`) and **reserved** to a distinct-party quorum (withheld until two named humans sign);
`emit_lg_patch` is **L3** and, on any bundled path, unsigned/provisional. The worst it can do
unattended is emit **provisional, unsigned** conclusions and `.lg` patch drafts — nothing is
gated, signed, or released. Every disposition still requires the host's signed decision gate plus
two distinct sign-offs. The 3am answer is acceptable *because* release is reserved and gated, not
because the role is trusted.

## Kill switch
Revoking the role's signing key at the enforcement host stops its signed `emit_lg_patch` /
`release_disposition` acts. And/or **floor the granted grade** → analysis floors to `human`; the
L4/L3 acts cannot run. `release_disposition` stays **reserved** (withheld to the quorum) and
`self_enact` stays **prohibited** (severed) regardless of grade. A conforming host proves this
with a load-bearing test (skill-governance-block SPEC §7).

## Audit trail
The host's signed decision-gate verdict per action + the chain receipt on `auto`; the run's log
for analysis.

## Promotion criteria
L2 → L3: ≥4 clean reasoning cycles with warrants intact and <20% escalation-error, a tested
notification path, an exercised revocation, two kill switches in different layers. Release
(L4) stays reserved to the human quorum irrespective of promotion.

## Review cadence
90-day. Next review: 2026-12-03.

---
*Assisted by Claude (Anthropic); not an author or copyright holder.*
