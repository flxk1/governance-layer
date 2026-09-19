"""build_role_skills — emit installable, schema-valid SKILL.md packages for the 7 governed roles.

Reproducible packaging: emits `../skills/<role>/SKILL.md` with the governance block in FRONTMATTER
matching the skill-governance-block spec (schema/governance-block.schema.json), so the NORMAL
installer (plugin install + an enforcement host's own connection step) installs them and the
enforcement host enforces the block.
Run: `python3 build_role_skills.py`  (idempotent). Then `validate_role_skills.py` checks the schema.
"""
from __future__ import annotations
from pathlib import Path

from .stamp import canonical_hash, stamp_line

# Each role: dict with the governance-block fields in STRUCTURED form (schema-correct).
# action = (kind, risk[, grade]); reserved = (kind, by_yaml); redress = (kind, by, overturn, within|None)
ROLES = [
 {"name": "grounder", "plane": "Loomground · ground (product)",
  "purpose": "Read-only evidence at coordinate + provenance, or ground-or-escalate. Serves; never writes. Product grounder — official versum only.",
  "use_when": "Use when a claim must be grounded against the official versum — 'ground this', 'is this in the corpus', 'give me the source for X at date D', 'confirm this against the graph'.",
  "grade": "L2",
  "actions": [("ground_query","low"),("read_evidence","low"),("emit_provenance_receipt","medium","L3")],
  "reserved": [],
  "prohibited": ["graph_write","binary_fetch","fabricate_citation","answer_from_model_memory","ground_from_private_folder"],
  "obligations": ["provenance_attached","coordinate_pinned","egress_checked","egress_payload_moat_safe","ingress_checked","official_versum_only","completeness_asserted"],
  "on_boundary": "escalate-with-named-axis",
  "redress": [("disputed_grounding","reviewer",True,None)],
  "budget": {"usd":1,"iters":20},
  "doors": "Host: a read-only grounding-evidence interface (provenance, ask, cross-workspace read). Bundled: portable read + ground-or-escalate; signs nothing."},

 {"name": "legal-reasoner", "plane": "Loomground · reason",
  "purpose": "Grounded premises to a warranted conclusion (apply, in-force, conflict, effect, deontic). Calls grounder first; enacts nothing alone.",
  "use_when": "Use when grounded premises must be argued to a conclusion — 'what follows from these provisions', 'is this permitted / obligatory / forbidden', 'which norm wins', 'how likely is liability'.",
  "grade": "L2",
  "actions": [("warrant_conclusion","medium"),("quantify_exposure","medium"),("emit_lg_patch","high","L3"),("release_disposition","critical","L4")],
  "reserved": [("release_disposition","{ quorum: 2, of: [legal_reviewer, policy_owner] }")],
  "prohibited": ["reason_over_unconfirmed","self_enact","parallel_grounding_layer"],
  "obligations": ["warrant_shown","premises_confirmed","grounding_called_first","egress_checked","egress_payload_moat_safe","completeness_asserted"],
  "on_boundary": "escalate-and-state-gap",
  "redress": [("released_disposition","affected_party",True,"14d")],
  "budget": {"usd":5,"iters":40},
  "doors": "Host: a legal-reasoning / lens / policy / coverage-matrix interface. release_disposition routes to the host's signed decision gate (reserved)."},

 {"name": "knowledge-steward", "plane": "Loomground · curate",
  "purpose": "Build and maintain the graph: ingest, concepts, placement, write, curate; enrich; erase. The one write/erase authority.",
  "use_when": "Use when material must enter, be curated in, or be erased from the graph — 'ingest this', 'add what we learned to the graph', 'curate the concepts', 'erase this subject'.",
  "grade": "L2",
  "actions": [("ingest_dryrun","low"),("extract_concepts","low"),("propose_placement","medium"),("graph_write","high","L3"),("curate_canon","high","L3"),("graph_erase","critical","L4")],
  "reserved": [("graph_erase","{ all: [data_protection_officer, workspace_owner] }"),("curate_canon","curator")],
  "prohibited": ["direct_write_bypassing_path","binary_fetch_in_session","invent_node","unlogged_mutation"],
  "obligations": ["single_write_path","dry_run_then_confirm","dedup_urn_sidecar","legal_basis_recorded","egress_checked","erase_egress_limit_disclosed"],
  "on_boundary": "quarantine-or-review-queue",
  "redress": [("graph_erase","subject",False,"30d"),("graph_write","workspace_owner",True,None)],
  "budget": {"usd":5,"iters":40},
  "doors": "Host: ingest / capture / memory / folder / mirror / erase interfaces. Writes append to the host's signed mutation chain (reserved)."},

 {"name": "lock-steward", "plane": "secure (host-enforced)",
  "purpose": "Provisions and discharges the per-folder egress lock (Privacy Lock). Manages the lock, never exempt. Ratchet + fail-secure.",
  "use_when": "Use when a folder's egress lock must be provisioned, checked, raised, lowered, or unsealed — 'lock this folder', 'lock status', 'egress-check this payload', 'unseal'.",
  "grade": "L2",
  "actions": [("lock_status","low"),("classify_content","low"),("propose_lock_profile","medium"),("egress_check","medium"),("ingress_check","medium"),("provision_lock","high","L3"),("raise_threshold","high","L3"),("lower_threshold","critical","L4"),("downgrade_backend","critical","L4"),("unseal","critical","L4")],
  "reserved": [("provision_lock","workspace_owner"),("lower_threshold","{ all: [workspace_owner, data_protection_officer] }"),("downgrade_backend","{ all: [workspace_owner, data_protection_officer] }"),("unseal","workspace_owner")],
  "prohibited": ["silent_mock_backend","weaken_without_distinct_party","assume_protected_on_unknown","egress_on_lock_unavailable","passphrase_in_context"],
  "obligations": ["secure_default_backend","no_silent_weakening","human_confirm_before_mutate","every_change_chained","provision_is_not_access","egress_check_not_self_waivable"],
  "on_boundary": "hold-and-explain",
  "redress": [("lower_threshold","workspace_owner",True,None),("provision_lock","workspace_owner",True,"30d")],
  "budget": {"usd":2,"iters":25},
  "doors": "Host: an egress-lock interface (setup/threshold/seal/classify/egress_check/ingress_check/audit_query). Mutations signed + reserved; bundled door HOLDs."},

 {"name": "policy-officer", "plane": "Loomground to enforcement host · govern",
  "purpose": "versum-policy to validated .lg to a human applying it. Makes known policy enforced. Know real-time; enforce-a-change reserved.",
  "use_when": "Use when a known policy must become enforced — 'compile this policy to .lg', 'validate this patch', 'apply this patch', 'rebind the lane'.",
  "grade": "L2",
  "actions": [("ground_policy","low"),("compile_lg_twin","medium"),("validate_patch","low"),("apply_patch","critical","L4"),("rebind_lane","high","L3")],
  "reserved": [("apply_patch","workspace_owner"),("rebind_lane","workspace_owner")],
  "prohibited": ["auto_apply_policy","enforce_unvalidated","self_widen_authority","silent_disable"],
  "obligations": ["litmus_classified","human_confirm_before_apply","fingerprint_pinned","validated_before_apply"],
  "on_boundary": "hand-off-or-escalate",
  "redress": [("apply_patch","workspace_owner",True,"14d")],
  "budget": {"usd":3,"iters":30},
  "doors": "Host: a policy-workflow interface (ingest/chat/validate/apply/open/lane-capabilities) plus a policy-declaration interface. apply_patch signed + reserved."},

 {"name": "auditor", "plane": "audit (host-enforced)",
  "purpose": "Read-only over the signed chain (verify_chain/tail/shadow_scan/discipline). Writes nothing but an attributed override. Reports, never repairs.",
  "use_when": "Use when the signed chain must be verified or reported on — 'verify the chain', 'tail the chain', 'shadow scan', 'discipline check', 'record an override'.",
  "grade": "L2",
  "actions": [("verify_chain","low"),("tail_chain","low"),("get_event","low"),("shadow_scan","low"),("discipline","low"),("record_override","medium")],
  "reserved": [],
  "prohibited": ["mutate_graph","mutate_policy","sign_content","repair_in_place"],
  "obligations": ["read_only_default","chain_verified_before_report","rationale_on_override","findings_not_masked"],
  "on_boundary": "report-not-repair",
  "redress": [("recorded_override","workspace_owner",True,None)],
  "budget": {"usd":1,"iters":30},
  "doors": "Host: a read-only audit interface (verify/tail/get-event/shadow-scan/discipline/overrides/record-override). record_override is the only append."},

 {"name": "local-grounder", "plane": "Loomground · ground (private) — LOCAL-ONLY",
  "purpose": "Grounds Felix's own work over his private knowledge folder. Firewalled from the product: never ships, never a product dependency, output never reaches the official versum.",
  "use_when": "Use when Felix's own work must be grounded over his private knowledge folder — 'ground this against my private notes', 'read my private evidence'.",
  "grade": "L2",
  "actions": [("ground_private","low"),("read_private_evidence","low")],
  "reserved": [],
  "prohibited": ["feed_product_grounding","write_to_official_versum","egress_private_content","ship"],
  "obligations": ["local_only","private_stays_private","firewalled_from_product","separate_store"],
  "on_boundary": "hold-local",
  "redress": [("private_grounding","felix",True,None)],
  "budget": {"usd":1,"iters":20},
  "doors": "No MCP / no signing / no product seam. A local reader over the private folder (Obsidian / local versum / local RAG)."},
]


