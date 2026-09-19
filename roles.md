# roles.md — the skill→role transition (governance layer)

ctrl orchestrates · **an enforcement host governs (this layer)** · Loomground grounds.
A loomground skill is *universal* and carries **no governance identity**. A **ROLE** = that
skill + a **governance-block** (skill-governance-block v0.1 schema). An enforcement host
**enforces** the block (a signed decision gate + hash-chain + receipts); the
**agent-registry records** it. One declaration → reader plans on it, enforcer verdicts on it.
"Loomground is universal; via an enforcement host and ctrl:legal these skills become governance
capabilities."

## Dual transport (per role, every function)
- **Offline/bundled skill door** — portable, fail-closed, **CANNOT sign**. Any
  signed/stateful/authoritative act on this path is a **fail-closed HOLD**, never a computed
  result.
- **Host-connected door** — the enforcement host's own interface, authoritative, **signed**.
- **Host-only acts** (an offline path here returns HOLD, not a value): gate a released
  disposition · append to the chain · mint/verify a receipt · erase — each requires the host's
  signed decision gate, its hash-chained mutation log, its signed receipts, and its signed
  tombstone erasure, respectively.

Verdict vocabulary (skill-governance-block SPEC §3, the Loomground join): **auto / human /
reserved / prohibited**, joined strictest-wins (`prohibited > reserved > refused > human > auto`).
Grade ladder L0<…<L6.

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
    - official_versum_only         # product path grounds ONLY on served official versum populations
    - completeness_asserted        # state coverage/limits of the answer; silence is not completeness
    - egress_checked               # release passes the lock's egress_check
    - egress_payload_moat_safe     # nothing that would leak the private/curated moat leaves
    - ingress_checked              # imported evidence passes ingress_check before it grounds
  prohibited:
    - graph_write                  # grounding never writes (that is knowledge-steward)
    - binary_fetch
    - fabricate_citation           # ground-or-escalate: no invented cite/version/reach
    - answer_from_model_memory
    - ground_from_private_folder   # the product NEVER grounds on Felix's private folder (that is local-grounder, local-only)
  reserved: []                     # pure read; nothing referred
  on-boundary: escalate-with-named-axis   # citation won't parse / reach contested / version undetermined / no confirming source -> STOP, name the failed axis
  redress:
    - { kind: disputed_grounding, by: reviewer, overturn: true }
  budget: { usd: 1, iters: 20 }
