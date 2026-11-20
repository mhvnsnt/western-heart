# PANTERA — Attire Slots (owner 2026-10-17; REORDERED owner 2026-10-21)

Canonical slot map. Slot ORDER is the law below; everything gets built and wired
at the same time — ordering is about slot positions, not schedule.

**2026-10-21 REORDER (owner, verbatim):** "his entire one, two, three, four,
five, they should be his like triple models and those reskins of the Tekken
version should be towards the back and not one or two or anything so you can
stop showing me those and start showing me the right models the triple 3D
models I put in for him and made for him I would much rather see those"
("triple" = Tripo, voice-to-text). His Tripo originals now lead the ladder;
every Tekken-version reskin ladders behind them. This supersedes the
2026-10-17 Pantera exception (the T7King reskin at Slot 1) and the
2026-10-20 swap.

**AUDITED TRIPO INVENTORY:** Pantera has exactly **TWO** Tripo originals on
record — Leo man and Leopard King (census `docs/ROSTER-COUNT-CANON-2026-10-21.md`:
"Per-fighter distinct pulls: Pantera 2"; `roster/TRIPO-REGISTRY.md` Pantera
row). No third, fourth, or fifth Pantera Tripo model exists in the registry,
the GitHub releases, or the roster docs, and none was invented to fill slots
3–5. If the owner pulls more Pantera Tripo models, they take the next front
slots in arrival order and the reskins shift back.

