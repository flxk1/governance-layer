import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from policy_notice import PolicyDiffItem, notice_for, run_notice_feed, is_policy_relevant


def _item(**kw):
    base = dict(subject_id="urn:dls:x", namespace="dls", change_type="new",
                source_class="eu:regulation", confirmed=True, coordinate={"rank": "eu:regulation"})
    base.update(kw)
    return PolicyDiffItem(**base)


def test_new_confirmed_policy_routes_to_policy_officer():
    n = notice_for(_item(deontic_force="O"))
    assert n.actionable and n.to == "policy-officer"
    assert n.kind == "policy_change_notice" and n.suggested_action == "compile_lg_twin"
    assert n.enacts_nothing is True


def test_unconfirmed_policy_is_held_not_routed():
    n = notice_for(_item(confirmed=False))
    assert n.kind == "policy_candidate_held" and n.actionable is False


def test_non_policy_knowledge_yields_no_notice():
    # a plain domain fact: no deontic force, not a policy-bearing rank
    n = notice_for(_item(source_class="dls:factsheet", deontic_force="", coordinate={"rank": "dls:note"}))
    assert n is None
    assert not is_policy_relevant(_item(source_class="dls:factsheet", coordinate={"rank": "dls:note"}))


def test_repeal_flags_retire_not_autoremove():
    n = notice_for(_item(change_type="repealed"))
    assert n.kind == "policy_repeal_notice" and n.suggested_action == "review_retire_lg"
    assert n.actionable and n.enacts_nothing is True   # tighten, human-confirmed; never auto-removed here


def test_malformed_item_is_quarantined_not_enacted():
    n = notice_for(PolicyDiffItem(subject_id="", namespace="", change_type="bogus",
                                  source_class="", confirmed=True))
    assert n.kind == "quarantine" and n.actionable is False and n.enacts_nothing is True


def test_feed_buckets_and_enacts_nothing():
    diff = [
        _item(subject_id="urn:dls:a", deontic_force="O"),                       # routed
        _item(subject_id="urn:dls:b", confirmed=False),                         # held
        _item(subject_id="urn:dls:c", change_type="repealed"),                  # repeal -> routed (retire)
        _item(subject_id="urn:dls:d", source_class="dls:factsheet",
              coordinate={"rank": "dls:note"}),                                 # non-policy -> no notice
        PolicyDiffItem(subject_id="", namespace="", change_type="x",
                       source_class="", confirmed=True),                        # quarantine
    ]
    r = run_notice_feed(diff)
    assert len(r["routed_to_policy_officer"]) == 2       # a + c
    assert len(r["held_unconfirmed"]) == 1               # b
    assert len(r["quarantined"]) == 1                    # the malformed
    assert r["enacts_nothing"] is True                   # THE invariant: LG2 compiles/applies nothing
