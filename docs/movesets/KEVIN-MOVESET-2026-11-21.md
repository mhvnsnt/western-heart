# KEVIN — Full Canon Moveset (2026-11-21)

Lane 2A (Kevin + canon-movesets job). Owner order, 2026-11-21 ~19:59 EST
(verbatim substance): "Go get all that stuff and wire it up to him [Kevin]
from all the decomps and recomps and already extracted and decrypted and
cracked stuff that you can get, and wire it up so he has his full canon move
set how he should."

## 1. Who Kevin is (canon)

- **CANON.md, "KEVIN — The Master Soul"**: "Not one of the nine. The
  teacher." Owner note, 2026-10-20: *"the fighter IS Kevin. Baek's model is
  Kevin's A2 attire; the Master's White reskin is PARKED. The Master Soul's
  story — the teacher who came on purpose — is Kevin's now."*
- Backstory is Baek Doo San's: taekwondo master, the man who taught Hwoarang
  everything the boy refused to learn gently; lost at sea, taken, broken,
  rebuilt; came back because students don't stop needing teachers. "The trial
  didn't call him. A student followed the pull — and Baek followed the
  student."
- Fighting philosophy: **"The kick is the question. Discipline is the
  answer."** Element: **Fire — the Plains of Chi-U.** Signature detail: he
  bows to every opponent — before the match, after it, win or lose.
- **God Molecule bible** (`God-molecule-production-stage`,
  `docs/canon/AUTHORED_STORY_SOURCE.md` + `ShowBible.tsx`): Kevin is a
  canonical, essential character — "just a guy, inside Mars' head" — who
  appears from behind/through the symbol on Mars's forehead after the world
  shifts, with his own parallel arcs and comedic pacing.
- **Roster** (`game/js/roster-full.js`): `{ id: 'baek-master-white', name:
  'KEVIN', title: "The Master Soul", base: 'Kevin', moveset: 'kevin', model:
  'baek', style: 'Tae Kwon Do', archetype: 'Pressure' }`.
- **Home base: Sun Rā's stage** (owner direction); Kevin can fight on any
  stage. Element home is the Plains of Chi-U (Fire).
