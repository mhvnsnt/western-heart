# TTT2 Xbox 360 — XDVDFS File Listing

**Source:** GoD package (Title ID `4E4D0859`), via `tools/surgical/god_carve.py`  
**Date:** 2026-10-24  
**Method:** Data0000–Data0004 stream-decoded from release `ttt2-7z-v1` (CRC32-verified vs INVENTORY.md), XDVDFS volume parsed at sector 32.

## Summary

78 files in the XDVDFS image (8.86GB total):
- `$SystemUpdate/` — 32 Xbox 360 system files (not game data)
- `AvatarAssetPack` (14MB), `Default.xex` (16MB, game executable)
- `data000.bin` … `data053.bin` — game data archives (numbering has gaps)
- `nrfo.bin` (299KB), `nxeart` (2.3MB)

## Game data archives (dataNNN.bin)

| File | Size | Start Data | Format (identified) |
|------|------|------------|---------------------|
| data000.bin | 4,064,970 | Data0004 | `0ff512ed` archive |
| data001.bin | 385,691,766 | Data0023 | (not yet pulled) |
| data002.bin | 38,587,710 | Data0025 | (not yet pulled) |
| data003.bin | 75,648,926 | Data0022 | (not yet pulled) |
| data004.bin | 4,075,114 | Data0025 | (not yet pulled) |
| data005.bin | 170,814,504 | Data0004 | (not yet pulled) |
| data006.bin | 20,354,904 | Data0004 | `0ff512ed` archive |
| data007.bin | 91,576,894 | Data0021 | (not yet pulled) |
| data008.bin | 129,855,846 | Data0005 | (not yet pulled) |
| data009.bin | 206,359,646 | Data0006 | (not yet pulled) |
| data010.bin | 199,306,610 | Data0007 | (not yet pulled) |
| data011.bin | 227,421,262 | Data0008 | (not yet pulled) |
| data012.bin | 175,345,986 | Data0010 | (not yet pulled) |
| data013.bin | 215,050,692 | Data0017 | (not yet pulled) |
| data014.bin | 173,896,704 | Data0019 | (not yet pulled) |
| data015.bin | 158,247,204 | Data0020 | (not yet pulled) |
| data016.bin | 56,362,068 | Data0021 | (not yet pulled) |
| data017.bin | 356,418,750 | Data0011 | (not yet pulled) |
| data018.bin | 557,332 | Data0031 | (not yet pulled) |
| data019.bin | 31,624 | Data0025 | (not yet pulled) |
| data025.bin | 189,334,638 | Data0013 | (not yet pulled) |
| data026.bin | 256 | Data0031 | (not yet pulled) |
| data027.bin | 613,117,984 | Data0014 | (not yet pulled) |
| data028.bin | 102,209,010 | Data0022 | (not yet pulled) |
| data034.bin | 199,287,232 | Data0003 | MP4 movie (`ftypnrfi`) |
| data035.bin | 250,237,456 | Data0028 | (not yet pulled) |
| data036.bin | 379,630,736 | Data0025 | (not yet pulled) |
| data037.bin | 305,710,000 | Data0029 | (not yet pulled) |
| data038.bin | 306,422,144 | Data0031 | (not yet pulled) |
| data039.bin | 464,935,296 | Data0033 | (not yet pulled) |
| data040.bin | 255,621,792 | Data0035 | (not yet pulled) |
| data041.bin | 436,231,024 | Data0037 | (not yet pulled) |
| data042.bin | 326,598,144 | Data0040 | (not yet pulled) |
| data043.bin | 302,789,856 | Data0001 | MP4 movie (`ftypnrfi`) |
| data044.bin | 437,646,976 | Data0041 | (not yet pulled) |
| data045.bin | 300,581,968 | Data0044 | (not yet pulled) |
| data046.bin | 222,882,496 | Data0000 | MP4 movie (`ftypnrfi`) |
| data047.bin | 429,342,832 | Data0046 | (not yet pulled) |
| data050.bin | 3,683,036 | Data0048 | (not yet pulled) |
| data051.bin | 51,581,392 | Data0025 | (not yet pulled) |
| data052.bin | 2,659,880 | Data0025 | (not yet pulled) |
| data053.bin | 412,736 | Data0025 | (not yet pulled) |

