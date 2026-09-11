# Requirement Traceability Matrix

Forward index: every requirement ID in `specs/spec.md` → its exact source → its acceptance criteria → any open
ambiguity → a confidence rating. Complements `spec.md §17` (a document-to-IDs reverse index); this file is the
per-ID forward view referenced as source 3 throughout `architecture/architecture.md` and
`architecture/architecture-review.md`.

**Confidence key:** **High** — stated verbatim in `PROBLEM-STATEMENT.md` and/or directly tested by one of the
nine graded checks. **Medium** — corroborated by at least one mockup screen or a second independent source, not
verbatim prose. **Low** — derived only from illustrative mock data (`DATA`) or a single inferred reading.

**Ambiguity key:** "None" = settled. Otherwise references the exact `spec.md §16` open-question item.

---

## Functional Requirements (FR)

| ID | Source page | Source section | Acceptance Criteria | Ambiguity | Confidence |
|---|---|---|---|---|---|
| FR-001 | SIGNIN | 26-29, 49-57 | Valid email/password establishes a session; invalid does not | None | High |
| FR-002 | SIGNIN | 62-64 | Every authorization decision traceable to company-id + admin-boolean alone | None | High |
| FR-003 | REG | 89-95, 107-124 | Form submission is the only way to add a server; no manual tool entry | None | High |
| FR-004 | REG | 91, 134-139 | No response → no registry entry; response → stored tool list matches reported | None | High |
| FR-005 | PS / REG | 74 / 92,136-137 | Every tool has exactly one of 3 risk labels before selectable | §16 item 11 (mechanism conflicts with automatic-flow mockup) | High |
| FR-006 | REG / DATA | 94,102-105,120-123 / 128,151,162,172,181 | Tenant server invisible cross-company; global requires admin | None (mechanism now explicit) | High |
| FR-007 | REG | 94, 141-144 | Unresponsive server eventually marked `down` without user action | None | Medium |
| FR-008 | REG / DATA / CONN | 142-144 / 296 / 74-79 | Dependent agent still answers, reports broken tool | None | High |
| FR-009 | PS / CONN | 80 / 53 | Credential never plaintext after save request processed | None | High |
| FR-010 | PS / CONN | 80-82 / 54,62-68 | No surface (UI/API/log/export) ever shows raw credential | None | High |
| FR-011 | PS | 177 | No persisted trace/prompt/conversation yields the credential post-call | None | High |
| FR-012 | CONN | 46 | Revoked connection can't be used to fetch a credential | None | Medium |
| FR-013 | CONN / DATA / AGENT | 56,71-79 / 197 / 290-293 | Revocation or expiry → degraded, no whole-run error | None | High |
| FR-014 | CONN | 36-50 | Row shows server, status, masked secret, added, last-used | None | Medium |
| FR-015 | PS / BUILD | 89-91 / 206 | Free-text chat entry point accepts a description | None | High |
| FR-016 | PS / BUILD | 95 / 38 | Platform derives intended behavior from description | None | High |
| FR-017 | PS / BUILD | 96,102-106 / 77-107,207 | Registry search shown; user selects/confirms servers | None | High |
| FR-018 | PS / BUILD | 97,102-105 / 79 | Tool-selection is a real halting interrupt, not sync form submit | None | High |
| FR-019 | PS / BUILD | 97-98 / 114-140 | Missing connection stops flow, offers add-credential path | None | High |
| FR-020 | PS / BUILD | 102-105 / 120 | Connection-check is a real interrupt | None | High |
| FR-021 | PS / BUILD | 103-104 / 209 | Both pauses resume exactly after a restart | None | High |
| FR-022 | PS / BUILD | 99-100,211 / 146-186,211,169-185 | Card shows immediate grade; capability score shown "not tested yet" | None (now reflects two-stage scoring) | High |
| FR-023 | BUILD | 47, 210 | Form and chat paths produce identical configuration | None | High |
| FR-024 | BUILD | 192 | User can request a change via composer after initial build | §16 item 8 (mechanism unresolved) | Medium |
| FR-025 | AGENT | 34-36, 111-181 | Overview shows graph, instructions, tools, both scores, metadata | None | High |
| FR-026 | AGENT | 117 | Changing configuration changes the rendered graph | None | High |
| FR-027 | PS / AGENT | 112-113 / 37,183-233 | Playground chat runs live agent, shows hand-offs | None | High |
| FR-028 | PS / AGENT | 115-116 / 38,209-232 | Write/destructive call pauses; nothing proceeds until decided | None | High |
| FR-029 | AGENT | 39, 256-259 | Approval pause still answerable after server restart | None | High |
| FR-030 | AGENT | 40, 252-253 | Thumbs up/down recorded and feeds score | None | Medium |
| FR-031 | AGENT | 41, 263-284 | Connections tab shows this agent's dependency health | None | High |
| FR-032 | AGENT | 42, 285-289 | Config names connection kind only, never identity/value | None | High |
| FR-033 | AGENT / DATA | 44-45,295-313 / 281-288 | Run history shows status/latency/cost/outcome per run | None | High |
| FR-034 | AGENT | 45 | Run data demonstrably feeds the score | None | Medium |
| FR-035 | PS / AGENT | 209-211 / 46,317-327 | Every agent has a callable HTTP endpoint | None | High |
| FR-036 | PS / AGENT | 211-212 / 47 | Downloaded collection + token → real response | None | High |
| FR-037 | PS / AGENT | 214-215 / 48,340-343 | Cross-company token on agent URL → 404 not 403 | §16 item 10 (scope: also intra-company?) | High |
| FR-038 | AGENT | 334 | Pending interrupt answerable outside the UI | §16 item 4 (public REST exposure scope) | Medium |
| FR-039 | PS / AGENT | 203-205 / 49-50,380-389 | Publish disabled below threshold, states why | None (thresholds themselves: see FR-056/057 note) | High |
| FR-040 | PS | 265 (check 3) | Unguarded write/destructive tool blocks publish | None | High |
| FR-041 | PS / AGENT / MARKET | 189-195 / 51 / 108-119 | Publish removes identity/creds/URLs/threads, even if planted | None | High |
| FR-042 | PS / REVIEW | 124-126 / 115 | Publish parks at review, doesn't go live directly | None | High |
| FR-043 | REVIEW | 114 | Only admin role can open/act on review queue | §16 item 2 (how admin accounts are provisioned) | High |
| FR-044 | REVIEW / DATA / AGENT | 43-58 / 239-279 / 366-369 | Admin sees org+author+design; author identity stripped only at final publish | None (two-stage pipeline now explicit) | High |
| FR-045 | PS / REVIEW | 127 / 85-89,119-123 | Approve / Request-changes / Reject are the three decisions | §16 item 3 (Reject resume semantics) | High |
| FR-046 | REVIEW | 116 | Approve & Request-changes resume the same parked run | §16 item 3 | High |
| FR-047 | PS / REVIEW | 129-131 / 94-109 | Multi-day, multi-deploy wait still resumes correctly | None | High |
| FR-048 | PS / REVIEW | 127 / 78-83 | Admin notes attach to a decision, visible to author | None | Medium |
| FR-049 | PS / MARKET | 125-126 / 38 | Only admin-approved agents ever listed | None | High |
| FR-050 | APP / MARKET | 99-118 / 56-104 | Listing shows design only: desc, servers, topology, score, org, installs | None | High |
| FR-051 | PS / MARKET | 136-140 / 45-51,74-89 | Install produces an independent copy in installer's workspace | None | High |
| FR-052 | PS / MARKET | 139-140 / 71-73,76-81 | Installer supplies own credentials; publisher's never transferred | None | High |
| FR-053 | PS / MARKET | 140 / 86-88 | No cross-visibility of runs either direction | None | High |
| FR-054 | MYAG / APP | 40-43 / 76-97 | Card grid, one per agent, click opens detail | §16 item 10 (per-user privacy layer) | High |
| FR-055 | MYAG | 43 | Only own workspace's agents, never another's, even via guessed URL | §16 item 10 | High |
| FR-056 | PS / AGENT | 197-199 / 146-168 | Two independent scores exist per agent | None | High |
| FR-057 | PS / AGENT | 200-201 / 166 | Every score traces to an enumerable, inspectable check | None | High |
| FR-058 | PS / AGENT | 182-187 / 124-142 | Per-tool approval mode stored in config, platform-enforced at run time | None | High |
| FR-059 | DATA / PS / BUILD | 12,54,93,26-29,65-68 / 217-223 / 68-69 | Platform can produce single or supervisor+specialist configs | None | High |
| FR-060 | PS | 217-223 (check 7) | ≥1 demo agent: coordinator+2 specialists, approval step, built via platform | None | High |
| FR-061 | PS / DECK | 227-234 (item 2) / slide 14 | A start-to-finish, no-cuts recording of the six steps exists | None | High |
| FR-062 | PS / DECK | 227-234 (item 3) / slide 14 | 1-2 page doc addresses all 8 rules + "what we'd do differently" | None | High |

