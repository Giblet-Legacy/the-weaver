# SPEC V1.2 — the-weaver (Tier 1: The Weaver, import from any directory)

SPEC_V1_2.md — specification for weaver_v1_2.py, the layer above Weaver v1.1.0.

Function:
    Makes The Weaver importable and runnable from any working
    directory. weaver.py and weaver_v1_1.py are frozen and not edited.
    Behaviour is otherwise exactly SPEC_V1_1.md.

Tier:     Tier 1 — Consumer (The Compensator)
Depends:  weaver_v1_1.py (Weaver v1.1.0)
Version:  SPEC 1.2.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)

---

## 1. The defect

`weaver_v1_1` imports `weaver` (v1.0.0), which at import time does
`import leighton_engine` (P14 **v1**). P14 v1 finds `weight-layer`
relative to the **working directory** (P14 NOTES; frozen). So importing
The Weaver from anywhere except inside a sibling repository fails with
`ModuleNotFoundError: No module named 'weight'`. The Weaver's own tests
and The Legacy's tests run from inside a sibling repo, so they passed.
Found on 2026-11-13 when The Legacy v4 ran from the parent directory:
its Morning Briefing failed.

## 2. The fix

Before importing `weaver_v1_1`, weaver_v1_2 puts the sibling
`weight-layer`, `trust-layer`, `leighton-engine-layer` and
`envelope-layer` directories on `sys.path`, located from its own file.
P14 v1's working-directory insert then no longer matters: `weight` is
already importable. No code below is changed.

## 3. Public API

`find_decayed_unknowns`, `build_prompt`, `call_lllm`, `main` and
`last_skipped_unverified` behave as in weaver_v1_1. `main` and
`find_decayed_unknowns` are v1.1's own functions, re-exported.

## 4. Tests (test_weaver_v1_2.py)

- In a fresh process whose working directory is outside the
  repositories: `import weaver_v1_1` fails (the defect, pinned) and
  `import weaver_v1_2` succeeds and finds a dream in a real P9
  substrate.
- The re-exported functions are v1.1's objects.

---

## Document control

- **SPEC 1.2.0** — 2026-11-13, by the VS Code AI during the
  Projection work (James: "the whole projection").
