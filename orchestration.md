# orchestration — the RVND Governance Orchestrator + ctrl:legal seam

Plane: **RVND = GOVERNANCE**. This file declares the loop that turns UNIVERSAL loomground
skills into GOVERNED ROLES and runs them under the RVND gate. ctrl orchestrates the vertical;
RVND governs each consequential act; loomground skills are the capabilities.

> Loomground is universal; via RVND/ctrl:legal these skills become governance capabilities.

---

## 1. The three planes, not blurred

| Plane | Role here | Never does |
|-------|-----------|------------|
| **ctrl** (`ctrl:legal`) | orchestrates the matter — intake, mode, dispatch, report | sign, gate, decide GO/NO-GO |
| **RVND** (this layer) | GOVERNS — plans + gates every consequential act, chains it, mints/erases | ground a claim; dispose a reserved act |
| **loomground** (3 skills) | grounds/reasons/builds — the capabilities | carry governance identity (no grade, no gate) |

The loomground skills state their own boundary: each is a *capability skill* that "carries no
governance identity — no grade, no governance-block, no decision-authority." This layer supplies
that identity by binding a **governance-block** to each and enforcing it in RVND.

---

## 2. A ROLE = loomground skill + governance-block

Per the skill-governance-block spec (`../skill-governance-block/SPEC.md`) each role declares:
`grade · actions · reserved · prohibited · obligations · on-boundary · redress · budget` (the 8 spec fields; access-scope is descriptive, enforced via `actions[]` guards over tags — not a spec field).
RVND ENFORCES the block; the agent-registry records it. The block is read at plan time by
`action_gate` and at 3am is a *reading of the block*, not a live judgement call.

| ROLE | loomground skill | grade | access-scope (descriptive) | reserved (→ WHO) | prohibited |
|------|------------------|-------|-----------------|------------------|------------|
| **grounder** | `grounding/SKILL.md` | L2 | read: versum via `loomground-versum:loomground-kg-chat` + `loomground_legal` | — (read-only, escalates on UNCERTAIN) | assert un-confirmed coordinate as confirmed |
| **reasoner** | `reasoning/SKILL.md` | L2 | read (via grounder first) | conflict-resolution *disposition* → GCO/counsel | reason over un-confirmed premise; emit bare verdict |
| **km / builder** | `knowledge-management/SKILL.md` | L1 | **write** (single path `loomground-versum:loomground-knowledge-write`) | curate/mint into confirmed layer → data-owner; **erase** → controller | any write outside the single path; invent nodes |

Grade + reserved + budget are the load-bearing fields — they decide whether an act is GO,
CONDITIONAL, or must be held for a human.

---

## 3. The governance loop — propose → validate → decide → (execute) → report

Run by the **RVND Governance Agent** over one matter, composing the roles
**grounder → reasoner → km** under the gate. Every arrow crossing into a consequential act
passes through `action_gate` → `Verdict ∈ {GO, CONDITIONAL, NO-GO}`.

```
ctrl:legal (vertical orchestrator)
   │  dispatches the matter, picks the mode (solo/panel/arena)
   ▼
RVND Governance Agent ──────────────── loop over the matter ───────────────┐
                                                                            │
  1 PROPOSE   grounder role  ── loomground grounding ──► confirmed evidence │
              (ground-or-escalate; UNCERTAIN ⇒ no proposal, escalate)       │
                                                                            │
  2 VALIDATE  reasoner role  ── loomground reasoning ──► warranted claim    │
              + confirmed-bar check; premise gaps named, not fabricated     │
                                                                            │
  3 DECIDE    action_gate(ActionRequest, block) ─► GateDecision             │
                GO          → benign + grade allows / standing approval     │
                CONDITIONAL → may proceed ONLY with human sign-off          │
                NO-GO       → prohibition / grade-floor / reserved act      │
                                                                            │
  4 EXECUTE   only on GO, or CONDITIONAL after the sign-off lands:          │
                km role writes via the single write path                    │
                → append signed event to the Ed25519 hash-chain (receipt)   │
              reserved act ⇒ NOT executed here — held for the human/GCO     │
                                                                            │
  5 REPORT    verdict + warrant + chain refs → back to ctrl:legal          │
              (a receipt any party can verify offline)                      ─┘
```

Refusal (**NO-GO**) is a valid, expected outcome — an unplanned or refused act must not proceed.

---

## 4. Dual transport — the bundled door vs the MCP door

Every governance function has two doors. A **signed / stateful / authoritative** act is
**MCP-ONLY**; the bundled path is a **fail-closed hold**, never a computed result.

| Function | Bundled skill (portable, CANNOT sign) | MCP door (authoritative, signed) |
|----------|----------------------------------------|-----------------------------------|
| plan + gate a disposition | evaluates block, returns *advisory* verdict, **holds** on any consequential act | `mcp__plugin_rvnd_rvnd__workspace_orchestrate` → `action_gate` (signed `GateDecision`) |
| ground / reason (read) | runs loomground skill locally | `rvnd:workspace_grounder`, `rvnd:workspace_legal`, `rvnd:workspace_lens` |
| append to the chain / mint receipt | **fail-closed hold** (cannot sign) | `rvnd:workspace_capture` / `rvnd:workspace_audit` → Ed25519 `mutation_log` append |
| erase (signed tombstone) | **fail-closed hold** | `rvnd:workspace_erase` → controller-key tombstone |
| record the block in registry | drafts the row | `rvnd:workspace_contract` / `rvnd:workspace_policy` |
| conformity / release check | advisory checklist | `rvnd:workspace_conformity` |

Rule: if it signs, chains, mints a receipt, or erases → MCP only. Offline/bundled = advise-and-hold.

---

## 5. The single release gate + the reserved-acts hold

- **One release gate.** The whole loop funnels to a single `action_gate` decision per
  consequential act (surfaced as the sign-off panel). CONDITIONAL routes to human sign-off;
  the release is not "computed" — it is *gated*.
- **Reserved-acts hold.** `rvnd.reservation.reserved_acts_for(...)` maps detected issue types to
  the human act the law reserves — e.g. AI Act (Reg. 2024/1689) Art. 14 → `ai-oversight-officer`
  *authorize*; controller sign for a data disposition; qualified counsel *sign* for legal opinions.
  When a matter triggers a reserved act the gate returns **NO-GO for autonomous execution** and
  **holds** for the named competence.
- **RVND governs but never itself disposes a reserved act.** The Governance Agent plans, gates,
  chains, and reports — the *disposition* is taken by the human / GCO / named competence, whose
  sign-off is what the chain then records. RVND places the human at the act; it does not stand in
  for them.

---

## 6. ctrl:legal integration (the seam)

1. `ctrl:legal` opens the matter and dispatches (solo / `/panel` / `/arena`) — vertical orchestration only.
2. For each consequential step it hands the act to the **RVND Governance Agent** via
   `rvnd:workspace_orchestrate`, which runs §3 over the role-ified loomground skills.
3. RVND returns `{verdict, warrant, chain_ref, held_reserved_acts[]}`. GO acts are executed +
   chained; CONDITIONAL acts wait for sign-off; reserved acts are surfaced to the human/GCO.
4. ctrl:legal composes the returned receipts into the matter report; it never overrides a NO-GO.

Governance/legal lenses (`rvnd:workspace_lens`, `rvnd:workspace_legal`) plug into any ctrl mode without
changing this loop.
