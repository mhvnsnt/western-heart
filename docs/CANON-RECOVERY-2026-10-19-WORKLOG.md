# WORKLOG — Canon recovery: restore dropped NEW VESSELS entries (2026-10-19)

## Owner instruction (verbatim, 2026-10-19 ~01:22 CDT)

"Bring that canon stuff back recover it all if anything is missing recover it"

## What was found

PR #258 (merged 2026-10-18 18:16 CDT, merge commit e39e0ec7) added
"## 7. THE NEW VESSELS" to CANON.md with 10 vessel entries:
LILI, ZAFINA, BAEK, JIN KAZAMA, STEVE FOX, DXMMII, MARIPOSA (Butterfly Soul),
DOC FRANK, KIKO TANAKA, SUN RĀ.

PR #277 (merged 2026-10-18 ~22:37 CDT, merge commit 9808e26d) merged the two
MARIPOSA entries into one (owner-confirmed: Zafina IS Mariposa, re-based —
kept). But it also dropped five vessel entries outright:

1. **BAEK — The Master Soul** — fully missing (28 lines)
2. **JIN KAZAMA — The Bloodline Soul** — fully missing (28 lines)
3. **STEVE FOX — The Boxer Soul** — fully missing (30 lines)
4. **DXMMII — The Rebuilt Soul** — fully missing (32 lines)
5. **DOC FRANK — The Builder Soul** — body intact, `### ` header line missing
   (merge left a headless fragment at the end of the MARIPOSA section)

Method: read CANON.md at main (e75a42a4), at #258's merge commit, and at
#277's merge commit via the GitHub API; diffed the NEW VESSELS section
across all three. Main's CANON.md is byte-identical to #277's version, so
the drops are all from #277.

## What was restored (verbatim, additions only)

- BAEK, JIN KAZAMA, STEVE FOX, DXMMII sections re-inserted byte-identical
  from #258, in their original relative order (after SILVERTONGUE, before
  MARIPOSA).
- `### DOC FRANK — The Builder Soul` header re-inserted above the surviving
  body fragment (after MARIPOSA, before KIKO TANAKA).
- Kept: SILVERTONGUE rename (owner-ordered, PR #269), merged MARIPOSA entry
  (owner-confirmed single character). Zero deletions — diff vs main is
  +120/−0.

## Verification

- All four restored sections byte-identical to #258's text (script-compared).
- DOC FRANK body fragment verified byte-identical to #258's body before
  restoring the header.
- Final NEW VESSELS order: SILVERTONGUE, BAEK, JIN KAZAMA, STEVE FOX,
  DXMMII, MARIPOSA, DOC FRANK, KIKO TANAKA, SUN RĀ.
