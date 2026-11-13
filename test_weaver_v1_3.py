"""
test_weaver_v1_3.py — The Weaver v1.3 (briefing from claims, engine as an aside) test suite

Function:
    Executable expression of SPEC_V1_3.md. Written before weaver_v1_3.py
    and run red first.

Functions in this file (pytest-collected):
    1. test_engine_command
    2. test_call_lllm
    3. test_compose_briefing
    4. test_main_without_engine

Helpers:
    5. ENGINE  — a stand-in engine cli.py
    6. _claims — find_decayed_unknowns-shaped results

Tier:     Tier 1 — Consumer (The Compensator)
Spec:     SPEC_V1_3.md 1.3.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys
from unittest.mock import patch

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import weaver_v1_3 as w  # noqa: E402

# 5. ENGINE
ENGINE = '''import sys
if sys.argv[2] == "silent":
    print("(nothing: the model refused to continue this seed)")
else:
    print(sys.argv[2] + " holds every entry in order")
    print("tokens 4 in, 6 out | stats line")
'''


# 6. _claims
def _claims():
    return [{"claim_id": "a" * 64, "subject": "ledger-layer", "object": "status", "unknown_text": "How large?",
             "lambda": 1.2345, "created_at": 0, "delta_t": 1},
            {"claim_id": "b" * 64, "subject": "silent", "object": "x", "unknown_text": "Who knows?",
             "lambda": 1.5, "created_at": 0, "delta_t": 1}]


# 1. test_engine_command
def test_engine_command(tmp_path, monkeypatch):
    cli_py = tmp_path / "cli.py"
    cli_py.write_text("")
    monkeypatch.setenv("LLLM_CLI", str(cli_py))
    assert w.engine_command() == [sys.executable, str(cli_py)]
    monkeypatch.setenv("LLLM_CLI", str(tmp_path / "nope.py"))
    with pytest.raises(RuntimeError, match="LLLM_CLI"):
        w.engine_command()
    monkeypatch.delenv("LLLM_CLI")
    with patch("shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="LLLM unavailable"):
            w.engine_command()


# 2. test_call_lllm
def test_call_lllm(tmp_path, monkeypatch):
    cli_py = tmp_path / "cli.py"
    cli_py.write_text(ENGINE)
    monkeypatch.setenv("LLLM_CLI", str(cli_py))
    monkeypatch.delenv("LLLM_HOME", raising=False)
    with pytest.raises(RuntimeError, match="LLLM_HOME"):
        w.call_lllm("ledger-layer")
    monkeypatch.setenv("LLLM_HOME", str(tmp_path))
    assert w.call_lllm("ledger-layer") == "ledger-layer holds every entry in order"
    with pytest.raises(RuntimeError, match="refused"):
        w.call_lllm("silent")


# 3. test_compose_briefing
def test_compose_briefing(tmp_path, monkeypatch):
    cli_py = tmp_path / "cli.py"
    cli_py.write_text(ENGINE)
    monkeypatch.setenv("LLLM_CLI", str(cli_py))
    monkeypatch.setenv("LLLM_HOME", str(tmp_path))
    text = w.compose_briefing(_claims())
    assert text.startswith("Morning briefing: 2 open questions are fading.")
    assert "1. ledger-layer / status  (λ 1.234, claim aaaaaaaaaaaa)" in text
    assert "   How large?\n   LLLM: ledger-layer holds every entry in order" in text
    assert "2. silent / x" in text and "Who knows?" in text
    assert text.count("LLLM:") == 1 and "unavailable" not in text
    monkeypatch.delenv("LLLM_HOME")
    text = w.compose_briefing(_claims())
    assert "LLLM:" not in text and text.count("(LLLM unavailable: ") == 1
    assert w.compose_briefing([]) == "No UNKNOWN claims found. Nothing to weave."
    one = w.compose_briefing(_claims()[:1], gen=lambda seed: "a line")
    assert "1 open question is fading." in one and "LLLM: a line" in one


# 4. test_main_without_engine
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
