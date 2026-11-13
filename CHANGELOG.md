# CHANGELOG — the-weaver (Tier 1: The Weaver)

CHANGELOG.md — build history for The Weaver, latest entry at top.

## [Unreleased]

### Good

- (none)

### Bad

- (none)

### Ugly

- (none)

## [v1.1.0] — 2026-11-13 — FROZEN

### Good

- `SPEC_V1_1.md`, `test_weaver_v1_1.py` (6 tests, run red first) and `weaver_v1_1.py`: reads P9 through substrate_v3's read-only API with verify-on-read (tampered claims are skipped and counted), and computes λ with P14 V3 in days. 14/14 pass.
- Built on James's delegation ("fix all 11 issues"). Frozen at 1.1.0 on James's sign-off ("freeze all", 2026-11-13).

### Bad

- Frozen on the laptop run alone (2026-11-13); confirmed on the S24 by James, 2026-11-13.
- v1.0.0 never found a claim in a real substrate: it parsed `created_at` with `float()`, but P9 writes ISO 8601 strings, so every row was skipped and the briefing always said "Nothing to weave". The v1 tests inserted numeric timestamps by hand. Pinned in test_weaver_v1_1 test 1; fixed in v1.1.

### Ugly

- (none)

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
