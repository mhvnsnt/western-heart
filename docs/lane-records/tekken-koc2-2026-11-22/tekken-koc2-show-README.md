# Tekken + KoC2 — show directory (Coordinator lane 3/4, owner order 2026-11-22)

Date: 2026-11-22/23. Lane record: `~/workspace/bannon-all-moves-tekken-koc2.md`.

## Headline (honest)

**0 Tekken moves and 0 KoC2 moves play in a real match. 0 stills, 0 MP4s.**
Nothing in this directory is match proof, because no Tekken or KoC2
clip passes the match seam gates. What is here instead is the evidence
for why, the per-clip pairing audit, the refusal wiring brick, and the
KoC2 loader disassembly — so the next lane does not redo this work or
fake the proof.

## Counts

| Game | Clips in repo / decoded | Wired | Plays in a real match |
|---|---|---|---|
| Tekken 3 | 230 clips, PARTIAL | 0 | 0 |
| Tekken 7 | 96 clips, PARTIAL | 0 | 0 |
| Tekken 5 Devil Within | 54 clips, PARTIAL | 0 | 0 |
| Western Heart MADE | 3 adaptations (not decoded motion) | 0 | 0 |
| **Tekken total** | **383 clips, PARTIAL, 0 FULL** | **0** | **0** |
| KoC2 | 0 decoded (16,660 MVS files, bitstream uncracked) | 0 | 0 |

## Files in this directory

- `pairing-audit.json` — all 383 Tekken clips, one row each: source,
  set memberships (throw clip 18 / truncated-before-contact 14 /
  spike exception 5 / non-wrestling 5 / MADE 3), receiver/reaction/
  root-travel/library-move all null, pairing verdict
  (361 BLOCKED_NO_RECEIVER / 14 BLOCKED_TRUNCATED / 5 NOT_A_MOVE /
  3 ADAPTATION). Built from the Bannon repo manifest, nothing invented.
- `gate-check.json` — seam-gate evaluation of all 383 clips + KoC2:
  0/383 playable. Every clip fails G2 (no receiver), G3 (no root
  travel), G4 (no library mapping), G6 (renderer cannot play
  position-pose JSON). G5 known-fail 68 (14 truncated + 54 DW
  no-active-frames-by-design), 315 unassessed per-clip.
- `tekken-wiring-brick.js` — registry of the 383 clips + KoC2 refusal
  state. `isPlayableTekkenClip()` returns false for every clip with
  the failing gates; `lookupKoC2Motion()` returns MISSING for every
  id. DRAFT, not landed, not appended to the engine.
- `tekken-wiring-brick-test.cjs` — headless test, **ALL PASS 14/14,
  exit 0** (run 2026-11-23).
- `prep/build-pairing-audit.py` — builds the audit from the manifest.
- `prep/tekken-koc2-gate-check.py` — builds the gate check from the audit.
- `prep/koc2-2894c0-chunk-lookup.log` — NEW Route A disassembly:
  chunk-name lookup at 0x2894c0 (calls 0x30cf80 next).
- `prep/koc2-28b178-chunk-loader.log` — NEW Route A disassembly:
  chunk loader at 0x28b178 (calls 0x28a6e8 / 0x28b0a0 / 0x28b0b8 next).
- `prep/koc2-28b108.log` — NEW Route A disassembly: range helper.
- `prep/koc2-route-a-next.md` — what the three functions do, the
  "KOC2"-stamped allocator finding (magic 0x4b4f4332), next functions,
  and stale docs to stop following (0x1189B8 correction, byte-1 doubt).
- `stills/`, `video/` — EMPTY on purpose. See the NOT-PROOF-YET notes
  inside them. No stills or MP4s exist because there is no playable
  clip to render; rendering one would be inventing a match.

## Why 0 play (plain words)

Every Tekken clip is one fighter alone. There is no second fighter
in the clip (no receiver, no reaction), the fighter's travel across
the mat was dropped when the clip was converted, no clip is mapped to
a named Bannon move, and the match renderer only plays 2K26
quaternion clips — Tekken clips are position-pose JSON and there is
no retarget build to play them. KoC2 has no motion at all: the 16,660
motion files are written in a code nobody has cracked yet.

## What unblocks the first real proof (in order)

1. King artifact rescue before 2027-02-19 (GitHub auth download of
   artifact 14688676730, 14,386,774 B, sha256 613826d7…; anonymous
   download is 401) + durable home (owner decision: new release vs
   alongside `tekken7-gamefiles-v1`).
2. Re-extract with `--compression none` (extracted .tkmvst is LZ4
   type 1, converter refuses it), generalise the #1803 workflow
   (fighter code as input, PR-event trigger), then Bryan, Heihachi,
   Jin, Yoshimitsu.
3. Pairing + root restore: receiver from AKI P2 / WMXIX / authored
   reaction (King .tkmvst receiver move 554 is the only lead); root
   x/z from the western-heart source pack root track.
4. Position-pose → rig retarget build for the match renderer.
5. VM/browser bout run on Finn / Big Cass / Elias / Enzo — stills
   AND MP4s, eye-checked vs source. That run is owed; this lane
   cannot do it (subagent has no live browser; match-run.py needs
   Playwright/Chromium).
6. KoC2: disassemble 0x30cf80, 0x28a6e8, 0x28aea0, 0x28b0a0,
   0x28b0b8; find the MVS bitstream reader; then file 01999.
