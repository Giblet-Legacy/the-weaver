# CHANGELOG — the-weaver (Tier 1: The Weaver)

CHANGELOG.md — build history for The Weaver, latest entry at top.

## [v1.0.0] — 2026-11-13

### Good
- Repository scaffolded: `Giblet-Legacy/the-weaver` created as Tier 1
  Consumer (The Compensator).
- `weaver.py` implemented to SPEC v1.0.0.
- 8/8 pytest tests pass.
- Reads P9 substrate, queries P14 for decay, sorts UNKNOWN claims by
  λ ascending (most decayed first), generates LLLM briefing.
- LLLM-only integration. Fails cleanly if LLLM unavailable.
- Time unit resolved: k in days⁻¹, timestamps converted from seconds
  before calling P14. Recorded in SPEC §1.

### Bad
- P14 SPEC v1.0.0 does not define the time unit for k. The Weaver
  chose days⁻¹ as the working unit. This is a genuine gap in the
  frozen primitive, not just a consumer choice — any future consumer
  picking k faces the same ambiguity.

### Ugly
- First test run: `test_find_decayed_unknowns_sorted_by_decay` failed
  with `assert 1.0 < 1.0`. Both claims had decayed to exactly 1.0
  because k = 0.1 was applied to t in seconds, which produces
  e^(-86400) — astronomically small. Fixed by converting timestamps
  to days. The failure exposed a spec gap in P14, recorded in NOTES.
