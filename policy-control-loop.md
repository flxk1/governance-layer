# X1 — the real-time policy-control loop
*governance-layer design doc. Local. Composes the six roles + RVND ops into one pipeline.*
*Opened 2026-09-04. ctrl orchestrates · RVND governs · Loomground grounds.*

## The claim
Policy that is **ingested in real time via versum** becomes **known** immediately, but is **enforced only
after a human confirms** the change. KNOW is real-time; ENFORCE-a-change is reserved. A rogue or injected
real-time ingest can make policy *known* — it cannot silently change what is *enforced*.

## The loop (six stages, mapped to role + RVND op)
```
  (1) INGEST      knowledge-steward   loomground-ingest -> loomground-knowledge-write   -> versum (provenanced, timestamped)
        |                                                                                   [copyright gate precondition, bound]
        v
  (2) KNOW        grounder            workspace_grounder / kg-chat (CONFIRMED-only)      -> policy queryable at coordinate, real-time
        |                             + governance_live / governance_map (current enforced policy, live board)
        v
  (3) NOTICE      (LG2 feed)          an L-CORPUS-style watch flags NEW/changed policy to the policy-officer   [DESIGN — not built]
        |
        v
  (4) COMPILE     policy-officer      loomground-governance:loomground / policy_ingest  -> validated .lg twin (express/policy/host)
        |                             patch_validate (fail-closed)                          applied:false  (a DRAFT — enforces nothing)
        v
  (5) APPLY       policy-officer      patch_apply  [RESERVED -> workspace_owner, L4]      -> policy on the signed chain (policy_fingerprint)
        |            *** the reserved human gate — no silent auto-apply ***
        v
  (6) ENFORCE     the gate            action_gate.gate  reads the applied .lg            -> GO / CONDITIONAL / NO-GO per action
        |                             + egress_check (lock-steward) for content at the boundary (X so both axes hold)
        v
  (7) REBIND      policy-officer      governance_open / lane_capabilities                -> every agent's NEXT act checked vs the new policy_fingerprint
        |
        v
  (8) AUDIT       auditor             verify_chain / shadow_scan / discipline            -> integrity + coverage, read-only, folder-scoped
```

## Who does what (no new grounding layer — composes existing planes)
| Stage | Role | Plane |
|-------|------|-------|
| ingest / know | knowledge-steward · grounder | Loomground |
| notice (feed) | LG2 watch (to build) | ctrl (loop) |
| compile / apply / rebind | policy-officer | Loomground `governance` → RVND `workspace_workflow` |
| enforce | the gate (`action_gate`) + lock-steward (`egress_check`) | RVND |
| audit | auditor | RVND `workspace_audit` |

## Security-by-design invariants
- **KNOW is real-time, ENFORCE-a-change is reserved.** `policy_ingest`/`governance_chat` apply **nothing**
  until a human `patch_apply` (stage 5). Ingestion can inform, never silently enforce.
- **No silent disable.** Turning a protection off needs `accepted_by` + `reason` (RVND `policy.disable`);
  the policy-officer's `silent_disable` is prohibited.
- **Validated before applied.** Only a `patch_validate`-clean twin may be applied (`enforce_unvalidated`
  prohibited).
- **Tighten-only widening.** Widening authority is a deliberate owner patch act; `authority_revoke` is the
  only tighten-in-passing (`self_widen_authority` prohibited).
- **Two enforcement axes.** The gate governs *who/grade/reserved/prohibited*; `egress_check` governs *what
  content crosses*. Both must pass — RV4's `egress_minimised` obligation binds the second into the release gate.
- **Write-nothing audit.** The auditor reports; it cannot repair, mutate the graph, or apply policy.

## Build state
- Built (local): the roles — grounder, legal-reasoner, knowledge-steward (CT1–CT4 egress obligations),
  lock-steward, **policy-officer**, **auditor**.
- Built (local): **LG2** the real-time NOTICE feed — `loops/policy_notice.py` (+ `test_policy_notice.py`,
  6/6). Scans an out-of-band policy diff → routes actionable **confirmed** policy changes to the
  policy-officer, **HOLDS** unconfirmed, flags a **repeal** for retire (tighten), **quarantines** malformed,
  and **enacts nothing** (the asserted invariant — compiles/applies no policy; that stays stage 4/5).
- Reserved/host: RV4 `.lg` obligation (2e), RV2 lock audit path, RV3 real backend, LG3 MARKERS_DE PR.
- The loop is a COMPOSITION over existing loomground skills + RVND ops — no parallel grounding or gate.
