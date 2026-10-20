# DOA4 Full Teardown — Continuation (2026-10-19 ~22:00 CDT)

**Status:** PARTIAL. Extraction 94.3% complete; fighter identification + animations
blocked (see below). Remaining items logged on TEARDOWN-IDLE-QUEUE.

## Extraction state (on main, teardown/dead-or-alive-4/)

| Archive | Tables decoded (triangulated GLBs) | Notes |
|---|---|---|
| chrone.afs | 30/30 | ✅ complete |
| chrtwo.afs | 68/68 | ✅ complete |
| chrthree.afs | 50/75 | ⚠️ tables 09–33 (25) not decoded |
| mot.afs | 11/11 | ✅ complete |
| stg.afs | 0/18 | ❌ IBUF base not discovered; stage models exist as point clouds only (doa4-bass/carved_models/stg) |
| anm.afs | 0 | ❌ animation format unknown (see ENCRYPTION-ANALYSIS.md) |

Total triangulated GLBs on main: **159**.

## Movesets (game/assets/movesets/, schema v2, MOVESET_IDS wired)

| File | Moves | Source |
|---|---|---|
| doa-bass.json | 20 | DOA5LR conversion (2026-10-19 lane) |
| doa-kasumi.json | 18 | DOA5LR conversion |
| doa-hayabusa.json | 16 | DOA5LR conversion |
| doa-ayane.json | 23 | **NEW this continuation** — DOAU guides/Reno, DOA Wiki |
| doa-tina.json | 26 | **NEW** — Jimbo DOAU guide + Prima DOA4 guide (facts) |
| doa-jannlee.json | 21 | **NEW** — Reno DOAU guide (real commands+damage) |

Full reference doc: `movesets/bass-armstrong/BASS-MOVELIST.md` (278 lines).
Conversion rules: `docs/movesets/DOA-VF-CONVERSION-2026-10-19.md`.

## Blockers (honest)

1. **Fighter identification of carved models:** GLBs are named by archive index
   (chrone_00 …) because the AFS file tables are still obfuscated (16-byte
   periodic cipher, 18 Ghidra audits, keystream not recovered —
   ENCRYPTION-ANALYSIS.md). A test render (chrone_00) shows the vertex pools are
   stored in **per-part local space**: the mesh only assembles into a character
   via the skeleton transforms in the **MdlGeo ObjGeo chunks, which are not
   parsed yet**. Visual roster ID is therefore not possible from these GLBs
   alone. Roster entries for DOA4 fighters stay unwired until MdlGeo/skeleton
   parsing lands.
2. **chrthree tables 09–33 + stg.afs decode:** needs the AFS bytes back on disk.
   ISO was cleared under ONE-STORE RULE (safe on GitHub release `doa4-iso-v1`,
   30 parts, byte-verified 2026-10-16). Re-download in progress 2026-10-19;
   note: part_01's first 16MB contain the UDF header but **no**
   `MICROSOFT*XBOX*MEDIA` magic at 0x3A0000 as previously reported — partition
   location must be re-established by scanning the completed part before the
   directory ranges for chrthree.afs/stg.afs can be Range-fetched.
3. **Animations (anm.afs/mot.afs):** format unknown; needs the same MdlGeo work
   or the Xenia dynamic path (audited NOT feasible on this VM, Audit14).
4. **Skeletons/bone weights:** in MdlGeo ObjGeo chunks, unparsed.
5. **100+ moves per fighter (FULL MOVESET LAW):** current DOA JSONs are core
   movelists (16–26 moves). Full DOA4 command lists exist per fighter (DOA Wiki)
   but expanding all 22 fighters to 100+ schema-v2 entries is a large authoring
   wave — queued on TEARDOWN-IDLE-QUEUE.

## DOA4 roster (for the remaining wiring waves)

Playable: Kasumi, Ryu Hayabusa, Kokoro, Hitomi, Brad Wong, Eliot, Bass
Armstrong, Zack, Jann Lee, Leifang, Tina Armstrong, La Mariposa, Bayman,
Christie, Ayane, Hayate. Unlockable: Ein, Gen Fu, Leon, Helena Douglas,
SPARTAN-458, Tengu. (22 fighters.)
