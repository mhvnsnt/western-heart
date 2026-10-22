# Decision: Ashlane → DOA moveset source mappings (user-locked 2026-10-22)

## Owner instruction (verbatim quote)
"Ashlane mappings update — user locked 2026-10-22 ~17:23 CDT." (10 mappings) + "Mapping locked 2026-10-22 ~17:24 CDT: **Tarzanian Devil → Brad Wong (DOA).**"

## Locked mappings

| WH / Ashlane character | DOA source | Source file | Notes |
|---|---|---|---|
| Hall Nighter | Jann Lee | doa bank (existing, untouched) | — |
| Maime | Eliot | `doa4-eliot.json` | — |
| Kobra | La Mariposa | `doa4-lamariposa.json` | User: Kobra isn't actually a masked luchador; mask added later. Female moveset is fine — masculinize movements/stances on top. |
| Hollow | Alpha-152 | `doa4-alpha152.json` | User: proprietary wrestling moves get built for Hollow fitting his bio/canon, NOT just copycat moves. |
| Triple XXX | Zack | `doa4-zack.json` | — |
| Tyneshia | Tina Armstrong | doa bank (existing, untouched) | — |
| Edwin Kennedy | Gen Fu | `doa4-genfu.json` | — |
| Viper | Ryu Hayabusa | doa bank (existing, untouched) | — |
| Echo | Christie | `doa4-christie.json` | — |
| Onyx | Lisa Hamilton | `doa4-lamariposa.json` | La Mariposa and Lisa Hamilton are the same person — one kit feeds both Kobra and Onyx; user approved both. |
| Tarzanian Devil | Brad Wong | `doa4-bradwong.json` | User: Brad Wong was unassigned; his wild drunken-fighter style works for the jungle savage. |

## Still open
- **Stan Combs only.** Sarah/Pai/Aoi/Eileen (VF5 women) still need female Ashlane characters identified — may resolve together with Stan Combs.

## User's principle (applies to all mappings)
"Persona matching is nice but not required — solid movesets wired up and converted to Tekken inputs is what matters. Refine with proprietary/canon moves on top later."

## Where this is enforced
- `moveset-library/movesets/CLAIMED-MAP.json` — single source of truth (includes these 11 plus previously locked VF5, intake, Bass→Vain Abel, Iori→Deathfang mappings, candidates, and open items).
- Each affected DOA4 federation file carries a `wh_claimed_map` provenance field naming the WH character.

## Method
User picked every mapping in chat; worker 59 recorded them into the claimed map and federation-file provenance. No moveset content was fabricated — mappings reference existing locked sources.
