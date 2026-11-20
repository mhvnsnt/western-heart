# Animation Bank Table — every fighter → base character → bank (2026-10-20)

Owner order (2026-10-20 ~21:50 CDT): *"Need to get the blanka clips from the
street fighter teardowns we have and same for Kronos with zangief and Koreshi
for vega etc, Iori for deathfang, wolf hawkfield for Nightwolf, Bryan fury for
Skull, Jack for SAM-UR-A1, bosconovitch for doc Frank, and so on, plus
anything else we've added from canon or these conversations, and Alisa for
Cape Jones, Steve Fox for zui, king for Pantera, armor king for Yukihyō, and
Bob for Burger, and so on."*

Owner standard (2026-10-20 ~21:59 CDT): the bar per fighter is at least the
Leo man level (King's animations playing on him, wired on main) — and banks
must draw from the NEWEST teardown sources we hold, not default to Tekken 3.
T3 is "really old and limited" next to Tekken 6/7/8 and the other torn-down
games. Every row below therefore records the bank's ERA; a fighter stuck on a
T3-only bank is flagged as a gap with the newer source that would fix it.

## How bank binding works (game/js/fighter.js `bankIdFor`, game/js/t3anims.js)

1. The fighter's moveset JSON `t3_source` (the provenance of its frame/move
   DATA) is mapped through `SOURCE_TO_BANK`. Per-fighter exceptions live in
   `bankIdFor` (the armor-king override from PR #405; the `FIGHTER_BANK` map
   added by this PR) for fighters whose DATA was built on a proxy table but
   whose canon base is a different character.
2. A bank provides the ACTION clips (stance, intro, light, medium, heavy,
   grab, block, hit, launch, ko, win, walks, dash, crouch, jumps, sidesteps)
   plus `rows.pack.json` — per-move clips keyed by T3 move row.
3. Per-move row clips are guarded (`_t3RowClipForMove`): a move's row clip
   plays ONLY when the move's own `t3_source` maps to the bound bank. Binding
   a fighter to their base's bank can therefore never play a third
   character's per-move clips; proxy-table moves fall back to the bank's
   generic actions until the moveset lane rebuilds them on the true table.
4. A fighter with no bank binding gets NO T3 actions (embedded locomotion +
   procedural) — never another character's clips (isolation doctrine).

## State after PR #405 (remainder banks) + this PR (row packs + overrides)

PR #405 landed the 9 remainder T3 banks (paul, lei, nina, hwoarang, eddy,
julia, anna, bosconovitch, armorking) with action clips + skeleton.json, and
fixed `SOURCE_TO_BANK` (bosconovitch → his own bank). This PR adds:
`rows.pack.json` for all 9 remainder banks (via tools/anim/t3_row_bake.py —
bosconovitch gets the FULL move-index bake, 647 rows, because Doc Frank is
the one fighter whose data is genuinely Bosconovitch-sourced: his action
clips are Bosco's own today, and his per-move clips fire the moment the
moveset lane stamps `t3_row` on his moves — verified 2026-10-20 that his
102 moves carry `t3_source` + `anim_ref` but NO `t3_row` yet, so today he
plays the bank's action clips; armorking gets the king-referenced rows
baked, and with the king/armorking family rule in `_moveRowAction` the
Armor King guest's and Yukihyō's king-sourced per-move clips DO fire on it;
the other 7 ship referenced-rows packs — currently zero WH movesets
reference their rows, because their fighters' data still sits on proxy
tables, so no per-move clip could fire for them yet regardless) and the
`FIGHTER_BANK` overrides in bankIdFor. FOLLOW-UP (one command, recorded so
it is never lost): when the moveset lane rebuilds a proxy fighter on their
true base table — or in any quiet compute window — run
`python3 tools/anim/t3_bake_packs.py <bank>` (added in this PR) to bake that
bank's full move-index pack; the rows then play with no further wiring.

### Correct own-bank, wired (era: Tekken 3 — newest COMPLETE bank we hold for these bases)

