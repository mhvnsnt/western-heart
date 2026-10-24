# Community / mod sources — Tekken 7 & 8 (batch 1, 2026-10-23)

Owner rule (pt151u): pull publicly posted community/mod content. **No pirated full-game copies or cracked game files.** Private, non-commercial repo; every source logged here. Files live under `teardown/community/<game>/`.
Note: this supersedes the "link only" rule in `docs/t7t8-reference/REFERENCE_SOURCES.md` for private teardown use only; NC-licensed data must not ship in a commercial build.

| # | URL | Author | What | Format | License / notes | Status |
|---|---|---|---|---|---|---|
| 1 | https://github.com/Kaiutzi21/Tekken8Movesets | Kaiutzi21 | Full T8 moveset dumps (TekkenMovesetExtractor export 1.0.1): moves, cancels, hit conditions, pushbacks, throws, input sequences, voiceclips. Pulled: LEE (v2, edited), KING (v2, edited), LAW, PAUL, ARMOR_KING. Not pulled yet: BRYAN, CLIVE, FAHKUMRAM, HEIHACHI, JIN, LARS, MIARY_ZO, RAVEN, SHAHEEN, STEVE, UNKNOWN, YOSHIMITSU | JSON (gzipped) + our `*.summary.json` move tables | CC BY-NC 4.0 (credit Kaiutzi21). LEE_v2 / KING_v2 are *edited* movesets, see each `Documentary.md`. Commit pinned in `SOURCE_COMMIT.txt` | **Pulled** → `teardown/community/tekken8/movesets/kaiutzi21/` |
| 2 | https://github.com/pbruvoll/rbnTekkenFrameData | pbruvoll (RBNorway) | T7 frame data for every T7 character, incl. Lee, Bob, Alisa, Law, King; `*-gifs.csv` link each move to an animation GIF | CSV | No license file (treat as all rights reserved; private reference) | **Pulled** → `teardown/community/tekken7/framedata/rbnorway/` |
| 3 | https://www.spriters-resource.com/arcade/tekken7/asset/561802/ | nonovplayxd | T7 HUD: life/rage gauges, round counters, win text, name plates, rage FX (236 PNG) | ZIP/PNG | Ripped game art, fan upload | **Blocked** (Cloudflare 403 for curl/scripts) — needs box browser download |
| 4 | https://sounds.spriters-resource.com/arcade/tekken7/asset/561714/ | nonovplayxd | T7 announcer: Round 1-9, Fight, KO, Perfect, Time Up, all character name calls (94 WAV) | ZIP/WAV | Ripped game audio | **Blocked** (Cloudflare) — needs browser |
| 5 | https://sounds.spriters-resource.com/pc_computer/tekken7/ | various | 84 T7 PC sound sets (voices per character, SFX) | ZIP | Ripped | Catalogued, not pulled |
| 6 | https://www.spriters-resource.com/pc_computer/tekken8/ | various | 53 T8 sheets: character artwork parts 1-6, general artwork, rank icons | ZIP/PNG | Ripped | Catalogued — use for character select renders |
| 7 | https://www.models-resource.com/pc_computer/tekken7/ | various | Only 4 T7 models (camel, dog, 2 workers) — no fighters | ZIP | Ripped | Low value, skipped |
| 8 | https://sketchfab.com/3d-models/alisa-bosconovitch-legacy-outfit-df8f1894d9984b5e97e76d1b6aec7d85 | vhongliang (credit rolance) | Alisa T7 legacy outfit, 22k tris (Cape Jones) | Sketchfab download (needs login) | Fan port of game model | Catalogued — needs Sketchfab login |
| 9 | https://github.com/Kiloutre/TekkenMovesetExtractor | Kiloutre | Extractor/editor; also animation editor + camera animator (source of the JSON format above) | Python | GPL-3.0 | Reference — needed to decode `anim_key` → animation data |
| 10 | https://github.com/AliK3112/tekken-8-movesets-scripts | AliK3112 | Scripts to analyze T8 moveset bin/JSON (moves, cancels, throws, inputs) | JS/Python | no license | Reference for decoding |
| 11 | https://github.com/KulaGGin/Tekken-7-Modding-Tutorials | KulaGGin | T7 modding tutorials | docs | — | Reference |
| — | SFMLab / DeviantArt T7 Lee & Alisa XPS ports | various | adult/NSFW edits | XPS/Source | Skipped (NSFW) | Skipped |

## Gaps that remain
- **Animations:** moveset JSONs hold move *logic* (cancels, frames, hit levels) but not animation curves; curves are in the game's `.anm`/motbin data, which isn't posted publicly for these characters. No 52-bone retarget possible from this batch.
- **Bob (Burger) and Alisa (Cape Jones):** not in Kaiutzi21's T8 set (Bob isn't in T8). Only T7 frame data (#2) so far.
- **Stages:** no public T7/T8 stage rips found in this pass beyond the fan T7 dojo already in repo.
- **HUD / announcer / select art:** found (#3-6) but Cloudflare blocks scripted download; a browser agent has to grab the ZIPs.
