# King Model Variants — Index (hunt 2026-10-13)

Every King variant / attire / model piece found across all sources.
Big binaries live on GitHub Release `king-variants-2026-10-13`
(https://github.com/mhvnsnt/western-heart/releases/tag/king-variants-2026-10-13);
small files + READMEs are committed here. Property of Bandai Namco — reverse-engineering
reference for the Western Heart chimera build (steal-like-an-artist playbook).

## DOWNLOADED (have on disk)
| Variant | Source | Location | Format | Poly count |
|---|---|---|---|---|
| T7 King P1 (static T-pose) | rigmodels | `rigmodels/5PMH7G85GYN7P71W3BD1V0249.fbx` (+ preview jpg); full 188MB texture set at `teardown/tekken7/king/` | FBX | 16,683 faces / 11,366 verts (site lists 54,612) |
| T8 King (Base) | DeviantArt (WhiteMageSunny) | Release asset `Tekken 8 - King TK8 Base.7z` | 7z: 5×FBX + TGA | TBD |
| T8 King S2 (Season 2 attire) | DeviantArt (WhiteMageSunny) | Release asset `Tekken 8 - King S2.rar` | RAR: FBX + TGA (107 files) | TBD |
| Beast King (Tekken Revolution alt) | archive.org/tekken-revolution | Release asset `beast-king-tekkenrevolution.zip` | ZIP→RAR (XPS-era rip) | TBD |

## BLOCKED — needs live browser session (parent task)
| Variant | Source | Blocker | Direct page |
|---|---|---|---|
| T7 King animated 16,683 (1 anim) | rigmodels | login + daily export quota; account was server-blocked 2026-10-13 ~01:24 EDT, may have reset | http://rigmodels.com/model.php?view=Tekken_7_King_3d_model__5PMH7G85GYN7P71W3BD1V0249 |
| T8 Armor King (AD-8 Blender port, 638MB) | Open3DLab | server-select click → login redirect | https://open3dlab.com/project/e57bd678-3b73-4203-a6d3-62672cdda4f8/ |
| T6 King 2P XPS | DeviantArt (Pedro-Croft) | DA deviation download needs login (fmmgmars) | https://www.deviantart.com/pedro-croft/art/TEKKEN-6-King-2P-XPS-Download-695250648 |
| T6 Armor King 1P XPS | DeviantArt (Pedro-Croft) | DA login | https://www.deviantart.com/pedro-croft/art/TEKKEN-6-Armor-King-1P-XPS-Download-692199421 |
| T5 King (1p,2p) PS2 rip | DeviantArt (DavidChikardi) | DA login (sta.sh link login-gated) | https://www.deviantart.com/davidchikardi/art/TEKKEN-5-Models-T-Pose-826629341 |
| TTT2 King XPS | DeviantArt (Sticklove/xnalara-customized) | DA login | http://xnalara-customized.deviantart.com/art/King-405245932 |
| SC5 King XPS | DeviantArt (1Vote4Sake) | DA login | https://www.deviantart.com/1vote4sake/art/SC5-King-XPS-1175126889 |
| TK6 King (wrestler) | DeviantArt (wakind) | DA login | https://www.deviantart.com/wakind/art/King%28wrestler%29-TK6-505500316 |
| T8 King (2023 release, FBX) | DeviantArt (WhiteMageSunny) | public Google Drive link truncated on page — needs browser to grab full URL | https://www.deviantart.com/whitemagesunny/art/Tekken-8---King-982092179 |
| T8 Armor King (Battle Cloth) | DeviantArt (WhiteMageSunny) | DA login | https://www.deviantart.com/whitemagesunny/art/Tekken-8---Armor-King-%28Battle-Cloth%29-1348579559 |

## NOT EXTRACTABLE (documented)
| Variant | Source | Why |
|---|---|---|
| T6 PSP King P1/P2/P3/Suit/Beast | Tekken 6 PSP ISO (`game-reverse-engineering/tekken6/tekken6-psp.iso`) | Models locked behind PSP encryption (EBOOT.BIN + DINF_400.BIN/DATA401.IDX); needs PPSSPP decryption → Namco archive RE → GMO extraction (multi-day). |

## NEGATIVE RESULTS (searched 2026-10-13)
- **SFMLab:** no King / Armor King port exists (Jin, Xiaoyu, Julia, Asuka, Kunimitsu, Eliza found, no King).
- **archive.org:** no standalone King model rips beyond tekken-revolution (Beast King, have it).
- **rigmodels:** only ONE "Tekken 7 King" listing (the 54,612 static, have it); other King entries are TTT-era animated low-poly (4,932 / 5,484) + 6,812 / 6,496 variants + Armor King 6,978 (see `rigmodels/README.md`).
- **TekkenMods:** per 2026-10-12 check, only custom/crossover King mods — no official P2/legacy-suit model (P2 built as P1 recolor instead, `roster/pantera/attires/p2/`, PR #10).
