# SPEC V1.1 — the-weaver (Tier 1: The Weaver, P9 v3 reader)

SPEC_V1_1.md — specification for weaver_v1_1.py, the layer above Weaver v1.0.0.

Function:
    Moves The Weaver onto P9's read API and P14's unit rule. weaver.py
    v1.0.0 is not edited. Where this document is silent, SPEC.md 1.0.0
    applies unchanged.

Tier:     Tier 1 — Consumer (The Compensator)
Depends:  P9 substrate_v3 (read-only API), P14 leighton_engine_v3, LLLM
Version:  SPEC 1.1.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)

---

## 1. Why v1.1

- **v1.0.0 finds nothing in a real substrate.** It reads `created_at`
  with `float()`, but P9 writes ISO 8601 strings
  (`2026-11-13T16:53:55.487591+00:00`). Every real claim was skipped,
  so the Morning Briefing (and The Legacy's Voice widget) always said
  "Nothing to weave". The v1 tests passed only because they inserted
  numeric strings by hand.
- v1.0.0 read `forge.db` with its own SQL and never verified a
  signature. P9 v3 now offers a read-only API with verify-on-read.
- v1.0.0 converted seconds to days itself before calling P14 v1. P14
  V3 now takes `time_unit` and does the conversion.

## 2. find_decayed_unknowns(db_path, now_ts=None, limit=3) -> list[dict]

1. Rows from `substrate_v3.list_claims(db_path, verify=True)` (active
   only, read-only). Rows that do not verify are skipped and counted
   in the module-level `last_skipped_unverified` (an int), so a
   tampered claim never reaches the briefing.
2. A candidate is a verified claim whose capsule has a non-empty str
   `UNKNOWN` face.
3. `created_at` is parsed as ISO 8601 (P9's format); a numeric string
   is accepted as epoch seconds for databases written by hand.
   Anything else is skipped.
4. λ = `leighton_engine_v3.compute_lambda([{timestamp: created,
   value: 1.5}], STACK_CLAIM_K, now, now, time_unit=STACK_TIME_UNIT)`.
5. Same output fields as v1 (`claim_id, subject, object, unknown_text,
   lambda, created_at` (epoch seconds), `delta_t`), sorted by λ
   ascending, at most `limit`.

## 3. Unchanged

`build_prompt`, `call_lllm` are v1.0.0's. `main` is v1.0.0's flow
with §2 in place of v1's search.

## 4. Tests (test_weaver_v1_1.py)

- A substrate written by P9 itself (ISO timestamps) yields candidates;
  v1.0.0 on the same file yields none (pins the defect).
- Sorted by decay: a 10-day-old dream ranks before a fresh one; its λ
  matches P14 V3 in days (≈ 1.18).
- Non-UNKNOWN claims are ignored; limit holds.
- A tampered claim is skipped and counted.
- The database bytes are unchanged after a run (read-only).
- `main` with a mocked LLLM prints the briefing; a missing database
  exits 1.

---

## Document control

- **SPEC 1.1.0** — 2026-11-13, by the VS Code AI on James's delegation
  ("fix all 11 issues").
