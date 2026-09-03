# roles.md — the skill→role transition (RVND governance layer)

ctrl orchestrates · **RVND governs (this layer)** · Loomground grounds.
A loomground skill is *universal* and carries **no governance identity**. A **ROLE** = that
skill + a **governance-block** (skill-governance-block v0.1 schema). RVND **enforces** the block
(the signed gate + hash-chain + receipts); the **agent-registry records** it. One declaration →
reader plans on it, enforcer verdicts on it. "Loomground is universal; via RVND/ctrl:legal these
skills become governance capabilities."

## Dual transport (per role, every function)
- **Bundled skill door** — portable, fail-closed, **CANNOT sign**. Any signed/stateful/authoritative
  act on this path is a **fail-closed HOLD**, never a computed result.
- **MCP door** — RVND `mcp__plugin_rvnd_rvnd__workspace_*`, authoritative, **signed**.
- **MCP-ONLY acts** (a bundled path here returns HOLD, not a value): gate a released disposition ·
  append to the chain · mint/verify a receipt · erase. Grounded in real RVND functions
  (`rvnd.action_gate.gate`, `rvnd.mutation_log.MutationLog.append` + `rvnd.signing`,
  `gateway._audit_receipt`, `rvnd.erasure` signed tombstone).

Verdict vocabulary (RVND `action_gate.Verdict`): **GO / CONDITIONAL / NO-GO**; strictest-wins over
the Loomground join `prohibited > reserved > refused > human > auto`. Grade ladder L0<…<L6.

---

## ROLE 1 — `grounder`  (skill: loomground `grounding`)
Read-only evidence-at-coordinate + provenance, or ground-or-escalate. Serves; never writes.

```
governance:
  grade: L2                                  # read-only may run unattended
  actions:
    - { kind: ground_query,        risk: low }
    - { kind: read_evidence,       risk: low }
    - { kind: emit_provenance_receipt, risk: medium, grade: L3 }   # MCP-only (signed)
  grounding-access:
    mode: read
    slice: coordinate = jurisdiction x source-class x point-in-time   # the legal profile axes
    bar: CONFIRMED-only            # graph-confirmed at coordinate; absence -> unconfirmed, never false-positive
    point-in-time: Level-1 (enactment/consolidation) precision; state the precision used
  obligations:
    - provenance_attached          # source URN + graph level + temporal precision on every answer
    - coordinate_pinned            # jurisdiction/source-class/in-force confirmed before serve
  prohibited:
    - graph_write                  # grounding never writes (that is knowledge-steward)
    - binary_fetch
    - fabricate_citation           # ground-or-escalate: no invented cite/version/reach
    - answer_from_model_memory
  reserved: []                     # pure read; nothing referred
  on-boundary: escalate-with-named-axis   # citation won't parse / reach contested / version undetermined / no confirming source -> STOP, name the failed axis
  redress:
    - { kind: disputed_grounding, by: reviewer, overturn: true }
  budget: { usd: 1, iters: 20 }
```
- **MCP door:** `rvnd:workspace_grounder`, `rvnd:workspace_ask`, `rvnd:cross_workspace_read` (reads only).
- **MCP-ONLY (signed):** `emit_provenance_receipt` → `gateway._audit_receipt` + chain; the bundled
  door returns the evidence but **HOLDs** the signed receipt.
- **Bundled door:** portable read + ground-or-escalate; fully usable offline, signs nothing.

---

## ROLE 2 — `legal-reasoner`  (skill: loomground `reasoning`)
Grounded premises → warranted conclusion (apply → in-force → rank-conflict → effect → deontic O/P/F
→ optional quantified/adversarial → optional `.lg` patch). Calls `grounder` first; decides nothing alone.

```
governance:
  grade: L2                                  # analysis may run unattended
  actions:
    - { kind: warrant_conclusion,  risk: medium }
    - { kind: quantify_exposure,   risk: medium }        # solver; fails closed w/o kernel
    - { kind: emit_lg_patch,       risk: high,     grade: L3 }
    - { kind: release_disposition, risk: critical, grade: L4 }   # MCP-only (the signed gate)
  grounding-access:
    mode: read (via grounder)
    slice: only premises grounder returned CONFIRMED + in-force at T
    bar: CONFIRMED-and-in-force; UNCERTAIN premise -> provisional, name the unmet premise
    point-in-time: version_in_force selected per premise
  obligations:
    - warrant_shown                # claim + ordered premises + skill/API per step; never a bare verdict
    - premises_confirmed           # every premise confirmed + in force at relevant T
    - grounding_called_first
  prohibited:
    - reason_over_unconfirmed
    - self_enact                   # produces a conclusion; has no authority to enact it
    - parallel_grounding_layer
  reserved:
    - { kind: release_disposition, by: { quorum: 2, of: [legal_reviewer, policy_owner] } }   # distinct parties (separation of duty)
  on-boundary: escalate-and-state-gap    # scope_applies contested / resolve_provisions no-dominant / classify_referral UNCERTAIN -> escalate
  redress:
    - { kind: released_disposition, by: affected_party, overturn: true, within: 14d }
  budget: { usd: 5, iters: 40 }
```
- **MCP door:** `rvnd:workspace_legal`, `rvnd:workspace_lens`, `rvnd:workspace_policy` (patch), `rvnd:workspace_matrix`.
- **MCP-ONLY (signed):** `release_disposition` → **`action_gate.gate(ActionRequest…)`** yielding
  GO/CONDITIONAL/NO-GO, and on GO an audit-triple receipt to the chain. A reserved
  quorum action is NO-GO/CONDITIONAL until distinct-party sign-off.