## The locked slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Leo man** | `attires/leomon/model.glb` (4,414,284 B) — **TRIPO ORIGINAL.** Owner-confirmed 2026-10-19: "Leo man is the tripo model for that attire slot 2, the one we had in game for so long and the original tripo model and the one we put in the pictures." The lion-head Leomon attire, RENAMED "Leo man" (proprietary to our universe). **PROVENANCE (owner correction 2026-10-20): the model came from Google Drive — it was NOT pulled through a Tripo URL**, so it carries no Tripo UUID. Wired build = lab build `pantera_leoman_t3real` — WH-Canonical-22 rig with the real decoded Tekken 3 King clips embedded (`king_on_pantera_leoman` bank baked on this exact rig): fully rigged, not a statue. Owner's untouched Drive original (23,645,536 B) + the canonical build are backed up in release `leoman-restore-20261020`. NOTE: directory is still `leomon/` on disk. Display name is "Leo man" everywhere the player sees it. **At Slot 2 until the 2026-10-21 reorder moved it to Slot 1.** |
| 2 | **Pantera — Leopard King** | `attires/leopard-king/model-refit.glb` (32,679,076 B; re-rig 2026-10-22: King's skeleton fitted inside the mesh + bone heat, proof `docs/proof/claude-2026-10-22/pantera-rigs/`) — previous build `attires/leopard-king/model-rigged.glb` (81,618,172 B) kept beside it — **TRIPO ORIGINAL**: https://studio.tripo3d.ai/3d-model/094c2f37-1c61-43fb-82ff-7124100a1021 ("tiger humanoid" by jaywillf69). Raw static pull (23,362,216 B, 1 mesh / 3 textures, meshopt-compressed) kept at `attires/leopard-king/model.glb`. Snow-leopard head with fangs bared, spotted white/black rosette tights, spotted tail with dark tip, big spotted paw gloves, spotted boots with black trim. Rigged build = canonical 49-joint Pantera/King template + 4-bone tail chain (Tail1–4, skinning follow; no authored tail animation exists), PR #493 (2026-10-21, supersedes the rejected 2026-10-20 rig; the 2026-10-20 build stays in git history + release `pantera-leopard-king-rigged-20261020`); see `attires/leopard-king/WORKLOG.md`. Render at `docs/tpose-refs/pantera-leopard-king/p1_front.png`. Added 2026-10-19; **at Slot 4 until the 2026-10-21 reorder moved it to Slot 2.** |
| 3 | **Pantera (P1 Original)** | `docs/tpose-refs/pantera-t7king/pantera-t7king.glb` — game key `pantera` (`game/assets/models/pantera.glb`). The full-res Tekken 7 King reskin (14.7MB, 19 meshes / 19 materials / 54 embedded images). Black panther mask, yellow eyes, purple tights, black trunks with red PANTERA. His first attire historically (he did the reskin first) — but it IS a Tekken-version reskin, so per the 2026-10-21 order it ladders behind his Tripo originals. **Was Slot 1.** (The base `pantera` model key itself is untouched — the souled vessels ride it.) |
| 4 | **Pantera — Snow Leopard** | `attires/snow-leopard/pantera-snow-leopard.glb` (7,434,348 B) — reskin of the older classic build per owner 2026-10-17: purple tights → blue, black panther head → white with snow-leopard rosette spots, yellow eyes → blue, nose → pink. Same T7 King P1 source (NOT T6 PSP), Mixamo rig intact, trunk/boot/glove design untouched. Original classic kept at `attires/classic/pantera-classic.glb` (also in git history) — archive of the pre-reskin build, never itself a wired slot. **Was Slot 3.** |
| 5 | **Pantera — Crimson Rage** | `attires/crimson-rage/pantera-attire5-crimson.glb` (14,675,572 B) — custom build via the Creation Suite (2026-10-18) on the T7 King base: deep crimson tights (custom composite, not a hue shift), black panther + RED scratch-marks decal from `customization/decal-library/pantera/` composited at the canonical placement (rect x=176,y=34,w=186,h=390 in 512×512 King_PantsLower_D), black trunks with red PANTERA, yellow tiger eyes from `customization/eye-library/` (owner's "I like" variant). Texture-only — zero rig/geometry changes (PANTERA RIG RULE). Render at `docs/tpose-refs/pantera-crimson-rage/p1_front.png`. **Slot unchanged.** |
| 6 | **Pantera — T7 P2** | `attires/p2-wired/pantera-attire4-p2.glb` (14,548,052 B) — the official Tekken 7 Player 2 scheme wired onto the T7King base GLB (P2 diffuse pack at `attires/p2/`): black tights with bronze tribal, black trunks with bronze KING logo, black boots with red trim, red/black gloves. Arms/gloves/mask unchanged (P2 keeps them). Render at `docs/tpose-refs/pantera-attire4-p2/p1_front.png`. Added 2026-10-18 at Slot 4; moved to Slot 6 on 2026-10-20; **slot unchanged by the 2026-10-21 reorder** (the filename keeps its historical `pantera-attire4-p2.glb` name). |

## Slot-ordering law (owner 2026-10-17; Pantera reorder owner 2026-10-21)

- **Early slots:** Western Heart / Eastern Mind-based attires — the forefront, original designs.
- **Later slots:** Tekken-based attires (ports, recolors, ripped variants).
- **Pantera (owner 2026-10-21):** his Tripo originals take the front slots in arrival order (Leo man, then Leopard King); ALL Tekken-version reskins — including his own first T7King reskin — ladder behind them. Proof renders and select-screen presentation lead with the Tripo models, never the reskins.
- All attires get done and wired up at the same time; the law only governs slot positions.
- Every attire goes through the Tekken character customizer + customization suite to be modified and made proprietary. The owner does the creative customization himself — slots are wired clean, no creative changes by agents.

## Backlog — extra King attires to pull and wire (later Tekken slots)

- **Tekken 3 King** — retro alt (per IDENTITY.md: "Tekken 3 as retro alt"). Model on hand; needs attire wiring.
- **Other in-game King attires** — pull every extra attire the games' Kings ship with, attach and modify as later slots.
- **PANTXRΛ-88 (cyborg)** — `attires/cyborg/CYBORG-88.md` concept on file; assets pending heavy-Leomon source. Western Heart-based → early slot when built.

## History

- 2026-10-17: slots defined by owner; forensics confirmed Slot 3's source is T7 King P1.
- 2026-10-17: Slot 3 reskinned to Snow Leopard colorway (blue tights / white rosetted head / blue eyes / pink nose); render at `docs/tpose-refs/pantera-snow-leopard/p1_front.png`.
- 2026-10-18: Slot 4 (T7 P2 scheme) + Slot 5 (Crimson Rage, custom Creation Suite build) wired in by the Pantera custom-attires lane. Renders own-eyes verified.
- 2026-10-19: CORRECTION — owner confirmed Slot 2 "Leo man" IS Pantera's ORIGINAL Tripo model (in-game for so long, the one in the pictures); the "NOT ON RECORD" registry note was wrong. Slot 6 "Leopard King" (Tripo 094c2f37) wired. Render own-eyes verified.
- 2026-10-20: Slot 2 RESTORED — `attires/leomon/model.glb` pushed (MODEL_URLS `pantera-leoman`, ATTIRE_VARIANTS Pantera Attire 2), fresh front T-pose ref rendered from the restored model; provenance corrected to owner-provided via Google Drive (see above).
- 2026-10-20: OWNER SLOT SWAP — Leopard King pushed up from Slot 6, swapped with Slot 4: Slot 4 = Leopard King (Tripo), Slot 6 = T7 P2. Leopard King rigged the same day (see `attires/leopard-king/WORKLOG.md`). Pure reorder — all six attires remain wired; nothing deleted.
- 2026-10-21: OWNER REORDER — TRIPO-FRONT (verbatim order at the top of this file). New order: Slot 1 = Leo man (Tripo), Slot 2 = Leopard King (Tripo), Slot 3 = T7King P1 reskin, Slot 4 = Snow Leopard, Slot 5 = Crimson Rage, Slot 6 = T7 P2. Supersedes the 2026-10-17 Pantera exception. Audit first: exactly two Pantera Tripo originals exist on record (registry + 2026-10-21 census) — slots 1–2 are Tripo; the reskins keep their previous relative order behind them. Both Tripo models were already rigged and wired, so no rig work was needed. Pure reorder in `game/js/attires.js` (default attire = first entry = Leo man); all six attires remain wired; nothing deleted.
