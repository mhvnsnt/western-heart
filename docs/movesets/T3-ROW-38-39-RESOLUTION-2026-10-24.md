# T3 King rows 38 vs 39 vs 40 — resolution with file evidence + T3 wire-in spec

**Date:** 2026-10-24. **Buttons:** LP1 = Left Punch = Tekken 1,
RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3,
RK4 = Right Kick = Tekken 4. **Authority for jumping:** hip-Y bone data
only (Hips rest = Root rest in this pack format, so world Hips Y =
`root_t` Y). Never move names, never JSON labels.

## Resolution (no relabel, no repoint — the file evidence closes it)

PR #1079's classifier doc (read from the #1079 branch, file
`docs/anim/T3-ANIM-CLASSIFICATION-JOB1-2026-10-24.md`) records, for bank
`king_on_pantera_leoman`:

| Row | Class | Trajectory (start → peak → end, m) | Rise / fall | Frames | `used_by` |
| --- | --- | --- | --- | --- | --- |
| 38 | jumping | 1.518 → 1.742 → 0.901 | 0.224 / 0.841 | 20 | `["cainelias"]` (Pantera NOT listed) |
| 39 | jumping | 1.518 → 1.742 → 0.901 | 0.224 / 0.841 | 20 | includes `pantera` (plus armor-king, hugo, kronos, kronos-attire2, kutz, marduk, yukihyo, zangief) |
| 40 | jumping | identical values | 0.224 / 0.841 | 20 | includes `pantera` |

The trajectories are IDENTICAL across 38/39/40 — one shared jumping-clip
family, not three distinct clips, and the jumping finding does not
depend on which key is cited.

**The boundary the #1079 doc left open** — "the classifier lists WHICH
fighters use a key; it does NOT state which input slot points at key 39
for Pantera; that slot-to-key link is UNMAPPED in this data and must be
confirmed from Pantera's moveset file" — **is now confirmed from
Pantera's moveset file on main** (`game/assets/movesets/pantera.json`):

| Row | Pantera move(s) carrying it as `t3_row` | Input | Context |
| --- | --- | --- | --- |
| 38 | `u+1,1` ("KING u+1,1 (T3 king r38)") | u+1,1 (jumping LP1) | Jumping input → jumping clip. CONSISTENT. |
| 39 | `u/f+1,1` ("KING u/f+1,1 (T3 king r39)") + generated `1_r39` | u/f+1,1 (jumping LP1) | Jumping input → jumping clip. CONSISTENT. |
| 40 | `u/b+1,1` ("KING u/b+1,1 (T3 king r40)") + generated `1_r40` | u/b+1,1 (jumping LP1) | Jumping input → jumping clip. CONSISTENT. |

**Conclusions:**

1. Row 38 is NOT re-labeled, NOT re-attributed, and NOT treated as
   Pantera's standing clip. The classifier's `used_by: ["cainelias"]`
   is bank-sharing metadata (the same `divmot03_king.bin` row reused
   across King-family banks); it does not override the moveset file,
   which wires row 38 to Pantera's jumping `u+1,1`. Both facts stand:
   the row jumps, and Pantera uses it only for a jumping input.
2. Row 39 IS Pantera's jumping `u/f+1,1` clip, and row 40 IS Pantera's
   jumping `u/b+1,1` clip. No moveset row is repointed by this
   resolution. Nothing changes for rows 38/39/40.
3. **The genuine error is downstream, not in rows 38/39/40:** the
   `anim_t3` nearest remaps for `FC.1`, `WS.1`, and `TACKLE.1` all point
   at row 39 with match "nearest limb/class/startup (approximate)".
   Row 39 is a jumping clip; borrowing it for full-crouch, rising, and
   tackle LP1 contexts is wrong. Replacement rows are UNMAPPED (no
   verified standing/rising row identified for these contexts) — the
   remaps stay recorded as wrong + approximate, and no substitute row
   is invented. (At runtime the nearest rows play LAST, after donor
   and pool, so the pool pick — not the recorded row — is what plays;
   the batch lane audits the pool pick, it does not trust the record.)
4. Generated keys `1_r39` / `1_r40` (inputs `1_r39` / `1_r40`) are not
   pressable notations. They are preserved, not deleted, per the
   no-clobber / preserve-quarantined-rows rule.

## PR #1079 status (verified this turn)

- **OPEN, NOT merged.** Head `00d8472a25e2d0b4365295ddb71796c63703d495`,
  branch `data/t3-anim-classification-job1-20261024`, base main,
  `mergeable_state` blocked. Files (additions only, no code, no moveset
  rows): `game/assets/anim/t3/anim-classification.json` (1,336,276
  bytes, 21 banks, 4,685 rows), `game/assets/anim/t3/anim-classification-summary.json`,
  `docs/anim/T3-ANIM-CLASSIFICATION-JOB1-2026-10-24.md`.
- Class totals verified from the summary: crouching 854 / jumping 1,181
  / standing 2,650. King bank `king_on_pantera_leoman`: 256 rows
  (42 / 63 / 151), source `teardown/tekken3/animations/divmot03_king.bin`.
- **This change does NOT duplicate those JSONs and does NOT merge.**
  The wire-in code PR is sequenced AFTER #1079 merges (see below).

