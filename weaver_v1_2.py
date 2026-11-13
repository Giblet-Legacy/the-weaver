"""
weaver_v1_2.py — The Weaver v1.2, importable from any working directory

Function:
    The layer above The Weaver v1.1.0 (weaver_v1_1.py), and the entry
    point to run from v1.2 on. v1.1 imports weaver.py, which imports
    P14 v1, which finds weight-layer relative to the working directory,
    so The Weaver failed to import from anywhere but a sibling repo.
    This layer puts the sibling layer directories on sys.path from its
    own location first, then re-exports v1.1 unchanged (SPEC_V1_2.md).

    weaver.py and weaver_v1_1.py are frozen and not edited.

Public API (re-exported from weaver_v1_1):
    1. find_decayed_unknowns
    2. build_prompt
    3. call_lllm
    4. main
    (last_skipped_unverified: read it from weaver_v1_1 after a call)

Tier:     Tier 1 — Consumer (The Compensator)
Depends:  weaver_v1_1.py (Weaver v1.1.0)
Spec:     SPEC_V1_2.md 1.2.0 (over SPEC_V1_1.md 1.1.0)
Version:  1.2.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _layer_dir in ("weight-layer", "trust-layer", "leighton-engine-layer", "envelope-layer"):
    _path = os.path.join(_PARENT, _layer_dir)
    if _path not in sys.path:
        sys.path.insert(0, _path)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import weaver_v1_1 as _v11  # noqa: E402

find_decayed_unknowns = _v11.find_decayed_unknowns
build_prompt = _v11.build_prompt
call_lllm = _v11.call_lllm
main = _v11.main


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
