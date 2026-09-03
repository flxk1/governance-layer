# mcp-door-map — dual transport for the governance layer

**Plane:** RVND = GOVERNANCE (the signed gate, the chain, receipts, erasure). ctrl orchestrates; Loomground grounds.
**What this layer is:** a governed **role** = a universal loomground skill + a governance-block (skill-governance-block spec) that **RVND enforces** and the agent-registry records. Loomground is universal; via RVND/ctrl:legal these skills become governance capabilities.

## The hard rule (real-software way vs cloud-LLM way)

Every governance function has **two doors**:

- **Bundled-skill door** — the RVND plugin's zero-install offline floor (`plugin/rvnd/bin/*`, stdlib-only, no service, no network). **Portable, advisory, fail-closed.** Every result carries `"authoritative": false` + a stderr `mode:` line. It CAN lint, preview, and check chain *linkage* — it **CANNOT sign, grant, append, or erase.** (Invariants asserted by `tests/test_floor_tools.py`: never silently upgrade, never silently downgrade.)
- **MCP door** — the live RVND server, plugin tools `mcp__plugin_rvnd_rvnd__workspace_*`, dispatched by `op`. **Authoritative and signed.**

> **A signed / stateful / authoritative act is MCP-ONLY.** Gate a disposition, append to the Ed25519 chain, mint or verify a receipt against the signer, register/widen a lane, apply a policy, erase — these exist only behind the MCP door because only the server holds the signing key and the chain state. **The host never computes a verdict and never signs; it asks the server to record, and the server signs.** The bundled path for any such act is a **fail-closed HOLD/escalate**, never a computed result. You cannot fake a signature or a chain append offline — the floor returns `authoritative:false` and routes you to the governed cycle.

## Door map

