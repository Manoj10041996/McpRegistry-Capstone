# Security design rules

Security rules for this project, sourced only from requirements actually present in
`McpRegistry-Capstone/specs/spec.md` (traced back to `problem-statement/`). Every rule below cites the
requirement ID(s) it comes from. Do not add a security control here — or anywhere in the design — that isn't
backed by a cited requirement; that's inventing a compliance requirement the capstone never asked for.

## Authentication

- Users authenticate with email and password; there is no requirement for anything beyond that (`FR-001`).
- A session carries exactly two claims — which company the user belongs to, and whether they are an admin —
  and every authorization decision in this project must be explainable in terms of just those two (`FR-002`).

## Authorization

- The admin review queue and its actions are inaccessible to non-admin users (`SEC-012`, `FR-043`).
- Only an admin may register or promote a server to `global` (shared-to-every-company) scope; a non-admin is
  restricted to `tenant`-scoped registration (`SEC-014`).
- Both controls are gated on the single admin boolean from `FR-002` — don't introduce a separate roles/
  permissions model unless a future requirement demands it.

## Tenant isolation

- Tenant-owned data must be scoped to the owning company at a layer that still enforces isolation if the
  application-level authorization check is removed — not "remember to filter every query" (`SEC-001`).
- No user may view another company's agents, connections, or runs by any means, including guessing an ID in a
  URL (`SEC-002`).
- A cross-company token calling an agent's URL gets 404, not 403 — a 403 would confirm the agent exists
  (`SEC-011`).
- The reviewed publish → admin-approve → install path is the *only* sanctioned way data crosses a company
  boundary; no other feature may create a second, unreviewed crossing (`SEC-015`).
- **Open caveat:** `spec.md §16` item 10 flags that isolation may need a second, per-user dimension nested
  inside the company boundary (an agent private to its creator even within their own company), which would
  change the scope of `SEC-001`/`SEC-002`/`SEC-011`. Unresolved — do not design around either answer until it's
  settled; ask rather than pick one.

## Secrets

- A credential is encrypted immediately on submission, before it is ever written to storage (`SEC-003`).
- No credential value may exist in any persisted state the platform controls, of any kind — this is unbounded,
  not limited to an obvious list of surfaces (logs, traces, configs, checkpoints, caches, backups, etc. are all
  covered) (`SEC-004`, `NFR-001`, `NFR-002`).
- An agent's configuration names only the *kind* of connection it needs, never a concrete credential identity or
  value (`SEC-005`).
- A credential is fetched at the moment a tool call needs it and dropped immediately after — never retained in
  any longer-lived execution artifact (`SEC-006`).

## Sensitive data

- Distinct from secrets: this is company-confidential material embedded in an agent's own instructions,
  description, or configuration. The publish pipeline must strip builder identity, credentials, internal URLs/
  system names, and run/thread contents from anything reaching the marketplace — even when such material was
  deliberately planted inside the agent (`SEC-009`).
- Stripping happens in two stages: credentials and internal workspace detail are removed before an admin ever
  sees a submission; the individual author's identity (beyond org name) is stripped later, only at final
  marketplace publish (`FR-041`, `FR-044`).
- An installed agent's credentials are supplied independently by the installer; nothing from the original
  publisher's workspace — credentials or otherwise — is ever shared with or derivable by the installer
  (`SEC-013`).

## Tool/action permissions

- Any tool marked write or destructive must pause for an explicit human approval decision before it executes,
  enforced by the platform's own control layer — an instruction telling the agent to ask first is not a control
  (`SEC-007`).
- An agent with any write/destructive tool that isn't gated behind approval must be blocked from publishing
  (`SEC-008`).
- Per-tool approval mode (auto vs. ask) is part of the stored agent configuration, not something decided ad hoc
  at execution time (`FR-058`).

## Auditability

The capstone does not mandate a general security audit log or compliance trail anywhere in the brief — do not
invent one. What *is* required is narrower: enough per-run detail (tool calls, cost, latency, outcome) to justify
why a capability score is what it is (`NFR-009`), and enough per-submission detail (which mechanical checks
passed or failed) to justify an admin's review decision (`NFR-010`). Treat these two as the full scope of
auditability for this project unless a specific requirement says otherwise.
