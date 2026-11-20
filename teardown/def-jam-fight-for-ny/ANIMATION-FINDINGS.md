# Def Jam: Fight for NY — Animation & Grappling System Findings

**For Western Heart's grappling design · Owner directive 2026-10-13 · Worker: defjam-teardown**
**Game:** Def Jam: Fight for NY (EA Chicago, 2004, PS2) — built on the AKI wrestling-engine lineage (Def Jam Vendetta, 2003)

> This is the proof of the owner's thesis: **a full wrestling grappling system running inside a
> Tekken-style 3D fighter engine.** EA Chicago took AKI's wrestling core (grapples, momentum,
> reversals) and re-skinned it as a hip-hop street fighter with five fighting styles. Every
> structural finding below is traced to files extracted from the PS2 disc (see the
> [wrestling-game teardown](../../../../../wrestling-game/teardown/def-jam-fight-for-ny/TEARDOWN.md) —
> repo-relative link; models stay in wrestling-game per the separation law).

---

## 1. Engine lineage (verified on-disc)

- `ASSETS/AKI_CFG.XML` ships on the FFNY disc: `<faceial_animation>`, `<hands_animation>`,
  `<direction_animation>` toggles and a `pause_use_aki` flag. The AKI config survived the
  EA Chicago rewrite — the grappling core is AKI's.
- The motion bank is `MOTION/WRES_ALL.VIV` — "WRES" = wrestling, 64MB, the single largest
  non-audio archive. Animation sets are named `wres001` … `wres141`.
- The move database `MOTION/MAIN_ALL.DAT` opens with the magic **`WAZA`** (技, "technique") —
  the AKI move-database tradition, with 676 named moves in plaintext.

## 2. One grappling core, five fighting styles

FFNY's design (confirmed by FIGHTER.XML: 142 entries across STF/MAR/WRE/SUB/KIC):

| Style | Code | Grapple flavor |
|-------|------|----------------|
| Streetfighting | STF | dirty brawling grapples |
| Martial arts | MAR | acrobatic/flamboyant grapples |
| Wrestling | WRE | slams, suplexes (the pure AKI moveset) |
| Submission | SUB | armbars, chokes, joint locks |
| Kickboxing | KIC | knees/elbows out of the clinch |

**The key architectural point:** strikes are style-specific, but **grappling is one shared
system**. Every style uses the same grapple button/mechanics; the style only changes which
`wresNNN` animation set and which WAZA moves fire. For Western Heart this means: build ONE
grappling state machine (grab → struggle → throw/hold), then skin per-style move tables on
top — exactly how FFNY gets 5 styles' worth of content out of one engine.

Controls (from the manual + GameSpot hands-on): 2 strike buttons, 1 grapple button, run.
Weak/strong strikes and grapples on **analog pressure** (tap vs. hold) — no complex inputs.
Front grapple, back grapple, and **environmental grapples** (crowd holds the opponent, car
hoods/walls as weapons). Reversals exist per AKI tradition.

## 3. The momentum → BLAZIN' → finisher loop

The fight economy that makes grappling pay:
1. Landing strikes/grapples/taunts fills the **momentum meter** (under the health bar).
2. Full meter → **BLAZIN' mode** (character glows, crowd roars).
3. In BLAZIN', grapple + right-stick direction fires the **Blazin' move** — a style-specific
   grapple finisher (over-the-top, often multi-stage: e.g. punch-d drunk combo into a throw).
4. Blazin' moves have **dedicated animation data**: `MOTION/BLAZIN.VIV` (2.9MB) is a separate
   bank from `WRES_ALL.VIV`. Finishers are not scaled-up normals — they are authored as
   their own set.

KO rule: health has a "danger" (red) zone; only in the red do KO attacks work —
weapon strike, Blazin' move, or style KO attack. **Takeaway for WH:** gate finishers behind
*both* a resource (momentum/Nine-Soul meter) *and* a victim state (danger zone). That
two-gate design is why FFNY fights have drama instead of one-touch kills.

## 4. Motion data architecture (from the disc)

```
MOTION/
  WRES_ALL.VIV   64MB  423 files: wresNNN.mnl / wresNNN.ord / wresNNN.orl  (NNN=001..141)
  BASE00.VIV      2MB  base skeleton + shared animations
  BLAZIN.VIV      3MB  blazin' finisher animations
  MAIN_ALL.DAT  283KB  WAZA move database (676 named moves, plaintext)
  CAMERA.XML    143KB  camera definitions
```

Per-move triplet (sizes + binary analysis):
- **`.mnl`** (172–682B) — per-move header/index. `10 fb` magic, then a TLV/opcode stream
  carrying embedded move IDs (`N04F4_A`-style). Hypothesis: AKI-style move script bytecode
  (the condition/effect script for the move). Open RE work.
