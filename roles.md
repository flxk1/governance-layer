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

## ROLE 4 — `lock-steward`  (skill: RVND `secure` / Privacy Lock)
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
- **MCP door:** `rvnd:workspace_lock` (setup/threshold_set/seal/classify/egress_check/ingress_check/audit_query).
- **MCP-ONLY (signed + reserved):** provision/threshold/backend/unseal mutations → signed chain event;
  the bundled door **HOLDs** every mutation. Weakenings are distinct-party reserved.
- **Bundled door:** status + classify + egress/ingress *checks* only; signs nothing, mutates nothing.

---

## ROLE 5 — `policy-officer`  (skill: Loomground→RVND `govern`)
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
- **MCP door:** `rvnd:workspace_workflow` (policy_ingest/governance_chat/patch_validate/patch_apply/
  governance_open/lane_capabilities), `rvnd:workspace_policy`.
- **MCP-ONLY (signed + reserved):** `apply_patch` → the signed enforce, reserved to the workspace owner.
- **Bundled door:** ground + compile the `.lg` twin + validate — all **provisional**; applying is a HOLD.

---

## ROLE 6 — `auditor`  (skill: RVND `audit`)
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
- **MCP door:** `rvnd:workspace_audit` (verify_chain/tail/get_event/shadow_scan/discipline/overrides/record_override).
- **The only append** is `record_override` — an attributed, rationale-bearing note; nothing else mutates.
- **Bundled door:** verify + tail + scan; a portable read of the chain. Repairs nothing.

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
- **No MCP / no signing / no product seam.** A local reader over the private folder
  (Obsidian / local versum / local RAG). It has no authoritative door by design.
- **The firewall is two-sided:** `grounder` (ROLE 1) is `official_versum_only` + prohibits
  `ground_from_private_folder`; `local-grounder` prohibits `feed_product_grounding` /
  `write_to_official_versum` / `egress_private_content` / `ship`. Verified NO-GO @L4 both sides.

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
