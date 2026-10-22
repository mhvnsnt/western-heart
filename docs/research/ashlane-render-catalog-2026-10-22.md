# Ashlane / Brutalfist Model Render Catalog — 2026-10-22

Render batch for user review: which Ashlane-universe characters become Western Heart fighters
with canon. **No canon writes in this doc — review material only.** The user decides canon after
seeing the renders.

## Render method

- three.js r160 GLTFLoader + Playwright headless Chromium, studio 3-point lighting, neutral
  radial-gradient background, ground shadow. 720x960 PNG.
- Models shown in their **natural pose** (A-pose / bind pose as authored) — no forced T-pose.
- Variant choice: the canonical default per character from the source repo's own roster
  (`brutalfistgrokversiontenpointfive/src/data/bannonGlbRoster.ts` — first-listed / "Default" attire),
  except PABLO which got **two** renders (base + blackreign, per user: blackreign is canon-relevant),
  and SOMBRA_NEGRA which only exists in `AshLane-prototype`.
- Large GLBs stay in the source repos — nothing duplicated into western-heart.

## VF5 mapping status (user decisions 2026-10-22)

**LOCKED (final — no changes without the user's word):**
- BANNON → Jeffry McWild
- EL_TORO_DE_ORO → Wolf Hawkfield (powerhouse with slight aerial)
- PABLO → El Blaze (big/fat powerhouse who TRIES to be aerial; Goldust theatricality + Black Reign/Abyss/Mankind darkness — matches his blackreign variant)
- NPC_FINXSSE → Lei-Fei

**Candidates (annotations only, not decided):**
- MASTER_SENSEI → Lau
- SOMBRA_NEGRA → Kage
- CIPHER → Goh (user note: Goh's moveset was slated for a music-themed fighter, "the emo type one" — Cipher may take that slot; user still thinking)
- AARON_RUBEN → Akira
- CODY → Jacky
- JAGER → Vanessa

**Unmapped:** TRIPLE_XXX, ECHO, HOLLOW, STATIC, STICKUP, ONYX, TYNESHIA, MAIME, EDWIN_KENNEDY,
HALL_NIGHTER, STAN_COMBS, KOBRA, VIPER.

**VF5 women flag:** Sarah, Pai, Aoi, Eileen have no Ashlane counterparts identified yet.
Female-presenting models visible in this batch: **Echo, Maime, Onyx, Tyneshia** — flagged for
the user's review as possible counterparts.

## Technical notes

- **SOMBRA_NEGRA_rigged.glb is damaged** (AshLane-prototype): JOINTS_0 skin indices go up to
  65535 against 58 skeleton joints (~92k vertices affected), and the mesh branch carries a bogus
  0.035 node scale. Rendered as bind-pose T-pose at natural scale for review. **Needs a full
  re-rig before any WH intake** — the skin data is unrecoverable as-is.
- BANNON_rigged.glb needed bone-aware camera framing (skinned geometry bounds were bind-pose).
- Viewer + batch scripts kept at `~/workspace/ashlane-renders/` (site/viewer.html, render.mjs,
  batch.json) for re-renders. Remote-storage links expire 2026-10-24 ~20:30 UTC.

## Renders

| Character | Variant file | Mapping | Render |
|---|---|---|---|
| BANNON | BANNON_rigged.glb | ★LOCKED → Jeffry McWild | https://muse.ai/files/1408826802312537/4489950821277670/qk4x7brbjwzgaq93rnq7e5sz/bannon-20261022-2025.png |
| EL_TORO_DE_ORO | EL_TORO_DE_ORO.glb | ★LOCKED → Wolf Hawkfield | https://muse.ai/files/1408826802312537/2598985037236717/73w2kfacvpnrwohqgbbv5qms/el-toro-de-oro-20261022-2025.png |
| PABLO | PABLO.glb | ★LOCKED → El Blaze | https://muse.ai/files/1408826802312537/1574393368048464/504y2u9l3y6xpjvdxuy5rhp8/pablo-20261022-2025.png |
| PABLO (Blackreign) | PABLO_blackreign.glb | ★LOCKED → El Blaze (dark variant) | https://muse.ai/files/1408826802312537/2048375479162142/bmtmxm4m5h9u0zvw7oqjubz7/pablo-blackreign-20261022-2025.png |
| NPC_FINXSSE | NPC_FINXSSE.glb | ★LOCKED → Lei-Fei | https://muse.ai/files/1408826802312537/1751812365906619/3tkl22yl8at4864qzs0xai2k/finxsse-20261022-2025.png |
| AARON_RUBEN | AARON_RUBEN.glb | candidate → Akira | https://muse.ai/files/1408826802312537/2297884290989210/n2fj84fedn6nv2hdub05akmr/aaron-ruben-20261022-2025.png |
| CIPHER | CIPHER.glb | candidate → Goh (music-themed?) | https://muse.ai/files/1408826802312537/1486502343334994/kz4evnbm6d0mzwzjmsb580h7/cipher-20261022-2025.png |
| CODY | CODY_sober.glb | candidate → Jacky | https://muse.ai/files/1408826802312537/1662913808569278/krs89t4ygn89oysoc38tc8cy/cody-20261022-2025.png |
| JAGER | JAGER.glb | candidate → Vanessa | https://muse.ai/files/1408826802312537/1091462996802417/75veo070nzaff0rojvamg81i/jager-20261022-2025.png |
| MASTER_SENSEI | MASTER_SENSEI.glb | candidate → Lau | https://muse.ai/files/1408826802312537/28488172414215864/76krb5vq5pbqcqdx1zfmobgc/master-sensei-20261022-2025.png |
| SOMBRA_NEGRA | SOMBRA_NEGRA_rigged.glb | candidate → Kage | https://muse.ai/files/1408826802312537/1078238548544546/j3cjl443q2f48noovl7woupx/sombra-negra-20261022-2025.png |
| BRUTUS | BRUTUS.glb | unmapped | https://muse.ai/files/1408826802312537/1757200623072667/gjwp8r00ovsqdneanfkruaev/brutus-20261022-2025.png |
| ECHO | ECHO.glb | unmapped (female-presenting) | https://muse.ai/files/1408826802312537/1623849365578656/pbq3bikgblidmdwh053hhv3n/echo-20261022-2025.png |
| EDWIN_KENNEDY | EDWIN_KENNEDY.glb | unmapped | https://muse.ai/files/1408826802312537/933155306326930/nbr9zhdhcbktcxhkiaadah7a/edwin-kennedy-20261022-2025.png |
| HALL_NIGHTER | HALL_NIGHTER.glb | unmapped | https://muse.ai/files/1408826802312537/1647574173571761/di63vec0u1dnw6txcx5zmqqj/hall-nighter-20261022-2025.png |
| HOLLOW | HOLLOW.glb | unmapped | https://muse.ai/files/1408826802312537/1064135016624422/zjwwnngk0by8ttl3oyid3dvm/hollow-20261022-2025.png |
| KOBRA | KOBRA.glb | unmapped | https://muse.ai/files/1408826802312537/4721442678142505/kdrjeizvq8k1alo9zagmos9u/kobra-20261022-2025.png |
| MAIME | MAIME_skinned.glb | unmapped (female-presenting) | https://muse.ai/files/1408826802312537/1142597925378799/bv94zofvxasetbiq88c09ckg/maime-20261022-2025.png |
| ONYX | ONYX_street.glb | unmapped (female-presenting) | https://muse.ai/files/1408826802312537/1652968499535741/mxjg03tpk7ehu7f86xfmcgsm/onyx-20261022-2025.png |
| STAN_COMBS | STAN_COMBS_gear.glb | unmapped | ⏳ pending upload approval |
| STATIC | STATIC.glb | unmapped | ⏳ pending upload approval |
| STICKUP | STICKUP.glb | unmapped | ⏳ pending upload approval |
| TARZANIAN_DEVIL | TARZANIAN_DEVIL_skinned.glb | unmapped | ⏳ pending upload approval |
| TITAN | TITAN.glb | unmapped | ⏳ pending upload approval |
| TRIPLE_XXX | TRIPLE_XXX.glb | unmapped | ⏳ pending upload approval |
| TYNESHIA | TYNESHIA.glb | unmapped (female-presenting) | ⏳ pending upload approval |
| VIPER | VIPER.glb | unmapped | ⏳ pending upload approval |
| WRECK_PATTERSON | WRECK_PATTERSON.glb | unmapped | ⏳ pending upload approval |

## Visual notes (from the renders)

- BANNON: huge tattooed heavyweight, metal mask, blonde dreads — reads Jeffry McWild instantly.
- EL_TORO_DE_ORO: minotaur luchador, gold/red — natural Wolf Hawkfield powerhouse look.
- PABLO base: big man in ornate matador-ish suit. Blackreign: black/white geometric bodysuit +
  mask — the "disturbed darkness" flavor the user described.
- FINXSSE: lean, shirtless, big cross necklace, jeans — Lei-Fei candidate look TBD by user.
- SOMBRA_NEGRA: white skull-mask face, long black hair, striped top — Kage candidate.
- ECHO: green-haired woman in black bodysuit. MAIME: pale figure in gray sweats. ONYX: green hair,
  striped jacket. TYNESHIA: athletic woman in white/pink.
- MASTER_SENSEI: orange gi (Goku-style) — visual Lau pairing is the user's call.
- JAGER: 4.8 MB model, blond bearded, heavily tattooed.
- TARZANIAN_DEVIL: leopard-print singlet.

## Other variants available (not rendered)

PABLO_goldenbull.glb, plus per-character alts listed in bannonGlbRoster.ts (attires). Re-render
on request — pipeline is reusable: `node render-ashlane.mjs <slug>` in
`~/workspace/proof-w38/pwtest/`.
