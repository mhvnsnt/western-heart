# Music: Ghost Surf Rock file landing + Nosferatu completion check (2026-10-25)

## Owner instruction (verbatim)
- "Ghost Surf Rock by Loyalty Freak Music = Cape Jones theme song. If Cape Jones gets an arena, Ghost Surf Rock is the MAIN track there (with interchanging tracks rotating around it)."
- Phase 4 music lane: commit the game's music files, wired into rotation, PR filed; do NOT merge (parent merges when clean + green).
- Standing rule checked first: PR #1030 was already OPEN for this work — inspect its branch before filing anything competing.

## What was found (evidence, not assumption)
- PR #1030 is NOT open: it was MERGED 2026-10-25T00:53:39Z (merge commit 8579c6df). Its branch work (rotation engine, library entries, loop-point fields) already lives on main. No competing PR was filed.
- Nosferatu 25: ALREADY on main via commit 7868804d590b (2026-10-25T01:34:24Z, "feat(music): commit 25 GPU-cut Nosferatu tracks + loop points (follow-up to #1030)"). Verified 25/25: zip sizes = GPU manifest size_bytes = main's committed sizes; library loopStart/loopEnd values match the GPU manifest exactly (spot-checked all 25 ranges, contiguous 0-5067s). Nothing was recommitted.
- Ghost Surf Rock gap (the only real gap): the Cape Jones jukebox pool's mainTrack points at `assets/music/ghost-surf-rock.mp3`, which returned 404 on main, and its status read "pending-file". A DIFFERENT filename, `cape-jones-ghost-surf-rock.mp3`, was already shipped by #1037 — but the pool does not reference it, so the pool still fell back to the procedural loop.
- Workspace copy verified before commit: `browser_downloads/sess-679381103/...-5-Loyalty_Freak_Music_-_Ghost_Surf_Rock.mp3`, ID3 title "Ghost Surf Rock", artist "Loyalty Freak Music", album "WITCHY, BATTY, SPOOKY, HALLOWEEN IN SEPTEMBER !!", duration 246.67s = 04:07, 3,948,657 bytes, git blob SHA-1 174d24ec3b79ee86d4da34ce0222a302cf5a64c2 — identical to main's `cape-jones-ghost-surf-rock.mp3` blob. Same bytes, pool-correct filename.

## Change in this PR
- Added `game/assets/music/ghost-surf-rock.mp3` (the verified bytes above).
- `game/data/jukebox-pools.json` (surgical string edits only): Cape mainTrack status pending-file -> file-landed; Nosferatu pool source note updated (#1030 merged, bytes committed in 7868804); coordination note updated (#1030 merged).
- `test/audio-jukebox.test.mjs`: the pending-file assertion flipped to assert the file path + no pending-file flag. No other test touched.
- NOT touched: `game/data/music-library.json` (no new library track — Ghost Surf Rock's library entry already exists as `cape-jones-ghost-surf-rock`; library total stays 54), no moveset files, no banner files, no T8 content.

## Rotation-test count interaction (52 -> 60 rule)
- The standing note said whichever of #1058/#1072 merges second must bump the rotation test 52 -> 60. That framing is stale on current main: #1058 already merged, main's library is 54 tracks (14 + 25 nos + 5 Tekken pending + 8 Cape Jones + 2 Loyalty Freak), and the rotation test already asserts 54. This PR adds zero library tracks, so the count stays 54 and the rotation test is untouched. Open PR #1072's test hunk (44 -> 52) predates the #1037/#1058 merges; its rebase is the merge lane's job, not this PR's — this PR does not touch `music-library.json` or the rotation test, so it cannot conflict with #1072 on either file.

## Known nit left for the parent (not hidden)
- The 25 Nosferatu library entries still carry `source.status: "cut-pending-kaggle-run"` even though the cuts are committed. Deliberately left alone: flipping 25 strings touches `music-library.json`, the file open PR #1072 also edits, for a cosmetic label the engine does not gate on (the engine gates on file/remote null, and all 25 files now exist). Parent may flip it in a follow-up or let the #1072 merge lane take it.

## Proof
- `node test/audio-jukebox.test.mjs` — ALL AUDIO/JUKEBOX CHECKS PASSED (with the edited pools + test files).
- `node test/music-rotation.test.mjs` — All music rotation checks passed (unchanged, 54 tracks).
- Pool resolution verified by reading the config: Cape mainTrack.file = `assets/music/ghost-surf-rock.mp3`, and that exact path is the file this PR adds. The procedural fallback is no longer reachable for this track.
- Live play verification (phone-portrait play of the Cape Jones pool) is owed to the parent's play-verify lane; this lane cannot drive the live browser.
