# Policy officer

**ID:** policy-officer
**Skill:** loomground `governance` (`loomground-governance:loomground`) + an enforcement host's policy-workflow interface
**Owner:** Felix (flxk1)
**Autonomy grade:** L2 — ground/compile/validate runs unattended; apply held to L4, rebind to L3
**Last reviewed:** 2026-09-04

## Purpose
The **versum-policy → enforceable `.lg`** bridge. Ground the ingested policy (known, real-time) →
compile a governance twin under the express/policy/host litmus → validate → **a human applies it**.
It turns *known* policy into *enforced* policy. KNOW is real-time; **ENFORCE-a-change is reserved.**

## Scope
**In scope (why):** `ground_policy` (low) — read the ingested policy via the grounder; `compile_lg_twin`
(medium) — policy-text → validated `.lg` twin, applies nothing; `validate_patch` (low) — `patch_validate`,
fail-closed, no writes.
**Out of scope (why):** applying policy without a human (`auto_apply_policy`); applying a patch that failed
validation (`enforce_unvalidated`); widening authority (stays a deliberate patch act — `authority_revoke`
is tighten-only); disabling a protection silently (`silent_disable` — needs accepted_by + reason).

## Trigger
Called when policy is ingested/changed and must become enforceable, or when an agent's lane must rebind
to a new policy. No cron (the real-time *feed* that notices new policy is LG2, separate).

## Grade — unattended vs held
- **Unattended (L2):** `ground_policy`, `compile_lg_twin`, `validate_patch` — produce a **draft twin**
  (`applied:false`).
- **Held (L3, host-only signed):** `rebind_lane` → the host mints a capability bound to the new
  `policy_fingerprint`.
- **Held (L4, host-only signed, reserved):** `apply_patch` → writes the policy to the signed
  chain — the act that changes what the gate enforces. On any offline/bundled door both are
  fail-closed HOLDs.

## Reserved / Prohibited (from the block)
- **Reserved:** `apply_patch` + `rebind_lane` to `workspace_owner` (the human who confirms the enforced change).
- **Prohibited:** `auto_apply_policy`, `enforce_unvalidated`, `self_widen_authority`, `silent_disable`.
- **On boundary:** hand-off-or-escalate — litmus=host → hand to the runtime; litmus unclear / unconfirmed
  policy → escalate, don't apply.

## Budget
`usd: 3`, `iters: 30`.

## Failure modes
1. *Silent enforce* — policy changed without a human. Symptom: an applied patch with no owner sign-off.
   Blast radius: the gate silently enforces (or stops enforcing) something no human chose. Notices:
   `auto_apply_policy` prohibited + `human_confirm_before_apply` + the reserved `apply_patch` gate.
2. *Unvalidated patch* — an ill-formed `.lg` reaches the chain. Symptom: `patch_apply` without a prior
   `patch_validate` pass. Blast radius: a broken policy graph. Notices: `enforce_unvalidated` prohibited +
   `validated_before_apply`.
3. *Authority creep* — the officer widens who may act. Symptom: a patch that grants (not just tightens)
   authority. Notices: `self_widen_authority` prohibited (widening is a deliberate owner patch act).

## 3am worst-case
Running amok, it **cannot change what is enforced**: `apply_patch` is **L4 + reserved** to the workspace
owner and `human_confirm_before_apply` means `policy_ingest`/`governance_chat` apply **nothing** until a
human `patch_apply`; `rebind_lane` is L3 + reserved; both are fail-closed HOLDs on any bundled path. It
**cannot apply garbage** (`enforce_unvalidated` prohibited; `validated_before_apply`), **cannot widen
authority** (`self_widen_authority` prohibited — tighten-only), and **cannot silently disable** a
protection (`silent_disable` prohibited — accepted_by + reason). The worst it can do unattended is
**ground**, **compile a draft twin**, and **validate** it — a proposal, enforcing nothing. The 3am answer
is acceptable *because* the enforce-a-change step is reserved to a human, not because the role is trusted.

## Kill switch
Revoking the role's signing key at the enforcement host stops its signed `apply_patch` (chain
write) + `rebind_lane` acts. And/or **floor the granted grade** → the role is reduced to
ground/compile/validate (draft twins only); no policy reaches the chain. `apply_patch`/
`rebind_lane` stay **reserved** and the apply-path prohibitions stay **severed** regardless of
grade.

## Audit trail
The host's `apply_patch` chain events (the applied policy + its `policy_fingerprint`); the host's
live-governance / lane-capabilities views project the current enforced policy; the draft twins
(compile/validate) are proposals, logged as such.

## Promotion criteria
L2 → L3: ≥4 clean ingest→compile→validate→(owner)apply cycles with every apply owner-confirmed and every
patch validated first, a tested notification path, an exercised revocation, two kill switches in different
layers. `apply_patch` (L4) stays reserved to the workspace owner irrespective of promotion.

## Review cadence
90-day. Next review: 2026-12-04.

---
*Assisted by Claude (Anthropic); not an author or copyright holder.*
