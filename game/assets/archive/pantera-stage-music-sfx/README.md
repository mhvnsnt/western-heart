# Pantera former voice-slot files — RENAMED, not deleted

Owner order 2026-10-24 21:28 CDT: "the files that are getting deleted just rename them to let them know what they actually supposed to be."

These 9 OGG files were deleted from `game/assets/voices/pantera/` by merged PR #1028. This directory restores them byte-for-byte (same blob SHAs as pre-merge main) under correctly-labeled names. They are stage music/SFX per the prior project record quoted in `game/data/voices/pantera.json` — NOT King voice — and they are NOT wired into the Pantera voice pools. The 52-clip Pantera voice set (`pantera-t2-*.ogg` + `pantera-classic-*.ogg` in `game/assets/voices/pantera/`) is unchanged by this restore.

Honesty note: the music-vs-SFX split for these 9 clips has NOT been verified by ear. The names say stage-music-sfx because that is what the prior project record states. Do not present any of these 9 as voice, and do not wire them into voice triggers without an owner ear check.

## Old name -> new name

- `game/assets/voices/pantera/intro-01.ogg` (23172 bytes, blob `dfdd252a555209f568373578466e77b28478d6ee`) -> `game/assets/archive/pantera-stage-music-sfx/stage-music-sfx-intro-01.ogg`
- `game/assets/voices/pantera/intro-02.ogg` (18395 bytes, blob `e41339278faaa8820083cce204cd772c3971a2f2`) -> `game/assets/archive/pantera-stage-music-sfx/stage-music-sfx-intro-02.ogg`
- `game/assets/voices/pantera/win-01.ogg` (36483 bytes, blob `f16f1d0345de3874cc8665b92e2b73c7bd0d3557`) -> `game/assets/archive/pantera-stage-music-sfx/stage-music-sfx-win-01.ogg`
- `game/assets/voices/pantera/win-02.ogg` (32203 bytes, blob `2bafc687c2f76f24419353d9226518d21e688eb4`) -> `game/assets/archive/pantera-stage-music-sfx/stage-music-sfx-win-02.ogg`
- `game/assets/voices/pantera/taunt-01.ogg` (36412 bytes, blob `d8d2a0e33aac79dede940420b0ed89fb64bee493`) -> `game/assets/archive/pantera-stage-music-sfx/stage-music-sfx-taunt-01.ogg`
- `game/assets/voices/pantera/taunt-02.ogg` (51902 bytes, blob `0c6706300d6be44531da3b7de29b5712318dc451`) -> `game/assets/archive/pantera-stage-music-sfx/stage-music-sfx-taunt-02.ogg`
- `game/assets/voices/pantera/hit-01.ogg` (15816 bytes, blob `ce465589e5841fa573e1c6924951bf6dcb9bfb63`) -> `game/assets/archive/pantera-stage-music-sfx/stage-music-sfx-hit-01.ogg`
- `game/assets/voices/pantera/ko-01.ogg` (21987 bytes, blob `5d58f6d80a9a89a13b44005c0b83e51d9ea9cd49`) -> `game/assets/archive/pantera-stage-music-sfx/stage-music-sfx-ko-01.ogg`
- `game/assets/voices/pantera/select-01.ogg` (4064 bytes, blob `13c2a6919112ee9ae71bd8a3406fbb1c2974f44e`) -> `game/assets/archive/pantera-stage-music-sfx/stage-music-sfx-select-01.ogg`

Restored from pre-merge main commit `62a44a2c64133a793725dd68ced03b712236f034` (first parent of PR #1028 merge commit `6ee90f40f6dfb49248a3d699a963e1f318f4b6d5`).