def _action(a):
    if len(a) == 3:
        return f"    - {{ kind: {a[0]}, risk: {a[1]}, grade: {a[2]} }}\n"
    return f"    - {{ kind: {a[0]}, risk: {a[1]} }}\n"


def _reserved(r):
    return f"    - {{ kind: {r[0]}, by: {r[1]} }}\n"


def _redress(r):
    kind, by, overturn, within = r
    s = f"    - {{ kind: {kind}, by: {by}"
    if overturn is not None:
        s += f", overturn: {str(overturn).lower()}"
    if within:
        s += f", within: {within}"
    return s + " }\n"


def _list(key, items):
    if not items:
        return f"  {key}: []\n"
    return f"  {key}:\n" + "".join(f"    - {i}\n" for i in items)


def _governance(role) -> str:
    g = "governance:\n"
    g += f"  grade: {role['grade']}\n"
    g += "  actions:\n" + "".join(_action(a) for a in role["actions"])
    g += ("  reserved: []\n" if not role["reserved"]
          else "  reserved:\n" + "".join(_reserved(r) for r in role["reserved"]))
    g += _list("prohibited", role["prohibited"])
    g += _list("obligations", role["obligations"])
    g += ("  redress: []\n" if not role["redress"]
          else "  redress:\n" + "".join(_redress(r) for r in role["redress"]))
    b = role["budget"]
    g += f"  budget: {{ {', '.join(f'{k}: {v}' for k, v in b.items())} }}\n"
    g += f"  on-boundary: {role['on_boundary']}\n"
    return g


