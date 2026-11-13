"""
weaver.py — The Weaver primitive layer

Function:
    Reads P9 substrate, finds UNKNOWN claims decaying toward neutral,
    uses LLLM to generate a Morning Briefing. Reads only; never writes.

Public API:
    1. find_decayed_unknowns — Query P9 for UNKNOWN claims, sorted by λ.
    2. build_prompt          — Construct the LLLM prompt.
    3. call_lllm             — Shell out to `lllm gen`.
    4. main                  — CLI entry point.

Tier:     Tier 1 — Consumer (The Weaver)
Depends:  P9 Substrate, P14 Leighton Engine, LLLM (CLI)
Version:  1.0.0 (on freeze; 0.0.0-dev until then)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys
import json
import sqlite3
import subprocess
import time

# Bootstrap P14
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "envelope-layer")))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "leighton-engine-layer")))
import leighton_engine


_DEFAULT_LAMBDA_0 = 1.5
_DEFAULT_K = 0.1
_DEFAULT_LIMIT = 3


def _forge_home():
    home = os.environ.get("FORGE_HOME")
    if not home:
        home = os.path.expanduser("~/.forge")
    return home


def _db_path():
    return os.path.join(_forge_home(), "forge.db")


# ---------------------------------------------------------------------------
# 1. find_decayed_unknowns
#    Query P9 for active UNKNOWN claims, sort by current λ ascending.
# ---------------------------------------------------------------------------
def find_decayed_unknowns(db_path, now_ts=None, limit=_DEFAULT_LIMIT):
    if now_ts is None:
        now_ts = time.time()

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT claim_id, capsule, created_at FROM claims WHERE is_active = 1"
        ).fetchall()
    finally:
        conn.close()

    candidates = []
    for claim_id, capsule_json, created_at in rows:
        try:
            capsule = json.loads(capsule_json)
        except json.JSONDecodeError:
            continue
        unknown_text = capsule.get("UNKNOWN")
        if not unknown_text:
            continue
        try:
            created_ts = float(created_at)
        except (TypeError, ValueError):
            continue
        delta_t = max(0.0, now_ts - created_ts)
        # P14's k = 0.1 assumes t is in days. Convert seconds to days.
        created_days = created_ts / 86400.0
        now_days = now_ts / 86400.0
        try:
            lam = leighton_engine.compute_lambda(
                [{"timestamp": created_days, "value": _DEFAULT_LAMBDA_0}],
                k=_DEFAULT_K,
                reference_time=now_days,
                computed_at=now_ts,
            )["lambda"]
        except Exception:
            continue
        candidates.append({
            "claim_id": claim_id,
            "subject": capsule.get("subject", ""),
            "object": capsule.get("object", ""),
            "unknown_text": unknown_text,
            "lambda": lam,
            "created_at": created_ts,
            "delta_t": delta_t,
        })

    candidates.sort(key=lambda c: c["lambda"])
    return candidates[:limit]


# ---------------------------------------------------------------------------
# 2. build_prompt
#    Construct the LLLM prompt from the candidate claims.
# ---------------------------------------------------------------------------
def build_prompt(claims):
    lines = [
        "You are the Weaver. You write a Morning Briefing for the operator.",
        "Below are UNKNOWN claims from their substrate that are decaying",
        "toward neutral — dreams they may have forgotten.",
        "",
        "For each claim, suggest one concrete next step.",
        "",
    ]
    for i, c in enumerate(claims, 1):
        lines.append(f"{i}. [{c['subject']} / {c['object']}] λ={c['lambda']:.3f}")
        lines.append(f"   UNKNOWN: {c['unknown_text']}")
        lines.append("")
    lines.append("Write the briefing as three short paragraphs. No preamble.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. call_lllm
#    Shell out to `lllm gen "<prompt>"`. Raises RuntimeError on any failure.
# ---------------------------------------------------------------------------
def call_lllm(prompt):
    home = os.environ.get("LLLM_HOME")
    if not home:
        raise RuntimeError("LLLM unavailable: LLLM_HOME is not set")
    if not os.path.isdir(home):
        raise RuntimeError(f"LLLM unavailable: LLLM_HOME does not exist: {home}")
    try:
        result = subprocess.run(
            ["lllm", "gen", prompt],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError("LLLM unavailable: `lllm` not on PATH")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"LLLM failed: {(e.stderr or '').strip()[:200]}")
    return result.stdout


# ---------------------------------------------------------------------------
# 4. main
#    CLI entry point. Returns 0 on success, 1 on any failure.
# ---------------------------------------------------------------------------
def main(argv):
    db_path = _db_path()
    if not os.path.exists(db_path):
        print(f"database missing: {db_path}", file=sys.stderr)
        return 1

    try:
        claims = find_decayed_unknowns(db_path)
    except Exception as e:
        print(f"weaver failed: {e}", file=sys.stderr)
        return 1

    if not claims:
        print("No UNKNOWN claims found. Nothing to weave.")
        return 0

    prompt = build_prompt(claims)
    try:
        briefing = call_lllm(prompt)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1

    print(briefing)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