- **Bundled door:** emits the warranted conclusion / `.lg` patch as **provisional (unsigned)**;
  releasing a disposition is a **HOLD** — the bundled path cannot sign or gate.

---

## ROLE 3 — `knowledge-steward`  (skill: loomground `knowledge-management`)
Build/maintain the graph asset: ingest (dry-run) → concepts → placement → **write** → curate; enrich;
loomground-capture:capture-session; **erase**. The one write/erase authority in this layer.

```
governance:
  grade: L2                                  # dry-run/propose may run unattended
  actions:
    - { kind: ingest_dryrun,       risk: low }
    - { kind: extract_concepts,    risk: low }
    - { kind: propose_placement,   risk: medium }
    - { kind: graph_write,         risk: high,     grade: L3 }    # MCP-only (chain append)
    - { kind: curate_canon,        risk: high,     grade: L3 }    # the canon run IS a write
    - { kind: graph_erase,         risk: critical, grade: L4 }    # MCP-only (signed tombstone)
  grounding-access:
    mode: write (single governed write path only)
    slice: candidate layer on write; confirmed layer minted only by curate
    bar: invent-nothing; missing context recorded incomplete, never false; low-overlap -> review queue
    point-in-time: every written span/node carries a fetch/validity timestamp
  obligations:
    - single_write_path            # loomground-versum:loomground-knowledge-write is the only executor (enrich/mental-model/organise delegate)
    - dry_run_then_confirm         # ingest + canon shown before they land; human confirms placements/canon writes
    - dedup_urn_sidecar            # canonical URN + dedup + house stub + sidecar on every write
    - legal_basis_recorded         # on erase (GDPR)
  prohibited:
    - direct_write_bypassing_path
    - binary_fetch_in_session
    - invent_node
    - unlogged_mutation            # every write is a chain event
  reserved:
    - { kind: graph_erase, by: { all: [data_protection_officer, workspace_owner] } }   # erase referred to humans, distinct parties
    - { kind: curate_canon, by: curator }
  on-boundary: quarantine-or-review-queue   # ingest quarantines; organise leaves novel/low-overlap unfiled; never guess a home
  redress:
    - { kind: graph_erase,  by: subject,        overturn: false, within: 30d }
    - { kind: graph_write,  by: workspace_owner, overturn: true }
  budget: { usd: 5, iters: 40 }
```
- **MCP door:** `rvnd:workspace_ingest`, `rvnd:workspace_capture`, `rvnd:workspace_memory`, `rvnd:workspace_folder`,
  `rvnd:workspace_mirror`, `rvnd:workspace_erase`.
- **MCP-ONLY (signed):**
  - `graph_write` / `curate_canon` → **`MutationLog.append(LogEvent)`** (SHA-256 `prev_hash` chain)
    + **`signing.sign_bytes`** (Ed25519 over canonical-content|prev_hash) → verifiable receipt.
  - `graph_erase` → **`rvnd:workspace_erase`** = `rvnd.erasure` sweep → **one signed composite tombstone**
    (`composite_tombstone_id`), reserved to a distinct-party human pair.
- **Bundled door:** ingest **dry-run**, concept extraction, placement **proposals** only. Every
  `graph_write` / `curate_canon` / `graph_erase` is a **fail-closed HOLD** — the portable skill
  cannot append to the chain, sign, or mint a tombstone.

---

## Enforcement seam (one declaration, two consumers)
- **Reader (ctrl, plan-time):** `need = max(grade, actions[].grade)`; gap above granted grade →
  surface, don't dispatch. Route every `reserved` to its human target (hold). Exclude `prohibited`
  (withhold the capability, not merely refuse). Carry `obligations` as accept-criteria. Cap at `budget`.
- **Enforcer (RVND, action-time):** `action_gate.gate` returns GO/CONDITIONAL/NO-GO per action from
  the same block; `unavailable`/unknown floors to the weaker-safer path (never a false GO). Registry
  records grade/prohibited/reserved/budget → the 3am worst-case is a *reading* of these lines.
- **Load-bearing invariants (per SGB §7):** a below-grade action → CONDITIONAL/human; a reserved
  action → reserved (NO-GO until sign-off); a prohibited kind → NO-GO (severed); an unattached
  obligation withholds release.
```
