# Install — loomground-governance-roles

A real, normal-installer path. The seven roles are packaged as a **plugin** whose skills each carry a
**skill-governance-block** in frontmatter; the standard tooling installs them, and any conformant
**enforcement host enforces the block**. Local-first throughout — nothing leaves the machine.

## What you get
`skills/<role>/SKILL.md` × 7 (grounder · legal-reasoner · knowledge-steward · lock-steward ·
policy-officer · auditor · local-grounder), each schema-valid against
`../skill-governance-block/schema/governance-block.schema.json`, plus `.claude-plugin/plugin.json`.

## Prerequisites (Tier 3 — installed once)
1. **An enforcement host** that speaks the skill-governance-block spec
   (github.com/flxk1/skill-governance-block) — install and initialize it per its own
   documentation (foundations, keys, per-folder signed chains). This repo names no specific host
   and depends on none; it declares the governance-blocks a conformant host reads. Local-first
   hosts bind to loopback only.
2. **A registered workspace** — with your chosen host, register this folder the way its own
   documentation describes (idempotent).
3. *(Optional, for grounding)* the **loomground engine** (versum / solver+kernel / deontic) + a served
   official corpus or the fetchers. *(Optional, for the semantic Privacy Lock)* a local model, per
   your host's own model-provisioning step. The deterministic pattern-pass lock needs neither.

## Install (the normal installer)
1. **Add the plugin** (Tier 2) — enable `loomground-governance-roles` the standard way (marketplace /
   `enabledPlugins` in settings, or drop this folder in your plugins dir). Managed settings can pin it
   org-wide.
2. **Connect your enforcement host** — follow its own connection procedure to register the
   block-reading hook (it registers the door, installs the skills, and wires its own enforcement
   hook). This repo ships no connector script; it ships the roles and their governance-blocks for
   any conformant host to read.
3. **The host now enforces each role's block.** When a role acts, its `governance:` block drives
   the host's signed decision gate to a Loomground verdict (`auto / human / reserved / prohibited`,
   joined strictest-wins): a below-grade act → `human`, a `reserved` act → held for the named
   human, a `prohibited` kind → severed regardless of grade.
4. *(Operational, optional)* record the roles in the agent-registry via the `agent-governance-registry`
   skill (rows + 90-day reviews + kill-switch), mirroring `agent-registry.md`.

## Per-role identity — for per-role kill-switch, audit, and actor-named binds
Most hosts resolve the acting agent from an identity signal of their own (an env var, a session
join, a header) — consult your host's docs for which one, and how to set it per role.
- **Still enforces under a shared identity** (identity-independent): the substantive verdicts — a
  block that gates actions (its `reserved` / `prohibited` / egress) fires **strictest-wins by
  action, not by who**. So the packaged roles govern correctly for permit/hold/deny even before
  you split identity.
- **Needs per-role identity** (anything keyed to the actor): per-role **kill-switch** (a breaker
  bound to a shared identity would kill every role at once, not just one), per-role **audit
  attribution**, and any **actor-named grant/reservation** (our `.lg` declares `actor <role>` +
  `grant <role>` + `reserve X by <role>`). To bind these, run each role under a distinct per-role
  identity.
- **⚠ Match the `.lg` actor id BYTE-FOR-BYTE.** Do not assume your host normalizes case or hyphens
  — the compiler emits the actor as the **underscore** form. So for the `lock-steward` skill the
  identity value is **`lock_steward`** (underscore) — NOT the hyphenated skill name. Mirror
  whatever `skills/<role>/<role>.lg` declares. A mismatch fails **silently**: the actor-named rule
  just doesn't match and the action falls through to the generic gate outcome.
- **Prove it during the test:** with the per-role identity set, dry-run one action the role's
  `reserve`/`grant` governs and confirm the verdict is the **role rule** (held/denied as declared),
  not the default gate result. If it behaves like the generic default, the identity string
  didn't match.

## Verify
```bash
pip install -e .
governance-layer validate   # every block SCHEMA-VALID against the spec (the G9 gate)
```
Deeper check (SPEC §6): each block compiles to a **WELL-FORMED** Loomground `.lg` patch via the
reference validator (schema-passing is necessary, not sufficient). The role governance behaviour
proven at build time was proven against one enforcement host under test — verify it again against
whichever host you connect, before relying on it.

## Known enforcement limits — verify before you rely on them
"An enforcement host enforces each role's block" rests on the host's own PreToolUse-style hook (or
equivalent) reaching the signed decision gate for **every** action class your roles can take —
not only the ones tested first. Two things worth checking on any host before you rely on it:

- **Coverage of low-visibility action classes.** A hook that classifies actions by an apparent
  footprint can under-model tool calls, external fetches, and searches — giving them an "empty
  footprint" that a fast-path allows without ever reaching the gate. Confirm your host's hook
  models every action class your roles can reach, not just the obviously dangerous ones, and that
  an *unavailable or unknown* classification floors to the weaker-safer verdict (never a false
  `auto`) — this is the load-bearing test the skill-governance-block spec requires of a
  conforming enforcer (SPEC §7).
- **Egress containment is a deployment tier, not a code guarantee, on most hosts.** Treat
  cloud-model / network egress containment as guaranteed only once your host's own documented
  deployment tier for it is applied (commonly an OS-level network boundary) — not merely because
  the code imports look clean in review.

Net: the roles' `prohibited`/`reserved` severing is sound by construction (skill-governance-block
SPEC §7's four load-bearing verdicts); whether your specific host's hook actually reaches the gate
for every action class, and whether egress containment is deployed at its documented tier, are
per-host facts to verify, not claims this repo can make on your host's behalf.

## Reserved (a human's act, never the installer's, never the assistant's)
Anything that **grants authority or changes security posture** stays a reserved act you run, via
your host's own tooling:
- registering a *governed agent lane* at a granted grade (carries an approver + rationale);
- provisioning / changing the egress lock (setup / threshold / seal);
- registering a commercial connector (credential **by reference**);
- flipping the enforcement hook from monitor to enforce.
The installer sets the roles up; **granting them authority and turning on teeth is yours.**

## Footprint
Baseline is a laptop, offline: host + plugin + your enforcement host's own init step + pattern-pass
lock + served corpus — no model, no GPU, no network, no data egress. The semantic model and
commercial connectors are later add-ons, not gates.
