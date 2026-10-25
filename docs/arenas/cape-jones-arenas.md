# Cape Jones Arenas — design doc (game stages first)

Owner directives 2026-10-24 20:35 + 20:38 CDT (standing, in MEMORY.md),
plus the coordinator's stage-id confirmation (music-wiring PR #1072).
Scope law 2026-10-24 20:51 CDT (GAME FIRST): this doc is about the two
GAME stages. Show references exist only where they feed the game (shared
assets, arena designs that become game stages). The show-location log is
a DOC NOTE in this file and in `docs/arenas/cape-jones-show-locations.md`
— not show-production work. No room shots, show renders, closet work, or
show-episode production enter this lane; show-only work stays in Claude's
lane / the show repo.

Show-facing naming law (non-negotiable): in Ep 1 the game appears as
**IMMORTAL QOMBAT**, never "Western Heart". Every show-facing sentence
in this doc follows that law. Repo/dev contexts say Western Heart.

## The two arenas

| Arena | Stage id (LOCKED, coordinated) | Tier | Builder | Home fighter |
|---|---|---|---|---|
| Cape Jones Arena (home turf) | `cape-jones-arena` | CAPE JONES | `capehouse` | `cyborgx` (CAPE JONES) |
| Halloween Beach (show-based) | `cape-jones-halloween-beach` | CAPE JONES | `capebeach` | `cyborgx` (CAPE JONES) |

Stage-select wiring: both defs live in `game/js/stages.js` STAGES, tier
`CAPE JONES` is in STAGE_TIERS (after CANON LANDS), and `main.js`
`buildStageSelect` renders every tier in STAGE_TIERS — no `main.js`
change was needed. Cards render with the palette swatch until thumb
atlas tiles exist (the atlas fallback path, same as every other stage).

### Stage-id confirmation (coordinator question, answered)

1. YES — `cape-jones-halloween-beach` is the beach arena's stage id. It
   is the id in the stage def, in the def's `musicStageId` field, and in
   `test/cape-arenas.test.mjs`. It matches the id music-wiring PR #1072
   already tags on its 8 new tracks. NO retag of the id is needed before
   #1072 merges. House/home turf keeps the existing audio-lane tag
   `cape-jones-arena`, which PR #1037's library already uses.