## Non-Functional Requirements (NFR)

| ID | Source page | Source section | Acceptance Criteria | Ambiguity | Confidence |
|---|---|---|---|---|---|
| NFR-001 | PS / CONN | 175 / 61-62 | Storage inspection never yields a usable token | None | High |
| NFR-002 | PS | 178-180 (check 2) | No credential discoverable anywhere, unbounded surface | None | High |
| NFR-003 | PS | 165-170 (check 1) | Isolation holds with app-level check removed | §16 item 10 (dimension: company only, or +per-user) | High |
| NFR-004 | — (absence) | — | N/A — treated as non-goal, demo-scale only | None | Low (assumption, not a requirement) |
| NFR-005 | REG / CONN / DATA | 142-144 / 74-79 / 296 | One dependency failure degrades only the affected agent | None | High |
| NFR-006 | PS | 103-104,129-131 (checks 5,6) | Full restart doesn't lose interrupt state; resumes exactly | None | High |
| NFR-007 | PS | 129-131 | Multi-day/multi-deploy gaps still resume correctly | None | High |
| NFR-008 | BUILD / AGENT | 73-140 / 209-232 | Each pause is self-explanatory without inspecting logs | None | Medium |
| NFR-009 | PS / AGENT | 200-201 / 295-313 | Per-run detail sufficient to justify the capability score | None | High |
| NFR-010 | DATA / REVIEW | 245-250 / 64-68 | Per-submission check detail sufficient to justify a decision | None | Medium |
| NFR-011 | — (absence) | — | N/A — no scale requirement beyond `docker compose up` | None | Low (assumption, not a requirement) |

