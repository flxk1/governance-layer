# Governance Layer — RVND + MCP

Turns the **universal loomground skills** into **governed roles**, and gives every governed act its
**authoritative signed door**. This is the RVND (governance) plane — separate from Loomground
(grounding) and ctrl (orchestration). *"Loomground is universal; via RVND/ctrl:legal these skills
become governance capabilities."*

## The move
A loomground skill is universal and carries no authority. Bind it a **governance-block** and it
becomes a governed **role**; **RVND enforces** the block, the agent-registry records it.

- **Governance-block = 8 spec fields** (`skill-governance-block`): `grade · actions · reserved ·
  prohibited · obligations · on-boundary · redress · budget`. **Access-scope is NOT a spec field** —
  it is expressed via `actions[]` guards over tags. (Correction from the build; verified against the schema.)
- **Role = loomground skill + governance-block.** Enforced at RVND's signed `action_gate`
  (`Verdict{GO|CONDITIONAL|NO_GO}`), landed on the Ed25519 hash-chain, provable via `rvnd:verify-a-receipt`.

## Artifacts
| File | What |
|---|---|
| **[roles.md](roles.md)** | the 3 loomground skills role-ified — each = skill + a full governance-block; which acts are MCP-only |
| **[rvnd-governance-team.md](rvnd-governance-team.md)** | the RVND governance sub-team (policy-onboarder · gatekeeper/enforcer · auditor · receipt-verifier · grounder-evidence · erase-officer), each routing to real `workspace_*` functions |
| **[mcp-door-map.md](mcp-door-map.md)** | the dual-transport map: bundled skill (portable, fail-closed) vs MCP `workspace_*` (authoritative). **Signed/stateful acts are MCP-only** — the bundled door fail-closes |
| **[orchestration.md](orchestration.md)** | the RVND Governance Agent's `propose → validate → decide → report` loop over a matter, composing the role-ified skills under the gate; how ctrl:legal invokes it (RVND governs; never itself disposes a reserved act) |

## Grounded + verified
Built via ctrl **/team**: a maker per artifact grounded in the real RVND repo + `workspace_*`
surface (read-only; `rvnd-repos` is hands-off), each independently refuted by `verify` on
**functions-real / schema-valid / signed-acts-MCP-only / planes-clean**. All four now accepted after
fixing the schema-validity defects verify caught (ISO→`14d`/`30d` durations; `grounding-access`
demoted from spec-field to `actions[]` guard; `graded`→`auto` verdict; `action_gate.py` file citation).

## The stack, whole
**Loomground** (universal skills: grounding · reasoning · knowledge-management) → **RVND** (this
layer: governance-blocks + the signed gate + MCP door) → **ctrl:legal** (orchestrates the vertical).

---
*Local, unpushed. rvnd-repos hands-off (consume-only). Publication reserved. Assisted by Claude
(Anthropic); not an author or copyright holder.*
