# Pantera — T7-only string anims audit + batch plan (Batch 1 first)

**Date:** 2026-10-24. **Base:** main, `game/assets/movesets/pantera.json`
(874 moves; strings list 81 entries). **Method:** for each strings-list
entry, the fired full-input move is resolved slot-first (the resolver's
order: slot alias, else exact key) and its animation status is read from
the file — `t3_row` present = single-row wired; `t7:` ref with no
`t3_row` = T7-only; `t8:` ref with no `t3_row` = T8-fired (no playable
clip either). This audit covers the strings list only; the full comma-key
census is at the end.
**Buttons:** LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## CORRECTION to any earlier "exact" reading (user batch order 2026-10-24 22:23 CDT)

`fighter.js` `_attackClipPlan` plays ONE resolved move per string (first
match wins, own bank only). A single wired row is therefore NOT, by
itself, a verified multi-hit string fix: the row must be shown to cover
all hits of the string. The 9 "single-row wired" strings below are
recorded as SINGLE-ROW WIRED, SEQUENCE COVERAGE UNVERIFIED — never as
fixed strings. For each string in a batch, the batch lane must produce
ONE of: (a) a verified sequence clip from the files, (b) a MADE sequence
clip built to the move's timing, or (c) an engine step-playback change
with proof that steps play correctly. NEVER a single-row rewire presented
as a string fix. GPU job 4 (sequence_scan) candidates feed option (a);
the Kaggle jobs 1–6 run is underway — its outputs are NOT claimed here
before they exist. PRIME CANDIDATE under separate validation (faster-
methods research, user 2026-10-24 22:25 CDT; workspace
`~/workspace/faster-methods/`): step-based string playback driven by
file cancel graphs — each string step = its own verified single-row
clip, chained by file cancel links (decoded cancel graphs: frv 11,573,
dnc 10,034). This is a HYPOTHESIS, not a fact: it must be validated
against the files before any batch wires on it. If it validates, it
eliminates the sequence-clip problem for options (a)/(b) and becomes
the faster correct method; the batch lane switches to it when it lands
and does not stall waiting. The research lane must not duplicate the
Kaggle jobs 1–6 work.

## Counts (strings list, 81)

| Status of fired full-input move | Count |
| --- | ---: |
| Single-row wired (`t3_row` present; sequence coverage UNVERIFIED) | 9 |
| T7-only (`t7:` ref, no `t3_row`, no playable clip) | 45 |
| T8-fired (`t8:` ref, no `t3_row`, no playable clip) | 27 |

**Fallback behaviour today (all 72 non-wired):** correct damage/frames
from the file, animation = donor/pool/generic via `_attackClipPlan`
(class-matched by button/limb/level/startup, or generic light/medium/
heavy). The T7-only ones are fixable ONLY by T7 clip extraction
(live-memory export, `anim_ref` − 0x8000 join); the T8-fired ones are
fixable by T7 extraction + repoint to the T7 twin where one exists (see
twin column), or by the #1073-style UNMAPPED treatment where none
exists. No string below is fixed by re-pointing it at another bank's row.

## Batch order (user 2026-10-24 22:23 CDT)

Per character, Pantera first: Batch 1 = LP1/RP2-only strings (punches
only, any directionals) FIRST; Batch 2 = LK3/RK4-only strings; Batch 3+
= mixed pairs, then triples/quads and the rest. Chain-throw chains are a
separate grapple system (throw-chain path, not comma typing) and are NOT
counted in any punch/kick batch. Batch counts: Batch 1: 19, Batch 2: 11,
Batch 3+: 13, chain: 38. Total 81.

### Batch 1 — LP1/RP2-only strings (19) — WIRES FIRST

Fired key in brackets; status: W = single-row wired (coverage
UNVERIFIED), T7 = T7-only, T8 = T8-fired. T7 twin = same-input `~t7.king`
key whose clip is the T7 extraction target (canonical twin first).