## Security Requirements (SEC)

| ID | Source page | Source section | Acceptance Criteria | Ambiguity | Confidence |
|---|---|---|---|---|---|
| SEC-001 | PS | 165-170 (check 1) | Scoping holds at a layer independent of the app-level check | §16 item 10 | High |
| SEC-002 | MYAG / SIGNIN | 43 / 79-87 | No cross-tenant view by any means, incl. guessed IDs | §16 items 7, 10 | High |
| SEC-003 | PS / CONN | 175 / 53 | Encryption happens before the write to storage | None | High |
| SEC-004 | PS | 178-180 (check 2) | No credential anywhere stored, unbounded — incl. checkpoints/caches | None | High |
| SEC-005 | PS / AGENT | 176 / 285-289 | Config names connection kind only | §16 item 5 (full config schema still open) | High |
| SEC-006 | PS | 177 | Credential fetched at use, not retained after | None | High |
| SEC-007 | PS | 184-187 | Platform enforces approval; instructions alone insufficient | None | High |
| SEC-008 | PS | 265 (check 3) | Unguarded write/destructive tool → publish blocked | None | High |
| SEC-009 | PS / MARKET | 191-195 / 108-119 | Planted confidential content stripped at publish, adversarially tested | None | High |
| SEC-010 | PS / REVIEW | 125-126 / 117 | No automatic path to public listing | None | High |
| SEC-011 | PS / AGENT | 214-215 / 340-343 | Cross-company token on agent URL → 404 not 403 | §16 item 7, 10 | High |
| SEC-012 | REVIEW | 114 | Review queue/actions inaccessible to non-admins | §16 item 2 (provisioning) | High |
| SEC-013 | PS / MARKET | 139-140 / 71-73 | Installer credentials independent, never derived from publisher's | None | High |
| SEC-014 | REG | 121-124 | Non-admin restricted to tenant scope; global requires admin | None | High |
| SEC-015 | PS | 171 | No feature besides publish→approve→install crosses a company boundary | None (generalization of an explicit sentence) | Medium |

