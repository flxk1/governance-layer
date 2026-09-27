"""compile_block_to_lg — SPEC §4 shape: no `release` gate, one `cord <kind> -> master` per
action, every action gate granted to the actor. Literal expected output for `grounder` (the
smallest role with a redress line); structural checks for all seven. The evaluator-backed check
runs only if a Loomground reference implementation is importable from a path this test is told
about — skipped, with the reason stated, otherwise (no reference is vendored into this repo).
"""
from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path

import pytest

from governance_layer.build_role_skills import ROLES
from governance_layer.compile_block_to_lg import compile_block

REPO_ROOT = Path(__file__).resolve().parents[1]

GROUNDER_BLOCK = {
    "grade": "L2",
    "actions": [
        {"kind": "ground_query", "risk": "low"},
        {"kind": "read_evidence", "risk": "low"},
        {"kind": "emit_provenance_receipt", "risk": "medium", "grade": "L3"},
    ],
    "reserved": [],
    "prohibited": ["graph_write", "binary_fetch", "fabricate_citation",
                   "answer_from_model_memory", "ground_from_private_folder"],
    "obligations": ["provenance_attached", "coordinate_pinned", "egress_checked",
                     "egress_payload_moat_safe", "ingress_checked", "official_versum_only",
                     "completeness_asserted"],
    "redress": [{"kind": "disputed_grounding", "by": "reviewer", "overturn": True}],
}

EXPECTED_GROUNDER_LG = """\
# grounder.lg — compiled from the governance block (SPEC §4). Generated; do not edit by hand.
human reviewer role reviewer
actor grounder grade L2

gate ground_query risk low grant grounder
gate read_evidence risk low grant grounder
gate emit_provenance_receipt risk medium grade L3 grant grounder

cord grounder -> ground_query
cord grounder -> read_evidence
cord grounder -> emit_provenance_receipt
cord ground_query -> master
cord read_evidence -> master
cord emit_provenance_receipt -> master

prohibit graph_write
prohibit binary_fetch
prohibit fabricate_citation
prohibit answer_from_model_memory
prohibit ground_from_private_folder
obligation provenance_attached on ground_query
obligation provenance_attached on read_evidence
obligation provenance_attached on emit_provenance_receipt
obligation coordinate_pinned on ground_query
obligation coordinate_pinned on read_evidence
obligation coordinate_pinned on emit_provenance_receipt
obligation egress_checked on ground_query
obligation egress_checked on read_evidence
obligation egress_checked on emit_provenance_receipt
obligation egress_payload_moat_safe on ground_query
obligation egress_payload_moat_safe on read_evidence
obligation egress_payload_moat_safe on emit_provenance_receipt
obligation ingress_checked on ground_query
obligation ingress_checked on read_evidence
obligation ingress_checked on emit_provenance_receipt
obligation official_versum_only on ground_query
obligation official_versum_only on read_evidence
obligation official_versum_only on emit_provenance_receipt
obligation completeness_asserted on ground_query
obligation completeness_asserted on read_evidence
obligation completeness_asserted on emit_provenance_receipt
redress disputed_grounding by reviewer overturn
"""


def test_grounder_lg_matches_literal_spec4_shape():
    out = compile_block("grounder", GROUNDER_BLOCK)
    assert out == EXPECTED_GROUNDER_LG


def _role_block(role: dict) -> dict:
    """The structured ROLES entry, reshaped into the block dict `compile_block` expects
    (mirrors `build_role_skills._governance`'s own field mapping)."""
    def action(a):
        return {"kind": a[0], "risk": a[1], **({"grade": a[2]} if len(a) == 3 else {})}

    def reserved(r):
        import yaml
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


ALL_ROLE_BLOCKS = [(role["name"], _role_block(role)) for role in ROLES]


@pytest.mark.parametrize("name,block", ALL_ROLE_BLOCKS, ids=[n for n, _ in ALL_ROLE_BLOCKS])
def test_no_release_gate_or_cord(name, block):
    out = compile_block(name, block)
    # a bare `release` token (the removed gate/cord endpoint) — not a substring of a legitimate
    # action name such as `release_disposition`
    assert not re.search(r"(?<![\w-])release(?![\w-])", out)
    assert not re.search(r"^gate release\b", out, re.M)
    assert not re.search(r"->\s*release\b", out, re.M)


