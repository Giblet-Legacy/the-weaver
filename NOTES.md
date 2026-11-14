# NOTES — the-weaver (Tier 1: The Weaver)

NOTES.md — open questions and decisions for The Weaver.

## Open questions

- **Q4 — Freeze v1.4.0?** One engine line per question; UTF-8 console
  output (SPEC_V1_4.md). weaver_v1_4.py built and green on the laptop
  (29/29). Raised 2026-11-14. Owner: James.
- **Q3 — Freeze v1.3.0?** Briefing from claims, engine as an aside
  (SPEC_V1_3.md). Built and green on the laptop (21/21). Not yet run on
  the S24 or against the real engine. Raised 2026-11-13. Owner: James.
  **Resolved 2026-11-13 — James: "freeze commmit and push".** Frozen on the laptop run; S24 run still to be confirmed.
- **Q2 — Freeze v1.2.0?** **Resolved 2026-11-13 — James: "freeze".** Frozen on the laptop run; confirmed on the S24 by James, 2026-11-13. weaver_v1_2.py (import from any directory)
  built and green on the laptop (17/17). Raised 2026-11-13. Owner: James.
- **Q1 — Freeze v1.1.0?** **Resolved 2026-11-13 — James: "freeze all".** Frozen on the laptop run; confirmed on the S24 by James, 2026-11-13. weaver_v1_1.py built and green on the
  laptop (14/14). Not yet run on the S24 or against LLLM. Raised
  2026-11-13. Owner: James.

## Decisions
- Reads directly from `FORGE_HOME/forge.db` (P9's schema).
- Uses P14's `compute_lambda` to calculate decay, prioritizing
  UNKNOWN claims that are closest to neutral (1.0) because they are
  the ones most likely to be forgotten.
- The prompt is sent to LLLM via subprocess. If LLLM is unavailable,
  the tool fails gracefully and prints a clear error.

## Gaps exposed in frozen primitives

- **P14 Leighton Engine does not define the time unit for `k`.**
  `compute_lambda` accepts `k` and `t` as bare floats. Neither the
  unit of `k` nor the unit of `t` is specified in SPEC v1.0.0.
  This is a real gap, not just an oversight of the consumer — any
  consumer choosing `k` will pick a unit by guesswork unless it is
  told otherwise.
  **The Weaver's decision:** treat `k` as days⁻¹ and convert
  timestamps from seconds to days before calling P14. Recorded in
  this weaver's SPEC §1.
  **For P14 v2:** SPEC should say "k has unit time⁻¹, and callers
  are responsible for choosing the time unit consistently." That
  formalises the freedom the current spec accidentally grants.
  **Resolved 2026-11-13:** P14 V3 (leighton-engine-layer SPEC_V3.md)
  makes `time_unit` required and records days as the stack
  convention. weaver_v1_1 uses it.
