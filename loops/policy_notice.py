"""LG2 — the real-time policy-notice feed (NOTICE stage of the X1 policy-control loop).

Fires when policy is ingested/changed in versum and ROUTES a notice to the policy-officer.
It is a WATCH, not an actor: it never fetches in-session, never compiles a .lg twin, and never
applies policy. NOTICE is real-time; ENFORCE-a-change stays the reserved human patch_apply
downstream (policy-officer). Fail-closed: unconfirmed policy is HELD (noticed, not routed);
a malformed item is quarantined; a repeal is flagged for retire (tighten), never auto-removed.

Consume-only. The diff is supplied out-of-band (the ingest plane's own change feed); this module
decides, from each item's coordinate, WHAT to route and WHAT to hold.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Ranks that can bear an enforceable governance rule (a policy), vs plain domain knowledge.
_POLICY_RANKS = ("regulation", "directive", "decision", "act", "statute", "law", "treaty")
# Deontic force markers that signal a norm is policy-bearing (obligation/prohibition/permission).
_DEONTIC = ("o", "p", "f", "obligation", "prohibition", "permission", "duty")


@dataclass
class PolicyDiffItem:
    subject_id: str
    namespace: str                 # dls | mrl | ...
    change_type: str               # new | amended | repealed
    source_class: str              # e.g. eu:regulation, de:formal-statute
    confirmed: bool                # only the confirmed layer is actionable
    coordinate: dict = field(default_factory=dict)   # jurisdiction/rank/competence/force/...
    deontic_force: str = ""        # O|P|F or "" — the policy-bearing signal
    provenance: str = ""


@dataclass
class Notice:
    kind: str                      # policy_change_notice | policy_candidate_held | policy_repeal_notice | quarantine
    subject_id: str
    change_type: str
    suggested_action: str          # compile_lg_twin | review_retire_lg | (none)
    actionable: bool               # False for held/unconfirmed/quarantine
    coordinate: dict
    provenance: str
    to: str = "policy-officer"
    enacts_nothing: bool = True     # invariant: the feed compiles/applies NOTHING


def _words(s: str) -> set[str]:
    """Lowercased word tokens (WHOLE words — so 'act' never matches 'factsheet')."""
    return {w for w in re.split(r"[^a-z]+", (s or "").lower()) if w}


def is_policy_relevant(item: PolicyDiffItem) -> bool:
    """A governance-relevant policy: a norm with deontic force, or a policy-bearing rank.
    Word-token match, not substring: 'de:formal-statute' -> {formal, statute} matches; 'factsheet' does not."""
    if _words(item.deontic_force) & set(_DEONTIC):
        return True
    rank = item.source_class.split(":", 1)[-1] or item.coordinate.get("rank", "")
    return bool(_words(rank) & set(_POLICY_RANKS))


def _malformed(item: PolicyDiffItem) -> bool:
    return not item.subject_id or not item.namespace or item.change_type not in {"new", "amended", "repealed"}


def notice_for(item: PolicyDiffItem) -> Notice | None:
    """One diff item -> the notice to route, or None if it is not a policy change.

    Fail-closed at every branch: malformed -> quarantine (not enacted); relevant-but-unconfirmed
    -> HELD (noticed, not routed as actionable); repeal -> retire review (tighten). The feed never
    compiles or applies — every Notice carries enacts_nothing=True.
    """
    if _malformed(item):
        return Notice("quarantine", item.subject_id or "?", item.change_type or "?", "", False,
                      item.coordinate, item.provenance)
    if not is_policy_relevant(item):
        return None                                   # domain knowledge, not a policy change
    if not item.confirmed:
        return Notice("policy_candidate_held", item.subject_id, item.change_type, "", False,
                      item.coordinate, item.provenance)   # HELD: don't route unconfirmed policy for compile
    if item.change_type == "repealed":
        return Notice("policy_repeal_notice", item.subject_id, item.change_type, "review_retire_lg", True,
                      item.coordinate, item.provenance)    # a repeal -> retire the .lg (tighten), human-confirmed
    return Notice("policy_change_notice", item.subject_id, item.change_type, "compile_lg_twin", True,
                  item.coordinate, item.provenance)


def run_notice_feed(diff: list[PolicyDiffItem]) -> dict[str, Any]:
    """Scan a policy diff -> the notices, bucketed. Never raises; enacts nothing."""
    notices = [n for n in (notice_for(i) for i in diff) if n is not None]
    routed = [n for n in notices if n.actionable]
    held = [n for n in notices if n.kind == "policy_candidate_held"]
    quarantined = [n for n in notices if n.kind == "quarantine"]
    return {
        "notices": notices,
        "routed_to_policy_officer": routed,      # actionable notices -> the policy-officer inbox
        "held_unconfirmed": held,                # noticed but withheld until confirmed
        "quarantined": quarantined,              # malformed, never enacted
        "enacts_nothing": all(n.enacts_nothing for n in notices),   # the invariant, asserted
    }
