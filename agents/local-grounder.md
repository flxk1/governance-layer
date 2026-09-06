# Local grounder

**ID:** local-grounder
**Skill:** loomground `grounding` — **LOCAL-ONLY**, over the private knowledge folder
**Owner:** Felix (flxk1)
**Autonomy grade:** L2 — local reads for Felix's own reasoning; it enacts nothing and crosses no boundary
**Last reviewed:** 2026-09-04

## Purpose
Ground **Felix's own** work against his **private knowledge folder**. It is the firewall counterpart to the
product `grounder`: it may read private material, but it is **local-only** — never packaged, never shipped,
never a product runtime dependency, and its output never enters the product's grounding path or the official
versum. One-way isolation: the product can't read private; private can't reach the product.

## Scope
**In scope (why):** `ground_private`, `read_private_evidence` (low) — read/ground against the private
knowledge folder for Felix's own use.
**Out of scope (why):** feeding the product's grounding (`feed_product_grounding`); writing private material
into the official/product versum (`write_to_official_versum`); egressing private content to a model, peer, or
file (`egress_private_content`); being included in any shipped/published/licensed product (`ship`).

## Trigger
Called when Felix wants his private knowledge folder to inform his own reasoning. Never on a product path.

## Grade — unattended vs held
- **Unattended (L2):** `ground_private`, `read_private_evidence` — local reads only.
- **Held:** none — it signs nothing and mints no receipt; it has no MCP/product seam to hold.

## Reserved / Prohibited (from the block)
- **Reserved:** none — local, private; nothing enacted, nothing crosses.
- **Prohibited:** `feed_product_grounding`, `write_to_official_versum`, `egress_private_content`, `ship`.
- **On boundary:** hold-local — anything that would cross into the product OR egress private content →
  STOP, hold local.

## The firewall (mirror of ROLE 1 grounder)
| direction | enforced on | how |
|-----------|-------------|-----|
| product ✗→ private | `grounder` (ROLE 1) | obligation `official_versum_only` + `ground_from_private_folder` **prohibited** (guard: `official_grounding_guard.guard_grounding`) |
| private ✗→ product | `local-grounder` (this) | `feed_product_grounding` + `write_to_official_versum` + `ship` **prohibited** |
Both sides severed ⇒ the wall holds regardless of which role is compromised. `official_grounding_guard`
additionally excludes any **private/local path** from product grounding by construction (fail-closed).

## Budget
`usd: 1`, `iters: 20`.

## Failure modes
1. *Private leaks into the product* — a private-folder claim reaches the official versum or the product
   grounder. Symptom: a product answer citing private material; a private path in the product's grounding
   source. Blast radius: the product loses clean-room self-containment (IP entanglement, licensing risk).
   Notices: `feed_product_grounding`/`write_to_official_versum` prohibited (this side) + the product
   grounder's `official_versum_only` + the guard's private-path exclusion (the other side).
2. *Private content egresses* — private material crosses the boundary to a model/peer/file. Notices:
   `egress_private_content` prohibited + `private_stays_private` (routes through `egress_check`, held).
3. *Ships by accident* — the role or its store gets packaged. Notices: `ship` prohibited + `local_only`;
   the store is separate from the official populations (dls/mrl), no path overlap.

## 3am worst-case
Running amok, it **cannot reach the product**: `feed_product_grounding`, `write_to_official_versum` and
`ship` are **prohibited** (severed), and the product grounder independently refuses any private path
(`official_versum_only` + the guard). It **cannot leak private content**: `egress_private_content` is
prohibited and `private_stays_private` routes every outward move through `egress_check` (held). It signs
nothing and writes nothing. The worst it can do unattended is **read Felix's own private folder for Felix's
own reasoning** — locally, crossing nothing. The 3am answer is acceptable *because* the firewall is
two-sided and severed, not because the role is trusted with the private material.

## Kill switch (real RVND code)
`revoke_agent_key(keyid)` in `rvnd/agent_keys.py` stops any signed act (it signs none anyway); flooring the
grade leaves it at local reads only. The firewall prohibitions (`feed_product_grounding`,
`write_to_official_versum`, `egress_private_content`, `ship`) stay **severed** regardless of grade.

## Audit trail
Local reads only; it appends nothing to a chain and writes no versum. Its non-existence in the product's
grounding provenance IS the guarantee — a product answer must cite an official population, never this role.

## Promotion criteria
Stays L2 by design — it earns no autonomy to write, ship, or cross. The review confirms the two-sided
firewall holds and no private path ever appears in the product's grounding provenance. No promotion to any
crossing or shipping grade — the role's value is that it cannot cross.

## Review cadence
90-day. Next review: 2026-12-04.

---
*Assisted by Claude (Anthropic); not an author or copyright holder.*
