"""Output-contract stamping (toolchain brief, Obligations).

Every emitted artefact — a compiled `.lg`, a built SKILL.md, a validation report — carries
`tool=governance-layer version=<ver> input_sha256=<hash>` so "which tool version, from what
input, produced this governance artefact" is always answerable.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from . import __version__

TOOL = "governance-layer"


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def stamp(input_sha256: str) -> dict:
    """The provenance record attached to an emitted artefact."""
    return {
        "tool": TOOL,
        "version": __version__,
        "input_sha256": input_sha256,
        "stamped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def stamp_line(input_sha256: str) -> str:
    """One-line stamp for a comment header (`.lg`, report)."""
    return f"tool={TOOL} version={__version__} input_sha256={input_sha256}"


def lg_stamp_comment(input_sha256: str) -> str:
    """Stamp comment for a compiled `.lg` (`#` line comments)."""
    return f"# stamped: {stamp_line(input_sha256)}"


def report_stamp_header(input_sha256: str) -> str:
    """Stamp header for a validation report."""
    return f"# governance-layer validation report — {stamp_line(input_sha256)}"


def canonical_hash(obj) -> str:
    """Stable sha256 of a JSON-serialisable object (sorted keys) — for build's role-source input."""
    return sha256_hex(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str))