## Workflow Requirements (WF)

| ID | Source page | Source section | Acceptance Criteria | Ambiguity | Confidence |
|---|---|---|---|---|---|
| WF-001 | REG | 89-95, 134-139 | Register → introspect → store, or no record at all | §16 item 11 | High |
| WF-002 | PS | 83 | One credential reused across every later build needing that server | None | High |
| WF-003 | PS / BUILD / DECK | 93-106 / 37-42 / slide 5 | 4-node graph, 2 interrupts, both durably resumable | None | High |
| WF-004 | PS / AGENT | 115-116 / 183-259 | Approval pause mid-run, resumable across restart | None | High |
| WF-005 | PS / REVIEW | 122-132 / 94-123 | Publish → parked review → 3-branch resolution | §16 items 3, 12 | High |
| WF-006 | PS / MARKET | 134-142 / 45-89 | Install → independent copy, no installer credentials yet | None | High |
| WF-007 | CONN / DATA | 71-79 / 197 | Revocation or expiry → dependent agents degrade | None | High |
| WF-008 | REG | 141-144 | Health check failure → dependent agents degrade | None | Medium |

## UI/Screen Requirements (UI)

| ID | Source page | Source section | Acceptance Criteria | Ambiguity | Confidence |
|---|---|---|---|---|---|
| UI-001 | SIGNIN | whole screen | Email/password sign-in; communicates isolation stakes | None | High |
| UI-002 | REG | 89-95 | Registration form; mandatory introspection; risk labels; health check | None | High |
| UI-003 | CONN | 52-57 | Add/encrypt; never returned; fetch-use-drop; revoke→degrade | None | High |
| UI-004 | BUILD | 205-212 | Chat→agent; registry search shown; connection check; form parity | §16 item 8 | High |
| UI-005 | MYAG | 39-44 | Card grid; click→detail; own-workspace-only | §16 item 10 | High |
| UI-006 | AGENT | 34-36 | Config-derived graph; tool table w/ risk+approval; both scores | None | High |
| UI-007 | AGENT | 37-40 | Chat; inline approve/reject; restart-safe pause; feedback→score | None | High |
| UI-008 | AGENT | 41-43 | Dependency health; abstract-only config reference; degrade-not-crash | None | High |
| UI-009 | AGENT | 44-45 | Run history table; feeds scoring | None | Medium |
| UI-010 | AGENT | 46-48 | Callable URL; working Postman download; 404-not-403 | None | High |
| UI-011 | AGENT | 49-51 | Publish gated on score/grade; unguarded tool blocks; stripping on publish | None | High |
| UI-012 | REVIEW | 113-118 | Admin-only queue; multi-day parked run; 3 decisions, 2 resume same run | §16 items 2, 3, 12 | High |
| UI-013 | MARKET | 37-42 | Approved-only listings; design-only; install copies+own creds | None | High |
| UI-014 | MARKET | 69-119, 91-104 | Connection check; pre-install tool table; "what is not here" list | None | Medium |

## API Requirements (API)

| ID | Source page | Source section | Acceptance Criteria | Ambiguity | Confidence |
|---|---|---|---|---|---|
| API-001 | PS / AGENT | 209-211 / 320,323-326 | An invoke endpoint exists per agent | None (exact shape is a design choice) | High |
| API-002 | AGENT | 333 | Streamed variant of invoke | §16 item 4 (conflicts with stretch-goal listing) | Low |
| API-003 | AGENT | 334 | Pending interrupt answerable via endpoint | §16 item 4 (capability P0, exposure shape inferred) | Medium |
| API-004 | AGENT | 335 | Postman collection retrievable as JSON | §16 item 4 | Low |
| API-005 | PS / AGENT | 214-215 / 324 | Bearer auth, company-scoped, cross-company → 404 | None | High |
| API-006 | PS / AGENT | 211-212 / 412-451 | Downloaded collection, once tokened, gets a genuine response | None | High |

