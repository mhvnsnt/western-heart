# Other source games and libraries for Western Heart + the Cape Jones show (ranked, 2026-10-23 CT)

Owner pt128u: "any other thing you can pull in that's open source or industry standard or any stuff from video games or 3D shows". Ranked by what it gives us now ÷ effort. Licensing: open sources ship; game rips stay in private builds (no public Namco/other-IP distribution, standing rule).

| # | Source | Gives us | How to extract | On box? |
|---|---|---|---|---|
| 1 | **CMU Graphics Lab Mocap** (2,500+ takes; free incl. commercial) | Show clips (idle, walk, sit, talk, wave, react), boxing guard and strikes, get-ups | BVH → `tools/anim-retarget/retarget_rot.py` + `bone_maps/cmu_to_wh.json` | Yes. `oss-anim-staging/cmu-mocap-bvh`, `cape-jones/3d-assets/animation/mocap-cmu` |
| 2 | **Tekken 8** (owner's copy) | Alisa and the whole cast's motion, menus, select, customization | `docs/tech/T8-EXTRACTION.md` | No (needs Paks) |
| 3 | **Tekken 7** (owner's copy) | Same as T8, UE4. UModel works as well as CUE4Parse | Same exporter with `--game GAME_TEKKEN7`; UModel `-game=tekken7` | No |
| 4 | **Quaternius UAL 1+2, KayKit** (CC0) | 80+ stylized locomotion, combat and emote clips | GLB → `retarget_rot.py` (needs a `ual_to_wh` map) | Yes. `oss-anim-staging/` |
| 5 | **ACCAD Open Motion, 100STYLE** (CC-BY) | Stylized walks (100 styles) and martial-art takes | BVH → `retarget_rot.py` | Yes. `oss-anim-staging/` |
| 6 | **Mixamo** (free, Adobe ID; royalty-free in games) | 2,000+ fight and show clips, Mixamo-named (our rig) | FBX → `retarget_blender.py`/`retarget_rot.py` with `mixamo_to_wh.json` | Owner login needed |
| 7 | **Tekken 6 / TTT2** (existing teardowns) | T6 Alisa (`asa`) motion is in the data once decoded; TTT2 roster | `teardown/tekken6/` (EBOOT decrypted; DATA401 notes), `teardown/tekken-tag-tournament-2/` | Partly (motion not yet decoded) |
| 8 | **Soulcalibur VI, Dead or Alive 6, Street Fighter 6/5** | Weapon/fight motion, menus, costumes | UE4 (SC6, SF5): UModel/CUE4Parse. DOA6: `fatal_frame`-style `.g1m/.g1a` (Noesis); SF6 (RE Engine): RETool + REE pak unpacker | Partial teardowns in `teardown/` |
| 9 | **Virtua Fighter 5 R.E.V.O.** (UE4 PC) | Wolf Hawkfield (Nightwolf owner ask), VF motion | CUE4Parse/UModel | Models only; motion never converted |
| 10 | **Def Jam FFNY, WWE 2K, Urban Reign** | Grapple/brawl motion, crowd and arena | Existing teardown folders; RenderWare/2K tools per `teardown/RE-TOOLCHAIN.md` | Partial |
| 11 | **AI video-to-mocap** (Rokoko Vision free tier; open: FreeMoCap, 4DHumans/WHAM) | Turn any show/fight reference video into BVH | Video → BVH → `retarget_rot.py` | Pipeline in `/workspace/mocap-src` |
| 12 | **3D shows / film assets** (Blender Open Movies: Sprite Fright, Charge, Wing It; CC-BY) | Production rigs, cartoon acting reference and cameras for the Cape Jones show | `.blend` → Blender → GLB / action export | No |
