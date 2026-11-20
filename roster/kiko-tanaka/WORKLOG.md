# WORKLOG — Kiko Tanaka = Rave record merge (2026-10-19)

## Owner order (verbatim)

- "Kiko is rave in this game and Kiko in others, Rave is his Raver personality from our canon"
- "Merge in and remem6kiko the ghost tanaka is Rave" (his words; "Merge in and remember, Kiko, the ghost tanaka is Rave")

## Meaning

KIKO TANAKA and RAVE are the SAME character in Western Heart. In other contexts he is "Kiko"; in this game he is RAVE. Rave is his "Raver" personality from canon. The unrobed/shrouded-face variant ("ghost Tanaka") is Rave. The robe pair (`game/assets/models/kiko-tanaka.glb` robed, `kiko-tanaka_alt1.glb` unrobed) are RAVE's models.

## Changes (records only — no model files touched, nothing deleted)

1. `roster/TRIPO-REGISTRY.md`
   - "Resolved names" table: added Kiko Tanaka → RAVE row.
   - Per-character table: merged the KIKO TANAKA row and the RAVE row into one RAVE row — A1 = Tripo hooded/robed (default), A2 = Tripo unrobed ("ghost Tanaka" = Raver personality), A3+ = `game/assets/models/rave.glb` (Lei Wulong in-game base) ladders back.
   - History: 2026-10-19 merge entry.
2. `roster/kiko-tanaka/ATTIRE-SLOTS.md` — rewritten as RAVE's slot map (A1 hooded Tripo, A2 unrobed "ghost Tanaka" Raver personality, A3 `rave.glb` in-game base). File paths unchanged; the roster dir is kept (no deletions).
3. `CANON.md` — additions-only note appended to the "KIKO TANAKA — The Painted Soul" section recording the Western Heart name RAVE + the Raver personality, in the owner's words. No canon text altered or removed.
4. `roster/ROSTER-GAPS-2026-10-19.md` — Q1 row 14 updated (Tripo attached, slot map), Q2 row 1 updated (name ✅, bio ✅ as The Painted Soul + Raver personality), "Tripo-attached and done" list corrected, plus a dated CORRECTION block superseding the audit's false separation.

## Final slot map for RAVE

| Slot | Display name | Model |
|------|--------------|-------|
| 1 | Rave — Hooded (Tripo) | `game/assets/models/kiko-tanaka.glb` (DEFAULT) |
| 2 | Rave — Unrobed / "ghost Tanaka" (Tripo) | `game/assets/models/kiko-tanaka_alt1.glb` (Raver personality) |
| 3 | Rave — In-game base | `game/assets/models/rave.glb` (Lei Wulong base, ladders back) |

## Verification

- All four edited files re-read after edit; anchors asserted before every replacement (script failed closed on mismatch).
- Zero deletions: diff vs main is additions/corrections only.
- `game/js/assets.js` MODEL_URLS keys (`rave`, `kiko-tanaka`, `kiko-tanaka_alt1`) left untouched — live-game wiring, not records.
- Owner's words recorded verbatim; nothing invented.
