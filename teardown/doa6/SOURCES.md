# Dead or Alive 6 — Sources

Every source searched for this lane (2026-11-20), what was pulled, and what
was not. Licence never gates pulling; it is logged honestly next to each
item.

## Pulled in whole (this PR)

| Item | Source | Version pinned | Licence | Verification |
| --- | --- | --- | --- | --- |
| Project-G1M | https://github.com/Joschuka/Project-G1M | main commit `d69a6d053ab9f038f4961e694a3a62a2aa2f689b`; latest release v1.8.2 tag `191825b` (28 Sep 2026) | GPL-2.0 | Upstream main tarball sha256 `589f63ccf2c813b23d11a436d06154b8e7dc5ffb8cad0ae36ee19c76f6856b92`; 33 files / 264,157 B; vendored tree under `tools/anim/doa6-project-g1m/` |
| RDBExplorer | https://github.com/MrIkso/RDBExplorer | main commit `22e72d8768092f8411480aaa7b8218c5003c8348`; releases: 5 tags, latest v1.0.1 | MIT | Upstream main tarball sha256 `842d4d5afc9af1d970dd573a37981e191d24011b48be2c0a97def35124fd6945`; 246 files / 2,800,992 B; vendored tree under `tools/anim/doa6-rdbexplorer/` |

Vendoring method: upstream tarballs fetched from codeload, extracted with
byte-exact verification against the tarball listings (sizes + sha256 of the
tarball). Two files are stored base64 (binary originals, no decoding on
disk): `Be.Windows.Forms.HexBox/HexBox.bmp`,
`Be.Windows.Forms.HexBox/HexBox.snk` — see the per-file note in
`tools/anim/doa6-rdbexplorer/README.md`. Everything else is vendored as
plain source files.

Project-G1M README carries a stale "Archiving this project…" note. It
predates the author's return: v1.7.5, v1.8.1 (Feb 2026, issue #52 fix +
release), v1.8.2 (28 Sep 2026) all shipped after it, and Joschuka answered
issues in Feb 2026. The project is maintained as of Sep 2026. "Copter" in
that note is collaborator hearhellacopters, whose fork carries fixes.

## Searched, NOT pulled (with reason)

| Item | Source | Why not pulled |
| --- | --- | --- |
| REDELBE 3.0 (DOA6 mod loader) | https://www.nexusmods.com/deadoralive6/mods/70, https://gamebanana.com/tools/10306 | Runtime texture/mesh layering loader, not an extractor. No public source repo found; distributed as a zip (CC BY-NC-ND 4.0). Needs the running game. Documented here for the mod-loading step; not needed to extract movesets. |
| qrdbtool (Lab of Lovers) | Community tool, no public GitHub found; credited in Steam Workshop / Skymods posts | Superseded for extraction by RDBExplorer (same job, maintained, MIT, public source). |
| DoA6LR_names.csv (SegadorMods) | Attached to https://www.patreon.com/SegadorMods/posts/how-to-install-6-162580752 | Name database for readable RDBExplorer extraction, derived from qrdbtool. Patreon-attached file; not fetched. Fetch it from that tutorial post when running the pipeline. |
| Kashira Mod Manager | https://github.com/umin135/KashiraModManager | DOA6 Last Round mod installer, not an extractor. Not needed for teardown. |
| DOA6 → GTA:SA animation packs (per-character .ifp) | https://www.gtainside.com/sanandreas/mods/213229-dead-or-alive-6-animation-kasumi/download/ (Kasumi 9.11 MB), Rig, Kokoro, Momiji, NiCO, Zack, Diego, Lisa Hamilton, Leifang | GTA San Andreas format, not WH-usable movesets; per-character partial sets (Kokoro's own page: "lacks kokoros whole animation set"). Cited as corroboration that G1A extraction works, not pulled. |
| DOA6 frame-data repos | Web search 2026-11-20 | No public DOA6 frame-data repo exists; top hits were SFV data (toolassisted/OKI) and Smash motion IDs. DOA frame data lives as community text (already the basis of `game/assets/movesets/doa-*.json`). |

## archive.org — checked LIVE 2026-11-21 00:38–00:51 UTC (not a stale note)

All hits are RAW FULL GAME / PATCH archives, not teardowns. None pulled.

| Item | Identifier | Contents | Size |
| --- | --- | --- | --- |
| Dead Or Alive 6 v1.22 incl. all DLCs | `dead.or.-alive.-6.v-1.22.-incl.-all.-dlcs` | `Dead.or.Alive.6.v1.22.Incl.ALL.DLCs.zip`, 2,554 files, md5 `3fdb316826354069f8b810a7a87c283c`, sha1 `0a7324343127e6c3fcfa17c20173fd82ad598ddf`, 2024-01-01 | 62,512,145,430 B |
| Dead or Alive 6 (repack, all DLCs) | `dead-or-alive-6-repack` | `Dead or Alive 6.zip`, 2,386 files, md5 `e0b8c0c166f3ac4cfc243d8f1862b22f`, 2026-06-27 | 62,377,013,534 B |
| Dead or Alive 6 Updates | `dead-or-alive-6-updates` | v1.21 (909,326,993 B) + v1.22 (2,285,940,921 B) + v1.22a (25,782,090 B) update archives, 2022-03-10 | 3,221,187,290 B total |

Identifier search `doa6` / `dead-or-alive-6` surfaced one extra hit only:
a `texts` spam page, not a teardown.

## SoulCalibur VI — no pull (reported, not rebuilt)

Searched the same way; NO complete working SCVI teardown exists anywhere
public. Evidence: umodel (Gildor) loads SCVI meshes/textures (AES key
public, UE 4.17) but animations are NOT supported — the gildor.org SC6
thread (crawled Nov 2026) records "Anim" = No, "nobody has cracked that
yet, only meshes and textures"; animations live in `.mot` files with no
public converter. FluffyQuack's tools (Fluffy Manager 5000, SC6 savegame
tool) do mod management / CaS import-export, not moveset/animation
extraction. Nexus hosts single-character Skyrim-format ports only (Kilik
MCO, Sophitia MCO by lingyt11) — partial, wrong format. FottenSC/Scuffle
reads SC6 movelist bytecode from LIVE process memory (needs the running
game + Cheat Engine addresses) — a research lead, not an extraction.
archive.org LIVE check 2026-11-21 00:38 UTC: exactly one software item,
`dixen-18-soulcalibur-vi` ("Soulcalibur VI (PC)", `[dixen18] Soulcalibur
VI.zip`, 11,441,266,068 B, md5 `55259ff04257400d1d0e23df4d8e05a1`, sha1
`feac0ac177d9dbcdeb2be1c49d0c147eb00f51e3`, 2026-05-21) — the raw full PC
game, not a teardown; already stored Nov 6–7 to WH+GRE releases
`soulcalibur6-archiveorg-20261106` (7×1.9 GB parts, whole-file md5/sha1
verified, pull-back verified), awaiting FreeArc `.dxn` extraction when disk
allows. Nothing further to pull for SCVI in this lane.
