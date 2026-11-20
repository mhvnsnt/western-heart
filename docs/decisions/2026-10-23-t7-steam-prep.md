# Decision log — T7 Steam prep (2026-10-23)

## T7 promoted to first-class source
Tekken 7 (Steam AppID 389730) is now a first-class pull target in
`tools/depot-pull/GAME-TARGETS.md`, per the owner's TEKKEN SOURCE PRIORITY law
(T5/T6/T7/TTT2 first, T3 fallback-only). Authorization: the user bought T7 on
Steam — game-ownership rule ("when the user says they own a game, THAT IS
AUTHORIZATION") applies; no proof requested, none needed.

## Depot: 389731, verified four ways
Windows content depot **389731** verified on steamdb.info across the base,
Originals, Ultimate and Definitive Edition packages. Single content depot for
all of T7; no per-character depots exist.

## No AES key needed
T7's paks are NOT encrypted (public community docs, CDDTreborn wiki). Only
Geese/Noctis DLC files use per-file encryption — out of scope. Documented in
`tools/depot-pull/FMODEL.md` with the rotation-check order if that ever changes.

## Pull runs user-side; we never touch Steam credentials
DepotDownloader needs the owning Steam account's login. Per standing policy we
NEVER solicit Steam credentials — so the pull (and any Steam Guard challenge)
happens on the user's machine via `tools/depot-pull/T7-USER-STEPS.md`
(2 paths, 5 steps max, plain language). No anonymous depot auth was attempted
for this paid game.

## Filelist design: shared chunks → post-unpack selection
T7's paks are shared numbered chunks, not per-character files, so
DepotDownloader filelists cannot isolate Law/Lars at the depot level.
`t7-law-lars.txt` and `t7-full-roster.txt` pull the paks (`regex:.*\.pak$`,
same pattern as `paks-only.txt`); fighter isolation happens post-unpack via
in-game `Game/Character/Items/Mesh/<CODE>/` paths, or user-side via the new
`t7-find-character-paks.bat` (repak list + 3-letter-code grep) so the user
uploads only the paks that matter instead of ~47 GB.

## Extraction pipeline documented
`teardown/tekken7/T7-STEAM-EXTRACTION.md`: repak unpack (no key) → asset
identification (community-verified paths + character codes) → umodel batch
export / FModel (Windows-or-Wine step) → Blender UEFormat → FBX/GLB →
moveset-library. Moveset-logic caveat kept honest: T7's native moveset binary
format is not publicly documented — assets come from the paks, frame data
continues from the existing `docs/t7t8-reference/frame-data-t7/` banks +
TTT2/T3 lanes.

## Disk
Full T7 depot ≈ 47 GB; VM has ~20 GB free. Pull does not run here.
DISK-RULES apply to whatever comes back: extract → convert → delete paks.

## Blocking on the user
1. Run T7-USER-STEPS.md (Path A if T7 installed, else Path B) — Law/Lars first.
2. Tell us the upload destination (GitHub release link or shared location).