## Format notes

- **MP4 movies** (`ftypnrfi` brand): data034, data043, data046 — cutscenes/movies, not character data.
- **`0ff512ed` archives**: data000, data006 — proprietary Namco format (magic `0ff512ed`, version 1). Content is compressed/encrypted (not zlib/lzma). Format not publicly documented; requires reverse-engineering.
- **Character data** (Law, Lars, etc.) is inside the dataNNN.bin archives. Specific file identification requires parsing the `0ff512ed` format or examining more bins.

## Full listing

```
    15597568  $SystemUpdate/AvatarEditor.xex
     3837952  $SystemUpdate/BiometricSetup.xex
      421888  $SystemUpdate/Dash.FieldCalibration.lex
      114688  $SystemUpdate/Dash.Kiosk.lex
       61440  $SystemUpdate/Dash.NetworkStorage.lex
     1953792  $SystemUpdate/Dash.NuiTroubleshooter.lex
      188416  $SystemUpdate/Dash.Search.xex
     1130496  $SystemUpdate/FFFE07DF00000001
    15958016  $SystemUpdate/FFFE07DF00000002
    10498048  $SystemUpdate/FFFE07DF00000006
    28680192  $SystemUpdate/FFFE07DF00000008
      466944  $SystemUpdate/Guide.AccountRecovery.xex
      413696  $SystemUpdate/Guide.AvatarMiniCreator.xex
       57344  $SystemUpdate/Guide.Fitness.xex
      258048  $SystemUpdate/Guide.NuiTroubleshooter.xex
      147456  $SystemUpdate/Xam.Community.xex
       90112  $SystemUpdate/Xam.LiveMessenger.xex
       20480  $SystemUpdate/Xam.WordRegister.xex
      573440  $SystemUpdate/XimeDic.xex
       69632  $SystemUpdate/XimeDicCh.xex
      512000  $SystemUpdate/Xna_TitleLauncher.xex
     1429504  $SystemUpdate/dash.ExtraAVCodecs.xex
     1507328  $SystemUpdate/dash.NuiFirstUse.xex
      188416  $SystemUpdate/dash.firstuse.xex
      434176  $SystemUpdate/dash.natalpregame.xex
     1470464  $SystemUpdate/dashnui.xex
      315392  $SystemUpdate/livepack.xex
       16384  $SystemUpdate/natalsu.xex
       28672  $SystemUpdate/nuihud.xex
    12324864  $SystemUpdate/su20076000_00000000
        6484  $SystemUpdate/system.manifest
      368640  $SystemUpdate/ximedicex.xex
    13799424  AvatarAssetPack
    15941632  Default.xex
     4064970  data000.bin
   385691766  data001.bin
    38587710  data002.bin
    75648926  data003.bin
     4075114  data004.bin
   170814504  data005.bin
    20354904  data006.bin
    91576894  data007.bin
   129855846  data008.bin
   206359646  data009.bin
   199306610  data010.bin
   227421262  data011.bin
   175345986  data012.bin
   215050692  data013.bin
   173896704  data014.bin
   158247204  data015.bin
    56362068  data016.bin
   356418750  data017.bin
      557332  data018.bin
       31624  data019.bin
   189334638  data025.bin
         256  data026.bin
   613117984  data027.bin
   102209010  data028.bin
   199287232  data034.bin
   250237456  data035.bin
   379630736  data036.bin
   305710000  data037.bin
   306422144  data038.bin
   464935296  data039.bin
   255621792  data040.bin
   436231024  data041.bin
   326598144  data042.bin
   302789856  data043.bin
   437646976  data044.bin
   300581968  data045.bin
   222882496  data046.bin
   429342832  data047.bin
     3683036  data050.bin
    51581392  data051.bin
     2659880  data052.bin
      412736  data053.bin
      298696  nrfo.bin
     2306048  nxeart
```