## Data Requirements (DATA)

| ID | Source page | Source section | Acceptance Criteria | Ambiguity | Confidence |
|---|---|---|---|---|---|
| DATA-001 | DATA / SIGNIN | 4 / whole screen | User: single company membership + admin boolean | §16 item 2 (admin provisioning) | Medium |
| DATA-002 | DATA / PS | various org fields / rule 2 | Company is the isolation boundary | §16 item 10 | High |
| DATA-003 | DATA / REG | 126-190 / 107-124 | Tool list populated only by live introspection | §16 item 11 | Medium |
| DATA-004 | DATA | 132-189 | Risk is exactly one of read/write/destructive | None | Medium |
| DATA-005 | DATA / CONN | 192-198 / 36-50 | Secret encrypted at rest, never returned | None | Medium |
| DATA-006 | DATA / AGENT | 6-124 / 171-179 | Exactly two scores; topology single or supervisor | §16 item 1 (schedule field: real or display-only) | Medium |
| DATA-007 | PS | 151-158 | Exists as a document; single runtime interprets it | §16 item 5 (schema fully open — the central design problem) | High |
| DATA-008 | DATA | 22-24 (example) | Approval mode enforced for write/destructive | None | Medium |
| DATA-009 | DATA | 26-29 | Present only when topology is supervisor | None | Low |
| DATA-010 | DATA / AGENT | 14,291-299 / 146-168 | Each score backed by an itemized check list | §16 item 6 (formula/thresholds are the team's choice) | Medium |
| DATA-011 | DATA | 281-288 | Sufficient to justify score checks | §16 item 1 (Schedule trigger type) | Medium |
| DATA-012 | DATA / REVIEW | 239-279 / 43-68 | Submission record supports the review screen | None | Medium |
| DATA-013 | DATA / APP | 200-237 / 99-118 | Excludes identity beyond org, credentials, internal detail | None | Medium |
| DATA-014 | PS / MARKET | 134-140 / 84-89 | Independent copy, own credentials, no cross-visibility | None | Low (entity inferred, not modeled in DATA) |

## Testing / Evaluation Requirements (TEST)

| ID | Source page | Source section | Acceptance Criteria | Ambiguity | Confidence |
|---|---|---|---|---|---|
| TEST-001 | PS | 263 | Isolation holds with app filter removed | §16 item 10 | High |
| TEST-002 | PS | 264 | Supplied credential found nowhere in stored state | None | High |
| TEST-003 | PS | 265 | Agent with unguarded write tool cannot publish | None | High |
| TEST-004 | PS | 266 | Planted confidential material doesn't survive publication | None | High |
| TEST-005 | PS | 267 | Kill mid-build → resumes correctly on restart | None | High |
| TEST-006 | PS | 268 | Approval pending overnight → still resumes next day | None | High |
| TEST-007 | PS | 269 | Multi-agent demo runs end to end incl. approval step | None | High |
| TEST-008 | PS | 270 | Downloaded Postman collection gets a real response | None | High |
| TEST-009 | PS | 271 | Cross-company agent-by-ID lookup doesn't reveal existence | §16 item 10 | High |
| TEST-010 | PS | 273-274, 243-253, 253 | Live system present; design defensible beyond passing checks | None | High |

---

## Coverage check

140 requirement IDs total (FR ×62, NFR ×11, SEC ×15, WF ×8, UI ×14, API ×6, DATA ×14, TEST ×10) — matches
`spec.md`'s current numbering with no gaps. 28 rows carry a non-"None" ambiguity pointer, all of them tracing to
one of the twelve items in `spec.md §16`; none of those 28 were resolved here — this file records where the
ambiguity reaches, it doesn't settle any of it.
