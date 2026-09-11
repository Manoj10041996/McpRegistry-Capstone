# Adversarial Review of specs/spec.md

**Role:** Adversarial reviewer. **Scope:** every requirement in `spec.md` (§6–§13, ~136 IDs) checked against
every page in the source material (`PROBLEM-STATEMENT.md`, `README.md`, `ANNOUNCEMENT.md`, `docs/index.html`,
all 8 `docs/screens/*.html`, `docs/assets/data.js`, `docs/assets/app.js`, `docs/deck/index.html`). `spec.md` is
**not modified** by this review.

**Method:** (1) re-read every source page line-by-line looking for anything not represented, or represented
more weakly, in `spec.md`; (2) re-read every `spec.md` requirement and check its claim against the exact source
text it cites; (3) specifically hunted for the eight categories called out in the review brief.

**Verdict key:** **PASS** — accurately and traceably represented. **PARTIAL** — represented, but incomplete,
imprecise, or missing a sub-condition present in the source. **MISSING** — a real source-backed requirement has
no corresponding entry anywhere in `spec.md`. **CONTRADICTED** — `spec.md`'s claim conflicts with what a source
page actually shows. **UNSUPPORTED** — `spec.md` asserts something no source page actually backs (checked for;
see §3).

---

## 1. Summary

| Verdict | Count | Detail |
|---|---|---|
| PASS | ~123 of ~136 IDs | Listed compactly in §4 |
| PARTIAL | 6 | REV-006, REV-008, REV-009, REV-010, REV-012, REV-013 |
| MISSING | 5 | REV-001, REV-002, REV-003, REV-005, REV-011 |
| CONTRADICTED | 2 | REV-004, REV-007 |
| UNSUPPORTED | 0 | None found — see §3 |

