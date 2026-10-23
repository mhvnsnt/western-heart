# Bruno — Miguel (Tekken) Moveset Takeover Spec

**Worker 74 — 2026-10-22.** Bruno replaces Miguel. This doc records the moveset-source
claim, the Attire 1 archive, and wiring status. Canon below is grounded in CANON.md only —
no invented backstory.

**Location key:** paths are repo-relative to `mhvnsnt/western-heart` unless marked otherwise.

---

## 1. Moveset-source claim (moveset source law)

- **Bruno takes ALL of Miguel's moves, stance, and animations** — full takeover, per user
  directive 2026-10-22.
- Miguel was NOT on the taken list (Taken: King, Armor King, Akuma, Shaheen, Lars, Zafina,
  Bosconovitch, Yoshimitsu, Lee Chaolan, Ling Xiaoyu, Eddy/Christie, Feng Wei).
- Claim recorded: **Miguel (Bruno)** added to the Taken list in `docs/owner-directives.md`
  ("## Moveset source law") on 2026-10-22. Miguel is now claimed — no other WH character
  may pull from him.
- Technical claim only: Miguel's identity never appears in canon prose. Moveset sources
  are bones; canon gives them souls (same rule as every other claim).

## 2. Canon (from CANON.md — nothing invented)

- Bruno is one of the twelve: a **mortal lost soul** — "not of the nine, lost the ordinary
  way" (CANON.md §5, "On the twelve"; grouped with Michiko and Purple Rain).
- No further canon entries exist for Bruno as of 2026-10-22. Any bio/writing for Bruno
  must be built from this entry plus CANON.md's cosmology — no invented locations,
  systems, or backstory elements. No AI slop.

## 3. Attire 1 — Tripo archive (NEW, priority)

- **Source:** user-provided Tripo3D pull, project "jack sparrow 3d model",
  <https://studio.tripo3d.ai/3d-model/b3f9dfb0-2027-4520-aa1f-930fbc6c0c81>
  (Tripo project owner: `jaywillf69`).
- **Archive:** `roster/bruno/attires/attire1/source/bruno-a1-jack-sparrow.glb`
  (24,432,052 bytes, sha256 `5f1fb5a7…e9906da41`) + `manifest.json` — dorowani #603 pattern.
- **Validation at archive time:** glTF 2.0 (gltfpack 1.2), declared length matches file
  size, JSON chunk parses — 1 mesh, 1 node, 3 images, no skins (unrigged static).
- **Immutable original:** annotated tag `bruno-a1-original` — "Restore point: these bytes
  never change."
- **Status:** archive-only. Unrigged static. NOT wired into MODEL_URLs. Per the
  AUTO-ARCHIVE standing directive.
- **Priority:** this A1 is the priority model for the rig pipeline — it supersedes the
  older in-game model for all new rigging work.

## 3b. Attire 2 — Tripo archive (NEW, "Sail the Sea")

- **Source:** user-provided Tripo3D pull, project "dreadlocked warrior 3d model",
  <https://studio.tripo3d.ai/3d-model/73bce9d1-d373-4855-af02-862c5f341de7>
  (Tripo project owner: `eqqq57218`), pulled 2026-10-22 ~20:33 CDT.
- **Archive:** `roster/bruno/attires/attire2/source/bruno-a2-dreadlocked-warrior.glb`
  (23,980,788 bytes, sha256 `ffff9706…eacf44`) + `manifest.json` — dorowani #603 pattern.
- **Validation at archive time:** glTF 2.0 (gltfpack 1.2), declared length matches file
  size, JSON chunk parses — 1 mesh, 1 node, 3 images, no skins (unrigged static).
- **Immutable original:** annotated tag `bruno-a2-original` — "Restore point: these bytes
  never change."
- **Status:** archive-only. Unrigged static. NOT wired into MODEL_URLs. Per the
  AUTO-ARCHIVE standing directive.

## 4. Older in-game model — missing face texture (do NOT confuse with A1/A2)

- The pre-existing Bruno model (`game/assets/models/bruno.glb`, landed during the fix2
  round; working copy also at `~/workspace/fix2/western-heart/game/assets/models/bruno.glb`)
  has a MISSING FACE TEXTURE.
- It needs the texture fix from the T-pose render batch task. Do not delete it; do not
  confuse it with the new A1 archive.
- Per the user-definitive NEED-MODELS list (2026-10-22), Bruno needs a model — the A1
  archive above is the path forward; the old file stays as-is until the texture fix lands.

## 5. Display order / ladder

- Display order law: Tripo models FIRST; Tekken reskins ladder behind as back-slot
  attires. Bruno's Attire 1 = the Tripo archive. The older Miguel-era
  `game/assets/models/bruno.glb` ladders behind once fixed/rigged.
  (Pantera is the sole Tripo-first exception; Bruno is not one.)

## 6. Open work (not this PR)

- Rig the A1 archive to Bruno's rig (full skinning pipeline per standing orders).
- Texture fix for the older `game/assets/models/bruno.glb` (T-pose render batch lane).
- Verify `game/assets/movesets/bruno.json` reflects Miguel's actual move data
  (moveset takeover = moves + stance + animations), not a stub.
