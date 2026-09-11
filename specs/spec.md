# Forge — Agent Platform Capstone: Normalized Specification

**Status:** Draft v1 — implementation-independent. No architecture, HLD, LLD, or code decisions are made in this document.

**Source of truth.** All content below is derived from the GitHub repository `fnusatvik07/agent-platform-capstone`
(branch `main`), which is the live target of `C:\capstone-MCPRegistry\problem-statement\brief.html`. The local
`problem-statement/` folder in this project contains only a loader shell; the substantive material was fetched
from that repository. Source keys used throughout this document:

| Key | File | Description |
|---|---|---|
| `PS` | `PROBLEM-STATEMENT.md` (root; byte-identical to `docs/problem-statement.md`) | The canonical brief |
| `RM` | `README.md` | Repo overview (secondary — see §16 re: rule-count mismatch) |
| `AN` | `ANNOUNCEMENT.md` | Course-admin announcement text (paste-ready boilerplate) |
| `IDX` | `docs/index.html` | "The UI to build" landing page |
| `SIGNIN` | `docs/screens/signin.html` | Sign-in mockup |
| `REG` | `docs/screens/registry.html` | MCP Registry mockup |
| `CONN` | `docs/screens/connections.html` | Connections mockup |
| `BUILD` | `docs/screens/build.html` | Build (chat) mockup |
| `MYAG` | `docs/screens/my-agents.html` | My Agents mockup |
| `AGENT` | `docs/screens/agent.html` | Agent detail mockup (tabs: overview, playground, connections, runs, api, settings) |
| `REVIEW` | `docs/screens/review.html` | Admin Review mockup |
| `MARKET` | `docs/screens/marketplace.html` | Marketplace mockup (list + detail views) |
| `DATA` | `docs/assets/data.js` | Mock data model — **illustrative only**, not a schema mandate |
| `APP` | `docs/assets/app.js` | Shared shell/card-rendering logic |
| `DECK` | `docs/deck/index.html` | 16-slide deck (cited by slide number) |

Every requirement below carries an exact source file + line/section reference. Where a mockup shows a concrete
number, label, or field that is not corroborated by the prose brief, it is explicitly flagged as illustrative
rather than folded silently into a requirement.

---

# 1. Executive Summary

Forge is a multi-tenant platform that builds, deploys, tests, scores, and publishes AI agents — it is not itself
an agent (`PS:16`). A signed-in user describes an agent in plain English; the platform determines the tools it
needs from a registry of introspected MCP servers, confirms the user has credentials for those tools, assembles
and deploys the agent from a configuration document (never generated code), and hands the user a chat playground
to test it in. Risky (write/destructive) tool calls pause for human approval. Once satisfied, the user publishes
the agent; an admin reviews and approves it before it becomes installable by users in other companies, who
receive an independent copy running on their own credentials (`PS:9-16, 47-142`).

The project is graded on nine binary, adversarially-designed checks (`PS:257-271`) plus a live 45-minute defense
of the design (`PS:243-274`). The checks probe exactly the properties an easy implementation tends to fake:
tenant isolation with the application filter removed, credential leakage, publish-time confidentiality stripping,
and durable resume of long-paused LangGraph interrupts across restarts.

---

# 2. Problem Statement

Today, every team that wants an agent writes one from scratch: duplicated LangGraph boilerplate, hardcoded API
keys per repository, and no shared answer to "what agents are running, and what can they touch?" (`PS:36-42`).
Forge is the platform that answers both questions by centralizing three things: a catalogue of tool servers with
automatically-discovered capabilities, a build process that turns a plain-English request into a governed,
versionable configuration, and a review gate that lets agents cross company boundaries safely once, and only
once, a human has looked at them (`PS:43-44, 47-59`).

The product surface is deliberately small: three tabs (MCP Registry, Build, My Agents) plus a Marketplace and an
Admin Review queue (`PS:49-59`). The six-step flow — register a server, connect once, describe an agent, test
it, publish it, have someone else install it — is both the demo script and the acceptance boundary: "Your demo
walks this path without cuts" (`PS:62-64`).

---

# 3. Goals

Restated directly from the brief's explicit list of what the finished software must do (`PS:18-27`):

- G1 — Authenticate users and keep each company's data completely separate.
- G2 — Store and encrypt third-party credentials.
- G3 — Catalogue MCP servers and read their capabilities automatically (not by manual entry).
- G4 — Run a multi-step LangGraph conversation that pauses for human input and survives a process restart.
- G5 — Generate, deploy, run, and score agents from configuration (not from generated code).
- G6 — Put a human approval step in front of anything risky.
- G7 — Expose every agent over an API.
- G8 — Deliver the unbroken six-step demo flow (`PS:62-142`).
- G9 — Pass all nine graded checks (`PS:257-271`) and be able to defend the design live (`PS:243-274`).
- G10 — Produce all four required submission deliverables together: the repository, a demo recording, a design
  document, and the multi-agent demo agent (`PS:227-234`; see `FR-061`, `FR-062`, `FR-060`).

---

# 4. Non-Goals

Explicitly out of scope, per the brief:

- NG1 — Building an agent. The deliverable is the platform that builds agents (`PS:16`).
- NG2 — Pixel-accurate UI reproduction of the mockups — "Match the behaviour, not the pixels" (`PS:30`; `IDX:204-206`).
- NG3 — Running on LangGraph Platform / its hosted Agent Server — it requires a paid licence; self-hosting is
  required instead (`PS:284-286`).
- NG4 — Any paid third-party account or service (`PS:280-281`).
- NG5 — Code generation with sandboxing (`PS:306-307`).
- NG6 — Single sign-on (`PS:306-307`).
- NG7 — Token exchange protocols (`PS:306-307`).
- NG8 — Per-agent service accounts (`PS:306-307`).
- NG9 — Canary deployments (`PS:306-307`).
- NG10 (stretch, not core) — Autonomous scheduling, playground streaming, agent versioning/rollback, marketplace
  ratings, OAuth-based connections, agents-that-use-other-agents-as-tools. These are explicitly listed under
  "If you finish early," i.e. optional enhancements, not requirements for the core submission (`PS:298-300`). See
  §16 for the tension this creates against several mockups that display some of these as if core.

---

# 5. Actors and Roles

| Actor | Definition | Source | Status |
|---|---|---|---|
| **User / workspace member** | Signs in with email + password; belongs to exactly one company; can register servers, add connections, build/test/publish agents, install from the marketplace | `SIGNIN` whole screen; `PS:20` | Explicit |
| **Company / Workspace (tenant)** | The isolation boundary. Owns agents, connections, and optionally private ("tenant"-scoped) servers | `PS` rule 2 (`160-170`); `DATA:128,151-189` (`scope` field) | Explicit |
| **Admin (reviewer)** | Can open the Admin Review queue and approve/reject/request-changes on submissions; shown in the mockup as belonging to a distinct "Forge Platform" identity rather than a tenant company | `REVIEW:29` (`org: "Forge Platform", role: "admin"`) | Explicit role, provisioning mechanism unspecified — see §16 |
| **Publisher / agent owner** | The user (and their company) who built and submitted an agent for review | `PS:122-132`; `REVIEW` queue rows | Explicit |
| **Installer** | A user in a *different* company who adds a marketplace agent to their own workspace | `PS:134-142`; `MARKET` detail view | Explicit |
| **MCP Server** | An external system the platform connects to as an MCP client; exposes a set of tools the platform introspects | `PS:69-76`; `REG` whole screen | Explicit (external actor, not a platform user) |
| **The platform runtime** | The single runtime component that reads an agent's configuration document and assembles/executes the agent | `PS:153-158` (rule 1) | Explicit |
| **Grader / evaluator** | Runs the nine checks against the submission and attends the live presentation, including deliberately removing the application-level tenant filter and planting confidential content to test stripping | `PS:257-274`; rules 2, 3, 5 "how this is tested" callouts | Explicit (adversarial actor, not a platform user) |

---

# 6. Functional Requirements

Priority legend: **P0** = required for the six-step demo and/or one of the nine graded checks. **P1** = shown
explicitly in a mockup or named in the brief, but not independently verifiable by a graded check and not part of
the six-step critical path.

## Sign-in / Session

**FR-001 — Email/password authentication**
- Requirement: A user authenticates with an email and a password.
- Source: `SIGNIN:26-29,49-57` ("Email and password is enough. What matters is what it keeps separate.")
- Priority: P0
- Acceptance Criteria: A valid email/password pair establishes a session; an invalid pair does not.

**FR-002 — Minimal session claims**
- Requirement: A session determines exactly two facts that govern everything else: which company the user
  belongs to, and whether they are an admin.
