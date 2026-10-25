# SOUL SYSTEMS (owner decision 2026-10-23)

KESSHOU stays THE finisher (`finisher.js`). Three new, separate mechanics sit on the Tekken base.
All costs use the existing Nine-Soul Meter (0..100, `fighter.meter`).

| System | Trigger / gate | Cost | Input | Effect |
|---|---|---|---|---|
| **結章 KESSHOU** (existing) | meter full + victim < 25% HP, on the killing blow | full meter | none (victory outro) | authored finisher beats; now picks a per-fighter variant (`game.kesshouVariant`) |
| **九魂解放 Nine-Soul Release** | meter full | 100 | 1+2+3+4 at full meter (below full the same press is Soul Kindle) | unblockable super, 30 dmg × variant power. HUD meter-ready indicator (`ui.setSoulReady`) when the meter first fills — no center-screen text (Tekken-exact fight UI, 2026-10-24) |
| **霊放 Reihou** "Spirit Release" | foe is in RAGE | 50 | 1+4 (only claimed while foe rages; otherwise the moveset's 1+4 plays) | spirit channels flare (`_spiritFlare`), foe's rage purged for the round (`_rageUsed`), 6 dmg |
| **試練の封 Trial's Seal** | round ends by KO and winner ≥ 50% HP, or KO came from a soul system | — | automatic | decisive verdict seal banner + `matchStats.seals`; not a death |

Interactions
- **SOUL URGE** (2+3 = URGE gauge) is untouched. **魂 ACTION / Spirit Action** fires from 2+3 *while URGE is on* + a context trigger.
- **RAGE**: Reihou is the counter to rage; a purged fighter cannot re-enter rage that round (no Rage Art).
- Release can be the killing blow that opens KESSHOU (meter is spent by Release, so KESSHOU then needs its own gates; Release KO still earns Trial's Seal).
- Balance: Release 30 dmg ≈ a T7 Rage Art at WH scale (rage.js 32); Reihou is cheap damage-wise and priced in meter so it is a tempo choice, not a combo ender.

Per-fighter variants — `tools/soul-variants/gen.mjs` → `game/data/soul-variants.json`
- `tier = 1 + 2·lore(title/name matches god|devil|demon|king|emperor|boss|master|legend|lord|true|final|ancient|soul|spirit|oni|dragon) + 2·(archetype Boss) + min(2, forms) + (≥8 move types) + (≥300 moves)`
- `count = clamp(3 + floor(tier/2), 3, 8)` → baseline 3–4, strong canon fighters 5–6+.
- Each variant is keyed to a real move type in the fighter's moveset (strike/throw/low/mid/high/heavy/fist/kick/launch…); runtime prefers the variant matching the last move type used.
- Each transformation form gets its own set (`forms.<id>`, ≥3, from that form's moveset when present).
- Names: `<SYSTEM> · <MoveType> <Chapter|Release|Flare|Seal>`, run through `tools/canon` rename + denylist.
- Test `test/soul-systems.test.mjs` asserts every roster fighter meets its minimum in all four systems.
