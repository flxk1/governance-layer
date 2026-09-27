"""tests/test_compiler_parity.py — the one-implementation rule, governance-layer side
(contract item 3). `skill-governance-block/reference/compile_block_to_lg.py` is the
canonical reference compiler for SPEC §4 (see that repo's README.md "Canonical compiler"
section and `reference/__init__.py`'s "Canonical-compiler decision"). That decision records
that governance-layer is *not* made to import it — doing so is out of the sgb leg's
territory — so governance-layer keeps its own copy (see `compile_block_to_lg.py`'s module
docstring, "canonical at ... this is a parity-tested copy").

This test is the parity proof that decision depends on: for every one of governance-layer's
7 declared role blocks (`skills/*/SKILL.md`) plus sgb's own worked example
(`skill-governance-block/examples/finalise-change.md`) — 8 cases total — both compilers must
produce byte-identical `.lg` text from the same block dict.

The sibling checkout is located via `GOVERNANCE_LAYER_SGB_PATH`, defaulting to
`../skill-governance-block` relative to this repo's root. This module skips — with the
reason stated — ONLY when that directory is absent; it must otherwise run.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest
import yaml

from governance_layer.build_role_skills import ROLES
from governance_layer.compile_block_to_lg import compile_block as gl_compile_block

REPO_ROOT = Path(__file__).resolve().parents[1]
SGB_ROOT = Path(
    os.environ.get("GOVERNANCE_LAYER_SGB_PATH", str(REPO_ROOT / ".." / "skill-governance-block"))
).resolve()

pytestmark = pytest.mark.skipif(
    not SGB_ROOT.is_dir(),
    reason=(
        f"sibling checkout not found at {SGB_ROOT} (set GOVERNANCE_LAYER_SGB_PATH to point at a "
        "skill-governance-block checkout); this module skips ONLY when the sibling is absent"
    ),
)


def _load_sgb_compile_block():
    """Import skill-governance-block's canonical `reference.compile_block_to_lg.compile_block`.
    `reference` is a package (its `compile_block_to_lg.py` does `from .stamp import ...`), so it
    is imported as a real package off a scoped `sys.path` entry rather than via a single-file
    importlib spec.
    """
    sgb_str = str(SGB_ROOT)
    if sgb_str not in sys.path:
        sys.path.insert(0, sgb_str)
    for modname in ("reference", "reference.compile_block_to_lg", "reference.stamp"):
        sys.modules.pop(modname, None)
    mod = importlib.import_module("reference.compile_block_to_lg")
    return mod.compile_block


SGB_COMPILE_BLOCK = _load_sgb_compile_block() if SGB_ROOT.is_dir() else None


def _role_block(role: dict) -> dict:
    """The structured ROLES entry, reshaped into the block dict `compile_block` expects
    (mirrors tests/test_compile_block_to_lg.py::_role_block, kept identical on purpose)."""

    def action(a):
        return {"kind": a[0], "risk": a[1], **({"grade": a[2]} if len(a) == 3 else {})}

    def reserved(r):
        return {"kind": r[0], "by": yaml.safe_load(r[1])}

    def redress(r):
        kind, by, overturn, within = r
        d = {"kind": kind, "by": by}
        if overturn is not None:
            d["overturn"] = overturn
        if within:
            d["within"] = within
        return d

    return {
        "grade": role["grade"],
        "actions": [action(a) for a in role["actions"]],
        "reserved": [reserved(r) for r in role["reserved"]],
        "prohibited": role["prohibited"],
        "obligations": role["obligations"],
        "redress": [redress(r) for r in role["redress"]],
    }


ROLE_CASES = [(role["name"], _role_block(role)) for role in ROLES]


def _finalise_change_case():
    md_path = SGB_ROOT / "examples" / "finalise-change.md"
    md_text = md_path.read_text(encoding="utf-8")
    start = md_text.find("```yaml\n")
    assert start != -1, "no ```yaml fenced governance block found in finalise-change.md"
    start += len("```yaml\n")
    end = md_text.find("```", start)
    assert end != -1, "unterminated ```yaml fenced block in finalise-change.md"
    doc = yaml.safe_load(md_text[start:end])
    return "finalise-change", doc["governance"]


ALL_CASES = ROLE_CASES + ([_finalise_change_case()] if SGB_ROOT.is_dir() else [])


def test_eight_cases_covered():
    """7 role blocks + sgb's own worked example, per the contract."""
    assert len(ALL_CASES) == 8
    assert {n for n, _ in ROLE_CASES} == {r["name"] for r in ROLES}
    assert ALL_CASES[-1][0] == "finalise-change"


@pytest.mark.parametrize("name,block", ALL_CASES, ids=[n for n, _ in ALL_CASES])
def test_governance_layer_and_sgb_reference_are_byte_identical(name, block):
    gl_out = gl_compile_block(name, block)
    sgb_out = SGB_COMPILE_BLOCK(name, block)
    assert gl_out == sgb_out
