"""
weaver_v1_1.py — The Weaver v1.1, reading P9 through its v3 API

Function:
    The layer above The Weaver v1.0.0 (weaver.py), and the entry point
    to run from v1.1 on. Finds verified, active UNKNOWN claims through
    P9 substrate_v3's read-only API, parses P9's ISO 8601 timestamps
    (v1.0.0 could not, so it never found a real claim), and computes λ
    with P14 V3 in days. The briefing prompt and the LLLM call are
    v1.0.0's (SPEC_V1_1.md).

    weaver.py is not edited.

Public API:
    1. find_decayed_unknowns(db_path, now_ts=None, limit=3) -> list[dict]
    2. main(argv) -> int
    (re-exported from v1.0.0: build_prompt, call_lllm)

Internal helpers (not exported):
    3. _epoch — P9 created_at (ISO 8601, or numeric) → epoch seconds, or None
    4. _layer — sibling layer import by directory and module name

Tier:     Tier 1 — Consumer (The Compensator)
Depends:  P9 substrate_v3, P14 leighton_engine_v3, LLLM (CLI)
Spec:     SPEC_V1_1.md 1.1.0 (over SPEC.md 1.0.0)
Version:  1.1.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import importlib
import os
import sys
import time
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import weaver as _v1  # noqa: E402

build_prompt = _v1.build_prompt
call_lllm = _v1.call_lllm

LAMBDA_ZERO = 1.5
last_skipped_unverified = 0


# ---------------------------------------------------------------------------
# 4. _layer
# ---------------------------------------------------------------------------
def _layer(dirname, modname):
    path = os.path.abspath(os.path.join(_HERE, "..", dirname))
    if path not in sys.path:
        sys.path.insert(0, path)
    return importlib.import_module(modname)


# ---------------------------------------------------------------------------
# 3. _epoch
#    SPEC_V1_1 §2 step 3.
# ---------------------------------------------------------------------------
def _epoch(created_at):
    try:
        return datetime.fromisoformat(created_at).timestamp()
    except (TypeError, ValueError):
        pass
    try:
        return float(created_at)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# 1. find_decayed_unknowns
#    SPEC_V1_1 §2.
# ---------------------------------------------------------------------------
def find_decayed_unknowns(db_path, now_ts=None, limit=_v1._DEFAULT_LIMIT):
    global last_skipped_unverified
    substrate = _layer("substrate-layer", "substrate_v3")
    le = _layer("leighton-engine-layer", "leighton_engine_v3")
    now = time.time() if now_ts is None else now_ts

    skipped = 0
    candidates = []
    for row in substrate.list_claims(db_path, verify=True):
        if not row["verified"]:
            skipped += 1
            continue
        cap = row["capsule"] or {}
        unknown_text = cap.get("UNKNOWN")
        if not isinstance(unknown_text, str) or not unknown_text:
            continue
        created = _epoch(row["created_at"])
        if created is None:
            continue
        ref = max(now, created)
        lam = le.compute_lambda([{"timestamp": created, "value": LAMBDA_ZERO}],
                                le.STACK_CLAIM_K, ref, now,
                                time_unit=le.STACK_TIME_UNIT)["lambda"]
        candidates.append({
            "claim_id": row["claim_id"],
            "subject": cap.get("subject", ""),
            "object": cap.get("object", ""),
            "unknown_text": unknown_text,
            "lambda": lam,
            "created_at": created,
            "delta_t": ref - created,
        })
    last_skipped_unverified = skipped
    candidates.sort(key=lambda c: c["lambda"])
    return candidates[:limit]


# ---------------------------------------------------------------------------
# 2. main
#    v1.0.0's flow with the v1.1 search. 0 success, 1 failure.
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
    if last_skipped_unverified:
        print(f"skipped {last_skipped_unverified} claim(s) that failed verification", file=sys.stderr)
    if not claims:
        print("No UNKNOWN claims found. Nothing to weave.")
        return 0
    try:
        briefing = call_lllm(build_prompt(claims))
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(briefing)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
