# Governance-layer toolchain

**ID:** governance-layer-toolchain
**Skill:** governance-layer `packaging/` (compile / build / validate)
**Owner:** Felix (flxk1)
**Autonomy grade:** L0 — no unattended action; `build`/`compile` emit a human-reviewed diff and are never auto-run; `validate` is read-only and the only entry point safe unattended
**Last reviewed:** 2026-09-06

## Purpose
The skill-governance-block toolchain: it **builds** the governed role SKILL.md packages
(`build_role_skills`), **compiles** each role's governance block to a Loomground `.lg` patch
(`compile_block_to_lg`), and **validates** those blocks against the skill-governance-block schema
(`validate_role_skills`). It mints the `.lg` declarations RVND and the agent-registry treat as
**ground truth** — so the tool that produces them must itself be governed.

## Scope
**In scope (why):** emit/refresh role SKILL.md packages; compile governance blocks → `.lg`;
schema-validate the blocks. Deterministic, reproducible, idempotent packaging over local source.
**Out of scope (why):** applying a `.lg` patch (that is `policy-officer`'s reserved
`apply_patch`); writing to the graph; any network/egress; deciding policy semantics (delegated to
the Loomground validator). This tool produces artefacts for human review; it enforces nothing.

## Trigger
Run on demand by a human when a role's governance block changes. **Never on cron/CI as an actor.**
CI may run `validate` (read-only) as a gate; CI must NOT run `build`/`compile` and commit their
output — those are a reviewed diff a human lands.

## Grade — unattended vs held
- **Read-only, unattended-safe (`validate`):** checks blocks against the schema, exits non-zero on
  failure. No writes. This is the G9 gate other packages' CI calls.
- **L0, human-reviewed diff (`build`, `compile`):** write `skills/<role>/SKILL.md` and
  `<role>.lg`. They emit; a human reviews the diff and lands it. Never auto-applied, never the
  authoritative source without that review.

## Reserved / Prohibited
- **Reserved:** landing (committing) generated SKILL.md / `.lg` output — a human act; and
  `apply_patch` (out of scope — belongs to `policy-officer`).
- **Prohibited:** auto-running `build`/`compile` in cron/CI and treating the output as applied;
  editing a compiled `.lg` by hand (they are generated — `# do not edit by hand`); network/egress;
  emitting an unstamped artefact.

## Obligations (output contract)
- **Stamp every artefact** (compiled `.lg`, validation report) with `tool name + version + input
  hash`, so "who/what produced this governance artefact, from what input" is always answerable.
- **Semver the compile/validate output contract**; keep a CHANGELOG; a contract change is a
  deliberate, versioned bump (downstream `.lg` consumers pin against it).
- Validation is **necessary but not sufficient** (SPEC §6): schema-pass AND the compiled `.lg`
  WELL-FORMED via the Loomground reference validator.

## Budget
`usd: 0` (local, deterministic; no model calls), `iters: n/a` (single-shot).

## Failure modes
1. *Silent drift* — `build`/`compile` auto-run in CI, output committed unreviewed; a governance
   block change ships without human sight. Notices: L0 gate (build/compile never unattended) + the
   reviewed-diff requirement. Blast radius: a wrong `.lg` becomes RVND ground truth.
2. *Unprovenanced artefact* — a `.lg` with no tool/version/input-hash stamp; "which tool version,
   from what block, produced this?" is unanswerable. Notices: the stamping obligation + a CI check
   that every emitted artefact carries a stamp.
3. *Stale contract* — the output contract changes without a semver bump; downstream `.lg`
   consumers break silently. Notices: semver + CHANGELOG obligation.
4. *False-valid* — schema passes but the `.lg` is not well-formed. Notices: SPEC §6 (validity =
   schema-pass AND Loomground-validator well-formed), run as a two-step gate.
</content>