2. Tagging ownership: the AUDIO lane (music-wiring, PR #1072 / #1058)
   owns `game/data/music-library.json` and adds the beach tag — NOT this
   lane. This lane owns `game/js/stages.js` only, and touching the
   library would collide with #1072's open diff. The coordination gap,
   stated plainly: #1072's own test logs it as a NOTE, not a failure —
   the beach pool is Ghost-first ONLY once all 8 shipped Cape tracks
   carry the `cape-jones-halloween-beach` tag. Until the audio lane adds
   it, the beach pool's tagged section is the 8 new tracks (Cape vibe,
   not Ghost-first). The 8 shipped tracks needing the tag:
   `cape-jones-ghost-surf-rock`, `cape-jones-ghost-waltz`,
   `cape-jones-hello-regan`, `cape-jones-dark-alley`,
   `cape-jones-graveyard`, `cape-jones-old-witch-place`,
   `cape-jones-witch-magical`, `cape-jones-sweat-time`.
   Merged-pool figure (audio lane's): 48 tracks = 32 battle + 8 Cape +
   8 new. (#1072's test comment counts 52 library entries = 44 on main
   + 8 new; the two figures differ by scope — library vs battle pool.)

## Arena 1 — Cape Jones Arena (home turf)

Directive: "tied to his house — the arena is like / set at Cape
Jones's house (his home turf)". Canon grounding: CANON.md §6 CYBORG X
(Cape Jones IS Cyborg X, first attire / main look; he flew through the
TV into the game) and `docs/HANDOFF-CAPE-JONES-X-WESTERN-HEART.md`
("Cape's house/room/neighborhood = a WH stage AND the show's setting;
in both canons Cape plays the game at home and flies in through the
TV"). Spec source: `stages/cape-house/STAGE-SPEC.md` (spec only, not
previously wired into stage select — this PR is the wiring it deferred).

HOUSE-READING CAVEAT (explicit interpretation, correctable): this def
plays the fight IN THE HOUSE SET at standard WH bounds (16.8 wide,
wallDistance 8.4, spawns ±3.5). The canon room scale in STAGE-SPEC.md
is 7.0 x 6.0 m (show-room scale, variant 1: closed walls = wall-splat
walls, furniture pushed to the edges). If the user corrects the reading
to literal room bounds, `dims` is a one-line change — the set dressing
does not move. Report corrections against this paragraph.

Set (builder `capehouse`): back + side walls (closed room), sofa +
coffee table pushed to the edges, CRT TV portal prop (glowing flickering
screen — the way in through the TV), LED wash strip along the back wall,
and the recliner EMPTY, stage-right edge. The recliner stays empty per
the canon .blend constraint (SCENE-CANON.md: recliner stays empty until
the light-flicker gag rig lands) — no figure is ever seated there.

Lighting: dusk interior. Sky (barely visible above the room)
`[[0.0,'#0a0812'],[0.5,'#1c1226'],[0.8,'#3a2030'],[1.0,'#120a14']]`,
fog `['#120a14', 18, 60]`, hemi warm `['#8a7a6a','#241a12',1.5]`, sun
warm window light `['#ffc890', 2.0, [-8,7,5]]`, grade exposure 1.4,
bloom 0.6. Floor kind `dark`, tint `#5a3a24`. Swatch
`['#1c1226','#ffc890']`.

Music pool: Ghost Surf Rock FIRST + interchange rotation, via the
`cape-jones-arena` tag the audio lane already carries (PR #1037 library
+ #1072 new tracks). Main track: Ghost Surf Rock — Loyalty Freak Music,
04:07, CC0, surf rock + spooky + witchy + batty + Halloween.

## Arena 2 — Malakor-style Halloween Beach (show-based, distinct)

Directive: a SECOND Cape Jones show arena, based on his show, distinct
from the house arena. Theme: Halloween beach, Malakor-style dark fantasy.
Malakor reference (read first: `~/memory/people/malakor.md`): TikTok
creator, dark fantasy AI art — hooded figures, floating eyes, medieval
mysticism, cosmic horror, deep purple + blue palettes, alchemical/occult
symbols (user-approved for the game's visual identity). The sunra stage
already cites the same reference (`@obruxomalakor`, occult grimoire
aesthetic, sigil rings) — this arena extends that vocabulary to a beach.

Vibe: matches the Ghost Surf Rock description — surf rock + spooky +
witchy + batty + Halloween, fun-spooky like a Scooby-Doo Halloween beach
(spooky-fun mystery, NOT grimdark). Bright surf accents (surfboards,
grinning jack-o-lanterns) carry the fun against the dark sky.

SKY — LOCKED (arena color/lock law): DARK PURPLE, user's color
reference "lean-colored" — heavy, thick, dirty purple sky (thick
atmosphere, NOT clean bright purple). Once built, this look is LOCKED:
any later change needs the user explicitly saying so. Do not brighten
or clean it up. Exact locked values (asserted by
`test/cape-arenas.test.mjs`, exact-match):

- Sky stops: `[[0.0,'#0d0716'],[0.45,'#241038'],[0.72,'#3d1c4e'],
  [0.88,'#4a2444'],[1.0,'#160a1e']]` — every stop dark and muted, the
  lightest stop (`#4a2444`) still murky, green never dominant.
- Fog (thick atmosphere): `['#1c0f2a', 14, 55]`.
- Hemi: `['#4a3560','#140a1c',1.2]`. Sun (dim murky moonlight):
  `['#9a7aaa', 1.1, [-8,9,4]]`. Rim: `['#5a4a9a', 0.7, [8,6,-7]]`.
  Fill: `['#7a5a8a', 0.5, [0,4,10]]`. Grade: exposure 1.1, bloom 0.6
  (dim on purpose — never brightened to "fix" visibility).
- Floor: kind `sand`, tint `#7a6278` (dusky purple-grey over sand),
  platformTint `#8a7088`. Swatch `['#241038','#ff8a3a']` (dark purple +
  jack-o-lantern orange).

Set (builder `capebeach`): surf water plane + foam line at the back,
dunes, palm silhouettes, surfboards stuck in the sand, sandcastle,
grinning jack-o-lanterns (flickering point light), hooded Malakor
figures watching from the dunes, floating eyes over the surf (the
game's own `makeEyeTexture`, as in the Phantom Marketplace), an
alchemical/occult sigil ring on the sand, and flapping bats
(mobile: 3, desktop: 6).

Music pool: Ghost Surf Rock rotation — Ghost Surf Rock as main track,
interchange tracks rotating around it — via the
`cape-jones-halloween-beach` tag (audio lane, see confirmation above).

## Wizard-gang tie-in

The beach arena carries the owner's own catalog connection: it was
researched for the game + wizard gang (owner's own shows) + Malakor
reference, per the 20:35 directive. Channel-flip contents are the
owner's own catalog — TRIPPEDD, wizard gang, other shows, bumps, cards,
segments, commercials. NO outside programs. What is asserted here is
only the shared-catalog log entry (below): the beach is a location
usable across the owner's catalog (Cape Jones show + wizard gang
shows). NO wizard-gang-specific set elements, characters, or lore are
asserted in the arena — none were supplied, and none are invented here.
If the owner names wizard-gang set elements, they land as a follow-up
edit to this doc + the builder, not as a guess.

## Show-location log (DOC NOTE, game-first)

The beach arena is LOGGED as a future Cape Jones show location:
somewhere Cape Jones chills at in his 3D show at some point — not just
a game stage, a show place. The log lives in
`docs/arenas/cape-jones-show-locations.md` (one entry; mirror it into
the cape-jones repo's environments docs from there if the show lane
wants it — that mirror is show-repo work, not this lane's). Western
Heart ↔ Cape Jones show connection, as recorded in the handoff: WH is
connected to the Cape Jones show a little bit, through multiverse
canon — Cape plays the game at home (in show-facing terms, IMMORTAL
QOMBAT) and flies in through the TV.

## Asset status — real vs pending (nothing silent)

v1 rule: neither def names an `obj` / `glb` / `pano` / `map` asset, so
Lane 5's `preloadStage` warms nothing and fight-load has NO arena-asset
404 surface. The v1 set is built by the builders in the established
canon-stage style (the same `buildBase` sky/floor/lighting + set
dressing pattern every canon stage uses). That is the PLAYABLE wiring,
and it is NOT presented as shipped real assets. Per-element status:

| Element | Status | Source / unblock path |
|---|---|---|
| House set (walls, sofa, TV, LED, recliner) | PLAYABLE v1 set in code; real GLB PENDING | `mhvnsnt/cape-jones:3d-assets/living_room.blend` → export `blender -b living_room.blend` → `stages/cape-house/living-room.glb` (STAGE-SPEC.md export path; never save over the .blend). Coordinator browser lane: the export runs in the cape-jones repo (Blender), then the GLB lands in WH via a follow-up PR that adds the `glb` field + GLB-with-fallback builder (buildHelix precedent). Palette then comes from SCENE-CANON.md (owner-locked) as carried by the .blend. |
| House exterior / kitchen / bedroom / neighborhood | GAP (spec says no 3D yet) | `cape-jones:docs/environments/HOUSE-DESIGN.md` (single-story ranch, beach suburb) — needs a teardown street stage or existing repo street kit as base (STAGE-SPEC.md next step 3). NOT in this PR. |
| Beach set (water, dunes, palms, boards, castle, lanterns, hooded figures, eyes, sigil, bats) | PLAYABLE v1 set in code; real prop GLBs PENDING | Open source, verified by search (not a visit): reodesuxz "Low Poly Beach Lifeguard & Boardwalk Pack" — https://reodesuxz.itch.io/low-poly-beach-lifeguard-boardwalk-pack — 27 models, FBX/GLB/OBJ/.blend, free for personal and commercial projects, no attribution required, do-not-resell. Contents cover lifeguard tower, boardwalk, umbrella, chair, towel, beach ball, sandcastle, surfboards + rack, palm tree, cooler, shells, starfish. Coordinator browser delegation: download the pack (itch.io download flow needs a browser session), place GLBs under `game/assets/stages/cape-beach/` (inside `game/`, so no proxy rule is needed), then a follow-up PR wires them through the gltfpack pipeline below. |
| Beach pano / sky texture | PENDING (sky gradient carries the locked look until then) | GPU job pack: render a 360 beach pano from the landed prop GLBs on the Kaggle/Colab pipeline, OR source a CC0 beach pano (Poly Haven / ambientCG, CC0). Do not ship a guessed URL. |
| Ghost Surf Rock rotation MP3s | PENDING browser download (audio lane) | Free Music Archive, Loyalty Freak Music, "WITCHY BATTY SPOOKY HALLOWEEN IN SEPTEMBER !!" collection. #1072 credits mark the new files PENDING with engine fallback to the procedural loop until they land. Audio lane owns the downloads + library tags. |
| Thumb atlas tiles for both arenas | PENDING (swatch fallback renders today) | `tools/stage-arena-pull/render_gallery.py` pattern: render own-eyes shots once the stages are live, add tiles to `assets/stages/thumbs/atlas.png` + `atlas.json`. Select cards are fully playable on swatches meanwhile. |

No Tekken/WWE names appear in canon writing anywhere in this PR; the
only game-file names are technical (builder names, file paths). All
characters are adults. No combat inputs are touched, so the LP1/RP2/
LK3/RK4 button naming law has no surface in this diff (playtest steps
below use the FIGHT button only).

## Fight-load / Netlify (verified by code, not by playing)

- v1 arenas fetch ZERO external assets: no `obj`/`glb`/`pano`/`map`
  fields, no texture loads outside `buildBase` canvas textures. There is
  nothing arena-side that can 404 at fight load. (Fighter models and
  music files are other lanes' paths and are out of this claim.)
- Preventive rule added NOW, mirrored in both files (test asserts both):
  `/stages/* → https://mhvnsnt.github.io/western-heart/stages/:splat 200`
  in `game/netlify.toml` and `game/_redirects`. Why: the future
  `stages/cape-house/living-room.glb` lives at repo root `stages/`,
  OUTSIDE the Netlify publish root (`game/`). Without this rule the
  Netlify build would 404 that GLB at fight load even though GitHub
  Pages serves it. Existing rules cover `/roster/*`, `/customization/*`,
  `/packages/*`, `/game/*` only. v1 does not need the rule; the GLB
  landing does. The gh-pages path needs no rule (repo-root paths serve
  as-is).
- Lane 5 integration (PR #1061, open): neither def declares
  `breakables`, so `stage-levels.js` gives both the generic treatment
  (upper + wall-broken 8.4 → 12.9 per the stagebreaks wall default) once
  #1061 merges. `preloadStage` (Lane 5, wired at the stage screen and at
  fight start) warms whatever fetchable assets a def names — for v1,
  none — and never throws. This PR is based on main WITHOUT Lane 5's
  files, so it merges independently of #1061; the 3-way merge lane
  reconciles the `stages.js` overlap (builders + defs vs preload code)
  when both are green.

## GPU job pack (prepared, NOT run — no times claimed)

`tools/cape-arenas-gpu/` carries the run sheet + `cape-gpu-jobs.py`
(gltfpack batch with Lane 5's pinned flags: `-cc` always, `-kn` only
for skinned fighters — stage props are unskinned, so no `-kn`; `-tc`
only if the output measures smaller; simplification allow-list only,
never a skinned fighter blind). Every job records nvidia-smi +
torch.cuda proof, input bytes, output bytes, wall time, AND CPU-baseline
time — the script writes those fields into its report JSON at run time.
No GPU job has been run for this lane and NO time is reported here:
there are no cape input GLBs yet (house export + beach pack both
pending), so there is nothing honest to measure. Coordinator GPU
delegation (Kaggle T4 x2 notebook
https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit, Colab as
overflow — switch, never stop; jobs queue continuously):

1. When the beach pack lands: run `cape-gpu-jobs.py` over
   `game/assets/stages/cape-beach/*.glb` → optimized outputs +
   report JSON with all proof fields. CPU baseline: re-run the same
   manifest with `--cpu-baseline` and attach both times.
2. When `living-room.glb` lands: same batch (unskinned room props;
   keep bone names out per the stage-prop rule).
3. Real-ESRGAN upscale batch for the beach pano + prop textures (Lane
   5's `tools/gltfpack/gpu/esrgan-upscale.py` pattern: CUDA required,
   fails loudly without weights) — inputs pending, same proof fields.
4. Card pre-renders for both arenas (thumb atlas tiles) + LOD
   generation for the beach prop set, same pipeline, same proof.

## Live playtest — parent browser delegation (NOT claimed)

This lane has no live browser. The coordinator's browser lane runs this
pass on the PUBLIC playable site (gh-pages path; the Netlify site
endearing-scone-b3d816.netlify.app is public, no dashboard login — per
the corrected standing note, never request a Netlify token). Phone
portrait mode, navigate like a human (screenshot, look, scroll, THEN
tap — never jump via selectors). Moving shots = VIDEO, not stills.

1. Load the site → menu → fighter select → pick any fighter → stage
   select → scroll to the CAPE JONES tier → tap CAPE JONES ARENA →
   FIGHT → fight one round. VIDEO proof: house set visible (walls, CRT
   TV glow, LED strip, empty recliner), and — once the audio lane's
   MP3s + tags land — Ghost Surf Rock audible as the main track.
2. Back to stage select → tap HALLOWEEN BEACH → FIGHT → fight one
   round. VIDEO proof: dark purple lean-colored heavy/thick/dirty sky
   (NOT brightened), beach + surf, Halloween elements (lanterns,
   hooded figures, floating eyes, sigil ring, bats), Malakor-style
   mood, spooky-fun (not grimdark), and — once the audio lane's MP3s +
   beach tags land — Ghost Surf Rock rotation audible.
3. If either arena 404s, fails to load, or the sky reads bright/clean
   purple: STOP, screenshot + video the failure, and report it as a
   failed verification — do not describe the arena as verified.
4. Audio caveat for the playtest lane: until the audio lane's MP3s land
   and #1072 (or its follow-up) tags all 8 shipped Cape tracks with
   `cape-jones-halloween-beach`, the beach fight will NOT open with
   Ghost Surf Rock (engine falls back to the procedural loop / the 8
   new tracks' pool). That is the audio lane's pending item, not a
   failure of these stage defs — log exactly what was heard.
