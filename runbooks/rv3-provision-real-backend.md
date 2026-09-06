# RV3 — lock-steward provisioning walk-through (per-folder egress lock, off `mock`)
*governance-layer runbook. Local. DRAFT of the conversational flow the `lock-steward` runs.*
*Opened 2026-09-04. Nothing here runs until Felix (workspace_owner) confirms — every mutating step is a RESERVED security-setting change.*

## Purpose
Replace the difficult console install with a conversation that provisions a **real** egress-lock backend
per `folder_context`, sets a conservative threshold, sets the audit path (folds in **RV2**), optionally
seals, and saves a per-folder lock profile — under the lock-steward's security-by-design block (the ratchet
+ fail-secure). Current state (live `setup_status`): `configured:true`, **`backend_spec:"mock"`**,
**`audit_log_path:null`** — so this closes both the mock-backend gap and the null audit path.

## Guards that frame the whole flow
- **Reserved:** `setup` / `threshold_set` / `seal` change a security setting → each runs only on the
  **owner's in-conversation confirm** (the human sign-off). The assistant proposes + explains; it does not
  self-run a security mutation.
- **Secure default:** empty `backend_spec` ⇒ the **recommended REAL backend** — never mock.
- **No silent mock / fail-secure:** if the recommendation resolves to `mock` (host has no real backend),
  **STOP** — do not accept mock-as-real; tell the user a real backend must be installed first.
- **Ratchet:** start the threshold **strict**; raising later is the easy L3 direction, lowering is L4 +
  reserved to {owner, DPO} + reason.
- **Passphrase never in context:** `seal`/`unseal` passphrases are human-held; `passphrase_in_context` is
  prohibited.
- **Every change chained:** each mutating call is a signed `MutationLog` event; the profile records
  who/when/reason (never the passphrase).

## The flow

**0 · Scope.** Confirm the `folder_context` to protect (one folder per run — never workspace-wide in one act).

**1 · READ current state** — `workspace_lock(op="setup_status")`.
> Steward: "This folder is *configured* but on a **mock** backend — it reports protected but doesn't really
> minimise, and its audit path is unset. I recommend provisioning a real backend + a strict threshold +
> an audit log. Shall I walk you through it?"

**2 · PROPOSE a lock profile** — `propose_lock_profile` (no mutation). Present in plain language and ask to
confirm/adjust:
- **backend:** recommended real backend (empty `backend_spec` = accept recommendation; **not** mock)
- **threshold:** start **strict** (conservative minimisation) — e.g. the highest sensible tier
- **audit_log_path:** a path inside the folder so lock/egress decisions persist (RV2)
- **oversight:** the live oversight level from the matrix (`workspace_policy set_oversight_level`)

**3 · CONFIRM (the human gate).** The owner's chat "yes" **is** the sign-off. This is the reserved-act
boundary — nothing below runs without it. (A relayed "go" is not enough; owner-direct, per standing discipline.)

**4 · PROVISION the backend** — `workspace_lock(op="setup")` with empty `backend_spec` (accept the real
recommendation).
- **Verify immediately:** re-read `setup_status`. If `backend_spec` is still `mock` → **FAIL-SECURE STOP**:
  the host has no real backend; report it, do not proceed as if protected. (Downgrading a real backend to
  mock would require `accepted_by` + `reason` — refused in this flow.)

**5 · SET THRESHOLD** — `workspace_lock(op="threshold_set", {folder_context, threshold})` at the strict
starting value. (Raising later = `raise_threshold` L3; lowering = `lower_threshold` L4 + reserved.)

**6 · SET AUDIT PATH (RV2)** — set `audit_log_path` (via `setup` params / `workspace_policy`) so lock +
egress decisions land in the folder audit, alongside the governance chain the `auditor` verifies.

**7 · SEAL (optional)** — `workspace_lock(op="seal", {folder_context})` for encryption at rest. The
passphrase is **entered by the human**, never passed through or stored by the agent.

**8 · VERIFY on the REAL backend** — prove it discriminates, not just that it's configured:
- `classify` a known-PII string → expect high findings (on a real backend, catch what the mock regex missed:
  spaced IBAN, SV-number, webhook secret).
- `egress_check{tool, arguments, task_scope}` an over-scope PII send → expect strip → `arguments:{}`.
- `workspace_audit(op="verify_chain", {folder_context})` → the provisioning events are on the signed chain.

**9 · SAVE the per-folder lock profile** — record `folder_context · backend · threshold · audit_log_path ·
oversight · confirmed_by · timestamp · reason`. **Never** the passphrase. Chain-logged.

**10 · HAND BACK.** Report the new state (real backend, strict threshold, audit on) and state the ratchet:
tightening is easy; **loosening (lower_threshold / downgrade_backend / unseal) is L4 + reserved to {owner,
DPO} + reason** — so the folder can only get safer without a human's signed decision.

## Runnable-the-moment-you-say-go
Steps 1, 2, 8's reads are non-mutating (safe to preview any time). Steps 4–7, 9 are the reserved mutations —
they execute only on your per-step confirm. If the host has no real backend (step 4 fail-secure), the flow
stops honestly rather than leaving a mock that looks protected.
