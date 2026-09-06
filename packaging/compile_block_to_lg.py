"""compile_block_to_lg — compile each role's governance block to a Loomground .lg patch (SPEC §4)
and emit it beside the SKILL.md. `validate_lg.sh` then runs the loomground reference validator;
a block is VALID (SPEC §6) iff its patch is WELL-FORMED.

SPEC §4: (1) one actor at the block grade; (2) one source gate per action (risk + optional grade,
granted to the actor); (3) reserve/prohibit/obligation/redress lines; (4) a human per role named in
reserved/redress. Here the action gates pipe into a single obligation-bearing `release` gate that
egresses to `master` — so master releases iff verdict=auto AND every egress obligation is attached.
"""
from __future__ import annotations
import sys
from pathlib import Path

import yaml

SKILLS = Path(__file__).resolve().parent.parent / "skills"


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


def compile_block(name: str, block: dict) -> str:
    actor = _actor(name)
    parties = set()
    for r in block.get("reserved", []) or []:
        parties |= _party_names(r["by"])
    for r in block.get("redress", []) or []:
        parties |= _party_names(r["by"])

    L = [f"# {name}.lg — compiled from the governance block (SPEC §4). Generated; do not edit by hand."]
    for p in sorted(parties):
        L.append(f"human {p} role {p}")
    L.append(f"actor {actor} grade {block['grade']}")
    L.append("")
    for a in block["actions"]:
        g = f" grade {a['grade']}" if a.get("grade") else ""
        L.append(f"gate {a['kind']} risk {a['risk']}{g} grant {actor}")
    L.append("gate release risk low")
    L.append("")
    for a in block["actions"]:
        L.append(f"cord {actor} -> {a['kind']}")
    for a in block["actions"]:
        L.append(f"cord {a['kind']} -> release")
    L.append("cord release -> master")
    L.append("")
    for k in block.get("prohibited", []) or []:
        L.append(f"prohibit {k}")
    for r in block.get("reserved", []) or []:
        L.append(f"reserve {r['kind']} by {_by_syntax(r['by'])}")
    for o in block.get("obligations", []) or []:
        L.append(f"obligation {o} on release")
    for r in block.get("redress", []) or []:
        s = f"redress {r['kind']} by {r['by'] if isinstance(r['by'], str) else _by_syntax(r['by'])}"
        if r.get("overturn"):
            s += " overturn"
        if r.get("within"):
            s += f" within {r['within']}"
        L.append(s)
    return "\n".join(L) + "\n"


def main():
    out = []
    for skill in sorted(SKILLS.glob("*/SKILL.md")):
        block = _fm(skill.read_text(encoding="utf-8")).get("governance") or {}
        name = skill.parent.name
        lg = compile_block(name, block)
        p = skill.parent / f"{name}.lg"
        p.write_text(lg, encoding="utf-8")
        out.append(str(p))
        print("compiled", p.relative_to(SKILLS.parent))
    return out


if __name__ == "__main__":
    main()
