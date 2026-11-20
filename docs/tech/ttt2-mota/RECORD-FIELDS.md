# TTT2 motbin move records — field map

What the 0x70-byte move records in a character's data006 motbin actually
carry, as established by the S5 bank-data production (WH #1558/#1561
follow-up #3) and used by `tools/anim/ttt2_bank_rows.py`. Everything below
was validated empirically against the shipped join tables
(`join/roger-join.json`, `join/jun-join.json`) and the decoded clip data —
distributions over all 2,197 Roger grid records and 742 Jun join records,
plus the banked slot records whose in-game behavior is probe-verified.

## Layout

- Big-endian, 0x70-byte records.
- Block base = (file offset of the bracketed character name) − 0x20C; the
  string pool starts at base + 0x20C and its first string is the bracketed
  name itself (`[ROGER]`, `[JUN_KAZAMA]`). (The join files print a "block
  base" 4 bytes lower — that is the block header start; the pool-anchored
  base here is the one the section pairs and string offsets resolve
  against, validated by the join cross-check below.)
- Section (ptr, count) u32 pairs at base + 0x140 + 8i (19 pairs, T7 order:
  reactions, requirement, hitCondition, projectile, pushback,
  pushbackExtradata, cancel, groupCancel, cancelExtradata,
  extraMoveProperty, moveBeginningProp, moveEndingProp, move, voiceclip,
  inputSequence, input, unknownParryRelated, cameraData, throwCameras).
- Roger: the movelist is pair 12 (ptr 0x872C0, count 2197).
- Jun: the header pairs do NOT carry the movelist (pair 12 parses as
  garbage). The grid begins at block + 0xA2D7C — located by anchoring on
  record `sDm_IKAO_plB`'s (name, anim, ref) triple and validated: 742/742
  mapped jun-join records sit at grid index == join `i`.
- Roger join cross-check: 2,179/2,180 records at grid index == join `i`.
  The one exception is `Co_Dummy_375` (join i=0), a dummy record whose
  triple does not appear in the raw grid — a framing edge artifact of the
  join lane's parse, reported as unmapped by the production tool.
- Jun join cross-check: 742/749; the 7 unmapped are header junk (the
  bracketed name, build-date strings, `Male_CST2`, refs 0/32767).

## Fields (offsets from record start, big-endian)

| Offset | Type | Meaning | Evidence |
|---|---|---|---|
| +0x00 | u32 | flags word (0x8001 in the high half on most combat records; small values on movement) | distribution |
| +0x0C | u32 | (see +0x00 — the two swap roles by record class; not consumed) | — |
| +0x10 | u32 | (char_id << 16) \| (grid_index − 23); char_id Roger 19, Jun 42; low half increments exactly +1 per grid record | verified across stance/lk/rk/grab/sidestep/jump records of both motbins |
| +0x1C | u32 | airborne_start (with +0x20) | jump records in both motbins: B/F jumps (9, 38); neutral jump Roger (20, 36), Jun (14, 40); crouch transition (1, 27) |
| +0x20 | u32 | airborne_end | same |
| +0x28 | u32 | index < 1286 on 439 Roger records (−1 elsewhere) — fits the voiceclip section count (1286) exactly; probable voiceclip index | distribution |
| +0x40 | u32 | **first_active_frame** | punch family reads (10,10) repeatedly (Tekken jabs are i10); kicks (8,8), (13,13), (16,16), (16,17), (19,19); throws (10,10)–(15,17); movement/reactions 0. Roger grab Thrmv_B1_00 = (11,11), matching WH's measured 1+3 startup class |
| +0x44 | u32 | **last_active_frame** | same |
| +0x4C | u32 | name string (pool-relative) | join |
| +0x50 | u32 | anim name string (pool-relative) | join |
| +0x54 | u32 | anim_ref = (bank << 14) \| index | join (#1557) |
| +0x5C | u32 | **attack word + flags**: low 16 bits are the game's attack word (the values `attackLevelOfWord` in game/js/t3anims.js classifies: Roger strikes 0x217 mid ×110, 0x512 high ×35, 0x10F low ×25, …); **bit 0x400000 = the character's own throw** | throw bit set on exactly the throw records — Roger 15/15 (Thrmv*/ThrMv* incl. ThrMvBB2pt_R0), Jun 6/6, no others; every throw record carries word 0x512 (u32 0x400512). The (word & 0x807) == 0x800 class (tag grapples Co_2pt_*, escapes Esc_*, Co_sabalo*) does NOT set the bit — those are not the character's own throws |
| +0x60 | u32 | near-unique per record (2,184/2,197 nonzero, all distinct) — a per-record id/offset, not a section index | distribution |

Notes:

- Some records legitimately carry first_active = 0 despite being throws:
  Jun's Thrmv_B2_00i (her shipped 2+4 grab), ThrmvLB2_00i and the tag throw
  Thrmv_2ptN00 read (0, 0) — the paired non-`i` records carry the windows
  (ThrmvBB2_L0i (15, 17), ThrMvBB2pt_R0 (12, 14)). Production copies the
  record as-is; the engine falls back to its measured window for such
  clips, exactly as it did before hit_frames existed.
- One Roger record has first_active > last_active, and 11 have
  first_active beyond the decoded clip length (shared records whose
  windows reference a longer variant). Copied as decoded; counted in the
  bake reports' `sanity` block.

## Not cracked (honest gaps)

- **Damage.** A brute-force search over (section × candidate index fields
  {+0x14, +0x28, +0x2C, +0x60, +0x10 halves} × stride {8..40} × offset,
  u16 and u32) found no combination reproducing the probe-verified grab
  damage (35) with plausible lk/rk damages consistently. hit_frames.json
  carries no damage field in any bank (kuma included), so this does not
  block the format; WH damage continues to come from moveset data.
- **Cancel graph / branch buttons.** Roger's cancel section is pair 6
  (ptr 0x1E8E0, count 8726, ≈32 bytes/record against the next pair). The
  T7 40-byte cancel layout does not survive the u32-index compression —
  it parses as structured-but-wrong — and a statistical layout scan was
  inconclusive. The T3 production took button masks from branch commands;
  there is no TTT2 analog yet, so hit_frames buttons are 0 (unknown)
  except the four slot-identity inputs. This is S6's open item.
- **+0x14** (Roger: 448 nonzero, max 690, 449 unique; attacks/jumps carry
  it, stance/reactions read 0) is neither a cancel index (too sparse) nor
  a hitCondition index that survived cross-checks. Unidentified.
