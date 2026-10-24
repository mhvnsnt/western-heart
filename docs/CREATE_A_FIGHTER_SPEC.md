# Create a Fighter (spec)

Owner: the creation-suite UI belongs to **Repo Co Dev** (`packages/creation-suite`, `docs/creation-suite/`). This is a spec and handoff; nobody else edits suite files. The import back-end is `tools/import_model.py` (see `docs/MODEL_IMPORT_AUTORIG.md`).

## Model: latest WWE 2K Create-a-Superstar, plus each teardown's suite
| Source | What we take (structure, not assets) |
|---|---|
| WWE 2K (CAW) | Part-by-part body (head, face morph, torso, arms, legs), layered attire slots (upper/lower/gloves/boots/mask/accessories, each with colour/material/logo layers), entrance + move-set + attributes tabs, save multiple attires per fighter |
| WWF No Mercy / WM XIX teardowns | Attire = whole-model swap per slot (`teardown/wwf-no-mercy/re-docs`), move-set slot tree (`moveset-library/movesets/MOVE-SLOTS.json`) |
| Tekken 6 / TTT2 Customize | Per-region item slots (head, face, upper, lower, hands, legs, items) with 2 colour channels each; items that attach to bones; T3 outfit slots (`teardown/tekken3/tools/tekken3recompiled/Outfit-Slots.md`) |
| Def Jam: Fight for NY | Build-a-fighter from a face/body base, tattoos/jewellery/bling as decals and bone props, style mix |
| Urban Reign | Simple preset swaps; menus as layout reference only (art still scrambled) |

## Screens
1. **Base**: pick body frame (canon Tekken bodies) or an imported model. Height slider drives the height/scale system (Western Heart #120).
2. **Parts**: head, hair, face, torso, arms, hands, legs, feet. Each part lists sources: WH originals first, then teardown parts (flagged THIRD-PARTY, logged to `docs/roster/<id>/parts.json`).
3. **Attire layers**: slots as above; colour/material per layer; logos/decals (owner art); props on bones.
4. **Body physics**: jiggle/secondary sliders (creation-suite `applyDNA`), naming in MODEL_IMPORT_AUTORIG.md.
5. **Move-set**: `docs/MOVESET_EDITOR_SPEC.md`.
6. **Card**: auto-generates the roster card (`game/ui-wh/cards.html`) and select portrait.
7. **Save**: new attire = new version, never overwrites (`<attire>_vN`).

## Four import paths (all run the same pipeline: fetch → version copy → rig map → segment → retarget map → gates → register → card)
| Path | Command |
|---|---|
| (a) brand-new fighter from parts | suite exports a GLB → `python3 tools/import_model.py out.glb --character <newid> --new "NAME" --attire a1 --render` |
| (b) upload to an existing fighter with no model | `... <model.glb> --character <id> --attire a1 --render` |
| (c) new attire on an existing fighter | `... <model.glb> --character <id> --attire a2 --render` |
| (d) new fighter from an uploaded model | `... <model.glb> --character <newid> --new "NAME" --attire a1 --render` (then add canon text to CANON.md via the owner) |

## Three sources
1. **In-game upload**: suite file picker → saved to `roster/_inbox/` → same command (UI work: Repo Co Dev).
2. **Google Drive link or folder**: public file → `import_model.py <link>` uses gdown. Private → agent runbook below.
3. **Hand the Drive link to an agent**: agent runs the runbook below.

## AGENT_IMPORT_RUNBOOK (Muse and any agent, from a Drive link)
1. Claim on agent-ops `CLAIMS.md` first (`import <character> <attire>`), PR via `gh`.
2. Get the file id from the link (`/d/<id>/` or `id=<id>`). Folder: list it with the Drive tools and do each GLB/FBX in turn.
3. Download with the **DownloadFile** tool (connection `google-drive`, `fileId <id>`, destination `/workspace/<task>/in/<name>.glb`). Never ask the owner to download.
4. `sha256sum` the download and note it.
5. Sparse clone western-heart (`git clone --filter=blob:none --sparse`, then `git sparse-checkout set tools lab game/ui-wh docs roster`).
6. Run `python3 tools/import_model.py /workspace/<task>/in/<name>.glb --character <id> --attire <a> --render`.
7. If any gate FAILs: stop, report the failing gate and the fix line from the report. Unrigged → Tripo/Mixamo rig on the T-pose model first.
8. Open the rendered PNGs yourself; check face, hands and feet are there and nothing is blank.
9. Add the id to `ART` in `game/ui-wh/roster.js`, run `capture_cards.mjs`, open the captures.
10. Commit (report json, versioned GLB, portraits, captures), `gh pr create`, merge only if checks are green and nothing is deleted. Send the owner the card PNG paths and PR link.
