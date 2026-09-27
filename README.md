# Governance Layer

Turn universal loomground skills into governed roles: compile, register, and bind each skill's
own governance block to an enforcement host's doors.

Every governed act gets its **authoritative signed door**. This is the enforcement
plane — separate from Loomground (grounding) and ctrl (orchestration).
*"Every shipped Loomground skill declares its own governance block; via an enforcement host and
ctrl:legal this layer compiles, registers, and binds that block to host doors, turning the skill
into a governed role."*

## The move
Every shipped loomground skill declares its own governance block, but the skill itself has no
grade, gate, or decision authority. This layer **compiles, registers, and binds** that declared
block to the host's doors, turning the skill into a governed **role**; **an enforcement host
enforces** the block, the agent-registry records it.

- **Governance-block = 8 spec fields** (`skill-governance-block`): `grade · actions · reserved ·
  prohibited · obligations · on-boundary · redress · budget`. **Access-scope is NOT a spec field** —
  it is expressed via `actions[]` guards over tags. (Correction from the build; verified against the schema.)
- **Role = loomground skill + governance-block.** Enforced at the host's signed decision gate
  (a Loomground verdict — `auto / human / reserved / prohibited`, joined strictest-wins), landed
  on a signed hash-chain, provable by replaying the chain.

**Offline door — HOLD.** On the offline door every signed or stateful act on the governed
graph — `graph_write`, `curate_canon`, `graph_erase`, `apply_patch`, `rebind_lane`,
`release_disposition`, `record_override`, `emit_provenance_receipt`, and every lock mutation
(`provision_lock`, `raise_threshold`, `lower_threshold`, `downgrade_backend`, `unseal`) — is a
HOLD. Offline tools may write only a local, unsigned working folder, and only after an explicit
confirm (a dry run is the default); that folder is not the governed record.

The obligation invariant of the skill-governance-block spec (SGB) §7(d) — an unattached
obligation withholds release — is exercised by a host, not by this compiler or evaluator:
obligations attach by declaration.

## Artifacts
| File | What |
|---|---|
| **[roles.md](roles.md)** | the seven governed roles — each = public skill(s) + a full governance-block; which acts are host-only |
| **[orchestration.md](orchestration.md)** | the governance-orchestrator's `propose → validate → decide → report` loop over a matter, composing the role-ified skills under the gate; how ctrl:legal invokes it (the enforcement host governs; it never itself disposes a reserved act) |

## Grounded + verified
Built via ctrl **/team**: a maker per artifact grounded in the skill-governance-block spec, each
independently refuted by `verify` on **schema-valid / signed-acts-host-only / planes-clean**. All
artifacts now accepted after fixing the schema-validity defects verify caught (ISO→`14d`/`30d`
durations; `grounding-access` demoted from spec-field to `actions[]` guard; `graded`→`auto` verdict).

## The stack, whole
**Loomground** (public skills: `loomground-versum` · `loomground-deontic` · `loomground-solver` ·
`loomground-governance` · `privacy-shield`) → an **enforcement
host** (governance-blocks + the signed gate) → **ctrl:legal** (orchestrates the vertical). This
repo ships the roles and the governance-blocks; it names no specific host and depends on none —
any host that reads the skill-governance-block spec (github.com/flxk1/skill-governance-block)
can enforce them.

## How this is made

The code and documentation are written with Loomground agents. The maintainer reads and corrects all of it.
