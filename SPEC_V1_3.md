# SPEC V1.3 — the-weaver (The Weaver: a briefing built from claims, the engine as an aside)

SPEC_V1_3.md — specification for weaver_v1_3.py, the layer above The Weaver v1.2.0.

Function:
    Makes the morning briefing work with the LLLM engine that actually
    exists. SPEC_V1_2.md remains authoritative for everything this
    document does not change. weaver.py, weaver_v1_1.py and
    weaver_v1_2.py are not edited.

Tier:      Tier 1 — Consumer (The Compensator)
Depends:   weaver_v1_2.py (1.2.0); the LLLM engine (optional)
Version:   SPEC V1.3 1.3.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Why v1.3

- v1.0's briefing sends a chat-style instruction prompt ("You are the
  Weaver … write three short paragraphs") to `lllm gen`. The engine is
  an n-gram model that continues from a seed; an instruction prompt
  as a seed gives a refusal or noise.
- `lllm` is installed by the engine's README as a bash function, which
  `subprocess` cannot see, so the call always failed.
- A refusal ("(nothing: …)", exit 0) would have been printed as the
  briefing.

## 2. Reaching the engine

`engine_command()` and `call_lllm(seed)` follow the Cockpit v1.3 rule
(SPEC_V1_3 §5): `LLLM_HOME` must be set and exist; the engine is
`[sys.executable, $LLLM_CLI]` if `LLLM_CLI` names a file, else `lllm`
on PATH; a non-zero exit, empty output, or output starting "(nothing"
is RuntimeError. Only the first line of the engine's output is kept.

## 3. The briefing

`compose_briefing(claims, gen=call_lllm) -> str`, from
`find_decayed_unknowns` results (most faded first):

    Morning briefing: N open questions are fading.

    1. <subject> / <object>  (λ 1.234, claim <first 12 of id>)
       <UNKNOWN text>
       LLLM: <one line the engine continued from the subject>

- The heading, subjects, objects, λ, ids and UNKNOWN text come only
  from the claims (truth from claims).
- The `LLLM:` line is the engine's continuation of the claim's subject
  (fluency from counts). It is omitted when the engine refuses or is
  unavailable; if it was unavailable for any claim, the briefing ends
  with `(LLLM unavailable: <reason>)` once. The briefing never fails
  because of the engine.
- No claims → "No UNKNOWN claims found. Nothing to weave."

## 4. main

v1.1's flow, with `compose_briefing` in place of the prompt and call.
Exit 0 whenever the briefing is printed.

## 5. Tests (test_weaver_v1_3.py)

- engine_command: LLLM_CLI with this Python; missing file and no engine
  raise.
- call_lllm: a stand-in engine script's first line; a refusal raises.
- compose_briefing: claims cited in order with λ and ids; an engine
  line per claim when it answers; omitted lines on refusal; one
  unavailable note when the engine is missing; no claims message.
- main prints a briefing from a real P9 database with an UNKNOWN cube
  and no engine installed, exit 0.

---

## Document control

- **SPEC V1.3 1.3.0** — 2026-11-13, by the VS Code AI on James's
  delegation ("make sure [the LLLM] is properly wired in"; "all of it").
