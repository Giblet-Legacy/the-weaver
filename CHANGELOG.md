# CHANGELOG — the-weaver (Tier 1: The Weaver)

CHANGELOG.md — build history for The Weaver, latest entry at top.

## [Unreleased]

### Good

- (none)

### Bad

- (none)

### Ugly

- (none)

## [v1.4.0] — 2026-11-14 — FROZEN

### Good

- `weaver_v1_4.py`, `SPEC_V1_4.md`, `test_weaver_v1_4.py` (8 tests, run
  red first): each open question gets its own engine line. The engine
  is seeded "subject object", then "object", then "subject", and a line
  is kept only if it is new to the briefing and names the subject. On
  James's PC build (fc1ac624ac8b) the three envelope-layer questions
  now get three different lines instead of "Envelope-layer and P2 at."
  three times. 29/29 pass. weaver.py and v1.1-v1.3 untouched. Built on
  James's delegation ("yes"). Not frozen (NOTES).

### Bad

- v1.3's `main` stops with UnicodeEncodeError on a Windows console
  (cp1252 has no "λ"). The Legacy was not affected (it does not print).
  v1.4's `main` writes UTF-8 and replaces what the console cannot show.

### Ugly

- (none)

## [v1.3.0] — 2026-11-13 — FROZEN

### Good

- `SPEC_V1_3.md`, `test_weaver_v1_3.py` (4 tests, run red first) and
  `weaver_v1_3.py`: the briefing is written from the fading UNKNOWN
  claims themselves, each cited with lambda and id; the LLLM engine adds
  at most one line per claim, continued from its subject. The engine is
  found through `LLLM_CLI` (run with this Python) or `lllm` on PATH; a
  refusal or a missing engine never breaks the briefing.
- 21/21 pass from the repo. weaver.py, v1_1 and v1_2 untouched. Built on
  James's delegation ("make sure [the LLLM] is properly wired in").
  Frozen at 1.3.0 (James: "freeze commmit and push", 2026-11-13); laptop run, S24 run
  still to be confirmed.

### Bad

- Found 2026-11-13: v1.0-v1.2 sent a chat-style prompt to an n-gram
  engine that continues seeds, and could not reach the engine at all
  (its README installs `lllm` as a shell function Python cannot see).

### Ugly

- From the parent directory the frozen v1 and v1.1 test files still fail
  to import (P14 v1 cwd bug, recorded at v1.2); v1.2 and v1.3 pass.

## [v1.2.0] — 2026-11-13 — FROZEN

### Good

- `SPEC_V1_2.md`, `test_weaver_v1_2.py` (3 tests, run red first) and `weaver_v1_2.py`: puts weight-, trust-, leighton-engine- and envelope-layer on sys.path from its own file before importing v1.1, so The Weaver imports and runs from any working directory. 17/17 pass.
- Frozen at 1.2.0 (James: "freeze", 2026-11-13).

### Bad

- Frozen on the laptop run alone (2026-11-13); confirmed on the S24 by James, 2026-11-13.
- Weaver v1.1 (frozen) could not be imported outside a sibling repo: weaver.py imports P14 v1, which finds weight-layer relative to the working directory. The tests ran from inside the repo and missed it; The Legacy's Morning Briefing failed when started from the parent directory. Found 2026-11-13; pinned in test_weaver_v1_2 test 1.

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
