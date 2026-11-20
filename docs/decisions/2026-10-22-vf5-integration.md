# Decision Log — 2026-10-22 — VF5 Full Integration (Worker 45)

## mon/msk identified as Eileen / El Blaze

**Decision:** `mon` = Eileen (Monkey Kung Fu), `msk` = El Blaze (Lucha Libre).

**Basis:** Release READMEs on `vf5-ps3-v1` (`mon` = monkey, `msk` = mask); render-verified msk as masked luchador athletic male build.

**Consequence:** The follow-up note "El Blaze has NO farc — he's DLC" was incorrect. Pablo → El Blaze is NOT blocked; `msk.farc`/`mskitm.farc` provide model + movelist source. Wired as one of the four locked mappings.

## El Blaze farc exists — Pablo mapping unblocked

**Decision:** Wire Pablo → El Blaze (msk) immediately; do not treat as blocked.

**Basis:** mskitm000 renders as complete T-pose luchador; GameFAQs VF5 El Blaze movelist converted to `vf-elblaze.json` (28 moves).

## Motion data deferred — not in release

**Decision:** Document as gap; do not block Phase 1/2 on it.

**Basis:** All 162 `*itm.farc` entries are obj/tex pairs only. Binary motion likely in 3.7GB `vf5-500m` ROM archive (not pulled). Moveset JSONs carry `anim_ref` hooks for the retarget pipeline when motion lands.

## Stages deferred to arena pipeline

**Decision:** List 38 `stg*.farc` files; defer extraction/visual-ID to the arena pipeline's stage-arena-pull tooling.

**Basis:** Stage→WH arena mapping requires seeing the geometry; the arena pipeline owns that ingestion. Research doc records the file list.

## Renders via expiring links, not committed

**Decision:** 18 T-pose PNGs upload to remote storage as they complete; parent relays URLs to user. Not committed to repo.

**Basis:** Keeps PR lean; renders are review-only (no canon until user says so). Dural's render flagged as Zen's approved base-mix layer.

## API-based branch+commit (no clone)

**Decision:** Used Git Database API for branch/PR/commit; merged via `git_merge.py`.

**Basis:** Repo is 7.1GB; clone impractical. API produces real branch+PR+merge commit. Additions only — no modifications, no deletions.