| Governance function | Bundled-skill door (portable, fail-closed — what it CAN'T do) | MCP door (authoritative) | Signed / MCP-only? |
|---|---|---|---|
| **Gate a disposition** (validate an action envelope → allow/hold/deny) | `rvnd-preview` — advisory *would-be* verdict from unambiguous rules only (grade-never-increases, action-allowlist, scope-presence). Unrankable grade → `hold`. `authoritative:false`. **Cannot** bind a verdict, apply the grade lattice, or clear a consequential act. | `rvnd:workspace_workflow(op="patch_validate")` / `op="operate")` — server evaluates envelope vs lane, returns rule-bound verdict via **`action_gate`**. | **MCP-ONLY.** Binding verdict = signed decision. Bundled = advisory hold. |
| **Dispose / apply a change** (commit graph mutation, register/widen lane, import policy) | *(no floor path — floor never grants)* `rvnd-lint` structural check only. | `rvnd:workspace_workflow(op="patch_apply")`; `op="governance_lane_register"` (widen → named approver + rationale); `op="policy_ingest"` (human-confirmed). | **MCP-ONLY.** Loosening is fail-closed until it has a versioned lane + approver + rationale; folds into the chain. |
| **Receipt — append** (write applied decision to audit chain) | *(none — floor cannot sign or append)* fail-closes to hold. | Written by the server on every `patch_apply`/`operate`/`approval_decide`: appended to the per-folder **Ed25519-signed hash chain**. | **MCP-ONLY.** The server signs, not the host. |
| **Receipt — verify** (check tamper-evidence + a receipt) | `rvnd-verify` — offline **linkage contiguity** only (prev-hash chaining; broken link → exit 5). Signature check only if `cryptography` importable AND entry carries key+sig, and even then "indicative, not authoritative" (body bytes may not match RFC 8785 canonical form). **Cannot** authoritatively verify a signature. | `rvnd:workspace_audit(op="verify_chain")`; `op="get_event"`, `op="discipline")`. Core primitive **`verify_chain`** — recomputes content hashes under RFC 8785, checks Ed25519 signatures. | Read is safe both doors; **authoritative** signature verification is MCP-ONLY. |
| **Grounder evidence** (provenance / claim status) | *(none in floor)* — grounding is a loomground read, not a governance write. | `rvnd:workspace_grounder(op="provenance.trace" \| "claim.status" \| "bibliography")`. | Read-only, not a signed act. (This is where the governed **grounding** role reads; an `actions[]` guard scopes it.) |
| **Policy / matrix write** (governance graph & coverage) | `rvnd-lint` validates a surface/patch structurally; **cannot** apply. Reads: none authoritative. | Read: `rvnd:workspace_workflow(op="governance_graph" \| "governance_netlist" \| "governance_query" \| "coverage_matrix" \| "loop_graph" \| "governance_lane_list")`. Write: `op="patch_apply"`. | Read = both doors. **Write = MCP-ONLY** (via `patch_apply`, signed to chain). |
| **Erase** (right-to-be-forgotten) | *(none — floor cannot erase or sign)* fail-closes to hold/escalate. | `rvnd:workspace_erase(op="request" \| "status" \| "subject" \| "sweep")` — a **signed tombstone**, not a silent delete; purges this folder's record + blocks re-ingestion; **cannot recall copies already past the boundary** (state so on render). | **MCP-ONLY.** Signed tombstone is the only honest erase. |
| **Session / identity** (resolve principal before governing) | *(none)* — no-id wall is fail-closed: an unresolved principal stops the action; never invent/reuse an identity. | `rvnd:workspace_session` (session state); identity resolved server-side via `CLAUDE_CODE_SESSION_ID` join + pid start-time binding. Approvals: `rvnd:workspace_workflow(op="approval_request" \| "approval_decide" \| "approval_resolve" \| "approval_delegate" \| "approval_list")`. Human sign-off via **`approval_decide`** (timeout = DENY; whether it COUNTS is the projection's call). | Identity resolution + human decision = **MCP-ONLY**. Bundled = fail-closed wall. |
| **Classify / lens** (privacy classify, egress, apply a lens) | *(none authoritative)* | `rvnd:workspace_lock(op="classify" \| "egress_check" \| "ingress_check" \| "audit_query" \| "threshold_get")`; `rvnd:workspace_lens`; `rvnd:workspace_model(op="classify" \| "cascade" \| "status")`. | Classify read may run both; **egress/ingress gating decisions are server-authoritative** (MCP door). |

## Notes that bind the two doors

- **Discover, don't memorise.** Resolve every verb to a live op at discovery time — `rvnd:workspace_workflow(op="help")`, `rvnd:workspace_audit(op="help")`, `rvnd:workspace_lock(op="help")`. If an expected op is absent, treat it as **unavailable and fail closed** — do not emulate it locally or in the floor.
- **Two MCP surfaces.** Full local server exposes `rvnd:workspace_workflow` + mutators. The **read-only egress gateway** exposes only `rvnd:workspace_lock`, `rvnd:workspace_audit`, `rvnd:workspace_grounder`, `rvnd:workspace_model`, `rvnd:workspace_contract`, `rvnd:workspace_policy` — `rvnd:workspace_workflow` and write/private tools are deliberately off it. On the gateway, mutations are simply unavailable; fail closed, don't route around it.
- **`transfer` is unavailable** — no verified single op records principals + a signed custody handoff; session export/import is bundle movement, not custody transfer. Mark unavailable until the server confirms one.
- **Governance identity is conferred here, not in the skill.** The three loomground skills (`grounding`, `reasoning`, `knowledge-management`) each state they carry *no* grade, no governance-block, no decision-authority. This layer's governance-block + RVND enforcement is what turns each into a governed role; the agent-registry records the block.

## RVND names confirmed against source (rvnd-repos/RVND, read-only)

- Core primitives: `action_gate` (the signed gate), `verify_chain` (RFC-8785 + Ed25519), `Ed25519`-signed hash chain, signed-`tombstone` erasure, `patch_apply`, `approval_decide` — all present in server source.
- MCP door: `mcp__plugin_rvnd_rvnd__workspace_{workflow,audit,lock,grounder,erase,session,lens,model,contract,policy}`, dispatched by `op` (mapping in `plugin/rvnd/references/catalogue.md`).
- Bundled door / offline floor: `plugin/rvnd/bin/{rvnd-probe,rvnd-lint,rvnd-preview,rvnd-verify}` — advisory, `authoritative:false`, invariants in `tests/test_floor_tools.py` (`plugin/rvnd/references/offline-floor.md`).

## Proven live (2026-09-03) — the MCP door for real
Against the live server `workspaces` v0.6.9.9 (deps aligned), following RVND's protocol
(read `governance://llms.txt` → `op="help"` discover → execute → report):
- **Authoritative validation via MCP:** `workspace_workflow(op="patch_validate")` on a well-formed
  `.lg` patch → `ok:true` + a server-projected governance graph (actor→gate→master, cords typed,
  reservations parsed). The server validates; the host does not.
- **Fail-closed via MCP:** the same op on a pipe-cycle patch → `ok:false`,
  `"pipe relation has a cycle (must be acyclic)"`, `projection:null`.
- **Consequential acts held (correct):** `patch_apply` / `workspace_orchestrate` (chain-record) /
  `workspace_erase` / workspace+lane registration are MCP-only, reserved, and need a registered
  workspace — NOT performed; holding them is the intended fail-closed behavior.
