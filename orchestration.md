# orchestration — the governance orchestrator + ctrl:legal seam

Plane: **enforcement = GOVERNANCE**. This file declares the loop that turns UNIVERSAL loomground
skills into GOVERNED ROLES and runs them under an enforcement host's gate. ctrl orchestrates the
vertical; the enforcement host governs each consequential act; loomground skills are the
capabilities.

> Loomground is universal; via an enforcement host and ctrl:legal these skills become governance
> capabilities.

---

## 1. The three planes, not blurred

| Plane | Role here | Never does |
|-------|-----------|------------|
| **ctrl** (`ctrl:legal`) | orchestrates the matter — intake, mode, dispatch, report | sign, gate, decide the verdict |
| **enforcement** (this layer) | GOVERNS — plans + gates every consequential act, chains it, mints/erases | ground a claim; dispose a reserved act |
| **loomground** (3 skills) | grounds/reasons/builds — the capabilities | carry governance identity (no grade, no gate) |

The loomground skills state their own boundary: each is a *capability skill* that "carries no
governance identity — no grade, no governance-block, no decision-authority." This layer supplies
that identity by binding a **governance-block** to each and having an enforcement host enforce it.

---

## 2. A ROLE = loomground skill + governance-block

Per the skill-governance-block spec (`../skill-governance-block/SPEC.md`) each role declares:
`grade · actions · reserved · prohibited · obligations · on-boundary · redress · budget` (the 8 spec fields; access-scope is descriptive, enforced via `actions[]` guards over tags — not a spec field).
An enforcement host ENFORCES the block; the agent-registry records it. The block is read at plan
time by the host's signed decision gate, and at 3am is a *reading of the block*, not a live
judgement call.

| ROLE | loomground skill | grade | access-scope (descriptive) | reserved (→ WHO) | prohibited |
|------|------------------|-------|-----------------|------------------|------------|
| **grounder** | `grounding/SKILL.md` | L2 | read: versum via `loomground-versum:loomground-kg-chat` + `loomground_legal` | — (read-only, escalates on UNCERTAIN) | assert un-confirmed coordinate as confirmed |
| **reasoner** | `reasoning/SKILL.md` | L2 | read (via grounder first) | conflict-resolution *disposition* → GCO/counsel | reason over un-confirmed premise; emit bare verdict |
| **km / builder** | `knowledge-management/SKILL.md` | L1 | **write** (single path `loomground-versum:loomground-knowledge-write`) | curate/mint into confirmed layer → data-owner; **erase** → controller | any write outside the single path; invent nodes |

Grade + reserved + budget are the load-bearing fields — they decide whether an act is `auto`,
held for `human`, or `reserved`.

---

## 3. The governance loop — propose → validate → decide → (execute) → report

Run by the **governance orchestrator** over one matter, composing the roles
**grounder → reasoner → km** under the gate. Every arrow crossing into a consequential act
passes through the host's signed decision gate → a Loomground verdict
`∈ {auto, human, reserved, prohibited}`.

```
ctrl:legal (vertical orchestrator)
   │  dispatches the matter, picks the mode (solo/panel/arena)
   ▼
governance orchestrator ──────────────── loop over the matter ────────────┐
                                                                            │
  1 PROPOSE   grounder role  ── loomground grounding ──► confirmed evidence │
              (ground-or-escalate; UNCERTAIN ⇒ no proposal, escalate)       │
                                                                            │
  2 VALIDATE  reasoner role  ── loomground reasoning ──► warranted claim    │
              + confirmed-bar check; premise gaps named, not fabricated     │
                                                                            │
  3 DECIDE    the host's signed decision gate ─► a Loomground verdict       │
                auto        → benign + grade allows / standing approval     │
                human       → may proceed ONLY with human sign-off          │
                reserved /  → prohibition / grade-floor / reserved act      │
                prohibited                                                  │
                                                                            │
  4 EXECUTE   only on auto, or human after the sign-off lands:              │
                km role writes via the single write path                    │
                → append signed event to the host's hash-chain (receipt)    │
              reserved act ⇒ NOT executed here — held for the human/GCO     │
                                                                            │
  5 REPORT    verdict + warrant + chain refs → back to ctrl:legal          │
              (a receipt any party can verify offline)                      ─┘
```

Refusal (**`prohibited`**) is a valid, expected outcome — an unplanned or refused act must not proceed.

---

## 4. Dual transport — the offline door vs the host-connected door

Every governance function has two doors. A **signed / stateful / authoritative** act is
**host-only**; the offline path is a **fail-closed hold**, never a computed result.

| Function | Offline/bundled skill (portable, CANNOT sign) | Host-connected door (authoritative, signed) |
|----------|----------------------------------------|-----------------------------------|
| plan + gate a disposition | evaluates block, returns *advisory* verdict, **holds** on any consequential act | the host's orchestrate call → its signed decision gate (a signed verdict) |
| ground / reason (read) | runs loomground skill locally | the host's grounder / legal / lens interfaces |
| append to the chain / mint receipt | **fail-closed hold** (cannot sign) | the host's capture / audit interfaces → a signed hash-chain append |
| erase (signed tombstone) | **fail-closed hold** | the host's erase interface → controller-key tombstone |
| record the block in registry | drafts the row | the host's contract / policy interfaces |
| conformity / release check | advisory checklist | the host's conformity interface |

Rule: if it signs, chains, mints a receipt, or erases → host-connected only. Offline/bundled = advise-and-hold.

---

## 5. The single release gate + the reserved-acts hold

- **One release gate.** The whole loop funnels to a single signed-decision-gate call per
  consequential act (surfaced as the sign-off panel). `human` routes to human sign-off;
  the release is not "computed" — it is *gated*.
- **Reserved-acts hold.** A reservation mapping ties detected issue types to
  the human act the law reserves — e.g. AI Act (Reg. 2024/1689) Art. 14 → `ai-oversight-officer`
  *authorize*; controller sign for a data disposition; qualified counsel *sign* for legal opinions.
  When a matter triggers a reserved act the gate returns **`reserved` (no autonomous execution)**
  and **holds** for the named competence.
- **The enforcement host governs but never itself disposes a reserved act.** The governance
  orchestrator plans, gates, chains, and reports — the *disposition* is taken by the human / GCO /
  named competence, whose sign-off is what the chain then records. The host places the human at
  the act; it does not stand in for them.

---

## 6. ctrl:legal integration (the seam)

1. `ctrl:legal` opens the matter and dispatches (solo / `/panel` / `/arena`) — vertical orchestration only.
2. For each consequential step it hands the act to the **governance orchestrator** via the
   enforcement host's own orchestrate call, which runs §3 over the role-ified loomground skills.
3. The host returns `{verdict, warrant, chain_ref, held_reserved_acts[]}`. `auto` acts are
   executed + chained; `human` acts wait for sign-off; reserved acts are surfaced to the human/GCO.
4. ctrl:legal composes the returned receipts into the matter report; it never overrides a
   `prohibited` verdict.

Governance/legal lenses (the host's lens / legal interfaces) plug into any ctrl mode without
changing this loop.
