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

## Known enforcement limits (REV1 pentest + 2-lane egress verification, 2026-09-06 — VERIFIED on origin/main 5dceee6)
The "RVND enforces each role's block" claim rests on **two** layers. Two separate limits, keep them apart:

- **Empty-footprint hook hole — a REAL engine gap (not by-design).** The PreToolUse hook's `classify()` does
  not model MCP-tool / WebFetch / WebSearch danger, so those get an **empty footprint** and the fast-benign
  path returns **ALLOW without ever reaching `action_gate`** — a silent `sys.exit(0)` permit. Offense proved
  it live at L2: `mcp__rvnd__workspace_erase`, a gmail send, a slack post, a WebFetch to an exfil URL, and
  WebSearch **all returned ALLOW, gate never called.** Worse than "not gated": under `RVND_HOOK_STRICT=1`
  those same calls return **ASK (human sign-off)**, so the fast-benign path **downgrades ASK → ALLOW,
  stripping the sign-off** (the in-code "loses nothing" comment is refuted on this build). So do **not** rely
  on the hook to gate a role's MCP-door acts or any WebFetch/WebSearch — enforcement of the MCP door rests on
  the **RVND MCP server's own server-side gate** (verify per `workspace_*` tool). *Incidental:* the
  Bash/irreversible path **does** enforce (a live `rm` probe was blocked); the gap is specific to the
  empty-footprint tool families. Recommended engine fix: model those families in `classify()`, or don't
  fast-benign them.
- **Egress is Tier-gated BY DESIGN (not a flaw).** The import guard is a **CI-only static scan with no
  runtime block** — but that is the documented tiering (`docs/concepts/air-gap-enforcement.md`): default
  install = Tier 1; load-bearing egress containment = the **operator OS firewall (Tier 3 / D4)**, a reserved
  deploy step. Treat cloud-LLM/egress containment as guaranteed **only with D4 applied**, not at the code layer.

Net: the **bundled-door fail-closed HOLDs and the `prohibited`/`reserved` severing are sound**, and the
Bash/irreversible path is gated. The gaps: (1) the hook does not gate — and actively downgrades ASK→ALLOW for
— the MCP/WebFetch/WebSearch classes (rely on the server-side gate; engine follow-up filed to the spine),
and (2) egress containment needs the D4 firewall. Track both in the readiness spine.

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
