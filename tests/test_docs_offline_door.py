"""The offline door, as the docs state it: every signed or stateful act on the governed graph is a
HOLD, and an offline tool writes only a local, unsigned working folder after an explicit confirm.

Two checks over the repo's Markdown:
  1. the HOLD statement is present, word for word (whitespace-normalised), in roles.md,
     orchestration.md, agent-registry.md, README.md, INSTALL.md, policy-control-loop.md and every
     agents/*.md;
  2. no Markdown file claims that a governed act proceeds, or a governed write lands, on the
     offline door.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

GOVERNED_ACTS = (
    "graph_write", "curate_canon", "graph_erase", "apply_patch", "rebind_lane",
    "release_disposition", "record_override", "emit_provenance_receipt",
    "provision_lock", "raise_threshold", "lower_threshold", "downgrade_backend", "unseal",
)

HOLD_STATEMENT = (
    "**Offline door — HOLD.** On the offline door every signed or stateful act on the governed "
    "graph — `graph_write`, `curate_canon`, `graph_erase`, `apply_patch`, `rebind_lane`, "
    "`release_disposition`, `record_override`, `emit_provenance_receipt`, and every lock mutation "
    "(`provision_lock`, `raise_threshold`, `lower_threshold`, `downgrade_backend`, `unseal`) — is a "
    "HOLD. Offline tools may write only a local, unsigned working folder, and only after an explicit "
    "confirm (a dry run is the default); that folder is not the governed record."
)

REQUIRED = sorted(
    [ROOT / n for n in ("roles.md", "orchestration.md", "agent-registry.md", "README.md",
                        "INSTALL.md", "policy-control-loop.md")]
    + list((ROOT / "agents").glob("*.md"))
)

SCANNED = sorted(
    p for p in ROOT.rglob("*.md")
    if ".git" not in p.parts and "__pycache__" not in p.parts
)

# Wording that states the superseded model: the offline door's one stateful write is a governed
# write, released by an unsigned confirm.
FORBIDDEN = [
    re.compile(r"one stateful write is versum", re.I),
    re.compile(r"writes only (when called )?with the explicit", re.I),
    re.compile(r"a write lands only on an explicit", re.I),
    re.compile(r"dry run unless the caller passes", re.I),
    re.compile(r"governed (act|write)s? (proceed|land|run)s? (on the )?offline", re.I),
    re.compile(r"offline[^.|]*\bgoverned (act|write)s? (proceed|land|run)s?\b", re.I),
]

NEGATION = re.compile(r"\b(HOLD|HOLDs|cannot|can't|not|never|none|nothing|no)\b", re.I)
PROCEEDS = re.compile(
    r"\b(proceeds?|lands?|runs? offline|is performed|are performed|executes?|goes through|appends?)\b",
    re.I)


def _norm(text: str) -> str:
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.M)    # bullet markers
    return re.sub(r"\s+", " ", text).strip()


def _sentences(text: str):
    for chunk in re.split(r"\n\s*\n|\|", text):              # paragraphs and table cells
        yield from re.split(r"(?<=[.!?])\s+", _norm(chunk))


def _rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def test_scan_covers_the_docs():
    names = {_rel(p) for p in SCANNED}
    for p in REQUIRED:
        assert _rel(p) in names
    assert len(list((ROOT / "agents").glob("*.md"))) >= 8


@pytest.mark.parametrize("path", REQUIRED, ids=_rel)
def test_hold_statement_present(path):
    assert _norm(HOLD_STATEMENT) in _norm(path.read_text(encoding="utf-8")), (
        f"{_rel(path)} does not state the offline-door HOLD")


@pytest.mark.parametrize("path", SCANNED, ids=_rel)
def test_no_governed_write_offline_claim(path):
    text = path.read_text(encoding="utf-8")
    flat = _norm(text)
    for pat in FORBIDDEN:
        m = pat.search(flat)
        assert m is None, f"{_rel(path)}: governed-write-offline claim: {m.group(0)!r}"
    for s in _sentences(text):
        low = s.lower()
        if "offline" not in low and "bundled" not in low:
            continue
        # An explicit confirm offline releases only the local working folder.
        if "explicit" in low and "confirm" in low:
            assert "working folder" in low, (
                f"{_rel(path)}: offline confirm not bounded to the working folder: {s!r}")
        # A governed act named with a proceed-verb must be stated as held / not performed.
        if any(a in s for a in GOVERNED_ACTS) and PROCEEDS.search(s):
            assert NEGATION.search(s), f"{_rel(path)}: governed act proceeds offline: {s!r}"


def test_hold_names_every_governed_act():
    for act in GOVERNED_ACTS:
        assert f"`{act}`" in HOLD_STATEMENT