| String | Fired key | Status | T7 extraction target / note |
| --- | --- | --- | --- |
| `2,1` | `2,1~t8.king` | T8 | `2,1~t7.king` (`king_23`); slot repoint BLOCKED on damage ruling (see Pantera doc §2: body 9 vs 15 vs 16) |
| `1,2` | `1,2` | T8 | `1,2~t7.king` (`king_3`) |
| `1+2,1` | `1+2,1` | T8 | `1+2,1~t7.king` |
| `1,2,1` | `1,2,1` | T8 | `1,2,1~t7.king` (`king_11`, "Palm Attack to Uppercut") — the parent's Palm Strike Uppercut example: correct damage (13 body; T7 per-hit "9,20,13") + fallback anim today; real fix = T7 `king_11` clip |
| `b+1,2` | `b+1,2` | T8 | `b+1,2~t7.king` |
| `b+2,1` | `b+2,1` | T8 | `b+2,1~t7.king` |
| `b+2,1+2` | `b+2,1+2` | T8 | `b+2,1+2~t7.king` |
| `d+1,2` | `d+1,2` | T8 | NO in-file T7 twin — unblock is T7 frame-data identification + extraction, not assumed |
| `df+1,2` | `df+1,2` | T8 | NO in-file T7 twin (canonical `d/f+1,2` is a separate twin-key case) |
| `df+2,1` | `df+2,1` | T8 | NO in-file T7 twin (canonical `d/f+2,1` separate) |
| `f+2,1` | `f+2,1` | T8 | `f+2,1~t7.king` |
| `f+2,d+1` | `f+2,d+1` | T8 | NO in-file T7 twin |
| `f+2,d+1,2` | `f+2,d+1,2` | T8 | `f+2,d+1,2~t7.king` |
| `ws2,2` | `ws2,2` | T8 | NO in-file T7 twin (canonical `WS.2,2` separate) |
| `FC.1,2` | `FC.1,2` | T7 | `king_115` — T7 clip extraction target |
| `d+1+2,2` | `d+1+2,2` | W row 98 | Sequence coverage UNVERIFIED (option a/b/c proof owed) |
| `d+1+2,2,1` | `d+1+2,2,1` | W row 198 | Sequence coverage UNVERIFIED |
| `d+1+2,2,1,1` | `d+1+2,2,1,1` | W row 257 | Sequence coverage UNVERIFIED |
| `d+1+2,2,1,1,2` | `d+1+2,2,1,1,2` | W row 258 | Sequence coverage UNVERIFIED |

Batch 1 verdict: 0 of 19 fixed. 14 T8-fired, 1 T7-only, 4 single-row
wired pending sequence proof. The batch lane's first work is the
sequence-clip question for the 4 wired rows + the T7 extraction join
for `king_3` / `king_11` / `king_23` / `king_115` and the other Batch 1
twins — one by one, each move's clip verified with file evidence before
that batch wires.

### Batch 2 — LK3/RK4-only strings (11)

| String | Fired key | Status |
| --- | --- | --- |
| `d/f+4,4` | `d/f+4,4` | W row 197 (coverage UNVERIFIED) |
| `d+3+4,4` | `d+3+4,4` | T8 (`d+3+4,4~t7.king` twin exists) |
| `d+3+4,4,4` | `d+3+4,4,4` | T8 (twin exists) |
| `d+3+4,4,4,4` | `d+3+4,4,4,4` | T8 (NO in-file T7 twin) |
| `df+3,4` | `df+3,4` | T8 (NO in-file T7 twin; canonical `d/f+3,4` separate) |
| `df+4,3` | `df+4,3` | T8 (NO in-file T7 twin; canonical `d/f+4,3` separate) |
| `df+4,3,4` | `df+4,3,4` | T8 (NO in-file T7 twin) |
| `df+4,3,d+4` | `df+4,3,d+4` | T8 (NO in-file T7 twin) |
| `CH.d+3+4,4,4,4` | `CH.d+3+4,4,4,4` | T7 (`king_94`) |
| `FC.d/f+4,4` | `FC.d/f+4,4` | T7 (`king_124`) |
| `FC.d/f+4,4,4` | `FC.d/f+4,4,4` | T7 (`king_125`) |

