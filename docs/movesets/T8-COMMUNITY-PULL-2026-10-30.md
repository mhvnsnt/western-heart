# TEKKEN 8 community pull — moveset/animation data + the T8 join (2026-10-30)

## Owner instruction (verbatim quote)

"I don't have Tekken 8 [on Steam], I am on it on disc, and you'll have to get it somewhere online... the modern community probably has it in pieces or something like the move sets... you can just pull it from the modern community bro, like the modeling community, modding community." — and, on being told the Steam snapshot lists TEKKEN 8: "Oh, so Tekken 8 is in there? I mean, if it's in there, bro, use it. Shit, I didn't know."

## Method the owner specified

Pull TEKKEN 8 in pieces from the modern modding/modeling community (movesets and animation data), use his own Steam library copy instead if the account actually owns the game, validate every piece, and join the T8-side remainder of the 781 previously-unmapped moves (the 81 strong T8-only candidates first). Standing rule (owner 2026-10-14): no full-game downloads for TEKKEN 7/8 — pieces from communities only.

## Method actually used

1. Steam ownership verified against the account record before any pull: app 1778820 TEKKEN 8 is listed as NOT owned in docs/tech/STEAM-LIBRARY.md (owner's own pasted library, 2026-10-23) and docs/plans/STEAM-LIBRARY-FOR-WESTERN-HEART.md ("TEKKEN 8 not owned on Steam: off-limits"). The DepotDownloader route therefore does not apply to T8; the community route carried the lane.
2. Community pieces acquired and hash-verified (raw files stored in the private game-reverse-engineering release t8-community-pieces-v1):
   - Kaiutzi21/Tekken8Movesets exports (TekkenMovesetExtractor format, CC BY-NC 4.0): King x2 extractions, Bryan, Jin, Heihachi, Shaheen, Yoshimitsu.
   - TekkenMods pieces (download URL token equals the file SHA-256; verified on the body): mod 6006 Screw Combos pack (24 character exports incl. the only circulating Asuka export), mod 7506 TKData King package (moveset.motbin + moveset.anmbin + moveset.mvl), mod 4412 Legacy Jin, mod 4756 Legacy Heihachi, mod 5397 Legendary Yoshimitsu, mod 7131 King AI, mod 6994 Armor King Reimagined, TKData Mod Loader v0.802.
   - wavu.wiki frame data via pbruvoll/tekkendocs movelist JSONs (8 characters incl. Bob).
   - AliK3112/tekken-8-movesets-scripts name_keys.json (45,716 entries) for de-anonymizing export move/animation names.
3. Validation at the T7 lane's bar: schema check against the exporter's own source; edit detection by the in-file hash test (original_hash vs last_calculated_hash) plus wavu (startup, damage) fingerprint sampling (Worker A: Heihachi and Shaheen exports are hash-clean = never re-saved after extraction; King DLC export is a deliberately exaggerated boss build, used as structure reference only); TKData package anatomy verified against the tekkenmods.com moveset-structure documentation (TEK magic at 0x8, table at 0x168).
4. The join (tools/tekken8-community/t8_join.py, mirroring the T7 method): cancel-graph chain search over each character's export (cancel blocks delimited by the 0x8000 terminator entry — verified on 100% of moves; commands decoded per the community-documented bitfield encoding; group cancels as shared entry edges; attack-class terminals only, pure-motion notations excepted), corroborated by wavu name+notation existence and (startup, damage) fingerprints. Names resolved through the name-key dictionary (97%+ of moves).

## Deviations

- The Steam DepotDownloader route for TEKKEN 8 was not used: the account record shows the game is not owned on Steam (owner owns the disc copy). Evidence in docs/tech/STEAM-LIBRARY.md. The owner's "use it if it's in there" approval stands recorded for the games the account does own.
- Bob premise corrected: Bob IS in TEKKEN 8 (Season 3 DLC, August 2026) with a 161-move wavu movelist, but no moveset export for him circulates yet — his resolutions are movelist-grade only.
- TekkenMods mod 7193 TEKKEN 8 BALANCED (224,463,100 bytes, TKData motbins incl. Bryan) was inventoried and hash-verified but not downloaded: Bryan is already covered by an export graph, and the pack exceeds the lane's single-file cap. Its direct URL and SHA-256 token are recorded in the lane report for a later grab.
- The Back To Basics mod's runtime-fetched .motbin set (the only known Shaheen TKData route) requires running its Windows downloader; not run — Shaheen is covered by a hash-clean export instead.
- Fighter moveset files were not edited; the moveset-provenance lane consumes these maps.

## Results — the join over the 300 T7-unmapped

- Resolved: 185 of 300 (80 high, 83 medium, 22 movelist-only). Unmapped: 115, each with a recorded reason.
- The 81 strong T8-only candidates: 27 resolved to export-graph terminals (18 of 61 no-evidence class, 9 of 20 notation-differs class). All 81 notations provably exist in TEKKEN 8 (wavu coverage: 51 exact name+notation, 4 name-only, 26 notation-only, 0 absent) — the 54 still unmapped are graph-side gaps (mostly chain throws and requirement-gated entries whose cancel chains the export graph does not close), not missing moves.
- Wider classes also resolved substantially: ambiguous pool 77 of 91, graph-only-held 63 of 89, MVL-matched graph-gap 11 of 39.
- For all 20 notation-differs entries, the TEKKEN 8 notation equals the WH notation; the TEKKEN 7 MVL notation was the outlier.
- Per-fighter maps: game/assets/anim/t8/clip-maps/ (schema wh-t8-clip-map/1); resolution record: game/assets/anim/t8/INDEX.json.

## Proof

- `game/assets/anim/t8/clip-maps/pantera-clip-map.json`
- `game/assets/anim/t8/clip-maps/phantom-clip-map.json`
- `game/assets/anim/t8/clip-maps/skull-clip-map.json`
- `game/assets/anim/t8/clip-maps/burger-clip-map.json`
- `game/assets/anim/t8/clip-maps/kinpo-clip-map.json`
- `game/assets/anim/t8/clip-maps/demonio-clip-map.json`
- `game/assets/anim/t8/clip-maps/diablo-clip-map.json`
- `game/assets/anim/t8/clip-maps/scimitar-clip-map.json`
- `game/assets/anim/t8/INDEX.json`
- `tools/tekken8-community/t8_join.py`
- Raw community pieces + SHA256SUMS: GRE release `t8-community-pieces-v1` (26 assets, 25 files + sums; every TekkenMods asset's SHA-256 equals its download token; every Kaiutzi21 asset matches the validator's in-memory hash).

## Self-check

- [x] I verified the result against the literal instruction: TEKKEN 8 was pulled in pieces from the modding community only (no full-game download), the Steam route was checked against the account record first, every piece is hash-verified and stored in the private store, the 81 T8-only candidates were joined first, and no fighter moveset files were edited.
