# Architecture work rules

This rule governs how architecture, HLD, and LLD are produced and judged on this project.

1. **Architecture is system-level.** It defines the major components, their boundaries, and how data and control
   flow between them — not how any one component is built inside.
2. **HLD is component/service interaction level.** It defines what each component does, its interfaces, and how
   components interact with each other and with external systems — not internal implementation detail.
3. **LLD is implementation/detail level/plandefines data shapes, algorithms, concrete interfaces, and
   component-internal design — the level at which code gets written from.
4. **Keep these three levels distinct.** Don't let system-level structure, component interaction, and
   implementation detail bleed into the same document or decision — see `.claude/rules/capstone.md` and
   `CLAUDE.md` for the required stage-gated review workflow between them.
5. **Avoid premature microservices.** Split into separate services only when a requirement demands it (e.g. an
   independent scaling, deployment, or failure-isolation need) — not by default, and not because it "seems more
   correct."
6. **Avoid unnecessary infrastructure.** Don't add a queue, cache, search index, service mesh, or separate
   datastore unless a specific requirement needs it. Prefer the simplest infrastructure that satisfies the
   requirement.
7. **Every component must have a reason.** If a component can't be justified by pointing at a requirement (or a
   dependency of one), it doesn't belong in the architecture.
8. **Every major decision cites requirement IDs.** Reference the specific `spec.md` requirement ID(s)
   (`FR-`/`NFR-`/`SEC-`/`WF-`/`UI-`/`API-`/`DATA-`/`TEST-`) that justify it. No citable ID means it's a design
   choice, not a requirement-driven decision — label it as such.
9. **Account for security, failure, persistence, and testability wherever the requirements call for it.** For
   each major component or decision, check: what security requirement applies, what happens on failure, what
   must persist and survive a restart, and how it can be tested — and address only the ones that actually apply,
   per the cited requirement IDs. Don't add handling for a concern no requirement raises.
