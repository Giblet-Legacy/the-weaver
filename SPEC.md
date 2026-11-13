# SPEC — the-weaver (Tier 1: The Weaver)

SPEC.md — specification for The Weaver.

Function:
    Reads P9 substrate, finds UNKNOWN claims decaying toward neutral,
    uses LLLM to generate a Morning Briefing that hands the thread
    back to the operator.

Tier:     Tier 1 — Consumer
Depends:  P9 Substrate (SQLite), P14 Leighton Engine, LLLM (CLI)
Version:  SPEC 1.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)

## 1. The Rule

The Weaver reads `FORGE_HOME/forge.db`. It finds active claims
where `capsule.UNKNOWN is not None`. For each, it computes λ using
P14's `compute_lambda` with default λ₀ = 1.5, k = 0.1, treating
the claim's `created_at` as the observation timestamp.

**Time unit.** P14's `compute_lambda` treats `t` as a bare float
and `k` as a bare float. The unit is not specified by P14. The
Weaver chooses **k in days⁻¹** and converts the database's
`created_at` timestamps (seconds) and the reference time to days
before calling P14. This is the only unit in which k = 0.1 produces
observable decay on human timescales (e.g. λ = 1.49 after 1 hour,
λ = 1.18 after 10 days, λ ≈ 1.00 after several weeks).

It sorts the candidates by λ ascending — most decayed first, i.e.
closest to neutral. It takes the top 3 and asks LLLM for one
concrete next step per claim.

## 2. Function Contracts

### 2.1 find_decayed_unknowns(db_path, now_ts=None) -> list[dict]
Returns candidate dicts sorted by λ ascending. Each contains
claim_id, subject, object, unknown_text, lambda, created_at.

### 2.2 build_prompt(claims) -> str
Constructs the LLLM prompt.

### 2.3 call_lllm(prompt) -> str
Shells out to `lllm gen "<prompt>"`. Raises RuntimeError if
LLLM_HOME is not set, the directory does not exist, or `lllm` is
not on PATH.

### 2.4 main(argv) -> int
Exit codes: 0 success, 1 runtime failure (missing DB, missing LLLM).

## 3. Known Limitations (v1.0.0)

- Uses default λ₀ = 1.5 and k = 0.1. Domain-specific calibration
  deferred to v2.
- Sorts by λ ascending (λ₀ ≥ 1.0 assumed — the default). Claims
  with λ₀ < 1.0 are handled but rank last.
- Only reads UNKNOWN claims. FACT/COUNTER decay is not reported.
- Read-only. Does not modify the substrate.
