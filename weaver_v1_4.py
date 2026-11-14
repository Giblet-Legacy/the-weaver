"""
weaver_v1_4.py — The Weaver v1.4, one engine line per question, not per subject

Function:
    The entry point from v1.4 (SPEC_V1_4.md). As v1.3 (the briefing is
    written from the fading UNKNOWN claims; the LLLM engine adds at most
    one "LLLM:" line per claim), but the engine is seeded with each
    question's own object first ("S O", then "O", then "S"), and a line
    is kept only if it is new to the briefing and mentions the subject.
    v1.3 seeded with the subject alone, so every question on one subject
    got the same line. weaver.py and weaver_v1_1–v1_3 are not edited.

Public API:
    1. seeds(claim) -> list[str]
    2. about(line, subject) -> bool
    3. compose_briefing(claims, gen=call_lllm) -> str
    4. main(argv) -> int
    (re-exported from v1.3: engine_command, call_lllm,
     find_decayed_unknowns, build_prompt)

Tier:     Tier 1 — Consumer (The Compensator)
Depends:  weaver_v1_3.py (1.3.0); the LLLM engine (optional)
Spec:     SPEC_V1_4.md 1.4.0 (over SPEC_V1_3.md 1.3.0)
Version:  1.4.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import weaver_v1_3 as _v13  # noqa: E402  (puts the sibling layers on sys.path)
import weaver_v1_1 as _v11  # noqa: E402
import weaver as _v1  # noqa: E402

engine_command = _v13.engine_command
call_lllm = _v13.call_lllm
find_decayed_unknowns = _v13.find_decayed_unknowns
build_prompt = _v13.build_prompt

_NOT_NAMES = {"the", "layer"}


# ---------------------------------------------------------------------------
# 1. seeds
#    SPEC_V1_4 §1: "S O", "O", "S"; no repeats, no empty seeds.
# ---------------------------------------------------------------------------
def seeds(claim):
    s, o = (claim.get("subject") or "").strip(), (claim.get("object") or "").strip()
    out = []
    for seed in (f"{s} {o}".strip(), o, s):
        if seed and seed not in out:
            out.append(seed)
    return out


# ---------------------------------------------------------------------------
# 2. about
#    SPEC_V1_4 §2: the line names one of the subject's words.
# ---------------------------------------------------------------------------
def about(line, subject):
    words = [w for w in re.split(r"[^A-Za-z0-9]+", subject.lower()) if len(w) >= 3 and w not in _NOT_NAMES]
    return not words or any(w in line.lower() for w in words)


# ---------------------------------------------------------------------------
# 3. compose_briefing
#    SPEC_V1_4 §2; everything else as v1.3 §3.
# ---------------------------------------------------------------------------
def compose_briefing(claims, gen=None):
    gen = gen or call_lllm
    if not claims:
        return "No UNKNOWN claims found. Nothing to weave."
    n = len(claims)
    lines = [f"Morning briefing: {n} open question{'' if n == 1 else 's'} {'is' if n == 1 else 'are'} fading.", ""]
    unavailable, used = None, set()
    for i, c in enumerate(claims, 1):
        lines.append(f"{i}. {c['subject']} / {c['object']}  (λ {c['lambda']:.3f}, claim {c['claim_id'][:12]})")
        lines.append(f"   {c['unknown_text']}")
        for seed in seeds(c) if unavailable is None else ():
            try:
                line = gen(seed)
            except RuntimeError as e:
                if str(e).startswith("LLLM refused"):
                    continue
                unavailable = str(e)
                break
            if line not in used and about(line, c["subject"]):
                used.add(line)
                lines.append(f"   LLLM: {line}")
                break
        lines.append("")
    if unavailable:
        reason = unavailable[len("LLLM unavailable: "):] if unavailable.startswith("LLLM unavailable: ") else unavailable
        lines.append(f"(LLLM unavailable: {reason})")
    return "\n".join(lines).rstrip("\n")


# ---------------------------------------------------------------------------
# 4. main
#    v1.3's flow with v1.4's compose_briefing; UTF-8 out, never a
#    UnicodeEncodeError on a console that has no "λ" (SPEC_V1_4 §3).
# ---------------------------------------------------------------------------
def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    db_path = _v1._db_path()
    if not os.path.exists(db_path):
        print(f"database missing: {db_path}", file=sys.stderr)
        return 1
    try:
        claims = find_decayed_unknowns(db_path)
    except Exception as e:
        print(f"weaver failed: {e}", file=sys.stderr)
        return 1
    if _v11.last_skipped_unverified:
        print(f"skipped {_v11.last_skipped_unverified} claim(s) that failed verification", file=sys.stderr)
    print(compose_briefing(claims))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
