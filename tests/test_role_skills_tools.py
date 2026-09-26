"""L2: every role's `allowed-tools` — non-empty, single-sourced from `ROLES`, every name a
served tool, no write tool for a role whose block prohibits generic writing — and the build is
idempotent (a fresh build/compile equals the tracked tree)."""
from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from governance_layer import build_role_skills, compile_block_to_lg
from governance_layer.build_role_skills import ROLES
from governance_layer.validate_role_skills import (
    GENERIC_WRITE_BAN_KINDS,
    SERVED_TOOLS,
    WRITE_TOOLS,
    validate_root,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _frontmatter(text: str) -> dict:
    end = text.find("\n---", 3)
    return yaml.safe_load(text[3:end]) or {}


@pytest.mark.parametrize("role", ROLES, ids=[r["name"] for r in ROLES])
def test_role_declares_a_non_empty_tools_list_in_the_single_source(role):
    assert role.get("tools"), f"{role['name']}: ROLES entry has no tools"
    assert len(role["tools"]) == len(set(role["tools"])), f"{role['name']}: duplicate tool grant"


@pytest.mark.parametrize("role", ROLES, ids=[r["name"] for r in ROLES])
def test_every_tool_is_a_served_loomground_mcp_tool(role):
    unknown = [t for t in role["tools"] if t not in SERVED_TOOLS]
    assert not unknown, f"{role['name']}: allowed-tools names an unserved tool: {unknown}"


@pytest.mark.parametrize("role", ROLES, ids=[r["name"] for r in ROLES])
def test_no_write_tool_for_a_role_that_prohibits_writing(role):
    prohibits_writing = any(k in GENERIC_WRITE_BAN_KINDS for k in role["prohibited"])
    if not prohibits_writing:
        pytest.skip(f"{role['name']} does not prohibit a generic writing kind")
    granted_write_tools = [t for t in role["tools"] if t in WRITE_TOOLS]
    assert not granted_write_tools, (
        f"{role['name']} prohibits writing but is granted {granted_write_tools}")


def test_grounder_and_local_grounder_and_auditor_never_get_a_write_tool():
    """The named case from the contract: a role whose whole point is read-only must never be
    granted the tools whose only effect is a graph mutation."""
    for name in ("grounder", "local-grounder", "auditor"):
        role = next(r for r in ROLES if r["name"] == name)
        granted = set(role["tools"]) & WRITE_TOOLS
        assert not granted, f"{name} must never get {granted}"


def test_generated_skill_md_declares_allowed_tools_matching_roles_single_source():
    for role in ROLES:
        path = REPO_ROOT / "skills" / role["name"] / "SKILL.md"
        fm = _frontmatter(path.read_text(encoding="utf-8"))
        declared = [t.strip() for t in (fm.get("allowed-tools") or "").split(",") if t.strip()]
        assert declared == role["tools"], f"{role['name']}: SKILL.md allowed-tools drifted from ROLES"


def test_no_generated_skill_md_names_the_non_public_internal_skills():
    """No generated SKILL.md may refer to `grounding/SKILL.md`, `reasoning/SKILL.md`, or
    `knowledge-management` as a skill name — those are not public skills; a role's SKILL.md must
    bind to the public skill that actually serves its tools instead (or say plainly that none
    does), inventing no new name."""
    banned = ("grounding/SKILL.md", "reasoning/SKILL.md", "knowledge-management")
    for role in ROLES:
        path = REPO_ROOT / "skills" / role["name"] / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        for b in banned:
            assert b not in text, f"{role['name']}/SKILL.md names {b!r}"


def test_validate_role_skills_accepts_the_generated_allowed_tools():
    ok, lines, _ = validate_root(REPO_ROOT)
    assert ok, "\n".join(lines)
    assert any("allowed-tools" in ln for ln in lines)


def test_build_and_compile_are_idempotent_against_the_tracked_tree():
    """A fresh `build` + `compile` into a scratch root reproduces the tracked `skills/` tree
    byte-for-byte (SPEC §4 determinism + the L0 'emits a diff, never auto-applies' contract:
    the diff, run again, must be empty)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build_role_skills.build(root=root)
        compile_block_to_lg.compile_root(root)
        for role in ROLES:
            for fname in (f"{role['name']}/SKILL.md", f"{role['name']}/{role['name']}.lg"):
                tracked = (REPO_ROOT / "skills" / fname).read_text(encoding="utf-8")
                fresh = (root / "skills" / fname).read_text(encoding="utf-8")
                # a fresh build's stamp line's timestamp-free provenance (tool/version/input hash)
                # must match; the input hash for build's SKILL.md is over the ROLE dict, stable
                # across a run, so the two texts should be identical outright.
                assert fresh == tracked, f"{fname}: build/compile is not idempotent"
