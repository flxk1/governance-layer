"""governance-layer — the skill-governance-block toolchain (build / compile / validate).

L0: `build`/`compile` EMIT a human-reviewed diff (never auto-apply); `validate` is READ-ONLY
(the G9 gate). Every emitted artefact is stamped tool+version+input_sha256.
"""
__version__ = "0.1.0"
