# Street Fighter IV — sources

Checked live 2026-11-20. Licence status never gated this pull; sources
are logged honestly below.

## Pulled: Dantarion `sf4tools` (vendored whole)

- Source repo: https://github.com/dantarion/sf4tools
- Description: "Set of tools of manipulating and editing files from the
  Super Street Fighter 4 series of games from Capcom"
- Licence: MIT — licence file vendored at `tools/sf4tools/LICENSE`
- Source branch/commit: `master` at
  `e5c17132f3b6e63f66150c3a347a9e8f6e0d73a4` (2015-05-06, "Fixed version
  names, link generation, probably other stuff, idk")
- Vendored under: `tools/sf4tools/` (upstream paths preserved beneath)
- What it is: `SFUltraDiff/src/` Python code (`bac.py`, `bcm.py`,
  `diff.py`, `util.py`) that parses `#BAC` moveset files and `.bcm`
  input/cancel files and dumps them as JSON; `SFUltraDiff` builds
  automated per-character changelists across Super / AE / 2012 from a
  SF4 PC install. The `html/` tree is the vendored Bootstrap 3 web UI
  for those changelists.
- Verification: `bac.py` was read before pulling — it opens `#BAC`
  files, detects endianness, reads the name-offset tables, and exports
  JSON. It is the moveset format as cracked by the SFIV modding
  community.

### Per-file sha256 (upstream content, as fetched 2026-11-20)

| File (under `tools/sf4tools/`) | Bytes | sha256 |
|---|---|---|
| `.gitignore` | 586 | `d26aa47144916b51d2ece66fda63e22c80b66c2eed9714f040d6ef4626909589` |
| `LICENSE` | 1075 | `91ff393f72b5f30ad9199a19ad47bcdaf5944656b6327c16da66422e2edc1edf` |
| `README.md` | 565 | `48f9111fd93bcaf9630959827d23d43eb06369ca298eefb33a7ba083bc7d9778` |
| `SFUltraDiff/html/css/bootstrap-theme.css` | 14936 | `382a4120b748eaf656e422f2f27c8778d311fabb97a644db97011ec176c130bf` |
| `SFUltraDiff/html/css/bootstrap-theme.css.map` | 38388 | `5455e0071ac2792bc84c1b45fdce0c7f2eefbb49b35b0b7d096b6ecb584b3ac0` |
| `SFUltraDiff/html/css/bootstrap-theme.min.css` | 13185 | `c72060928bf66e8ff55b42e653f95429d4777769d790921ff8390eb1068da303` |
| `SFUltraDiff/html/css/bootstrap.css` | 121220 | `0e430441e9833f9e3b9219b4837068670afbb50171678365b95f45de9291b632` |
| `SFUltraDiff/html/css/bootstrap.css.map` | 245960 | `aaf99fdfeec73316716454ce5d2c51eb54efa6f98710c7c45d73207f94a2607c` |
| `SFUltraDiff/html/css/bootstrap.min.css` | 99961 | `e9503448692b738dd260fbd7f7cabf2e11f09b600fa97e6eb3a56eba5b1a7e9b` |
| `SFUltraDiff/html/fonts/glyphicons-halflings-regular.eot` | 20335 | `f495f34e4f177cf0115af995bbbfeb3fcabc88502876e76fc51a4ab439bc8431` |
| `SFUltraDiff/html/fonts/glyphicons-halflings-regular.svg` | 62927 | `d168d50a88c730b4e6830dc0da2a2b51dae4658a77d9619943c27b8ecfc19d1a` |
| `SFUltraDiff/html/fonts/glyphicons-halflings-regular.ttf` | 41280 | `bd18efd3efd70fec8ad09611a20cdbf99440b2c1d40085c29be036f891d65358` |
| `SFUltraDiff/html/fonts/glyphicons-halflings-regular.woff` | 23320 | `fc969dc1c6ff531abcf368089dcbaf5775133b0626ff56b52301a059fc0f9e1e` |
| `SFUltraDiff/html/js/bootstrap.js` | 55258 | `a9d250db6b377dcc698f55167295d617b6eee4d5936121ff91eca5e7e140c361` |
| `SFUltraDiff/html/js/bootstrap.min.js` | 29110 | `898d05a17f2cfc5120ddcdba47a885c378c0b466f30f0700e502757e24b403a1` |
| `SFUltraDiff/src/bac.py` | 18015 | `e1c993e3b91ac109776c2739cc301c3b558a7628b86bf3dcd7be4341db88ffbd` |
| `SFUltraDiff/src/bcm.py` | 12589 | `e06c9e58b548a12672fa83279d49b51d367a0c2f35cfe9a3757afc7347d8f704` |
| `SFUltraDiff/src/diff.py` | 11214 | `41d3e1f0ad40b63c7657b9516aa0aa1f678f234aebc2395aaddfdbcde940a998` |
| `SFUltraDiff/src/util.py` | 5489 | `de026aa54f0df1ecb226c49da04b59147da7fb205ee82c5800fa84da96264941` |

## Recorded, NOT vendored: `jvankooo/sf4-nx`

- Repo: https://github.com/jvankooo/sf4-nx — static-recomp port of
  Street Fighter IV (Xbox 360) to Switch (ReXGlue + XenosRecomp +
  Vulkan). GPL-3.0. Tip commit
  `06cd530bca8e5dbbebe609c09f2183070ab05273`, release v0.1.0.
- Full record in `sf4-nx.md`, including why it was recorded and not
  vendored (29.7 MB / 1,677 files, mostly generic shared SDK; no
  game-derived content; needs the owner's Xbox 360 disc).

## Searched, NOT found (no complete extracted pack anywhere)

- archive.org, live 2026-11-20: 40 software items across the three
  games — all raw game images/builds/prototypes/fixes/MUGEN. No
  teardown, no decomp, no extracted moveset pack. File lists inspected
  for `Street_Fighter_IV_CSF` (4.49 GB Steam files),
  `ultra-street-fighter-iv.-xbox-360` (8.25 GB image),
  `street-fighter-x-tekken_202409` (1.66 GB files),
  `street-fighter-vs-tekken` (4.69 GB ISO),
  `PS3_BLES01252_Updates` (28.6 MB update pkg).
- GitHub: no SFIV/SFxT/USFIV moveset dump, no USFIV recomp, no SFxT
  recomp (Facebook "SFxT RECOMP" logo only, no code).
- Models Resource: USFIV page has 2 assets total (Adon DAE 14.21 MB +
  1 stage element); no SFIV roster pack; no SFxT page.
- Modding tools that exist but were NOT pulled (need game files to
  run; no GitHub mirror / dead hosts): piecemontee SF4 Asset Explorer
  v0.38 (SourceForge mercurial source; binary on mediafire), Dantarion
  Ono! bac/bcm editor (host watissf.dantarion.com unreachable;
  `dantarion/ono` is 404), Anotak bcm tool, Sloth86 EMG tools,
  mariokart64n SFxT Importer (DeviantArt maxscript).

## Repo state before this pull

- `mhvnsnt/western-heart` already held SF EX teardowns
  (`teardown/street-fighter-ex-plus-alpha/`, `-ex2-plus/`, `-ex3/`,
  `teardown/street-fighter-3d-games/` with `extracted/` +
  `tools/build_sf_movesets*.py` + `pac_index.py`) and SFV
  (`teardown/street-fighter-5/`). No sfiv/sfxt/usfiv directory
  existed before this pull. SF EX `PL/*.PAC` clips are held with NO WH
  bank converter and the P00X index → character names is not
  established — the same converter gap now applies to bac/bcm.
