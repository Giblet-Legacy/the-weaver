# Forge Stack Context — The Weaver

CLAUDE.md — Context briefing for AI assistants working in this repository.

## What this repo is
Tier 1 Consumer. It reads P9 substrate (the claims database), queries
P14 Leighton Engine for decayed trust, and uses LLLM to weave the most
important `UNKNOWN` claims into a daily "Morning Briefing".

## The Immutable Rule
Entry point from v1.1: `weaver_v1_1.py` (SPEC_V1_1.md): P9 via `substrate_v3`, P14 via `leighton_engine_v3` (days). `weaver.py` is frozen v1.0.0.

Never rewrite a primitive. Add a layer. You consume P9 and P14. You do
not rewrite them.

## LLM: LLLM only
Do not use Ollama or OpenRouter. You shell out to `lllm gen` to generate
the briefing.

## Constraints
- Standard library only (except `pytest` for dev).
- British English (-ise, artefact).
- Header discipline on every file and function.
