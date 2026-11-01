# TASKBOARD (Western Heart backlog any agent can pull)

How to use: pick the top unowned item, set `owner` + `branch` (this is the claim; also follow CLAIMS.md if present), push early, link the PR. Rules: [`docs/AGENT-TEAM-PROTOCOL.md`](../AGENT-TEAM-PROTOCOL.md), handoffs: [`HANDOFF.md`](HANDOFF.md), free tools: [`FREE-RESOURCES.md`](FREE-RESOURCES.md). Edit this file surgically, one item per PR line change.

Status: `open` · `claimed` · `paused (limit)` · `in review` · `done`. Seeded 2026-10-23.

| # | Item | Status | Owner | Branch / PR |
|---|---|---|---|---|
| 1 | **Fight HUD + touch buttons**: visible PSX/Tekken 1-2-3-4 diamond, block/heat/rage on phone | in review | Muse | #842 `fix/touch-tekken-buttons` |
| 2 | **Character select rebuilt from Tekken 8** (layout, big renders, info panels; refs: AshLane, Brutal Fist); fix wrong-model and T-posed portraits | claimed | Grok | — |
| 3 | **Match loading**: shorten arena→fight load, make the progress bar actually move | claimed | Grok | — |
| 4 | **Universal T7/T8 moveset + AI** for every fighter (e.g. Lee→Purple Rain full list, Bob→Burger rig and moves) | claimed | Grok | — |
| 5 | **Stages / menus / systems** from T7/T8 + teardowns (HUD, submenus, game systems) | in review (part) | Grok / Muse | #845, #841, #836 |
| 6 | **Face-cone skin weights** (face verts weighted to spine/pelvis/root); universal fix + CI check; Purple Rain, Star, Scarlet, Madeline first | claimed | Muse + Grok | #840 (tooling) |
| 7 | **Cape Jones / Alisa slot**: cyborg-x 52-bone rig; Alisa stance and moves from T8 (T7 fallback); CMU mocap show clips | claimed | Grok | — |
| 8 | **T8 asset pipeline** in repo (non-Steam extraction tools + how-to) so every agent can pull T8 | claimed | Grok | — |
| 9 | **Claude's 16 limb-isolated rigs + build script**: push from Claude's machine at 6 PM CT reset | paused (limit, resets 6 PM CT) | Claude Code | #825 |
| 10 | Wave 2 auto-rigs (Chordz, Vain Abel A2-A4, Aotsuki, Dio Jade God) | in review | — | #837 |
| 11 | Claude autosave hook (`.claude/settings.json`, `CLAUDE.md`) | claimed | Grok | — |
| 12 | agent-ops CI blocked by Actions billing: owner raises spending limit / go public / self-hosted runner | open (owner) | — | — |
| 13 | Roster integrity test (`test/roster-integrity.test.mjs`): ids unique, referenced files exist | claimed | Jules | session [11272083988152511701](https://jules.google.com/session/11272083988152511701) |
| 14 | Docs link-check CI gate (`tools/docs-links/`, fail only on new broken links) | claimed | Jules | session [7284020919156373839](https://jules.google.com/session/7284020919156373839) |
| 15 | `tools/TOOLS-INDEX.md` completeness check + fill missing entries from tool READMEs | claimed | Jules | session [10362622652159135005](https://jules.google.com/session/10362622652159135005) |
| 16 | **Negativo re-rig** (owner 2026-10-31: cone face, arms crushed, head/neck weighted toward the pelvis). Skeleton re-fit from his own landmarks (`tools/auto_rig/refit_upper_body.py`), bone heat, head/neck territory, stretch gate; other agents: please do not run a parallel Negativo rig, review / B2-upload the result instead | claimed | Claude Code | #1463 `claude/amazing-keller-p8644u` |
