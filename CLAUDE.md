# Working instructions — Forge Agent Platform Capstone

## Source of truth

1. `problem-statement/` (and the GitHub repo it mirrors, `fnusatvik07/agent-platform-capstone`) is the sole
   authoritative source for requirements. Never answer a requirements question from general knowledge.
2. `McpRegistry-Capstone/specs/spec.md` is the normalized specification derived from that source. Use it for
   day-to-day reference; where it and `problem-statement/` disagree, `problem-statement/` wins and `spec.md`
   gets corrected.
3. Never modify anything under `problem-statement/` — it is read-only source material.

## Non-negotiable rules

- Never invent a requirement. Every requirement must trace to a specific location in `problem-statement/`.
- Never let an assumption, inference, or design choice pass as a requirement — keep it labeled as what it is
  (see `spec.md` §15 Assumptions / §16 Open Questions), even when it's convenient not to.
- Every architecture, HLD, or LLD decision must cite the requirement ID(s) (`FR-`/`NFR-`/`SEC-`/`WF-`/`UI-`/
  `API-`/`DATA-`/`TEST-`) it satisfies. A decision with no citable requirement is a design choice — say so.
- Challenge unsupported technology choices. A library, pattern, or service needs a requirement or an explicit,
  stated tradeoff behind it — not habit, familiarity, or "it's common."
- Prefer the minimum architecture necessary to satisfy the actual requirements. No speculative abstraction, no
  building for hypothetical future needs.
- When an ambiguity would materially change the architecture, ask before proceeding — don't guess silently.
- When clarification genuinely isn't available in the moment, document the assumption explicitly (as an
  assumption) and flag it for later confirmation — don't let it quietly become load-bearing.
- Preserve traceability end to end: requirement → architecture → HLD → LLD → code. If a link breaks, fix the
  trace before moving on, don't paper over it.
- Keep architecture, HLD, and LLD as distinct artifacts. Architecture = system-level structure and boundaries.
  HLD = component-level design within that structure. LLD = implementation-level detail (data shapes,
  interfaces, algorithms). Don't blend them into one document or skip a layer.
- Do not write implementation code until the design artifacts for that part of the system have been through
  their review stage and are stable.

## Design review workflow (required, in order)

```
REQUIREMENTS → ARCHITECTURE → ARCHITECTURE REVIEW → HLD → HLD REVIEW → LLD → LLD REVIEW → FINAL TRACEABILITY
```

Each arrow is a gate. Before advancing past a REVIEW stage, perform an explicit proof-check of everything
produced so far against `spec.md` and `problem-statement/` — walk every requirement ID the stage touches and
confirm it's satisfied. Don't advance with open items unless the user has explicitly signed off on deferring
them.

## How to work with me

Default to challenging my proposed designs, not agreeing with them. When I propose an architecture or design
choice, ask what requirement justifies it, what would break it, and whether something simpler satisfies the
same requirement — before building on top of it. Silence is not agreement; if something looks unjustified,
say so before proceeding.
