"""
weaver_v1_3.py — The Weaver v1.3, a briefing built from claims with the LLLM engine as an aside

Function:
    The entry point from v1.3 (SPEC_V1_3.md). The briefing is written
    from the fading UNKNOWN claims themselves (subjects, objects, λ, ids,
    question text), and the LLLM engine adds at most one line per claim,
    continued from the claim's subject and marked "LLLM:". The engine is
    found through LLLM_CLI (run with this Python) or `lllm` on PATH,
    since the engine's README installs `lllm` as a shell function that
    Python cannot see. A refusal or a missing engine never breaks the
    briefing. weaver.py, weaver_v1_1.py and weaver_v1_2.py are not edited.

Public API:
    1. engine_command() -> list[str]
    2. call_lllm(seed) -> str             — first line; a refusal raises
    3. compose_briefing(claims, gen=call_lllm) -> str
    4. main(argv) -> int
    (re-exported from v1.2: find_decayed_unknowns, build_prompt)

Tier:     Tier 1 — Consumer (The Compensator)
Depends:  weaver_v1_2.py (1.2.0); the LLLM engine (optional)
Spec:     SPEC_V1_3.md 1.3.0 (over SPEC_V1_2.md 1.2.0)
Version:  1.3.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import shutil
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import weaver_v1_2 as _v12  # noqa: E402  (puts the sibling layers on sys.path)
import weaver_v1_1 as _v11  # noqa: E402
import weaver as _v1  # noqa: E402

find_decayed_unknowns = _v12.find_decayed_unknowns
build_prompt = _v12.build_prompt


# ---------------------------------------------------------------------------
# 1. engine_command
#    SPEC_V1_3 §2 (the Cockpit v1.3 rule).
# ---------------------------------------------------------------------------
def engine_command():
    cli_path = os.environ.get("LLLM_CLI")
    if cli_path:
        if not os.path.isfile(cli_path):
            raise RuntimeError(f"LLLM unavailable: LLLM_CLI is not a file: {cli_path}")
        return [sys.executable, cli_path]
    found = shutil.which("lllm")
    if not found:
        raise RuntimeError("LLLM unavailable: set LLLM_CLI to the engine's lllm/cli.py, or put an "
                           "`lllm` executable on PATH")
    return [found]


# ---------------------------------------------------------------------------
# 2. call_lllm
#    `gen <seed>`; the first line only. Refusal, failure, no engine →
#    RuntimeError.
# ---------------------------------------------------------------------------
def call_lllm(seed):
    home = os.environ.get("LLLM_HOME")
    if not home:
        raise RuntimeError("LLLM unavailable: LLLM_HOME is not set")
    if not os.path.isdir(home):
        raise RuntimeError(f"LLLM unavailable: LLLM_HOME does not exist: {home}")
    try:
        r = subprocess.run(engine_command() + ["gen", seed], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise RuntimeError(f"LLLM unavailable: {e}") from None
    if r.returncode != 0:
        raise RuntimeError(f"LLLM failed: {((r.stderr or '') + (r.stdout or '')).strip()[:200]}")
    line = (r.stdout or "").strip().split("\n")[0].strip()
    if not line or line.startswith("(nothing"):
        raise RuntimeError(f"LLLM refused: {line or 'no output'}")
    return line


# ---------------------------------------------------------------------------
# 3. compose_briefing
#    SPEC_V1_3 §3: truth from the claims, one optional engine line each.
# ---------------------------------------------------------------------------
def compose_briefing(claims, gen=None):
    gen = gen or call_lllm
    if not claims:
        return "No UNKNOWN claims found. Nothing to weave."
    n = len(claims)
    lines = [f"Morning briefing: {n} open question{'' if n == 1 else 's'} {'is' if n == 1 else 'are'} fading.", ""]
    unavailable = None
    for i, c in enumerate(claims, 1):
        lines.append(f"{i}. {c['subject']} / {c['object']}  (λ {c['lambda']:.3f}, claim {c['claim_id'][:12]})")
        lines.append(f"   {c['unknown_text']}")
        if unavailable is None:
            try:
                lines.append(f"   LLLM: {gen(c['subject'])}")
            except RuntimeError as e:
                if not str(e).startswith("LLLM refused"):
                    unavailable = str(e)
        lines.append("")
    if unavailable:
        reason = unavailable[len("LLLM unavailable: "):] if unavailable.startswith("LLLM unavailable: ") else unavailable
        lines.append(f"(LLLM unavailable: {reason})")
    return "\n".join(lines).rstrip("\n")


# ---------------------------------------------------------------------------
# 4. main
#    v1.1's flow with compose_briefing. 0 whenever a briefing prints.
# ---------------------------------------------------------------------------
def main(argv):
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