- Source: `SIGNIN:62-64` ("Two things travel with you for the rest of the session: which company you belong to,
  and whether you are an admin. Everything else follows from those.")
- Priority: P0
- Acceptance Criteria: Every authorization decision elsewhere in the product can be explained in terms of these
  two claims alone.

## MCP Registry

**FR-003 — Register a server**
- Requirement: A user can register an MCP server by supplying its name, transport, endpoint, auth type, and
  visibility (shared vs. private-to-my-company).
- Source: `REG:89-95` (reqPanel), `REG:107-124` (form fields)
- Priority: P0
- Acceptance Criteria: Submitting the form with these fields is the only way to add a server; no field lets a
  user hand-enter a tool list.

**FR-004 — Mandatory live introspection on save**
- Requirement: On save, the platform itself connects to the server and asks it for its tool list; the record is
  only persisted if the server answers.
- Source: `REG:91` ("your platform connects to the server and asks it what tools it has... I do not type tool
  names in by hand"); `REG:134-139` ("What happens on save" checklist, including "If it does not answer, nothing
  is saved")
- Priority: P0 — CRITICAL
- Acceptance Criteria: A server that does not respond to introspection produces no registry entry. A server that
  does respond produces a stored tool list matching what it reported.

**FR-005 — Tool risk classification stored per tool**
- Requirement: Every introspected tool is recorded as one of `read`, `write`, or `destructive`.
- Source: `PS:74` ("Each tool is recorded as read, write, or destructive. That marking matters in step 4.");
  `REG:92,136-137`
- Priority: P0
- Acceptance Criteria: Every tool belonging to a registered server has exactly one of the three risk labels
  before it can be selected into an agent. *(How the label is derived is a design choice — see §15 assumption on
  manual classification.)*

**FR-006 — Server visibility scoping**
- Requirement: A server can be shared with every company (`global`) or kept private to the registering company
  (`tenant`). Only an admin may set a server's visibility to `global`; a non-admin user's registration is
  restricted to `tenant` scope.
- Source: `REG:94,102-105,120-123` (the "Visible to" dropdown's exact option text is "Everyone (admin only)"
  vs. "Just my workspace"); `DATA:128,151,162,172,181` (`scope` field)
- Priority: P0
- Acceptance Criteria: A `tenant`-scoped server registered by Company A never appears in Company B's registry
  view. A non-admin user cannot register or promote a server to `global` scope. See `SEC-014`.

**FR-007 — Periodic health re-check**
- Requirement: A scheduled job periodically re-checks every registered server and marks unresponsive ones as
  down.
- Source: `REG:94,141-144` ("A scheduled job re-checks every server and marks the dead ones.")
- Priority: P1 (mechanism required; exact frequency unspecified — design choice)
- Acceptance Criteria: A server that stops responding is eventually marked `down` without user action.

**FR-008 — Dependent agents degrade, not fail, on server outage**
- Requirement: An agent whose server dependency is down is marked `degraded` rather than being disabled or
  erroring outright.
- Source: `REG:142-144`; `DATA:296` (`degraded` status in `STATUS` enum); `CONN:74-79`
- Priority: P0
- Acceptance Criteria: With a dependency down, the agent still answers using its other tools and reports the
  broken one.

## Connections (credentials)

**FR-009 — Add a credential, encrypted on save**
- Requirement: A user can add a credential for a registered server; it is encrypted immediately on submission.
- Source: `PS:80` ("I paste mine in once, and it is encrypted immediately."); `CONN:53`
- Priority: P0
- Acceptance Criteria: The credential value is never stored in plaintext at any point after the save request is
  processed.

**FR-010 — Credentials are never returned**
- Requirement: Once stored, a credential value is never given back to the user, the UI, a log, or any part of
  the system that does not strictly need it for the single call it is used in.
- Source: `PS:80-82`; `CONN:54,62-68`
- Priority: P0 — CRITICAL
- Acceptance Criteria: No UI surface, API response, log entry, or export ever contains a stored credential's raw
  value; the Connections table shows only a masked placeholder (`CONN:43`).

**FR-011 — Fetch-use-drop at call time**
- Requirement: When a tool call needs a credential, the platform fetches it, uses it for that one call, and
  discards it — it is not retained in any longer-lived execution artifact.
- Source: `PS:177` ("When a tool needs it: fetch it, use it, drop it.")
- Priority: P0 — CRITICAL
- Acceptance Criteria: Inspecting any persisted trace, prompt, or conversation record after a tool call never
  yields the credential used for that call.

**FR-012 — Revoke a connection**
- Requirement: A user can revoke a stored connection.
- Source: `CONN:46` (Revoke button per row)
- Priority: P0
- Acceptance Criteria: A revoked connection can no longer be used to fetch a credential for tool execution.

**FR-013 — Revocation or expiry degrades dependent agents, does not crash them**
- Requirement: A connection leaving `active` status — whether by user revocation or by the credential expiring
  on its own — leaves every agent that depends on it `degraded`: it keeps working with its other tools and
  reports the broken one.
- Source: `CONN:56,71-79`; `DATA:197` (the connections list's own illustrative example uses a Jira connection
  with `status: "expired"`, not revoked, to demonstrate this exact behavior); `AGENT:290-293`
- Priority: P0
- Acceptance Criteria: After revocation or expiry, invoking the agent does not error the whole run; the response
  indicates which capability is unavailable.

**FR-014 — Connections list detail**
- Requirement: Each connection row shows: server, status (active/expired/revoked), masked secret, date added,
  and last-used time.
- Source: `CONN:36-50`
- Priority: P1

## Build (the core LangGraph flow)

**FR-015 — Plain-English chat entry point**
- Requirement: A chat interface accepts a free-text description of the desired agent.
- Source: `PS:89-91`; `BUILD:206`
- Priority: P0

**FR-016 — Understand step**
- Requirement: The platform works out what the described agent needs to do.
- Source: `PS:95`; `BUILD:38` (steps array, "Understand — Work out what it should do")
- Priority: P0

**FR-017 — Propose and confirm tools (pause 1)**
- Requirement: The platform searches its MCP registry, shows the user the servers it believes are needed, and
  the user selects/confirms which to use.
- Source: `PS:96,102-106`; `BUILD:77-107,207`
- Priority: P0

**FR-018 — Tool selection is a real interrupt**
- Requirement: The tool-selection step is implemented as a LangGraph interrupt that halts execution until the
  user answers, not a synchronous form submit inside one request.
- Source: `PS:97,102-105` ("Those two moments where it stops and waits for me are the centre of this project.
  They are LangGraph interrupts..."); `BUILD:79` (`interrupt: select_tools`)
- Priority: P0 — CRITICAL

**FR-019 — Check connections and stop if one is missing (pause 2)**
- Requirement: After tool selection, the platform checks the user's connections for each selected server; if any
  is missing, it stops and offers a way to add the missing credential before continuing.
- Source: `PS:97-98`; `BUILD:114-140`
- Priority: P0

**FR-020 — Connection check is a real interrupt**
- Requirement: The missing-connection stop is also implemented as a LangGraph interrupt.
- Source: `PS:102-105`; `BUILD:120` (`interrupt: missing_connection`)
- Priority: P0 — CRITICAL

**FR-021 — Both build interrupts survive a restart**
- Requirement: Both pause points must survive the server process restarting while paused, and resume execution
  exactly where they left off.
- Source: `PS:103-104` ("the build must survive a server restart while it is paused and pick up exactly where it
  left off"); `BUILD:209`; graded check 5 (`PS:267`)
- Priority: P0 — CRITICAL

**FR-022 — Build, deploy, and present the result**
- Requirement: Once both pauses are resolved, the platform writes the configuration, deploys the agent, and
  shows the finished result (name, description, capability summary) as a card. Only the safety/governance grade
  is available immediately, computed from static configuration checks; the capability score is shown as not yet
  tested until the agent has run history.
- Source: `PS:99-100,211`; `BUILD:146-186,211`; `BUILD:169-185` (the result card shows the capability score as
  "not tested yet" alongside an immediate governance grade, with the prose "It scores C until you have actually
  run it")
- Priority: P0

**FR-023 — Equivalent form-mode entry point**
- Requirement: A structured form exists as an alternative entry point that walks the same steps; both entry
  points must produce the identical agent configuration — the builder logic must not be implemented twice.
- Source: `BUILD:47` ("Use a form instead"); `BUILD:210` ("Both paths must produce the same agent configuration —
  do not write the builder twice.")
- Priority: P0
- In plain terms: Give users a simple fill-in-the-blanks form as an alternative to chatting — but both routes
  must build the exact same agent underneath, so the actual "builder" logic only exists once.

**FR-024 — Post-build follow-up edits via chat**
- Requirement: After the initial build, the user can request a change through the same chat composer (e.g. "also
  include issues labelled bug").
- Source: `BUILD:192` (composer placeholder text)
- Priority: P1 — shown in the mockup's composer only; not elaborated in the prose brief, and the mechanism
  (in-place edit vs. rebuild) is not specified.
- In plain terms: Once the agent is built, let the user ask for a small tweak (like "also include issues
  labelled bug") right in the same chat, instead of starting the whole build over.

## Agent detail — Overview

**FR-025 — Overview tab contents**
- Requirement: The agent detail page's overview shows: the agent's graph, its instructions text, its full tool
  list with risk level and whether each tool asks for approval, both scores with the checks behind them, and key
  metadata (model, topology, schedule, run count/last-run, visibility).
- Source: `AGENT:34-36` (`REQ.overview`); `AGENT:111-181` (`T.overview`)
- Priority: P0

**FR-026 — Graph is derived from configuration, not hand-drawn**
- Requirement: The agent graph visualization must be generated from the stored configuration document such that
  changing the configuration changes the picture.
- Source: `AGENT:117` ("Drawn from the agent's configuration, not hand-maintained. Change the config and the
  picture changes.")
- Priority: P0

## Agent detail — Playground

**FR-027 — Playground chat**
- Requirement: Each agent has a playground: a chat window where the user runs the live agent and observes its
  work, including visible hand-offs between coordinator and specialists for multi-agent agents.
- Source: `PS:112-113`; `AGENT:37` (`REQ.playground`); `AGENT:183-233` (`T.playground`)
- Priority: P0

**FR-028 — Inline approval gate on risky tool calls**
- Requirement: When execution reaches a tool call marked write or destructive, the run pauses and the playground
  shows an inline Approve/Reject control; nothing downstream of that call executes until a decision is made.
- Source: `PS:115-116` ("When the agent tries to do something risky, like posting to Slack, it stops and asks me
  first. I click Approve or Reject right there in the chat."); `AGENT:38,209-232`
- Priority: P0 — CRITICAL (graded check 7)

**FR-029 — Approval pause survives restart**
- Requirement: A playground run parked on an approval interrupt must still be waiting and answerable after a
  server restart.
- Source: `AGENT:39,256-259` ("This run is parked on an interrupt. Restart the server and come back — the
  approval is still here..."); graded check 6 (`PS:268`)
- Priority: P0 — CRITICAL

**FR-030 — Feedback feeds the score**
- Requirement: The user can give a thumbs-up/down reaction on a run, and this feeds into the agent's score.
- Source: `AGENT:40,252-253` ("feeds the score")
- Priority: P1 (the feed mechanism is explicit; the weighting/formula is a design choice)

## Agent detail — Connections tab

**FR-031 — Show this agent's connection dependencies**
- Requirement: The agent detail page shows which of the user's connections this agent uses and whether each is
  healthy.
- Source: `AGENT:41` (`REQ.connections`); `AGENT:263-284` (`T.connections`)
- Priority: P0

**FR-032 — Configuration references connections abstractly only**
- Requirement: The agent's stored configuration must say only that it needs a connection of a given kind (e.g.
  "needs a Slack connection"), never which specific credential or its content.
- Source: `AGENT:42` (`REQ.connections`); `AGENT:285-289` ("The agent's configuration only says 'this needs a
  Slack connection'. That is why it can be published to the marketplace without leaking anything...")
- Priority: P0 — CRITICAL (this is the mechanism that makes FR-051/FR-052 possible)

## Agent detail — Runs tab

**FR-033 — Run history**
- Requirement: The agent detail page shows a run history with, per run: status, latency, cost, and an outcome
  summary.
- Source: `AGENT:44-45` (`REQ.runs`); `AGENT:295-313` (`T.runs`); `DATA:281-288`
- Priority: P0

**FR-034 — Run history feeds scoring**
- Requirement: Run history data feeds into the agent's score(s).
- Source: `AGENT:45` ("These numbers feed the agent score.")
- Priority: P0 (feed relationship explicit; formula is a design choice)

## Agent detail — API tab

**FR-035 — Callable invoke endpoint**
- Requirement: Every agent exposes a callable HTTP endpoint.
- Source: `PS:209-211`; `AGENT:46,317-327`
- Priority: P0

**FR-036 — Working, downloadable Postman collection**
- Requirement: The agent page has a "Download Postman Collection" button; the downloaded collection, once a
  token is supplied, can be sent and returns a genuine response from that agent.
- Source: `PS:211-212` ("A person should be able to download it, hit Send, and get a response from their
  agent."); `AGENT:47`; graded check 8 (`PS:270`)
- Priority: P0 — CRITICAL

**FR-037 — Cross-company invoke returns 404, not 403**
- Requirement: A token belonging to another company that calls this agent's URL gets HTTP 404, not 403.
- Source: `PS:214-215` ("A 403 confirms the agent exists."); `AGENT:48,340-343`; graded check 9 (`PS:271`)
- Priority: P0 — CRITICAL

**FR-038 — Resume capability for pending interrupts**
- Requirement: A pending approval/interrupt on a run can be answered programmatically (not only through the UI).
- Source: `AGENT:334` (`POST /v1/agents/:id/resume`)
- Priority: P1 — shown only in the mockup's endpoint table, not elaborated in the prose brief. The *capability*
  to resume a pending interrupt is P0 (required by FR-029/graded check 6); exposing it specifically as a public
  REST endpoint with this exact shape is inferred from the mockup, not mandated verbatim.

## Agent detail — Settings / Publish

**FR-039 — Publish blocked below score threshold, with a stated reason**
- Requirement: The Publish button is disabled when the agent's score(s) fall below the platform's required
  threshold, and the disabled state states why.
- Source: `PS:203-205` ("an agent that scores badly cannot be published. The button is disabled and it says
  why."); `AGENT:49-50,380-389`; graded check 3 (`PS:265`)
- Priority: P0 — CRITICAL

**FR-040 — Unguarded write/destructive tool blocks publish**
- Requirement: An agent that has any write or destructive tool not gated behind approval cannot be published.
- Source: graded check 3 (`PS:265`); rule 4 (`PS:182-187`)
- Priority: P0 — CRITICAL

**FR-041 — Publishing strips everything company-internal**
- Requirement: Publishing removes builder identity, credentials, internal URLs/system names, and run/thread data
  from what is sent onward, leaving only the agent's design (what it does, what kinds of access it needs) — even
  when such material has been deliberately embedded in the agent's own instructions.
- Source: `PS:189-195` (rule 5); `AGENT:51`; `MARKET:108-119`; graded check 4 (`PS:266`)
- Priority: P0 — CRITICAL

## Publish workflow / Admin Review

**FR-042 — Publish parks a run at review, does not go live directly**
- Requirement: Clicking Publish starts a run that immediately pauses at the admin review queue rather than
  making the agent live.
- Source: `PS:124-126` ("It does not go live. It goes to an admin..."); `REVIEW:115`
- Priority: P0

**FR-043 — Review queue is admin-only**
- Requirement: Only users with the admin role can open or act on the review queue.
- Source: `REVIEW:114` (reqPanel: "A queue only admins can open.")
- Priority: P0

**FR-044 — Review shows the agent's design, credentials/internal detail already stripped, plus mechanical checks**
- Requirement: The review screen shows, per submission, the agent's design with credentials and internal
  workspace detail (URLs, secrets) already removed, its scores, and a set of automatic checks each with a
  pass/fail state. The submitting company and the individual author's name are still visible to the admin at
  this stage — stripping the author's identity down to org-name-only happens later, at final marketplace publish
  (see `FR-050`, `SEC-009`). "Stripped design" here means credential/internal-detail stripping only, not
  identity stripping, until that final step.
- Source: `REVIEW:43-58` (queue rows render `${q.org} · ${q.by} · ${q.submitted}` directly); `DATA:239-279`
  (`submissions[].org`, `submissions[].by`, `submissions[].checks`); `AGENT:366-369` ("credentials and anything
  internal to your workspace are stripped first")
- Priority: P0

**FR-045 — Three admin decisions**
- Requirement: The admin can Approve (agent goes live in the marketplace), Request changes (returned to the
  author with notes, remains theirs), or Reject (closed, author told why).
- Source: `PS:127` ("either approves it or sends it back with notes"); `REVIEW:85-89,119-123`
- Priority: P0

**FR-046 — Approve and Request-changes resume the same parked run**
- Requirement: Both Approve and Request-changes resume the same parked run from exactly where it stopped.
- Source: `REVIEW:116` ("Approve publishes it. Request changes sends it back to the author with notes. Both
  resume the same parked run.")
- Priority: P0
- Note: Reject's resume semantics are not specified with the same clarity — see §16 (open question, deferred by
  stakeholder as of this writing).

**FR-047 — Review pause survives long waits and multiple restarts**
- Requirement: A publish-review run parked on the admin queue must survive an arbitrarily long wait (explicitly
  exercised: three days, across two deploys and a weekend) and remain correctly answerable.
- Source: `PS:129-131`; `REVIEW:94-109`; graded check 6 (`PS:268`)
- Priority: P0 — CRITICAL

**FR-048 — Admin notes attached to a decision**
- Requirement: The admin can attach free-text notes to a decision, visible to the submitting author.
- Source: `PS:127`; `REVIEW:78-83`
- Priority: P0

## Marketplace

**FR-049 — Only admin-approved agents are listed**
- Requirement: An agent appears in the marketplace only after an admin has approved it; there is no path to a
  listing that bypasses review.
- Source: `PS:125-126`; `MARKET:38` (reqPanel: "Every listing here was approved by an admin. Nothing reaches
  this page automatically.")
- Priority: P0

**FR-050 — Listing shows design only**
- Requirement: Each marketplace listing shows the agent's design (description, required server types, topology,
  score, publishing org name, install count) with no credential or internal detail.
- Source: `APP:99-118` (`listingCard`); `MARKET:56-104`
- Priority: P0

**FR-051 — Install creates an independent copy**
- Requirement: A user in a different company can install a marketplace agent ("Add to my workspace"), receiving
  an independent copy in their own workspace.
- Source: `PS:136-140`; `MARKET:45-51,74-89`
- Priority: P0

**FR-052 — Installer supplies their own credentials**
- Requirement: The installer is prompted to supply their own credentials for the agent's required servers; the
  original publisher's credentials are never transferred and never accessible to the installer.
- Source: `PS:139-140`; `MARKET:71-73,76-81`
- Priority: P0 — CRITICAL

**FR-053 — No cross-visibility between publisher and installer**
- Requirement: The original owner never sees the installer's runs, and the installer's edits/usage never affect
  the original agent.
- Source: `PS:140`; `MARKET:86-88` ("editing it changes nothing for anyone else, and the publisher never sees
  your runs")
- Priority: P0

## My Agents

**FR-054 — Card grid of the user's own agents**
- Requirement: My Agents shows every agent belonging to the signed-in user's workspace as a card (name, status,
  description, servers used, both scores, last-run info); clicking a card opens the agent's detail page.
- Source: `MYAG:40-43`; `APP:76-97` (`agentCard`)
- Priority: P0

**FR-055 — Scoped strictly to the caller's own workspace**
- Requirement: My Agents shows only the signed-in user's own workspace's agents; no other company's agent is
  ever visible here, including by guessing a URL.
- Source: `MYAG:43` ("This page shows only your agents. Another user signing in must never see one of these,
  even by guessing a URL.")
- Priority: P0 — CRITICAL (graded check 1)

## Scoring

**FR-056 — Two independent scores per agent**
- Requirement: Every agent carries exactly two scores: a capability score ("how well it works") and a safety
  grade ("how safely it is set up").
- Source: `PS:197-199` (rule 6); `AGENT:146-168`
- Priority: P0

**FR-057 — Scores must be explainable from enumerable checks**
- Requirement: Both scores must be computed from inspectable, enumerable checks/signals — never a model's
  subjective guess — and the platform must be able to show exactly which checks produced the number/grade.
- Source: `PS:200-201` ("you must be able to point at exactly why a number is what it is — no asking a model to
  guess a score."); `AGENT:166` ("Every number here traces to a check you can point at.")
- Priority: P0 — CRITICAL (also part of the presentation defense, `PS:273-274`)

## Agent shape / tool governance

**FR-058 — Per-tool approval mode enforced by the platform**
- Requirement: An agent's configuration records, per tool, whether it runs automatically or requires approval,
  and this is enforced by the platform's control layer regardless of what the agent's own instructions say.
- Source: `PS:182-187` (rule 4); `AGENT:124-142`
- Priority: P0 — CRITICAL

**FR-059 — Single or coordinator+specialists topology**
- Requirement: An agent can be composed either as a single agent, or as a coordinator ("supervisor") delegating
  to two or more named specialist sub-agents, each with a defined role.
- Source: `DATA:12,54,93` (`topology` field), `DATA:26-29,65-68` (`subagents[]`); `PS:217-223` (rule 8);
  `BUILD:68-69`
- Priority: P0 (the platform must be able to produce this shape; see FR-060 for the mandatory demo instance)

**FR-060 — Mandatory multi-agent demo agent, built through the platform**
- Requirement: At least one shipped demo agent must be a genuine multi-agent system (coordinator + ≥2
  specialists) with a human-approval step in its flow, and it must have been produced using the platform's own
  build flow — not hand-authored.
- Source: `PS:217-223` (rule 8: "It must be built through your own platform, not hand-written. That is the proof
  your platform can produce agents shaped like this, and not just simple ones."); graded check 7 (`PS:269`)
- Priority: P0 — CRITICAL deliverable

## Submission deliverables

**FR-061 — Demo recording deliverable**
- Requirement: A video recording of the six-step flow (register a server → connect → describe an agent → test
  it → publish it → someone else installs it), executed start to finish with no cuts, is a required submission
  artifact separate from the live presentation.
- Source: `PS:227-234` (submit table, item 2: "A demo recording | The six steps above, start to finish, without
  cuts."); corroborated independently by `DECK` slide 14 ("A demo recording walking the six steps, start to
  finish, without cuts.")
- Priority: P0
- Acceptance Criteria: A single recording exists showing all six steps in one unbroken pass; no step is skipped
  or shown via a static screenshot in place of the running product.

**FR-062 — Design document deliverable**
- Requirement: A 1–2 page design document exists, distinct from source code and from this spec, explaining how
  the team made each of the 8 rules true and what they would do differently with another month.
- Source: `PS:227-234` (submit table, item 3: "A design document | One or two pages: how you made each rule
  true, and what you would do differently with another month."); corroborated independently by `DECK` slide 14.
- Priority: P0
- Acceptance Criteria: The document addresses all 8 rules individually and includes an explicit
  "what we'd do differently" section.

---

# 7. Non-Functional Requirements

## Security (qualities; itemized controls are in §8)

**NFR-001 — Credentials encrypted at rest**
- Requirement: Stored credential material is encrypted such that direct inspection of storage does not yield a
  usable token.
- Source: `PS:175`; `CONN:61-62` ("Encrypted at rest. Nobody reading the database gets a usable token.")
- Priority: P0. Algorithm/key-management approach is a design choice (§15).

**NFR-002 — No credential in any searchable artifact**
- Requirement: No credential value is discoverable anywhere in persisted state, without limit to a named list of
  surfaces — configuration, logs, traces, and saved conversations are examples, not the full set (see `SEC-004`
  for the same principle stated as a control).
- Source: `PS:178-180`; graded check 2 (`PS:264`)
- Priority: P0.

## Tenant isolation

**NFR-003 — Structural, not filter-based, isolation**
- Requirement: Cross-tenant data isolation must hold even when the application-level authorization check is
  removed.
- Source: `PS:165-170` (rule 2: "Do not enforce this by remembering to add a filter to every query... Find a way
  to make it structurally impossible. How this is tested: we delete your application-level check and try
  again."); graded check 1 (`PS:263`)
- Priority: P0 — CRITICAL. See SEC-001/SEC-002 for the itemized controls.

## Performance

**NFR-004 — No numeric performance target specified**
- Requirement: The brief specifies no explicit latency or throughput target.
- Source: absence in `PS`; `DATA:281-288` run durations (5.2s–9.0s) are illustrative mock data, not a target.
- Priority: N/A — labeled **assumption**, not a requirement. Treat "demo-plausible" (single-digit seconds per
  step, matching the mock data's order of magnitude) as an unstated expectation only.

## Reliability

**NFR-005 — Isolated failure domains**
- Requirement: A single dependency failure (an MCP server down, a credential revoked) must not take down a
  company's other agents or tools — it degrades only the affected agent/tool.
- Source: `REG:142-144`; `CONN:74-79`; `DATA:296` (`degraded` status)
- Priority: P0.

## Persistence / restart-resume

**NFR-006 — Durable interrupt state across full process restarts**
- Requirement: All in-flight paused graph state — both build-time interrupts, the playground approval interrupt,
  and the publish-review interrupt — must be durably persisted so that a full server restart does not lose it,
  and execution resumes from the exact interrupt point.
- Source: `PS:103-104,129-131`; graded checks 5 and 6 (`PS:267-268`)
- Priority: P0 — CRITICAL. This is the single most load-bearing non-functional requirement in the brief; it
  underlies FR-021, FR-029, and FR-047.

**NFR-007 — Long-duration pauses**
- Requirement: Persisted interrupt state must remain correctly resumable after multi-day waits and multiple
  deploys, not just a same-process pause.
- Source: `PS:129-131` ("That approval might sit there for three days. Across two deploys and a weekend.")
- Priority: P0.

## Usability

**NFR-008 — Self-explanatory pause UI**
- Requirement: Each of the three pause points (tool selection, missing connection, playground approval) must
  present enough information for a person to decide without inspecting logs — what is being asked, why, and what
  action is available.
- Source: `BUILD:73-140`; `AGENT:209-232`
- Priority: P1 — a usability quality, not independently graded by the nine checks, but load-bearing for the live
  demo (`PS:62-64`).

## Observability

**NFR-009 — Enough run detail to justify a score**
- Requirement: The platform must retain per-run detail (tool calls, cost, latency, outcome) sufficient to
  reconstruct why a score is what it is.
- Source: `PS:200-201`; `AGENT:295-313`
- Priority: P0.

**NFR-010 — Enough detail to justify review checks**
- Requirement: Enough information must be retained per submission to display the mechanical review checks shown
  to an admin (e.g., "two granted tools were never used in 23 runs").
- Source: `DATA:245-250` (`submissions[].checks` example); `REVIEW:64-68`
- Priority: P0.

## Scalability

**NFR-011 — No scale requirement beyond a single-team demo**
- Requirement: None specified. The only deployment requirement is `docker compose up` producing a running system
  (`PS:231`). There is no stated requirement for multi-instance operation, horizontal scaling, or high
  availability.
- Source: absence in `PS`; contrast with the explicit `docker compose up` submission requirement.
- Priority: N/A — labeled **non-goal**, included here only to satisfy the template's instruction to address
  scalability "where actually justified." It is not justified by any source material; do not design for it.

---

# 8. Security Requirements

**SEC-001 — Structural tenant scoping**
- Requirement: All tenant-owned data (agents, connections, runs, submissions) must be scoped to the owning
  company at a layer that still enforces isolation if the application-level authorization check is removed.
- Source: `PS:165-170`; graded check 1 (`PS:263`)
- Priority: P0 — CRITICAL

**SEC-002 — No cross-tenant visibility by any means, including guessed IDs**
- Requirement: A user must never be able to view another company's agents, connections, or runs, including by
  guessing/enumerating identifiers in a URL.
- Source: `MYAG:43`; `SIGNIN:79-87` ("Helios Systems... not visible to you")
- Priority: P0 — CRITICAL

**SEC-003 — Encrypt credentials before persistence**
- Requirement: A credential is encrypted immediately upon submission, before it is written to storage.
- Source: `PS:175`; `CONN:53`
- Priority: P0

**SEC-004 — Credential values never surface anywhere**
- Requirement: No credential value may exist in any persisted state the platform controls, of any kind — this
  guarantee is unbounded, not limited to an enumerated list of surfaces. Named examples the platform must cover
  include (but are not limited to) API responses, UI surfaces, log entries, traces, saved conversations,
  LangGraph checkpoint state, vector-store embeddings, cached model requests/responses, and backups — any
  storage layer the platform adds later is covered by the same rule, not just the ones named here.
- Source: `PS:178-180` ("we search **everything** your system stored for the token we gave you. Finding it
  **anywhere** is a fail." — the test methodology is deliberately unbounded, not scoped to a named list);
  graded check 2 (`PS:264`)
- Priority: P0 — CRITICAL

**SEC-005 — Configuration references credentials abstractly only**
- Requirement: An agent's configuration document must name only the *kind* of connection required, never a
  concrete credential identity or value.
- Source: `PS:176`; `AGENT:285-289`
- Priority: P0

**SEC-006 — Fetch-use-drop credential lifecycle at execution time**
- Requirement: A tool call's credential is fetched at the moment of use and not retained afterward.
- Source: `PS:177`
- Priority: P0

**SEC-007 — Platform-enforced approval gate, not instruction-based**
- Requirement: Any tool marked write or destructive requires an explicit human approval decision before it
  executes, enforced by the platform's own control layer — an instruction such as "always ask before posting" is
  explicitly insufficient.
- Source: `PS:184-187` (rule 4: "This has to be enforced by the platform... it is not a control — it is a
  suggestion, and models do not always follow suggestions.")
- Priority: P0 — CRITICAL

**SEC-008 — Unguarded write/destructive tool blocks publish**
- Requirement: An agent with any write/destructive tool that is not gated behind approval must be blocked from
  publishing.
- Source: graded check 3 (`PS:265`)
- Priority: P0 — CRITICAL

**SEC-009 — Publish-time confidentiality stripping, adversarially tested**
- Requirement: The publish pipeline must remove builder identity, credentials, internal URLs/system names, and
  run/thread contents from anything that leaves the company's workspace, even when such material has been
  deliberately planted inside the agent's instructions or description.
- Source: `PS:191-195` (rule 5: "How this is tested: we hand you an agent with company-confidential material
  planted inside it, and check what comes out the other side."); `MARKET:108-119`; graded check 4 (`PS:266`)
- Priority: P0 — CRITICAL

**SEC-010 — No automatic marketplace publish path**
- Requirement: Nothing reaches the public marketplace listing without an admin's explicit approval.
- Source: `PS:125-126`; `REVIEW:117`
- Priority: P0

**SEC-011 — 404, not 403, for cross-tenant agent access**
- Requirement: A request to invoke, stream, or resume an agent using a token that does not belong to that
  agent's owning company must return HTTP 404 — a 403 would confirm the agent's existence.
- Source: `PS:214-215`; `AGENT:340-343`; graded check 9 (`PS:271`)
- Priority: P0 — CRITICAL

**SEC-012 — Admin-only review surface**
- Requirement: The admin review queue and its actions must be inaccessible to non-admin users.
- Source: `REVIEW:114`
- Priority: P0

**SEC-013 — Independent installer credentials**
- Requirement: An installed agent's credentials are supplied independently by the installer and are never
  derived from or shared with the publisher's credentials.
- Source: `PS:139-140`; `MARKET:71-73`
- Priority: P0 — CRITICAL

**SEC-014 — Admin-only global server registration**
- Requirement: Only an admin may register or promote a server to `global` (shared-to-every-company) scope; a
  non-admin user is restricted to registering `tenant`-scoped (private-to-my-company) servers.
- Source: `REG:121-124` (the registration modal's "Visible to" dropdown option is literally labeled "Everyone
  **(admin only)**", contrasted with "Just my workspace")
- Priority: P0. See `FR-006`.

**SEC-015 — The reviewed marketplace path is the only sanctioned cross-company data flow**
- Requirement: The publish → admin-approve → install path is the *only* mechanism by which any data may cross a
  company boundary. No other feature (support tooling, admin impersonation, a convenience "share with another
  company" shortcut, debugging endpoints, etc.) may create a second, unreviewed cross-tenant data path.
- Source: `PS:171` ("The marketplace is the single deliberate exception — which is exactly why an admin guards
  it."), read as a standing design invariant rather than a one-off remark about rule 2.
- Priority: P0. Generalizes `SEC-001`, `SEC-010`.

---

# 9. Workflow Requirements

**WF-001 — Register → introspect → catalogue**
- Requirement: Registering a server (input) leads deterministically to either (a) a stored, introspected tool
  catalogue with each tool risk-labeled, or (b) no record at all if introspection fails. There is no partial or
  manually-populated state.
- Source: `REG:89-95,134-139`
- Priority: P0. Realizes FR-003–FR-005.

**WF-002 — Connect once, reuse everywhere**
- Requirement: A credential added for a server is available to every agent the same user subsequently builds
  that needs that server — it is not re-entered per agent.
- Source: `PS:83` ("Every agent I build from now on reuses this connection.")
- Priority: P0. Realizes FR-009–FR-011.

**WF-003 — Build graph with two interrupts**
- Requirement: Description → Understand → Propose tools **[interrupt: wait for selection]** → Check connections
  **[interrupt: wait for missing credential, if any]** → Build & deploy → Present result. Both interrupt points
  must be durably resumable across a full restart.
- Source: `PS:93-106`; `BUILD:37-42` (the four-node "Builder graph" sidebar); `DECK` slide 5
- Priority: P0 — CRITICAL. Realizes FR-015–FR-022.

**WF-004 — Playground run with an approval pause**
- Requirement: A playground conversation may, at any point a risky tool is reached, pause and require an
  Approve/Reject decision before continuing; the pause must be resumable across a restart.
- Source: `PS:115-116`; `AGENT:183-259`
- Priority: P0 — CRITICAL. Realizes FR-027–FR-029.

**WF-005 — Publish → admin-parked review → resolution**
- Requirement: Publish (subject to the score/approval gate) → run parks at Admin Review **[interrupt: wait for
  admin decision, which may take days]** → Approve resumes into "live in marketplace" / Request-changes resumes
  into "back to author, editable" / Reject resumes (semantics under §16) into "closed."
- Source: `PS:122-132`; `REVIEW:94-123`
- Priority: P0 — CRITICAL. Realizes FR-039–FR-048.

**WF-006 — Install into a new workspace**
- Requirement: Selecting an approved marketplace listing and choosing "Add to my workspace" produces an
  independent agent copy owned by the installer's company, initially lacking the installer's own credentials
  until supplied.
- Source: `PS:134-142`; `MARKET:45-89`
- Priority: P0. Realizes FR-049–FR-053.

**WF-007 — Credential revocation or expiry propagates to degraded state**
- Requirement: A connection leaving `active` status — by revocation or by expiring on its own — transitions
  every dependent agent's status to `degraded` without interrupting its other capabilities.
- Source: `CONN:71-79`; `DATA:197` (expired-status example)
- Priority: P0. Realizes FR-013.

**WF-008 — Server health check propagates to degraded state**
- Requirement: A background health check that finds a server down transitions every dependent agent's status to
  `degraded`.
- Source: `REG:141-144`
- Priority: P0. Realizes FR-007–FR-008.

---

# 10. UI/Screen Requirements

Each screen mockup carries its own explicit "what you must build on this screen" panel (a `reqPanel`, rendered
in red in the mockups). These are restated here at screen granularity; the underlying behavior is already
itemized as FR-IDs above (cross-referenced).

**UI-001 — Sign in**
- Source: `SIGNIN` whole screen
- Requirements: Email/password sign-in (FR-001); the page must communicate that isolation is the whole point of
  signing in (`SIGNIN:101-108`, "The whole security requirement... make it structurally impossible").
- Priority: P0

**UI-002 — MCP Registry**
- Source: `REG:89-95`
- Requirements: registration form (FR-003); mandatory live introspection (FR-004); read/write/destructive
  labeling (FR-005); background health re-check (FR-007); global vs. tenant visibility (FR-006).
- Priority: P0

**UI-003 — Connections**
- Source: `CONN:52-57`
- Requirements: add-and-encrypt (FR-009); never returned (FR-010); fetch-use-drop (FR-011); revoke leaves
  dependents degraded, not crashed (FR-013).
- Priority: P0

**UI-004 — Build**
- Source: `BUILD:205-212`
- Requirements: chat → deployed agent (FR-015–FR-022); registry search shown to user (FR-017); connection check
  with a way to add a missing credential (FR-019); both stops are durable LangGraph interrupts (FR-018, FR-020,
  FR-021); form mode sharing the same builder (FR-023); result shown as a card (FR-022).
- Priority: P0

**UI-005 — My Agents**
- Source: `MYAG:39-44`
- Requirements: card grid, one card per agent, shared card shape with Marketplace/Review (FR-054); click opens
  detail (FR-054); strictly own-workspace-only visibility (FR-055).
- Priority: P0

**UI-006 — Agent · Overview**
- Source: `AGENT:34-36`
- Requirements: config-derived graph (FR-026); instructions; full tool table with risk + approval mode
  (FR-058); both scores with itemized checks (FR-056–FR-057).
- Priority: P0

**UI-007 — Agent · Playground**
- Source: `AGENT:37-40`
- Requirements: chat window (FR-027); inline Approve/Reject on risky calls, nothing proceeds until answered
  (FR-028); pause survives restart (FR-029); thumbs up/down feeds score (FR-030).
- Priority: P0

**UI-008 — Agent · Connections**
- Source: `AGENT:41-43`
- Requirements: show dependency health (FR-031); configuration references connections abstractly only (FR-032);
  revoke degrades, does not crash (FR-013).
- Priority: P0

**UI-009 — Agent · Runs**
- Source: `AGENT:44-45`
- Requirements: run history with status/latency/cost/outcome (FR-033); feeds scoring (FR-034).
- Priority: P0

**UI-010 — Agent · API**
- Source: `AGENT:46-48`
- Requirements: callable URL (FR-035); working downloadable Postman collection (FR-036); cross-company calls get
  404 not 403 (FR-037).
- Priority: P0

**UI-011 — Agent · Settings**
- Source: `AGENT:49-51`
- Requirements: publish blocked below threshold with a stated reason (FR-039); unguarded write tool blocks
  publish (FR-040); publishing strips company-internal material (FR-041).
- Priority: P0

**UI-012 — Admin Review**
- Source: `REVIEW:113-118`
- Requirements: admin-only queue (FR-043); publish parks a run here, may wait days, across restarts (FR-042,
  FR-047); Approve / Request-changes / Reject, first two resume the same parked run (FR-045–FR-046); nothing
  reaches the marketplace any other way (FR-049).
- Priority: P0

**UI-013 — Marketplace (list view)**
- Source: `MARKET:37-42`
- Requirements: only admin-approved listings (FR-049); listing shows design only, never credentials/internal
  detail (FR-050); "Add to my workspace" copies configuration, installer supplies own credentials (FR-051–
  FR-052); publisher never sees installer's runs (FR-053).
- Priority: P0

**UI-014 — Marketplace (detail / install view)**
- Source: `MARKET:69-119`
- Requirements: per-required-server connection check before/at install (FR-052); the listing's tool table (tool
  name, risk, approval mode) shown before install, mirroring the agent overview tab's tool table
  (`MARKET:91-104`); explicit "what is not here" list — builder identity, credentials, internal URLs,
  runs/threads (FR-041, SEC-009).
- Priority: P0

---

# 11. API Requirements

The prose brief mandates only that an endpoint exists, that it is company-scoped with 404-masking, and that a
working Postman export exists (`PS:207-215`). The specific endpoint shapes below are drawn from the `agent.html`
mockup's API tab and are the clearest available signal of intended shape, but — unlike the invoke/404/Postman
requirements — they are not independently corroborated by the prose brief or the nine graded checks, so they are
marked accordingly.

**API-001 — Invoke endpoint**
- Requirement: A synchronous invoke endpoint exists for each agent, accepting some form of input and returning a
  response.
- Source: `PS:209-211`; `AGENT:320,323-326` (`POST /v1/agents/:id/invoke`)
- Priority: P0 (an invoke endpoint's *existence* is explicit; exact path/verb/payload shape shown is a mockup
  illustration, not a mandated contract — design choice).

**API-002 — Streaming endpoint**
- Requirement: A streamed variant of invoke (e.g., over SSE).
- Source: `AGENT:333` (`POST /v1/agents/:id/stream`)
- Priority: **P1, and arguably out of MVP scope** — `PS:300` explicitly lists "Streaming in the playground" under
  "If you finish early" (a stretch goal), which directly conflicts with the mockup showing it as a standing
  endpoint. See §16.

**API-003 — Resume endpoint**
- Requirement: An endpoint to answer a pending approval/interrupt.
- Source: `AGENT:334` (`POST /v1/agents/:id/resume`)
- Priority: P0 for the underlying *capability* (required by graded check 6 via FR-029); P1 for its specific
  exposure as a public REST endpoint with this shape (inferred from mockup only).

**API-004 — Postman collection endpoint**
- Requirement: An endpoint returning the agent's Postman collection as JSON.
- Source: `AGENT:335` (`GET /v1/agents/:id/postman`)
- Priority: P1 — the *download button producing a working collection* is P0 (FR-036); exposing it additionally
  as its own GET endpoint is a mockup-only detail.

**API-005 — Bearer token auth, company-scoped, 404-masked**
- Requirement: Every invoke-family endpoint authenticates via a bearer token and authorizes by company; a
  cross-company token gets 404.
- Source: `AGENT:324` (`Authorization: Bearer $FORGE_TOKEN`); `PS:214-215`; graded check 9
- Priority: P0 — CRITICAL. See SEC-011.

**API-006 — Postman collection must produce a real response**
- Requirement: The downloadable Postman collection must be a valid Postman v2.1 collection which, once the token
  variable is filled in, can be sent and returns a genuine (not canned) response from the agent.
- Source: `PS:211-212`; `AGENT:412-451` (live export logic, schema
  `https://schema.getpostman.com/json/collection/v2.1.0/collection.json`); graded check 8
- Priority: P0 — CRITICAL. See FR-036.

---

# 12. Data Requirements

The mock data in `DATA` (`docs/assets/data.js`) is explicitly labeled by its own file header as "Mock data for
the Forge mockups. Illustrative only — students build their own" (`DATA:1`). Entities below are inferred from
that file plus the prose brief; **field names, types, and enumerated values shown are illustrative**, not a
schema mandate, except where the prose brief itself states a constraint (noted per entity).

**DATA-001 — User**
- Fields (illustrative): identity, display name, initials, single company membership, admin boolean.
- Source: `DATA:4` (`me: {name, initials, org, role}`); `SIGNIN` whole screen
- Constraint (explicit): belongs to exactly one company; carries an admin boolean (`SIGNIN:62-64`, FR-002).

**DATA-002 — Company / Workspace (tenant)**
- Fields (illustrative): name.
- Source: `DATA` various `org` fields; `PS` rule 2
- Constraint (explicit): is the isolation boundary (SEC-001, SEC-002).

**DATA-003 — MCP Server (registry entry)**
- Fields (illustrative): name, scope (global/tenant), transport, auth type, status (ok/down), connected flag,
  last-checked time, description, tool list.
- Source: `DATA:126-190`; `REG:107-124` (registration form fields)
- Constraint (explicit): tool list must be populated by live introspection, not manual entry (FR-004).

**DATA-004 — Tool (child of Server)**
- Fields (illustrative): name, risk (read/write/destructive), description.
- Source: `DATA:132-189`
- Constraint (explicit): risk must be one of exactly three values (FR-005).

**DATA-005 — Connection (credential)**
- Fields (illustrative): server, status (active/expired/revoked), added date, last-used time, encrypted secret.
- Source: `DATA:192-198`; `CONN:36-50`
- Constraint (explicit): secret is encrypted at rest and never returned (SEC-003, SEC-004).

**DATA-006 — Agent**
- Fields (illustrative): name, description, status (draft/live/pending_review/published/degraded), topology
  (single/supervisor), owning company, servers used, model identifier, instructions text, schedule (optional),
  score, grade, run count, last-run time.
- Source: `DATA:6-124`; `AGENT:171-179`
- Constraint (explicit): exactly two scores per agent (FR-056); topology is single or supervisor+specialists
  (FR-059).

**DATA-007 — Agent Configuration document**
- Fields: **not specified.** The brief deliberately leaves this open: "Work out for yourself what that document
  needs to contain. That is the central design problem of this capstone." (`PS:157-158`)
- Source: `PS:151-158` (rule 1)
- Constraint (explicit, minimal): must exist as a document (not generated code); a single runtime interprets it
  to assemble the agent; it must reference required connections abstractly only (SEC-005); it must record, per
  tool, risk and approval mode (FR-058). Everything beyond these constraints is an open design choice — see §15.

**DATA-008 — Agent–Tool binding**
- Fields (illustrative): server, tool name, risk, approval mode (auto/ask).
- Source: `DATA:22-24` example within `agents[].tools[]`
- Constraint (explicit): approval mode for write/destructive tools is platform-enforced (FR-058, SEC-007).

**DATA-009 — Subagent (specialist)**
- Fields (illustrative): name, role description. Present only when topology is `supervisor`.
- Source: `DATA:26-29`

**DATA-010 — Score**
- Fields (illustrative): numeric capability score (0–100 in the mock), letter safety grade (A–F in the mock).
- Source: `DATA:14,291-299`; `AGENT:146-168`
- Constraint (explicit): each score must be backed by an itemized list of checks (FR-057). Numeric scale, letter
  mapping, and formula are **not specified** — the mock's `70`/`B` publish-threshold numbers are illustrative
  example data only (`PS:201`, "you decide how to calculate them").

**DATA-011 — Run**
- Fields (illustrative): when, status (ok/wait/err), trigger (Schedule/Playground/API), latency (ms), cost
  (USD), outcome text.
- Source: `DATA:281-288`
- Constraint (explicit): must be sufficient to justify score checks (NFR-009).

**DATA-012 — Submission (review-queue item)**
- Fields (illustrative): agent snapshot, org, submitting user, submitted time, waiting duration, score/grade,
  description, required servers, list of `{ok, text}` checks.
- Source: `DATA:239-279`; `REVIEW:43-68`

**DATA-013 — Marketplace Listing**
- Fields (illustrative): name, description, publishing org (name only), score, grade, install count, required
  server types, topology.
- Source: `DATA:200-237`; `APP:99-118`
- Constraint (explicit): excludes builder identity beyond org name, credentials, internal URLs/system names, and
  runs/threads (SEC-009, `MARKET:108-119`).

**DATA-014 — Marketplace Installation**
- Fields: not modeled explicitly in `DATA` (no install records shown in the mock data) — inferred entity.
- Source: `PS:134-140`; `MARKET:84-89`
- Constraint (explicit): must be an independent copy, own credentials, no cross-visibility to/from the publisher
  (FR-051–FR-053).

---

# 13. Testing / Evaluation Requirements

The nine checks below (`PS:257-271`) are the literal, binary grading mechanism. Each is restated verbatim with
its cross-referenced requirement IDs.

**TEST-001 — Tenant isolation with the filter removed**
- Check (verbatim): "One user cannot reach another user's agents — with your application filter removed."
- Source: `PS:263`
- Validates: SEC-001, SEC-002, FR-055.

**TEST-002 — Credential search**
- Check (verbatim): "A credential we supply appears nowhere in anything your system stored."
- Source: `PS:264`
- Validates: SEC-003, SEC-004, SEC-006, FR-010, FR-011.

**TEST-003 — Unguarded write tool blocks publish**
- Check (verbatim): "An agent with an unguarded write tool cannot be published."
- Source: `PS:265`
- Validates: SEC-007, SEC-008, FR-039, FR-040.

**TEST-004 — Planted confidential content stripped on publish**
- Check (verbatim): "Planted confidential material does not survive publication to the marketplace."
- Source: `PS:266`
- Validates: SEC-009, FR-041.

**TEST-005 — Build resumes after a mid-build kill**
- Check (verbatim): "Killing the server mid-build resumes correctly on restart."
- Source: `PS:267`
- Validates: NFR-006, FR-018, FR-020, FR-021.

**TEST-006 — Overnight-pending approval resumes**
- Check (verbatim): "An approval left pending overnight still resumes the next day."
- Source: `PS:268`
- Validates: NFR-006, NFR-007, FR-029, FR-047.

**TEST-007 — Multi-agent demo runs end to end with its approval step**
- Check (verbatim): "The playground runs the multi-agent demo end to end, including its approval step."
- Source: `PS:269`
- Validates: FR-028, FR-059, FR-060.

**TEST-008 — Downloaded Postman collection gets a real response**
- Check (verbatim): "The downloaded Postman collection gets a real response."
- Source: `PS:270`
- Validates: FR-036, API-006.

**TEST-009 — Cross-company agent lookup does not reveal existence**
- Check (verbatim): "Asking for another company's agent by ID does not reveal that it exists."
- Source: `PS:271`
- Validates: SEC-011, FR-037.

**TEST-010 — Live presentation defense**
- Requirement: The team must be able to explain, live, why the system is built the way it is; passing all nine
  checks is not sufficient on its own. The presentation must include the actual running system — see `C12`.
- Source: `PS:273-274` ("Your presentation is graded alongside these. A system that passes all nine but that you
  cannot explain is not a pass."); presentation structure at `PS:243-253` (demo / design walkthrough / questions,
  15 minutes each); `PS:253` ("Bring the running system. Slides alone will not do.")
- Priority: P0.

---

# 14. Explicit Constraints

- C1 — Must implement the build/execution flow as a LangGraph graph with real interrupts and checkpointing
  (named explicitly, not inferred): "runs a multi-step LangGraph conversation that pauses for human input and
  survives restarts" (`PS:23`); course content list names "checkpointers" and "multi-agent handoffs" (`RM:20`).
- C2 — Must **not** depend on LangGraph Platform / its hosted Agent Server (requires a paid licence); must
  self-host the server from day one (`PS:284-286`).
- C3 — No paid account of any kind is required anywhere in the stack; free model tiers or a locally-run model are
  acceptable (`PS:280-281`).
- C4 — Free public MCP servers may be used; a custom one may be written if a specific capability is needed
  (`PS:281-282`).
- C5 — The submission must run via `docker compose up` (`PS:231`).
- C6 — The submission README must explain how to start the system and how to log in (`PS:231`).
- C7 — Implementation language/framework choice for the platform itself is unconstrained — "Build it in whatever
  framework you like" (`PS:30`); there is deliberately no starter code (`RM:80-82`).
- C8 — UI fidelity requirement is behavioral, not visual: "Match the behaviour, not the pixels" (`PS:30`;
  `IDX:204-206`).
- C9 — An agent must be represented as a configuration document; the runtime must not generate and execute
  arbitrary code (e.g., generated Python) to run an agent (`PS:151-158`, rule 1).
- C10 — Explicitly discouraged as time sinks (not stated as forbidden, but the brief says they "will eat your
  time and teach you very little here"): code generation with sandboxing, single sign-on, token exchange
  protocols, per-agent service accounts, canary deployments (`PS:304-307`).
- C11 — Teams of exactly four; registration and the 20 September deadline are course-administration constraints,
  not technical requirements (`PS:236-241`) — see §15 re: treating dates as boilerplate.
- C12 — The live presentation must include the actual running system; a demo recording and slides alone do not
  satisfy this ("Bring the running system. Slides alone will not do." — `PS:253`). See `TEST-010`.

---

# 15. Assumptions

Marked explicitly as **not** stated verbatim in the source material — do not treat these as requirements without
separate confirmation.

- A1 — **Tool risk classification mechanism.** The brief requires each tool be labeled read/write/destructive
  (FR-005) but does not say how the label is derived. *Project decision on record (not a brief requirement):*
  classification requires manual admin/owner review and confirmation after introspection — the platform must not
  trust an MCP server's self-reported annotation hints directly, since MCP tool annotations
  (`readOnlyHint`/`destructiveHint`) are optional and untrusted per the MCP spec itself. **This decision
  conflicts with the one piece of reference UI that depicts the classification flow:** `REG:134-139`'s "what
  happens on save" checklist shows classification happening automatically, inline, with the server going
  straight to `ok`/usable — no pending-review status exists anywhere in the `STATUS` enum (`DATA:291-297`) or
  the registry card's rendering logic. This conflict is not resolved here — see §16 item 11.
- A2 — **Score formula and numeric thresholds.** `PS:200-201` explicitly assigns this to the team ("You decide
  how to calculate them"). The mockup's "score ≥ 70 / grade ≥ B" publish gate (`AGENT:370-371`) is illustrative
  sample data, not a specified threshold.
- A3 — **Admin account provisioning mechanism.** `REVIEW:29` implies a platform-level admin identity distinct
  from any tenant company, but sign-in (`SIGNIN`) shows no role/org selection. How an admin account is created is
  unspecified — deferred, open question (§16).
- A4 — **Agent Configuration document schema.** Deliberately left open by the brief itself (`PS:157-158`); only
  the minimal constraints in DATA-007 are explicit.
- A5 — **Encryption algorithm / key management** for credentials at rest. Unspecified beyond "encrypted"
  (`PS:175`).
- A6 — **Checkpointer/persistence backend** for LangGraph interrupt state. Unspecified beyond "your own server"
  and the general course topic of "checkpointers" (`RM:20`, `PS:284-286`).
- A7 — **Performance/latency targets.** None specified; treat as demo-scale only (NFR-004).
- A8 — **Reject semantics on the parked review run.** Deferred, open question (§16).
- A9 — **Scheduling execution.** `PS:300` lists it as a stretch goal; whether the MVP needs a real execution
  engine behind the `schedule` field shown throughout the mockups, or can treat it as display-only, is deferred
  (§16).
- A10 — **Streaming and the public resume/postman-JSON endpoints** (API-002–API-004). Shown in the mockup's API
  tab but not corroborated by the prose brief; streaming is explicitly listed as a stretch goal, which directly
  conflicts with its appearance as a standing endpoint in the mockup (§16).
- A11 — **"20 September" deadline / groups-of-four.** Treated as reusable course-announcement boilerplate
  (`ANN:1` is literally labeled "paste-ready") rather than confirmed facts about this specific team's actual
  deadline.
- A12 — **404-masking scope beyond the invoke API.** SEC-011/FR-037 are stated verbatim only for the agent's
  callable URL. Extending the same 404-masking behavior to UI routes is a reasonable inference from `MYAG:43`
  ("even by guessing a URL") applied to agent detail pages, but is not stated verbatim for the UI layer as it is
  for the API.

---

# 16. Open Questions / Ambiguities

Carried forward from the initial inspection (some already partially resolved with the stakeholder; status noted)
plus new ones surfaced while writing this specification.

1. **Scheduling scope for MVP.** *(Deferred by stakeholder as of this writing.)* The brief's stretch-goal list
   contradicts the mockups, which treat `schedule` as baseline agent data (cards, detail page, run-trigger type,
   and the Build-chat demo itself sets "Weekdays 08:00" as part of a successful build). Needs a decision before
   any scheduler/executor is built.
2. **Admin account provisioning.** *(Deferred by stakeholder.)* Seeded platform-level admin vs. per-company admin
   flag — unresolved.
3. **Reject semantics on the parked review run.** *(Deferred by stakeholder.)* Does Reject resume-then-terminate
   the same LangGraph interrupt as Approve/Request-changes, or is it handled as a separate, non-graph action?
   `REVIEW:119-123` shows Approve and Request-changes both with a resume-style icon; Reject is shown differently
   (plain ✕, "closed").
4. **Streaming and the mockup-only API endpoints (stream / resume / postman-JSON).** The stream endpoint directly
   conflicts with the "if you finish early" stretch-goal listing of streaming. The resume and postman-JSON
   endpoints are plausible and low-risk to build, but are sourced only from the mockup's illustrative table, not
   the prose brief or the graded checks — confirm whether public REST exposure (vs. an internal-only mechanism)
   is actually wanted for MVP.
5. **Exact Agent Configuration document schema.** Deliberately left as "the central design problem of this
   capstone" (`PS:157-158`) — not an ambiguity to resolve via clarification, but flagged here as the largest
   single piece of designed-not-specified surface area, to be addressed in the architecture phase, not this spec.
6. **Score formula and thresholds.** Explicitly the team's own design choice (`PS:201`) — flagged so the
   mockup's illustrative "70/B" numbers are not mistaken for a spec'd contract during architecture.
7. **404-masking scope for UI routes vs. only the API.** Reasonable inference, not verbatim — confirm intended
   scope (agent detail pages? My Agents? Marketplace detail for an unapproved/foreign listing?) before
   implementing route-level authorization.
8. **Follow-up chat edits after initial build (FR-024).** The composer placeholder implies iterative refinement
   ("also include issues labelled bug") but neither the prose brief nor any reqPanel specifies whether this
   re-enters the same interrupt-bearing build graph, produces a new version, or edits in place.
9. **Documentation rule-count mismatch (informational, not blocking).** `README.md` says "seven rules" and omits
   the endpoint/Postman/404 rule from its list; the slide deck's "Rule six/seven" labels are shifted by one
   relative to `PS`'s canonical 8-rule numbering (deck skips a label for the "publishing strips the company"
   rule). `PS` is authoritative; no requirement is actually missing (the endpoint rule remains graded check 8),
   but this is worth knowing if referencing README/deck during the design write-up.
10. **Per-user privacy scope, nested inside company-level isolation (from adversarial review REV-004).** The
    agent Settings tab (`AGENT:352-361`) shows a "Private to you" card with its own "Change" affordance,
    distinct from "no other workspace can reach it at all" — and the Overview → Details card independently shows
    `Visible to: you only` (`AGENT:177`). This suggests agents may default to creator-private *within* their own
    company, with an explicit opt-in to share company-wide — a second isolation dimension nested inside the
    company boundary that `FR-054`, `FR-055`, `SEC-001`, `SEC-002`, `SEC-011`, and `FR-037` do not currently
    address (they treat company as the only boundary). This is also consistent with graded check 1's literal
    wording — "one **user** cannot reach another **user's** agents" (`PS:263`), not "one company" — which had not
    previously been read as potentially distinct from check 9's "another **company's** agent" (`PS:271`).
    **Not resolved here:** does intra-company visibility default to creator-private with an opt-in company-wide
    share, or is it unconditional and the settings-tab copy is just mockup flavor text? Whichever answer is
    correct changes the scope of `FR-054`, `FR-055`, `SEC-001`, `SEC-002`, `SEC-011`, and `FR-037`.
    **Resolved at HLD (`architecture/hld.md §0`, decision D1):** company + owner-user RLS, chosen by the
    stakeholder after reviewing this exact source. Agents default creator-private within their own company; the
    "Change" affordance is implemented as `setVisibility()` (HLD §1.5). This spec entry is kept, not deleted,
    as the record of the ambiguity and the reasoning that resolved it.
11. **Tool-risk-classification mechanism conflicts with the reference UI (from adversarial review REV-007).**
    The project decision recorded in `§15 A1` (manual admin/owner review required before a server is usable)
    has no supporting state anywhere in the source material — `REG:134-139`'s "what happens on save" checklist
    depicts fully automatic classification with the server going straight to `ok`, and no
    pending/awaiting-review value exists in the `STATUS` enum (`DATA:291-297`). **Not resolved here:** either
    revisit the manual-review decision, or — if it's kept — define a new status (e.g. `pending_classification`)
    and how `UI-002` represents a server sitting in it. Affects `FR-005`, `WF-001`.
    **Resolved at HLD (`architecture/hld.md §0`, decision D2):** manual review kept, with a new
    `pending_classification` tool status (HLD §1.3) and a corresponding admin-facing UI surface not present in
    any source mockup, explicitly flagged there as an addition beyond `problem-statement/`.
12. **Resubmission semantics after "Request changes" (from adversarial review REV-012).** `REVIEW:121` and
    `PS:127` establish that "Request changes" sends a submission back to the author with notes, but no source
    page states what happens when the author acts on those notes and clicks Publish again: does it resume the
    *same* parked interrupt/thread with updated content, or start an entirely new submission/thread? This is
    distinct from — and in addition to — the already-open question of Reject's resume semantics (item 3 above).
    **Not resolved here.** Affects `WF-005`, `FR-045`, `FR-046`.

---

# 17. Requirement Traceability

Per-requirement source citations are inline in §6–§13. The index below is a reverse map — source document to the
requirement IDs it substantiates — for audit purposes.

| Source document | Requirement IDs substantiated |
|---|---|
| `PS` — `PROBLEM-STATEMENT.md` (rules, six-step flow, grading, submission, constraints) | FR-001–FR-002, FR-004–FR-005, FR-009–FR-011, FR-015–FR-022, FR-028–FR-029, FR-035–FR-037, FR-039–FR-042, FR-045, FR-047, FR-049, FR-051–FR-053, FR-055–FR-060, all NFR-001–NFR-007/009/011, all SEC-001–SEC-013, all WF-001–WF-008 (narrative), all TEST-001–TEST-010, all C1–C11, A2, A9–A11 |
| `RM` — `README.md` | C1 (course-content naming), A6; informational rule-count note (§16.9) |
| `AN` — `ANNOUNCEMENT.md` | A11 (boilerplate deadline text) |
| `IDX` — `docs/index.html` | C8, screen index cross-references (UI-001–UI-014 overview), FR-025 (graph list) |
| `SIGNIN` | FR-001–FR-002, SEC-002, UI-001, A3 |
| `REG` | FR-003–FR-008, WF-001, WF-008, UI-002 |
| `CONN` | FR-009–FR-014, WF-002, WF-007, UI-003 |
| `BUILD` | FR-015–FR-024, WF-003, UI-004 |
| `MYAG` | FR-054–FR-055, SEC-002, UI-005 |
| `AGENT` | FR-025–FR-041, FR-058, WF-004, UI-006–UI-011, API-001–API-006, A10 |
| `REVIEW` | FR-042–FR-048, WF-005, UI-012, A8 (§16.3) |
| `MARKET` | FR-049–FR-053, WF-006, UI-013–UI-014, SEC-009, SEC-013 |
| `DATA` (illustrative only — never sole authority for a requirement) | DATA-001–DATA-014, A1–A2 |
| `APP` | FR-054 (card shape reuse), FR-050 (`listingCard`) |
| `DECK` | Corroborating restatement only — no requirement is sourced from `DECK` alone anywhere in this document |

---

## Summary classification

**A. Requirements that are definitely required** (stated verbatim in `PROBLEM-STATEMENT.md` and/or directly
tested by one of the nine graded checks): FR-001–FR-005, FR-009–FR-011, FR-015–FR-022, FR-026, FR-028–FR-029,
FR-032, FR-035–FR-037, FR-039–FR-042, FR-045–FR-047, FR-049, FR-051–FR-053, FR-055–FR-060; all of NFR-001–NFR-003,
NFR-006–NFR-007, NFR-009–NFR-010; all of SEC-001–SEC-013; all of TEST-001–TEST-010; C1–C9.

**B. Requirements inferred from multiple pages** (not a single verbatim sentence, but corroborated by ≥2
independent sources — prose + at least one screen, or ≥2 screens): FR-008, FR-013, FR-023, FR-025, FR-027,
FR-030–FR-031, FR-033–FR-034, FR-043–FR-044, FR-048, FR-050, FR-054, WF-001–WF-008, most of §10, DATA-001–
DATA-006, DATA-008–DATA-013.

**C. Ambiguous requirements** (real requirement exists, mechanism/scope undefined): A1 (tool risk classification
— partially resolved by project decision, not brief text, and that decision itself conflicts with the reference
UI — see §16 item 11), A3 (admin provisioning), A4 (config schema — open by design), A8 (reject semantics), A12
(404-masking scope for UI), open question §16.8 (follow-up chat edits). **Newly flagged by the adversarial
review (specs/spec-review.md):** `FR-054`, `FR-055`, `SEC-001`, `SEC-002`, `SEC-011`, `FR-037` (scope pending
§16 item 10 — per-user privacy layer), `FR-005`, `WF-001` (mechanism pending §16 item 11 — tool-classification
conflict), `WF-005`, `FR-045`, `FR-046` (resubmission semantics pending §16 item 12).

**D. Potential grading traps** (easy to get subtly wrong even with a superficially working demo):
- Enforcing isolation only in application code (fails TEST-001, which explicitly removes that layer).
- Letting a credential leak into a LangGraph trace, checkpoint blob, or agent-generated conversation transcript —
  not just the obvious "prompt" surface (fails TEST-002).
- Score/approval gates that are checked once at build time but not re-verified at publish time if the agent's
  tool set changed afterward (fails TEST-003).
- Stripping company data from the *displayed* marketplace listing but leaving it recoverable in the underlying
  stored configuration the installer's copy is cloned from (fails TEST-004).
- Using in-memory-only interrupt/checkpoint state that survives a graceful shutdown but not a hard kill (fails
  TEST-005).
- Implementing "resume" as a short-lived in-process timer/callback rather than durable state, which silently
  breaks after an overnight gap (fails TEST-006).
- Hand-authoring the required multi-agent demo agent's configuration directly instead of producing it through the
  platform's own build flow — the brief explicitly anticipates and forbids this shortcut (fails TEST-007 in
  spirit even if the demo runs).
- A Postman collection that is exported once from static/cached mock data rather than generated live against the
  real deployed agent and a real token (fails TEST-008).
- Returning 403, an empty 200, or a different error shape for cross-tenant agent access instead of exactly 404
  (fails TEST-009).
- Treating the mockup's illustrative score thresholds (70/B) or data shapes as a specified contract rather than
  example data, and defending that choice as "the spec said so" in the live presentation when it did not
  (undermines TEST-010, the presentation defense).

**E. Questions that must be answered before architecture begins:**
1. Scheduling: display-only field for MVP, or real execution engine? (§16.1)
2. Admin account provisioning mechanism? (§16.2)
3. Reject semantics on the parked review-graph run? (§16.3)
4. Are the streaming, resume, and Postman-JSON endpoints in scope as public REST surfaces for MVP, given
   streaming's explicit stretch-goal status? (§16.4)
5. What should the 404-masking behavior's scope be — API only, or also UI routes for cross-tenant resource IDs?
   (§16.7)
6. Does a post-build follow-up chat message re-enter the interrupt-bearing build graph, version the agent, or
   edit in place? (§16.8)
