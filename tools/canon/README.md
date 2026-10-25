# tools/canon: shared canon renamer + CI gate
Owner rule: every item imported from another game gets an Eastern Mind Western Heart canon name in every player-facing string and public file.
- Private map: `game-reverse-engineering/naming/CANON-NAME-MAP.json` (original, canon, source, kind). It is never committed here.
- Pipelines run `node tools/canon/canon.mjs in.json out.json --map <private map>`. It exits 2 if a source name survives.
- CI: `.github/workflows/canon-names.yml` runs `check.py` on added lines under `game/`.
- Tests: `node tools/canon/test.mjs`.
