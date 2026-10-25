"""
Prompt builder: creator-facing move description -> canonical SCRIPT prompt.

This is where WH's laws become code:
  - style hints come from the fighter's moveset source (never free-form),
  - prompts describing minors / sexual content / real-person likenesses are
    rejected (ALL CHARACTERS ARE ADULTS),
  - famous names are rejected (game ships no famous names; Tekken fighter
    names may appear in *technical* params only, never user-facing prompts),
  - every job declares duration + archetype so frame-data anchoring has a target.

CPU-only, std-lib.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from script_contract import ContractError, ScriptRequest  # noqa: F401  (re-export)


# ---------------------------------------------------------------------------
# Style hints keyed by Tekken moveset source.
# Mirrors docs/research/SCRIPT-INTEGRATION-2026-10-23.md Sec 8.
# Unmapped fighters are intentionally absent: flagged, never guessed
# (REPLACEMENT MAP law).
# ---------------------------------------------------------------------------
STYLE_HINTS: Dict[str, List[str]] = {
    "king": ["lucha-libre wrestling", "chain grappling", "powerful throws"],
    "armor-king": ["wrestling", "dark brawler", "chain throws"],
    "akuma": ["karate-based rushdown", "power strikes"],
    "shaheen": ["military close-quarters", "efficient strikes"],
    "lars": ["military", "dynamic entry strikes"],
    "zafina": ["contortionist", "evasive", "unpredictable angles"],
    "bosconovitch": ["unorthodox movement", "comic timing"],
    "yoshimitsu": ["sword-stance movement", "spinning evasion"],
    "lee-chaolan": ["elegant kickboxing", "precise straight punches"],
    "ling-xiaoyu": ["acrobatic kung fu", "evasive dance-like footwork"],
    "law": ["rapid strikes", "jeet-kune-do-inspired"],
    "paul-phoenix": ["power karate", "devastating straight punches"],
    "feng-wei": ["internal martial arts", "iron-palm strikes"],
    "craig-marduk": ["vale-tudo brawler", "heavy grappling"],
    "true-ogre": ["monstrous power strikes"],
    "lucky-chloe": ["agile dance-fighter", "acrobatic kicks"],
    "raven": ["ninjutsu", "teleport-stance movement"],
    "jun-kazama": ["defensive karate", "flowing counters"],
    "roger-jr": ["beast-mimicry boxing", "kangaroo stance"],
    "hwoarang": ["taekwondo kick chains", "fast footwork"],
    "alisa": ["android movement", "detachable-limb flow"],
}

MOVE_ARCHETYPES = ("strike", "throw", "stance", "taunt", "evasion")

# Rejection patterns: minors, sexual content, real-person likeness.
# Kept deliberately conservative; reviewed with the owner before widening.
_REJECT_PATTERNS = [
    (re.compile(r"\b(child|kid|teen|minor|baby|toddler|schoolgirl|schoolboy)\b", re.I),
     "describes a minor"),
    (re.compile(r"\b(nude|naked|sexual|sexy|erotic|lingerie|strip)\b", re.I),
     "sexual content"),
]

# Famous-name guard: a small denylist of patterns that indicate a real person
# is being named. This is a first-pass filter, not a name database.
_FAMOUS_HINT = re.compile(
    r"\b(like|as)\s+(mike\s*tyson|muhammad\s*ali|bruce\s*lee|conor|mcgregor)\b", re.I
)


@dataclass
class JobSpec:
    """Canonical generation job: prompt + constraints for the inference service."""

    prompt: str
    style_hints: List[str]
    archetype: str
    duration_s: float
    seed: int
    model: str = "script-base"
    constraints: Dict[str, object] = field(default_factory=dict)


def canon_filter(text: str) -> str:
    """Reject prompts that violate canon/safety law. Returns cleaned text."""
    for pattern, reason in _REJECT_PATTERNS:
        if pattern.search(text):
            raise ContractError(f"prompt rejected ({reason}): {text!r}")
    if _FAMOUS_HINT.search(text):
        raise ContractError(
            "prompt rejected (names a real person — game ships no famous names)"
        )
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) < 4:
        raise ContractError("prompt too short to describe a move")
    return cleaned


def build_script_prompt(
    move_desc: str,
    moveset_source: str,
    archetype: str = "strike",
    duration_s: float = 2.0,
    seed: int = 0,
    model: str = "script-base",
    upright_bias: float = 0.8,
) -> JobSpec:
    """Build the canonical SCRIPT prompt for a move description.

    moveset_source: lowercase Tekken fighter key, e.g. "king".
    Raises ContractError if the source is unmapped (flagged, never guessed)
    or the description fails the canon filter.
    """
    if moveset_source not in STYLE_HINTS:
        raise ContractError(
            f"moveset source {moveset_source!r} is unmapped — flagged per "
            "REPLACEMENT MAP law, no style hints assigned"
        )
    if archetype not in MOVE_ARCHETYPES:
        raise ContractError(f"unknown archetype {archetype!r}")
    if not (0.5 <= duration_s <= 6.0):
        raise ContractError(f"duration_s {duration_s} outside [0.5, 6.0]")

    desc = canon_filter(move_desc)
    style = STYLE_HINTS[moveset_source]
    prompt = (
        f"a martial artist performs: {desc}. "
        f"movement quality: {', '.join(style)}. "
        f"move type: {archetype}. upright stance, balanced, facing the opponent."
    )
    return JobSpec(
        prompt=prompt,
        style_hints=list(style),
        archetype=archetype,
        duration_s=duration_s,
        seed=seed,
        model=model,
        constraints={
            "max_duration_s": duration_s,
            "require_foot_contact": archetype != "taunt",
            "upright_bias": upright_bias,
            "forbidden": ["ground", "weapons"],
        },
    )


def style_hints_for(moveset_source: str) -> List[str]:
    """Public accessor used by the creation-suite wiring lane."""
    if moveset_source not in STYLE_HINTS:
        raise ContractError(f"unmapped moveset source: {moveset_source!r}")
    return list(STYLE_HINTS[moveset_source])
