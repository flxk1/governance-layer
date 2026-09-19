# Lock steward

**ID:** lock-steward
**Skill:** loomground `knowledge-management` + an enforcement host's egress-lock interface (Privacy Lock)
**Owner:** Felix (flxk1)
**Autonomy grade:** L2 — status/classify/propose runs unattended; provision + strengthen held to L3, weaken/unseal to L4
**Last reviewed:** 2026-09-04

## Purpose
Provision and operate the **per-folder egress lock** (the Privacy Lock) through a conversation
that saves settings — replacing the console install. Then **discharge** the minimisation gate
(`egress_check`) on every egress. It manages the lock and is **never exempt** from it; on its own
it can only make protection *stronger*.

## Scope
**In scope (why):** `lock_status`, `classify_content` (risk low) — read the folder's protection
state + content sensitivity; `propose_lock_profile` (risk medium) — draft folder/threshold/backend
from the conversation, no mutation; `egress_check`/`ingress_check` (risk medium) — run the
server-authoritative minimisation gate (an evaluation, not a setting change).
**Out of scope (why):** standing up a mock/weak backend that reports protected (`silent_mock_backend`);
self-approved weakening (`weaken_without_distinct_party`); treating an unknown lock as protected
(`assume_protected_on_unknown`); falling through when the backend is down (`egress_on_lock_unavailable`);
holding a passphrase in context (`passphrase_in_context`).

## Trigger
Called on demand — a user wants to install/adjust egress protection on a folder, or an outward
act needs its `egress_check` discharge. No cron.

## Grade — unattended vs held
- **Unattended (L2):** `lock_status`, `classify_content`, `propose_lock_profile`, `egress_check`,
  `ingress_check`.
- **Held (L3, host-only signed):** `provision_lock` (`setup` + `seal`), `raise_threshold` — the
  *strengthen* direction of the ratchet → a mutating call on the host's egress-lock interface +
  chain event.
- **Held (L4, host-only signed):** `lower_threshold`, `downgrade_backend`, `unseal` — the *weaken*
  direction; each carries `accepted_by` + `reason`.
  On any offline/bundled door every provision/threshold/seal/unseal is a **fail-closed HOLD**.

## Reserved / Prohibited (from the block)
- **Reserved:** `provision_lock` + `unseal` to `workspace_owner`; `lower_threshold` +
  `downgrade_backend` to **distinct parties** {workspace_owner, data_protection_officer}.
- **Prohibited:** `silent_mock_backend`, `weaken_without_distinct_party`, `assume_protected_on_unknown`,
  `egress_on_lock_unavailable`, `passphrase_in_context`.
- **On boundary:** hold-and-explain — any lock op unavailable / status ambiguous / weakening
  unconfirmed → STOP, **hold egress**, name what is unprotected.

## Security-by-design (the two moves)
1. **The ratchet (asymmetric change).** Strengthening (`provision_lock`, `raise_threshold`) is L3;
   weakening (`lower_threshold`, `downgrade_backend`, `unseal`) is L4 **and** reserved to distinct
   humans **and** requires `accepted_by` + `reason`. Autonomous acts can only tighten; loosening
   always costs a human's signed reason — the general no-silent-downgrade shape any conforming
   host applies to its own protections.
2. **Fail-secure default-deny.** Absence of a lock is never read as permission: unknown / absent /
   unreachable status ⇒ the folder is UNPROTECTED ⇒ egress is HELD.
Plus: `provision_is_not_access` (managing a folder's lock grants no egress right over its content)
and `egress_check_not_self_waivable` (the steward routes its own outward calls through the gate),
so a compromised steward cannot self-exempt — and `egress_check` is server-authoritative, so it
cannot fake a pass.

## Budget
`usd: 2`, `iters: 25`.

## Failure modes
1. *Silent mock* — a weak backend that reports protected. Symptom: `setup_status` backend ≠ a real
   backend while status reads "protected". Blast radius: a folder believed safe, egressing freely.
   Notices: `silent_mock_backend` prohibited + `secure_default_backend` obligation.
2. *Self-approved weakening* — the steward lowers a threshold / unseals to let content out. Symptom:
   a threshold change or unseal with one or no distinct-party sign-off. Blast radius: exfiltration.
   Notices: the reserved distinct-party gate + `no_silent_weakening` (accepted_by + reason, signed).
3. *Optimistic egress* — treating an unknown/unreachable lock as safe. Symptom: an egress while
   `setup_status` is unknown or the backend is down. Blast radius: unminimised data past the boundary.
   Notices: `assume_protected_on_unknown` + `egress_on_lock_unavailable` prohibited; fail-secure bar.

## 3am worst-case
Running amok, the block bounds the blast radius by construction. It **cannot weaken** protection on
its own: `lower_threshold`/`downgrade_backend`/`unseal` are **L4** *and* **reserved** to distinct
humans with `accepted_by` + `reason`; `provision_lock`/`raise_threshold` are **L3** (a granted-L2
actor floors to `human`) and on any bundled path a fail-closed HOLD. It **cannot fake protection**:
`silent_mock_backend` is prohibited and `secure_default_backend` forces the recommended real backend.
It **cannot fall open**: unknown/unreachable lock ⇒ egress HELD (`assume_protected_on_unknown` +
`egress_on_lock_unavailable` prohibited). It **cannot self-exempt**: `egress_check` is
server-authoritative and `egress_check_not_self_waivable` routes its own egress through it. The worst
it can do unattended is **read** status, **classify** content, **propose** a profile, and **run**
the (server-authoritative) egress/ingress checks — it changes no setting and opens no boundary.
The 3am answer is acceptable *because* provisioning and weakening are gated and reserved, and the
default is deny — not because the role is trusted.

## Kill switch
Revoking the role's signing key at the enforcement host stops its signed `provision_lock`/
`raise_threshold` (L3) and `lower_threshold`/`downgrade_backend`/`unseal` (L4) acts. And/or
**floor the granted grade** → the role is reduced to status/classify/propose + the (read-only)
egress checks; no setting changes. The weaken-direction acts stay **reserved** and the
fail-secure prohibitions stay **severed** regardless of grade. On a read-only egress-gateway
deployment, all mutating ops are simply unavailable → fail closed.

## Audit trail
The host's egress-lock interface emits chain events on every mutating op
(`every_change_chained`); the per-folder **lock profile** records who confirmed / when / reason
(never the passphrase); its read op returns the audit query.

## Promotion criteria
L2 → L3: ≥4 clean provision/adjust cycles with a real backend (no mock), every weaken correctly
held to the distinct-party pair, a tested notification path, an exercised revocation, two kill
switches in different layers. Weaken (L4) stays reserved to the {workspace_owner, DPO} pair
irrespective of promotion.

## Review cadence
90-day. Next review: 2026-12-04.

---
*Assisted by Claude (Anthropic); not an author or copyright holder.*
