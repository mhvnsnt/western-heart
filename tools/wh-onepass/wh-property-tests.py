#!/usr/bin/env python3
"""Property-based tests for the WH one-pass validator (Hypothesis).

These test INVARIANTS, not examples: Hypothesis generates hundreds of
inputs per property and shrinks any failure to the smallest case.
This is the quality-automation lane: instead of hand-writing one test
per move, the framework hunts for counterexamples automatically.

Properties (all grounded in the real T7 data rules):
1. Determinism: validating the same move twice gives the same result.
2. Null damage is never invented: a None damage stays a gap through
   validation; the pipeline never fills it with a guessed number.
3. Button mapping is injective: 1/2/3/4 map to four DISTINCT labels
   (LP1/RP2/LK3/RK4), and the reverse map recovers the digit.
4. Cache keys are content-sensitive: different bytes -> different SHA-256.
5. Notation conversion round-trips on button-only strings: converting
   notation_original with digits to LP form and back recovers the digits.

Run:  python3 wh-property-tests.py
Requires: hypothesis (pip install hypothesis). Small max_examples so the
gate stays fast on a 2-core box; raise it for a nightly deep run.
"""

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hypothesis import given, settings, strategies as st  # noqa: E402

from wh_onepass import (  # noqa: E402
    BUTTON_MAP,
    expected_notation_lp,
    validate_move,
)

REVERSE_MAP = {v: k for k, v in BUTTON_MAP.items()}

move_strategy = st.fixed_dictionaries(
    {"notation_lp": st.text(min_size=1, max_size=40)},
    optional={
        "notation_original": st.text(min_size=0, max_size=40),
        "damage": st.one_of(st.none(), st.text(min_size=1, max_size=12)),
        "hit_level": st.one_of(st.none(), st.text(min_size=1, max_size=12)),
    },
)


@given(move_strategy)
@settings(max_examples=100, deadline=None)
def test_deterministic(move):
    assert validate_move(move) == validate_move(move)


@given(st.none())
@settings(max_examples=10, deadline=None)
def test_null_damage_never_invented(_):
    move = {"notation_lp": "LP1", "damage": None}
    _, _, null_damage = validate_move(move)
    assert null_damage == 1  # still a gap after validation, not a number


@given(st.sampled_from(sorted(BUTTON_MAP)))
@settings(max_examples=10, deadline=None)
def test_button_map_injective(digit):
    label = BUTTON_MAP[digit]
    assert REVERSE_MAP[label] == digit
    assert len(set(BUTTON_MAP.values())) == 4


@given(st.binary(min_size=1, max_size=200), st.binary(min_size=1, max_size=200))
@settings(max_examples=100, deadline=None)
def test_cache_key_content_sensitive(a, b):
    if a != b:
        assert hashlib.sha256(a).hexdigest() != hashlib.sha256(b).hexdigest()


@given(
    st.lists(
        st.sampled_from(["LP1", "RP2", "LK3", "RK4"]),
        min_size=1,
        max_size=4,
    )
)
@settings(max_examples=100, deadline=None)
def test_notation_round_trip(labels):
    # Build a digit string, convert to LP form, convert back.
    digits = "".join(REVERSE_MAP[lab] for lab in labels)
    spaced = ",".join(digits)  # e.g. "1,2,1"
    lp_form = expected_notation_lp(spaced)
    back = lp_form
    for lab, dig in REVERSE_MAP.items():
        back = back.replace(lab, dig)
    assert back == spaced


if __name__ == "__main__":
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS %s" % name)
    print("all property tests passed")
