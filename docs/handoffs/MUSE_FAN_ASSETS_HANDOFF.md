# Muse handoff: public collection for Western Heart

**Assigned to:** Muse (Ashes)  
**Assigned by:** Owner via Grok Bot, 2026-10-14  
**Repo:** `mhvnsnt/western-heart`  
**Board:** `mhvnsnt/agent-ops` TAG-TEAM row (this handoff)  
**Workflow:** follow `docs/agent-handoff/PRODUCERBOT_WORKFLOW.md` when that PR is on main (open as [western-heart #128](https://github.com/mhvnsnt/western-heart/pull/128)); also follow the media proof standard there.

## Start immediately

**Start now. Run in parallel with Grok Bot, Repo Co Dev, and the other agents.**

Do **not** wait for models, animations, teardown wiring, or the creation suite to finish. Those are owned by other agents.

### Hard do-not-touch (other agents' claims)
- Teardown wiring / importers / extraction scripts under `teardown/`
- Creation suite under `docs/creation-suite/` and `customization/`
- Physics sandbox / jiggle / Lab physics files
- Model perfection, weight-paint repair, and animation retarget work already claimed elsewhere

Your work is **additive docs + catalogs + private binary storage + contact sheets only.** Small PRs. Push incrementally.

---

## Mission (four tracks)

Collect public, reuse-safe material that feeds Western Heart's move-set editor, creation suite (later), and modeling/motion reference. Four tracks:

| # | Track | Where it lands |
|---|---|---|
| 1 | Free public frame data, move lists, combo guides, stage layouts | Extend `docs/t7t8-reference/` (CC0 sources copied into git; non-CC0 = links only in `REFERENCE_SOURCES.md`) |
| 2 | Fan-made, reuse-licensed fighter models, stages/arenas, fighting animations | Catalog in `docs/fan-assets/`; binaries as private `mhvnsnt/box-storage` release assets |
| 3 | Reference images and videos as links (modeling + motion) | Per-character / per-move catalogs under `docs/fan-assets/references/` |
| 4 | Placeholder for owner's own T7/T8 extractions | Stub under `docs/t7t8-reference/OWNER_EXTRACTIONS.md` — fill only when the owner hands over files, then treat like other teardowns |

---

## Track 1 — Public frame data / move lists / combos / stages

Extend what PR [#127](https://github.com/mhvnsnt/western-heart/pull/127) started (`docs/t7t8-reference/`).

- Prefer CC0 / public-domain dumps you can copy into git (e.g. Wavu wiki frame data already in flight).
- For sources that are **not** CC0: record URL, license note, and what it covers in `docs/t7t8-reference/REFERENCE_SOURCES.md`. **Do not** paste copyrighted text or tables wholesale.
- Combo guides: link + short summary of useful routes; no full copyrighted guide text.
- Stage layouts: dimensions, hazards, camera notes as structured JSON/MD you author from public facts, with source links.
- Keep `wh_body_map.json` in sync when you add fighters.

---

## Track 2 — Fan-made reuse-licensed models / stages / animations

### Allowed sources
- Sketchfab: **downloadable** items licensed **CC0 / CC-BY / CC-BY-SA** only
- Mixamo (Adobe) free animations (credit Mixamo; follow their current terms)
- OpenGameArt, Poly Haven, itch.io free packs with explicit reuse licenses
- Open motion-capture datasets with clear licenses (e.g. CMU mocap derivatives that allow reuse)

### Exclude (hard)
- Rips or extractions of official **Tekken** or other commercial game files, even if someone tagged them CC
- Anything whose description, tags, or mesh topology make it obvious it is a game dump
- "Free download" model sites that redistribute ripped game assets without a creator license
- When in doubt: skip, log the URL under `docs/fan-assets/REJECTED.md` with the reason

### Per-item record
For every accepted item, add a row to `docs/fan-assets/CATALOG.md` **and** an object in `docs/fan-assets/catalog.json`:

| Field | Required |
|---|---|
| `name` | yes |
| `url` | yes (canonical page, not a CDN hotlink) |
| `author` | yes |
| `license` | yes (exact SPDX or Sketchfab label) |
| `poly_count` | yes (triangles or verts; say which) |
| `format` | yes (glb / fbx / obj / bvh / …) |
| `category` | `fighter` \| `stage` \| `animation` |
| `sha256` | yes once binary is in box-storage |
| `box_storage_release` | yes (tag + asset name) |
| `wh_move_slots` | for animations: list of WH slots (see mapping below) |
| `credit_line` | yes (paste-ready for CREDITS.md) |

### Storage rule
- **Binaries:** private `mhvnsnt/box-storage` release assets only. Record SHA-256.
- **Git:** manifests, catalogs, contact sheets, credits — no large meshes/anims in western-heart git.

### Credits
Append every CC-BY / CC-BY-SA credit line to `docs/fan-assets/CREDITS.md` (create if missing). CC0 still gets a courtesy attribution line.

### Animation → WH move slots
Map each accepted animation to Western Heart move slots used by the move-set editor / practice mode. Use these slot ids (extend the list in the catalog if you need more, and note why):

`idle`, `walk_fwd`, `walk_back`, `dash_fwd`, `dash_back`, `crouch`, `jump`, `block_high`, `block_low`, `hit_standing`, `hit_crouching`, `knockdown`, `getup`, `jab`, `straight`, `hook_l`, `hook_r`, `uppercut`, `low_kick`, `mid_kick`, `high_kick`, `sweep`, `throw_attempt`, `throw_break`, `special_1`, `special_2`, `rage_art`, `victory`, `defeat`, `entrance_idle`

Put the mapping on each animation object in `catalog.json` as `wh_move_slots: ["jab", ...]`.

### Contact sheet
Build `docs/fan-assets/contact-sheet.png` (or a small set `contact-sheet-fighters.png`, `contact-sheet-stages.png`, `contact-sheet-anims.png`) showing thumbnails of accepted items with name + license under each. Follow the media proof standard (open the image, check it by eye, SHA-256 in a SUMS file).

---

## Track 3 — Reference images and videos (links only)

Creator motion from **TikTok, YouTube, and Facebook is approved as reference** (owner 2026-10-14). Catalog links; do not rehost the videos.

Layout:

```
docs/fan-assets/references/
  README.md                 # how to use these refs
  by-character/<wh_id>.md   # e.g. pantera.md, demonio.md
  by-move/<slot>.md         # e.g. jab.md, sweep.md
  index.json                # machine-readable: character, move, url, platform, creator, notes
```

Each entry: URL, platform, creator handle, what to look for (stance, timing, silhouette), and which WH character or move slot it supports. Prefer fair-use reference use; never claim the linked video is a WH asset.

---

## Track 4 — Owner T7/T8 extractions (placeholder)

Create `docs/t7t8-reference/OWNER_EXTRACTIONS.md` with:

- Status: **WAITING on owner** — do not download rips from fan/model-sharing sites.
- When the owner provides extractions from copies he owns (same path as TTT2/T6), ingest them like other teardowns: private storage, source log, additive PR, no deletes.
- Stub tables for: models, stages, animations, other files — empty until files arrive.
- Point to existing teardown dirs for the pattern (`teardown/tekken6`, `teardown/tekken-tag-tournament-2`) but **do not edit those trees** (Repo Co Dev / wiring claims).

---

## Delivery checklist (Muse)

1. Claim the task in `mhvnsnt/agent-ops` `CLAIMS.md` (branch + PR).
2. Open a western-heart branch; add stub dirs/files first if needed (`docs/fan-assets/`, track-4 stub).
3. Collect in small batches; one PR per batch or per track is fine.
4. Every PR body uses the instruction-gate headings (see below).
5. Binaries → `box-storage` release; git keeps manifests + SHA-256.
6. Contact sheet + CREDITS.md updated before you call a batch done.
7. Update the TAG-TEAM row status/links in the same or a follow-up agent-ops PR.
8. Proof: paths in the PR body; open images; no deleted files.

### Instruction-gate headings (every PR)
```
## Owner instruction (verbatim quote)
## Method the owner specified
## Method actually used
## Deviations (none / list, each with owner approval link)
## Proof (paths to files, frames, test output)
## Self-check: I verified the result against the literal instruction
```

---

## Owner instruction (verbatim, for your PR quotes)

> Yes the fan made versions of the fighters the stages and the animations from the games you can get those that are up on for free reuse like that are up on sketch Fab and makes a mold and creative comments and other websites that's kind of what I'm saying in the animations and stages and stuff you can get some you can get all you can do all of that you can do all of that stuff
>
> But focus on perfecting the models and animations and then getting all the tear down files set up and getting all of the creation sweep and all that stuff set up first before you start on any of that new stuff get all the tear down files wired up cuz I own those files and games and all the other files that we pulled in and then after that then you can go collect the stuff that's out there hopefully you know all that other stuff over remember it label it down put it in the repo actually tell Muse to do it put in a thing like a handoff to Muse and I'll go tell music to do that to start doing that right now and then you can still pull all of that stuff from the public sites where it's shared
>
> **URGENT update (owner via parent, same day):** Muse starts NOW, running in parallel. Start immediately; don't touch teardown wiring, creation suite or physics files.

Also covered by this handoff (owner / parent steering):
1. Free public frame data, move lists, combo guides, stage layouts (extend `docs/t7t8-reference`; CC0 copied, others links only).
2. Fan-made reuse-licensed models, stages, animations (Sketchfab CC0/CC-BY/CC-BY-SA downloadable, Mixamo, OpenGameArt, Poly Haven, itch.io free packs, open motion datasets).
3. Reference images/videos as links; TikTok / YouTube / Facebook creator motion approved as reference; catalog per character and move.
4. Placeholder for owner's own T7/T8 extractions, added like other teardowns when he provides them. No rips.

---

## Out of scope for Muse on this ticket
- Selling / publishing concerns (owner rule: private mod until he says otherwise — do not hold back licensed public collection over sale worries).
- Ripping T7/T8 from piracy sites or "free model" rip mirrors.
- Editing creation-suite, physics, or teardown wiring files.

When a batch is ready, ping the board and link the PR + contact sheet.