**Two findings materially change the security model and should block sign-off on §5 (Actors) and §8 (Security)
until resolved: REV-004 (undisclosed per-user privacy layer inside a company) and REV-007 (the adopted "manual
tool-review" decision contradicts the reference UI).** The rest are real but lower-blast-radius.

---

## 2. Issues (the 13 non-PASS items)

### REV-001 — MISSING: "Demo recording" submission deliverable

1. **Requirement ID:** None in `spec.md`. Should be a new FR (e.g. `FR-061`) and/or `§14` constraint.
2. **Source:** `PS:227-234` (submit table, item 2: "**A demo recording** | The six steps above, start to finish,
   without cuts."); corroborated independently by `DECK` slide 14 ("A demo recording walking the six steps,
   start to finish, without cuts.").
3. **Current interpretation in spec.md:** `G8` ("Deliver the unbroken six-step demo flow") covers the *live
   system's capability* to walk the flow, and `TEST-010` covers the *presentation*. Neither captures that a
   **recorded video** of that flow is itself a required, separately-gradable submission artifact.
4. **Problem:** This is one of exactly four items in the "What to submit" table — a literal grading deliverable
   — and it is absent from `spec.md` entirely. A team could build a flawless platform, ace the live demo, and
   still be non-compliant with the submission requirements because no recording exists.
5. **Recommended correction:** Add `FR-061 — Demo recording deliverable`: a video recording of the six-step flow
   (register → connect → describe → test → publish → install), executed start to finish with no cuts, is a
   required submission artifact. Source `PS:232`, `DECK` slide 14. Priority P0.
6. **Confidence:** High — verbatim in two independent sources, unambiguous.

---

### REV-002 — MISSING: "Design document" submission deliverable

1. **Requirement ID:** None in `spec.md`. Should be a new FR (e.g. `FR-062`).
2. **Source:** `PS:227-234` (submit table, item 3: "**A design document** | One or two pages: how you made each
   rule true, and what you would do differently with another month."); corroborated by `DECK` slide 14 ("A short
   design document — how you made each rule true, and what you would do differently with another month.").
3. **Current interpretation in spec.md:** Not referenced anywhere — not in Goals, not in §14 Explicit Constraints,
   not in §6 Functional Requirements.
4. **Problem:** Same class of omission as REV-001 — a named, literal submission deliverable with a specific
   content requirement (must address each rule's satisfaction + a retrospective "what I'd do differently") is
   entirely absent from the spec.
5. **Recommended correction:** Add `FR-062 — Design document deliverable`: a 1–2 page document explaining how
   each of the 8 rules was made true, and what the team would change with another month, is a required submission
   artifact — distinct from this spec document and from source code comments. Source `PS:233`, `DECK` slide 14.
   Priority P0.
6. **Confidence:** High — verbatim in two independent sources.

---

### REV-003 — MISSING: Live running system required at presentation ("slides alone will not do")

1. **Requirement ID:** None in `spec.md`. Related to `TEST-010` but not covered by it.
2. **Source:** `PS:253` ("Bring the running system. Slides alone will not do.")
3. **Current interpretation in spec.md:** `TEST-010` covers *that* the team must defend the design live, and
   cites the 15/15/15-minute structure, but does not state the explicit constraint that a live, running instance
   of the platform must be present and demoed — not a recording, not slides.
4. **Problem:** A team that plans to present with only the demo recording (REV-001) plus slides would satisfy a
   literal reading of `TEST-010` as currently worded but would fail this explicit brief requirement.
5. **Recommended correction:** Add to `TEST-010` (or a new `§14` constraint, e.g. `C12`): the presentation must
   include the actual running system, not just the recording or slides. Source `PS:253`.
6. **Confidence:** High — unambiguous, single explicit sentence.

---

### REV-004 — CONTRADICTED: undisclosed per-user privacy layer inside a company

1. **Requirement IDs affected:** `FR-054`, `FR-055`, `SEC-001`, `SEC-002`, `SEC-011`, `FR-037` (all treat
   "company/workspace" as the *only* isolation boundary).
2. **Source:** `AGENT` (agent.html) Settings tab, `T.settings` (lines ~352-361):
   > **Private to you** — "Nobody else in **Northwind Labs** can see this agent, and no other workspace can
   > reach it at all." [**Change** button]

   Corroborated independently by the same screen's Overview → Details card (`T.overview`, line ~177):
   `<dt>Visible to</dt><dd>you only</dd>`.
3. **Current interpretation in spec.md:** `§5 Actors and Roles`, `FR-054/FR-055`, and `SEC-001/SEC-002` all
   describe exactly one isolation boundary — company/workspace — phrased as "My Agents shows only the signed-in
   user's own workspace's agents" (`FR-055`), i.e. every member of a company is implicitly assumed to see every
   agent that company owns.
4. **Problem:** The mockup explicitly distinguishes two *separate* statements — "nobody else in \[my own
   company\] can see this" **and** "no other workspace can reach it at all" — as two different guarantees, with
   a togglable "Change" control on the first one. That means the source material describes a **second,
   finer-grained privacy layer** (creator-private-by-default within a company, with an explicit opt-in to share
   company-wide) that `spec.md` has silently collapsed into the single company-level boundary. This is not a
   cosmetic detail: it changes what `SEC-002` ("no cross-tenant visibility... including guessing a URL") and the
   404-masking rule (`SEC-011`/`FR-037`, currently scoped only to "another company's token") need to cover. The
   brief's own check 1 wording is itself agnostic here — "**One user** cannot reach another user's agents" —
   not "one company" — which is consistent with a per-user boundary existing on top of the company one and was
   not previously flagged.
5. **Recommended correction:** Treat this as an open design question requiring your decision (do not let me
   silently pick), phrased as: does an agent default to creator-private within its own company, with an explicit
   company-wide "share" action — or is intra-company visibility unconditional and the settings-tab copy is just
   mockup flavor text? If the former, `FR-054/055`, `SEC-001/002`, and `SEC-011/FR-037` all need a second
   isolation dimension (owner-user, nested inside owner-company) added, and check 1's "another user" wording
   should be re-examined against check 9's "another company" wording for the same reason.
6. **Confidence:** High that the source material describes this distinctly (two independent citations, explicit
   "Change" affordance) — but the *correct resolution* is genuinely ambiguous, not something I should silently
   assume either way.

---

### REV-005 — MISSING: registering a *global* server requires admin privileges

1. **Requirement ID:** `FR-006` (currently silent on this).
2. **Source:** `REG` (registry.html) registration modal, lines 121-124:
   ```html
   <label>Visible to</label>
   <select><option>Just my workspace</option><option>Everyone (admin only)</option></select>
   ```
3. **Current interpretation in spec.md:** `FR-006` — "A server can be shared with every company (`global`) or
   kept private to the registering company (`tenant`)" — states the two visibility values but not who is allowed
   to choose `global`.
4. **Problem:** The dropdown option's own label — "Everyone **(admin only)**" — is an explicit authorization
   constraint on this action that `spec.md` drops. Without it, a plausible (and wrong) implementation lets any
   regular user promote a server to platform-wide visibility.
5. **Recommended correction:** Amend `FR-006` (or add `SEC-014`): only an admin may register or mark a server as
   `global`/shared-to-everyone; a non-admin user's registration is restricted to `tenant` (private-to-my-company)
   scope. Source `REG:121-124`.
6. **Confidence:** High — literal UI label, unambiguous.

---

### REV-006 — PARTIAL (weakened): credential-search test scope narrowed to a named list

1. **Requirement IDs affected:** `SEC-004`, `NFR-002`.
2. **Source:** `PS:178-180` (rule 3, "How this is tested"): "we search **everything your system stored** for the
   token we gave you. Finding it anywhere is a fail."
3. **Current interpretation in spec.md:** `SEC-004` — "No API response, UI surface, log entry, trace, or saved
   conversation ever contains a stored credential's usable value." `NFR-002` similarly says "configuration, logs,
   traces, or saved conversations."
4. **Problem:** Both requirements phrase the guarantee as an enumerated list of five-ish named surfaces. The
   brief's actual test is deliberately unbounded — "everything your system stored," "anywhere" — which as
   written should also cover things the enumerated list doesn't obviously suggest: LangGraph checkpoint blobs,
   vector-store embeddings, cached LLM request/response pairs, backup snapshots, container/environment dumps, and
   any other persistence layer the team adds later. An enumerated list reads as implicitly exhaustive and invites
   exactly the failure mode graded check 2 is designed to catch: "we didn't think to check X."
5. **Recommended correction:** Reword `SEC-004`/`NFR-002` to state the unbounded principle first ("no credential
   value may exist in **any** persisted state the platform controls, of any kind"), with the named list kept only
   as non-exhaustive examples ("including but not limited to...").
6. **Confidence:** Medium-high — this is a phrasing/scope risk, not a factual error, but it is exactly the kind
   of "weakened security requirement" the review brief asked me to hunt for.

---

### REV-007 — CONTRADICTED: adopted "manual tool-risk review" decision vs. the reference UI's automatic flow

1. **Requirement IDs affected:** `FR-005`, `WF-001`, `§15 A1`.
2. **Source:** `REG` (registry.html) "What happens on save" checklist, lines 134-139 — four items rendered with
   a **pass** checkmark as one atomic, automatic sequence: (1) open a connection, (2) ask for its tool list, (3)
   **mark each tool read, write or destructive**, (4) store the list, mark the server healthy — with only a
   failure branch ("if it does not answer, nothing is saved"). No pending/awaiting-manual-review state is shown
   anywhere between steps 3 and 4; the server becomes immediately `ok`/usable.
3. **Current interpretation in spec.md:** `§15 A1` records a project decision (made earlier in this
   engagement, not stated in the brief itself) that tool-risk classification "requires manual admin/owner review
   and confirmation after introspection" before a server is usable.
4. **Problem:** `spec.md` correctly labels A1 as a project decision layered on top of an unspecified brief
   requirement — but it does not disclose that this specific decision **conflicts with the one piece of reference
   UI that actually depicts the classification flow**. The mockup shows classification happening automatically,
   inline, with the server going straight to `ok`/connected — no "pending classification" or "needs review"
   status exists anywhere in the `STATUS` enum (`DATA:291-297`) or the registry card's rendering logic to
   represent a server awaiting manual sign-off.
5. **Recommended correction:** Either (a) revisit the manual-review decision given it has no supporting UI state
   to render against, or (b) if manual review is kept, explicitly add a new server/tool status (e.g.
   `pending_classification`) to `DATA-003`/`DATA-004` and describe how the registry screen (`UI-002`) represents
   it — since none of the source material currently shows what that state looks like. Either way, `A1` should be
   updated to disclose the conflict rather than presenting the decision as merely "unspecified by the brief."
6. **Confidence:** High that the contradiction exists as described; medium on which resolution is preferable
   (that's a design call, not something to silently resolve here).

---

### REV-008 — PARTIAL: connection *expiry* (not just revocation) also triggers `degraded`, and isn't in FR-013/WF-007

1. **Requirement IDs affected:** `FR-013`, `WF-007`.
2. **Source:** `CONN` (connections.html), lines 71-79: "The Jira connection above **has expired**. The agent
   that used it is now showing as **degraded**..."; `DATA:197` shows the Jira connection's `status: "expired"`
   (a third status distinct from `active`/`revoked`).
3. **Current interpretation in spec.md:** `FR-013`/`WF-007` state only that **revoking** a connection degrades
   dependent agents; expiry is not mentioned as an independent trigger.
4. **Problem:** The example the mockup itself uses to illustrate the degraded state is an *expired* connection,
   not a *revoked* one — meaning natural credential expiry (e.g., an OAuth token lapsing on its own, with no user
   action) is at least as central a trigger as manual revocation, yet `spec.md` only models the manual-action
   case.
5. **Recommended correction:** Broaden `FR-013`/`WF-007` to "any connection transitioning out of `active` status
   (whether by user revocation or by the credential expiring) degrades dependent agents the same way," and add a
   corresponding requirement for *detecting* expiry (background check, or detection on first failed use).
6. **Confidence:** High — the mock data and the screen's own illustrative example both use expiry, not
   revocation.

---

### REV-009 — PARTIAL: `FR-044` overstates how much is "stripped" before admin review

1. **Requirement IDs affected:** `FR-044`, `SEC-009`.
2. **Source:** `REVIEW` (review.html) queue rendering, lines 43-58, renders `${q.org} · ${q.by} · ${q.submitted}`
   directly per submission (`DATA:239-279` — every `submissions[]` entry carries `org` and `by`, e.g. `org:
   "Northwind Labs", by: "Priya Raman"`) — i.e. the admin plainly sees the submitting company **and the
   individual author's name**. Compare `AGENT` T.settings, line 369: "Your credentials and anything internal to
   your workspace are **stripped first**" (before going to the admin) — and `MARKET`'s "what is not here" list,
   which excludes "**Who built it, beyond an org name**" only from the *final public listing*, not from the
   review queue.
3. **Current interpretation in spec.md:** `FR-044` — "The review screen shows, per submission, the agent's
   **stripped design**..." — implies the admin sees an already-fully-stripped artifact.
4. **Problem:** Read literally, `FR-044` suggests the admin's view has already had the same stripping applied
   that the final marketplace listing gets. The actual source shows a two-stage stripping: credentials and
   internal-workspace detail (URLs, secrets) are removed before the admin sees a submission, but organizational
   identity (company name **and individual author name**) is still visible to the admin, with individual author
   name being stripped only at the later step of going from "approved" to "live in the public marketplace
   listing." `FR-044`'s wording doesn't distinguish these two stages.
5. **Recommended correction:** Reword `FR-044` to specify exactly what is stripped pre-review (credentials,
   internal URLs/system names) versus what remains visible to the admin only (company name, submitting author)
   versus what's stripped again at final publish (author name, per `SEC-009`/`FR-050`'s "publishing org name"
   only).
6. **Confidence:** Medium — this is an imprecision in wording, not a functional contradiction; the underlying
   two-stage behavior is otherwise correctly split across `FR-041`/`FR-044`/`FR-050`, it's just not stated
   explicitly as a two-stage pipeline anywhere.

---

### REV-010 — PARTIAL: `FR-022` implies both scores exist at build completion; only one does

1. **Requirement ID:** `FR-022`.
2. **Source:** `BUILD` (build.html) result card, lines 169-172:
   ```html
   <dt>Score</dt><dd class="row" style="gap:7px">
     <span class="faint">not tested yet</span>
     <span class="grade c">C</span>
   </dd>
   ```
   and prose immediately below (lines 182-185): "It scores **C** until you have actually run it. Test it in the
   playground — the score climbs, and you cannot publish below a B."
3. **Current interpretation in spec.md:** `FR-022` — "...shows the finished result (name, description,
   capability summary, **initial score**) as a card."
4. **Problem:** "Initial score" (singular) glosses over that, per the mockup, only the **safety/governance
   grade** (the "C" in this example) is computable immediately from the static configuration; the **capability
   score** is explicitly shown as "not tested yet" until the agent has actual run history. `FR-056`/`FR-057`
   correctly establish two separate scores elsewhere in the spec, but `FR-022` doesn't reflect that one of them
   starts in an explicit "untested" state rather than a numeric value.
5. **Recommended correction:** Reword `FR-022` to state that the newly-built agent's card shows an immediate
   safety/governance grade (computed from static config checks) while the capability score is shown as
   "not yet tested" until the agent has run history.
6. **Confidence:** Medium-high — directly evidenced by the mockup's own copy, low ambiguity.

---

### REV-011 — MISSING: no standing invariant generalizing "marketplace is the single deliberate exception"

1. **Requirement ID:** None currently states this as its own control; closest are `SEC-001`/`SEC-010`/`SEC-013`,
   each of which covers one specific mechanism rather than the general principle.
2. **Source:** `PS:171` (immediately following rule 2's isolation text): "The marketplace is the single
   deliberate exception — **which is exactly why an admin guards it.**"
3. **Current interpretation in spec.md:** Isolation (`SEC-001/002`) and marketplace-gating (`SEC-010`) are both
   present, but nothing in `spec.md` states the *general* invariant that the reviewed marketplace/install path is
   the **only** sanctioned way data ever crosses a company boundary — i.e., no other current or future feature
   (support tooling, cross-company sharing, admin impersonation, debugging endpoints, etc.) may create a second,
   unreviewed crossing.
4. **Problem:** Without this stated as a standing design invariant, a plausible but wrong addition later (e.g. "let
   an admin view any company's agents directly for support purposes," or a convenience "share this agent with
   another company" shortcut bypassing review) would violate the brief's intent while not obviously violating any
   single enumerated `SEC-XXX` item.
5. **Recommended correction:** Add a new `SEC-014` — "The reviewed publish→approve→install path is the only
   mechanism by which any data may cross a company boundary; no other feature may create a second, unreviewed
   cross-tenant data path." Source `PS:171`.
6. **Confidence:** Medium — this is a generalization of an explicit sentence rather than a literal restatement,
   but the sentence is clearly meant as a governing principle, not a throwaway aside.

---

### REV-012 — PARTIAL/ambiguous: resubmission after "Request changes" isn't modeled

1. **Requirement IDs affected:** `WF-005`, `FR-045`, `FR-046`.
2. **Source:** `REVIEW:121` ("**Request changes** — back to the author, still theirs"); `PS:127` ("...sends it
   back with notes."). No source page shows what happens when the author then acts on those notes and re-submits.
3. **Current interpretation in spec.md:** `WF-005` ends the "Request changes" branch at "back to author, editable"
   with no next step defined.
4. **Problem:** It's unclear whether clicking Publish again after edits (a) resumes the *same* parked
   interrupt/thread with updated content, (b) starts an entirely new submission/thread, or (c) something else —
   and this is not listed among the existing open questions in `spec.md §16` even though it directly affects the
   durable-interrupt design (`NFR-006`) the same way the admin-decision resume does.
5. **Recommended correction:** Add this as a new open question in `§16` (e.g. §16.10): does re-publishing after
   "Request changes" resume the same parked graph run/thread, or create a new one?
6. **Confidence:** Medium — clearly unaddressed by any source page, so this is a genuine gap rather than a
   subjective reading.

---

### REV-013 — MISSING (minor): marketplace detail view's tool table isn't captured under UI-014

1. **Requirement ID:** `UI-014`.
2. **Source:** `MARKET` (marketplace.html) detail view, "What it can do" table (lines ~91-104) — shows the
   listing's tools with risk badges and approval-mode column, same shape as the agent overview's tool table.
3. **Current interpretation in spec.md:** `UI-014` lists only the per-required-server connection check and the
   "what is not here" exclusion list; it omits that the detail view also surfaces the agent's tool/risk/approval
   table to a prospective installer before they install.
4. **Problem:** Minor completeness gap — an installer's ability to see exactly what tools (and their risk level)
   they're about to grant access to before installing is a reasonable pre-install transparency requirement that
   isn't captured anywhere.
5. **Recommended correction:** Add to `UI-014`: the marketplace detail view shows the listing's tool table (tool
   name, risk, approval mode) before install, mirroring the agent overview tab's tool table.
6. **Confidence:** Medium — clearly present in the mockup, but low severity (a display completeness item, not a
   security or workflow gap).

---

## 3. Explicit negative checks (requested focus areas that came back clean)

- **"Requirements mentioned in slides but missing from brief.html":** Checked every slide in `DECK` against
  `PS`. Every substantive claim in the deck is a restatement or compression of something already in `PS` (the
  only divergence is the cosmetic rule-numbering-by-one-slide issue `spec.md §16.9` already documents). **No
  deck-only requirement was found.**
- **UNSUPPORTED:** Checked every `spec.md` requirement that cites a source for a claim not actually present at
  that citation. Found none — every requirement's prose is backed by the text at its cited location. (Several
  requirements draw on illustrative mock data, but `spec.md` already flags those explicitly as illustrative
  rather than presenting them as requirements — see its own §12 preamble and §15 A2.)

---

## 4. Compact verdict table (all other requirement IDs)

Every ID below is **PASS** unless cross-referenced to a REV-item above.

- **FR-001–FR-004:** PASS. **FR-005:** PASS on the requirement itself; see **REV-007** for its mechanism
  assumption (A1). **FR-006:** see **REV-005**. **FR-007–FR-012:** PASS. **FR-013:** see **REV-008**.
  **FR-014–FR-021:** PASS. **FR-022:** see **REV-010**. **FR-023–FR-041:** PASS, except **FR-044**: see
  **REV-009**. **FR-042–FR-053:** PASS. **FR-054–FR-055:** PASS on wording, but scope affected by **REV-004**.
  **FR-056–FR-060:** PASS.
- **NFR-001:** PASS. **NFR-002:** see **REV-006**. **NFR-003–NFR-011:** PASS.
- **SEC-001–SEC-002:** PASS on wording, scope affected by **REV-004**. **SEC-003:** PASS. **SEC-004:** see
  **REV-006**. **SEC-005–SEC-010:** PASS. **SEC-011:** PASS on wording, scope affected by **REV-004**.
  **SEC-012–SEC-013:** PASS.
- **WF-001:** PASS on wording; see **REV-007** for the flow it describes. **WF-002–WF-004:** PASS. **WF-005:**
  see **REV-012**. **WF-006:** PASS. **WF-007:** see **REV-008**. **WF-008:** PASS.
- **UI-001–UI-013:** PASS. **UI-014:** see **REV-013**.
- **API-001–API-006:** PASS.
- **DATA-001–DATA-014:** PASS.
- **TEST-001–TEST-009:** PASS. **TEST-010:** PASS on what it covers; see **REV-003** for what it's missing.
- **§14 Explicit Constraints C1–C11:** PASS. **§15 Assumptions A1–A12:** PASS as disclosures, except A1 should
  additionally disclose the conflict in **REV-007**.

---

## 5. Recommended edit list for spec.md (not applied — for your approval)

1. Add `FR-061` (demo recording deliverable) — REV-001.
2. Add `FR-062` (design document deliverable) — REV-002.
3. Extend `TEST-010` or add `C12` (live system required at presentation) — REV-003.
4. Add an explicit open question (§16.11) on the per-user privacy layer, and flag `FR-054/055`, `SEC-002`,
   `SEC-011`, `FR-037` as scope-pending-that-answer — REV-004.
5. Amend `FR-006` (or add `SEC-014`) for admin-only global server registration — REV-005.
6. Reword `SEC-004`/`NFR-002` to lead with the unbounded "everything stored" principle — REV-006.
7. Update `A1` to disclose the conflict with the registry mockup's automatic flow — REV-007.
8. Broaden `FR-013`/`WF-007` to include expiry, not just revocation — REV-008.
9. Reword `FR-044` to describe the two-stage stripping pipeline accurately — REV-009.
10. Reword `FR-022` to reflect that only the safety grade, not the capability score, is available at build time
    — REV-010.
11. Add `SEC-014` (or fold into #5's new ID) generalizing the "marketplace is the only crossing" invariant —
    REV-011.
12. Add an open question on resubmission-after-request-changes semantics — REV-012.
13. Extend `UI-014` with the pre-install tool table — REV-013.

No changes have been made to `spec.md`. Awaiting your direction on which of the above to apply.
