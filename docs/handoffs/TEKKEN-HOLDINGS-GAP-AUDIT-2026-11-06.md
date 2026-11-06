# TEKKEN HOLDINGS GAP AUDIT — 2026-11-06

**Purpose (owner order 2026-11-06):** name EVERYTHING we are missing, 100% to 100%,
per game, so the owner knows exactly where we stand before filling gaps.
Research-only audit. Every claim below was verified against the live repos
(`mhvnsnt/western-heart` main via GitHub API tree/contents, `mhvnsnt/game-reverse-engineering`
main, both repos' releases) and the agent-ops checkpoints on 2026-11-06.
Local clones were NOT trusted (they are stale).

**Status key:**
- **HELD + WIRED** — in a store AND assembled into the playable game / catalogs.
- **HELD** — byte-stored on GitHub (repo tree or release), not wired.
- **PARTIAL** — some layers decoded, named layers missing.
- **MISSING** — not held in any usable form.

**Stale-record warning (read first):** `game-reverse-engineering/TEARDOWN-STATUS.md`
percentages (T5 ~20%, T6 ~40%, T7 ~40%, TTT2 ~15%) are 2026-10-19/20 snapshots and are
superseded by this audit. The agent-ops checkpoint `tekken5-teardown.json` says
`status: done` but its own progress field reads "Devil Within data 5%, archive mapping
~40%" — that "done" is the coordinator phase only (2026-10-20/21); the finisher never
completed. `checkpoints/ttt2-resume-100.json` is a **0-byte file** (dead since
2026-11-02); the TTT2 resume lane's brief was never restored.

---

## 1. TEKKEN 3 (PS1)

Evidence: WH `teardown/tekken3/` = 19,812 files on main; GRE `tekken3/`;
checkpoints `tekken3-teardown-complete.json` (done 2026-10-13, WH PR #30) and
`tekken3-reverse-engineer.json` (done 2026-10-12).

| Category | State | Evidence |
|---|---|---|
| Movesets | **HELD + WIRED** | 22 files (21 characters + common, JSON+CSV) in WH `teardown/tekken3/movesets/`; these banks drive the game. GRE holds the deep set for 7 fighters (bryan, gunjack, heihachi, jin, king, xiaoyu, yoshimitsu). Program count: 3,247 moves. |
| Anim banks | **HELD + WIRED** | `game/assets/anim/t3/` = 850 files across 29 character dirs (incl. `ogre`, 211 clips; `raven`, `luckychloe` generic banks); raw `divmot00–20 + divmot99` bins in `teardown/tekken3/animations/`. Every T3 bank character is held or consumed by a WH fighter. |
| Models / textures | **HELD** | 67 models mapped (GRE `model-inventory`), 8,556 textures inventoried; WH `teardown/tekken3/tim-output/` = 17,117 files, `models/` = 54. |
| Stages | **HELD (extracted), NOT WIRED** | 15 stage dirs (`a,b,c,d,e,f,g,i,j,k,l,m,n,t,u`), each `stage.json` + panorama OBJ, in `teardown/tekken3/stages/`. No T3 stage geometry exists under `game/` — see §7. |
| Frame data | **PARTIAL / N-A** | No standalone T3 frame-table set (T7-style tables exist only for T7; `game/data/` has no t3 frame dir). Move rows inside the movesets carry the data. |
| Customization | **N/A** | Tekken 3 has no customization system in the original game. Nothing to hold. |
| Code RE | **PARTIAL** | BNS parsed (303 records); Ghidra deep-dive was deferred in the 2026-10-12 checkpoint and never resumed. |

**Missing from T3: essentially nothing asset-side.** The only open threads are the
deferred Ghidra pass and wiring the extracted stages.

---

## 2. TEKKEN 5 (PS2) + DEVIL WITHIN — owner's top-priority teardown

> **CORRECTION 2026-11-06 (Fill 1 lane): TK5DATA0.BIN IS CRACKED AND FULLY
> EXTRACTED — and it contains none of the items this section attributed to it.**
> DATA0 = 112,445 records x 18,432 B; each of its 44 files is encrypted with a
> 2048-byte LCG keystream tile (w' = 5w + 3 mod 2^32) seeded by its file index
> (1..44). All 44 payloads are MPEG-2 FMV streams (intros, endings, cutscene
> movies — 1,948,071,008 B, ffprobe-verified, frames visually checked). Stored
> on GRE release `tekken5-data0-cracked-20261106` (per-file sha256 in its
> MANIFEST-data0.md; format in DATA0-FORMAT.md). **Versus models, T5-native
> movesets/animations, stage geometry, audio banks, the skull mask,
> pack->character attribution and all Devil Within gameplay data are NOT in
> DATA0** — the standing candidate is TK5DATA1.BIN's 1,571 split files
> (held, checksum-verified, contents never inventoried). The stale DATA0
> claims below are corrected in place.

Evidence: GRE `tekken5/TEARDOWN-STATUS.md` (Lane E update 2026-10-20),
`TEARDOWN-DEVIL-WITHIN.md`, `TEARDOWN-DEVIL-WITHIN-DEEP.md`, `TK5-E5-E6-DATA.md`;
WH checkpoints `gap-closure-w7b/w7d/w7e` (PRs #459/#521/#485); WH `teardown/tekken5/`.

### 2.1 What we HOLD

| Item | State | Evidence |
|---|---|---|
| ISO | **HELD, byte-perfect** | GRE release `tekken5-iso-v1`: 10 assets, 4,483,548,101 B stored; ISO = 4,483,547,136 B, **MD5 `8c20e626260890d5562e9e6f628d658f`**, SHA256 `7831994299…`. (WH release `tekken5-ps2-v1` exists but carries **0 assets** — pointer only.) |
| Full disc extraction | **HELD (raw)** | GRE release `tekken5-disc-v1`: 14 assets, 4,039,180,062 B — TK5DATA0/1/2/3 raw + DATA0 head. |
| DATA0 payloads | **HELD, CRACKED + EXTRACTED (2026-11-06)** | 44 MPEG-2 FMVs, 1,948,071,008 B payload, GRE release `tekken5-data0-cracked-20261106` (sha256 manifest + format doc). |
| DATA1 split | **HELD** | 1,571 files split via the recovered file table; 1,355 checksum-verified, 216 empty/sentinel (W7b). |
| Overlays E0–E4 (DATA3≡DATA5) | **HELD, decoded** | LZSS cracked; deobfuscated ELFs byte-identical between DATA3/DATA5. |
| E5/E6 (roster module) | **HELD, decoded** | LZSS solved; 33-fighter roster + name tables extracted — GRE `tekken5/data/roster.json` (35,854 B), `name_tables.json` (97,621 B). |
| Customization (costume packs) | **HELD + WIRED (catalog)** | 80 packs checksum-verified → **79 textured GLBs + 1 geometry-only** (pack1109, placeholder TIM2) on WH release `tekken5-costume-glbs-v1` (81 assets, 55.4 MB, pull-back sha-verified); `customization/parts/tekken5/CATALOG.json` = 80 parts on WH main. |
| ctype-5 models | **HELD, decoded** | 16 VIF-0x82 models proven (238/238 blobs), 8 GLBs on release `tekken5-ctype5-glbs-v1`. Verdict: environment/effect pieces, **NOT** customization items. |
| Videos / UI (E7 archive) | **PARTIAL** | E7 format cracked: 17 `charipu` character IPUs + NAMCO/KAZ_OP IPUs + mask/flash/sedat extracted (release `tekken5-tk5data5-v1`, plus WH draft release `tekken5-ps2-extract-v1`). Full UI extraction not finished (`teardown/tekken5/ui/UI-EXTRACTION-STATUS.md`). |

### 2.2 What we are MISSING (the hard core)

- **TK5DATA0.BIN (2,072,586,240 B) — CRACKED 2026-11-06** (see the correction
  banner above). It is an FMV archive only: 44 MPEG-2 movies, all extracted.
  The earlier "layer-1 = LCG seed-1 + unidentified second layer" model was
  wrong; the true scheme is a per-file LCG keystream tile, seed = file index.
- **Versus character models 0% decoded, T5-native animations 0%, T5-native
  movesets 0%, versus stage geometry 0% — and none of them are in DATA0.**
  Next hunt: the contents of DATA1's 1,571 split files (held, never
  inventoried). WH `teardown/tekken5/STAGES.md`
  is a 15–16 stage list documented from public data; its "Disc verification" section
  is empty — no stage file has ever been mapped from the disc.
- **Audio:** TK5DATA2 (romD, 244,426,640 B) head mapped only (first bank + name
  clusters). Per-bank extraction never ran.
- **Skull mask item: NOT FOUND in DATA1** (named gap since W7b).
- **Pack→character attribution: 0/80 proven** — all 80 costume packs sit in the
  catalog with `null` attribution; no data-proven table exists yet.
- **Cutscenes/story beyond E7:** RESOLVED 2026-11-06 — the complete DATA0 FMV
  set (44 movies: intros, endings, story/Devil Within cutscene movies) is
  extracted and stored (release above). The E7 IPU slice remains a separate,
  partial extraction of a different (IPU) copy.

### 2.3 DEVIL WITHIN — line-item breakdown (becomes "Heart and Mind Within")

| Item | State | Evidence |
|---|---|---|
| Design spec | **HELD** | GRE `tekken5/TEARDOWN-DEVIL-WITHIN.md`: 5 stages, bosses, exact controls, enemy AI patterns, gem economy, S-rank conditions, unlocks + WH adaptation spec. Stage-flow diagram verified. |
| Mode code identified | **HELD** | Module = overlay **E4** of TK5DATA5; deep-dive in `TEARDOWN-DEVIL-WITHIN-DEEP.md` (7,212-function inventory). Per-function decompiled C **not** produced (R5900 sleigh limit). |
| Mode structure tables | **HELD, extracted** | GRE `tekken5/devil-within/`: `romdata_manifest.tsv` (325 files the mode loads), `area_tables.json` — **5 stages / 37 areas / 30 slots / 41 chamber links**, `stage_demo_table.json`. |
| Enemy + boss data | **HELD (parameter tables)** | `char_tables.json` (38,905 B) + **60 per-character JSONs** in `tekken5/devil-within/characters/` (`chr_jin`, `chr_devil`, `chr_boss1/2/3/5`, `chr_mon_power1–4 lv1–4`, `chr_mon_speed…`) — the OBJ+CHR tables the binary defines. |
| DW animations | **PARTIAL — names only** | File names located in TK5DATA2 (`gym_dw_nog00.dat`, `gym_dw_rari*.dat`, `gym_djin_newhane00–03.dat`, `dwfkao00/dwhadoh00/dwup00.dat`) per WH `teardown/tekken5/DEVIL-WITHIN-DATA.md` (2026-10-23). The `.dat` payloads were never extracted (romD bank extraction, above). |
| DW stage geometry / placements / scripts | **MISSING — NOT in DATA0** | Was assumed to live in TK5DATA0 packs; DATA0 is cracked and holds only FMVs (2026-11-06). Remaining candidate: DATA1's 1,571 split files. WH status line (2026-10-23): stage geometry, boss AI, mechanics "mapped for the RE bench, not yet extracted." |
| Boss AI behaviour | **PARTIAL** | Parameter tables held (above); behaviour code not decompiled per-function. |
| Gimmick / item numeric tables | **MISSING — NOT in DATA0** | `gim.db`, `item.txt`, `gimmick_*.txt` named in DEEP §7 as inside the archive packs; not in DATA0 (cracked, FMV-only). DATA1 split files are the remaining candidate. |
| Jin's DW brawler moveset / Devil Gene meter data | **MISSING as data** | Known from the design spec only; NOT in DATA0 (cracked, FMV-only) — DATA1 split files are the remaining candidate. |
| DW UI / menus | **MISSING** | No DW UI extraction. |

**Honest T5 total:** acquisition 100%, disc split ~90%, customization slice 100%,
Devil Within *tables* ~70%, Devil Within *geometry/assets* 0%, versus-game core
(models/moves/stages/audio) 0%. The TK5DATA0 lock is OPEN (2026-11-06) and held
none of it — it is the FMV archive. The remaining T5 hunt is the content
inventory of DATA1's 1,571 split files.

---

## 3. TEKKEN 6 (PSP; PS3 noted separately)

Evidence: WH `teardown/tekken6/TEKKEN6-FINAL-STATE.md` (rounds 13–15, PRs
#446/#558/#705); `teardown/tekken6/` = 3,920 files on main; checkpoint
`wh-tekken6-100.json` (blocker RESOLVED 2026-10-25).

| Category | State | Evidence |
|---|---|---|
| ISO | **HELD** | Release `tekken6-psp-v1`, ISO sha256 `b5e52660a52cae…` (816 MB) — the reproducibility chain's root; every input regenerable from the release alone. |
| Containers | **HELD, 100%** | DATA401: **76/76** top-level files decrypted, adler-exact; cipher chain in-tree (`tools/bulk_decrypt.py`, `decode_all76.py`, `sector_cipher.py`). |
| Meshes | **HELD** | NDPP **3,444/3,444** slice sections → GLBs; 24 character slot GLBs (12 packages × slots 0+10); r11 skeleton set (supersedes r9/r10). |
| Movesets | **HELD, 100% notation** | 18 COM files byte-exact → 55 JSONs (18 characters × v1/v2/v3) in `teardown/tekken6/movesets/`; **6,814 notation-carrying moves, 6,814 fully decoded, 0 partial** (round 15). Characters: armor-king, asuka, baek, dragunov, eddy, heihachi, jin, king, kuma, law, lee, xiaoyu, marduk, nina, raven, roger, wang, zafina. |
| Endings | **HELD** | Release `tekken6-endings-v1` (46 files, byte-verified). |
| Animations | **PARTIAL** | COM tail-zone MOTA placement proven (108/108 cross-validated) but T6 PSP clips were **never converted to playable banks** — there is no `game/assets/anim/t6/` in WH. WH fighters use T3/T7/TTT2 banks. |
| Wiring into WH | **PARTIAL** | The 18 T6 movesets sit in `teardown/`; they reach fighters only where a WH moveset file was individually built from them (Wang/Raven/Roger T6 sources exist; the Byou→Wang build was ordered 2026-11-06 and is a separate lane). The bulk is held-not-wired. |
| Textures (pixels) + skinning weights | **MISSING — capture-class** | NTPP pixels/CLUT and palette→bone selection are **statically impossible** (proven terminal negative, rounds 11–13). Unlock = ONE PPSSPP GE capture session (`PPSSPP-LIVE-RUN-GUIDE.md`). The session has never been run. GLBs therefore lack true texture pixels and game-true skinning. |
| Stages | **MISSING — by source design** | Verdict closed round 13: stage packages carry **no NDPP geometry** (placement + texture containers only). Sole decodable piece: one 2×2 ground-plane quad (`teardown/tekken6/stages/slice/`). PSP T6 stages cannot be filled from the PSP version. |
| COM tail payloads (slots 25/26/30) | **PARTIAL** | Layouts proven round 15; field semantics unproven. |
| PS3 version | **PARTIAL / UNVERIFIED** | WH release `tekken6-ps3-full-v1` exists but is a **Draft**; no PS3 teardown is wired anywhere. **Scenario Campaign (the console beat-'em-up mode) is not held at all.** |

---

## 4. TEKKEN TAG TOURNAMENT 2 (Xbox 360)

Evidence: WH `teardown/tekken-tag-tournament-2/` (64 files); checkpoints
`ttt2-full-teardown.json` (**needs_owner**, 2026-10-14), `ttt2-motion-20261103.json`
(done 2026-11-04), `teardown-sweep-ttt2.json` (blocked 2026-10-20);
WH PRs #1556/#1557/#1558/#1561/#1581; `docs/handoffs/TTT2-BANKS-2026-11-04.md`.

| Category | State | Evidence |
|---|---|---|
| Source archive | **HELD** | Full game 7z = 13,363,624,393 B as 26 chunks on WH release `ttt2-7z-v1`; work archives `ttt2-work-archive-2026-10-30` (WH) / `ttt2-work-archive-20261023` (GRE). |
| Container decode | **PARTIAL** | `data004.bin` reassembled **byte-exact** (6,522,032 B, sha256 `18b18d0ff235…`); MOTA table layer parsed (21 tables); per-clip decode cracked for types 0xC8 + 0x64. DATA001–DATA028 mapped (`DATA001-DATA028-DECODE-20261030.md`, section tables in-tree). |
| Banks built | **HELD + WIRED (2 fighters)** | Roger Jr: 15 clips; Jun: 12 actions. Rows landed: Roger 323 rows + Jun 114 rows (`rows.pack.json` + `hit_frames.json`, WH #1581). **Row 48 withheld in both** (owner ruling pending). |
| Every other character's bank | **MISSING (unbuilt)** | The 1,875-entry main MOTA table is decoded as a container; only the Roger/Jun joins were ever built. The other ~57 fighters' motion was never joined or converted. |
| True Ogre (TTT2) | **MISSING — file does not exist** | No TTT2 True Ogre moveset file exists in the data (`ogr` = Ancient Ogre only). Not a decode failure; the content was never in TTT2 in that form. Chatur's fallback is the held T3 ogre bank. |
| Movesets beyond Roger/Jun | **MISSING** | 59-fighter roster is documented (`ROSTER.md`) only; no other TTT2 moveset tables extracted. |
| Stages | **MISSING** | `STAGES.md` states it plainly: "documented from public game data — **NOT extracted from the archive**." All 29 stage geometries sit inside the un-extracted STFS chunks. Zero held. |
| Full STFS extraction | **NEVER RAN** | Disk-gated in Oct 2026, never resumed: `ttt2-full-teardown` = needs_owner; the resume checkpoint is 0 bytes. The selective/surgical path (data004) is what produced everything above. |
| Customization / Fight Lab | **PARTIAL (research only)** | `teardown/ttt2-customization-research.md`; no items extracted. |

---

## 5. TEKKEN 7 (Steam, depot 389731)

Evidence: GRE releases `t7-depot389731-wave0…wave5-20261031` + `t7-shipping-exe-20261031`;
checkpoints `steam-full-pull-20261031.json`, `steam-realcode-t7t8-20261030.json`,
`steam-pakchunk1p-filelist-20261030.json`; WH tree census 2026-11-06.

| Category | State | Evidence |
|---|---|---|
| Full game source | **HELD, 100%** | Depot 389731: 577 files, **86,942,923,011 B**. Stored: wave0 18,247,613,804 B (pakchunk1_P) + wave1 20,108,014,670 + wave2 15,859,867,240 + wave3 12,852,978,091 + wave4 12,972,980,785 + wave5 6,843,298,626 = **86,884,753,216 B**, plus the exe separately (58,439,680 B, sha256 `7f2b6872…`, pull-back verified). Depot 389732 (promo): **not available from this account** (verified 2026-11-01). |
| Frame data | **HELD + WIRED** | `game/data/t7-frame-data/` = **44 character tables** on WH main. |
| Motion format | **CRACKED** | rotsm/MOTA spec + parser (GRE PR #74); clips on GRE release `t7-rotsm-clips-v1` (59,211,723 B). Format-200 bodies fully decoded; **format-100 bodies sliced/indexed only — quantised encoding unsolved (gap F11)**. |
| Move→anim join | **PARTIAL** | 781 audited unmapped refs → **481 mapped** (450 with byte-exact clip locators), **31 mapped but their clip file sits in un-located bank-0x0000 (F2)**, **300 unmapped** (81 strong T8-only candidates, 91 ambiguous pools, 39 requirement-gated). WH clip-maps exist for **8 fighters** (`game/assets/anim/t7/clip-maps/`). Program gap **F1** = the unmapped remainder; **F5 = 453 WH moves with no anim at all**. |
| Bank-0x0000 (F2) | **PARTIAL — fillable from held data** | `pakchunk1-WindowsNoEditor_P.pak` (18,247,606,148 B in manifest) **is** stored (wave0). The hunt doc's §9 sits on GRE PR #80 — still OPEN, guard-gated, **not on GRE main**. |
| 14 frame-table-only characters | **MISSING (moveset + bank unbuilt)** | Claudio, Devil Jin, Eliza, Fahkumram, Feng Wei, Geese Howard, Gigas, Kazumi, Kazuya, Kunimitsu, Leo, Leroy, Lidia, Noctis — frame table held, no moveset file, no anim bank (none appears in `game/assets/anim/t7/`, 22 dirs). Extra note: Geese + Noctis DLC files are per-file encrypted in the depot (community-documented), so those two need an added decrypt step. |
| Pak extraction | **PARTIAL** | GRE `teardown/tekken7-steam/`: `pakchunk0/` + `pakchunk0_P/` (manifest + models + textures subsets), `pakchunk1/decrypted/`, `tkdata/` (dictionary/list/mothead). WH `teardown/tekken7/` = 247 files (tekkenmods docs 116, King focus 97, models 17). Community models for 6 fighters in GRE `tekken7/models/`. The full pak set has never been unpacked end-to-end. |
| Customization items | **HELD (data), NOT WIRED** | GRE `tekken7/customization/`: `items.json` 4,027,346 B + `CATALOG.json` 107,640 B + chara_list/color_rules/palette/presets. WH `customization/parts/tekken7/` = only 12 files converted. WH release `w6-tekken7-parts-20261021` holds the skull-mask source uassets. |
| Older WH archive | **SUPERSEDED** | WH release `tekken7-full-v1` (8 assets, 3,291,403,115 B, 2026-10-16) is an earlier partial archive — **not** the Steam depot. Do not confuse the two. |

### 5.1 TEKKEN 7 STAGES
Raw stage content (`Game/Content/Maps`, `stgXX`) is inside the held paks — **HELD
raw, ZERO extracted/decoded**. The 34-stage ID table is mapped in docs only
(`teardown/TEKKEN-ARENA-STATUS.md`, itself stale: it still says "blocked on the full
47GB game — never acquired," which the depot pull superseded). The only T7 stage
held in extracted form anywhere is **one community map**: Mishima Dojo
(GRE `tekken7/arenas/mishima-dojo-map-2_17_24.rar`, 40,790,120 B; copy in WH
`teardown/tekken7/arenas/`) — an unopened archive, not wired.

---

## 6. TEKKEN 8

Evidence: GRE release `t8-community-pieces-v1` (2026-10-31); WH `teardown/tekken8/`
(11 files); checkpoint `steam-realcode-t7t8-20261030.json` (T8 pass BLOCKED).

| Category | State | Evidence |
|---|---|---|
| Community TKData dumps | **HELD (6 fighters)** | Release `t8-community-pieces-v1`: full data JSONs — Bryan 26,810,886 B, Jin 33,364,986 B, King ×2 (~32.7–32.9 MB), Heihachi 13,457,364 B, Shaheen 11,870,559 B, Yoshimitsu 31,093,684 B — plus small moveset JSONs (asuka/bob/bryan/heihachi/jin/king/shaheen) and `name_keys.json` (1,492,249 B). |
| Frame tables | **HELD (1 file)** | WH `game/data/t8_frame_tables.json`. |
| Anim slice | **HELD + WIRED (Law only)** | `game/assets/anim/t8/` = 11 files; Buffalo Bill's 796-move file draws `t8:[law]` = 162 moves (of t8 162 / t7 303 / t3 229 + forestlaw 102). |
| Models | **PARTIAL (2 community pulls)** | GRE `tekken8/models/`: Asuka SFM rar (30,027,257 B), Yoshimitsu S1 Blender 7z (83,173,144 B); WH release `tekken8-full-v1` = **one** 235,642,880 B part + sha256 (models/arenas only). |
| The game itself | **MISSING** | No T8 depot pull has ever run. The realcode lane's T8 pass is BLOCKED (2026-10-30): no Steam session / route was ever arranged for T8. No T8 moveset data beyond the 6 community dumps + Law; no T8 anim banks; no T8 customization. |
| T8 stages | **MISSING** | Arena data exists only inside the un-split community archive part; nothing extracted. |
| Waiting on T8 | — | **81 WH moves are strong T8-only candidates** (from the T7 join, §5) and cannot be honestly filled from T7 data. |

---

## 7. STAGES — headline table (owner asked specifically)

| Game | Stage state |
|---|---|
| Tekken 3 | **EXTRACTED, not wired** — 15 panorama OBJs + `stage.json` in WH teardown. |
| Tekken 5 (versus) | **MISSING** — name list only; NOT in TK5DATA0 (cracked 2026-11-06, FMV-only); DATA1 split files unexamined. |
| Devil Within (5 stages) | **PARTIAL** — structure/area/chamber tables extracted from the E4 binary; geometry, placements, scripts MISSING (not in DATA0 — cracked, FMV-only; DATA1 is the candidate). |
| Tekken 6 PSP | **DOES NOT EXIST in source** — proven: packages hold placement + textures only; 1 ground-plane quad extracted. |
| TTT2 (29 stages) | **MISSING** — public-data list only; geometry inside the never-fully-extracted STFS archive. |
| Tekken 7 (~34 stages) | **HELD RAW in the depot paks, ZERO decoded**; 1 community map archive (Mishima Dojo) held unopened. |
| Tekken 8 | **MISSING** — no usable stage data held. |

**Playable game today:** there is **no Tekken stage geometry under `game/` at all**.
Fights run on WH-original/procedural staging (`arenas/` = 173 files of panorama
drafts from Eastern Mind / No Mercy / Mat Legends sources; root `stages/` = one
WH-original spec, `cape-house/STAGE-SPEC.md`). Every Tekken stage in the game is a
future wiring job, and for T7 it is purely an extraction job on data we already hold.

---

## 8. WIRING STATE — the four buckets

**(a) Held AND wired into the playable game:**
T3 movesets + anim banks (the game's core); T7 frame data (44 tables); T7 clip-maps
(8 fighters); TTT2 Roger/Jun banks + rows; T5 costume GLBs (catalog); T8 Law slice
(inside Buffalo Bill); T6 moveset data only where individually built into a fighter.

**(b) Held but not wired:**
T6's 18 movesets + 3,444 mesh GLBs (teardown only); T5 Devil Within tables + E7
videos; T7 customization catalog (GRE, 4 MB items data vs 12 files converted);
T7 rotsm clips beyond the 8 clip-mapped fighters; T3 stage OBJs; GRE pakchunk0
model/texture extracts.

**(c) Decoded in a teardown repo, never assembled:**
T5 DATA1's 1,571 split files; TTT2 data004's MOTA tables for the unbuilt cast;
T5 E7 archive contents beyond the catalog slice; T6 COM tail payloads.

**(d) Not held at all:**
T5 versus models/moves/stages + DW geometry (NOT in DATA0 — cracked, FMV-only; DATA1 split files unexamined); the Tekken 8 game;
T6 PS3 full teardown + Scenario Campaign; TTT2 full STFS extraction + all stage
geometry; T7 stage extraction (raw held, decoded missing); T6 texture pixels +
skinning (capture-gated); DW gimmick/item tables + DW UI.

---

## 9. FILL PATHS — per missing item (named, not acquired)

| Missing item | Fill path | New acquisition needed? |
|---|---|---|
| T5 models, moves, stages, DW geometry (NOT in DATA0) | Content inventory + RE on DATA1's 1,571 held split files (DATA0 itself is DONE: cracked, FMV-only, release `tekken5-data0-cracked-20261106`) | **No** — DATA1 split already stored |
| DW boss AI behaviour, Jin DW moveset, gem/item tables | DATA1 split-file inventory (DATA0 held none of it); the extracted OBJ/CHR + area tables narrow the search | No |
| T5 audio banks | romD bank-directory RE on held TK5DATA2 | No |
| T5 skull mask; pack→character attribution | DATA1 search (DATA0 is open and holds neither); attribution table still unlocated | No |
| T6 texture pixels + skinning | **One PPSSPP GE capture session** (guide written: `PPSSPP-LIVE-RUN-GUIDE.md`) | No — a session, not a download |
| T6 stages / Scenario Campaign | Console (PS3) version only — the Draft `tekken6-ps3-full-v1` release is the in-hand lead and is unverified | **Maybe** — verify the Draft release first |
| TTT2 remaining banks (~57 fighters) | Reassemble held 7z chunks → STFS → repeat the proven data004 join per character. Disk space is the only gate | No — chunks already stored |
| TTT2 stages + full extraction | Same reassembly; STFS stage chunks | No |
| TTT2 True Ogre | **Does not exist** — fill Chatur from the held T3 ogre bank (211 clips) instead | No |
| T7 stages (all) | Unpack held depot paks (repak list/unpack documented in `teardown/tekken7/T7-STEAM-EXTRACTION.md`); umodel/FModel export step needs Windows or Wine | No |
| T7 bank-0x0000 (31 clips) | Hunt inside the held pakchunk1_P (wave0 release); land GRE PR #80's §9 first | No |
| T7 format-100 clips (F11) | RE on held rotsm clips (bs7/nsa-nsd twin-hunt per the realcode brief) | No |
| T7 14 frame-only fighters | Build movesets from held depot motbins + the held frame tables; Geese/Noctis add the per-file DLC decrypt step | No |
| T7 customization wiring | Convert the held GRE catalog/items data into the WH creation suite | No |
| T8 everything (movesets, banks, stages) + the 81 T8-only moves | A Tekken 8 pull via the same DepotDownloader route proven on T7, or more community TKData dumps per fighter | **Yes** — T8 was never pulled; route named only, per research-only scope |

---

## 10. Bottom line

- **Cold (done, proven):** T3 assets; T6 PSP static teardown; T5 ISO + disc split +
  customization; T7 full depot storage + frame data; TTT2 Roger/Jun.
- **Held but dark:** most of T6's wiring, T5's Devil Within tables, T7's stages and
  customization, TTT2's other 57 banks.
- **Flat missing:** all of T5's versus core + Devil
  Within's geometry), the whole of Tekken 8 beyond community scraps, TTT2 stage
  geometry, T7 stage extraction, and T6's texture pixels (one capture session away).

*Audit run 2026-11-06. Sources: WH main tree census (60,785 paths), GRE main
contents API, 30+ releases across both repos, agent-ops checkpoints as cited.
Nothing in this doc is marked owner-approved; it is a holdings record.*
