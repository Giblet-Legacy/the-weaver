"""
test_weaver_v1_2.py — The Weaver v1.2 (import from any directory) test suite

Function:
    Executable expression of SPEC_V1_2.md. Written before
    weaver_v1_2.py and run red first. Each check runs in a fresh Python
    process whose working directory is outside every repository, the
    way an operator starts it.

Functions in this file (pytest-collected):
    1. test_v1_1_fails_outside_repos
    2. test_v1_2_works_outside_repos
    3. test_reexports

Helpers:
    4. _run_elsewhere — run code in a fresh process from a temp directory

Tier:     Tier 1 — Consumer (The Compensator)
Spec:     SPEC_V1_2.md 1.2.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import subprocess
import sys
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
SUBSTRATE = os.path.abspath(os.path.join(ROOT, "..", "substrate-layer"))


# 4. _run_elsewhere
def _run_elsewhere(tmp_path, code):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    return subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=str(tmp_path),
                          capture_output=True, text=True, env=env, timeout=120)


# 1. test_v1_1_fails_outside_repos
def test_v1_1_fails_outside_repos(tmp_path):
    r = _run_elsewhere(tmp_path, f"""
        import sys; sys.path.insert(0, {ROOT!r})
        import weaver_v1_1
    """)
    assert r.returncode != 0 and "No module named 'weight'" in r.stderr


# 2. test_v1_2_works_outside_repos
def test_v1_2_works_outside_repos(tmp_path):
    r = _run_elsewhere(tmp_path, f"""
        import os, sys
        sys.path.insert(0, {ROOT!r}); sys.path.insert(0, {SUBSTRATE!r})
        import weaver_v1_2, substrate_v3
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        db = os.path.join(os.getcwd(), "forge.db")
        substrate_v3.init_db(db)
        substrate_v3.write_claim(db, {{"subject": "tide", "object": "late",
                                       "UNKNOWN": "Why late?"}}, Ed25519PrivateKey.generate())
        found = weaver_v1_2.find_decayed_unknowns(db)
        print("found", len(found), round(found[0]["lambda"], 3))
    """)
    assert r.returncode == 0, r.stderr
    assert "found 1 1.5" in r.stdout


# 3. test_reexports
def test_reexports():
    sys.path.insert(0, ROOT)
    import weaver_v1_1
    import weaver_v1_2
    for name in ("find_decayed_unknowns", "build_prompt", "call_lllm", "main"):
        assert getattr(weaver_v1_2, name) is getattr(weaver_v1_1, name)
