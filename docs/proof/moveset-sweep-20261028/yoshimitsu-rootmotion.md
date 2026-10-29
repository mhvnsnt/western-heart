# Yoshimitsu-bank root motion: per-clip facing (2026-10-29)

## Measurement (not a guess)
- Each row clip's first-frame forward vector was read from the knee-front heading: the direction the knees point at frame 0 in Hips space. That is `clipHeading` in game/js/t3anims.js.
- bryan and jin banks: every row sits at 0°.
- Yoshimitsu bank: the stance clips sit at about 13–21°. 112 rows are near 0° and 58 rows are near 180°; the rest are scattered.
- The rows near 180° are baked backwards: in play, their hit travels away from the opponent.

## In-game proof (jin_soul f+2, row 125)
| | Hips heading idle → active | gap during active |
|---|---|---|
| before | 48° → −140° | 1.45 → 2.36 m |
| after | 31° → 59° | 1.45 m (holds) |

## Fix
- `alignRowHeadings` turns a row 180° (rotation plus root translation about frame 0) when its frame-0 heading is more than 135° from the circular mean of the stance clips.
- Rows any moveset uses under a facing or back-turned T3 condition (0x24–0x2E) are excluded, because those are meant to face away.
- 59 rows are turned. The loader logs "[WH-T3] bank 'yoshimitsu': N row clips baked >135° …".

## Sweep harness timing (test only)
- Once hits connect, hit-stop ate the fixed post-press tail. Queued long-string hits then fired after the trace ended, so 4 strings lost their final hit.
- The sweep now drains the attack and its queue (capped at 360 frames) before the tail.
- The juggle follow-up waits the same way, so it fires as a fresh move instead of being buffered into the launcher string.

## Result (same harness, same opponent)
| fighter | before | after | fixed | regressed | juggles |
|---|---|---|---|---|---|
| jin_soul | 685/1041 | 770/1041 | 85 | 0 | 64 → 64 |
| phantom | 677/1048 | 752/1048 | 75 | 0 | 17 → 17 |

Known issue: jin_soul's juggle total is unchanged, but the passing set shifts by 8 keys. The newly failing ones are u/f+3+4,b+1, u/f+3+4,1~t3.yoshimitsu, d+1+4,b+1,b+1(,b+1), 1+2,2,1,4(,4/,2) and US.2+3, all "follow-up 1 never hit the airborne opponent". With correct forward travel the launch lands the foe at a different spot for the fixed 0.85 m follow-up jab.

Data: sweep-jin_soul-rootmotion.json, sweep-phantom-rootmotion.json.
