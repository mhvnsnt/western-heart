# TEKKEN TAG TOURNAMENT 2 — Teardown for Western Heart

**Role in Chimera Build:** 59-fighter roster source + tag-team systems. TTT2 is the biggest Tekken roster ever shipped — every fighter is a potential Western Heart reskin base or alt-costume donor.
**Developer:** Namco Bandai (2011 arcade / 2012 console)
**Platform:** Xbox 360 (this dump: EU region)
**Last updated:** 2026-10-13 (full teardown sweep)

---

## What's Extracted and Documented

### 7z Archive — Downloaded + Verified (DONE 2026-10-13)
- `Tekken Tag Tournament 2.7z` — **13,363,624,393 bytes** (byte-exact vs Archive.org metadata), item `tekken-tag-tournament-2_202609`
- 80 archive entries, 72 real files, **13.45GB uncompressed**
- Full header listing: `HEADER-LISTING.txt` (committed here)
- **Safe storage: NOT YET** — the 13.3GB archive exceeds GitHub's 2GB/file limit (needs 7×2GB split to Release) and the browser file-grant limit (no TeraBox path). Owner decision pending on storage route. **Per NO-DELETE-BEFORE-SAFE-STORAGE LAW the local 7z stays.**

### Disc Structure (from header listing)
Xbox 360 package layout, Title ID `4E4D0859`:

| Path | Contents |
|------|----------|
| `0000000000000000/4E4D0859/00000002/` | Main game data — 3 large blobs (358MB, 1.94GB, 2.03GB) + 51MB file |
| `0000000000000000/4E4D0859/00009000/` | Small config/system files (45KB–340KB each) |
| `4E4D0859/00007000/392CFF5C9DB17CCAEBC3.data/` | **Data0000–Data0051: 52 × 170MB split data** (~8.8GB — the bulk game content: models, stages, audio) |

### Roster (documented from game knowledge, 59 fighters)
The largest Tekken roster: all of Tekken 6's 40 + returning favorites (Jun, Michelle, Ogre, True Ogre, Angel, Devil, Tiger Jackson, Roger Jr., Alex, Forest Law, Baek, Bruce, Wang, Ganryu, Kunimitsu, etc.) + newcomers Jaycee (Julia alter-ego), Slim Bob, Sebastian. **~120+ attire variations** across the roster.

---

## What's Blocked and Why

- **Extraction BLOCKED by disk space.** Archive (13.3GB) + extracted (13.45GB) = ~27GB needed simultaneously; disk cannot hold both above the 88% ceiling. Options: (1) split 7z to GitHub Release in 2GB chunks, delete local, re-download in pieces; (2) selective extraction of character/stage data only; (3) owner pulls to TeraBox from Archive.org directly. **Owner decision pending.**
- **Xbox 360 package decryption:** the Data0000–Data0051 blobs and the 3 large files in `00000002/` are Xbox 360 STFS/container format. Extraction needs Xbox 360 tooling (Velocity/Xbox 360 Content Manager equivalent, or Linux `xbox360` STFS parsers). The tekken-decrypt tool hunt (`~/workspace/tools/tekken-decrypt/`) pulled FModel + repak for Tekken 7 (UE4) — TTT2 is NOT UE4 (it's Namco's in-house engine), so a different extractor is needed.
- **Character models inside the blobs:** once extracted, expect Namco proprietary model format (not GMO — TTT2 is PS3/X360 era, likely the same family as Tekken 6's console format, distinct from PSP GMO).

---

## Chimera Build Value

- **59 fighters = the deepest reskin pool** of any chimera source game. Every Western Heart fighter concept can find a TTT2 base.
- **Tag-team systems:** 2v2 tag mechanics, tag assaults, tag throws — the template if Western Heart ever adds tag mode.
- **~120+ attires:** the largest alt-costume library; P2/customization variants for every base.
- **Fight Lab / Combot:** TTT2's Combot (customizable robot fighter) is a direct reference for a chimera create-a-fighter system.

---

## Next Steps

1. Owner decision: storage route for the 13.3GB archive (GitHub split / selective extraction / TeraBox)
2. Extract Xbox 360 containers → map internal file structure
3. Extract character models + attires → chimera reskin pool
4. Extract stages → chimera stage targets
5. Document the Namco X360 model format alongside the Tekken 6 findings
