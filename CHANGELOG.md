# Changelog

All notable changes to the governance-layer toolchain output contract are recorded here.
The compile/validate output contract is semver'd; a contract change is a deliberate, versioned
bump (downstream `.lg` consumers pin against it).

## [0.1.0] — 2026-09-06

Initial install-ready (LIGHT) package.

### Added
- PEP 621 `pyproject.toml` (setuptools), src-layout package `governance_layer`, console entry
  point `governance-layer = governance_layer.cli:main`.
- CLI subcommands honouring the L0 grade:
  - `validate` — READ-ONLY schema-check of role governance blocks (the G9 gate); non-zero on failure.
  - `build` / `compile` — EMIT a human-reviewed diff into `<root>/skills`; never auto-apply.
  - `--root` (default CWD) so the installed CLI works outside the source tree.
- Output-contract **stamping**: every compiled `.lg`, every built SKILL.md, and every validation
  report carries `tool=governance-layer version=<ver> input_sha256=<hash>`.
- Bundled `governance-block.schema.json` as package-data, resolved via `importlib.resources`
  (replaces the sibling-repo path dependency). Provenance (source repo, commit, sha256) recorded in
  `schema_provenance.json`.

### Notes
- Schema-pass is NECESSARY but not SUFFICIENT (SPEC §6): full validity also requires the compiled
  `.lg` to be WELL-FORMED via the Loomground reference validator.
