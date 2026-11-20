# Non-Tekken Extractions — Batch Research + Wiring Plan

**Date:** 2026-10-24
**Scope:** Characters whose moves/animations do NOT come from Tekken 7, researched in one batch.
**Button convention (everywhere in this document):** LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4. File fields that still store numeric inputs (`input`, `input_slots`) are quoted verbatim alongside their LP1/RP2/LK3/RK4 display form. Numeric and display forms are never silently swapped.
**No Tekken 8 data is used in this plan.** Any field in a repo file that carries a `t8:` prefix is listed below as EXCLUDED, not as wiring.

## How this was verified

Every count and field below was checked against `main` of `mhvnsnt/western-heart` through the data API on 2026-10-24, not taken from a prior summary:

- `game/data/moveset-library/index.json` — bank totals and pending-bank list.
- `game/data/moveset-library/banks/wrestling.json` (blob `89c1901c6016be847255114e1c1354599a48233c`, 5,329,678 bytes) — counted in full: 4,409 rows, 4,153 with a non-empty `input` field, 256 with `input: null`, 4,409 with an `anim_ref` field, 0 with an `input_lp` field.
- `game/data/moveset-library/banks/wmxix.json` — counted in full: 169 rows, 0 with a non-empty `input`, 169 with an `anim_ref` field.
- `game/data/moveset-library/banks/vf5.json` — counted in full: 96 rows, 96 with a non-empty `input`, 96 with an `anim_ref` field, 0 Dural rows.
- `game/assets/movesets/megami.json` — counted in full: 304 entries in `moves`, 155 carrying `tekken_base: "Jun Kazama (TTT2)"`, 149 carrying a `t8_source` field, 153 carrying an `anim_ref` field, 151 with no `anim_ref` field.
- `game/assets/movesets/zen.json` — counted in full: 639 entries in `moves` (interim Heihachi kit, kept separate), 25 entries in `wh_true_moveset.moves`, all 25 with `anim_ref: null` and `anim_status: "UNMAPPED"`.
- `game/assets/movesets/menajerii.json` — counted in full: 193 entries in `moves`, 7 with an `anim_ref` field, 186 with no `anim_ref` field.
- `game/assets/movesets/cainelias.json` — counted in full: 46 entries in `moves`.
- `game/assets/movesets/index.json` — fighter/tekken_base table (see discrepancies note below).
- `docs/research/VF5-MOTION-GAP-2026-10-22.md`, `docs/research/VF5-FULL-INTEGRATION-2026-10-22.md`, `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`, `roster/zen/CANON.md`, `docs/tech/STEAM-LIBRARY.md`, `docs/research/RE-WWE2K22-PLAN-2026-10-23.md`, `docs/research/WWE-CAW-EXTRACTION-STATUS.md`.

## Wiring rule used throughout (no class-correct guesses)

A move is WIRED only when a file attaches an exact clip to that exact move: a bank row id + `anim_ref` value, a moveset entry's `anim_ref` field, or a `t3_bank` + row number. "Same class" (strike vs strike, throw vs throw) is never wiring. If no exact clip exists, the entry is marked **UNMAPPED** — never filled with a "closest match."

