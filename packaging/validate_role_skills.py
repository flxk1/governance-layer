"""validate_role_skills — check every generated role SKILL.md's governance block against the
skill-governance-block JSON schema. Schema-passing is NECESSARY (SPEC.md §6: full validity also
requires the compiled .lg patch to be WELL-FORMED via the Loomground validator)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent / "skills"
SCHEMA = (HERE.parent.parent / "skill-governance-block" / "schema" / "governance-block.schema.json")

try:
    import yaml  # type: ignore
except Exception:
    yaml = None
try:
    import jsonschema  # type: ignore
except Exception:
    jsonschema = None


def _frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def main() -> int:
    if yaml is None or jsonschema is None:
        print(f"SKIP: need PyYAML ({yaml is not None}) + jsonschema ({jsonschema is not None})")
        return 2
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    ok = True
    for skill in sorted(SKILLS.glob("*/SKILL.md")):
        fm = yaml.safe_load(_frontmatter(skill.read_text(encoding="utf-8"))) or {}
        block = fm.get("governance")
        if block is None:
            print(f"FAIL {skill.parent.name}: no governance block"); ok = False; continue
        errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(block),
                      key=lambda e: e.path)
        if errs:
            ok = False
            print(f"FAIL {skill.parent.name}:")
            for e in errs[:5]:
                print(f"    {list(e.path)}: {e.message}")
        else:
            print(f"OK   {skill.parent.name}  (grade {block.get('grade')}, "
                  f"{len(block.get('actions', []))} actions, {len(block.get('prohibited', []))} prohibited)")
    print("\nALL SCHEMA-VALID" if ok else "\nSCHEMA ERRORS ABOVE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
