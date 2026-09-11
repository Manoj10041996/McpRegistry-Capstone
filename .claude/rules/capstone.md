# Capstone source-of-truth and traceability policy

This rule governs how requirements and design work are sourced and justified on this project.

1. **`problem-statement/` is authoritative.** It is the sole source of truth for what this capstone requires.
   General knowledge, convention, or "how these platforms usually work" is never a substitute for it.
2. **`McpRegistry-Capstone/specs/spec.md` is the normalized specification**, derived from `problem-statement/`.
   Use it as the day-to-day reference; where it conflicts with `problem-statement/`, `problem-statement/` wins
   and `spec.md` must be corrected to match.
3. **Every design feature maps to requirement IDs.** Any architecture, HLD, LLD, or code decision must cite the
   specific `spec.md` requirement ID(s) (`FR-`/`NFR-`/`SEC-`/`WF-`/`UI-`/`API-`/`DATA-`/`TEST-`) it satisfies. A
   feature with no citable ID is not a requirement — call it what it is (a design choice) or don't build it yet.
4. **No unsupported requirements.** Nothing is treated as required unless it traces to an exact location in
   `problem-statement/`. Do not infer a requirement from what seems reasonable or common practice.
5. **No silent assumptions.** Anything not explicitly stated in `problem-statement/` must be logged as an
   assumption or open question (`spec.md` §15/§16) — never written into a requirement's normative text as if it
   were settled.
6. **No modifications to `problem-statement/`, ever.** It is read-only source material for the life of this
   project.
