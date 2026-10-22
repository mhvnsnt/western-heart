# Soulcalibur II (Xbox) — Audio/Video Inventory (Phase 14, JOB 3)

## Audio — bgm.afs: 76 ADX entries decoded to FLAC

Source: `bgm.afs` (239,644,672 B), range-fetched from the release ISO asset at sector×2048 (header byte-identical to the phase-13 probed table). Every entry verified ADX by magic (`80 00`) + header fields; decoded with vgmstream-cli r2117 (already on disk at `~/workspace/tools/vgmstream/`) to WAV, then FLAC via ffmpeg (lossless). All 76 entries: 48,000 Hz, stereo, CRI ADX (coding type 3). Total decoded duration 73.8 min. Files live in GitHub release `scii-phase14-av`; sha256 per file in `PHASE14-AV-MANIFEST.json`.

| # | ADX bytes | Duration (s) | Samples | FLAC | FLAC bytes |
|---|---|---|---|---|---|
| 0 | 5633622 | 104.325 | 5007608 | bgm-00.flac | 14174493 |
| 1 | 1300480 | 24.076 | 1155640 | bgm-01.flac | 3285768 |
| 2 | 8183808 | 151.485 | 7271263 | bgm-02.flac | 19254898 |
| 3 | 180378 | 3.339 | 160277 | bgm-03.flac | 414311 |
| 4 | 234234 | 4.337 | 208160 | bgm-04.flac | 521224 |
| 5 | 183654 | 3.4 | 163197 | bgm-05.flac | 409939 |
| 6 | 241074 | 4.463 | 214218 | bgm-06.flac | 552530 |
| 7 | 294642 | 5.455 | 261825 | bgm-07.flac | 699999 |
| 8 | 256806 | 4.755 | 228219 | bgm-08.flac | 588933 |
| 9 | 1840626 | 34.084 | 1636052 | bgm-09.flac | 3912318 |
| 10 | 1880082 | 34.815 | 1671105 | bgm-10.flac | 4006070 |
| 11 | 1793826 | 33.218 | 1594447 | bgm-11.flac | 4144486 |
| 12 | 1737126 | 32.167 | 1544039 | bgm-12.flac | 4176101 |
| 13 | 10034010 | 185.814 | 8919052 | bgm-13.flac | 22419326 |
| 14 | 1537002 | 28.462 | 1366162 | bgm-14.flac | 3923679 |
| 15 | 971514 | 17.99 | 863520 | bgm-15.flac | 2315573 |
| 16 | 2572288 | 47.623 | 2285912 | bgm-16.flac | 6258794 |
| 17 | 2672640 | 49.428 | 2372520 | bgm-17.flac | 6536590 |
| 18 | 3534282 | 65.448 | 3141516 | bgm-18.flac | 7922110 |
| 19 | 3314934 | 61.386 | 2946532 | bgm-19.flac | 6801642 |
| 20 | 7282688 | 134.792 | 6470026 | bgm-20.flac | 16708940 |
| 21 | 4243456 | 78.562 | 3770996 | bgm-21.flac | 10964718 |
| 22 | 411498 | 7.619 | 365714 | bgm-22.flac | 662602 |
| 23 | 162558 | 3.009 | 144425 | bgm-23.flac | 350269 |
| 24 | 315414 | 5.84 | 280308 | bgm-24.flac | 564862 |
| 25 | 233262 | 4.318 | 207283 | bgm-25.flac | 492545 |
| 26 | 217998 | 4.035 | 193704 | bgm-26.flac | 472635 |
| 27 | 6483968 | 120.039 | 5761893 | bgm-27.flac | 16137436 |
| 28 | 5924864 | 109.677 | 5264501 | bgm-28.flac | 15077459 |
| 29 | 4825088 | 89.342 | 4288419 | bgm-29.flac | 11491630 |
| 30 | 4956160 | 91.746 | 4403809 | bgm-30.flac | 11733906 |
| 31 | 6105088 | 112.999 | 5423975 | bgm-31.flac | 14914703 |
| 32 | 5081088 | 94.052 | 4514486 | bgm-32.flac | 12677814 |
| 33 | 6135808 | 113.582 | 5451959 | bgm-33.flac | 15492780 |
| 34 | 4171776 | 77.236 | 3707306 | bgm-34.flac | 10475019 |
| 35 | 6207488 | 114.932 | 5516722 | bgm-35.flac | 14819637 |
| 36 | 7827456 | 144.913 | 6955835 | bgm-36.flac | 18847781 |
| 37 | 5048320 | 93.422 | 4484236 | bgm-37.flac | 13143140 |
| 38 | 827190 | 15.317 | 735209 | bgm-38.flac | 2090964 |
| 39 | 4214784 | 78.035 | 3745666 | bgm-39.flac | 11000448 |
| 40 | 4251648 | 78.693 | 3777266 | bgm-40.flac | 11070625 |
| 41 | 5705728 | 105.623 | 5069886 | bgm-41.flac | 14502886 |
| 42 | 5650432 | 104.584 | 5020037 | bgm-42.flac | 14910329 |
| 43 | 5910528 | 109.41 | 5251663 | bgm-43.flac | 14442225 |
| 44 | 1368064 | 25.321 | 1215402 | bgm-44.flac | 3148263 |
| 45 | 2656256 | 49.159 | 2359638 | bgm-45.flac | 6283918 |
| 46 | 2488320 | 46.019 | 2208904 | bgm-46.flac | 6008444 |
| 47 | 2459648 | 45.487 | 2183357 | bgm-47.flac | 6463147 |
| 48 | 2355200 | 43.56 | 2090889 | bgm-48.flac | 5812567 |
| 49 | 2519040 | 46.586 | 2236112 | bgm-49.flac | 6524043 |
| 50 | 1718272 | 31.779 | 1525386 | bgm-50.flac | 3763076 |
| 51 | 2521088 | 46.628 | 2238145 | bgm-51.flac | 5510454 |
| 52 | 2267136 | 41.949 | 2013575 | bgm-52.flac | 5551756 |
| 53 | 2062336 | 38.164 | 1831879 | bgm-53.flac | 5132584 |
| 54 | 1677312 | 30.994 | 1487723 | bgm-54.flac | 4224642 |
| 55 | 4782080 | 88.528 | 4249328 | bgm-55.flac | 11301867 |
| 56 | 4247552 | 78.62 | 3773737 | bgm-56.flac | 10730905 |
| 57 | 4579328 | 84.755 | 4068240 | bgm-57.flac | 11660509 |
| 58 | 313254 | 5.8 | 278400 | bgm-58.flac | 498885 |
| 59 | 2820096 | 52.164 | 2503891 | bgm-59.flac | 6393796 |
| 60 | 8183808 | 151.485 | 7271263 | bgm-60.flac | 19254898 |
| 61 | 270162 | 5.001 | 240069 | bgm-61.flac | 573314 |
| 62 | 324270 | 6.004 | 288175 | bgm-62.flac | 697984 |
| 63 | 270594 | 5.009 | 240453 | bgm-63.flac | 487105 |
| 64 | 324738 | 6.012 | 288579 | bgm-64.flac | 705005 |
| 65 | 216486 | 4.007 | 192357 | bgm-65.flac | 472668 |
| 66 | 485622 | 8.992 | 431615 | bgm-66.flac | 1135214 |
| 67 | 635130 | 11.76 | 564495 | bgm-67.flac | 1474199 |
| 68 | 553626 | 10.251 | 492040 | bgm-68.flac | 1250026 |
| 69 | 691182 | 12.798 | 614319 | bgm-69.flac | 1328925 |
| 70 | 17590374 | 325.747 | 15635840 | bgm-70.flac | 41745993 |
| 71 | 1297314 | 24.023 | 1153120 | bgm-71.flac | 2777338 |
| 72 | 862974 | 15.98 | 767040 | bgm-72.flac | 1727485 |
| 73 | 330822 | 6.125 | 294000 | bgm-73.flac | 711244 |
| 74 | 11282432 | 208.89 | 10026697 | bgm-74.flac | 26760130 |
| 75 | 4337664 | 80.287 | 3853767 | bgm-75.flac | 11195650 |

