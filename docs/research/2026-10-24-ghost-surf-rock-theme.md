# Ghost Surf Rock — Cape Jones theme song (2026-10-24)

Owner directive 2026-10-24 19:41 CDT: "Ghost Surf Rock" by Loyalty Freak
Music = Cape Jones theme song. If Cape Jones gets an arena, Ghost Surf
Rock is the MAIN track there (with interchanging tracks rotating around
it).

## Track

- Title: Ghost Surf Rock
- Artist: Loyalty Freak Music
- Album: WITCHY BATTY SPOOKY HALLOWEEN IN SEPTEMBER !!
- Length: 04:07
- License: CC0 1.0 Universal — verified on the Free Music Archive track
  page (26.8K plays, 4.4K downloads, released Oct 01, 2018). Earlier
  cape-jones record: PR #236, merged as 5b95a331.
- Source page: https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/Ghost_Surf_Rock
- Game file (pending download): game/assets/music/ghost-surf-rock.mp3
- Library entry: game/data/music-library.json, id `ghost-surf-rock`,
  status `pending-download`, modes `cape-jones-theme`, moods spooky /
  surf / ghostly / halloween / fun. The entry follows the exact
  pending-slot pattern from the music-rotation work: file null,
  remote null, so the rotation pools skip it entirely until the
  bytes land. The intended filename is recorded in the entry's
  `filePending` field.

## Vibe (defines Cape Jones music picks)

Surf rock + spooky + witchy + batty + Halloween. Spooky, surf, fun,
ghostly, Halloween-ish. Use this vibe when picking music for Cape Jones
/ Western Heart.

## Arena rule (applies when a Cape Jones arena lands)

- Add the arena's stage id to the track's `stages` list in
  game/data/music-library.json. The engine's stage-wins jukebox rule
  then makes Ghost Surf Rock the arena's main track.
- Interchanging tracks rotate around it: the arena's rotation pool is
  Ghost Surf Rock first, then the other stage-tagged tracks in order.
  Rotation-pool behavior arrives with the music-rotation engine work
  (PR #1030); the library entry here is forward-compatible with it.
- Until the arena exists, the track is only picked when a caller
  requests mode `cape-jones-theme` or mood spooky/surf/ghostly/
  halloween. Nothing in the current game requests those, so the entry
  can never be picked accidentally while the file is pending.

## Pending follow-up (not hidden)

The mp3 binary itself is NOT in this PR: downloading it needs a live
browser session on the Free Music Archive page above. Once downloaded,
commit it to game/assets/music/ghost-surf-rock.mp3 with that exact
filename, set the entry's file field to that path, and flip the
entry's status from `pending-download` to live. No code change is
needed at that point. Until then the rotation pools skip the entry
entirely, and any direct request that resolves to it falls back to
the procedural loop, so the game never goes silent.

## Other Loyalty Freak songs (candidates, NOT yet wired)

Owner: other Loyalty Freak songs are also OK for remaining cues. These
albums carry album-level CC0 1.0 statements on their Free Music
Archive pages, each with the caveat "please check individual tracks
for their respective licensing info" — so each track needs its own
per-track license check before it is added to the library or shipped:

- INSTRUMENTAL R&B BEATS TO SING OR RAP ON (17 tracks)
- MELODIES WITH A BEAT (14 tracks)
- ROLLER DISCO DANCE DANCE (8 tracks)
- MINIMAL AMBIENT BOUNCE (7 tracks)
- TO CHILL AND STAY AWAKE (7 tracks)

Do NOT assume the whole catalog is CC0. Verify per track, then add
one library entry per verified track, same pattern as above.
