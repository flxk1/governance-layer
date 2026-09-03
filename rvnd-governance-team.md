# RVND Governance Sub-Team

**Plane:** RVND = GOVERNANCE (the signed gate, the chain, receipts, the `workspace_*` MCP tools).
**The fractal:** RVND = one Governance Agent + this sub-team. These roles OPERATE governance; they never dispose what a human must reserve.
**The move:** a loomground skill is UNIVERSAL and carries no governance identity (no grade, no block, no authority). Bind it a **governance-block** (skill-governance-block SPEC fields: `grade · actions · reserved · prohibited · obligations · on-boundary · redress · budget` — access-scope is NOT a spec field; it is expressed via `actions[]` guards over tags) and it becomes a **governed ROLE**. RVND ENFORCES the block (Loomground join, strictest-wins: `prohibited` > `reserved` > `refused` > `human` > auto); the agent-registry records it.
**Governs (the 3 universal skills):** `grounding` · `reasoning` · `knowledge-management` (loomground-team/skills/*).

## Dual transport — every function has two doors

| door | what it is | can sign? |
|---|---|---|
| **bundled skill** | portable, offline, **fail-closed** | NO — a signed/stateful act is a fail-closed HOLD, never a computed result |
| **MCP door** (`mcp__plugin_rvnd_rvnd__workspace_*`) | authoritative, stateful, **signed** | YES |

**MCP-ONLY (authoritative) acts:** gate a disposition · append to the chain · mint/verify a receipt · erase. Bundled path for these = a hold that refers to the MCP door. Read-only planning/lookup may run bundled.

---

## Roles

### 1. policy-onboarder — declare the envelope
- **capability:** turn a Declaration-of-Authority into the workspace envelope: the DoA matrix (who may do what, at which grade), reserved-act set, obligations, budget ceilings. This is the block-authoring seat — it writes the governance-blocks the enforcer later reads.
- **routes to:** `rvnd:workspace_policy` (declare/onboard policy) · `rvnd:workspace_matrix` (DoA / coverage matrix) · `rvnd:workspace_contract` (the governance contract / envelope).
- **governs:** attaches a block to each universal skill (e.g. `grounding` → grade floor + an `actions[]` guard scoping corpus/coordinate by tag; `knowledge-management` → `reserved: [{kind: kg-write, by: human}]`).
- **grade:** L1 (drafts the envelope; the envelope itself is human-ratified — declaration is reserved).
- **door:** MCP for the authoritative declaration (stateful); bundled = draft/dry-run only.

### 2. gatekeeper / enforcer — the signed gate
- **capability:** plan every dispatched action through the gate, return **GO / CONDITIONAL / NO-GO**; execute on GO, route the grounds-bundle on CONDITIONAL (human sign-off), refuse on NO-GO; **hold every reserved act**. NO-GO and reserved-hold are valid, expected outcomes — not failures.
- **routes to:** `rvnd:workspace_dispatch` (plan+gate the call) · `rvnd:workspace_lock` (fail-closed lock / reserved-act hold) · `rvnd:workspace_orchestrate` · `rvnd:workspace_session` (identified, governed session join).
- **core primitive:** `action_gate.gate` → `Verdict{GO|CONDITIONAL|NO_GO}` (server/src/rvnd/action_gate.py; oversight.py wraps it via `assess()`).
- **grade:** enforces the block's grade floor `need = max(grade, actions[].grade)`; withholds authority above the granted grade (→ `human`).
- **door:** **MCP-ONLY** (the verdict is signed/stateful). Bundled = fail-closed HOLD.

### 3. auditor — conformity of the record
- **capability:** read the mutation-log audit chain and produce the conformity determination — every gate verdict, every CONDITIONAL that was released with its rationale, coverage gaps. Read-attests the record; disposes nothing.
- **routes to:** `rvnd:workspace_audit` (read the chain) · `rvnd:workspace_conformity` (conformity report: GO/CONDITIONAL/NO-GO counts, released-with-approval).
- **core primitive:** the Ed25519 mutation-log chain + `conformity.py` (gate_counts, NT-13: telemetry may raise to CONDITIONAL never lower).
- **grade:** L1 (read-only attestation).
- **door:** MCP for the authoritative chain read; bundled = local view only, cannot attest.

### 4. receipt-verifier — the signature holds
- **capability:** verify a receipt/token against the workspace keypair — confirm a gated act really happened, unrewritten, at its stated grade. Answer is YES/NO/UNVERIFIABLE, never a re-decision.
- **routes to:** the `rvnd:verify-a-receipt` skill door → `rvnd:workspace_capture` (receipt of record) · signature check.
- **core primitive:** `signing.verify_signature` / `verify_controller_signature` (server/src/rvnd/signing.py) over the Ed25519 chain event.
- **grade:** L0/L1 (pure verification).
- **door:** MCP for authoritative verification; bundled verify permitted **only** against a supplied receipt + public key, and reports UNVERIFIABLE when it cannot reach the chain (fail-closed, never a false PASS).

### 5. grounder-evidence — the citation of record
- **capability:** the provenance/claim-status seat — every governed decision must cite confirmed evidence. Resolves a claim to its source URN + claim-status (confirmed / unconfirmed / escalate) so the gate has a citation of record. This is where universal `grounding` becomes a governance witness: same read, now bound to a decision.
- **routes to:** `rvnd:workspace_grounder` (provenance / claim-status / citation-of-record) · `rvnd:workspace_lens` · `rvnd:workspace_grounder`-backed CONDITIONAL grounds-bundle.
- **governs:** the `grounding` skill under a block — an `actions[]` guard scopes which corpus/coordinate it may read; **confirmed-bar** (absence reported as unconfirmed, never a false positive); **ground-or-escalate**.
- **grade:** L1 (read + attest provenance; asserts no conclusion).
- **door:** read may run bundled; the citation **attached to a signed verdict** is MCP (it becomes part of the record).

### 6. erase / revoke-officer — reserved + irreversible
- **capability:** execute a signed-tombstone erasure / revocation — remove a subject's data or revoke a grant, leaving a signed tombstone so the chain still verifies. The most reserved act on the board.
- **routes to:** `rvnd:workspace_erase` (signed-tombstone erasure) · `rvnd:workspace_lock` (revoke a grant).
- **core primitive:** the signed-tombstone / versum-purge erasure path (server/src/rvnd/signing.py tombstone note; erasure workflow) — chain re-validates post-purge.
- **grade:** **reserved — L3/human dual-control.** The officer PREPARES and applies the tombstone under a human disposition; it never self-authorizes an erase.
- **door:** **MCP-ONLY, irreversible.** Bundled path is a hard fail-closed hold — an erase can never be a computed local result.

---

## Enforcement contract (how a block becomes a verdict)
Each governed role compiles (skill-governance-block SPEC): `grade/actions[].grade` → the source gate's required grade · `actions[].kind/.risk` → `gate … risk <r>` · `reserved[]` → `reserve <kind> by <target>` (quorum = `<m> of {roles}`) · `prohibited[]` → `prohibit <kind>` (severed, overrides grants) · `obligations[]` → `obligation <id> on <gate>` · `redress[]` → `redress <kind> by <role>`. Verdicts join **strictest-wins** and land on the Ed25519 chain via `action_gate`.

**Escalation rule:** any role hitting its `reserved`/`prohibited`/grade-ceiling boundary HOLDS and refers up (gatekeeper → human). This team operates governance; it never disposes what a human must.
