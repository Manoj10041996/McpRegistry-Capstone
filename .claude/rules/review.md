# Adversarial review requirement

No architecture artifact — architecture, HLD, or LLD — is finalized without an adversarial review pass first.
This is the substance behind the ARCHITECTURE REVIEW / HLD REVIEW / LLD REVIEW gates in `CLAUDE.md`'s design
workflow, not a separate optional step.

## Review against

- `problem-statement/` — the authoritative source.
- `McpRegistry-Capstone/specs/spec.md` — the normalized specification.
- Requirements traceability — every decision in the artifact must trace to a requirement ID; check the trace
  actually holds, don't just check that an ID is cited.

## Must identify

For the artifact under review, explicitly check for and report:

- **Missing requirements** — a requirement in `spec.md`/`problem-statement/` that the artifact doesn't address.
- **Unsupported design decisions** — a component, pattern, or technology in the artifact with no requirement
  behind it.
- **Contradictions** — anywhere the artifact conflicts with `spec.md` or `problem-statement/`, or conflicts with
  itself.
- **Over-engineering** — complexity, abstraction, or infrastructure beyond what the cited requirements need (see
  `.claude/rules/architecture.md`).
- **Security gaps** — anywhere a `.claude/rules/security.md` control isn't actually satisfied by the design.
- **Failure/recovery gaps** — anywhere the design doesn't account for a failure or restart-resume requirement
  that applies to it.
- **Testability gaps** — anywhere the design can't actually be verified against the requirement or graded check
  it claims to satisfy.

Findings get reported the way `specs/spec-review.md` does: requirement ID, source, current interpretation, the
problem, a recommended correction, and a confidence level. Don't silently fix what you find — report it, and let
ambiguous cases become open questions rather than a decision you make on your own.

## Disagreement is required, not optional

If a design the user proposes conflicts with `spec.md` or `problem-statement/`, say so plainly and explain the
conflict — do not soften it into a suggestion, and do not implement it as asked without flagging the conflict
first. Passing review is about the specification being satisfied, not about the user's proposal being approved.