## T3 classification wire-in — exact spec for the follow-up PR (PR-B)

**Wire-in point (verified on main):**
`packages/creation-suite/src/movelist-editor.js` —
`validateAssignment(slotContext, candidate)` (line 409; stance check
lines 427–435 trusts `deriveCandidateProperties()`), and
`deriveCandidateProperties(candidate)` (line 346; reads
`candidate.properties` / `candidate.anim_properties` ONLY when
`clip.source === "clip"` (line 353), otherwise falls back to
input-derived properties, source `"input"`). Library entries already
carry `t3_bank` + `t3_row` (lines 511–517) — that pair is the join key.
Pantera's moves carry NO `properties`/`anim_properties` today (0 of 874),
so every library entry currently validates on input-derived properties
— the exact gap the file header (lines 49–60) says cannot catch a clip
that jumps while its JSON label says "jab".

**Classification file shape (from the #1079 doc, to be re-verified
against the merged file before PR-B lands):** top-level keys are bank
names; each row key is the T3 row number with fields `class`, `rise_m`,
`fall_m`, `drop_m`, `start_y_m`, `peak_y_m`, `end_y_m`,
`net_travel_m`, `peak_travel_m`, `frames`, `used_by`. Class vocabulary
is exactly three values — jumping, crouching, standing — mapping
directly onto the editor's stance vocabulary. `rising`, `crouch_dash`,
`back_turned`, `sidestep` are NOT produced and remain UNMAPPED — never
invent them from these rows.

**Function to add (PR-B, in `movelist-editor.js`, exported):**

```js
// attachClipClassification(entries, classification, bankMap)
// - entries: fromMovesetFile() output (or movelist-data.js entries).
// - classification: the parsed anim-classification.json object.
// - bankMap: t3_source label -> classification bank key (table below).
// For each entry with t3_row != null and bankMap[entry.t3_bank] present:
//   const rec = classification[bankMap[entry.t3_bank]]?.[String(entry.t3_row)];
//   if (rec && rec.class) entry.properties = { stance: rec.class,
//     direction: entry.properties?.direction ?? 'none',
//     type: entry.properties?.type ?? (entry.move_class === 'throw' ? 'grapple' : 'strike'),
//     limb: entry.properties?.limb ?? entry.limb ?? null, source: 'clip' };
// Entries with no join keep their existing properties untouched (still
// source "input" or "canon" — never silently upgraded to "clip").
// Returns { applied, skipped_no_row, skipped_no_bank, skipped_no_record }
// so the host can prove the join rate; a 0-applied run with a present
// file is a failure, not a pass.
```

**Bank map (t3_source label → classification bank key; derived from
the 8 MOD fighters' files on main):**

| `t3_source` / entry `t3_bank` | Classification bank | Fighters |
| --- | --- | --- |
| `king` | `king_on_pantera_leoman` | pantera |
| `bryan` | `bryan` | burger, skull |
| `jin` | `jin` | demonio, kinpo, scimitar |
| `yoshimitsu` | `yoshimitsu` | phantom |
| `heihachi` | UNMAPPED — NO ALIAS | diablo |

**Heihachi gap (unchanged, not substituted):** `game/assets/anim/t3/heihachi/`
on main has 33 items but NO `rows.pack.json` (classifier HTTP 404).
Heihachi motion IS classified under `heihachi_on_jin`
(`divmot13_heihachi.bin`, 195 rows: 28 / 60 / 107). NO rows are copied
and NO alias is created silently: landing a real heihachi rows pack, or
a documented alias with owner approval, is the unblock. Until then,
diablo's entries keep input-derived properties and heihachi lookups
against the classification file are UNMAPPED. PR-B must NOT map
`heihachi` → `heihachi_on_jin` on its own authority.

**Host wiring (PR-B):** the host / library builder that produces
candidates must call `attachClipClassification` with the merged
`game/assets/anim/t3/anim-classification.json` and the bank map above,
BEFORE any `validateAssignment` call that is presented as clip-checked.
Once `source` is `"clip"`, `deriveCandidateProperties()` returns the
measured class and the stance check enforces it: a jumping clip in a
standing slot comes back `status: "wrong"`, `allowed: false`.

**Acceptance tests (PR-B, must pass before it is called done):**

1. Fixture test with the #1079 records for rows 38/39/40 (values in the
   table above): an entry with (`king_on_pantera_leoman`, 39) validates
   `wrong` in a standing slot and `correct` in a jumping slot.
2. Real-file test after #1079 merges: load the merged
   `anim-classification.json`, join all 8 MOD fighters' T3 entries, and
   report the join rate + the full list of standing-context entries
   that flip to `wrong` — each flip gets a disposition (repoint to a
   verified row, or UNMAPPED), never a bulk rewire.
3. Heihachi test: diablo entries produce 0 `source: "clip"` properties
   until the alias/pack lands.
4. No test may present an input-derived status as clip-verified
   (the file header's rule, unchanged).

**PR-B trigger:** file PR-B the moment PR #1079 merges to main (and
re-sync to that main first). PR-B must not ride inside this change:
this change's Pantera data edits must stay independently mergeable
whether or not #1079 lands, and the wire-in is only verifiable against
the merged classification file.