```
- **Host door:** a read-only grounding-evidence interface (provenance, ask, cross-workspace read).
- **Host-only (signed):** `emit_provenance_receipt` → the host's signed receipt + chain; any
  offline door returns the evidence but **HOLDs** the signed receipt.
- **Offline door:** portable read + ground-or-escalate; fully usable offline, signs nothing.

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
    - completeness_asserted        # state which premises/branches were and were NOT reached
    - egress_checked               # a released conclusion passes the lock's egress_check
    - egress_payload_moat_safe     # the warrant/patch leaks no private or curated-moat content
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
- **Host door:** a legal-reasoning / lens / policy (patch) / coverage-matrix interface.
- **Host-only (signed):** `release_disposition` → **the host's signed decision gate**, yielding
  a Loomground verdict (`auto/human/reserved/prohibited`), and on `auto` an audit-triple receipt
  to the chain. A reserved quorum action is held/`reserved` until distinct-party sign-off.
- **Offline door:** emits the warranted conclusion / `.lg` patch as **provisional (unsigned)**;
  releasing a disposition is a **HOLD** — the offline path cannot sign or gate.

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
    - egress_checked               # any mirror/export of the graph passes the lock's egress_check
    - erase_egress_limit_disclosed # state what a signed tombstone can and cannot reach downstream
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
- **Host door:** ingest / capture / memory / folder / mirror / erase interfaces.
- **Host-only (signed):**
  - `graph_write` / `curate_canon` → the host's **hash-chained mutation log** (SHA-256 `prev_hash`
    chain) + an **Ed25519 signature** (over canonical-content|prev_hash) → verifiable receipt.
  - `graph_erase` → the host's **erasure sweep** → **one signed composite tombstone**, reserved to
    a distinct-party human pair.
- **Offline door:** ingest **dry-run**, concept extraction, placement **proposals** only. Every
  `graph_write` / `curate_canon` / `graph_erase` is a **fail-closed HOLD** — the portable skill
  cannot append to the chain, sign, or mint a tombstone.

---

## ROLE 4 — `lock-steward`  (skill: secure / Privacy Lock, host-enforced)
Provisions and discharges the per-folder egress lock. Manages the lock, never exempt from it.
Ratchet + fail-secure: secure default backend, no silent weakening, every change chained.

```
governance:
  grade: L2                                  # status/classify may run unattended
  actions:
    - { kind: lock_status,        risk: low }
    - { kind: classify_content,   risk: low }
    - { kind: propose_lock_profile, risk: medium }
    - { kind: egress_check,       risk: medium }
    - { kind: ingress_check,      risk: medium }
    - { kind: provision_lock,     risk: high,     grade: L3 }
    - { kind: raise_threshold,    risk: high,     grade: L3 }
    - { kind: lower_threshold,    risk: critical, grade: L4 }
    - { kind: downgrade_backend,  risk: critical, grade: L4 }
    - { kind: unseal,             risk: critical, grade: L4 }
  obligations:
    - secure_default_backend       # provisioning defaults to the strongest backend, never a mock
    - no_silent_weakening          # any weakening is explicit, chained, distinct-party
    - human_confirm_before_mutate
    - every_change_chained
    - provision_is_not_access      # standing up the lock never grants read of protected content
    - egress_check_not_self_waivable  # the steward cannot waive its own egress_check
  prohibited:
    - silent_mock_backend
    - weaken_without_distinct_party
    - assume_protected_on_unknown  # unknown classification -> treat as protected, fail-secure
    - egress_on_lock_unavailable   # lock unavailable -> deny egress, never fail-open
    - passphrase_in_context        # never accept/hold a Seal passphrase in-session
  reserved:
    - { kind: provision_lock,    by: workspace_owner }
    - { kind: lower_threshold,   by: { all: [workspace_owner, data_protection_officer] } }
    - { kind: downgrade_backend, by: { all: [workspace_owner, data_protection_officer] } }
    - { kind: unseal,            by: workspace_owner }
  on-boundary: hold-and-explain
  redress:
    - { kind: lower_threshold, by: workspace_owner, overturn: true }
    - { kind: provision_lock,  by: workspace_owner, overturn: true, within: 30d }
  budget: { usd: 2, iters: 25 }
```
- **Host door:** an egress-lock interface (setup/threshold_set/seal/classify/egress_check/ingress_check/audit_query).
- **Host-only (signed + reserved):** provision/threshold/backend/unseal mutations → signed chain event;
  any offline door **HOLDs** every mutation. Weakenings are distinct-party reserved.
- **Offline door:** status + classify + egress/ingress *checks* only; signs nothing, mutates nothing.

---

## ROLE 5 — `policy-officer`  (skill: Loomground→enforcement host `govern`)
versum-policy → validated `.lg` twin → a **human** applies it. Makes known policy enforced.
Knowing/compiling policy is unattended; enforcing a change is reserved.

```
governance:
  grade: L2                                  # ground/compile/validate may run unattended
  actions:
    - { kind: ground_policy,   risk: low }
    - { kind: compile_lg_twin, risk: medium }
    - { kind: validate_patch,  risk: low }
    - { kind: apply_patch,     risk: critical, grade: L4 }   # MCP-only (the signed enforce)
    - { kind: rebind_lane,     risk: high,     grade: L3 }
  obligations:
    - litmus_classified            # every policy tagged real-time-know vs enforce-a-change
    - human_confirm_before_apply
    - fingerprint_pinned           # the applied patch is pinned to a validated fingerprint
    - validated_before_apply       # no patch applies that has not passed validate_patch
  prohibited:
    - auto_apply_policy            # never applies a policy change without a human
    - enforce_unvalidated
    - self_widen_authority
    - silent_disable               # never quietly turns enforcement off
  reserved:
    - { kind: apply_patch, by: workspace_owner }
    - { kind: rebind_lane, by: workspace_owner }
  on-boundary: hand-off-or-escalate
  redress:
    - { kind: apply_patch, by: workspace_owner, overturn: true, within: 14d }
  budget: { usd: 3, iters: 30 }
