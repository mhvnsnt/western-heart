# Urban Reign stages/missions decode — follow-ons (Lane 4, continued)

Date: 2026-11-08. Builds on Lane 4 (`UR-STAGE-MISSION-DECODE.md`) — nothing
here redoes Lane 4; it finishes the five follow-ons Lane 4 left open.
All claims measured; unmeasured stays UNMEASURED. No commercial game files
are copied into the game — decoded data + index in the repo; raw bytes stay
on disk (~/workspace/urban-reign-redux/decoded/inputs/).

Canon (Jay, 2026-11-08 ~00:04 — supersedes the "three Jin figures" reading):
there is NO Jin Kazama in our game at all — no Jin Kazama character, no
bloodline Jin. The ONLY Jin is the soul JIN (刃, the Blade Soul), pickable
as Phantom. The Redux Jin guest is a template donor only, never a
character. The Devil Jin kit (gym_ikdv_*) is moveset donor data only,
never a character. The revised Devil law still applies (Jay, 2026-11-07
~22:32) — "Devil" may appear only in OUR own way/language, never in the
Devil Within way. No canon name invented in the game — the UR arena
labels are PROPOSED (PPK ids), Jay names them.

## 1. Full 97-mission-PPK census — DONE (100/100)

Script: `decoded/mission_census.py` (roster-lib `ppk_entries` + `parse_vmd`
per entry; stage VMD = largest non-fighter VMD; fighter = has KUBI/KOSHI/
MUNE/KATA_L/KATA_R/HIZA_L/HIZA_R nodes; stage VMD → Editor `meshes.load` →
summary + 0.5 m-grid position set; fighter VMDs → node census only).
Outputs: `decoded/missions/census/missionNNN.{ppk,mesh,fighters,posset}.json`
(400 files; primary copy in /var/tmp/ur-census/ — home copy best-effort,
home quota flaps; see §6).

Counts: **87 DECODED, 4 NO STAGE-CANDIDATE, 9 NOT DECODED.**
Total: **8,975 PPK entries, 272 fighter VMDs** across the 100 missions.

- NO STAGE-CANDIDATE VMD (all VMDs are fighter-signature): missions
  **33, 47, 51, 64**. These missions carry no stage shell in their PPK —
  the stage is loaded another way (UNMEASURED which).
- NOT DECODED — the stage020 failure class, 3 distinct undecodable VMDs:
  - **7dd4** (sha f05ef229f351ec6d): missions **37, 50, 59, 61**.
  - **01cd** (sha e00032844bd817e5): missions **69, 77, 83, 92**.
  - **bd01** (sha c6036a2cee286370 — BYTE-IDENTICAL to stage020.ppk's
    bd01): mission **99**.
  All fail `meshes.load` / `read_mesh` with the same EOF error
  (`ValueError: not enough values to unpack (expected 2, got 0)` —
  command-walk reads past EOF, no op-0 terminator). So the undecodable
  class is NOT stage020 alone: it is 3 VMDs covering 9 missions (9% of
  the mission list). The named route for all of them is the Editor on
  Windows (Jay's machine) — see §2.

## 2. stage020 geometry — STILL BLOCKED (in-VM routes exhausted)

- The author's native `vmd_mesh.py` (Editor Source/vendor/native/native/)
  fails IDENTICALLY to roster-lib's on stage020 bd01 (2,528,444 B):
  `ValueError: not enough values to unpack (expected 4, got 0)` at
  `vmd_mesh.py:21`. `diff` proves the two copies differ ONLY in the
  influence-count assert (line 81: `<10` vs `<=32 and p1<=p0+qwc*16`).
  The other 22 stage020 entries were checked — only `bd01` is a VMD.
- `stage020.mesh.json` confirms NOT DECODED (roster-lib variant:
  expected 2, got 0). stage020's VMD has only 2 nodes, both `BUKI_1`
  (a weapon, not a stage shell).
- **New (this pass): stage020's geometry is identified.** Mission 99's
  embedded stage VMD is byte-identical to stage020's bd01 (same size
  2,528,444, same SHA256 c6036a2cee286370). Mission 99's off00 area id
  is 21 = **LAST BOSS FLOOR** (stage-name table, §3). So the ONLY
  mission on stage020's geometry is mission 99, "Closing In" vs Shinkai,
  whose place label is LAST BOSS FLOOR. That is a measured single-use
  correlation — NOT a proven 1:1 file→place identity, because §4 proves
  other stage files are shared across many place labels. stage020 is
  the arena for the LAST BOSS FLOOR mission; calling the file itself
  "the LAST BOSS FLOOR stage" is the natural reading of a single use,
  not a proven identity.
