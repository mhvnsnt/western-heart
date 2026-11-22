# Nine Souls — T3 Body Replacement Map

Owner order 2026-10-15: replace ALL T3 default character models with T6, TTT2, or better (preference T6 > TTT2 > T7-style). T3 models move to legacy (back of attire list).

**Scope:** the Nine Souls of Tong-Nou (ROSTER.md). Each soul's default body was a Tekken 3 TMD extraction (pending teardown — none exist on disk yet).

## Per-soul mapping

| Soul | Kanji | T3 donor (legacy) | Replacement (default) | Source |
|------|-------|-------------------|----------------------|--------|
| RIN | 凛 (protagonist) | Jin Kazama TMD | Demonio's body (`demonio-a1`, `roster/demonio/attires/attire1/model.glb`) — RIN's vessel body | `rin-body.glb` was the Steve Fox model, retired (wrong canon per owner 2026-10-15; the Steve body belongs to Zui) |
| BYOU | 病 (sick) | Lei Wulong TMD | — **BLOCKED by owner** — | `rave.glb` (T7-style Lei, PR #170) available but WH name for Lei is unmapped; per owner directive, left untouched |
| TOU | 闘 (fighting) | Paul Phoenix TMD | Own Eastern Mind body (`tou-soul-tex.glb`, 2026-11-10) | Built from Sato art (CHARA_b012 + R_TOH); the assembled Paul body (`tou-body.glb`) is legacy; Paul is his fighting base, not his body |
| SHA | 沙 (sand) | Ling Xiaoyu TMD | Saku Ra's own Tripo (`saku-ra`, `roster/sakura/attires/attire1/model-rerig.glb`) | `sha-body.glb` (T7 Xiaoyu) is legacy |
| KAI | 海 (sea) | Eddy Gordo TMD | Own Eastern Mind body (`kai-soul-tex.glb`, 2026-11-10) | Built from Sato art (CHARA_b006); `kai-body.glb` (the Eddy shell) is legacy |
| JIN | 刃 (blade) | Yoshimitsu TMD | Vessel Phantom's own Tripo (`phantom`, `roster/phantom/attires/attire1/model-rerig.glb`) | `jin-body.glb` (T7 Yoshimitsu) is legacy/ladder-back |
| RETSU | 烈 (violent) | Bryan Fury TMD | `game/assets/models/retsu-body.glb` — T7-style Bryan | PR #170 `skull.glb` (RigModels fan rip) |
| ZEN | 禅 (still) | Julia Chang TMD | Own Tripo spirit body (`zen`, Tripo 8c46e379, `roster/zen/attires/attire1/model.glb`) | `zen-body.glb` (T7 Julia) is Attire 2 legacy only — it is NOT Zen's body (owner correction 2026-11-21) |
| GYOU | 行 (moving) | Hwoarang TMD | Own spirit body (`gyou-attire1`) | Gyou is NOT Hwoarang (Hwoarang's holder is Tobi); his Paul holding is conditional — only if he needs somebody (owner 2026-11-21) |

**Result (corrected 2026-11-21):** the "6 of 9 T7-style bodies" count no longer holds — RIN, SHA, KAI, JIN and ZEN now fight in their own/vessel bodies, TOU and GYOU in their own soul/spirit bodies, and only RETSU still defaults to a T7-style donor body (Bryan) pending the owner's call. BYOU/Lei is resolved (Lei→Rave, 2026-11-06).

## Attire order (owner rule)

- Attire 1 (default): the soul's own body above (Tripo original or Eastern Mind soul body); the T7-style donor body, where one existed, ladders back as a legacy attire.
- Legacy (last): the Tekken 3 TMD extraction — still pending teardown. When extracted, it lands as the final attire, never the default.

## Provenance

All T7-style models are RigModels fan rips (third-party), integrated on PR #170 (`roster-integrate-phase1`). Soul-body files were renamed `<soul>-body.glb` per the soul they serve. The "byte copies (verified by size)" claim was size-only and is FALSE for RIN: `rin-body.glb` shares only the size (8,808,768 B) with the Steve Fox model — it is a re-export of the Steve Fox model, not Jin. No new models were created; no game files were deleted.

## Notes

- `jin-body.glb` serves **JIN (刃, the Blade Soul)** — Yoshimitsu. Not to be confused with RIN (凛), whose body is `rin-body.glb` (Jin Kazama).
- BYOU's vessel is Zui (Steve body); the Lei→BYOU body mapping was resolved 2026-11-06 (Lei→Rave; see Resolution below).

## Resolution (2026-11-06)

The blocked BYOU/Lei mapping above is resolved. The owner named Lei
Wulong's WH fighter: **Rave** (Kiko Tanaka / Ghost — locked 2026-10-19 /
2026-10-21, see `game/js/roster-full.js`). Byou's moveset base is **Wang
Jinrei** (Tekken 6) per the owner's 2026-11-06 ruling ("He can have wang
if no one else does"); the Lei layer was removed from
`game/assets/movesets/byou.json` and Wang's decoded T6 PSP kit wired in
its place. Byou's vessel remains **Zui** (Steve body), unchanged. The
dated entries above stand as the historical record of the blocked state.