@pytest.mark.parametrize("name,block", ALL_ROLE_BLOCKS, ids=[n for n, _ in ALL_ROLE_BLOCKS])
def test_exactly_one_cord_to_master_per_action(name, block):
    out = compile_block(name, block)
    master_cords = re.findall(r"^cord (\S+) -> master$", out, re.M)
    assert sorted(master_cords) == sorted(a["kind"] for a in block["actions"])
    assert len(master_cords) == len(set(master_cords))


@pytest.mark.parametrize("name,block", ALL_ROLE_BLOCKS, ids=[n for n, _ in ALL_ROLE_BLOCKS])
def test_every_action_gate_granted_to_the_actor(name, block):
    out = compile_block(name, block)
    actor = name.replace("-", "_")
    for a in block["actions"]:
        assert re.search(rf"^gate {re.escape(a['kind'])} risk \S+(?: grade \S+)? grant {actor}$",
                          out, re.M), out


@pytest.mark.parametrize("name,block", ALL_ROLE_BLOCKS, ids=[n for n, _ in ALL_ROLE_BLOCKS])
def test_no_other_node_or_cord(name, block):
    """SPEC §4: exactly actor + source gates + human roles, and authority/egress cords only —
    no pipe (gate -> gate) cord."""
    out = compile_block(name, block)
    kinds = {a["kind"] for a in block["actions"]}
    for m in re.finditer(r"^cord (\S+) -> (\S+)$", out, re.M):
        frm, to = m.groups()
        assert to == "master" or to in kinds  # authority cords land on an action gate
        if to != "master":
            assert frm == name.replace("-", "_")  # only the actor cords into an action gate


def _load_loomground_ref():
    """A Loomground reference implementation, if this environment names one. Never a hardcoded
    session-scratch path — set GOVERNANCE_LAYER_LOOMGROUND_REF to a directory holding
    `loomground.py` to run the evaluator-backed checks."""
    ref_dir = os.environ.get("GOVERNANCE_LAYER_LOOMGROUND_REF")
    if not ref_dir or not (Path(ref_dir) / "loomground.py").is_file():
        return None
    spec = importlib.util.spec_from_file_location("loomground_ref", Path(ref_dir) / "loomground.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["loomground_ref"] = mod
    spec.loader.exec_module(mod)
    return mod


LOOMGROUND_REF = _load_loomground_ref()


@pytest.mark.skipif(LOOMGROUND_REF is None,
                     reason="GOVERNANCE_LAYER_LOOMGROUND_REF not set to a checkout with loomground.py; "
                            "no reference evaluator is vendored into this repo")
@pytest.mark.parametrize("name,block", ALL_ROLE_BLOCKS, ids=[n for n, _ in ALL_ROLE_BLOCKS])
def test_compiled_patch_is_well_formed_and_reaches_master(name, block):
    L = LOOMGROUND_REF
    out = compile_block(name, block)
    graph = L.check(L.parse(out))
    actor = name.replace("-", "_")
    reserved_kinds = {r["kind"] for r in block["reserved"]}
    for a in block["actions"]:
        tok = dict(id="t1", kind=a["kind"], risk=a["risk"], party="deployer", provenance=[])
        res, _ = L.evaluate(graph, [dict(actor=actor, source=a["kind"], token=tok)])
        verdict = res[a["kind"]]["verdict"]
        master = res[a["kind"]].get("master")
        if a["kind"] in reserved_kinds:
            assert verdict == "reserved" and master == "withhold"
        elif a.get("grade") and a["grade"] != block["grade"]:
            assert verdict == "human" and master == "withhold"
        else:
            assert verdict == "auto" and master == "act"
    for kind in block["prohibited"]:
        first = block["actions"][0]
        tok = dict(id="t1", kind=kind, risk=first["risk"], party="deployer", provenance=[])
        res, _ = L.evaluate(graph, [dict(actor=actor, source=first["kind"], token=tok)])
        assert res[first["kind"]]["verdict"] == "prohibited"
        assert res[first["kind"]]["master"] == "withhold"