Batch 2 verdict: 0 of 11 fixed. Wires only after Batch 1, in the same
one-by-one manner.

### Batch 3+ — mixed strings (13)

| String | Fired key | Status |
| --- | --- | --- |
| `d/f+4,2` | `d/f+4,2` | W row 196 (coverage UNVERIFIED) |
| `d+1+2,2,1,1,3` | `d+1+2,2,1,1,3` | W row 264 (coverage UNVERIFIED) |
| `d+1+2,2,1,1,2,4` | `d+1+2,2,1,1,2,4` | W row 259 (coverage UNVERIFIED) |
| `d+1+2,2,1,1,3,3` | `d+1+2,2,1,1,3,3` | W row 265 (coverage UNVERIFIED) |
| `1+2,3` | `1+2,3` | T8 (twin exists) |
| `3,2` | `3,2` | T8 (NO in-file T7 twin) |
| `3,2,2` | `3,2,2` | T8 (NO in-file T7 twin) |
| `3,2,2*` | `3,2,2*` | T8 (NO in-file T7 twin) |
| `b+1,4` | `b+1,4` | T8 (twin exists) |
| `d+3+4,4,4,2` | `d+3+4,4,4,2` | T8 (NO in-file T7 twin) |
| `1,2,1,1,2,4,4,4,1,3` | `1,2,1,1,2,4,4,4,1,3` | T7 (`king_138`, 10 Hit Combo 1) |
| `1,2,1,1,3,3,4,3,2,1+2` | `1,2,1,1,3,3,4,3,2,1+2` | T7 (`king_139`, 10 Hit Combo 2) |
| `BURNING_HAMMER.2+4,3+4,1+3,1+2,1+2+3` | (same) | T7 (`king_288`, "Screwdriver" — a throw name, not the Screw mechanic; chain family, listed here only because the batch classifier puts it outside the pure stance-chain set) |

Note: the two 10-hit strings are the pending-prefix sequences from the
Stage 0 plan — they verify in sequence (each step fires in turn), not
as a single row.

### Chain-throw chains (38) — separate grapple system

All 38 fire T7-ref moves (`king_211`–`king_293` range: Pile Driver,
Double Heel Hold, Standing Heel Hold, Indian Death Lock, Arm Breaker,
Head Jammer, Chicken Wing Face Lock, Reverse Arm Slam, Backdrop, German
Suplex, Power Bomb, Reverse Special Stretch Bomb, Cannonball Buster,
Manhattan Drop, Victory Bomb, Cobra Clutch, Sleeper, Cobra Twist,
Reverse DDT, Burning Hammer, Tackle). Their slot-resolved keys exist;
what is UNVERIFIED is the comma-typed final chords (`1+2+3` /
`1+2+4` — 6 DANGLING in the Stage 0 sim) and the throw-chain system's
rescue of them. Play one chain throw end-to-end on the live build
before any chain is called fixed. Chain work does not displace Batch 1.

## Full comma-key census (context, not the batch list)

372 comma-containing move keys on main: 136 with an exact T3 row,
148 T7-only (no `t3_row`), 88 T8 (no `t3_row`). The strings-list audit
above is the user-facing subset; the batch lane works the strings list
first, then the remaining comma keys in the same batch order.

## What "fixed" means for a batch (reporting rule)

A batch is fixed only when: every string in it plays its correct clip
(sequence clip (a), MADE sequence clip (b), or engine step-playback (c)
with proof), the change is merged cleanly (3-way, no clobber), deployed
to the playable build, and played on the live build with touch taps in
phone portrait — first hits AND continuations. Simulation alone is NOT
fixed. This change fixes 0 strings; it delivers the audit + batch order
+ extraction targets so the batch lane wires one by one.
