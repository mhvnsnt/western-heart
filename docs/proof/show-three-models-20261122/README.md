# Show the owner his three models — proof renders (2026-11-22)

The owner did not believe the Lane F model audit's claim that Cornerstone,
Scimitar, and Chordz were missing models. He asked to SEE the models. These
are front-view renders of the actual GLB files on main, rendered with the
repo's own three.js + GLTFLoader (Meshopt decoder). No AI, no stand-ins —
every pixel is the file in the repo.

## The images

| Image | Model file on main | What it shows |
|---|---|---|
| `cornerstone-front.png` | `roster/ryuji-rock/attires/attire1/model-rigged.glb` (29,112,760 B; Tripo 20c1fd2e-40d0-4500-9be6-50f6494ab5e1) | CORNERSTONE — Yamazaki x The Rock: black shirt, blonde top hair, gold chain, big gold bull belt buckle. Matches canon (`roster/ryuji-rock/CANON.md`). |
| `scimitar-front.png` | `roster/scimitar/attires/attire1/source/scimitar-a1-rigged.glb` (19,132,660 B; owner's Tripo pull a3e76dd5) | SCIMITAR — the desert vizier: bare chest, long black wavy hair, goatee, gold spiked shoulder armor, curved scimitar at the waist, white-and-gold harem pants, curled-toe shoes. Scar x Jafar, Shaheen soldier frame. Matches canon (`roster/scimitar/CANON.md`). |
| `chordz-front.png` | `roster/chordz/attires/attire1/model-rigged.glb` (28,753,932 B) | CHORDZ — the emo guitarist: black strapped leather, tall lace-up boots, wild spiky black hair, pale face with dark eye makeup. Matches canon (`roster/chordz/CANON.md`). |
| `chordz-p1-edward-scissorhands-front.png` | `roster/chordz/transformations/phase1/source/chordz-p1-edward-scissorhands.glb` (20,735,052 B; Tripo f9a71d52-20b7-43dd-a819-d8c21fe5dfda; md5 `7710f5b90ff89cef155444a428302c32` = manifest) | CHORDZ phase 1 — the Edward Scissorhands look: same emo guitarist, long silver scissor-blades shooting out of both hands. This is the "Cuts" look. |

## The Cuts / Chordz answer (from the files)

- There is **no `roster/cuts` directory and no `cuts` entry in
  `game/js/roster-full.js`** — "Cuts" is not a separate fighter in the files.
- **Chordz IS the Edward Scissorhands guy.** His phase-1 transformation
  file is literally named `chordz-p1-edward-scissorhands.glb` and its
  manifest says: "Stage 2: blades shoot out of his hands (Edward
  Scissorhands)". "Cuts" is the name for Chordz's blade form, not a second
  fighter. No mix-up between two fighters — one fighter, one blade form.
- **Kutz is a different fighter** (Goh Hinogami, the emo punk / moshpit
  maniac, Chordz's tag partner — see `roster/chordz/CANON.md`). Do not
  confuse Kutz with Cuts/Chordz.
- Chordz's other blade forms, also in the repo: phase 2
  `chordz-p2-blade-spikes.glb` (spiked ball of blades instead of hands) and
  final `chordz-final-cutter-who-strums.glb` (Batman Who Laughs with knives
  all over). All three are archive-only, not wired into MODEL_URLS.

## DEFECT: Scimitar's wired file renders NOTHING when skinned

`scimitar-front.png` above was rendered with the skin bypassed (bind-pose
geometry only). Rendered normally — the way the game loads it — the file
shows **nothing at all**: `scimitar-skinned-BLANK-evidence.png` (flat grey,
5,290 bytes).

Measured cause: the file's skin is broken. Its skinned bounding box is
min `[7477, 4.7, 2119]` max `[136113800, 149112601, 38920884]` — the skin
explodes the 1.26M-vertex mesh to ~136 MILLION units, so nothing is ever on
screen. The geometry itself is fine (bind-pose box is a correct 1.8 m).
The auto-rig (`tools/auto_rig/rig_tripo_static.py`) produced a bad skin for
this file; the same tool's output renders fine for Cornerstone and Chordz.
**Fix owed: re-rig `scimitar-a1-rigged.glb`.** Until then, the game loads a
Scimitar that is invisible.

Related render note: the same auto-rigged files carry stored bone
transforms that deform the mesh on load (rendered legs 2–3x too long); the
renders here reset bones to bind pose with `pose()` first. The game should
be checked for the same deformation on Cornerstone / Chordz.

## Stale canon notes (for a later cleanup, not this PR)

- `roster/chordz/CANON.md` and `roster/scimitar/CANON.md` still say "no
  MODEL_URLS key / blocked on model" (2026-10-23). Both ARE wired now
  (`game/js/assets.js`: `chordz` line 566, `scimitar` line 435). The CANON.md
  files are out of date, not the wiring.

## How the renders were made

Workdir `~/workspace/_show-three-models-20261122/` (CHECKPOINT.md there):
GLBs pulled from main via git promisor fetch (`git cat-file blob`),
rendered in headless Chromium with the repo's own
`game/vendor/three.module.js` + `GLTFLoader.js` + `meshopt_decoder.js`
(all `EXT_meshopt_compression`), front view, fit-to-bounding-box, 1280x900.
