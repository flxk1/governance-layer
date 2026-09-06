"""governance-layer CLI — the skill-governance-block toolchain.

Subcommands mirror the toolchain and honour its L0 grade:
  validate  READ-ONLY schema-check (the G9 gate); exits non-zero on failure.
  build     EMIT skills/<role>/SKILL.md (a reviewed diff); never auto-applies.
  compile   EMIT <role>.lg beside each SKILL.md (a reviewed diff); never auto-applies.

`build`/`compile` operate on a --root (default CWD) so the installed CLI works outside the repo.
Every emitted artefact is stamped tool+version+input_sha256.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__
from . import build_role_skills, compile_block_to_lg, validate_role_skills


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="governance-layer",
                                description="skill-governance-block toolchain (build/compile/validate)")
    p.add_argument("--version", action="version", version=f"governance-layer {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="READ-ONLY schema-check of role governance blocks (G9 gate)")
    pv.add_argument("--root", default=".", help="repo root holding skills/<role>/SKILL.md (default: CWD)")
    pv.add_argument("--report", default=None, help="write a stamped report to this path (optional)")

    pb = sub.add_parser("build", help="EMIT skills/<role>/SKILL.md (reviewed diff; never auto-applies)")
    pb.add_argument("--root", default=".", help="target root; writes into <root>/skills (default: CWD)")

    pc = sub.add_parser("compile", help="EMIT <role>.lg beside each SKILL.md (reviewed diff)")
    pc.add_argument("--root", default=".", help="root holding skills/<role>/SKILL.md (default: CWD)")

    args = p.parse_args(argv)

    if args.cmd == "validate":
        return validate_role_skills.main(
            root=Path(args.root),
            report_path=Path(args.report) if args.report else None,
        )
    if args.cmd == "build":
        written = build_role_skills.main(root=Path(args.root))
        print(f"\nEMITTED {len(written)} SKILL.md package(s) — review the diff and land it (L0).")
        return 0
    if args.cmd == "compile":
        written = compile_block_to_lg.main(root=Path(args.root))
        print(f"\nEMITTED {len(written)} .lg patch(es) — review the diff and land it (L0). "
              "Validity also requires the Loomground reference validator (SPEC §6).")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
