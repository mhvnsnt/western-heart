# Pantera voice rewire — 2026-10-24

## What was replaced

The old Pantera voice set — 9 OGG files in `game/assets/voices/pantera/`
(`intro-01`, `intro-02`, `win-01`, `win-02`, `taunt-01`, `taunt-02`,
`hit-01`, `ko-01`, `select-01`) attributed to `teardown/eastern-mind` /
`F_KING` stage voices — was DELETED in full (9 files). Prior project
record states those 9 `F_KING` clips were music/SFX, not King voice, so
they were not reused as voice in any form.

## What replaced it

52 OGG Vorbis clips in `game/assets/voices/pantera/`, from the verified
King voice bank `AkBankVoiceKIN.bnk`:

- Primary (preferred): Set B — TekkenMods mod 1242, "King Grunts from
  Tekken 2", 26 clips, `pantera-t2-01.ogg` … `pantera-t2-26.ogg`.
  Owner ear-checked 2026-10-24: better quality, preferred.
- Alternate: Set A — TekkenMods mod 681, "King Classic Sounds",
  26 clips, `pantera-classic-01.ogg` … `pantera-classic-26.ogg`.

Source game: Tekken. Source character: King. Decoded from the
loudness-normalized WAVs in `king-mods/f2-t2grunts/norm/` (Set B) and
`king-mods/f1-classic/norm/` (Set A), converted with
`king-mods/kaggle_batch_audio.py` (ffmpeg loudnorm + libvorbis q5,
parallel batch, printed proof: per-file durations, loudness stats,
output sizes, sha256). Combined size 1.58 MB.

## How triggers were assigned (honesty rule)

The bank carries slot IDs (WEM IDs), not content names. No clip was
assigned a spoken line, and no content label was invented. Clips are
identified by position number only, and every clip's `text` is
position-based ("King voice bank, position N (T2 grunts)" /
"(Classic)").

Triggers were assigned per set, independently, by duration rank only:

- longest 3 → intro; next 4 → win; next 4 → ko;
- remaining clips ≥ 1.0 s → taunt; remaining sub-1 s clips → hit;
- shortest clip → select.

Resulting pools (both sets combined): intro 6, win 8, ko 8, taunt 7,
hit 21, select 2. Every clip's `note` states: trigger assigned by
duration rank only, content not verified by ear, to be confirmed at
the owner voice session.

## Engine wiring (voice.js contract)

Manifest: `game/data/voices/pantera.json`. `game/js/voice.js` filters
`clips` by `trigger`, so all six triggers resolve to real clips.
Variant support: clips are ordered T2 first, then Classic, per
trigger. `voice.play('pantera', trigger, variantIdx)` picks
`pool[variantIdx % pool.length]`, so variantIdx values in the
manifest's `variantMap` preferred range play the T2 set and values in
the classic range play the Classic alternate. Note honestly: default
`play()` with no variantIdx picks at random from the full pool (both
sets); a caller that wants preferred-only playback must pass a
variantIdx in the preferred range. Clip `status` is `verified-bank`
(not `placeholder`), so the engine plays audio rather than falling
back to subtitle-only.

## What still needs the owner's ear

At the owner voice session, for all 52 clips: confirm what each clip
actually is (bark / roar / exertion / line), reassign any trigger
that duration alone got wrong, and replace position-based `text`
with real transcriptions only where actually heard. Until then,
nothing in this set is presented as a verified spoken line.
