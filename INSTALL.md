# Install — loomground-governance-roles

A real, normal-installer path. The seven roles are packaged as a **plugin** whose skills each carry a
**skill-governance-block** in frontmatter; the standard tooling installs them and **RVND enforces the
block**. Local-first throughout — nothing leaves the machine.

## What you get
`skills/<role>/SKILL.md` × 7 (grounder · legal-reasoner · knowledge-steward · lock-steward ·
policy-officer · auditor · local-grounder), each schema-valid against
`../skill-governance-block/schema/governance-block.schema.json`, plus `.claude-plugin/plugin.json`.

## Prerequisites (Tier 3 — installed once)
1. **RVND** — `pip install rvnd` (or the internal mirror), then `workspaces init` (foundations, keys,
   per-folder Ed25519 chains). Local-first: binds `127.0.0.1` only.
2. **A registered workspace** — `workspaces workspace add "<your-folder>"` (idempotent).
3. *(Optional, for grounding)* the **loomground engine** (versum / solver+kernel / deontic) + a served
   official corpus or the fetchers. *(Optional, for the semantic Privacy Lock)* a local model
   (`workspaces models pull <id>` / BYOK). The deterministic pattern-pass lock needs neither.

## Install (the normal installer)
1. **Add the plugin** (Tier 2) — enable `loomground-governance-roles` the standard way (marketplace /
   `enabledPlugins` in settings, or drop this folder in your plugins dir). Managed settings can pin it
   org-wide.
2. **Connect the governance server** — from your RVND checkout:
   ```bash
   ./scripts/connect-agent-hub.sh            # registers the RVND MCP + installs skills + the enforcement hook
   #   --hook monitor   (default: log verdicts, never block)   --hook enforce   (gate fail-closed)
   #   --scope user|project   ·   --dry-run
   ```
   This is idempotent and self-detecting.
3. **RVND now enforces each role's block.** When a role acts, its `governance:` block drives
   `action_gate.gate` → **GO / CONDITIONAL / NO-GO** on the signed chain: a below-grade act → CONDITIONAL,
   a `reserved` act → held for the named human, a `prohibited` kind → severed regardless of grade.
4. *(Operational, optional)* record the roles in the agent-registry via the `agent-governance-registry`
   skill (rows + 90-day reviews + kill-switch), mirroring `agent-registry.md`.

## Per-role identity — for per-role kill-switch, audit, and actor-named binds
RVND's hook resolves the acting agent from **`RVND_AGENT` first** (`hook.py:_agent`). `connect-agent-hub`
sets a fixed `RVND_AGENT=claude-code`, so by default **all 7 roles present to the gate as one actor**.
- **Still enforces under the shared identity** (identity-independent): the substantive verdicts — a block
  that gates actions (its `reserved` / `prohibited` / egress) fires **strictest-wins by action, not by who**.
  So the packaged roles govern correctly for permit/hold/deny even before you split identity.
- **Needs per-role identity** (anything keyed to the actor): per-role **kill-switch** (the breaker is
  per-actor — killing one would kill `claude-code` for all), per-role **audit attribution**, and any
  **actor-named grant/reservation** (our `.lg` declares `actor <role>` + `grant <role>` + `reserve X by
  <role>`). To bind these, run each role on a lane with **`RVND_AGENT=<role>`**.
- **⚠ Match the `.lg` actor id BYTE-FOR-BYTE.** RVND does **no** normalization (no case/hyphen folding), and
  the compiler emits the actor as the **underscore** form. So for the `lock-steward` skill the value is
  **`RVND_AGENT=lock_steward`** (underscore) — NOT the hyphenated skill name. Mirror whatever `skills/<role>/<role>.lg`
  declares. A mismatch fails **silently**: the actor-named rule just doesn't match and the action falls through to
  the generic gate outcome.
- **Prove it during the test:** with the per-lane `RVND_AGENT` set, dry-run one action the role's `reserve`/`grant`
  governs and confirm the verdict is the **role rule** (HOLD/deny as declared), not the default action-gate result.
  If it behaves like the generic default, the actor string didn't match.

## Verify
```bash
python3 packaging/validate_role_skills.py     # every block SCHEMA-VALID against the spec
```
Deeper check (SPEC §6): each block compiles to a **WELL-FORMED** Loomground `.lg` patch via the reference
validator (schema-passing is necessary, not sufficient). The role governance behaviour is proven against
the real `rvnd.action_gate` (see the proofs in the session scratchpad).

## Known enforcement limits (REV1 pentest, 2026-09-06 — read before relying on the gate)
The "RVND enforces each role's block" claim rests on **two** layers, and one has a hole:
- **PreToolUse hook** — REV1 found the hook classifier assigns an **empty footprint to every `mcp__*`,
  `WebFetch`, and `WebSearch` call**, so the hook's fast-benign path returns *allow* **without calling
  `action_gate`**. So the **hook layer does not gate the MCP door** (or WebFetch/WebSearch) — a role's
  MCP-door acts, and any tool in those classes, are **not** gated by the hook, even at L2.
- **RVND MCP server** — the `workspace_*` tools gate server-side. Enforcement of the MCP-door acts
  therefore rests on **that** gate, not the hook. **Verify server-side coverage** for the specific
  `workspace_*` tools a role uses before treating an MCP-door act as gated; do not assume the hook covers it.
- **Egress** is not contained at the code layer — the import guard is a **CI-only static AST scan, no
  runtime block**. Cloud-LLM/egress containment is load-bearing **only with the D4 OS firewall applied**
  (a reserved deploy step). The bundled skill door remains fail-closed (signs/egresses nothing) regardless.

Net: the **bundled-door fail-closed HOLDs and the `prohibited`/`reserved` severing are sound**; the gap is
that per-tool *hook* gating does not cover the MCP/WebFetch/WebSearch classes, and egress needs D4. Track
the fixes in the readiness spine (REV1).

## Reserved (a human's act, never the installer's, never the assistant's)
Anything that **grants authority or changes security posture** stays a reserved act you run:
- registering a *governed agent lane* at a granted grade (`governance_lane_register`, carries
  `approved_by` + `rationale`);
- provisioning / changing the Privacy Lock (`workspaces lock` / `init` / `threshold_set` / `seal`);
- registering a commercial connector (`connector_register`, credential **by reference**);
- flipping the enforcement hook to `enforce`.
The installer sets the roles up; **granting them authority and turning on teeth is yours.**

## Footprint
Baseline is a laptop, offline: host + plugin + `workspaces init` + pattern-pass lock + served corpus —
no model, no GPU, no network, no data egress. The semantic model and commercial connectors are later
add-ons, not gates.
