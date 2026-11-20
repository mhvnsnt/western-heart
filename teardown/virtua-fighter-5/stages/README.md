# VF5 Extracted Stages

All stage/arena geometry from Virtua Fighter 5 PS3 (BLES00029), extracted with
`../tools/farc_extract.py`. Each `stg*.farc` on GitHub Release `vf5-ps3-v1`
contains `stgXXX_obj.bin` (geometry) + `stgXXX_tex.bin` (textures), decompressed
from the FArC container.

Inner file counts verified with farc_extract.py on every archive (all 38 parse
clean; each holds exactly 1 obj + 1 tex).

## Stage archives (18 arenas)

| Code | .farc | Uncompressed | BGM track | Confident ID |
|------|-------|--------------|-----------|--------------|
| are | `stgare.farc` | 57.3MB | vf5b_are.adx | Arena (Akira) |
| aur | `stgaur.farc` | 61.7MB | vf5b_aur.adx | — |
| ban | `stgban.farc` | 48.5MB | vf5b_ban.adx | — |
| bar | `stgbar.farc` | 38.8MB | vf5b_bar.adx | Bar (Brad) — confirmed by stage-select UI symbol `stage_icon_bar` |
| cas | `stgcas.farc` | 45.8MB | vf5b_cas.adx | — |
| djo | `stgdjo.farc` | 47.5MB | vf5b_djo.adx | Dojo |
| dur | `stgdur.farc` | 57.8MB | vf5b_dur.adx | Dural's stage |
| hai | `stghai.farc` | 44.9MB | vf5b_hai.adx | — |
| jin | `stgjin.farc` | 53.3MB | vf5b_jin.adx | Shinto Shrine (Kage) — `jin` = jinja |
| nyc | `stgnyc.farc` | 60.1MB | vf5b_nyc.adx | New York City (Jacky) — confirmed by stage-select UI symbol `stage_icon_nyc` |
| riv | `stgriv.farc` | 55.8MB | vf5b_riv.adx | River (Shun) |
| sin | `stgsin.farc` | 36.8MB | vf5b_sin.adx | — |
| slk | `stgslk.farc` | 48.1MB | vf5b_slk.adx | — |
| tak | `stgtak.farc` | 59.0MB | vf5b_tak.adx | — |
| tan | `stgtan.farc` | 31.6MB | vf5b_tan.adx | — |
| ter | `stgter.farc` | 37.6MB | vf5b_ter.adx | Terrace |
| umi | `stgumi.farc` | 50.8MB | vf5b_umi.adx | Sea — `umi` = sea in Japanese (Jeffry) |
| yuk | `stgyuk.farc` | 48.4MB | vf5b_yuk.adx | Snow — `yuki` = snow (Vanessa) |

Codes marked "—" are left as codes: the on-screen display names are baked into
stage-select UI textures (AET/PIC), not plaintext. Each code's BGM track is
confirmed from USRDIR/fcache.txt, so the stage↔code mapping is game-verified.

## Training / special stages (20 archives)

| Code | .farc | Uncompressed | Notes |
|------|-------|--------------|-------|
| tr2–tr9 | `stgtr2.farc` … `stgtr9.farc` | 17–21MB each | training-stage variants (8 files) |
| trm | `stgtrm.farc` | 28.4MB | training (menu?) |
| trn | `stgtrn.farc` | 17.0MB | training |
| trs | `stgtrs.farc` | 4.5KB | training stub — tiny |
| ts2, ts3 | `stgts2.farc`, `stgts3.farc` | ~1.4–1.5MB | test stages |
| tst | `stgtst.farc` | 935KB | test stage |
| du1–du4 | `stgdu1.farc` … `stgdu4.farc` | 0.7–2.2MB | Dural-related stages |
| cid | `stgcid.farc` | 16KB | stub |
| wht | `stgwht.farc` | 4.5KB | stub |

**Scale check:** largest arena geometry (`stgaur` 61.7MB, `stgnyc` 60.1MB
uncompressed) lines up with the documented "up to 300,000 polygons per stage"
for VF5.

**Next step for import:** same pipeline as characters — decompressed
`*_obj.bin` via the chrrox 3ds Max script, `*_tex.bin` via TXP.bms (QuickBMS).