```
- **Host door:** a policy-workflow interface (ingest/chat/validate/apply/open/lane-capabilities)
  plus a policy-declaration interface.
- **Host-only (signed + reserved):** `apply_patch` → the signed enforce, reserved to the workspace owner.
- **Offline door:** ground + compile the `.lg` twin + validate — all **provisional**; applying is a HOLD.

---

## ROLE 6 — `auditor`  (skill: audit, host-enforced)
Read-only over the signed chain. Writes nothing but an **attributed override**. Reports, never repairs.

```
governance:
  grade: L2                                  # pure read over the chain
  actions:
    - { kind: verify_chain,    risk: low }
    - { kind: tail_chain,      risk: low }
    - { kind: get_event,       risk: low }
    - { kind: shadow_scan,     risk: low }
    - { kind: discipline,      risk: low }
    - { kind: record_override, risk: medium }   # the one append: an attributed override note
  obligations:
    - read_only_default
    - chain_verified_before_report # verify the chain before any finding is reported
    - rationale_on_override        # an override carries a named rationale + author
    - findings_not_masked          # never suppress or soften a finding
  prohibited:
    - mutate_graph
    - mutate_policy
    - sign_content                 # the auditor never signs governed content
    - repair_in_place              # reports a defect; never fixes it silently
  reserved: []                     # pure read + attributed override
  on-boundary: report-not-repair
  redress:
    - { kind: recorded_override, by: workspace_owner, overturn: true }
  budget: { usd: 1, iters: 30 }
```
- **Host door:** a read-only audit interface (verify_chain/tail/get_event/shadow_scan/discipline/overrides/record_override).
- **The only append** is `record_override` — an attributed, rationale-bearing note; nothing else mutates.
- **Offline door:** verify + tail + scan; a portable read of the chain. Repairs nothing.

---

## ROLE 7 — `local-grounder`  (skill: Loomground `ground` — LOCAL-ONLY, private)
Grounds **Felix's own** work over his **private** knowledge folder. Firewalled from the product:
never ships, never a product dependency, output never reaches the official versum. The mirror-image
of `grounder` — same read discipline, opposite firewall.

```
governance:
  grade: L2                                  # local private read
  actions:
    - { kind: ground_private,        risk: low }
    - { kind: read_private_evidence, risk: low }
  obligations:
    - local_only                   # runs only on this machine; no network egress
    - private_stays_private        # private content never leaves the private store
    - firewalled_from_product      # never a dependency of, or input to, the shipped product
    - separate_store               # a store distinct from the official versum, never cross-written
  prohibited:
    - feed_product_grounding       # its output NEVER feeds the product grounder
    - write_to_official_versum     # never writes into the official/served versum
    - egress_private_content
    - ship                         # never packaged, published, or distributed
  reserved: []
  on-boundary: hold-local
  redress:
    - { kind: private_grounding, by: felix, overturn: true }
  budget: { usd: 1, iters: 20 }
```
- **No host connection, no signing, no product seam.** A local reader over the private folder
  (Obsidian / local versum / local RAG). It has no authoritative door by design.
- **The firewall is two-sided:** `grounder` (ROLE 1) is `official_versum_only` + prohibits
  `ground_from_private_folder`; `local-grounder` prohibits `feed_product_grounding` /
  `write_to_official_versum` / `egress_private_content` / `ship`. Both prohibitions are severed
  regardless of grade — a conforming host's load-bearing test (SPEC §7) proves both sides hold.

---

## Enforcement seam (one declaration, two consumers)
- **Reader (ctrl, plan-time):** `need = max(grade, actions[].grade)`; gap above granted grade →
  surface, don't dispatch. Route every `reserved` to its human target (hold). Exclude `prohibited`
  (withhold the capability, not merely refuse). Carry `obligations` as accept-criteria. Cap at `budget`.
- **Enforcer (the enforcement host, action-time):** the host's signed decision gate returns a
  Loomground verdict (`auto/human/reserved/prohibited`) per action from the same block;
  `unavailable`/unknown floors to the weaker-safer path (never a false `auto`). Registry records
  grade/prohibited/reserved/budget → the 3am worst-case is a *reading* of these lines.
- **Load-bearing invariants (per SGB §7):** a below-grade action → `human`; a reserved
  action → `reserved` (held until sign-off); a prohibited kind → `prohibited` (severed); an unattached
  obligation withholds release.
```
