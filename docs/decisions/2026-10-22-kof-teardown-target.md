# Decision: KOF full-teardown target (user directive 2026-10-22 ~17:21 CDT)

## Owner instruction (verbatim quote)
"We need to pull a full tear down of one of those games. Whatever the most recent one we can get our hands on. And keep it from clouding up local disc. Get the full tear down 100%. Get it extracted. Deciphered and decrypted. And then pull moves and animations from it."

## Candidate evaluation

| Candidate | Year | Engine | Acquirable? | Verdict |
|---|---|---|---|---|
| KOF XV | 2022 | UE4 | NO — no full dump on Internet Archive (searched 2026-10-22) | rejected: not acquirable |
| KOF XIV | 2016 | custom SNK | NO — no full game dump on IA (frame data and trailers only) | rejected: not acquirable |
| KOF: Maximum Impact 2 | 2006 | PS2 proprietary | YES — `the-king-of-fighters-maximum-impact-2-japan-ps2-iso` on IA, 1.8 GB single ISO, md5 `ce765cca13d3c05e9f13b30959c24084` | **ACQUIRED — full-teardown target** |
| KOF: Maximum Impact 1 | 2004 | PS2 proprietary | YES — `king-of-fighters-maximum-impact-english-xbox` on IA (USA/Xbox + Regulation A) | fallback only |

## Acquired: KOF: Maximum Impact 2 (PS2, Japan, SLPS-25638)

Most recent 3D KOF actually acquirable from public archival sources. Downloading from
IA 2026-10-22 (~1.8 GB, ~20 min at observed speed). Teardown standard: extract ->
decipher -> decrypt -> document, then pull moves and animations.

**Priority extractions:** Iori Yagami 3D moveset (Deathfang upgrade from 2D to 3D),
then the full roster into the moveset library under the locked conversion standard
(Tekken notation, Tekken feel, input-to-move fidelity).

## Raiden / Big Bear correction

Raiden is NOT playable in MI2 — fandom documents him only as a cameo (Clark's
Another Outfit Variation E, as Big Bear). His only 3D playable appearance is
**Fatal Fury: Wild Ambition** (Hyper Neo Geo 64 arcade 1999 / PS1 port 2000).
Acquiring separately: `fatal-fury-wild-ambition-usa_202503` on IA (448 MB .chd,
md5 `557b9d20a2d0b9682ac089cbda13a51e`), downloading 2026-10-22. PS1 extraction
tooling is mature; HNG64 arcade has no public extraction toolchain, so the PS1
port is the practical source for Raiden's 3D moves/animations (for Titan).

## Local-disk rule (user explicit)

Large files go to Releases/external, NOT local disk. Plan: download -> extract
moves/animations (small data, stays) -> push ISO/CHD chunks to a GitHub release
-> delete local copies. Nothing large sits on the VM.

## INTEGRATION LAW constraint (standing user directive 2026-10-22)

Everything extracted from these teardowns lands in Tekken structure, never as
parallel KOF/Fatal Fury subsystems: moves in Tekken notation into Tekken move
slots, animations retimed to Tekken conventions, fighters as Tekken-style roster
entries with attire ladders. Source game is provenance metadata only — it never
surfaces as a menu, roster, or system in-game.
