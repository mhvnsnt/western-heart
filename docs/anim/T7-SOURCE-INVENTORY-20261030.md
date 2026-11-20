# Tekken 7 animation programme — per-fighter source inventory (2026-10-30)

Programme step (b): for every fighter on the roster, determine the T7 base
character and whether the GRE teardown holds their mothead/mask source.
Checked fresh 2026-10-30 against main 665739b8 (merge #1258).

## Where the sources actually live — read this first

The programme brief's phrase "the GRE teardown on disk
(teardown/tekken7-steam/tkdata + pakchunk)" does NOT describe the
western-heart repo: that path does not exist there. The GRE tree lives in
the PRIVATE repo `mhvnsnt/game-reverse-engineering`, at
`teardown/tekken7-steam/tkdata/mothead/`:

- `bin/` — 57 `*mot.bin` move-table binaries (anim names/ids)
- `json/` — 56 `*mot.json` decoded move tables (no `testmot.json`)
- `mask/` — 58 `*rotsm.arc` clip banks, INCLUDING `common.arc`
  (5,049,396 bytes)
- `movelist/` — 53 `*.mvl` movelists

What western-heart itself holds for T7 animation:

- `tools/anim/t7_anim64.py` (0x64 decoder, port of TKMovesets2
  ParseAnimation0x64) + `tools/anim/t7_clipmap.py` (motbin-to-clip join)
- `game/assets/movesets/t7/` — 33 T7 character move-table overlays
  (`t7-<name>-lp-rp-lk-rk.json`), NOT clip banks
- `game/assets/anim/t7/` — `INDEX.json` (headline still true: ZERO T7 clip
  banks), `STANCE-STATUS.json`, and two motbin banks
  (`frv-pond-motbin-bank.json`, `dnc-ryusan-motbin-bank.json`)
- `teardown/tekken7/king/` — King MODEL + textures only (no `.arc`)
- `teardown/models/tekken7/MODELS-INDEX.md` — community-rip MODELS
  (meshes), not motion

Two standing records corrected by this inventory:

1. The clipmap docstring's "0x8000 shared common bank (not in the
   extracted data)" is stale against the GRE listing: `common.arc` IS
   held in `mask/`. The next clipmap step for the 0x8000 bank is to test
   the join against `common.arc` — not to assume it decodes, and not to
   keep reporting the bank as unheld.
2. Pakchunk0 is still ruled out for clips (see `game/assets/anim/t7/
   INDEX.json` headline: its manifest holds meshes + textures only).
   The live-memory TKMovesets extraction remains the fallback for any
   clip the GRE banks do not yield — never a closest-match clip.

GRE code letters used below are the T7 internal codes from
`teardown/tekken7/TEKKEN7-ROSTER-MAPPING.md` (e.g. KIN = King, MIG =
Miguel, BOB = Bob, JIN = Jin, ASA = Alisa, MRX = Akuma). "FULL" means all
four files are present in the GRE tree: `<code>mot.bin`,
`<code>mot.json`, `<code>rotsm.arc`, `<code>.mvl`.

## Core-8 — the programme order (Pantera/King first, then core-8)

