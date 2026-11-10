# Pantera (King T7) input → move → clip matrix — pass 1 (2026-11-10, MoneyManBusch / Grok)

Owner (t386u): Pantera first, 100% King T7, proven by real on-screen presses. This is pass 1:
the movement rows only, driven through the SAME per-frame path game.js runs
(`TekkenBuffer.noteDirection(stick, dt)` → new latch → `trySystemMotion(dir)` → `_tickState`)
at 60 fps in node (`test/tekken-dash-pantera.test.mjs`). **Node proof only — no touchscreen /
browser proof yet.** Not a claim of 100%.

Sources: King T7 motbin `kinmot.json` (the reverse-engineering repo, tkdata mothead json),
own-slot bank `game/assets/anim/t3/t7_king/` (real King T7 generic clips, 60 fps).

| Command | Stick per frame (60 fps) | Recognized | Exact clip | Result (node) | Pass |
|---|---|---|---|---|---|
| f,f (dash) | f×2, n×2, f×1 | `tekdash` dash (Kg_sDASHF) | t7_king `dash` (coyt_dash125) | +1.41 m over 30 f, then idle | ✅ |
| b,b (backdash) | b×2, n×2, b×1 | `tekdash` backdash (sDASH_00B) | t7_king `backdash` (coyt_newback) | −0.667 m over 30 f, no invuln, mirrored at facing −1 | ✅ |
| f (single tap) | f×1, n×30 | — | — | no dash, no travel | ✅ (negative) |
| f held | f×40 | — | — | no dash | ✅ (negative) |
| f,b | f×2, n×2, b×2 | — | — | no dash | ✅ (negative) |
| f,f airborne | — | — | — | refused | ✅ (negative) |
| f,f then 1 | dash, then button 1 | `f,F+1` Jaguar Hook | **`f,F+1` row: `UNMAPPED:t7-clip-pending`** (the `f,F+1~t7.king` row has `t7:king:king_48`) | attack fires from the dash | ⚠️ fires, **wrong row / no real clip** |

## Before this pass (main `fb21d043`)
f,f and b,b did **nothing** for Pantera: the latch only starts KOF `system` rows and
`pantera.json` has none. The same test on main fails 4/5 (only the negatives pass).

## Not yet sourced / not done (next passes)
- **KBD (backdash cancel).** `sDASH_00B`'s own cancel list has u/b → `Kg_wDASH_00B`, n (frames 1–29) → `sDASH_00BLp`, end at 30 → `sWALK_00B`. The crouch (d/b) cancel lives in the packed group-cancel table (needs decoding). Not invented.
- **f re-press at dash frame 12** → `Kg_sDASHF` again / `sRUN__00F` (run). Not wired.
- **Crouch dash `f,n,d,df`.** `pantera.json` has no `cd_entry`, so the buffer never latches CD.
- **Duplicate rows.** Plain vs `~t7.king` rows (e.g. `f,F+1`, `f,F+2` "Beast Elbow" vs "Rolling Elbow") — the resolver picks the plain unmapped row.
- **Sidestep clip choice, all 13 T7 generic banks.** They are baked forward = +x, lateral = z, but `t3anims.js` `lateralDx` reads x (≈ +0.005 for both sidesteps), so the right sidestep never finds a clip. The sign of z (is `sSTEP_01L` +z the character's left?) needs a rendered check before the fix.
- **Touchscreen proof** (real presses on the deployed build) — parent computerUse task.
