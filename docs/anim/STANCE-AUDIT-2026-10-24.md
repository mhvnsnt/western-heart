# Stance Audit — Roster-Wide Fix (2026-10-24)

## Owner directive (verbatim)
> "some have incorrect stances per character and Canon but too many are sharing them in character select screen and during fights"

## Root cause
Stances come from the T3 animation bank bound via `bankIdFor(charId, movesetId)` in `game/js/fighter.js`. Two sharing mechanisms:

1. **Moveset sharing**: 14 characters share moveset `demonio`, 8 share `bryan`, 6 share `xiaoyu`, 4 share `heihachi`, 3 share `gunjack`, 2 share `king`. Characters not in the `FIGHTER_BANK` override map fall back to their moveset's bank via `SOURCE_TO_BANK`, so all sharers get the SAME stance clip.

2. **Null-bank fallback**: Characters whose moveset is not in `MOVESET_MAP` or `SOURCE_TO_BANK` get `null` from `bankIdFor`, so they fall back to the embedded near-static Idle (fight) or the shared CMU 14_01 guard (select screen, `stance-aim.js`).

## Banks on disk (22 T3 banks)
anna, armorking, bosconovitch, bryan, eddy, forestlaw_on_law, gon, gunjack, heihachi, heihachi_on_jin, hwoarang, jin, julia, king_on_pantera_leoman, kuma, law, lei, nina, ogre, paul, xiaoyu, yoshimitsu

## Full roster audit (58 characters)

### CORRECT — bank matches Tekken base (21)
| Char | Base | Bank | Notes |
|------|------|------|-------|
| pantera | King | king | Correct |
| phantom | Yoshimitsu | yoshimitsu | Correct |
| diablo | Heihachi | heihachi | Correct |
| skull | Bryan | bryan | Correct |
| retsu | Bryan | bryan | Correct |
| sha | Xiaoyu | xiaoyu | Correct |
| sakura | Xiaoyu | xiaoyu | Correct |
| rin | Jin | jin | Correct (demonio IS Jin per canon) |
| demonio | Jin | jin | Correct |
| samura1 | Jack-7 | gunjack | Correct-ish (gunjack = Jack bank) |
| awapop | Nina | nina | Via FIGHTER_BANK override |
| torch | Anna | anna | Via FIGHTER_BANK override |
| kingtyrant | Eddy | eddy | Via FIGHTER_BANK override |
| kai | Eddy | eddy | Via FIGHTER_BANK override |
| tou | Paul | paul | Via FIGHTER_BANK override |
| gyou | Hwoarang | hwoarang | Via FIGHTER_BANK override |
| rave | Lei | lei | Via FIGHTER_BANK override |
| yukihyo | Armor King | armorking | Via FIGHTER_BANK override |
| nightwolf | Julia | julia | Via FIGHTER_BANK override |
| chatur | True Ogre | ogre | Via FIGHTER_BANK override |
| dorowani | Gon | gon | Via FIGHTER_BANK override |
| menajerii | Roger Jr. | kuma | Via FIGHTER_BANK override (Roger shares Kuma bank) |
| gashadokuro | Kuma | kuma | Via FIGHTER_BANK override |
| aotsuki | Panda | kuma | Via FIGHTER_BANK override (Panda shares Kuma bank) |
| zen | Heihachi* | julia | CONFLICT (see below) — RESOLVED 2026-10-24 by PR #1019: zen -> UNMAPPED (null). |

### FIXED IN THIS PR (3) — banks existed, overrides missing
| Char | Base | Was | Now | Notes |
|------|------|-----|-----|-------|
| docfrank | Bosconovitch | gunjack (WRONG) | bosconovitch | Bank exists on disk; was on gunjack bank |
| tobi | Hwoarang | null (CMU fallback) | hwoarang | Bank exists; was returning null |
| buffalo-bill | Marshall Law | null (CMU fallback) | law | Bank exists; was returning null |