- Blocker: the geometry itself is still undecodable in-VM. Exact
  unblocker: run the Redux Editor on Windows (Jay's machine) against
  stage020.ppk / mission099.ppk and export bd01's mesh; or find a
  third reader that handles this VMD variant. stage020 is NOT registered
  in the game (the UR test asserts its absence).

## 3. Mission .bin semantics — PROVEN field map

Source: SLUS_212.09 disassembly (Capstone 5.0.7, MIPS32 LE, skipdata —
596,814 instructions, `decoded/iso/slus_text.asm`) + per-mission value
distributions, missions 1–100. Full table:
`/var/tmp/ur-census/mission_bin_fields.json`. Mission loader is module
`ao_mission.cpp` 0x271b60–0x274000; format strings `mission%03d.bin`
(vaddr 0x6C2F80), `mission%03d.ppk` (0x6B9D58), `data/mission`
(0x6C2FB0). Loader: `mission%03d.bin` formatted via jal 0x32a970
(sprintf), read via jal 0x28f480; buffer malloc 0x2800 (10,240 B)
stored at global 0x70BC6C. `.bin` files: mission000–255, all exactly
8,300 B (`decoded/inputs/mission_defs/`).

| Offset | Type | Proven meaning | Evidence |
|---|---|---|---|
| 0x00 | u16 | Per-mission area/place label (0–25) → stage-name table §3. NOT the stage-geometry selector (proven §4: the same stage VMD serves missions with different off00 values) | Setter 0x238ba8 → global 0x5E8C88; read by game-state code (0x22b6a0, branch on mode 2..6). Values 0–25. NAME UNPROVEN (inference: area/scene id). |
| 0x02 | u16 | UNPROVEN | Setter 0x238470 → global 0x59D124. Values {0, 99} only; 33 missions at 99. No correlation with FAQ partner status. |
| 0x08 | i32 ×0.001 | Player spawn X (m), −28.15..51.22 | — |
| 0x0c | i32 ×0.001 | Player spawn Z (m), −31.43..39.50 | — |
| 0x10 | i16 /32768 | Player spawn facing (fraction of full turn), −1..0.93 | — |
| 0x14 | i32 ×0.001 | Slot-1 spawn X | — |
| 0x18 | i32 ×0.001 | Slot-1 spawn Z | — |
| 0x1c | i16 /32768 | Slot-1 facing | — |
| 0x1e | i16 | UNPROVEN | Values {0,200,600,1000,1500}; loaded as $a1 in delay slot of jal 0x236200 (fighter-struct field copier, $a0=slot 1). |
| 0x20 | i16 | Slot-1 presence: −1 = no second fighter (47 missions), −2 = special/choice path (38), positive = fixed id (15: 3,15,19,20,21,30,31,40,41,42) | Does NOT correlate cleanly with the FAQ partner column — NOT proven to be the partner field (cross-tab: NONE 37@−1/8@−2/2@31; ALLOWED 24@−2/6@−1/8 positive; NAMED 6@−2/4@−1/5 positive). |
| 0x24 | u16 | UNPROVEN | → fighter struct +0x8C9A. |
| 0x28 | u16 | UNPROVEN | → sub-struct pointer in fighter +0x8CEC. |
| 0x74 / 0x76 | i16 | Condition fields, UNPROVEN | Tested with 0x20. 0x74 ∈ {0,1,3,7,8,11,21,27,28}; 0x76 always 0. |
| 0xa8 | u16 (1–5) | Count of 172-byte records at 0x1d4 (stride 0xac), copied into runtime fighter table (0x271d88) | → global 0x94D170. |
| 0xac | u16 | UNPROVEN | → fighter +0x8DF4. Values {0,13,16,62,65534}. |
| 0x15c | u16 (0–2) | Count of 28-byte records at 0x162 (u16@+0, u32@+10, stride 0x1c) | Mission 1's single record is all zeros. |
| 0x1754 / 0x1756 / 0x1758 | u16 ×3 | Activation flags | Each passed to 0x274000, which sets flag array 0xABF9A0[id]=1. 0x1754 ∈ 25 values 0–32; 0x1756 ∈ {0,2,6,8,11,13,15,22,29}; 0x1758 ∈ {0,3}. |
| 0x1d0 | u16 (1–5) | UNPROVEN (what it counts) | → global 0x94D174, clamped to ≤32. |
| 0x1884 | slot table (22×24B) | UNPROVEN — **NO reader in SLUS main.text or any DVP overlay** | All literal 0x1884 offsets searched. Likely editor/legacy data the game never reads. |
| 0x1e0–0x206c | — | No reader in the mission module (except the 0x1754 trio) | Complete $s5 access list taken. |

Correction recorded: 0x271de8 is a tail-call to getter 0x2385e0 (global
0x59D13C), NOT a table lookup — the earlier "×60 table" reading was
wrong; the table lookups at 0x61D020/0x61D038 index off that global.

### Stage-name table — PROVEN

8-byte records `{u32 id; char* name}` at file offset 0x4ea3c0 in
SLUS_212.09, ids 0–54 sequential, pointers into Table A (0x6BA360+).
Mission areas are ids 0–25 (matches off00's 0–25 range). Per-mission
place = off00 → this table.

0 CHINA TOWN · 1 RESTAURANT · 2 SCRAPPED CAR · 3 WAREHOUSE ·
4 GLENN'S HIDEOUT · 5 BAR · 6 SOUTH END · 7 SUBWAY ·
8 SHOPPING CENTER 1 · 9 SHOPPING CENTER 2 · 10 BACK ALLEY ·
11 HOMELESS · 12 MEETING SPACE · 13 CENTER CITY A · 14 SOUTH END(N) ·
15 SHOPPING CENTER(B) · 16 APARTMENT · 17 CENTER CITY B · 18 GREEN HILL ·
19 BOSS ROOF · 20 PARKING · 21 LAST BOSS FLOOR · 22 GROUND FLOOR ·
23 LAST BOSS AREA · 24 THEATER · 25 RESTAURANT(D) · 26 WAREHOUSE(VS) ·
27 TAEKWONDO(VS) · 28 VS BATTLE 4 · 29 VS BATTLE 5 · 30 VS BATTLE 6 ·
31 SCRAPPED CAR(VS) · 32 SPEECH MEETING · 33 AURORA VISION · 34 CITY HALL ·
35 KIDNAPPING · 36 ARMY · 37 STAGE1(B) · 38 STAGE2(B) · 39 STAGE3(B) ·
40 STAGE4(B) · 41 STAGE5(B) · 42 STAGE6(B) · 43 STAGE7(B) ·
44 THROW AWAY · 45 STAGE 46 · 46 STAGE 47 · 47 STAGE 48 · 48 STAGE 49 ·
49 STAGE 50 · 50 STAGE 51 · 51 STAGE 52 · 52 STAGE 53 · 53 STAGE 54 ·
54 STAGE 55.

Corrects Lane 4's inventory: BAR id 5 was missing; GLENN'S HIDEOUT /
MEETING SPACE / BOSS ROOF / LAST BOSS FLOOR are Table A's authoritative
forms vs Table B's HIDEOUT / MEETING PLACE / ROOF / LAST BOSS ROOM.
The FAQ walkthrough (`decoded/inputs/urban-reign-faq.txt`) does NOT name
places per mission (titles/opponents/objectives/strategy only);
per-mission list at `decoded/missions/mission-list-faq.txt` (100 lines).

## 4. Place-name → PPK id mapping — (filled from the link run)

Script: `mission_stage_link.py` (in /var/tmp/ur-census-script/ — home
copy pending quota). Identity test = byte-identical stage VMD SHA256
(mission's stage VMD vs the 7 stage PPK VMDs), plus the Lane 4 posset
overlap (0.5 m grid) as a cross-check. Outputs:
`mission_stage_link.json`, `place_ppk_map.json` in /var/tmp/ur-census/.

Stage PPK VMD identities (measured from the stage JSONs):
- stage003: fff0, sha 5b0ac7c7eccde4e8, 3,986,192 B
- stage004: 1eb9, sha 1fe8193c869390af, 3,119,520 B
- stage028: d863, sha 9ee5c2835a717eb8, 2,190,784 B
- stage029: 96cb, sha 40784af4020c9a18, 5,651,184 B
- stage030: 718d, sha ef1921004485dab3, 3,573,184 B
- stage031: 3f25, sha 0981f5b91e96465b, 3,898,752 B
- stage020: bd01, sha c6036a2cee286370, 2,528,444 B (undecodable)

Results (`mission_stage_link.json`, `place_ppk_map.json` in
/var/tmp/ur-census/; 25 distinct stage-VMD clusters across the 100
missions). Two independent tests agree exactly:

**Mission → stage PPK (measured, byte-identical VMD SHA256 AND 100.0%
posset overlap — both tests give the same answer for every identified
mission):**
- stage003 ← missions **30, 35, 42, 54** (places: SHOPPING CENTER(B),
  GLENN'S HIDEOUT, CENTER CITY B, BACK ALLEY)
- stage004 ← missions **9, 20, 24, 44, 48, 66, 82** (places: SHOPPING
  CENTER 2, GLENN'S HIDEOUT, CHINA TOWN, SUBWAY, SHOPPING CENTER(B),
  BACK ALLEY, APARTMENT)
- stage020 ← mission **99** (place: LAST BOSS FLOOR) — geometry
  undecodable, so no posset/overlap (0.0% by absence, not by mismatch)
- stage028 / stage029 / stage030 / stage031 ← **NO missions** (0 each)

**Place → PPK: there is NO 1:1 map — and that is the measured answer.**
The same stage geometry serves missions with many different place
labels (stage003: 4 places; stage004: 7 places), and the same place
label uses different stages (GLENN'S HIDEOUT: stage003 mission 35 AND
stage004 mission 20). So off00 is a per-mission place label, NOT a
stage selector; the geometry comes from the mission PPK's embedded
stage VMD. The correct primitive is mission→stage PPK (12 missions
identified), not place→PPK. Median posset overlap across all missions
is 10.2% — the low values just mean "not one of these 6 stages", not a
failed match; the 100.0% matches are the real signal.

**What the 6 stage PPKs are (measured use):** only stage003 and
stage004 are mission stages (11 missions between them). stage028/029/
030/031 are used by no mission 1–100 — they are most plausibly VS-mode
arenas (the stage-name table has VS entries 26–31: WAREHOUSE(VS),
TAEKWONDO(VS), VS BATTLE 4/5/6, SCRAPPED CAR(VS)), but that link is
UNMEASURED — no byte or overlap evidence ties those ids to these PPKs.
The other ~18 stage geometries in the mission set exist only inside
mission PPKs, not as standalone stage PPKs (25 clusters total, 7 of
them the Lane 4 stage PPKs).

## 5. Stage registration in the game — (filled after the PR lands)

Branch `ur-stages-missions` from main `a89b10b0`. 6 UR stage defs
(`ur-stage003` etc.), tier 'URBAN REIGN', builder `urstage`, OBJs at
`game/assets/stages/ur/stageNNN.obj` (vertices + UVs + decoded vertex
colors, metres, no scale), `hidePlatform: true` (the decoded stage
carries its own floor at y=0). Test `game/tests/ur-stages.test.mjs`.
stage020 NOT registered (undecodable). Names are PROPOSED labels
(PPK ids) — Jay names the arenas.

PR: **#1650** — https://github.com/mhvnsnt/western-heart/pull/1650
(branch `ur-stages-missions`, commits e95681e6 OBJs, 10c9440e
registration + test, 9d90c881 WORKLOG). OPEN + MERGEABLE, 8 files,
+738,212/−1. NOT merged — left open for parent verification.
Checks: node --check OK; ur-stages 8/8 green; full suite 296/245/51
(same 51 pre-existing failures as main, zero regressions).

## 6. Disk note (do NOT overstate to Jay)

Home quota is the binding limit, not device free space (`df` shows 47 GB
free, but the btrfs subvolume quota throws EDQUOT and flaps on a minutes
timescale as other agents write). Primary outputs went to /var/tmp
(2.0 GB tmpfs, no quota); home copies are best-effort. A restart during
the session wiped /tmp and /var/tmp once; scripts were recreated and are
regenerable. Nothing was deleted from Jay's dirs.
