# JOIN SEARCH — ROUND 3 (Target-0 completeness, XEX lane, 2026-11-04)

Method: identical to rounds 1–2 (`tools` = `decode/join-round2/scan_container.py` v3:
magic census MOTA/bxml/mvlt/BXML/MVLT/NTXR/GIDX/NSXR/MBB/PCTB/MCAM, MOTA table
parse with 0x64/0xC8 marker sampling, BE-u16 index-run hunt (values 1..1874,
run >= 24), NRFI box walk. Source assets pulled from release
`ttt2-work-archive-2026-10-30` (mhvnsnt/western-heart); every .gz sha256
verified EXACT against `scan0/expected.json` before decompression.

## Containers scanned

| container | decoded bytes | sha256 of source .gz (verified) | census highlights | verdict |
|---|---|---|---|---|
| data003 | 334,336,624 | 790a0b41daf41441ee321c05c194a983c6288bd341ad8c2a858d34404d52c17a | NTXR 3826, GIDX 4439, MOTA 0, BXML/MVLT 0 | texture container — NO join |
| data005 | 283,908,372 | f947a5e8a10ee9531fa84d502b9c20d87d61d03cb0a91b43f805dc0b640f8c7e | MOTA 330 strings / 206 plausible tables (counts up to 654), BXML/MVLT 0 | motion container — MOTA tables only, NO join |
| data006 | 77,278,156 | 1f7ddf493f0d7ce5a7f916d3e81cd5028adad40eff81c0f64ac6ead8ecfd16b2 | MOTA 330 / 129 plausible, BXML/MVLT 0 | motion container — NO join |
| data019 | 177,104 (LZX chunks x6 reassembled in order) | 234967b3c22c1aa39071dacc888b5101edf96454018559c9a55580ebc6129b01 (tar) | all-zero census; strings = tutorial xtal scripts (`libtutorial.xtal`, Stage1Info) | tutorial scripts — NO join |
| data050 | 44,928,288 | f14e0858d3195bfeb221f5b4e72a002ca526d8480d4bcc43706cb8206f36e4a5 | all-zero census, no u16 runs >= 29 | NO join |
| data051 | 165,763,536 | f325cd094087f71e226b2d14aec17ee2a32629c0126e1b31e183606c742e9682 | NTXR 61, GIDX 21612, MOTA 0, BXML/MVLT 0 | texture container — NO join |
| data053 | 3,461,024 (LZX chunks x107 reassembled in order) | 1124e3429de33d26e1fff51f9293dea4cf0477b524fda2f2a838bb3ea72cfe72 (tar) | BXML x1 at offset 256 (imge payload start) | see below — NO join |

## data053 BXML — identified, not a moveset

The single `BXML` at offset 256 heads the NRFI `imge` payload. Its string
table identifies it as the customization/equipment database, not a character
moveset: `Fighter`, `Equipment`, `Position`, `citemid`, `instances`,
`uju_cmn_aur_type1green`, `defitem`, `emblem`, `technique`, `printpattern`
(aura/item definitions). No mvlt, no MOTA reference, no u16 index runs >= 24.
It contains no per-move animation indices.

## Conclusion (rounds 1+2+3 combined)

Every decoded TTT2 container has now been scanned with the same method.
The per-move -> MOTA-index join exists in NONE of them. The only new motion
data found in round 3 is additional MOTA tables in data005/data006 (more
clips for the 0x64 decoder to cover — the game's decompression routine in
default.xex serves all containers). The join remains where Kiloutre reads
it: live-memory motbin `anim_addr`, reachable via the default.xex analysis
(Targets 2-4) or the RPCS3 live-memory fallback.

Scan JSONs: `xex-lane/scan0/data{003,005,006,019,050,051,053}-scan.json`.