- **Attire ladder** (PR #278, merged 2026-10-19; `roster/baek/ATTIRE-SLOTS.md`):
  A1 = Kevin Tripo model, his face (default) · A2 = original Baek model ·
  A3 = Master White (PARKED). Baek is NOT a separate fighter — Baek folds
  into Kevin; Baek's model is attire material in Kevin's ladder.

## 2. What Kevin's canon moveset IS

Kevin's moveset **is Baek Doo San's flawless Tae Kwon Do**, as the fighter
KEVIN. Canon defines **no move-level changes** vs Baek's kit — the canon
modifications are identity-level only:

1. Identity: name/title/base KEVIN, "The Master Soul", the teacher's story.
2. Attire ladder above (A1 Kevin Tripo / A2 Baek / A3 Master White PARKED).
3. Two WH-original canon signature moves, wired 2026-10-24 (see §3):
   **"Eleventh Lecture"** (`1+4`) and **"Master's White"** (`1+2`).
   (The Baek-file signatures "Homework" `1+4` / "Kick Is the Question" `1+2`
   are also carried in the file as donor rows.)
4. Home stage: Sun Rā's stage.

### The file: `game/assets/movesets/kevin.json`

- **207 moves** (158 strike / 24 signature / 14 throw / 4 string / 3 special /
  2 reversal / 2 stance), 13 slots, 6 strings, 14 specials.
- Every playable row carries a **real Baek name + input** (Jab, Double
  Punches, Chonsan, Flamingo Rocket, Bolt Cut, Chipping Sweep, Reverse Middle
  Kick, …). **Zero** move names contain "BAEK" — the names are the moves'
  own names, not the donor's label.
- Bare `1` and `2` jabs carry **real published frame data** (see §3).
- `tekken_base: Baek`, `t3_source: hwoarang` — honest source attribution:
  the kit IS Baek's Tae Kwon Do, animated on the declared T3 Hwoarang proxy
  bank (see §4 gaps).

## 3. Sources (all real, all cited in the file itself)

| # | Source | What it gives | Licence / provenance |
|---|--------|---------------|----------------------|
| 1 | `teardown/tekken6/movesets/t6psp-baek-doo-san-moveset-v3.json` (in-repo; 276 records, 81 unique commands) | Baek names + glyph commands (T6 PSP COM decode) | Commercial game data, community-extracted/decoded, held in-repo. Licence logged honestly per LICENCE-NOT-A-GATE (never gates, never leaves a gap). No game files shipped in this PR — only the derived JSON moveset. |
| 2 | `game/assets/ttt2/movesets/bae.json` (in-repo; 102 records) | Baek names, inputs, throw escapes (TTT2 movelist; underlying dataset for the 153 TTT2 rows carried in the source file) | Same as above. |
| 3 | `game/assets/movesets/t3-hwoarang.json` (in-repo; 723 moves) | Frames / damage / animation on the same input (declared T3 Hwoarang proxy — Taekwondo, the closest T3 bank) | Same as above; proxy disclosed per row, never presented as real Baek data. |
| 4 | Published frame data: tekkendocs.com/t6/baek + TTT2 movelist | Bare `1`: T6 8 dmg, i10, +1/+8; TTT2 9 dmg, i10, +1/+8/+8. Bare `2`: T6 8 dmg, i10, +0/+7; TTT2 9 dmg, i10, +0/+7/+7 | Community reference data (published frame data). |
| 5 | WH canon, `docs/canon-movelist-wiring-2026-10-24.md` | Canon signatures "Eleventh Lecture" (`1+4`) + "Master's White" (`1+2`); canon_moves wired 2026-10-24, additive, no Tekken entry replaced | Western Heart original canon. `wh:` anim refs are placeholders for animations NOT yet authored; NOT play-verified. |
| 6 | PR #1792 branch `wh-moveset-fix/p2-rebuilds-20261120`, head `7f7bf8b5`, file `game/assets/movesets/baek-master-white.json` (sha256 `41484ed9…af48e4`, 207 moves) | The rebuilt Baek dataset this file is derived from | In-repo PR payload (merge-HELD, owner's call — NOT touched by this PR). Derivation recorded in the file's `kevin_rebuild` record. |

**Derivation (exact, re-runnable — see lane workdir `build_kevin.py`):**
source file → `fighter` baek-master-white → `kevin`; `display` BAEK MASTER
WHITE → `KEVIN`; 6 `wh:baek-master-white:` anim refs re-namespaced to
`wh:kevin:` (4 signature rows + 2 canon_moves); `canon_owner`
BAEK-MASTER-WHITE → `KEVIN` (2 rows); new `kevin_rebuild` provenance record.
**Everything else is byte-identical to the source file** — all 207 moves,
slots, strings, specials, `baek_kit`, `baek_rebuild`, `canon_moves`,
`canon_wiring`, `merge_sources`, `anim_set_lock`, `expansion`,
`restored_from_sweep_338`. Donor/provenance keys untouched (`merge_source`
ttt2:baek, `ttt2_source` baek, `donor.baek.*`, `t3_source` hwoarang,
`tekken_base` Baek). No move invented; no frame/damage/animation invented.

**Archive.org:** checked live 2026-11-20 by the PR #1792 lane for the
sibling VF5 sources (57 VF5 title hits, no decoded dataset beyond what the
repo holds). No new game acquisition was needed for Kevin: every source
above already lives in-repo, so no archive.org pull was staged and no game
was bought (NO-BUY).

## 4. Gaps (reported, not papered over)

- **No Baek frame/damage/animation bank exists in holdings** except the bare
  `1`/`2` jabs. Playable rows run Hwoarang motion (disclosed per row and in
  the rebuild records). The T6 PSP decode yields names + glyph commands
  only; the TTT2 movelist yields names, inputs, throw escapes only.
- **38 of 81 T6 commands have no same-input Hwoarang row** (mostly long
  Flamingo strings) and stay kit-only (`baek_kit`), never invented.
- **Canon signature animations (`wh:kevin:sig:*`) are NOT yet authored** —
  placeholder refs, NOT play-verified (same standing gap as the 2026-10-24
  canon wiring).
- **No Baek stance table exists** in sources (`stance_after` empty).
- **No T7 Baek bank exists** (Baek is not in Tekken 7 — correct; T7 is not
  a gap, it is a fact).
- **`test/full-movelist-baseline.json` has NO `kevin` row yet.** The row can
  only be computed by running `test/full-movelist-combos.test.mjs
  --write-baseline` against the merged tree. The test applies no floor to
  fighters missing from the baseline, so this is owed, not blocking.
  (Local test run was blocked by an execution-risk check on the cloned tree;
  CI on the PR is the verification path.)

## 5. What this PR wires (and does not touch)

**Wired (6 files):**
- `game/assets/movesets/kevin.json` (NEW, 159,289 B, sha256
  `3304466023a5a5339d52223c76555c78f9b482b1a11894800a9f93294f0d90f7`) —
  the complete Kevin moveset.
- `game/assets/movesets/index.json` — `kevin` entry added (generator
  formula: display KEVIN, tekken_base Baek, t3_source hwoarang, moves 207,
  inputs 13 = len(slots), bytes = file size). Required: `movesets.js`
  `_fetchOne` returns null for ids missing from the index. Sibling entries
  are stale (pre-date the current generator/files); a full index
  regeneration is a separate follow-up, not churned here.
- `game/js/roster-full.js` — KEVIN entry `moveset: 'bryan'` → `'kevin'`
  (1 line). Before this PR Kevin played **Bryan Fury's kit** in-game.
- `game/data/roster_map.json` — `baek-master-white` entry `wh_moveset:
  'bryan'` → `'kevin'` (1 line).
- `game/js/movesets.js` — `'kevin'` added to `MOVESET_IDS` (1 line).
- This doc.

**Untouched by design:**
- PR #1792 (OPEN, merge-HELD) — its files, its branch, its merge call
  (the owner's). If #1792 lands with changes to `baek-master-white.json`,
  re-derive `kevin.json` from the new head with the same transform.
- PR #278 (MERGED 2026-10-19) — the attire ladder it landed stands as-is.
- `baek.json` (stays staged under its own id; no second card — canon-fix
  P3), `baek-master-white.json` on main (stays as the pre-rebuild file),
  `game/data/soul-variants.json` (the `baek-master-white` row already
  exists; the roster id is unchanged), `test/full-movelist-baseline.json`
  (kevin row owed — see §4), `game/js/assets.js` (the live-game default
  model swap rides with the auto-rig pass; Kevin's Tripo GLB is still an
  unrigged static — **not claimed done here**).
- No files deleted. No merge (merge calls are the owner's, never the lane's).

## 6. Verification done here (own-eyes, API-verified)

- Source files read from main via the GitHub API and hash-verified:
  T6 decode 276 moves ✓, TTT2 bae 102 records ✓, `t3-hwoarang.json`
  775,627 B ✓; #1792-branch files git-blob-sha1 + sha256 matched the PR
  body's published digests ✓; main `baek.json` (111 moves) /
  `baek-master-white.json` (291 moves) git-blob-sha1 matched the API ✓.
- `kevin.json`: 207 moves, 13 slots, 6 strings, 14 specials; leak scan
  clean under the exact `full-movelist-combos` rule (0 of 207 move names hit
  the deny list; display clean); only the intended renames differ from the
  source (4 signature rows + 2 canon_moves + identity fields + the new
  `kevin_rebuild` record), asserted programmatically by `build_kevin.py`.
- Each wiring diff verified to be exactly the intended lines (index +8,
  roster-full 1 line, roster_map 1 line, movesets +1 line).
- **Not verified here:** the node test suites (`input-matrix`,
  `soul-systems`, `full-movelist-combos`, `moveset-slot-hijack`,
  `moveset-editor`) — local run blocked (see §4); **CI on this PR must go
  green before any merge call**, and the `kevin` baseline row must be
  written from a `--write-baseline` run. In-game play of Kevin on the new
  moveset is still owed (auto-rig pass gates the live default swap).
