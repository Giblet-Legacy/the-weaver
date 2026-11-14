# SPEC V1.4 — the-weaver (The Weaver: one engine line per question, not per subject)

SPEC_V1_4.md — specification for weaver_v1_4.py, the layer above The Weaver v1.3.0.

Function:
    James (2026-11-14) saw his first briefing with the engine running:
    three open questions, all on envelope-layer, each with the same
    line, "LLLM: Envelope-layer and P2 at." v1.3 seeds the engine with
    the subject alone, and the engine is deterministic, so every
    question on one subject gets the same line. v1.4 seeds with each
    question's own object first and keeps a line only if it is new to
    the briefing and about the subject. SPEC_V1_3.md remains
    authoritative for everything this document does not change.
    weaver.py and weaver_v1_1–v1_3 are not edited.

Tier:      Tier 1 — Consumer (The Compensator)
Depends:   weaver_v1_3.py (1.3.0); the LLLM engine (optional)
Version:   SPEC V1.4 1.4.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Seeds

For a claim with subject S and object O, `seeds(claim)` is, in order
and without repeats or empty seeds:

1. `"S O"` — the most specific;
2. `"O"` — the question's own topic;
3. `"S"` — v1.3's seed.

## 2. Which line is kept

`compose_briefing(claims, gen=call_lllm)` asks the engine for each seed
in turn and keeps the first line that:

- is not a refusal (`call_lllm` raises "LLLM refused");
- is not already in this briefing; and
- is about the subject: it contains, ignoring case, at least one of the
  subject's words (S split on anything that is not a letter or digit,
  without "the", "layer" and words under three characters). A subject
  with no such words accepts any line.

If no seed gives such a line, the claim has no `LLLM:` line. Checked on
James's PC build (fc1ac624ac8b) for the three envelope-layer questions:
"P1 envelope v2, P2 sign …", "Status: 2.0.0 frozen. New code imports
envelope v2. …" and "Envelope-layer design contradicts envelope-layer
status." — three different lines, each about envelope.

Everything else is v1.3's §3: the heading, subjects, objects, λ, ids and
UNKNOWN text come only from the claims; an unavailable engine (any
error other than a refusal) stops engine calls for the rest of the
briefing and adds `(LLLM unavailable: <reason>)` once.

## 3. Reaching the engine, main

v1.3's `engine_command`, `call_lllm` and `main` (with v1.4's
`compose_briefing`), except that `main` writes UTF-8 and replaces what
the console cannot show. v1.3's `main` stopped with UnicodeEncodeError
on a Windows console (cp1252 has no "λ"), found while checking v1.4 on
James's PC.

## 4. Tests (test_weaver_v1_4.py)

- `seeds`: order, no repeats, no empty seeds.
- `compose_briefing` with a stand-in engine:
  - three questions on one subject get three different lines, from
    their objects;
  - a refused seed falls through to the next;
  - a line that is not about the subject is skipped;
  - a line already used is skipped, and a claim with no usable line
    has no `LLLM:` line;
  - an unavailable engine is noted once and not called again;
  - no claims gives v1.3's message.
- `main` prints a briefing from a real P9 database with an UNKNOWN cube
  and no engine installed, exit 0; run as a script with a cp1252
  console encoding it still exits 0.

---

## Document control

- **SPEC V1.4 1.4.0** — 2026-11-14, by the VS Code AI on James's
  delegation (the repeated "Envelope-layer and P2 at." line; "yes").