### KEEP — do not change per user directive (2)
| Char | Base | Bank | Notes |
|------|------|-----|-------|
| zui | Steve Fox | jin (via demonio) | USER 2026-10-24: "he can keep that" — hands-up drunken stagger stance. DO NOT CHANGE. |
| cyborgx | Alisa | gunjack + explicit stanceClip | Has explicit `stanceClip: 'assets/anim/oss/cyborgx/stance.glb'` (CMU 13_17 boxing guard). DO NOT CHANGE. |

### APPROXIMATE — bank is kit's bank, not exact base (1)
| Char | Base | Bank | Notes |
|------|------|-----|-------|
| silvertongue | Lili | xiaoyu | Per lili.json t3_source: "her kit's T3 bank". Lili has no decoded bank; xiaoyu is the kit's bank, not Lili's own. Documented as APPROXIMATE, not exact. |

### UNMAPPED — no decoded bank for Tekken base (29)
These characters currently share a bank (via moveset fallback) or use CMU fallback. Their TRUE stance is BLOCKED on bank decoding. Sharing is a known gap until their bank lands.

| Char | Base | Current bank (shared) | Unblock path |
|------|------|----------------------|--------------|
| kinpo | Asuka | jin (shared) | T3 Asuka bank decode, or T7 Asuka extraction |
| waterfall | Josie | jin (shared) | T3 Josie bank decode, or T7 Josie extraction |
| burger | Bob | bryan (shared) | T3 Bob bank decode, or T7 Bob extraction |
| scimitar | Shaheen | jin (shared) | T3 Shaheen bank decode, or T7 Shaheen extraction |
| purplerain | Lee | jin (shared) | T3 Lee bank decode, or T7 Lee extraction |
| dio | Akuma | heihachi (shared) | T3 Akuma bank decode, or T7 Akuma extraction |
| michiko | Katarina | jin (shared) | T3 Katarina bank decode, or T7 Katarina extraction |
| star | Christie | xiaoyu (shared) | T3 Christie bank decode, or T7 Christie extraction |
| bruno | Miguel | bryan (shared) | T3 Miguel bank decode, or T7 Miguel extraction |
| negativo | Negan | bryan (shared) | T7 Negan extraction (Negan is T7 DLC, no T3) |
| thor | Ganryu | bryan (shared) | T3 Ganryu bank decode, or T7 Ganryu extraction |
| slice | Dragunov | bryan (shared) | T3 Dragunov bank decode, or T7 Dragunov extraction |
| baek-master-white | Kevin | bryan (shared) | Kevin is non-Tekken (Virtua Fighter); needs VF extraction or MADE stance |
| mariposa-monarch | Zafina | xiaoyu (shared) | T7 Zafina extraction (Zafina is T7 DLC, no T3) |
| pond | Raven | null (CMU) | T7 Raven (frv) mot.bin decoded at move level (PR #61); clip bytes need Grok's box / live memory |
| ryusan | Lucky Chloe | null (CMU) | T7 Chloe (dnc) mot.bin decoded at move level (PR #61); clip bytes need Grok's box / live memory |
| megami | Jun | null (CMU) | Jun is TTT2, not T7. Needs TTT2 Jun extraction or MADE stance |
| chordz | Lars | null (CMU) | T3 Lars bank decode, or T7 Lars extraction |
| byou | ??? | jin (shared) | Base UNCLEAR: nine-souls appendix said Lei, but owner 2026-10-21 clarified "Lei is Rave, not Byou". Owner must name Byou's base. |
| dxmmii-patchwork | Mokujin | jin (shared) | Mokujin mimics others (MIX PER CANON); stance should mimic per canon, not fixed |
| charger | Blanka | bryan (shared) | Blanka is non-Tekken (Street Fighter); needs SF extraction or MADE stance |
| kronos | Zangief + Golem | king (placeholder) | Non-Tekken; king bank is placeholder, not correct. Needs MADE stance or SF extraction |
| deathfang | Iori Yagami | heihachi (placeholder) | Non-Tekken (KOF); heihachi bank is placeholder. Needs MADE stance or KOF extraction |
| ryuji | Ryuji Yamazaki | null (CMU) | Non-Tekken (Fatal Fury/KOF); needs MADE stance or extraction |
| vainabel | Bass Armstrong | null (CMU) | Non-Tekken (DOA); needs MADE stance or DOA extraction |
| koreshi | Kakashi + Super Saiyan | heihachi (placeholder) | Non-Tekken; heihachi bank is placeholder. Needs MADE stance |
| cainelias | Undertaker (WWE) | king (placeholder) | Non-Tekken (WWE); king bank is placeholder. Needs WWE extraction or MADE stance |

### NOT IN ROSTER (1)
| Char | Notes |
|------|-------|
| Ash (Ashes from Ashlane) | NOT in western-heart roster. User 2026-10-24: "User likes Ash's stance, but Ash can have the 'lost stance' instead for his canon." Lost stance = stance fitting Lost Soul / lost-wandering canon. Guidance recorded here for when Ash is added to the roster. Use Ash's liked stance as reference, but assign lost stance per canon. |

## Sharing groups BEFORE this fix
- jin bank: rin (correct), demonio (correct), byou, zui (KEEP), kinpo, waterfall, scimitar, purplerain, michiko, dxmmii-patchwork = 10 chars
- bryan bank: retsu (correct), skull (correct), burger, bruno, negativo, thor, slice, baek-master-white, charger = 9 chars
- xiaoyu bank: sha (correct), sakura (correct), star, mariposa-monarch, silvertongue (APPROX) = 5 chars
- heihachi bank: diablo (correct), dio, deathfang, koreshi = 4 chars
- gunjack bank: samura1 (correct-ish), cyborgx (KEEP), docfrank (FIXED to bosconovitch) = 3 chars
- king bank: pantera (correct), kronos, cainelias = 3 chars

## Sharing groups AFTER this fix
- gunjack bank: samura1, cyborgx (KEEP) = 2 chars (docfrank left)
- All other groups unchanged (UNMAPPED characters still share until their banks land)
- tobi and buffalo-bill now have their OWN banks (hwoarang, law) instead of null/CMU shared fallback

## User-specific stance guidance (2026-10-24)
1. **ASH**: Likes Ash's stance, but Ash can have "lost stance" for canon. Ash not in roster yet; guidance recorded above.
2. **ZUI**: KEEP hands-up drunken stagger stance. DO NOT CHANGE.
3. **MIX PER CANON (standing rule)**: Some characters get moves from MULTIPLE Tekken fighters mixed together, based on canon — not just one base fighter. This applies to stance as well: for mixed characters, stance comes from primary base or canon, not from a single moveset. Examples: dxmmii-patchwork (Mokujin mimics), kronos (Zangief + Golem), koreshi (Kakashi + Super Saiyan). For these, stance is MIX, not single-bank.

## ZEN conflict (flagged for owner)
- roster-full.js: Zen base = Heihachi
- FIGHTER_BANK: zen -> julia (nine-souls appendix: ZEN's vessel base = Julia)
- CANON.md appendix: Julia -> NIGHTWOLF / soul ZEN as unresolved three-way conflict
- Current: kept julia per existing override. Owner must resolve: is Zen's stance Heihachi's or Julia's?
- RESOLVED 2026-10-24 (owner decision, PR #1019, docs/decisions/2026-10-24-zen-base-decision.md): Zen is NEITHER Heihachi NOR Julia. Base chain: Eleven/Twelve (SF, 2D concept) -> Dural (VF5, 3D implementation) -> Zen's own canon moves on top, X.COPY as ONE super. FIGHTER_BANK zen is now null (UNMAPPED) because no Dural bank exists in the repo yet. The "Does NOT resolve Zen conflict" line under "What this PR does NOT do" below describes PR #1016's scope only; it is superseded for Zen by PR #1019.

## What this PR does
1. Adds 3 FIGHTER_BANK overrides (docfrank, tobi, buffalo-bill) — each gets its own base's bank, distinct stance, no longer shared or null.
2. Documents full audit (this file) — every character, current bank, correct bank, status, unblock path.
3. Documents Zui KEEP, Ash guidance, MIX PER CANON principle, Zen conflict.

## What this PR does NOT do (honest gaps)
- Does NOT fix UNMAPPED characters' sharing — their banks don't exist on disk. Fixing requires T3/T7/TTT2 extraction or MADE stances, which are separate lanes.
- Does NOT change Zui or Cyborgx stances (per user KEEP directive).
- Does NOT resolve Zen conflict (needs owner decision).
- Does NOT add Ash to roster (Ash not in western-heart; guidance recorded for future).

## Verification
- Code: FIGHTER_BANK overrides added, syntax verified by reading edited file.
- Simulation: bankIdFor('docfrank', 'gunjack') now returns 'bosconovitch' (was 'gunjack'); bankIdFor('tobi', 'tobi') now returns 'hwoarang' (was null); bankIdFor('buffalo-bill', 'buffalo-bill') now returns 'law' (was null).
- Live playtest still owed: select screen must show distinct stances for docfrank, tobi, buffalo-bill; fight idle must show distinct stances. Owner verifying by playing is the final step.


## Follow-up 2026-10-24 (T3 stance gap lane)

Scope of this entry: the 29 UNMAPPED characters only. No code changed
in this entry's PR, no KEEP character touched, no stance clip added.

### Count reconciliation

This audit's UNMAPPED table has 27 rows. The lane total is 29:
27 + zen (moved to UNMAPPED by PR #1019, owner decision: Zen is
neither Heihachi nor Julia, FIGHTER_BANK zen is null) + ryuji-rock
(CORNERSTONE), a roster id in game/js/roster-full.js that this audit
never lists (audit covers 58 ids, the roster has 59). Sharing groups
today, corrected: jin 8, bryan 7, xiaoyu 2, heihachi 3, king 3,
null 6 = 29.

### Headline: fixable NOW from an existing bank = 0 of 29

Every one of the 22 decoded banks under game/assets/anim/t3/ was
checked against every UNMAPPED base (bank ids, FIGHTER_BANK,
SOURCE_TO_BANK, moveset index sources, and each bank's
t3_neutral.json idle clip). No UNMAPPED character's own base has a
bank on disk, and FIGHTER_BANK holds no entry for any of them
except zen: null (intentional). There is therefore no valid
mapping-only fix, and this PR deliberately makes NO FIGHTER_BANK
change: wiring a cousin bank (Lei for Lee, Eddy for Christie,
Heihachi for Akuma) as if it were the character's own would repeat
the sharing error. The idle clip is t3_neutral.json (slot 0x3,
looped); t3_stance.json is the round-start intro (slot 0x0), not
the idle.

### Corrections to this audit, verified on main

- chordz is NOT null: chordz.json and the moveset index both give
  t3_source jin, so chordz shares the jin stance. It joins the jin
  group (8, not 7).
- "T3 X bank decode" is impossible for most rows: Asuka, Raven,
  Dragunov debuted in T5; Bob, Miguel, Lars, Zafina in T6; Josie,
  Shaheen, Katarina, Chloe, Negan, Akuma in T7; Christie in T4;
  Lee and Ganryu in T1/T2 (not T3); Jun in T2 (not T3). Their honest
  path is later-game extraction (T7 in almost every case, TTT2 for
  Jun), not a T3 bank. Only Mokujin is a genuine T3 case (below).
- baek-master-white base is CONFLICTED: roster says Kevin, moveset
  file says Baek. Owner input required before any target bank is
  named. Current bank bryan (shared) either way.
- byou index entry is STALE: it still says Lei Wulong, but the
  owner clarified 2026-10-21 that Lei is Rave, not Byou. Owner must
  name Byou's base.
- ryuji fight-path bank is call-site dependent (index: no source,
  null; roster moveset ryuji-rock names king as proxy). Either way
  it is NOT Yamazaki's own bank. Verify by playing; do not wire
  king as a fix.
- zen index entry is STALE but harmless: it still says Heihachi /
  anim_bank heihachi, while FIGHTER_BANK zen: null wins. Do not
  restore heihachi or julia without a new owner decision.

### Per-character status (29)

FIXABLE NOW: none. NEEDS T7 extraction (16): kinpo Asuka, waterfall
Josie, burger Bob, scimitar Shaheen, purplerain Lee, dio Akuma,
michiko Katarina, star Christie, bruno Miguel, negativo Negan,
thor Ganryu, slice Dragunov, mariposa-monarch Zafina, chordz Lars,
pond Raven, ryusan Lucky Chloe. NEEDS TTT2 extraction (1): megami
Jun (Jun is not playable in T7; the MADE specs hold NO stance pose,
and decoded clips must REPLACE them, not sit alongside them).
NEEDS T3 re-rip / TTT2 / MIX decision (1): dxmmii-patchwork Mokujin
— divmot15 is size-0 on the owner's disc (BNS entry 295); the
original-disc entry is 127,368 bytes; Mokujin mimics by canon, so a
fixed single stance needs an owner MIX decision. NEEDS non-Tekken
extraction or MADE stance (8): charger Blanka (SF), kronos Zangief
+ Golem (MIX), deathfang Iori (KOF), ryuji Yamazaki (KOF),
ryuji-rock Yamazaki + Rock (MIX), vainabel Bass (DOA), koreshi
Kakashi + Super Saiyan (MIX), cainelias Undertaker (WWE). NEEDS
VF5 Dural extraction or MADE stance (1): zen. OWNER INPUT (2):
baek-master-white, byou.

### Extraction spec for the T7 rows (so the lane needs no re-research)

Per character: Tekken 7, that character, neutral standing idle
clip (the standing guard loop — NOT the round intro, NOT a win
pose), delivered as a new bank dir game/assets/anim/t3/<target>/
with t3_neutral.json at minimum, wired by ONE FIGHTER_BANK line
once the bank exists and its idle is verified, then playtested on
select screen and in fight. Pond / ryusan shortcut: their T7
mot.bin files are already decoded at move level (PR #61: Raven
frv, Chloe dnc); only the idle clip bytes remain, via live-memory
export from a running T7. Future FIGHTER_BANK lines (DO NOT apply
until each target bank exists): kinpo asuka, waterfall josie,
burger bob, scimitar shaheen, purplerain lee, dio akuma, michiko
katarina, star christie, bruno miguel, negativo negan, thor
ganryu, slice dragunov, mariposa-monarch zafina, pond raven,
ryusan chloe, megami jun, chordz lars, dxmmii-patchwork mokujin,
zen dural.

### Batch verification (GPU script, local CPU run)

The lane's batch script verifies all 22 banks' idle clips in one
batched pass and prints the full 29-row matrix (PASS only if a
character plays its OWN base's bank). Local run in this lane:
torch is not installed on that VM, so it ran on CPU (pure-python
fallback) — a correctness run, NOT a GPU run. Result: bank idle
clips 18 PASS / 4 CHECK (lei, nina, eddy, bosconovitch — diagnostic
flags for the bank lane; none of the 4 banks is shared by any of
the 29); character matrix 0 PASS / 29 FAIL. The GPU run on the
2x Tesla T4 Kaggle notebook is still owed and must be reported as
such, not claimed from the CPU run. The script lives in the lane
workspace (kaggle_batch_stance_verify.py) with --fetch-remote and
--device cuda modes for the notebook run.
