"""
Likeness policy gates as code.

Three gates, all enforced before any GPU work happens:
  1. consent: the subject consented (own face) or the face is AI-generated
  2. adult:   the subject is an adult — ALL CHARACTERS ARE ADULTS, no exceptions
  3. no-famous-faces: third-party / celebrity faces are rejected
     (canon law: the game ships no famous names — faces follow the same rule)

Policy failures RAISE. They never warn-and-continue.
Std-lib only.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass
from typing import Dict, List

from stages import IntakeSpec, StageError


@dataclass
class LikenessRecord:
    record_id: str
    photo_path: str
    face_source: str  # "own" | "ai-generated"
    subject_is_adult: bool
    consented_at: float
    notes: str = ""


# In-memory registry. The real service persists this (append-only log);
# the contract — one record per avatar, id referenced by IntakeSpec — is stable.
_REGISTRY: Dict[str, LikenessRecord] = {}


def _record_id(photo_path: str, face_source: str) -> str:
    digest = hashlib.sha256(f"{photo_path}|{face_source}".encode()).hexdigest()[:16]
    return f"likeness-{digest}"


def check_consent(face_source: str, consent_given: bool) -> None:
    """Gate 1: own face requires explicit consent; ai-generated needs none."""
    if face_source == "own" and not consent_given:
        raise StageError("consent gate: own-face photo requires explicit consent")
    if face_source not in ("own", "ai-generated"):
        raise StageError(f"consent gate: face_source {face_source!r} not allowed")


def check_adult(subject_is_adult: bool, subject_age_years: int | None = None) -> None:
    """Gate 2: ALL CHARACTERS ARE ADULTS. No exceptions, no owner override path."""
    if subject_age_years is not None and subject_age_years < 18:
        raise StageError("adult gate: subject is a minor — pipeline stopped")
    if not subject_is_adult:
        raise StageError("adult gate: subject must be confirmed adult")


def check_no_famous_face(
    claimed_identity: str | None = None, is_public_figure: bool = False
) -> None:
    """Gate 3: no third-party / celebrity faces.

    Only the subject's own face (with consent) or an AI-generated face may
    enter the pipeline. Anything identified as someone else is rejected.
    """
    if is_public_figure:
        raise StageError("likeness gate: public-figure faces are not allowed")
    if claimed_identity:
        raise StageError(
            f"likeness gate: claimed identity {claimed_identity!r} — "
            "only own face or AI-generated faces allowed"
        )


def log_likeness_record(
    photo_path: str,
    face_source: str,
    subject_is_adult: bool,
    consent_given: bool,
    subject_age_years: int | None = None,
    claimed_identity: str | None = None,
    is_public_figure: bool = False,
    notes: str = "",
) -> LikenessRecord:
    """Run all three gates; on success, log and return the likeness record.

    Raises StageError on any gate failure. The returned record_id goes into
    IntakeSpec.consent_record_id.
    """
    check_consent(face_source, consent_given)
    check_adult(subject_is_adult, subject_age_years)
    check_no_famous_face(claimed_identity, is_public_figure)
    record = LikenessRecord(
        record_id=_record_id(photo_path, face_source),
        photo_path=photo_path,
        face_source=face_source,
        subject_is_adult=subject_is_adult,
        consented_at=time.time(),
        notes=notes,
    )
    _REGISTRY[record.record_id] = record
    return record


def get_record(record_id: str) -> LikenessRecord:
    try:
        return _REGISTRY[record_id]
    except KeyError:
        raise StageError(f"unknown likeness record {record_id!r}")


def build_intake_spec(
    photo_path: str,
    width_px: int,
    height_px: int,
    record: LikenessRecord,
) -> IntakeSpec:
    """Assemble a validated IntakeSpec from a passed likeness record."""
    spec = IntakeSpec(
        photo_path=photo_path,
        width_px=width_px,
        height_px=height_px,
        subject_is_adult=record.subject_is_adult,
        consent_record_id=record.record_id,
        face_source=record.face_source,
    )
    return spec.validate()
