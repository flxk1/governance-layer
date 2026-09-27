"""compile_block_to_lg — compile each role's governance block to a Loomground .lg patch (SPEC §4)
and emit it beside the SKILL.md. `validate_lg.sh` then runs the loomground reference validator;
a block is VALID (SPEC §6) iff its patch is WELL-FORMED.

Canonical-compiler decision: `skill-governance-block/reference/compile_block_to_lg.py` is
canonical for SPEC §4 (see that repo's README.md "Canonical compiler" section and its
`reference/__init__.py`). This module is NOT an import of that canonical module — sgb's own
decision (recorded there) declines to make governance-layer import it, since that would mean
editing governance-layer from sgb's task, which is out of that leg's territory. This module is
instead a parity-tested copy: `tests/test_compiler_parity.py` proves byte-for-byte identical
output between this compiler and the canonical one for every role block plus sgb's own worked
example. If the two ever diverge, the canonical copy governs the spec's meaning.

SPEC §4, exactly, and nothing else:
  1. one `actor`, granted the block `grade`;
  2. one source `gate` per `actions[]` entry, carrying its `risk` and (if any) `grade`, granted to
     the actor, each with a `cord` straight to the single `master` (no intermediate gate);
  3. `reserve`/`prohibit`/`obligation`/`redress` lines from the matching fields;
  4. a `human` role for every role named in `reserved`/`redress`.
No other node or cord is emitted — in particular there is no `release` gate. An earlier version of
this compiler routed every action gate through an intermediate `gate release risk low` with no
`grant`, so `release` was always `refused` (no actor is ever granted an ungated gate) and no action
could ever reach `master act`; see the audit report and `tests/test_compile_block_to_lg.py`.

Obligation placement (PO decision, SPEC §3/§7(d)): SPEC §3 gives `obligation <id> on <gate>`, and
§7(d) requires an unattached obligation to withhold release. The reference language's own
well-formedness check (`loomground.check`, `obligation on undeclared gate <X>`) requires every
`obligation ... on X` to name a node whose class is `gate`; `master`'s class is `master`, not `gate`,
so `obligation <id> on master` does not parse under the reference implementation — one line per
obligation directly on `master` is not available. Each declared obligation is instead attached to
*every* action source gate for the role (one `obligation <id> on <kind>` line per action). This is
well-formed, and because every action gate egresses straight to `master`, it still gates every path
to `master` under SPEC §7(d).

L0: EMITS a human-reviewed diff; never auto-applies. Every `.lg` is stamped tool+version+input_sha256.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .stamp import lg_stamp_comment, sha256_hex


def _fm(text: str) -> dict:
    end = text.find("\n---", 3)
    return yaml.safe_load(text[3:end]) or {}


def _actor(name: str) -> str:
    return name.replace("-", "_")


def _party_names(by) -> set:
    if isinstance(by, str):
        return {by}
    if isinstance(by, dict):
        if "all" in by:
            return set(by["all"])
        if "of" in by:
            return set(by["of"])
    return set()


def _by_syntax(by) -> str:
    if isinstance(by, str):
        return by
    if "all" in by:
        return " and ".join(by["all"])
    if "of" in by:
        return f"{by['quorum']} of {{ {', '.join(by['of'])} }}"
    return "owner"


def compile_block(name: str, block: dict, input_sha256: str = "") -> str:
    actor = _actor(name)
    parties = set()
    for r in block.get("reserved", []) or []:
        parties |= _party_names(r["by"])
    for r in block.get("redress", []) or []:
        parties |= _party_names(r["by"])

    L = [f"# {name}.lg — compiled from the governance block (SPEC §4). Generated; do not edit by hand."]
    if input_sha256:
        L.append(lg_stamp_comment(input_sha256))
    for p in sorted(parties):
        L.append(f"human {p} role {p}")
    L.append(f"actor {actor} grade {block['grade']}")
    L.append("")
    # SPEC §4(2): one source gate per action, granted to the actor, egressing straight to master.
    for a in block["actions"]:
        g = f" grade {a['grade']}" if a.get("grade") else ""
        L.append(f"gate {a['kind']} risk {a['risk']}{g} grant {actor}")
    L.append("")
    for a in block["actions"]:
        L.append(f"cord {actor} -> {a['kind']}")
    for a in block["actions"]:
        L.append(f"cord {a['kind']} -> master")
    L.append("")
    for k in block.get("prohibited", []) or []:
        L.append(f"prohibit {k}")
    for r in block.get("reserved", []) or []:
        L.append(f"reserve {r['kind']} by {_by_syntax(r['by'])}")
    # PO decision: the reference language rejects `obligation ... on master` (master is not a
    # `gate`), so each obligation is attached to every action source gate instead (see module
    # docstring). One `obligation <id> on <kind>` line per (obligation, action) pair.
    for o in block.get("obligations", []) or []:
        for a in block["actions"]:
            L.append(f"obligation {o} on {a['kind']}")
    for r in block.get("redress", []) or []:
        s = f"redress {r['kind']} by {r['by'] if isinstance(r['by'], str) else _by_syntax(r['by'])}"
        if r.get("overturn"):
            s += " overturn"
        if r.get("within"):
            s += f" within {r['within']}"
        L.append(s)
    return "\n".join(L) + "\n"


def compile_root(root: Path) -> list[str]:
    """EMIT `<role>.lg` beside each `skills/<role>/SKILL.md` under `root`. Returns paths written."""
    root = Path(root).resolve()
    skills = root / "skills"
    out = []
    for skill in sorted(skills.glob("*/SKILL.md")):
        src = skill.read_text(encoding="utf-8")
        block = _fm(src).get("governance") or {}
        name = skill.parent.name
        lg = compile_block(name, block, input_sha256=sha256_hex(src))
        p = skill.parent / f"{name}.lg"
        p.write_text(lg, encoding="utf-8")
        out.append(str(p))
        print("compiled (emitted, review the diff)", p.relative_to(root))
    return out


def main(root: Path | None = None):
    return compile_root(root or Path.cwd())


if __name__ == "__main__":
    main()
