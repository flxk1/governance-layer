"""PART B (2), governance-layer half: `grounder` and `knowledge-steward` are bound to the new
coordinate tools `versum_coords`, `versum_cell`, `nd_resolve` (served by loomground-mcp, same
server/namespace as the existing `versum_*` tools these roles already reference), and each role's
grounding rule is explicit: only verification 'confirmed' counts as grounding; a candidate-tier
plane coordinate is unconfirmed and grounds nothing until a curator confirms it.

Covers the contract's TESTS clause: both roles list the three tools; the governance blocks
validate; compiled artifacts are in sync with sources (regeneration is a no-op — proven generally
by test_role_skills_tools.py::test_build_and_compile_are_idempotent_against_the_tracked_tree,
which this module's roles are a subset of); the grounding rule treats candidate as non-grounding.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from governance_layer.build_role_skills import ROLES
from governance_layer.validate_role_skills import SERVED_TOOLS, validate_root

REPO_ROOT = Path(__file__).resolve().parents[1]

NEW_TOOLS = ("versum_coords", "versum_cell", "nd_resolve")
BOUND_ROLE_NAMES = ("grounder", "knowledge-steward")


def _role(name: str) -> dict:
    return next(r for r in ROLES if r["name"] == name)


def _frontmatter(text: str) -> dict:
    end = text.find("\n---", 3)
    return yaml.safe_load(text[3:end]) or {}


def test_new_coordinate_tools_are_served():
    for t in NEW_TOOLS:
        assert t in SERVED_TOOLS, f"{t} missing from SERVED_TOOLS"


def test_grounder_and_knowledge_steward_declare_all_three_coordinate_tools_in_roles_source():
    for name in BOUND_ROLE_NAMES:
        tools = _role(name)["tools"]
        for t in NEW_TOOLS:
            assert t in tools, f"{name}: ROLES entry missing {t}"


def test_other_roles_are_not_granted_the_new_coordinate_tools():
    """The contract binds exactly `grounder` and `knowledge-steward` — no silent over-grant."""
    for role in ROLES:
        if role["name"] in BOUND_ROLE_NAMES:
            continue
        for t in NEW_TOOLS:
            assert t not in role["tools"], f"{role['name']}: unexpectedly granted {t}"


def test_generated_skill_md_declares_the_coordinate_tools_for_both_roles():
    for name in BOUND_ROLE_NAMES:
        path = REPO_ROOT / "skills" / name / "SKILL.md"
        fm = _frontmatter(path.read_text(encoding="utf-8"))
        declared = [t.strip() for t in (fm.get("allowed-tools") or "").split(",") if t.strip()]
        for t in NEW_TOOLS:
            assert t in declared, f"{name}/SKILL.md: allowed-tools missing {t}"


def test_governance_blocks_validate_against_the_schema():
    ok, lines, _ = validate_root(REPO_ROOT)
    assert ok, "\n".join(lines)


def test_grounder_governance_block_treats_candidate_as_non_grounding():
    block = _frontmatter((REPO_ROOT / "skills" / "grounder" / "SKILL.md").read_text(encoding="utf-8"))["governance"]
    assert "confirmed_coordinate_only" in block["obligations"]
    assert "assert_unconfirmed_coordinate_as_confirmed" in block["prohibited"]


def test_knowledge_steward_governance_block_treats_candidate_as_non_grounding():
    block = _frontmatter(
        (REPO_ROOT / "skills" / "knowledge-steward" / "SKILL.md").read_text(encoding="utf-8")
    )["governance"]
    assert "candidate_not_confirmed_until_curated" in block["obligations"]
    assert "present_candidate_as_confirmed" in block["prohibited"]
    # only curate_canon (reserved to the curator) mints the confirmed layer
    reserved_kinds = {r["kind"] for r in block["reserved"]}
    assert "curate_canon" in reserved_kinds


def test_no_vetted_tier_is_asserted_anywhere():
    """The repo has no pre-existing 'vetted' verification tier; only 'confirmed' grounds."""
    for name in ("roles.md", "agents/grounder.md", "agents/knowledge-steward.md"):
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        assert "vetted" not in text.lower(), f"{name}: unexpected 'vetted' tier"


def test_docs_state_candidate_is_explicitly_unconfirmed_for_both_roles():
    for name in ("roles.md", "agents/grounder.md", "agents/knowledge-steward.md"):
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        assert "candidate" in text.lower()
        assert "unconfirmed" in text.lower() or "UNCONFIRMED" in text
