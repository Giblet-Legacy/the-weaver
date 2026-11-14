"""
test_weaver_v1_4.py — The Weaver v1.4 (one engine line per question) test suite

Function:
    Executable expression of SPEC_V1_4.md. Written before weaver_v1_4.py
    and run red first.

Functions in this file (pytest-collected):
    1. test_seeds
    2. test_one_line_per_question
    3. test_refused_falls_through
    4. test_off_subject_and_repeats_skipped
    5. test_unavailable_once
    6. test_no_claims
    7. test_main_without_engine
    10. test_main_on_a_cp1252_console

Helpers:
    8. _claim  — a find_decayed_unknowns-shaped result
    9. Engine  — a stand-in for call_lllm, from a table of seed -> line

Tier:     Tier 1 — Consumer (The Compensator)
Spec:     SPEC_V1_4.md 1.4.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import subprocess
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import weaver_v1_4 as w  # noqa: E402

REFUSED = None  # in an Engine table: the engine refuses this seed


# 8. _claim
def _claim(subject, obj, n=1):
    return {"claim_id": str(n) * 64, "subject": subject, "object": obj, "unknown_text": f"Question {n}?",
            "lambda": 1.487, "created_at": 0, "delta_t": 1}


# 9. Engine
class Engine:
    def __init__(self, table, unavailable=False):
        self.table, self.unavailable, self.calls = table, unavailable, []

    def __call__(self, seed):
        self.calls.append(seed)
        if self.unavailable:
            raise RuntimeError("LLLM unavailable: LLLM_HOME is not set")
        line = self.table.get(seed, REFUSED)
        if line is REFUSED:
            raise RuntimeError("LLLM refused: (nothing: the model refused to continue this seed)")
        return line


# 1. test_seeds
def test_seeds():
    assert w.seeds(_claim("envelope-layer", "P1 Envelope")) == ["envelope-layer P1 Envelope", "P1 Envelope",
                                                               "envelope-layer"]
    assert w.seeds(_claim("sky", "sky")) == ["sky sky", "sky"]
    assert w.seeds(_claim("sky", "")) == ["sky"]


# 2. test_one_line_per_question
def test_one_line_per_question():
    eng = Engine({"P1 Envelope": "P1 envelope v2, P2 sign.",
                  "status": "Status: 2.0.0 frozen. New code imports envelope v2.",
                  "envelope-layer design": "Envelope-layer design contradicts envelope-layer status.",
                  "envelope-layer": "Envelope-layer and P2 at."})
    out = w.compose_briefing([_claim("envelope-layer", "P1 Envelope", 1), _claim("envelope-layer", "status", 2),
                              _claim("envelope-layer", "design", 3)], gen=eng)
    lines = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("LLLM:")]
    assert lines == ["LLLM: P1 envelope v2, P2 sign.", "LLLM: Status: 2.0.0 frozen. New code imports envelope v2.",
                     "LLLM: Envelope-layer design contradicts envelope-layer status."]
    assert out.startswith("Morning briefing: 3 open questions are fading.")
    assert "1. envelope-layer / P1 Envelope  (λ 1.487, claim 111111111111)" in out and "Question 2?" in out


# 3. test_refused_falls_through
def test_refused_falls_through():
    eng = Engine({"ledger-layer": "The ledger-layer holds every entry."})
    out = w.compose_briefing([_claim("ledger-layer", "status")], gen=eng)
    assert "LLLM: The ledger-layer holds every entry." in out
    assert eng.calls == ["ledger-layer status", "status", "ledger-layer"]


# 4. test_off_subject_and_repeats_skipped
def test_off_subject_and_repeats_skipped():
    eng = Engine({"design": "Design; new code must import record v2.",           # not about envelope
                  "envelope-layer": "Envelope-layer and P2 at."})
    out = w.compose_briefing([_claim("envelope-layer", "design", 1), _claim("envelope-layer", "other", 2)], gen=eng)
    lines = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("LLLM:")]
    assert lines == ["LLLM: Envelope-layer and P2 at."]   # the second question has no new line, so none
    assert "record v2" not in out and "Question 2?" in out


# 5. test_unavailable_once
def test_unavailable_once():
    eng = Engine({}, unavailable=True)
    out = w.compose_briefing([_claim("a-layer", "x", 1), _claim("b-layer", "y", 2)], gen=eng)
    assert eng.calls == ["a-layer x"]
    assert out.count("(LLLM unavailable: LLLM_HOME is not set)") == 1 and "LLLM:" not in out


# 6. test_no_claims
def test_no_claims():
    assert w.compose_briefing([], gen=Engine({})) == "No UNKNOWN claims found. Nothing to weave."


# 7. test_main_without_engine
def test_main_without_engine(tmp_path, monkeypatch, capsys):
    sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "substrate-layer"))
    import substrate_v3
    home = tmp_path / "forge"
    home.mkdir()
    db = str(home / "forge.db")
    substrate_v3.init_db(db)
    substrate_v3.write_claim(db, {"subject": "ledger-layer", "object": "status", "FACT": "Frozen",
                                  "UNKNOWN": "How large can it grow?", "face": "FACT", "polarity": "affirm"},
                             Ed25519PrivateKey.generate())
    monkeypatch.setenv("FORGE_HOME", str(home))
    monkeypatch.delenv("LLLM_HOME", raising=False)
    monkeypatch.delenv("LLLM_CLI", raising=False)
    assert w.main([]) == 0
    out = capsys.readouterr().out
    assert "1. ledger-layer / status" in out and "How large can it grow?" in out
    assert "(LLLM unavailable: " in out


# 10. test_main_on_a_cp1252_console
def test_main_on_a_cp1252_console(tmp_path):
    sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "substrate-layer"))
    import substrate_v3
    home = tmp_path / "forge"
    home.mkdir()
    substrate_v3.init_db(str(home / "forge.db"))
    substrate_v3.write_claim(str(home / "forge.db"), {"subject": "ledger-layer", "object": "status", "FACT": "Frozen",
                                                      "UNKNOWN": "How large?", "face": "FACT", "polarity": "affirm"},
                             Ed25519PrivateKey.generate())
    env = {k: v for k, v in os.environ.items() if k not in ("LLLM_HOME", "LLLM_CLI")}
    env.update(FORGE_HOME=str(home), PYTHONIOENCODING="cp1252")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "weaver_v1_4.py")], env=env, capture_output=True, timeout=120)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")[-400:]
    assert b"1. ledger-layer / status" in r.stdout
