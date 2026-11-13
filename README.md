# the-weaver — Tier 1: The Weaver

README.md — repository purpose and consumer contract for The Weaver.

Function:
    Solves the "drift" problem. It reads P9 substrate, finds claims on
    the UNKNOWN face that are decaying toward neutral (forgotten
    dreams), and uses LLLM to generate a "Morning Briefing" to hand
    the thread back to the operator.

Tier:     Tier 1 — Consumer (The Compensator)
Depends:  P9 Substrate (SQLite), P14 Leighton Engine (decay math)
LLM:      LLLM only (lllm CLI as subprocess)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
Status:   1.0.0 frozen (weaver.py). v1.1 (weaver_v1_1.py, SPEC_V1_1.md)
          frozen at 1.1.0. v1.2 (weaver_v1_2.py, SPEC_V1_2.md: imports from
          any directory) frozen at 1.2.0. Run `python weaver_v1_2.py`.
