# Ultra Street Fighter IV — sources

Checked live 2026-11-20. Nothing is vendored in this directory — this
is a record of what was searched and found, so the next lane does not
re-search it. Licence/source is logged honestly next to each item.

## Searched

| Source | What was found | Verdict |
|---|---|---|
| archive.org (advancedsearch, 15 rows then software filter, 40 rows) | `ultra-street-fighter-iv.-xbox-360` — Xbox 360 image ZIP 8,254,186,617 B; `ultra-street-fighter-iv-blus-31218` — PS3 image; `link_20251007_20251007_1905` | Raw game dumps only — NOT teardowns, NOT pulled |
| Models Resource (PC) | USFIV page: 2 assets total — Adon fighter DAE 14.21 MB (Dec 10, 2017, Ozci) + 1 stage element | Single model, no animations — NOT pulled |
| Sounds Resource (PC) | USFIV: 138 assets — voices EN/JP + character sounds | Audio only |
| Shoryuken Forums Archive / TL.net | Oni Sakura / Shin Sakura PC mods (command files + ultras/animations/voice/costume zips, uploadmirrors links) | Character mods, not a teardown |
| GitHub | No USFIV decomp/recomp repo found; `jvankooo/sf4-nx` covers vanilla SFIV only | Nothing to pull |
| Steam Community | SF4E / SF4-Ember rollback netplay mods (github.com/fabeloper/sf4e, github.com/Confetti3/SF4-Ember-Netplay) | Netplay mods, not a teardown |

## Shared toolchain (pulled under SFIV)

The SFIV bac/bcm toolchain is pulled in `../street-fighter-4/` —
`tools/sf4tools/` (Dantarion, MIT, source commit
`e5c17132f3b6e63f66150c3a347a9e8f6e0d73a4`). USFIV uses the same
formats, so that toolchain reads USFIV files. No separate USFIV pull
was needed or made.
