# Bank audit: which fighters animate on someone else's character (2026-11-07)

Owner (verbatim): "And ur using incorrect banks for some character ls and some have mixed banks on purpose but some
should have fully one character banks and data unless it comes from Tekken code like that".

## The census

`tools/anim/bank_audit.mjs` (run it; the table is `docs/anim/BANK-AUDIT-2026-11-07.md`) asks the game's own code which
bank every roster fighter binds (`fighter.js bankIdFor`), and lists every bank of that fighter's canon base that exists
on disk (T3, TTT2, T7). Result on main after the Fill 3 TTT2 banks landed overnight:

- **Own bank, correct (28):** Pantera (King), Demonio (Jin), Diablo (Heihachi), Phantom (Yoshimitsu), Skull / Retsu
  (Bryan), Sakura / Sha (Xiaoyu), Gyou / Tobi (Hwoarang), Kai / King Tyrant (Eddy), Tou (Paul), Awa Pop (Nina), Torch
  (Anna), Nightwolf (Julia), Yukihyo (Armor King), Doc Frank (Bosconovitch), Dorowani (Gon), Chatur (True Ogre), Pond
  (Raven), Ryusan (Lucky Chloe), Megami (Jun), Menajerii (Roger Jr.), Buffalo Bill (Law), Gashadokuro (Kuma), Rave (Lei),
  Rin (Jin), Samura1 (Gun Jack: the owner's control fighter, untouched).
- **Stand-in by necessity (no bank of their own can exist):** non-Tekken bases (Charger / Blanka, Kronos, Deathfang /
  Iori, Ryuji, Koreshi, Cain Elias, Vain Abel), T7-only bases with no action bank yet (Waterfall / Josie, Scimitar /
  Shaheen, Dio / Akuma, Michiko / Katarina), DXMMII (Mokujin copies other styles by Tekken's own design), Baek (owner
  question: Baek or Kevin), Negativo (own T7 Negan stance + attacks; his base actions ride Bryan).
- **Owner ruling:** Zen stays unmapped (2026-10-24 decision).
- **On a stand-in while their own character's bank now exists (13):** Zui (Steve Fox, on Jin), Kinpo (Asuka, on Jin),
  Purple Rain (Lee, on Jin), Chordz (Lars, on Jin), Cyborg X (Alisa, on Gun Jack), Star (Christie, on Xiaoyu), Bruno
  (Miguel, on Bryan), Thor (Ganryu, on Bryan), Slice (Dragunov, on Bryan), Aotsuki (Panda, on Kuma), Burger (Bob, on
  Bryan), Mariposa (Zafina, on Xiaoyu), Silvertongue (Lili, on Xiaoyu).

## Why those 13 are not switched today

Their own banks are the Fill 3 TTT2 banks (`docs/tech/ttt2-mota/join/FILL3-BANKS.md`), which landed **inert** by design.
Two findings block binding them as they are:

1. **Coverage.** Each covers 7 to 14 action clips (T3 banks: 30); none has block, hit or KO, and Steve Fox, Christie,
   Ganryu and Dragunov have no stance at all. Bound alone they would leave those actions on the bind pose. The engine now
   has the standard answer, a per-slot layer (`fighter.js layerOwnSlots`): the character's own clip wherever it exists,
   the bound bank only for what it lacks (shared reactions, the way Tekken's own common bank serves every character).
2. **Quality, judged by eye** (`ttt2-own-slots-by-eye-1.png`, `-2.png`: poselab, the game's own loader + retarget, each
   fighter's own TTT2 slot where it has one, front and side): the TTT2 clips retarget with a strong forward pitch on our
   rigs. Zui's, Kinpo's, Purple Rain's and Bruno's walks are nearly horizontal; Kinpo's, Purple Rain's, Chordz's and
   Bruno's stances hunch; Aotsuki's Panda clips contort. That is the fold class the Jun bank had before its re-bake
   (`docs/handoffs/MEGAMI-JUN-BANK-SCALE-FIX-2026-11-04.md`). Switching now would make these fighters look worse.

So the layer ships **with no fighter active** (`OWN_SLOT_BANKS = {}`), the 13 sit in `OWN_SLOT_CANDIDATES`, and poselab
can preview a candidate (`showFighter({ id, clip, ownCandidates: true })`). Next step for this lane: re-bake the 13
fighters' TTT2 clips with the Jun-fix chain selection (whole-clip FK span + anatomical-coherence sweep), judge each by
eye, and move each fighter into `OWN_SLOT_BANKS` as its clips pass. Per-move clips (each move's own TTT2 row) are a
further wiring step, as for Roger.
