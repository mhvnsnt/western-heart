# anims/show — show / story animation set (NEW, separate from fight moves)
- Fight movesets (`game/`, `lab/`, `moveset-library/`) are **read-only** here. Nothing in this folder overwrites or retimes them.
- `INDEX.json` = slot → source per character. `CLIP-INDEX.json` = cutscene/story/pre-fight/heart-and-mind scenes WH can consume.
- Baked clips go to `anims/show/<char>/<slot>.glb` and must list their source in `anims/show/<char>/SOURCES.md`.
- Sources allowed (owner rule 2026-10-23): teardowns + existing repo work first; show-only motions from approved creator-motion/mocap reference (CMU set in cape-jones) and open-source rigs. No hand-keying until the owner says so.