The Move List Creator hook is the `anim_ref` field plus the input fields, per `game/assets/movesets/megami.json` field `canon_wiring.editor: "packages/creation-suite/src/movelist-editor.js (canon_moves + canon properties support)"`. A `wh:` value is a placeholder for an animation not yet authored (that file's own `canon_wiring.note` says so). A `made:` value is a wiring label pending an authored clip. A `null` value is UNMAPPED. A `t8:` value is EXCLUDED from this plan.

## Index discrepancies found (do not paper over)

- `game/data/moveset-library/index.json` says the T3 bank has `source_banks: 20` and 4,648 moves. The task brief's "22 banks" figure is NOT confirmed by that index file. Use 20 / 4,648 until a bank-by-bank count supersedes it.
- `game/assets/movesets/index.json` says Megami has 299 moves; the Megami file on `main` now has 304 entries in `moves`. It says Cain Elias has 41 moves; the Cain Elias file on `main` now has 46 entries in `moves`. The index file is stale relative to the moveset files. File counts above are the counted values; index counts are quoted only where they are the sole source.

## Summary table

| Character | True source | Model | Move list (input/damage) | Exact clip wired | Status |
|---|---|---|---|---|---|
| Zen | VF5 Dural (stance/base layer) + SFIII Twelve / SFV Eleven concept + own canon + X.COPY as ONE super | Tripo models in `roster/zen/CANON.md` (spirit body, spirit, Oversoul, Tentacle Mode) | `wh_true_moveset` 25 entries, inputs present | NONE — all 25 `anim_ref: null` | UNMAPPED (model only for Dural motion) |
| Megami | TTT2 Jun Kazama | UNMAPPED in this batch (no TTT2 model/clip bank in repo) | 155 TTT2-labelled entries in `megami.json` | 0 TTT2 clips; 151 entries have no `anim_ref` at all; 4 canon entries point at `wh:` placeholders | UNMAPPED for clips; input/damage data present for TTT2-labelled rows |
| Menajerii | TTT2 Roger Jr. | UNMAPPED in this batch | 193 entries, `t3_source` = Tekken Wiki TTT2 Roger Jr. movelist, "documented, no teardown bank" | 3 via `t3:kuma:row:*` (T3 Kuma proxy rows, NOT TTT2 Roger Jr. clips) + 4 `wh:menajerii:*` placeholders; 186 with no `anim_ref` | UNMAPPED for TTT2 clips |
| Cain Elias | WWE (Undertaker concept) | UNMAPPED in this batch for WWE clips | 46 entries | 46 via `t3:king:row:*` (T3 King proxy rows, NOT WWE 2K clips) | WWE-clip UNMAPPED; T3-proxy wired only |
| Chatur | Tekken 3 True Ogre | T3 bank | 152 entries | T3 bank rows (see §5) | WIRED via T3 bank (exact rows cited) |
| Dorowani | Tekken 3 Gon | T3 bank | 175 entries | T3 bank rows (see §5) | WIRED via T3 bank (exact rows cited) |
| Tobi | Tekken 3 Hwoarang | T3 bank | 729 entries | T3 Hwoarang rows | WIRED via T3 bank (exact bank cited) |
| Bannon / El Toro de Oro / Pablo / Finxsse | VF5 Jeffry / Wolf / El Blaze / Lei-Fei | VF5 models extracted | VF5 federation conversions (25 / 21 / 28 / 22 rows) | `vf:*` refs are federation-conversion labels, NOT decoded VF5 motion clips | MOVE DATA present; decoded VF5 motion UNMAPPED (same VF5 motion gap as Dural) |
| WWE 2K19 / 2K20 / 2K22 move library | WWE 2K (see §4) | No 2K clip bank in the moveset library | No Mercy bank (verified) + WMXIX bank (verified, provisional) | No Mercy `anim_ref` values are exact clip paths; WMXIX `anim_ref` values are registered clip paths with UNMAPPED move identity | No Mercy: WIRED at bank level (inputs present); WMXIX: UNMAPPED for move identity and inputs |

---

## 1. VF5 Dural → Zen

### What Zen actually is (from files, not from a summary)

`roster/zen/CANON.md` (fighting-base section, owner 2026-10-22, decision resolved 2026-10-24 in `docs/decisions/2026-10-24-zen-base-decision.md`):

- Base = Twelve (Street Fighter III: 3rd Strike) and his 3D relative Eleven (Street Fighter V). Owner quote in that file: "Twelve/eleven stance and moves from the street fighter games", "use his 3d relative eleven instead too".
- X.COPY (Twelve's Super Art: he becomes a copy of the opponent for a while) is ONE of Zen's abilities, not his identity: "he has to have his own stuff as well that fits his canon."
- NOT Julia (Nightwolf owns Julia's moves) and NOT Heihachi (Heihachi becomes Diablo).
- Base mix, owner 2026-10-22: "Dural's stance is Zen's stance for now", Dural is a permanent layer of the base mix, and Twelve's/Eleven's movement (including Twelve's dancing idle stance) is added ON TOP.
- Dural was chosen because it is the closest 3D thing to Eleven/Twelve (2D Street Fighter shapeshifters). That rationale is recorded in `game/assets/movesets/zen.json`, `wh_true_moveset.base_chain`: "Eleven/Twelve (Street Fighter, 2D concept: shapeshifting mimicry) -> Dural (Virtua Fighter 5, 3D implementation: chrome humanoid, closest 3D thing to Eleven/Twelve) -> Zen's own canon moves on top."

### Current state — model only, motion never converted (verified fact)

- `docs/research/VF5-MOTION-GAP-2026-10-22.md`: "VF5 PS3 motion data was never acquired. All pulled archives (release `vf5-ps3-v1`, 89 assets) contain character models and textures only. No motion/animation files exist in any accessible archive. The format is undocumented publicly."
- Same doc, Dural specifically: `dur.farc` (760B) + `duritm.farc` (25.5MB) extracted via `tools/farc_extract.py` — 28 entries, all `*_obj.bin` (models) and `*_tex.bin` (textures). Zero motion files.
- `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`: "VF5 motion data was never converted. The VF5 teardown has model data only — no motion/animation extraction exists on disk. Dural's stance, idle, strikes, and movement are therefore entirely absent."
- `game/data/moveset-library/banks/vf5.json`: 96 rows total — El Blaze 28, Jeffry 25, Lei-Fei 22, Wolf 21 — and **0 Dural rows**. There is no Dural move row to wire to Zen in the library.
- `game/js/fighter.js`: `zen: null` in the bank table (UNMAPPED per the 2026-10-24 owner decision). The interim 639-move Heihachi kit in `zen.json` `moves` is separate data and is NEVER mixed with `wh_true_moveset`.

### Zen's true moveset — exact wiring (or UNMAPPED) per entry

Source: `game/assets/movesets/zen.json`, `wh_true_moveset.moves` (25 entries). Every entry below has `anim_ref: null`, `anim_status: "UNMAPPED"`. Inputs are quoted in LP1/RP2/LK3/RK4 display form as stored in the file's `display_input` field. No clip is claimed for any of them.

Twelve moves (category `twelve`):

| id | Name | display_input | anim_ref |
|---|---|---|---|
| `ndl` | N.D.L. | d, d/f, f+LP1 | null — UNMAPPED |
| `axe` | A.X.E. | d, d/b, b+LP1 | null — UNMAPPED |
| `axe-air` | A.X.E. (Air) | AIR.d, d/b, b+LP1 | null — UNMAPPED |
| `dra` | D.R.A. | AIR.d, d/b, b+LK3 | null — UNMAPPED |
| `hug` | H.U.G. | LP1+LK3 | null — UNMAPPED |
| `flg` | F.L.G. | f+LP1+LK3 | null — UNMAPPED |
| `trw` | T.R.W. | b+LP1+LK3 | null — UNMAPPED |
| `bmk` | B.M.K. | b+LK3 | null — UNMAPPED |
| `kokkuu` | Kokkuu | AIR.f, f | null — UNMAPPED |
| `kabe-haritsuki` | Kabe Haritsuki | f | null — UNMAPPED |

Super moves (category `super`):

| id | Name | display_input | anim_ref |
|---|---|---|---|
| `xndl` | X.N.D.L. | d, d/f, f, d, d/f, f+LP1 | null — UNMAPPED |
| `xflat` | X.F.L.A.T. | AIR.d, d/f, f, d, d/f, f+RK4 | null — UNMAPPED |

X.COPY as ONE super (category `xcopy`) — this is the single mimicry ability, not Zen's identity:

| id | Name | display_input | anim_ref |
|---|---|---|---|
| `xcopy` | X.C.O.P.Y. | d, d/f, f, d, d/f, f+LP1+RP2 | null — UNMAPPED |

Zen's own canon signatures (category `zen_signature`) — inputs, limb, damage, startup are from `canon-moves-needing-made-animations-2026-10-24.md` (ZEN section) as recorded in `wh_true_moveset.sources`; clips do not exist:

| id | Name | display_input | Filed limb / damage / startup | anim_ref |
|---|---|---|---|---|
| `does-not-compete` | Does Not Compete | b+LP1+RP2 | armL / 15 / 15f | null — UNMAPPED |
| `refused-seat` | Refused Seat | LP1+RP2 | armR / 16 / 17f | null — UNMAPPED |

Canon form attacks with NO input in the file (`NEEDS-INPUT` in the file itself — do not invent one):

| id | Name | display_input in file | anim_ref |
|---|---|---|---|
| `tentacle-pastel-ink` | Pastel ink blast | NEEDS-INPUT | null — UNMAPPED |
| `tentacle-razor-beam` | Razor beam | NEEDS-INPUT | null — UNMAPPED |
| `tentacle-wave` | Pastel wave | NEEDS-INPUT | null — UNMAPPED |
| `oversoul-attack` | Oversoul combined-form attack | NEEDS-INPUT | null — UNMAPPED |
| `spirit-attack` | Spirit-form stand attack | NEEDS-INPUT | null — UNMAPPED |
| `spirit-side-switch` | Spirit side-switch | NEEDS-INPUT | null — UNMAPPED |

Transformations (category `transformation`, triggers from `roster/zen/CANON.md` forms chain, touch TRANSFORM + full nine-soul meter):

| id | Name | display_input in file | anim_ref |
|---|---|---|---|
| `transform-tentacle` | TENTACLE MANIFESTATION | TRANSFORM, up | null — UNMAPPED |
| `transform-oversoul` | OVERSOUL | TRANSFORM, up | null — UNMAPPED |
| `transform-withdraw` | WITHDRAW | TRANSFORM, down | null — UNMAPPED |
| `transform-release` | OVERSOUL RELEASE | TRANSFORM, down | null — UNMAPPED |

Stance itself: `wh_true_moveset.stance` = "Dural's stance is Zen's stance (permanent base layer, owner 2026-10-22); Twelve's dancing idle stance is added ON TOP once converted 2D->3D. Stance itself is UNMAPPED until VF5 Dural motion is extracted." No stance clip is claimed.

Eleven contribution, stated exactly as the file states it: Eleven has NO own moveset — before every SFV match it randomly morphs into another character and fights with that character's kit (`wh_true_moveset.eleven_note`, source: Street Fighter Wiki, Eleven). Eleven therefore contributes ZERO distinct moves here — concept (mimicry) and 3D-form lineage only. Zen does NOT randomly morph; his only mimicry is X.C.O.P.Y. above.

Dural move contribution, stated exactly as the file states it: Dural has no officially published movelist; her style is an amalgamation of moves from several VF fighters (`wh_true_moveset.dural_note`, source: Video Game Characters Database, Dural). No specific VF5 Dural attack row is wired as a Zen move in `wh_true_moveset` — wiring VF5 rows as Zen moves would make Zen a copycat again. Dural's layer is stance + inhuman movement + amalgam principle, pending VF5 motion extraction.

### Interim Heihachi kit — what it is and what it is NOT

`zen.json` `moves` (639 entries) is built on `t3_bank: "moveset_heihachi.json"`, `t3_bank_rows: 383`, `t3_bank_attack_rows: 96`. Its `anim_ref` prefixes, counted: `t3:heihachi:*` 307 rows, `t7:heihachi:*` 183 rows, `t8:heihachi:*` 145 rows, `wh:zen:sig:*` 4 rows (the two signatures, each appearing twice — once in `moves`, once in `wh_true_moveset` context; the signature clips themselves are not authored). Per this plan's no-T8 rule, the 145 `t8:heihachi:*` refs are EXCLUDED and are not Zen wiring. The Heihachi kit is interim data only and is never mixed with `wh_true_moveset`.

### VF5 motion options (VM-doable research, no waiting state)

1. **FARC model path (already done, motion absent).** `tools/farc_extract.py` on `dur.farc` / `duritm.farc` yields models/textures only. Re-running it cannot produce motion; the motion files are not in those archives. Do not re-run it expecting a different result.
2. **Full-archive search (VM-doable, format work required).** `docs/research/VF5-MOTION-GAP-2026-10-22.md` notes the 4GB `vf5-500m` split archive (8 parts, high-entropy, not fully pulled) *may* contain motion files — this is UNVERIFIED. VM-doable step: inventory that archive's file list (without downloading the full 4GB to this VM) and look for non-model, non-texture entries. If none exist, the motion source is outside the pulled archives.
3. **VF5 Final Showdown PC path (research only).** The 2026-10-22 gap doc notes MikuMikuLibrary covers VF5FS PC *models*; it does not cover PS3 motion. No public documentation of the VF5 PS3 motion format was found in the 2026-10-22 web research or in this batch's web search. Motion-format reverse engineering (header identification, bone-track parsing, keyframe decompression) is a multi-day RE task, not a single-session conversion.
4. **MADE path (labelled MADE, never presented as decoded).** Zen's stance, Twelve moves, and canon signatures can be authored as MADE specs from their documented descriptions (SuperCombo Twelve archive, canon notes) — the same pattern as the Megami MADE specs on `main` (`game/assets/anim/made/megami/`). MADE specs must carry `provenance: "MADE"` and must be REPLACED by decoded Dural motion when it exists, not kept alongside it as if decoded.
5. **Wiring target when Dural motion lands (from `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`, not yet existing):** land at `game/assets/anim/vf5/dural/` with `skeleton.json` + `rows.pack.json`, register in the anim bank table, and bind `bankIdFor('zen')` to `dural` when the base layer activates. FIGHT clips (stance/idle, strikes, Twelve conversions) go to the combat bank; SHOW clips (intro/win, transformation presentation) go to intro/win slots ONLY per the SHOW-ANIMATION LOCK and must never enter the moveset without explicit owner approval.

**Specific technical blocker (not a waiting state):** VF5 PS3 motion files are not present in any archive pulled to this repo, and their format is undocumented publicly. This Linux VM cannot run the PS3 game to capture motion live. That blocks decoded Dural clips; it does not block the MADE path or the archive-inventory step above.

### VF5 federation conversions — the wiring pattern to copy (not Dural content)

`game/assets/movesets/vf-elblaze.json` / `vf-jeffry.json` / `vf-wolf.json` / `vf-leifei.json` (schema-v2) convert VF inputs to Tekken inputs per `docs/movesets/DOA-VF-CONVERSION-2026-10-19.md` (P→LP1/RP2, K→LK3/RK4, P+K→LP1+RP2, P+G→LP1+LK3, K+G→LK3+RK4). Library example, verified in `banks/vf5.json` row `vf5:el-blaze:1`: `name: "Jab"`, `input: "1"` (display LP1), `anim_ref: "vf:elblaze/jab"`, `limb: "armR"`, `damage: 7`, `frames: {startup: 14, active: 2, recovery: 26}`, `provenance.source_file: "vf-elblaze.json"`, `provenance.source_key: "1"`. That `anim_ref` is a federation-conversion label, NOT a decoded VF5 motion clip — the same distinction applies to every VF5 row until motion lands. When Dural motion lands, its rows must use the same fields (`id`, `input`, `input_slots`, `anim_ref`, `limb`, `damage`, `frames`, `provenance.source_file`, `provenance.source_key`) with `source_character: "DURAL (VF5)"` and a real motion-clip `anim_ref`, not a `vf:*` label.

---

## 2. TTT2 Jun → Megami

### Current state (verified from the file itself)

`game/assets/movesets/megami.json` on `main`:

- `fighter: "megami"`, `tekken_base: "Jun Kazama (Tekken Tag Tournament 2)"`, `t3_source: "tekken-wiki TTT2 Jun Kazama movelist (documented, no teardown bank)"`, `ttt2_source: "tekken.fandom.com/wiki/Jun_Kazama/Tekken_Tag_Tournament_2_Movelist"`, `ttt2_note: "Jun is NOT in T7. All moves from Tekken Tag Tournament 2. TTT2 is the source, NOT T7."`
- Stances: `GEN (Genjitsu, b+LP1+RP2)`, `IZU (Izumo, f+LP1+RP2)` — stored in the file with numeric `b+1+2` / `f+1+2` forms alongside LP1/RP2 display forms in `canon_moves`.
- 304 entries in `moves`. Field census: `name` 304, `input` 304, `input_lp` 304, `input_slots_lp` 300, `tekken_base` 155, `anim_ref` 153, `t8_source` 149.
- **The 149 `t8_source` rows are EXCLUDED from this plan.** Their `anim_ref` values are of the form `t8:jun:jun-1`, `t8:jun:jun-1,1`, etc. Those are not TTT2 Jun clips and must not be presented as TTT2 wiring, must not be copied into the Move List Creator as TTT2 clips, and must not be used to claim Megami is clip-wired. Jun is not a T7 fighter (story ghost only), and this plan uses no T8 data at all.
- **151 entries have no `anim_ref` field at all.** Those are input/damage data without any clip — UNMAPPED for animation.
- The 4 canon entries in `canon_moves` point at `wh:` placeholders, and that section's own note says: "`wh:` refs are placeholders for animations not yet authored; `made:` refs are wiring labels pending the sibling animation lane clips. NOT play-verified."

### Actual TTT2-wired fields (input/damage level — clips UNMAPPED)

These rows carry `tekken_base: "Jun Kazama (TTT2)"` and full LP1/RP2/LK3/RK4 input fields. Their clip field is absent — that absence is the wiring fact, not a gap to guess over:

| File key | Name | `input` (file) | `input_lp` (file) | Damage | Hit / throw data in file | `anim_ref` |
|---|---|---|---|---|---|---|
| `1+3` | Shiho Nage | `1+3` | `LP1+LK3` | 35 | Front throw, escape `1` | NONE — UNMAPPED |
| `2+4` | Katanuki | `2+4` | `RP2+RK4` | 35 | Front throw, escape `2` | NONE — UNMAPPED |
| `1+3~L` | Cloud Taste | `1+3` | `LP1+LK3` | 40 | Left-side throw, escape `1` | NONE — UNMAPPED |
| `2+4~R` | Wind Wheel | `2+4` | `RP2+RK4` | 40 | Right-side throw, escape `2` | NONE — UNMAPPED |
| `BT 1+3` | Twisted Limbs | `1+3` | `LP1+LK3` | 50 | Back throw | NONE — UNMAPPED |
| `d/f+1+2` | Riai | `d/f+1+2` | `d/f+LP1+RP2` | 40 | Command throw, escape `1+2` | NONE — UNMAPPED |
| `d/f+2+3` | White Mountain | `d/f+2+3` | (file field present per census; value follows the same LP1/RP2/LK3/RK4 mapping) | 40 | Command throw, escape `2` | NONE — UNMAPPED |

Do NOT invent Jun→Megami pairings from move-name similarity (e.g., do not map a T7/T8 Jun-named clip to a TTT2 Jun move because the names match). The only Jun clips that would count as TTT2 wiring are clips extracted from a TTT2 Jun source, filed under a TTT2 bank, with the move's input as the key. None exist in the repo.

### Megami's 4 canon moves (WH-original, MADE — not Jun TTT2 moves)

Source: `megami.json` `canon_moves` + MADE specs on `main` under `game/assets/anim/made/megami/` (README-MADE.md present on `main`). These are canon/WH-original and must never be mislabelled as decoded Jun moves:

| Name | `display_input` | `anim_ref` in file | Damage / startup in file | Status |
|---|---|---|---|---|
| Threshold Keeper | b+LP1+RP2~b | `wh:megami:threshold-keeper` | 0 / 18f, stance | MADE spec, clip NOT authored |
| Sealed Door | d/b+LP1+RP2 | `wh:megami:sealed-door` | 30 / 34f, unblockable gate-slam | MADE spec, clip NOT authored |
| Kaimon (Opening) | GEN LP1+RP2 | `wh:megami:kaimon` | 24 / 26f, wall splat | MADE spec, clip NOT authored |
| Seal of the Shrine | RAGE,d/f+LP1+RP2 | `wh:megami:seal-of-the-shrine` | 55 / 20f, block -18, hit +0d, Rage Art | MADE spec, clip NOT authored |

Wiring plan for these four: keep them in `canon_moves` with their `wh:` refs and `display_input` fields for the Move List Creator; when a decoded TTT2 Jun clip genuinely matches one (same input, same limb, same outcome — not merely same class), replace the `wh:` ref with the decoded bank ref and change the provenance from MADE to decoded. Do not keep both as if both were decoded.

### TTT2 extraction options (VM-doable research)

1. **Documented movelist (already in the file, VM-doable, no clips).** The Tekken Wiki TTT2 Jun movelist (URL in §8) gives input, damage, and hit level/range for Jun's TTT2 kit. It does NOT give startup frames for most moves and gives no clips. That is why `megami.json`'s `frame_convention` says startup values are "from documented i-frames where known (i10 1,2,4 / i13 b+4,2 / i14 d/f+2,1 / i16 u/f+4,3 / i16 d/b+1,2), otherwise standard Tekken archetype estimates" — estimates are flagged as estimates in that file and must not be re-presented as extracted frame data.
2. **TekkenMovesetExtractor — Tag2 via CEMU (tool verified to exist, platform-blocked on this VM).** The tool's own documentation describes exporting from Tag2 under CEMU (Wii U emulator): find the CEMU base address with Cheat Engine scans, set `cemu_base` / `cemu_p1_addr` in `game_addresses.txt`, then export. That path requires a Windows machine running CEMU + TTT2 (Wii U). This Linux VM cannot run that stack — specific technical blocker, not a waiting state. It is listed in §8 as a parent-delegation item with the exact release URL.
3. **T5/T3 Jun fallback — INVALID, do not use.** Jun is not a Tekken 3 fighter (no Jun bank exists in the T3 library: the T3 reference files are Anna, Bosconovitch, Eddy, Forest Law, Gon, Hwoarang, Julia, Kuma, Law, Lei, Nina, Ogre, Paul). Substituting Asuka rows (Jun's TTT2 moveset shares throws with Asuka in the wiki tables, e.g., Katanuki / Cloud Taste / Wind Wheel appear in both) would be a name-similarity guess and is forbidden by the wiring rule. TTT2 Jun fallback = UNMAPPED.
4. **MADE core specs (already started on `main`).** `game/assets/anim/made/megami/` holds MADE specs for Jun core strings (Whiplash LP1,LP1; Jab Uppercut LP1,RP2; Jab Uppercut Spin Kick LP1,RP2,RK4; Jab Low Kick LP1,LK3; GEN/IZU entries) built only from the documented movelist. Their own header says timing is NEEDS-SPEC because the movelist page documents no startup. Those specs are the correct interim wiring for the Move List Creator (input + limb + hit level, labelled MADE) until decoded TTT2 clips exist.

### Menajerii — same TTT2 blocker, different fighter

`game/assets/movesets/menajerii.json`: `tekken_base: "Roger Jr. (Tekken Tag Tournament 2)"`, `t3_source: "tekken-wiki TTT2 Roger Jr. movelist (documented, no teardown bank)"`, 193 entries, 7 with `anim_ref` (4 `wh:menajerii:*` placeholders + 3 `t3:kuma:row:*` T3 Kuma proxy rows), 186 with no `anim_ref`. The 3 T3 Kuma rows are T3 proxy wiring, NOT TTT2 Roger Jr. clips. The TTT2 Roger Jr. movelist page URL was not verified in this batch — it is UNVERIFIED, not guessed, and is a §8 delegation item to fetch exactly.

---

## 3. WWE-based characters — what is actually wired, and what is not

### The only WWE-concept fighter in the moveset index

Cain Elias — `game/assets/movesets/cainelias.json`: `tekken_base: "Undertaker (WWE)"`, `t3_source: "king"`, 46 entries. Every entry is wired through a T3 King proxy row, NOT through a WWE clip. Verified examples (file fields quoted verbatim):

| File key | Name in file | `input` | `t3_row` | `t3_command` | `anim_ref` | Limb / damage |
|---|---|---|---|---|---|---|
| `1` | CAIN ELIAS 1 (T3 king r38) | `1` (display LP1) | 38 | LP | `t3:king:row:38` | armL / 7 |
| `2` | CAIN ELIAS 2 (T3 king r203) | `2` (display RP2) | 203 | RP | `t3:king:row:203` | armR / 12 |
| `3` | CAIN ELIAS 3 (T3 king r64) | `3` (display LK3) | 64 | LK | `t3:king:row:64` | legL / 9 |
| `4` | CAIN ELIAS 4 (T3 king r216) | `4` (display RK4) | 216 | RK | `t3:king:row:216` | legR / 18 |

That is the wiring pattern for a WWE-concept fighter today: WWE concept + T3 King motion bank. No WWE 2K clip is attached to any Cain Elias move. Do not present the T3 King rows as WWE moves.

Pantera is NOT a WWE-based character in this plan: his base is King (Tekken), and his moveset is a Tekken moveset. Pablo is NOT WWE-based either: his base is El Blaze (VF5, lucha libre style), wired through the VF5 federation conversion above.

### WWE 2K19 / 2K20 / 2K22 / 2K26 — game-file status

- `docs/tech/STEAM-LIBRARY.md` (on `main`) lists WWE 2K19 (app 817130), WWE 2K20 (app 1015500), and WWE 2K22 (app 1255630) as owned titles, with the note for 2K22: "movesets, anims, CAW creation suite (best rig/anim quality of the three)." WWE 2K26 is NOT listed in that file — its ownership is UNVERIFIED in this batch. Do not claim it.
- **No WWE 2K clip bank exists in the moveset library.** `game/data/moveset-library/index.json` `pending_banks` lists `vf5-motion`, `t7`, `ttt2`, `t6`, `soulcalibur`, `urban_reign`, `bloody_roar`, `sf`, `def_jam` — there is no `wwe2k` pending-bank entry and no `wwe2k` bank file. The WWE 2K move library is therefore UNMAPPED at bank level, regardless of game ownership.
- `docs/research/RE-WWE2K22-PLAN-2026-10-23.md` (the 2K22 reverse-engineering plan, reconstructed from a lost worker doc) gives the VM-doable research path: Phase 1 Oodle decompression (call the game's own `oo2core_*.dll` via FFI, or `libooz` — license unverified, stays private until read), Phase 2 `.pac` format (64-bit ID addressing, nested pacs, `string_win.pac` string tables, character folders `pac/ch` / `pac/edit/ch`, oracle tools CakeTools / rePac / PAC Editor / WrestleMinus / CakeHook `_mods`), Phase 3 `.ch.pac` character work (texture-first validation via `DDS` magic, mesh heuristics, skeleton via bone-name strings, animations via frame-count/track headers), Phase 4 creation suite (`pac/edit/**` census, master parts table via `string_win.pac` cross-reference, CAW saves as Rosetta Stone). The 2K22 community path is also documented publicly: 2K22 character data lives in `bakedfile00.cak` (`charactermapping.jsfb` in the Characters folder, opened with Caketools) — see the SmackTalks tutorial URL in §8. That tooling is Windows/PC tooling; it is not runnable on this Linux VM without the game files, which is the specific blocker below.
- **Specific technical blocker (not a waiting state):** WWE 2K titles are tens of GB each, Windows PC games, and no 2K `.pac` / `.cak` / moveset file is present in this repo or on this VM. Extracting 2K movesets requires a Windows PC with the owned game installed (see §8 delegation items). That blocks decoded 2K clips; it does not block using the already-verified No Mercy and WMXIX banks below.

### No Mercy bank — VERIFIED, and its inputs ARE the wiring

`game/data/moveset-library/banks/wrestling.json` — verified in full against `main` (blob SHA above):

- `bank: "wrestling"`, `game: "wwf_no_mercy"`, `count: 4409`, `source_game_label: "WWF No Mercy (N64) — mat-kings DB"`.
- 4,153 rows have a non-empty `input` field; 256 rows have `input: null` (those 256 are UNMAPPED for input — do not invent inputs for them).
- 4,409 rows have an `anim_ref` field. Verified example, row 0: `id: "wrestling:mk-0000"`, `name: "Chop 01"`, `name_status: "DB label from No Mercy re-docs"`, `anim_ref: "teardown/wwf-no-mercy/animations/clips/anim_3322.npy"`, `type: "strike"`, `position: "standing"`, `orientation: "forward"`, `input: "1"`, `input_slots: ["1"]`, `frames.total: 13`, `damage: 2`, `provenance.mk_move_id: "MK-0000"`, `provenance.mk_category: "Weak Arm Striking"`, `provenance.mk_power: "F"`, `provenance.mk_slot_eligibility: ["weakArmStrikeSlot1", "weakArmStrikeSlot2"]`, `provenance.estimated: ["damage (WH scale)", "hit_level", "subtype", "limb"]`.
- Type census: grapple 3,304, throw 584, strike 377, counter 103, aerial 39, transition 2. Position census: standing 3,464, grounded 775, running 117, airborne 39, corner 14.
- **Input conversion required before Move List Creator use (mechanical, not invented):** the bank stores numeric Tekken-style inputs (`"1"`, `"2+4"`, `"f+2+4"`, `"1+3 [opponent grounded]"`, `"d+3"`, `"f,f+2"`, etc.) and has **0 rows with an `input_lp` field**. The Creator wiring step is to ADD an `input_lp` field by the fixed mapping 1→LP1, 2→RP2, 3→LK3, 4→RK4, preserving direction prefixes and bracketed conditions verbatim (e.g., `input: "2+4"` → `input_lp: "RP2+RK4"`; `input: "1+3 [opponent grounded]"` → `input_lp: "LP1+LK3 [opponent grounded]"`). That mapping is mechanical and auditable row by row; it does not change the move, the clip, or the slot eligibility. Rows with `input: null` stay UNMAPPED for input.
- **What the bank does NOT give:** `hit_level` and `limb` are in the bank's own `provenance.estimated` list for row 0 (and the same estimation flag pattern applies bank-wide per the index file's honesty note: "estimated fields are flagged per-entry in `provenance.estimated`; nothing is invented as canon"). Startup/active/recovery are `null` on row 0; only `frames.total` is populated (13). Do not present estimated damage, hit level, limb, or frame data as extracted values.
- **Move List Creator wiring for No Mercy rows:** key = bank `id` (e.g., `wrestling:mk-0000`); slot eligibility = `provenance.mk_slot_eligibility` (e.g., `weakArmStrikeSlot1`); clip = `anim_ref` (e.g., `teardown/wwf-no-mercy/animations/clips/anim_3322.npy`); input = bank `input` + added `input_lp`; position/orientation = bank `position` / `orientation` (standing/forward, grounded, running, airborne, corner). A No Mercy row becomes a Creator move only when all four (id, input_lp, slot eligibility, anim_ref) are present. The 256 input-null rows fail that test and stay out until an input source is found.

### WMXIX bank — VERIFIED, provisional labels, NO inputs, never move names

`game/data/moveset-library/banks/wmxix.json` — verified in full against `main`:

- `bank: "wmxix"`, `game: "wwe_wrestlemania_xix"`, 169 rows, 0 with a non-empty `input`, 169 with an `anim_ref` field.
- Verified example, row 0: `id: "wmxix:wmxix-001"`, `name: "Mat Legends Grapple A"`, `name_status: "provisional registry label — per-clip move identity not yet decoded (TEARDOWN.md §5 open item: per-clip hash-set -> move-category mapping); NOT a canon move name"`, `source_game_label: "WWE WrestleMania XIX (GC) — YANM clips"`, `anim_ref: "teardown/wmxix/animations/a.json"`, `type: "grapple"`, `position: "standing"`, `input: null`, `input_slots: []`, `provenance.wmxix_move_id: "WMXIX-001"`, `provenance.wmxix_canon_id: "ML-A"`, `provenance.estimated: ["damage (WH scale)", "type", "position", "input"]`.
- **Rules for WMXIX, stated plainly:** (1) Never present a WMXIX clip label (e.g., "Mat Legends Grapple A") as a real move name — the file itself says it is NOT a canon move name. (2) Never invent an input for a WMXIX row — all 169 have `input: null` and `input_slots: []`. (3) The next step is the file's own open item: per-clip hash-set → move-category mapping (TEARDOWN.md §5), which would give each clip a category, not a name or an input. Until that mapping lands, WMXIX rows are UNMAPPED for the Move List Creator (they have a clip path but no input and no verified move identity, so they fail the four-field Creator test above).
- WMXIX creation-suite parts (separate from moves): `docs/research/WWE-CAW-EXTRACTION-STATUS.md` records 2,690 CAW `edit_data` files catalogued (1,470 textures + 1,200 YOBJ meshes) under `customization/parts/wmxix/`, plus 1,478 raw textures still needing slot sorting. Those are creation parts, not moves — do not wire them as moves.

### WWE 2K creation-suite data (what exists in repo docs, not in the move library)

- `docs/research/WWE2K-CREATION-SUITE-TARGETS-2026-10-23.md` and `WWE2K22-CREATION-SUITE-2026-10-23.md` (on `main`) hold the 2K creation-suite structure research (CAW structure, parts catalog, combined creation suite). `customization/wwe2k-caw/` holds that structure research so the 2K part taxonomy slots into `customization/parts/` when files land. That is taxonomy research, not extracted 2K moves — do not cite it as a move bank.
- The 2K19 moves/entrance animation data referenced in `WWE-CAW-EXTRACTION-STATUS.md` ("Moves/entrance animation data for 2K15–2K20 is already secured (wwe2k19-animation-packs-v1 release)") is a release reference, not a bank file in `game/data/moveset-library/` on `main`. Until a bank file with row ids, inputs, and `anim_ref` values is verified on `main`, 2K19 animation packs are UNVERIFIED for Creator wiring in this plan. That release is a §8 delegation item to locate and verify, not a cited bank.

---

## 4. Earlier-Tekken bases — T6 / T5 / T3

### T3 — the only earlier-Tekken bank actually wired (verified)

`game/data/moveset-library/index.json`: bank `t3`, game `tekken3`, file `banks/t3.json`, 4,648 moves, `source_banks: 20`. (Not 22 — see discrepancies note.)

Characters whose Tekken base is explicitly Tekken 3 in the moveset index (primary source, not fallback):

| Character | File | `tekken_base` in index | T3 source field in index | Moves in index |
|---|---|---|---|---|
| Chatur | `game/assets/movesets/chatur.json` | True Ogre (Tekken 3) | `teardown/tekken3/movesets/moveset_ogre.json (bank divmot14_ogre.bin, bank_type 14, 330 rows)` | 152 |
| Dorowani | `game/assets/movesets/dorowani.json` | Gon (Tekken 3) | `teardown/tekken3/movesets/moveset_gon.json (bank type 19, divmot19_gon.bin, 369 rows, 157 attacks)` | 175 |
| Tobi | `game/assets/movesets/tobi.json` | Hwoarang (Tekken 3) | `hwoarang` | 729 |

T3 reference files (same bank, for lookup — not separate characters): `t3-anna.json` (Anna, 743), `t3-bosconovitch.json` (266), `t3-eddy.json` (707), `t3-forestlaw.json` (102), `t3-gon.json` (151), `t3-hwoarang.json` (723), `t3-julia.json` (419), `t3-kuma.json` (530), `t3-law.json` (693), `t3-lei.json` (790), `t3-nina.json` (754), `t3-ogre.json` (161), `t3-paul.json` (497). Counts are from `game/assets/movesets/index.json`.

**T3-as-fallback vs T3-as-primary distinction (important, do not blur):** Most other fighters in the index carry a `t3_source` value that is a *proxy bank name* (`jin`, `bryan`, `king`, `heihachi`, `law`, `xiaoyu`, `gunjack`, `yoshimitsu`, `kuma`, `paul`, `lei`, `eddy`, `bosconovitch`, `nina`, `julia`, `ogre`, `forestlaw`) — that value names the T3 bank their interim rows were built from, NOT a claim that their Tekken base is Tekken 3. Example: Zen's `t3_source: "heihachi"` does not make Zen a Tekken 3 character; his true base is the Dural/Twelve mix in §1, and the Heihachi rows are interim. Example: Cain Elias's `t3_source: "king"` does not make him a Tekken 3 character; his concept base is WWE (see §3). Only Chatur, Dorowani, and Tobi (above) have `tekken_base` explicitly naming Tekken 3.

**T3 wiring format (exact):** T3 rows are cited as `t3:<bank>:row:<n>` in moveset `anim_ref` fields (e.g., Cain Elias `t3:king:row:38`), with `t3_row`, `t3_command` (LP/RP/LK/RK), `startup`, `active`, `recovery`, `damage`, and `limb` fields on the moveset entry. That is the complete wiring — bank + row + command + input — and it is the pattern the VF5 and TTT2 lanes must match when their banks land.

### T6 — present as an ISO on disk, no decoded bank, no assigned character

- Local file (this VM, not the repo): `~/workspace/t6work/tekken6-psp.iso` (460 MB, dated 2026-10-23 in local listing). The local T6 work directory also contains ELF cross-reference output naming `DATA401.IDX` (`%s/DATA401.IDX` string, `DINF_400.BIN`, `packdatas_t` structures) from `teardown/tekken6/decrypted/EBOOT.DECRYPTED.ELF` (4,158,144 bytes, 6,188 strings).
- **Blocker, stated specifically:** the T6 PSP data index is encrypted (DATA401.IDX), no decoded T6 move bank exists in the repo, and no WH character in the moveset index claims Tekken 6 as its base. The moveset-library `pending_banks` entry for `t6` says only "pending — decrypt6 lane DATA401." Until a decrypt lane produces a bank file with row ids and inputs, T6 contributes ZERO wired moves, and no character may be assigned to T6 on the basis of the ISO's existence.
- **VM-doable next step (not a waiting state):** inventory the ISO's file list and the DATA401.IDX header structure from the existing ELF xref output, and record which T6 characters (if any) the owner assigns to T6. Do not download another T6 copy and do not claim T6 moves from T3 rows.

### T5 — no bank, no assigned character, UNMAPPED

No moveset index entry claims Tekken 5 as its `tekken_base`, no `t5` bank exists in the moveset library (the pending-banks list has no `t5` entry), and no T5 file was verified in this batch. T5 is therefore UNMAPPED for every character. The only legitimate T5 use in this plan is as a *future* fallback inquiry for Megami/Menajerii if TTT2 clips cannot be obtained — and even then, only if a T5 Jun / Roger Jr. bank is actually produced and its rows are cited by bank + row, never by name similarity. (Note: Jun and Roger Jr. are TTT2 fighters; a T5 source for them would need its own verification — it is not assumed here.)

---

## 5. Other owned games — research only, no move wiring

Per `docs/tech/STEAM-LIBRARY.md`, the owned titles relevant to this batch are listed with their app ids. **None of them is claimed as any WH character's `tekken_base` in `game/assets/movesets/index.json`.** Their repo docs are systems research, not move banks. That is the finding — do not upgrade systems research into move wiring.

| Game (app id from STEAM-LIBRARY.md) | Repo research doc on `main` | What it actually gives | Move wiring |
|---|---|---|---|
| Fire Pro Wrestling World (564230) | `docs/research/FIRE-PRO-SYSTEMS-2026-10-23.md`, `docs/research/RE-FIREPRO-DESTINY2-PLAN-2026-10-23.md` | CPU vs CPU simulation, edit-a-wrestler depth, AI logic programming | NONE — no Fire Pro move bank in the library; no character claims Fire Pro as base |
| Yakuza 0 (638970) / Yakuza Kiwami (834530) / Yakuza Kiwami 2 (927380) | `docs/research/YAKUZA-EXPANDED-2026-10-23.md`, `docs/research/YAKUZA-KIWAMI-2026-10-23.md` | Brawler movesets, Heat actions, Dragon Engine animation/ragdoll | NONE — no Yakuza move bank in the library; no character claims Yakuza as base |
| Gang Beasts (285900) | `docs/research/GANG-BEASTS-PHYSICS-2026-10-23.md` | Active ragdoll physics (with Human Fall Flat / Euphoria as comparators) | NONE — physics reference, not moves; no character claims Gang Beasts as base |
| Nioh 1/2 | `docs/research/NIOH-SYSTEMS-2026-10-23.md`, `NIOH2-SYSTEMS-2026-10-23.md`, `RE-GEOMOD-NIOH2-PLAN-2026-10-23.md` | Systems research | NONE |
| Def Jam: Fight for NY | `docs/research/WWE-CAW-EXTRACTION-STATUS.md` §4 | Models + motion data (`WRES_ALL.VIV`) extracted, mesh decode (SHPS) still open RE work; contributes fight-system findings (grappling core, styles), not creation parts | NONE for moves until SHPS decodes |
| Dead or Alive | (bank only) | `banks/doa.json`: 146 moves, 6 source banks; movesets `doa-ayane.json` (23), `doa-bass.json` (22), `doa-hayabusa.json` (18), `doa-jannlee.json` (21), `doa-kasumi.json` (20), `doa-tina.json` (26) | Bank-level only; DOA characters are reference movesets, not WH roster bases in this batch |
| Street Fighter (general) | (movesets only) | `sf-akuma.json` (168), `sf-blanka.json` (37), `sf-ryu.json` (34), `sf-ken.json` (32), `sf-vega.json` (36), `sf-zangief.json` (36), plus Akuma-pattern translations (Cammy 10, Chun-Li 10, Dhalsim 10, Guile 11, M. Bison 12, Sagat 10) | Reference only, except Twelve/Eleven for Zen (§1) — and those Twelve rows are UNMAPPED for clips |
| Urban Reign / SoulCalibur / Bloody Roar | (pending banks only) | `pending_banks`: `urban_reign` ("pending — PPK binary RE"), `soulcalibur` ("pending — approved systems only"), `bloody_roar` ("pending — beast transformations") | NONE |

**Do NOT download large files for this section.** Sources and file lists are recorded above; no game ISO, pak, or depot was downloaded in this batch, and none should be downloaded to this VM for research purposes.

---

## 6. Batch wiring plan — what lands where, in what order

Order is by "already has exact file wiring" first, so the batch ships usable Creator data instead of stacking UNMAPPED items:

1. **No Mercy bank → Move List Creator (VM-doable now).** Add `input_lp` to all 4,153 input-bearing rows by the fixed numeric mapping (§3), preserving bracketed conditions verbatim. Keep the 256 input-null rows out (UNMAPPED). Creator test per row: `id` + `input_lp` + `provenance.mk_slot_eligibility` + `anim_ref` all present. Estimated fields (`damage`, `hit_level`, `limb`, `startup/active/recovery`) stay flagged in `provenance.estimated` and are never presented as extracted.
2. **T3 banks → already wired; audit, don't rebuild.** Chatur (divmot14_ogre), Dorowani (divmot19_gon), Tobi (Hwoarang) keep their bank+row wiring. Audit step: confirm each moveset entry's `anim_ref` resolves to a row in `banks/t3.json` (4,648 rows) — any entry that does not resolve becomes UNMAPPED, not "closest row."
3. **VF5 federation conversions → keep as conversion labels, do not upgrade to decoded clips.** Jeffry/Wolf/El Blaze/Lei-Fei rows keep their `vf:*` refs with their federation-conversion provenance. When VF5 motion lands, replace `vf:*` refs row by row with real motion-clip refs only where the input, limb, and move identity match exactly.
4. **Zen true moveset → MADE specs first, Dural motion second.** Author MADE specs (labelled MADE) for the 25 `wh_true_moveset` entries from their documented inputs/descriptions, starting with stance (Dural stance + Twelve dancing idle, as separate layers, not blended) and X.C.O.P.Y. (ONE super, input d, d/f, f, d, d/f, f+LP1+RP2). Keep every `anim_ref: null` until a real clip or a MADE spec exists — never backfill with a Heihachi row.
5. **Megami/Menajerii TTT2 → MADE core + documented movelist now, decoded clips via delegation (§8).** Keep the 155 TTT2-labelled Megami rows and the 193 Menajerii rows as input/damage data. Keep the 149 `t8:` Megami rows EXCLUDED from Creator TTT2 wiring (flag them in the Creator as "excluded source — do not wire"). Extend the MADE specs on `main` (`game/assets/anim/made/megami/`) to cover Izumo follow-ups and the remaining TTT2 strings, labelled MADE with NEEDS-SPEC timing where the movelist gives no startup.
6. **WMXIX → hash-set mapping only.** Do not assign inputs or names. The single next step is the TEARDOWN.md §5 open item: per-clip hash-set → move-category mapping for the 169 registered clips. Until that lands, WMXIX rows stay out of the Creator.
7. **WWE 2K / T6 / T5 → delegation + inventory only (this VM).** No bank exists, so no Creator wiring is claimed. The VM-doable steps are: (a) locate and verify the `wwe2k19-animation-packs-v1` release as a bank file or record it as UNVERIFIED (see §3); (b) inventory the T6 ISO file list / DATA401.IDX header from existing xref output; (c) record owner assignments for any T6/T5 character before any extraction is attempted.

### Move List Creator field contract (applies to every row above)

A Creator move is complete only when all of these are present in the file, with these exact field names:

- `input` (file verbatim, numeric Tekken form) + `input_lp` (LP1/RP2/LK3/RK4 display form, fixed mapping, conditions preserved).
- `anim_ref` — one of: `t3:<bank>:row:<n>`, `vf:<fighter>/<move>` (conversion label only), `teardown/<game>/animations/<clip>` (verified clip path), `wh:<fighter>:<move>` (placeholder — Creator shows "clip not authored"), `made:<source>:<move>` (MADE spec — Creator shows "MADE, not decoded"), or `null` (UNMAPPED — Creator shows "no clip").
- `provenance` — `source_file` + `source_key` (or bank `id` + `mk_move_id` / `wmxix_move_id`), plus `estimated` list for any estimated field.
- NEVER a `t8:` value. NEVER a WMXIX provisional label as `name` without its `name_status` field alongside it. NEVER a T3 proxy row presented as the true game's clip (label the proxy as proxy: e.g., Cain Elias rows are "T3 King proxy for a WWE concept," not "WWE moves").

---

## 7. What is UNMAPPED — consolidated (no guessing, no filler)

- Zen: Dural stance clip, Dural idle/movement clips, all 25 true-moveset clips, Twelve 2D→3D conversion clips, Eleven distinct moves (Eleven has none — concept only, see §1).
- Megami: all TTT2 Jun clips (151 entries with no `anim_ref`; the other 153 `anim_ref` values are 149 EXCLUDED `t8:` refs + 4 `wh:` placeholders). TTT2 startup frames for most moves (movelist gives damage/hit level, not startup).
- Menajerii: all TTT2 Roger Jr. clips (186 entries with no `anim_ref`; 3 T3 Kuma proxy rows are not Roger Jr. clips).
- WWE 2K19/2K20/2K22: entire 2K move library (no bank file on `main`). WWE 2K26: ownership itself UNVERIFIED (not in STEAM-LIBRARY.md).
- WMXIX: move identity + inputs for all 169 clips.
- No Mercy: inputs for 256 rows (`input: null`).
- T6: entire T6 move library (encrypted DATA401.IDX, no decoded bank, no assigned character).
- T5: entire T5 library (no bank, no assigned character).
- Fire Pro / Yakuza / Gang Beasts / Nioh / Def Jam: entire move libraries for WH Creator purposes (systems research only).

---

## 8. BROWSER DELEGATION NEEDED — exact URLs and tasks for a live-browser session

This subagent cannot operate a live browser or sign into sites, and no browser visit is claimed in this document. The items below need a parent live-browser session (sign-in/download where noted). Each item states exactly what to get and where it lands; nothing here is a waiting state for this plan — the VM-doable steps in §6 proceed without these.

1. **TTT2 Jun movelist (text reference, no sign-in).**
   - URL: https://tekken.fandom.com/wiki/Jun_Kazama/Tekken_Tag_Tournament_2_Movelist
   - Get: the full TTT2 Jun movelist (throws, strings, GEN/IZU follow-ups, damage, hit level) as a saved page/file, and confirm it matches the 304 entries already in `game/assets/movesets/megami.json` (notably the 155 TTT2-labelled rows). Land the saved copy under `docs/research/` with its URL and fetch date. This does NOT give clips or startup frames.
2. **TTT2 Roger Jr. movelist (text reference, no sign-in).**
   - URL: UNVERIFIED in this batch — fetch the Tekken Wiki TTT2 Roger Jr. movelist page by searching that site for "Roger Jr. / Tekken Tag Tournament 2 Movelist" and record the exact URL found. Do not guess the URL slug.
   - Get: same as item 1, checked against the 193 entries in `game/assets/movesets/menajerii.json`.
3. **TekkenMovesetExtractor (Tag2 via CEMU path — Windows + CEMU + TTT2 Wii U required).**
   - URL: https://github.com/Kiloutre/TekkenMovesetExtractor/releases
   - Get: the release build + its Tag2/CEMU instructions (set `cemu_base` / `cemu_p1_addr` in `game_addresses.txt` per the tool docs, then export Jun from a running TTT2 Wii U session under CEMU). Land exports as a TTT2 Jun bank (moveset JSON + animation clips) with a README naming game version/platform, tool version, and every move/clip that could NOT be extracted. This VM cannot run CEMU/Windows, so this item is delegation-only.
4. **WWE 2K22 character-data structure (community tutorial, no sign-in stated).**
   - URL: https://smacktalks.org/forums/topic/77748-tutorial-character-data-1-the-charactermapping-file-in-wwe-2k22/
   - Get: the `charactermapping.jsfb` / `bakedfile00.cak` / Caketools procedure for 2K22, and confirm which 2K22 files hold the Create-A-Moveset slot structure (categories, slot positions, move library) that the Creator needs. Land notes under `docs/research/` — do not download game files through the browser.
5. **WWE 2K19 modding suite (community tool, Windows).**
   - URL: https://github.com/2KLive/Genesis
   - Get: the Genesis release + user guide (moveset editor: 18 move categories; pofo editor; `.pac` import with chunk regeneration) and assess whether its moveset export format can be converted to the §6 Creator field contract. Windows-only; delegation-only for any run against game files.
6. **Steam game files (sign-in required — do NOT attempt from this VM).**
   - Titles (app ids from `docs/tech/STEAM-LIBRARY.md`): WWE 2K19 (817130), WWE 2K20 (1015500), WWE 2K22 (1255630), Fire Pro Wrestling World (564230), Yakuza 0 (638970), Yakuza Kiwami (834530), Yakuza Kiwami 2 (927380), Gang Beasts (285900).
   - Get (one title at a time, selective files only — never a full depot to this VM): for WWE 2K22 first, the Create-A-Moveset data files (moveset/slot structure + move library) and, for the creation suite, the `pac/edit/**` parts census files. For TTT2, the Wii U title + Title Update path needed for item 3 is a separate acquisition decision (TTT2 is not a Steam title in STEAM-LIBRARY.md — do not assume a Steam path for it).
   - Land: converted bank files + a README (game version, tool used, gaps) in the private reverse-engineering repo area used for game-derived data, NOT as raw game files in the public western-heart repo.
7. **VF5 full-archive inventory (no sign-in, archive listing only).**
   - Source: the `vf5-500m` split archive referenced in `docs/research/VF5-MOTION-GAP-2026-10-22.md` (8 parts, 4GB, high-entropy, not fully pulled).
   - Get: a file listing (names/sizes only) to determine whether any motion files exist in that archive. Do NOT download the full 4GB to this VM. If the listing shows no motion files, record that as the closure of the archive-search path in §1.
8. **Verify the `wwe2k19-animation-packs-v1` release (locate, do not assume).**
   - Source: referenced in `docs/research/WWE-CAW-EXTRACTION-STATUS.md` as "Moves/entrance animation data for 2K15–2K20 is already secured (wwe2k19-animation-packs-v1 release)."
   - Get: the release location, its file list, and whether it contains row ids + inputs + clip paths convertible to the §6 Creator contract. If it cannot be located, record it as UNVERIFIED and keep 2K19 at UNMAPPED. Do not cite it as a bank until verified.

## Sources cited (all verified in this batch unless marked UNVERIFIED)

- Repo files on `main` (via data API): `game/data/moveset-library/index.json`, `game/data/moveset-library/banks/wrestling.json`, `banks/wmxix.json`, `banks/vf5.json`, `banks/t3.json` (via index), `game/assets/movesets/index.json`, `game/assets/movesets/megami.json`, `zen.json`, `menajerii.json`, `cainelias.json`, `vf-elblaze.json` (via bank provenance), `game/js/fighter.js` (zen: null), `game/assets/anim/made/megami/README-MADE.md`, `docs/research/VF5-MOTION-GAP-2026-10-22.md`, `docs/research/VF5-FULL-INTEGRATION-2026-10-22.md`, `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`, `roster/zen/CANON.md`, `docs/tech/STEAM-LIBRARY.md`, `docs/research/RE-WWE2K22-PLAN-2026-10-23.md`, `docs/research/WWE-CAW-EXTRACTION-STATUS.md`, `docs/research/FIRE-PRO-SYSTEMS-2026-10-23.md`, `docs/research/YAKUZA-EXPANDED-2026-10-23.md`, `docs/research/GANG-BEASTS-PHYSICS-2026-10-23.md`.
- Public web (text search/fetch only, no browser visit claimed): Tekken Wiki TTT2 Jun movelist (URL in §8 item 1); TekkenMovesetExtractor Tag2/CEMU documentation (release URL in §8 item 3); SmackTalks 2K22 charactermapping tutorial (URL in §8 item 4); Genesis 2K19 suite (URL in §8 item 5); SuperCombo Twelve archive and Street Fighter Wiki Eleven and Video Game Characters Database Dural (URLs as recorded in `zen.json` `wh_true_moveset.sources`).
- UNVERIFIED in this batch (explicitly not used as wiring): TTT2 Roger Jr. movelist URL; WWE 2K26 ownership; `wwe2k19-animation-packs-v1` release location/contents as a bank; VF5 `vf5-500m` archive contents (motion presence); the "22 T3 banks" figure (index says 20).
