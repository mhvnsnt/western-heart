# Steam pull corrections — coordinator correction, 2026-10-24 (Lane 7 addendum)

This file amends Lane 7 PRs #1051 (priority), #1052 (wrestling), #1053 (rest). It does not
edit any pack file and does not duplicate any other lane's work. It builds on the GPU-extract
lane's per-file table at ~/workspace/gapfill-20261024/gpu-extract/reports/PER_FILE_TABLE.md —
read that table for the full per-file record; this file records only what changes for Lane 7.

Button names: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick =
Tekken 3, RK4 = Right Kick = Tekken 4.

## 1. frv / dnc are LANDED sources, not open work

- CORRECTION (verified via GitHub API by this lane, 2026-10-24): game-reverse-engineering
  PR #61, "T7 Steam: Master Raven (frv/Pond) + Lucky Chloe (dnc/Ryusan) movesets converted to
  JSON", is CLOSED + MERGED 2026-10-24T21:41:46Z. It is NOT open.
- Effect on Lane 7: the tekken7 pack in PR #1051 described frv.json / dnc.json as teardown-lane
  outputs. Read them instead as LANDED sources: frv.json (Raven, 2,338 moves, 11,573 cancels in
  the raw table count; per-move cancel sum 11,590 by the documented motOrigin-duplication rule)
  and dnc.json (Chloe, 2,183 moves, 10,034 cancels raw / 10,051 per-move). Do NOT re-open, redo,
  or duplicate frv/dnc conversion. The remaining frv/dnc blocker is unchanged and narrow:
  bank-0x8000 clip bytes (frv 1,593 moves / 911 distinct refs; dnc 1,527 moves / 910 distinct
  refs) — anim_ref minus 0x8000 is the key; unblock in order: (1) live-game memory via Kiloutre
  TKMovesets, (2) pakchunk supply plus an AES key via a secure channel. Never substitute
  another bank's clips.
- Related guardrail from the same table: the teardown tree has TWO mot.bin paths with identical
  sizes pair-for-pair (teardown/tekken7-steam/tkdata/mothead/bin/ AND teardown/tkdata/mothead/bin/);
  content identity (SHA) between the two copies was NOT verified — use the tekken7-steam path
  only and never parse both copies as different characters.

## 2. TTT2 Jun — transcribed, motion NOT extracted

- TTT2 Jun movelist: 97 moves transcribed at movelist level (name + command + damage + hit
  range) to ~/workspace/ttt2-jun/ttt2-jun-lp-rp-lk-rk.json. Wire status: PARTIAL only — a patch
  resolving 97 entries to existing entries plus 5 genuinely-missing input slots; startup, block,
  hit and counter-hit frames are all UNMAPPED.
- Motion clips: NOT extracted. Only route: Kiloutre TTT2 path under CEMU Wii U (coordinator
  browser / CEMU delegation, GitHub or Google tap-to-sign-in only where a sign-in is required).
  LukzB T7-adaptation files are WITHDRAWN and segregated — never used as TTT2 data.
- Effect on Lane 7: TTT2 is a pending bank in the moveset-library index, not a Steam-owned title
  in this lane's packs. No Lane 7 pack claims TTT2 Jun motion. When CEMU clips land, they wire
  through the TTT2 pending bank, not through a Steam pull pack.

## 3. VF5 Dural — frame rows transcribed, motion NOT deciphered

- VF5 Dural REVO frame data: 194 entries transcribed from the official skill chart p.1 to
  ~/workspace/vf5-dural/vf5-dural-revo-frame-data.json. Wire status: PARTIAL only — direction
  prefixes UNMAPPED on all 194, VF damage kept raw with WH damage null, and the P/K/G to
  LP1/RP2/LK3/RK4 map is PROPOSED only. REVO p.2 directional table was not retrieved.
- Motion: NOT deciphered. mot_DUR.bin was probed: 8,078,704 bytes, entropy 6.653, no magic
  (no MOTA / MVLT / TKM2 / FARC), no _wj bone strings — a packed/encoded payload, format TBD.
  No public VF5 extractor, rip, or container was found. Bone names (49, j_ / kl_ / n_ / _wj)
  are known from obj.bin SKIN blocks, not from this blob.
- Effect on Lane 7: VF5 is not a Steam-owned title in this lane's packs (it is already banked
  in the moveset library as vf/vf5). No Lane 7 pack claims VF5 Dural motion. Next step is a
  farc-container parse plus payload probe (GPU-extract lane Job 5), then a spec — never a decode
  claim before that.

## 4. WWE No Mercy / WMXIX + DOA — no public motion parser found

- WWE No Mercy / WMXIX banks: no public AKI motion-format parser found (web search returned
  reviews, guides, and ROM-hack community material only). WWE 2K22 CAW work in-repo is
  slots/editor data, not motion. Unblock: a supplied dump plus format reverse-engineering from
  scratch, probe first — never a claim that an AKI parser exists.
- DOA formats: no DOA motion container spec or extractor found. Search returned costume-mod
  AutoLink tooling plus unrelated COM3D2 .anm material — that material is NOT DOA data and
  must never be relabelled as such. Same probe-and-report rule as WWE.
- Effect on Lane 7: this CONFIRMS the wrestling PR (#1052) positions and tightens them. The
  No Mercy pack is a wire note for the already-banked 4,409-move catalogue (inputs present),
  not a motion pull. The WMXIX pack stays PROVISIONAL and unwired: 169 rows, 0 inputs, labels
  not real move names — and now, additionally, no public motion parser exists to fill the
  motion side. Any future WMXIX motion work starts from a supplied dump + probe, not from a
  tool claim in this lane.

## 5. What did NOT change

- No GPU job has run in either lane. No output in this addendum is a GPU result. Kaggle batch
  plans in PR #1051 remain prepared, not run.
- No commercial assets were extracted by Lane 7. Raw commercial files go only in the PRIVATE
  game-reverse-engineering repo, never in public western-heart.
- Canon, play-style, display-order, and proprietary-naming laws in the three PRs are unchanged.