- **`.ord`** (300–755KB) — the payload. 6-byte `10 fb` header + embedded **EAGL object**
  (EA's toolchain format: borrows the `\x7fELF` magic, proprietary header — not parseable
  by readelf). Code + animation data for the move.
- **`.orl`** (12–21KB) — **per-bone animation tracks**. After the `10 fb` header and section
  names (`.data`, `.shstrtab`, `.rel`, `__EAGL_TOOL`, `Animation`), the bulk is a run of
  `11 07 VV` triplets where `VV` sweeps smoothly as signed 8-bit — **uniformly-sampled,
  quantized bone-rotation keyframes**. Track count / bone map / time base = open work.

Character models tie in via `V2IP_xxx_F.o` → `__PosePaletteBank`: the bone palette used for
skinning. So the pipeline is: **WAZA move → wresNNN triplet → .orl bone tracks → PosePaletteBank
skinning**. One shared skeleton convention across all 78 fighters (all `.o` rigs are ~5KB —
same bone count, different proportions via the mesh).

**`AUDIO/ANIMTAGS.DAT`** (`TAGS` magic, 1,919 tags like `A100_EC`): the animation tag index —
the engine addresses animations by tag, not by filename. Moves reference tags; the tag table
resolves to `wresNNN` sets. (This is the indirection layer WH wants: gameplay code says
"play GRAPPLE_FRONT_STRONG", the tag table resolves it to data.)

## 5. The grappling vocabulary (from the WAZA database)

Plaintext move names shipped on disc — the actual AKI/EA grappling move list, directly
reusable as WH's grappling move-table seed: `POWERBOMB`, `POWERPLEX`, `PILEDRIVER`,
`SIDESLAM`, `ARMBAR`, `CHOKE`, `CHOKEOUT`, `HEADBUTT`, `DROPKICK`, plus style moves
(`SOUTHPAW`, `BLITZ`, `FULL`, `JACK`, `BOOT`, `KRUNCH`, `MONEY`, `SLINGIN`, `BUSTIN`,
`CHOPS`, `FISTED`, `HAMMER`, `HITMAN`, `DEVIL`…). Full 676-name list:
`wrestling-game/teardown/def-jam-fight-for-ny/motion/waza_names.txt`.

`ASSETS/COMBS.XML` shows how moves chain: `<comb entry>` lists `skill no` sequences with
score/mp bonuses — **combos are data (skill-ID sequences), not code**. WH's combo system
should be the same: ordered skill-ID lists with meter rewards.

## 6. What Western Heart should steal (concrete)

1. **One grappling state machine, N style skins.** FFNY proves 5 styles × 1 core works.
   WH's wrestling mode: single grab/struggle/throw state machine; styles supply move tables.
2. **Two-gate finishers.** Resource (momentum/Nine-Soul) + victim state (danger zone).
   Prevents degenerate one-touch kills, creates drama.
3. **Finishers as a separate bank.** `BLAZIN.VIV` exists apart from `WRES_ALL.VIV` — author
   WH's Soul Surge finishers as their own set, not scaled normals.
4. **Tag indirection.** Gameplay references anim tags (`A100_EC`-style); a tag table resolves
   to data. Decouples design from assets — designers retarget without touching code.
5. **Combos as data.** Skill-ID sequences with meter bonuses in XML, not hardcoded.
6. **Environmental grapples.** Crowd/wall/car grapples are FFNY's signature — WH's arenas
   (Shrine of the Blade etc.) should have grapple-interactable geometry.
7. **Analog-pressure grapples.** Weak/strong on tap-vs-hold, no complex inputs — fits the
   "Tekken inputs are the language" rule: keep grapple inputs simple, depth in the struggle.
8. **Seed the move table from WAZA.** The 676 plaintext names are a ready-made grappling
   vocabulary — port the names/roles, re-author the animations in WH style.

## 7. Open RE work (not blocking)

- SHPS mesh decode (vertex encoding past header unknown) → GLB conversion of 78 fighters
- EAGL object header layout → skeleton + PosePaletteBank decode
- `.orl` bone map + time base → playable animation curves
- `.mnl` bytecode semantics → move condition/effect scripts
- Full 1.65GB audio (format documented: same BIGF container)

## Provenance

Extracted 2026-10-13 from `SLUS_210.04.Def Jam - Fight for NY.iso` (Archive.org,
4,694,573,056 bytes) via surgical ISO9660 range extraction. Formats: `TEARDOWN.md` in
`mhvnsnt/wrestling-game` (`teardown/def-jam-fight-for-ny/`). Tools: `bigf_extract.py`
(BIGF-variant), `iso_tree.py`.
