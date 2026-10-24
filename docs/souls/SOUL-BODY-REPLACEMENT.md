# Nine Souls — T3 Body Replacement Map

Owner order 2026-10-15: replace ALL T3 default character models with T6, TTT2, or better (preference T6 > TTT2 > T7-style). T3 models move to legacy (back of attire list).

**Scope:** the Nine Souls of Tong-Nou (ROSTER.md). Each soul's default body was a Tekken 3 TMD extraction (pending teardown — none exist on disk yet).

## Per-soul mapping

| Soul | Kanji | T3 donor (legacy) | Replacement (default) | Source |
|------|-------|-------------------|----------------------|--------|
| RIN | 凛 (protagonist) | Jin Kazama TMD | `game/assets/models/rin-body.glb` — T7-style Jin | RigModels fan rip via Demonio (`demonio.glb`, on main) |
| BYOU | 病 (sick) | Lei Wulong TMD | — **BLOCKED by owner** — | `rave.glb` (T7-style Lei, PR #170) available but WH name for Lei is unmapped; per owner directive, left untouched |
| TOU | 闘 (fighting) | Paul Phoenix TMD | — **PENDING extraction** — | No T7-style Paul model exists in PR #170; needs T6/TTT2 extraction |
| SHA | 沙 (sand) | Ling Xiaoyu TMD | `game/assets/models/sha-body.glb` — T7-style Xiaoyu | PR #170 `saku-ra.glb` (RigModels fan rip) |
| KAI | 海 (sea) | Eddy Gordo TMD | `game/assets/models/kai-body.glb` — T7-style Eddy | PR #170 `king-tyrant.glb` (RigModels fan rip) |
| JIN | 刃 (blade) | Yoshimitsu TMD | `game/assets/models/jin-body.glb` — T7-style Yoshimitsu | PR #170 `phantom.glb` (RigModels fan rip) |
| RETSU | 烈 (violent) | Bryan Fury TMD | `game/assets/models/retsu-body.glb` — T7-style Bryan | PR #170 `skull.glb` (RigModels fan rip) |
| ZEN | 禅 (still) | Julia Chang TMD | `game/assets/models/zen-body.glb` — T7-style Julia | PR #170 `nightwolf.glb` (RigModels fan rip) |
| GYOU | 行 (moving) | Hwoarang TMD | — **PENDING extraction** — | No T7-style Hwoarang model exists in PR #170; needs T6/TTT2 extraction |

**Result:** 6 of 9 replaced with T7-style bodies (best available — no T6/TTT2 extractions exist yet). 1 blocked by owner decision (BYOU/Lei). 2 pending future T6/TTT2 extraction (TOU/Paul, GYOU/Hwoarang).

## Attire order (owner rule)

- Attire 1 (default): the T7-style body above.
- Legacy (last): the Tekken 3 TMD extraction — still pending teardown. When extracted, it lands as the final attire, never the default.

## Provenance

All T7-style models are RigModels fan rips (third-party), integrated on PR #170 (`roster-integrate-phase1`). Soul-body files are byte copies of the PR #170 fighter GLBs (verified by size), renamed `<soul>-body.glb` per the soul they serve. No new models were created; no game files were deleted.

## Notes

- `jin-body.glb` serves **JIN (刃, the Blade Soul)** — Yoshimitsu. Not to be confused with RIN (凛), whose body is `rin-body.glb` (Jin Kazama).
- BYOU's vessel is Zui (Steve body); the Lei→BYOU body mapping is flagged blocked until the owner names Lei's WH fighter (see `roster/rave/CONCEPT.md` on PR #170 for the pending Rave concept).