def build(root: Path | None = None):
    """EMIT skills/<role>/SKILL.md under `root` (default CWD). Every file is stamped with
    tool+version+input_sha256; the input is the role's canonical source. L0: emits a diff, never
    auto-applies — a human reviews and lands it."""
    out = Path(root or Path.cwd()).resolve() / "skills"
    written = []
    for role in ROLES:
        input_sha256 = canonical_hash(role)
        d = out / role["name"]; d.mkdir(parents=True, exist_ok=True)
        desc = f"{role['purpose']} {role['use_when']}".replace('"', "'")   # quote-safe: descriptions carry colons
        fm = (f"---\nname: {role['name']}\n"
              f"description: \"{desc}\"\n"
              f"metadata: {{ provenance: {{ stamp: \"{stamp_line(input_sha256)}\" }} }}\n"
              f"{_governance(role)}"
              "---\n")
        body = (f"\n# {role['name']}\n\n**Plane:** {role['plane']}\n\n{role['purpose']}\n\n"
                f"**Doors.** {role['doors']}\n\n"
                "## Governance identity\n"
                "The `governance:` block above is the whole of this skill's authority. A skill is universal; "
                "the block turns it into a governed **role** that ctrl plans on and an **enforcement "
                "host enforces** "
                "(a signed verdict on the host's hash-chain -- auto / human / reserved / prohibited, "
                "joined strictest-wins), and the agent-registry records. Reserved acts hold for a human; "
                "prohibited kinds are severed regardless of grade.\n")
        (d / "SKILL.md").write_text(fm + body, encoding="utf-8")
        rel = (d / "SKILL.md").relative_to(out.parent)
        written.append(str(rel))
        print("built (emitted, review the diff)", rel)
    return written


def main(root: Path | None = None):
    return build(root)


if __name__ == "__main__":
    main()
