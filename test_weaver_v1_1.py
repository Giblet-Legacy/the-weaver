"""
test_weaver_v1_1.py — The Weaver v1.1 (P9 v3 reader) test suite

Function:
    Executable expression of SPEC_V1_1.md. Written before
    weaver_v1_1.py and run red first. Uses a substrate written by P9
    itself, so timestamps are real ISO 8601 strings.

Functions in this file (pytest-collected):
    1. test_real_substrate_is_found
    2. test_sorted_by_decay_in_days
    3. test_only_unknown_and_limit
    4. test_tampered_claim_skipped
    5. test_read_only
    6. test_main

Fixtures and helpers:
    7. home   — FORGE_HOME with a P9 substrate of three claims
    8. _age   — set a claim's created_at to N days ago

Tier:     Tier 1 — Consumer (The Compensator)
Spec:     SPEC_V1_1.md 1.1.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sqlite3
import sys
import time
from datetime import datetime, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = os.path.dirname(os.path.abspath(__file__))
for _p in (ROOT, os.path.join(ROOT, "..", "substrate-layer")):
    if _p not in sys.path:
        sys.path.insert(0, os.path.abspath(_p))

import substrate_v3  # noqa: E402
import weaver  # noqa: E402
import weaver_v1_1  # noqa: E402

KEY = Ed25519PrivateKey.generate()


# 8. _age
def _age(db, claim_id, days):
    ts = datetime.fromtimestamp(time.time() - days * 86400, tz=timezone.utc).isoformat()
    conn = sqlite3.connect(db)
    with conn:
        conn.execute("UPDATE claims SET created_at=? WHERE claim_id=?", (ts, claim_id))
    conn.close()


# 7. home
@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_HOME", str(tmp_path))
    db = str(tmp_path / "forge.db")
    substrate_v3.init_db(db)
    old = substrate_v3.write_claim(db, {"subject": "moon", "object": "cheese",
                                        "UNKNOWN": "What if the moon is cheese?"}, KEY)
    new = substrate_v3.write_claim(db, {"subject": "tide", "object": "late",
                                        "UNKNOWN": "Why is the tide late?"}, KEY)
    substrate_v3.write_claim(db, {"subject": "sky", "object": "blue", "FACT": "The sky is blue"}, KEY)
    _age(db, old, 10)
    return db, old, new


# 1. test_real_substrate_is_found
def test_real_substrate_is_found(home):
    db, _, _ = home
    assert weaver.find_decayed_unknowns(db) == []  # the v1.0.0 defect, pinned
    assert len(weaver_v1_1.find_decayed_unknowns(db)) == 2


# 2. test_sorted_by_decay_in_days
def test_sorted_by_decay_in_days(home):
    db, old, new = home
    found = weaver_v1_1.find_decayed_unknowns(db)
    assert [c["claim_id"] for c in found] == [old, new]
    assert found[0]["lambda"] == pytest.approx(1.1839, abs=1e-3)
    assert found[1]["lambda"] == pytest.approx(1.5, abs=1e-3)
    assert found[0]["unknown_text"] == "What if the moon is cheese?"


# 3. test_only_unknown_and_limit
def test_only_unknown_and_limit(home):
    db, _, _ = home
    assert all(c["subject"] != "sky" for c in weaver_v1_1.find_decayed_unknowns(db))
    assert len(weaver_v1_1.find_decayed_unknowns(db, limit=1)) == 1


# 4. test_tampered_claim_skipped
def test_tampered_claim_skipped(home):
    db, old, new = home
    conn = sqlite3.connect(db)
    with conn:
        text = conn.execute("SELECT capsule FROM claims WHERE claim_id=?", (new,)).fetchone()[0]
        conn.execute("UPDATE claims SET capsule=? WHERE claim_id=?", (text.replace("late", "early"), new))
    conn.close()
    found = weaver_v1_1.find_decayed_unknowns(db)
    assert [c["claim_id"] for c in found] == [old]
    assert weaver_v1_1.last_skipped_unverified == 1


# 5. test_read_only
def test_read_only(home):
    db, _, _ = home
    before = open(db, "rb").read()
    weaver_v1_1.find_decayed_unknowns(db)
    assert open(db, "rb").read() == before


# 6. test_main
def test_main(home, monkeypatch, capsys):
    monkeypatch.setattr(weaver_v1_1, "call_lllm", lambda prompt: "BRIEFING " + prompt.split("\n")[6][:20])
    assert weaver_v1_1.main([]) == 0
    assert "BRIEFING" in capsys.readouterr().out
    monkeypatch.setenv("FORGE_HOME", os.path.join(os.path.dirname(home[0]), "absent"))
    assert weaver_v1_1.main([]) == 1
