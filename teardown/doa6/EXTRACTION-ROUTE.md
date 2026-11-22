# DOA6 extraction route — the fork, what was proven, what is still open

Lane 1D, 2026-11-22. How to get REAL DOA6 PC game files into the vendored
G1M/RDB toolchain, and why the complete native extraction is still open.

## The fork (read this first)

There are two different DOA6 PC releases, and the vendored toolchain docs
conflate them:

- **DOA6 v1.22 (2019, the 62 GiB game on archive.org)** — ships NO `root.rdb`.
  It ships 8 small `.rdb` index files + `.rdb.bin*` data segments + a `data/`
  dir of 2,165 hashed `.file` entries. The 8 indexes were fetched live via
  HTTP Range requests and fully inventoried (148,031 entries, ~105 GiB
  logical): see `probe/rdb-inventory.json` in the lane workdir.
- **DOA6 Last Round (2026 re-release)** — ships `root.rdb` (+ `root.rdx`),
  the format the vendored RDBExplorer was built/tested for (Nioh 3 + DOA6LR).

`teardown/doa6/README.md`'s "PC game ships as root.rdb" line describes Last
Round, not v1.22. The 62 GiB archive.org items were verified live to contain
no `root.rdb` / no `.rdx` (ZIP64 central directories parsed in full).

## Toolchain gap — proven, not assumed

The vendored RDBExplorer does NOT correctly read DOA6 (2019) `.rdb` location
metadata. Its `ParseLocation` handles binary 13-byte / 17-byte location
structs. DOA6 (2019) entries store the location as a NUL-terminated ASCII
string `<hex>@<hex>` (e.g. `5ac01@01c4a`), metadata sizes 8–20 bytes
(verified by dumping raw entry bytes). RDBExplorer would parse those ASCII
bytes as binary offsets (garbage) or skip them. The `Flags` field DOES encode
storage (0x00110000 = External+Zlib, 0x00120000 = Internal+Zlib), so the
compression side is readable — only the location resolution is broken.
The exact meaning of `hex@hex` is UNRESOLVED (offset@container-id is the
leading hypothesis, unverified).

What closes the gap (in order):
1. Extend RDBExplorer's `ParseLocation` to the ASCII `hex@hex` form and
   resolve it against the `.rdb.bin*` segments, OR find the DOA6-era tool
   that already reads it (qrdbtool / eterniti — NOT vendored here; a clone
   was removed on an execution-risk notice, do not re-clone without a
   parent/owner call).
2. The toolchain needs Windows (.NET 10 GUI RDBExplorer + Noesis +
   ProjectG1M.dll) or a proven Wine path. No Windows lane ran in this lane.
3. Then: game files → `.g1m`/`.g1t`/`.g1a`/`.g2a` → Noesis → FBX → WH bank.

## The 62 GiB route — what was proven without staging it

- Disk cannot stage 62 GiB (150G disk, ~119G used, quota wall binding).
- PROVEN: the game data IS range-fetchable. The 8 `.rdb` indexes were fetched
  with ~5 MB of downloads (Range requests, inflate with zlib, magic `_DRK0000`
  verified). The `.rdb.bin*` segments are individually range-fetchable the
  same way (largest single entry: `MaterialEditor.rdb.bin_0`, 14.88 GB
  uncompressed). CharacterEditor data totals ~2.9 GiB.
- So a streaming lane is possible: range-fetch one `.rdb.bin*` segment at a
  time (or one character's entries), extract, push to a release, delete the
  local segment. Nobody ran that lane here — it needs the location-format fix
  first (gap 1 above) and a Windows/Noesis step for the G1A/G2A decode.
- Kaggle/Colab/cloud-GPU route: NOT assessed in this lane (no status check
  run). It does not remove gap 1 or the Windows requirement; it only moves
  the disk problem. If a parent/owner wants it, the lane to run is: cloud box
  with the game files (or range-fetched segments) + the fixed RDBExplorer +
  Noesis, streaming outputs to a release.

## What this lane delivered instead (the closest complete thing)

The GTAV06 GTAinside `.ifp` packs (see GTAINSIDE-IFP.md): the complete DOA6
animation set as extracted by the community, converted to `wh-anim/1` and
banked in `game/assets/anim/doa6/`. Real extracted keyframes — but GTA:SA
format on a GTA ped skeleton, not DOA6-native G1A/G2A on a DOA6 skeleton.
That native extraction is still open pending gaps 1–3 above.

## DoA6LR_names.csv — still needs a browser task

- Source: SegadorMods Patreon post (public, no paywall):
  https://www.patreon.com/SegadorMods/posts/how-to-install-6-162580752
  Attachment `DoA6LR_names.csv` (7,733,875 B) + `RDBExplorer_v1.0.4.zip`.
  The unauthenticated Patreon API returns metadata only (no download URL);
  the HTML fetch hits a JS/bot wall. NEEDS a browser task (parent to
  arrange): open the post signed-in/JS-rendered and download the attachment.
- The CSV is the name table for DOA6LR's `root.rdb` (from qrdbtool) — it does
  NOT include any new Last Round costume. It is needed for the Last Round
  route, not for the v1.22 route.

## archive.org — checked live 2026-11-22

- `dead.or.-alive.-6.v-1.22.-incl.-all.-dlcs` (62,512,145,430 B, 2,554 files;
  md5 3fdb316826354069f8b810a7a87c283c, sha1 0a7324343127e6c3fcfa17c20173fd82ad598ddf)
- `dead-or-alive-6-repack` (62,377,013,534 B, 2,386 files)
- `dead-or-alive-6-updates` (v1.21 + v1.22 + v1.22a)
- Search `doa6 OR dead-or-alive-6*`: 37 hits — 3 software (above), 33 movies
  (combo-challenge/voice videos), 1 audio (Honoka voices), 1 texts spam page.
  NO teardown / extracted animation pack exists on archive.org.