| Fighter | Base | Bank | Note |
|---|---|---|---|
| pantera | King | king_on_pantera_leoman | GOLDEN REFERENCE (Oct 14–15 setup) |
| demonio (+ rin, demonio forms) | Jin | jin | owner canon: Tekken's Jin = Demonio |
| skull (+ retsu) | Bryan Fury | bryan | owner's named case — already correct |
| samura1 | Gun Jack | gunjack | owner's "Jack for SAM-UR-A1" ✔ (T3-era Jack) |
| sakura (+ sha) | Xiaoyu | xiaoyu | |
| phantom (+ jin_soul) | Yoshimitsu | yoshimitsu | |
| diablo | Heihachi | heihachi_on_jin | Heihachi's own divmot13 on Jin's skeleton (his KMD lacks hip/shoulder verts); an own-rig decode also ships as `heihachi_ownrig` (PR #405) — switch is one line in T3_BANKS if the owner prefers it |
| armor-king (guest) | Armor King | armorking | PR #405 override; divmot03_king on King's own rig (AK has no T3 stream) |

### Fixed by this PR (binding changed)

| Fighter | Canon base | Bank before | Bank now | Era | Verdict |
|---|---|---|---|---|---|
| docfrank | Dr. Bosconovitch | gunjack (substitution) | bosconovitch (PR #405 source fix + this PR's full 647-row pack) | T3 | FIXED — owner's named case; he animates on Bosco's own action clips now, and the full pack is baked so his per-move clips fire as soon as the moveset lane stamps t3_row on his moves (0/102 carry it today — they carry t3_source + anim_ref only) |
| awapop | Nina Williams | jin | nina | T3 | FIXED (actions); her move DATA is still jin-table — moveset-lane rebuild on Nina's table activates her per-move clips (rows bake with the follow-up command above) |
| torch | Anna Williams | jin | anna | T3 | FIXED (actions); data still jin-table |
| kingtyrant | Eddy Gordo | xiaoyu | eddy | T3 | FIXED (actions); data still xiaoyu-table |
| kai | Eddy (KAI's vessel) | jin | eddy | T3 | FIXED (actions) |
| tou | Paul Phoenix (TOU's vessel) | heihachi | paul | T3 | FIXED (actions) |
| byou | Lei Wulong (BYOU's vessel) | jin | lei | T3 | FIXED (actions) |
| gyou | Hwoarang (GYOU's vessel) | jin | hwoarang | T3 | FIXED (actions) |
| zen | Julia Chang (ZEN's vessel) | heihachi | julia | T3 | FIXED (actions) |
| rave | Lei Wulong | xiaoyu | lei | T3 | FIXED (actions); data still xiaoyu-table |
| yukihyo | Armor King | king_on_pantera_leoman | armorking | T3 | FIXED — owner's named case; same King motion, now baked on King's own rig (matches his proportions, same rationale as PR #405's armor-king override); his 155 king-sourced move rows fire from the armorking pack via the king/armorking family rule in _moveRowAction (the Armor King guest, 125/125 king rows, gets the same) |
| nightwolf | Julia Chang (CANON) / Wolf Hawkfield (owner 2026-10-20) | xiaoyu | julia | T3 | INTERIM — see flag below |

**NIGHTWOLF FLAG (owner decision):** CANON.md locks Nightwolf's base to Julia
Chang; the owner's 2026-10-20 order names Wolf Hawkfield (Virtua Fighter) for
his clips. No VF motion data exists in any of our stores (G-VF below), so Wolf
cannot be wired today. He is bound to Julia (his canon base, bank exists)
instead of the previous Xiaoyu substitution. If the owner wants him left
unbound until VF motion is decoded, reverting is one line in
`FIGHTER_BANK` (game/js/fighter.js).

### Substitutions that REMAIN (all flagged; fixing source in the GAP register)

| Fighter(s) | Bound bank | Real base | Why / gap |
|---|---|---|---|
| charger, blanka, sf-blanka | bryan | Blanka (SF) | G-SF — no SF clips exist in our stores (proven, case #1) |
| kronos, kronos-attire2, zangief, sf-zangief, hugo, marduk | king_on_pantera_leoman | Zangief (SF) / Hugo / Marduk | G-SF for Zangief; Hugo = SF-line; Marduk = G-T6. King is the size-class stand-in, flagged |
| koreshi, vega, sf-vega | xiaoyu (koreshi/vega) | Vega (SF) | G-SF |
| deathfang, iori | heihachi | Iori Yagami (KOF) | G-KOF — no KOF game held at all |
| dio, sf-akuma | heihachi | Akuma (SF) | G-SF |
| sf-ryu, sf-ken | jin | Ryu / Ken (SF) | G-SF |
| zui | jin | Steve Fox | G-T6 — Steve debuts in T4; NO T3 Steve stream exists. Jin is a flagged stand-in, NOT his base |
| kinpo | jin | Asuka Kazama | G-T6/T7 — Asuka debuts in T5 |
| cyborgx (Cape Jones) | gunjack | Alisa Bosconovitch | G-T6 — Alisa debuts in T6; owner's named case, waits on the T6 PSP animation decode |
| burger, bob | bryan / jin | Bob | G-T6 — Bob debuts in T6 |
| star | xiaoyu | Christie Monteiro | G-T6 |
| slice | bryan | Sergei Dragunov | G-T6 |
| thor | bryan | Ganryu | G-T6 (Ganryu is in T3-era lore but has no T3 divmot stream in the 20 extracted) |
| bruno | bryan | Miguel Caballero Rojo | G-T6/T7 |
| michiko | jin | Katarina Alves | G-T7 only — no earlier source exists |
| scimitar | jin | Shaheen | G-T7 only |
| chordz | jin | Lars Alexandersson | G-T6 — Lars debuts in T6 |
| lili | xiaoyu | Emilie "Lili" de Rochefort | G-T6/T7 |
| negativo | bryan | Negan (T7 DLC) | G-T7 |
| sunra | heihachi | Pac-Man (T7 rig) | G-T7; his rig's DAE carries 0 clips (PR #275) |
| waterfall | jin | Josie Rizal | G-T7 |
| purplerain | jin | Lee Chaolan | G-T6/T7 (no T3 Lee stream) |
| baek (+ baek-master-white, kevin slot) | bryan | Baek Doo San | G-T6/T7 (no T3 Baek stream in the extracted 20) |
| dxmmii (+ dxmmii-patchwork) | jin | Mokujin | G-T5 — divmot15 is ABSENT from the disc (BNS 295, size 0, proven) |
| demonio-winged | jin (via deviljin) | Devil Jin | Family substitution, flagged: Devil Jin debuts T5 (G-T5) |
| doc-frank-hood, doc-frank-machine-shop, docfrank (forms) | gunjack | Dr. Bosconovitch | Doc Frank's FORM movesets were built on gunjack data (their own t3_source); base docfrank is fixed. Rebuilding the forms' data on Bosco's table is moveset-lane work |
| cainelias | king_on_pantera_leoman | Undertaker archetype | G-WRESTLE — No Mercy Undertaker clips exist (5,787 decoded) but were never retargeted to a WH bank |
| ryuji-rock | king_on_pantera_leoman | (rock form) | flagged stand-in; ryuji base file has no source data at all |
| heihachi-era note | — | — | Diablo's bank is T3-era; his T6/T7-era bank is G-T6/G-T7 |

### No bank bound (null → embedded/procedural; isolation doctrine — correct until their source exists)

vainabel (Bass/DOA + Kane archetype — G-DOA/G-WRESTLE) · mariposa (Zafina —
G-T6/T7) · ryuji (no source data) · burger-demon / burger-speed-demon /
burger-the-mouth (Kusaregedo forms — SamSho is sprite data, no bone-clip
source exists) · doa-kasumi, doa-bass, doa-hayabusa, doa-ayane, doa-tina,
doa-jannlee (G-DOA) · vf-akira, vf-sarah, vf-kage (G-VF) · sf-cammy,
sf-chunli, sf-dhalsim, sf-guile, sf-mbison, sf-sagat (G-SF, no moveset source
data at all yet).
## GAP register — exact missing source per fighter (teardown sweep picks these up)

Nothing below is silently substituted. Where a substitute bank is bound today
it is listed in the substitution table above; where no bank is bound the
fighter runs embedded/procedural and is listed here.

### G-SF — Street Fighter animation data (CHARGER is case #1)
**Fighters:** charger + blanka + sf-blanka (Blanka), kronos-line + zangief +
sf-zangief (Zangief), koreshi + vega + sf-vega (Vega), sf-ryu/sf-ken/sf-akuma
+ the no-source SF guests (cammy, chunli, dhalsim, guile, mbison, sagat).
**Inventory (proven 2026-10-20):** NO decoded SF animation data exists in any
of our stores. `moveset-library/animations/ANIMATION-INDEX.json` lists no SF
source at all. The SF cast models on main are Sketchfab intakes — Blanka's is
documented STATIC (no skin) in
`teardown/street-fighter-5/CAST-STATUS.md` and
`teardown/street-fighter-3d-games/SF-TEARDOWN-STATUS.md`; they carry no clips.
**What DOES exist:** raw per-character animation data inside the SF EX Plus
Alpha PAC packages — `teardown/street-fighter-3d-games/extracted/ex-plus-alpha/PL/P00.PAC … P19.PAC`
(26 packs, on main) with chunk index `PAC-CHUNK-INDEX.json` (the extraction
README states the packs contain "TMD parts, TIM textures, animation data").
**Exact missing extraction:** (1) PAC container decode — the 44-entry chunk
table is anomalous (46/1144 entries out-of-range; chunk sub-headers unsolved;
already logged on the teardown idle queue as a dedicated RE pass);
(2) P-slot → character mapping confirmation (SEL2/name-table cross-check from
SLUS_005.48 still pending); (3) the PS1-era per-object animation format decode
+ retarget to the WH canonical 22 bones (SF EX models are segmented TMD, not
skinned — a converter does not exist yet). Newer-era alternative: SFV was
never acquired (needs owner purchase); USFIV / SF×Tekken discs not on disk
(13–17 GB, disk-gated). Until one lands, CHARGER keeps the flagged bryan
substitution — his moveset DATA is 100% Blanka (PR #392); only the clips lag.

### G-KOF — Iori / KOF animation data
**Fighters:** deathfang, iori.
**Inventory:** no King of Fighters game exists in any teardown store (no KOF
directory in game-reverse-engineering or western-heart/teardown). The only
Iori material held is the Sketchfab model + frame-data movesets.
**Exact missing source:** a KOF game acquisition + extraction (KOF XIV/XV are
the 3D entries whose Iori motion could retarget; 2D entries are sprite data —
not convertible to bone clips). Deathfang keeps the flagged heihachi
substitution meanwhile; his werewolf form's clips are the same bank (both
forms share his moveset family).

### G-VF — Virtua Fighter motion data
**Fighters:** nightwolf (owner: Wolf Hawkfield), realizzt (Brad Burns),
kutz (Goh Hinogami), vf-akira, vf-sarah, vf-kage.
**Inventory:** VF5 extraction is models-complete (`teardown/vf5`, release
vf5-model-library-v1) but NO VF motion data has ever been converted — the
ANIMATION-INDEX has no VF entry and WH conversion of VF5 models is itself
blocked (Windows 3ds Max pipeline per the scoreboard).
**Exact missing extraction:** VF5 motion file decode (the game's animation
containers were never RE'd by any lane) + a VF→canonical-22 retarget. This is
the source that would also satisfy the owner's Wolf-for-Nightwolf order over
the interim Julia binding.

### G-DOA — Dead or Alive animation data
**Fighters:** doa-kasumi, doa-bass, doa-hayabusa, doa-ayane, doa-tina,
doa-jannlee; vainabel's Bass-based attires ride along.
**Inventory:** DOA4 teardown is model-side (165 GLBs, PR #386); the PR #381
audit proved the "complete" claim false — the .anm/keystream side is
undecoded (five-oracle protocol defined, gate G5 open with the sweep lane).
**Exact missing extraction:** DOA4 animation container decode (in the sweep
lane's phase-3 scope). Until then the DOA guests have no bank — correct per
the isolation doctrine (no substitution).

### G-T6 — Tekken 6 (PSP) animation extraction — the single biggest unlock
**Fighters whose bases debut or live in T6:** zui (Steve Fox), kinpo (Asuka),
cyborgx (Alisa — owner's named case), burger (Bob), star (Christie), slice
(Dragunov), thor (Ganryu), chordz (Lars), bruno (Miguel), lili (Lili),
mariposa (Zafina), marduk (Marduk), baek/kevin-slot (Baek).
**Inventory:** T6 PSP teardown is ~90% — models, items, stages extracted —
but its ANIMATION data is documented "encrypted" in the ANIMATION-INDEX (the
46 decoded items are ending cinematics only). PPSSPP decrypted-EBOOT dump →
debugger trace → fit formula → known-plaintext verify is the proven method
(deep-research digest 2026-10-20); PR #388 (T6 PSP round 2) is the sweep
lane's active vehicle.
**Exact missing extraction:** the T6 PSP motion-stream decrypt + decode.
Every fighter above is stuck at T3-era-or-no bank until it lands; zui's
jin substitution and cyborgx's gunjack substitution are the two owner-named
cases it fixes.
**Lars/Chordz precision (2026-10-23):** `docs/anim/LARS-ANIM-GAP-20261023.md`
records the exact missing bank files (`game/assets/anim/t3/lars/`), the TTT2
STFS source + its four blockers (disk, safe-storage upload, STFS tooling,
format RE), and the unblock sequence. His moveset data is complete meanwhile
(469 moves, T7+T8 merged).

### G-T7 — Tekken 7 animation pipeline (does not exist)
**Fighters:** michiko (Katarina — T7-only base), scimitar (Shaheen — T7-only),
negativo (Negan — T7 DLC), yukihyo (Armor King T7-era bank; T3 fallback
wired), diablo (Heihachi T7-era bank), kinpo (Asuka T7-era), bruno (Miguel
T7-era), dio (Akuma is SF-side, G-SF).
**Inventory:** the ANIMATION-INDEX states it plainly — "Tekken 7: Full game
never acquired. Individual model rips have no animation data." The
tekken7-full-v1 release holds models (inside another repo's release), not a
motion pipeline.
**Exact missing extraction:** T7 game acquisition + its animation format RE
(UE4-era .uasset motion). No lane has started it; it is the deepest gap in
this table and the reason several "newest-era" verdicts cap at T3/T6.

### G-T5 — Mokujin (DXMMII) + Tekken 5-era banks
**dxmmii:** divmot15 (Mokujin's stream) is ABSENT from the owner's T3 disc —
BNS record 295 has size 0 (proven; docs/anim/T3-REMAINDER-BANKS-20261020.md
§4). No T3 Mokujin bank can ever be baked from this disc. Options the sweep
can pick up: TTT1/T5 Mokujin data if a future teardown holds it — until then
dxmmii keeps the flagged jin substitution (thematically Mokujin mimics the
cast; a per-match mimic binding is a game-design option for the owner, not a
silent default).
**Tekken 5:** extraction is present and complete per the T5 coordinator
(DATA1 = 1,571 files; decrypt verify + first model proof are the finisher
lane's), but no T5 animation bank has been baked for any fighter — T5-era
banks (e.g. Devil Jin for demonio-winged, Raven/Asuka-era sources) wait on
the T5 motion decode.

### G-WRESTLE — No Mercy / WMXIX motion (held, conversion unwired)
**Fighters:** cainelias (Undertaker archetype), vainabel (Kane archetype).
**Inventory:** 5,787 No Mercy clips ARE decoded (NPY, AKI skeleton) and 170
WMXIX clips (JSON, 70-bone Yukes) — the ANIMATION-INDEX's two biggest sets —
and an AKI→Tekken3 retarget is proven (aki_to_tekken3.py, used for King).
What is missing is the per-character step: nobody has retargeted the
Undertaker/Kane clip sets onto the WH canonical bank format or bound them.
That is conversion work on HELD data (no new extraction), sized like the
T3 remainder bake; the sweep or a follow-up bank lane can pick it up.

### G-OTHER — single-fighter gaps
- **waterfall** (Josie Rizal, T7): no Josie data held — G-T7 class.
- **purplerain** (Lee Chaolan): T6/T7-era base; T3 has no Lee stream — G-T6 class.
- **sunra** (Pac-Man T7 rig): PR #275's DAE carries 0 animation clips; his
  T7 rig motion is G-T7 class. Flagged heihachi substitution meanwhile.
- **dio** (Akuma): G-SF class (his model is a community rip with no clips).
- **burger forms** (Kusaregedo kit): Samurai Shodown VI is 2D sprite data;
  WORKLOG already records `anim_ref: samsho:kusaregedo/` "clips to be built
  from footage" — no bone-clip source exists; forms stay unbound.
- **ryuji / ryuji-rock:** ryuji has no source data at all (null). ryuji-rock
  rides king (flagged). Sourcing Ryuji's base data is a moveset-lane item;
  the bank follows the data.

## Era summary (owner's newest-era standard)

- Own-bank at the newest COMPLETE era we hold: 17 bank keys wired (16 T3 +
  armorking hybrid). For T3-native bases, T3 IS the newest complete bank in
  our libraries — the T6/T7 upgrades for Heihachi/Jin/King-class bases do not
  exist as pipelines yet (G-T6/G-T7), so no fighter was left on a T3 bank
  when a newer COMPLETE bank was available. That is the honest reading of
  the standard: prefer newest complete, flag the rest — which this table does.
- Every T3-only verdict above names its newer source: T6 PSP decode (G-T6)
  unlocks 13 fighters' bases; T7 pipeline (G-T7) unlocks 8 more; SF PAC
  decode (G-SF) unlocks the whole SF wing; VF decode (G-VF) unlocks 6;
  DOA4 anm decode (G-DOA) unlocks 6.