| WH fighter | T7 base | GRE code | mot.bin | mot.json | rotsm.arc | movelist | Status |
|---|---|---|---|---|---|---|---|
| Pantera | King | KIN | kinmot.bin | kinmot.json | kinrotsm.arc (7,794,048) | kin.mvl | FULL — decoder + clipmap already run (PRs #1226/#1228: 467/552 attacks resolve; 71 on 0x8000 + 14 inline are the gaps) |
| Demonio | Jin Kazama | JIN | jinmot.bin | jinmot.json | jinrotsm.arc | jin.mvl | FULL — clipmap not yet run |
| Dio | Akuma | MRX | mrxmot.bin | mrxmot.json | mrxrotsm.arc | mrx.mvl | FULL — clipmap not yet run |
| Cyborg X | Alisa Bosconovitch | ASA | asamot.bin | asamot.json | asarotsm.arc | asa.mvl | FULL — clipmap not yet run |
| Burger | Bob Richards | BOB | bobmot.bin | bobmot.json | bobrotsm.arc | bob.mvl | FULL — clipmap not yet run |
| Bruno | Miguel Caballero Rojo | MIG | migmot.bin | migmot.json | migrotsm.arc | mig.mvl | FULL — clipmap not yet run |
| Deathfang | Iori Yagami (KOF) | — | — | — | — | — | NOT A T7 FIGHTER — T7 programme does not apply; KOF XV motion route per `docs/anim/DEATHFANG-ANIM-GAP-20261023.md` |
| Chatur | True Ogre (Tekken 3) | — | — | — | — | — | NOT IN T7 — T7 programme does not apply; T3 bank route (`game/assets/movesets/index.json`: ogre bank divmot14) |

Finding: source availability is NOT the core-8 blocker. All six
T7-applicable core-8 fighters have full GRE source held. The blockers are
programme (a) the 0x64 joint-frame fix (still gated on paired 0xC8/0x64
data or a named community source — no guessed rotation ships) and
programme (c) the per-fighter decoder/clipmap runs, which have only been
done for King.

## Owner-named WH fighters with a T7 base (mapping doc)

| WH fighter | T7 base | GRE code | Status |
|---|---|---|---|
| Pantera | King | KIN | FULL (see core-8) |
| Demonio | Jin Kazama | JIN | FULL (see core-8) |
| Phantom | Yoshimitsu | YOS | FULL — yosmot.bin, yosmot.json, yosrotsm.arc, yos.mvl |
| Diablo | Heihachi Mishima | HEI | FULL — heimot.bin, heimot.json, heirotsm.arc, hei.mvl |
| Skull | Bryan Fury | BRY | FULL — brymot.bin, brymot.json, bryrotsm.arc, bry.mvl |
| Sam-∪R-Λ1 | Jack-7 | JAC | FULL — jacmot.bin, jacmot.json, jacrotsm.arc, jac.mvl |
| Saku Ra | Ling Xiaoyu | XIA | FULL — xiamot.bin, xiamot.json, xiarotsm.arc, xia.mvl |

## The 33 T7 overlay characters held in western-heart

`game/assets/movesets/t7/t7-<name>-lp-rp-lk-rk.json` exists for all 33
below, and every one of them also has FULL GRE source (all four files).
The overlay table is move data, not clips — clips come from the GRE
rotsm.arc via the clipmap join, which has not been run for any of them
yet (King is the only clipmap run on record).

| T7 character | GRE code | T7 character | GRE code |
|---|---|---|---|
| Akuma | MRX | Lars Alexandersson | LAR |
| Alisa Bosconovitch | ASA | Marshall Law | LAW |
| Claudio Serafino | ITA | Lee Chaolan | LEE |
| Sergei Dragunov | DRA | Leo Kliesen | LEO |
| Eddy Gordo | EDD | Leroy Smith | NSB |
| Eliza | ELZ | Lidia Sobieska | NSD |
| Fahkumram | NSC | Lili Rochefort | LIL |
| Feng Wei | FEN | Ling Xiaoyu | XIA |
| Ganryu | GAN | Lucky Chloe | DNC |
| Geese Howard | MRY | Master Raven | FRV |
| Gigas | CRZ | Miguel Caballero Rojo | MIG |
| Hwoarang | HWO | Negan | NSA |
| Jack-7 | JAC | Nina Williams | NIN |
| Josie Rizal | MUT | Noctis Lucis Caelum | MRZ |
| Katarina Alves | LTN | Paul Phoenix | PAU |
| Kazumi Mishima | KZM | Steve Fox | STE |
| Kazuya Mishima | KAZ | Zafina | ZAF |
| Kuma | KUM | | |
| Kunimitsu | KNM | | |

Note on the two motbin banks already in `game/assets/anim/t7/`:
`frv-pond` (Master Raven, 2,338 moves, 1,593 on 0x8000) and `dnc-ryusan`
(Lucky Chloe, 2,183 moves, 1,527 on 0x8000) are move tables, not clip
banks — their 0x8000 moves are exactly the ones the `common.arc` test
above may unblock.

## Wider roster — how the rest is decided

Every other moveset file in `game/assets/movesets/` (128 files in
`game/assets/movesets/index.json`) is decided by its `tekken_base`
field in that index: if the base is one of the 51 T7 roster characters
in `teardown/tekken7/TEKKEN7-ROSTER-MAPPING.md`, the GRE tree holds its
source on the same pattern (the tree covers essentially the whole T7
roster: 57/56/58/53 files across the four dirs), and the remaining work
is only the per-fighter clipmap run — no new source hunt. If the base
is not a T7 roster character, the T7 programme does not apply; those
fighters belong to their own donor programme (KOF, Street Fighter, DOA,
VF5, or T3-only — e.g. True Ogre, Mokujin, Gon, Ogre, Dr. Bosconovitch).
Borderline files are decided individually, not by a blanket rule:
`marduk` (Craig Marduk, T7 DLC, MAR held) is T7-applicable;
`demonio-human` (Demonio variant) rides the Jin source via the Demonio
file family; `t3-law` is the T3 Law file, so its T7 route runs through
the Law source, not the T3 file; `megami` (Jun, TTT2) and `menajerii`
(Roger Jr., TTT2) are not T7.

## Flags for the next runs (not conclusions)

- `nsa`/`nsb`/`nsc`/`nsd` rotsm.arc files are all exactly 3,891,648
  bytes. Verify distinct content before any clipmap run uses them;
  identical size is a flag, not a finding.
- The 0x64 joint-frame fix still gates baking for every fighter: a
  decoder run without it produces crumpled 0x64 clips (King finding,
  BUILD-LOG 2026-10-29 18:00). Inventory does not change that gate.
- Next programme steps in order: (1) test the 0x8000 join against
  `common.arc` on King; (2) clipmap runs for the other five T7 core-8
  bases in the King format (attacks resolved / total, bank split
  0x0000/0x4000/0x8000/inline); (3) the 0x64 fix, then bake + wire.
