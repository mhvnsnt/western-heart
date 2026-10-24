# Vixen — intake registration

**Roster id:** `vixen` · **Status:** ✅ landed (2026-10-22), staged, awaiting character assignment

## Source
- Original archive: `~/workspace/browser_downloads/sess-3045850964/browser-download-20261022T082043.274642700Z-3-Vixen_Commission.rar` (412 MB)
- sha256: `e6d2754b09f6de050e8a586d6fca3c4ed49f57fcdc4c1f36abfdc41c2be5e5a7`
- A later re-download (`…-19-Vixen_Commission.rar`) is byte-identical — extracted once.

## Staged bytes (not committed — 985 MB exceeds the blobs-API limit)
- `~/workspace/fix2/smutbase-source/vixen/Vixen (Commission).blend` (985 MB)

## What's inside (byte-inspected 2026-10-22)
- Blender 4.02 file, fully rigged GZM widget rig (Genesis-family custom rig) + body morphs.
- Clothing is **separate modeled geometry**: `Body Suit`, `Bra` ×2, `Boots`, `Glove L/R`, `Pantie`, `Pantie 3`, `Stocking` ×2, `Choker`, `BDSM harness`, `Belt`, `Necklace` — separate objects from the body (`Vixen Mesh`).
- 88 objects total.

## 🚩 MOVESET REBUILD REQUIRED
Per the saved directive, Vixen needs a **full moveset built with TEKKEN inputs** —
**do NOT reuse her source game's (Injustice 2) input system.** Her rig, morphs,
and animations are Blender-side assets only; the fighting moveset must be
authored fresh in Tekken notation (`game/assets/movesets/vixen.json` pattern)
and registered in `game/js/movesets.js`. No moveset JSON exists for her yet.

## Next
- Moveset lane: author the Tekken-notation moveset (flag above).
- Character assignment: fighter slot or customization-donor designation (see `docs/SMUTBASE-INTAKE-QUEUE.md`).