## Video — movie.afs: 3 MPEG-PS entries, byte-carried

Source: `movie.afs` at sector×2048 (header byte-verified). Entries extracted byte-exact (no transcode) and probed with ffprobe/ffmpeg. Files live in GitHub release `scii-phase14-av`; sha256 in `PHASE14-AV-MANIFEST.json`.

| # | File | Bytes | Video | Audio | Duration (s) |
|---|---|---|---|---|---|
| 0 | movie0.mpg | 402294784 | mpeg1video 640x368 @30000/1001 | adpcm_adx 48000 Hz stereo | 148.9 |
| 1 | movie1.mpg | 17285120 | mpeg1video 640x448 @30000/1001 | adpcm_adx 48000 Hz stereo | 24.006 |
| 2 | movie2.mpg | 19556352 | mpeg1video 640x448 @30000/1001, 457 frames | PES 0xC0 present; ffprobe misdetects codec (Sofdec ADX-in-PS family, cf. movie1) | 15.54 |

Notes: movie2's audio PES (stream 0xC0) is present from the first pack, but ffprobe's PS demuxer misidentifies its codec (mp2 parse errors); its sibling movie1 with the same Sofdec multiplex identifies cleanly as ADX. The file is shipped byte-exact regardless — identification does not gate extraction. movie2 duration is from its video stream (457 frames @ 30000/1001 ≈ 15.54 s; ffprobe reports no container duration).
