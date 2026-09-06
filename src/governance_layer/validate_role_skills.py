"""validate_role_skills — check every generated role SKILL.md's governance block against the
skill-governance-block JSON schema. Schema-passing is NECESSARY (SPEC.md §6: full validity also
requires the compiled .lg patch to be WELL-FORMED via the Loomground validator).

READ-ONLY: this is the G9 gate other packages' CI calls. It never writes governed source; it may
write a stamped report only to an explicit --report path. The schema is bundled package-data,
resolved via importlib.resources (never a sibling-path lookup).
"""
from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from .stamp import report_stamp_header, sha256_hex

try:
    import yaml  # type: ignore
except Exception:
    yaml = None
try:
    import jsonschema  # type: ignore
except Exception:
    jsonschema = None


def schema_text() -> str:
    """The bundled governance-block schema, resolved from package-data (works from site-packages)."""
    return resources.files(__package__).joinpath("schema/governance-block.schema.json").read_text(
        encoding="utf-8")


def _frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def validate_root(root: Path) -> tuple[bool, list[str], str]:
    """Schema-check every skills/<role>/SKILL.md under root. Returns (ok, report_lines, input_sha256).
    input_sha256 covers the concatenation of all validated block sources — the report's provenance."""
    root = Path(root).resolve()
    skills = root / "skills"
    lines: list[str] = []
    ok = True
    schema = json.loads(schema_text())
    corpus_parts: list[str] = []
    for skill in sorted(skills.glob("*/SKILL.md")):
        src = skill.read_text(encoding="utf-8")
        corpus_parts.append(src)
        fm = yaml.safe_load(_frontmatter(src)) or {}
        block = fm.get("governance")
        if block is None:
            lines.append(f"FAIL {skill.parent.name}: no governance block")
            ok = False
            continue
        errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(block),
                      key=lambda e: e.path)
        if errs:
            ok = False
            lines.append(f"FAIL {skill.parent.name}:")
            for e in errs[:5]:
                lines.append(f"    {list(e.path)}: {e.message}")
        else:
            lines.append(f"OK   {skill.parent.name}  (grade {block.get('grade')}, "
                         f"{len(block.get('actions', []))} actions, "
                         f"{len(block.get('prohibited', []))} prohibited)")
    lines.append("")
    lines.append("ALL SCHEMA-VALID" if ok else "SCHEMA ERRORS ABOVE")
    return ok, lines, sha256_hex("".join(corpus_parts))


def main(root: Path | None = None, report_path: Path | None = None) -> int:
    if yaml is None or jsonschema is None:
        print(f"SKIP: need PyYAML ({yaml is not None}) + jsonschema ({jsonschema is not None})")
        return 2
    root = Path(root or Path.cwd())
    ok, lines, input_sha256 = validate_root(root)
    header = report_stamp_header(input_sha256)
    print(header)
    for ln in lines:
        print(ln)
    if report_path is not None:
        Path(report_path).write_text(header + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
        print(f"(stamped report written to {report_path})")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
