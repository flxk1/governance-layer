# Governance Layer

Turns the **universal loomground skills** into **governed roles**, and gives every governed act its
**authoritative signed door**. This is the enforcement plane — separate from Loomground
(grounding) and ctrl (orchestration). *"Loomground is universal; via an enforcement host and
ctrl:legal these skills become governance capabilities."*

## The move
A loomground skill is universal and carries no authority. Bind it a **governance-block** and it
becomes a governed **role**; **an enforcement host enforces** the block, the agent-registry records it.

- **Governance-block = 8 spec fields** (`skill-governance-block`): `grade · actions · reserved ·
  prohibited · obligations · on-boundary · redress · budget`. **Access-scope is NOT a spec field** —
  it is expressed via `actions[]` guards over tags. (Correction from the build; verified against the schema.)
- **Role = loomground skill + governance-block.** Enforced at the host's signed decision gate
  (a Loomground verdict — `auto / human / reserved / prohibited`, joined strictest-wins), landed
  on a signed hash-chain, provable by replaying the chain.

## Artifacts
| File | What |
|---|---|
| **[roles.md](roles.md)** | the 3 loomground skills role-ified — each = skill + a full governance-block; which acts are host-only |
| **[orchestration.md](orchestration.md)** | the governance-orchestrator's `propose → validate → decide → report` loop over a matter, composing the role-ified skills under the gate; how ctrl:legal invokes it (the enforcement host governs; it never itself disposes a reserved act) |

## Grounded + verified
Built via ctrl **/team**: a maker per artifact grounded in the skill-governance-block spec, each
independently refuted by `verify` on **schema-valid / signed-acts-host-only / planes-clean**. All
artifacts now accepted after fixing the schema-validity defects verify caught (ISO→`14d`/`30d`
durations; `grounding-access` demoted from spec-field to `actions[]` guard; `graded`→`auto` verdict).

## The stack, whole
**Loomground** (universal skills: grounding · reasoning · knowledge-management) → an **enforcement
host** (governance-blocks + the signed gate) → **ctrl:legal** (orchestrates the vertical). This
repo ships the roles and the governance-blocks; it names no specific host and depends on none —
any host that reads the skill-governance-block spec (github.com/flxk1/skill-governance-block)
can enforce them.

---
*Local, unpushed. Publication reserved. Assisted by Claude (Anthropic); not an author or copyright holder.*
