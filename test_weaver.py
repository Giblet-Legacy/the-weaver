"""
test_weaver.py — The Weaver test suite

Function:
    Executable expression of SPEC.md. Written before weaver.py per
    build discipline.

Tier:    Tier 1 — Consumer (The Weaver)
Spec:    SPEC.md v1.0.0
Licence: MSL-1.0
"""

import os
import sys
import json
import sqlite3
import time
import pytest
from unittest.mock import patch

# Bootstrap: add P1 and P14 so we can compute lambda in tests if needed
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "envelope-layer")))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "leighton-engine-layer")))

import weaver


@pytest.fixture
def forge_home(tmp_path, monkeypatch):
    """Isolated FORGE_HOME with a P9-schema database containing a few claims."""
    monkeypatch.setenv("FORGE_HOME", str(tmp_path))
    db_path = tmp_path / "forge.db"

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE claims (
            claim_id TEXT PRIMARY KEY,
            signer TEXT NOT NULL,
            capsule TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            superseded_by TEXT,
            created_at TEXT NOT NULL
        )
    """)

    now = time.time()

    def insert(cid, capsule, created_ts):
        conn.execute(
            "INSERT INTO claims (claim_id, signer, capsule, is_active, created_at) "
            "VALUES (?, ?, ?, 1, ?)",
            (cid, "did:key:z6Mktest", json.dumps(capsule), str(created_ts)),
        )

    # An UNKNOWN claim created 10 days ago (heavily decayed toward neutral)
    insert("claim-a", {
        "subject": "moon", "object": "cheese",
        "UNKNOWN": "What if the moon is cheese?",
    }, now - 10 * 86400)

    # An UNKNOWN claim created 1 hour ago (barely decayed)
    insert("claim-b", {
        "subject": "sky", "object": "green",
        "UNKNOWN": "What if the sky is green?",
    }, now - 3600)

    # A FACT claim — should NOT be included
    insert("claim-c", {
        "subject": "sun", "object": "star",
        "FACT": "The sun is a star.",
    }, now - 10 * 86400)

    conn.commit()
    conn.close()
    return tmp_path


def test_missing_db_fails(monkeypatch, tmp_path):
    monkeypatch.setenv("FORGE_HOME", str(tmp_path))  # no forge.db inside
    rc = weaver.main([])
    assert rc == 1


def test_missing_lllm_env_fails(forge_home, monkeypatch, capsys):
    monkeypatch.delenv("LLLM_HOME", raising=False)
    rc = weaver.main([])
    assert rc == 1
    captured = capsys.readouterr()
    assert "lllm" in captured.err.lower()


def test_find_decayed_unknowns_only_unknown(forge_home):
    db_path = str(forge_home / "forge.db")
    claims = weaver.find_decayed_unknowns(db_path)
    subjects = [c["subject"] for c in claims]
    assert "moon" in subjects
    assert "sky" in subjects
    assert "sun" not in subjects  # FACT, not UNKNOWN


def test_find_decayed_unknowns_sorted_by_decay(forge_home):
    db_path = str(forge_home / "forge.db")
    claims = weaver.find_decayed_unknowns(db_path)
    # moon created 10 days ago should be MORE decayed (closer to 1.0)
    # than sky created 1 hour ago. Sorted by lambda ascending means
    # moon (λ closer to 1.0) should come before sky (λ closer to 1.5).
    assert claims[0]["subject"] == "moon"
    assert claims[0]["lambda"] < claims[1]["lambda"]


def test_find_decayed_unknowns_limit_three(forge_home):
    db_path = str(forge_home / "forge.db")
    claims = weaver.find_decayed_unknowns(db_path, limit=1)
    assert len(claims) == 1


def test_build_prompt_contains_claim_text(forge_home):
    db_path = str(forge_home / "forge.db")
    claims = weaver.find_decayed_unknowns(db_path)
    prompt = weaver.build_prompt(claims)
    assert "moon" in prompt.lower()
    assert "cheese" in prompt.lower()
    assert "briefing" in prompt.lower() or "weave" in prompt.lower()


def test_main_with_lllm_mocked(forge_home, monkeypatch, capsys):
    monkeypatch.setenv("LLLM_HOME", str(forge_home))
    with patch("weaver.call_lllm", return_value="Mock briefing output") as mock:
        rc = weaver.main([])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Mock briefing output" in captured.out
        assert mock.called


def test_call_lllm_missing_binary(forge_home, monkeypatch):
    monkeypatch.setenv("LLLM_HOME", str(forge_home))
    with patch("subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(RuntimeError, match="not on PATH"):
            weaver.call_lllm("test prompt")
