# Heights check (PR #120 vs public sources)

**Roster baseline: Tekken 8 heights** (owner 2026-10-14). Where T7 and T8 differ, the six bodies below use their T8 values in `lab/game/data/characters/heights.json`. All other fighters stay on the T7/T8 value they already had.

T7 source: https://www.esportstales.com/tekken/characters-ages-heights-and-weights (fan aggregate of bios/manuals; not an official Bandai Namco list). T8 source: https://tekken8.sorao.site/height-weight (compiled from T8 in-game profiles). No official Bandai Namco page publishes a full height table.

| WH | Body | Roster cm | T7 cm | T8 cm | Status |
|---|---|---|---|---|---|
| pantera | King | 200 | 200 | 200 | match |
| king | King | 200 | 200 | 200 | match |
| demonio | Jin | 183 | 180 | 183 | T8 (was T7 180) |
| phantom | Yoshimitsu | 178 | 178 | 178 | match |
| diablo | Heihachi | 179 | 179 | 179 | match |
| skull | Bryan | 186 | 186 | 186 | match |
| sam_ur_a1 | Gun Jack | None | None | None | match |
| saku_ra | Xiaoyu | 159 | 157 | 159 | T8 (was T7 157) |
| zui | Steve | 184 | 187 | 184 | T8 (was T7 187) |
| kinpo | Asuka | 167 | 160 | 167 | T8 (was T7 160) |
| waterfall | Josie | 178 | 178 | None | match |
| king_tyrant | Eddy | 188 | 188 | 188 | match |
| burger | Bob | 196 | 196 | None | match |
| awa_pop | Nina | 168 | 160 | 168 | T8 (was T7 160) |
| scimitar | Shaheen | 185 | None | 185 | match |
| purple_rain | Lee | 178 | 178 | 178 | match |
| nightwolf | Julia | 165 | 165 | None | match |
| michiko | Katarina | None | None | None | match |
| star | Christie | None | None | None | match |
| torch | Anna | 163 | 163 | None | match |
| dio | Akuma | 178 | 178 | None | match |
| cyborg_x | Alisa | 165 | 163 | 165 | T8 (was T7 163) |
| bruno | Miguel | 196 | 196 | None | match |

Notes:
- Roster is on T8 heights for the six bodies that changed between T7 and T8: demonio/Jin 183, saku_ra/Xiaoyu 159, zui/Steve 184, kinpo/Asuka 167, awa_pop/Nina 168, cyborg_x/Alisa 165. Everyone else unchanged.
- Josie 178 cm comes only from the fan list; Josie's weight is unknown there, so treat it as low confidence.
- Gun Jack, Katarina, Christie: no public height found; still null. Jack-8 is 225 cm (T8), Jack-7 235 cm (T7).
