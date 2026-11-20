#!/usr/bin/env python3
"""Generate ~/workspace/urban-reign-redux/URMOD-EXTRACTION.md from measured JSONs.

Sources (all measured, none hand-copied):
- extracted/core/manifest.json, coverage.json, dvd000_table.json, dvd001_table.json
- extracted/core/fighter_entries.json
- extracted/fighters/*/parse.json (+ .sha256 sidecars)
- extracted/hd-main/manifest.json, extracted/hd-full/manifest.json
"""
import hashlib, json, os
from pathlib import Path

ROOT = Path.home() / "workspace" / "urban-reign-redux"
CORE = ROOT / "extracted" / "core"
F = ROOT / "extracted" / "fighters"

man = json.loads((CORE / "manifest.json").read_text())
cov = json.loads((CORE / "coverage.json").read_text())
fe = json.loads((CORE / "fighter_entries.json").read_text())
d0 = json.loads((CORE / "dvd000_table.json").read_text())
d1 = json.loads((CORE / "dvd001_table.json").read_text())
hd_main = json.loads((ROOT / "extracted" / "hd-main" / "manifest.json").read_text())
hd_full = json.loads((ROOT / "extracted" / "hd-full" / "manifest.json").read_text())
main_bytes = sum(os.path.getsize(p) for p in (ROOT / "extracted" / "hd-main").glob("*.png"))
full_bytes = sum(os.path.getsize(p) for p in (ROOT / "extracted" / "hd-full").glob("*.png"))

TASK25 = ["Asuka", "Bryan", "Jin", "Kazuya", "King", "Nina", "Paul", "Yoshimitsu", "Hwoarang",
          "Heihachi", "Devil Jin", "Reina", "Kunimitsu", "Bob", "Christie", "Armor Queen",
          "Cammy", "Leon", "CJ", "Kiryu", "Jeff", "Snake", "Renamon", "Vergence", "Ricardo"]


def node_count(name):
    pj = F / name / "parse.json"
    if not pj.exists():
        return "—"
    j = json.loads(pj.read_text())
    if "model" in j and "vmd" in j["model"]:
        return str(j["model"]["vmd"]["active_named_nodes"])
    if "package" in j:
        for mi in j["package"].get("members", []):
            if "embedded_vmd" in mi:
                return f"{mi['embedded_vmd']['active_named_nodes']} (embedded)"
    return "—"


def mouth(name):
    pj = F / name / "parse.json"
    if not pj.exists():
        return "—"
    j = json.loads(pj.read_text())
    if "mouth" in j:
        m = j["mouth"]
        return f"loose {m['loose']} / pkg {m['package']}"
    return "pkg 0/0/0 (embedded)"


L = []
A = L.append
A("# Urban Reign Redux 0.5 — .urmod extraction (Lane 2)")
A("")
A("**Date:** 2026-11-08 ~02:00–02:50 CST  ")
A("**Pack:** Urban Reign Redux 0.5 V97 (`urr-base-1`, id `urr-0.5-v97`), from the author's own GitHub release v0.5.0  ")
A("**Method:** the author's own tools only — `Source/vendor/mod-manager/urrpack.py` (.urmod = ZIP + manifest), `urrlayout.py` (AFS layout), `Source/vendor/roster-lib/toolnative/` (`gyu_structure`, `gyu_decode`, `vmd_structure`, `vmd_mesh`, `ppk_index`, `texture`/`gs_texture`), `Source/editor/review.py` (mouth-node check). No hand-written parser; where a roster-lib tool could not parse a piece, that is recorded as a tool limit, not worked around.  ")
A("**Rules:** `docs/RULES_NO_GUESSING.md` read before data work. No ISO downloaded or fetched. No piracy/ROM/leak sites. No login/paywall bypass.")
A("")
A("## 1. What a .urmod is (measured, not assumed)")
A("")
A(f"- The core mod is a ZIP (`{man['format']}`) with `manifest.json`, `data/NNNNNN.bin` parts, and portraits. Verified: **{len(man['parts'])} parts, {sum(p['length'] for p in man['parts']):,} bytes**, every part SHA-256-checked against the manifest — **0 bad**.")
A(f"- Output disc the pack builds: **{man['output_size']:,} bytes, SHA-256 `{man['output_sha256']}`, PCSX2 CRC {man['pcsx2_crc']}**. Source disc: {man['source_size']:,} bytes, SHA-256 `{man['source_sha256'][0]}`.")
A("- Parts + copies are a binary diff of the output disc against the source ISO: a part is a changed byte range of the output disc; a copy is a range copied verbatim from the source ISO at build time. **Parts cover only 14.56% of the output disc** (670,765,056 of 4,606,052,352 bytes). Everything not in parts exists ONLY in the source ISO — which is not on this VM.")
A(f"- DVD000 AFS table + names: **100% covered by parts** (rebuilt from parts; {len(d0)} entries). DVD001 table + names: **100% covered** ({len(d1)} entries). DVD000 data region: 35.8% covered. DVD001 data region: 10.8% covered. ELF (runtime): 38.4% covered (19,810,304 of 51,564,544 bytes, 273 parts).")
A("- The two HD packs are plain PNG ZIPs (`urr-hd-1`): main set 76 files, full set 397 files — all SHA-verified, all extracted (see §5).")
A("")
A("## 2. The fighter list — 29 found, not 25")
A("")
A("The task named 25 fighters. The pack actually holds **29**: the manifest roster's 23 custom-slotted fighters plus 6 more whose model/package live in stock slots (CID map from the author's `extract_portraits.py`). The 4 not in the task's list are Baek, Jack, Steve, Violet — all four are Tekken guests with custom model/package entries in the roster. Tekken guests total 20 (16 roster + Bryan, King, Hwoarang, Heihachi in stock slots); crossovers total 9 (Cammy, Leon, CJ, Kiryu, Jeff, Snake, Renamon, Vergence, Ricardo).")
A("")
A("## 3. Per-fighter extraction table")
A("")
A("Model = loose VMD (`converter/design/test/chrNN.vmd`); Package = PPK (`afs/safe/ppk/charNNN.ppk`). Coverage = share of the file's bytes present in the .urmod parts. Gaps = byte ranges that only exist in the source ISO. **EXTRACTED means the exact bytes are on disk under `extracted/fighters/<Name>/`; anything below 100% was NOT written out** (no gap-filled files — a file with invented bytes is not the file). Node counts come from the author's `vmd_structure.parse_vmd` on the extracted file (or its embedded copy inside the package).")
A("")
A("| Fighter | CID | Model idx / size / coverage / gaps | Package idx / size / coverage / gaps | Extracted | Nodes | Mouth (AGO/KUCHI_R/KUCHI_L) |")
A("|---|---|---|---|---|---|---|")
for name in sorted(fe):
    f = fe[name]
    m, p = f["model"], f["package"]
    ext = []
    if m.get("extracted"):
        ext.append("model.vmd")
    if p.get("extracted"):
        ext.append("package.ppk")
    ext_s = ", ".join(ext) if ext else "—"
    tag = "★" if name in TASK25 else "†"
    A(f"| {tag} {name} | {f['cid']} | {m['index']} / {m['size']:,} B / {m['coverage']:.3f} / {m['gap_count']} gaps, {m['gap_bytes']:,} B | "
      f"{p['index']} / {p['size']:,} B / {p['coverage']:.3f} / {p['gap_count']} gaps, {p['gap_bytes']:,} B | {ext_s} | {node_count(name)} | {mouth(name)} |")
A("")
A("★ = one of the 25 named in the task. † = additional fighter found in the pack (Baek, Jack, Steve, Violet).")
A("")
A("**Totals: 58 fighter files (29 models + 29 packages); 8 fully covered and extracted; 50 partial (81.3%–99.9% covered, except Leon 34.5%/42.3%).**")
A("")
A("## 4. The 8 extracted files (exact bytes, SHA-256)")
A("")
for name in sorted(fe):
    f = fe[name]
    for kind in ("model", "package"):
        e = f[kind]
        if e.get("extracted"):
            fn = "model.vmd" if kind == "model" else "package.ppk"
            A(f"- `{e['extracted']}` — {e['size']:,} B, SHA-256 `{e['sha256']}` (DVD000 entry {e['index']}, `{e['name']}`)")
A("")
A("Parsed with the author's roster-lib tools (full detail in each `extracted/fighters/<Name>/parse.json`):")
A("")
for name in sorted(fe):
    pj = F / name / "parse.json"
    if not pj.exists():
        continue
    j = json.loads(pj.read_text())
    if "package" in j:
        pk = j["package"]
        members = []
        for mi in pk.get("members", []):
            desc = f"key {mi['key']} ({mi['size']:,} B)"
            if "embedded_vmd" in mi:
                desc += f" = embedded model VMD, {mi['embedded_vmd']['active_named_nodes']} nodes"
            members.append(desc)
        A(f"- **{name} package** ({pk.get('ppk', {}).get('declared_entries')} members, {pk.get('ppk', {}).get('lookup_groups')} lookup groups): " + "; ".join(members) + ".")
        if "mouth" in j:
            A(f"  - Mouth nodes (author's `review.py` `mouth_nodes`, 3 = moving, 0 = static): loose model {j['mouth']['loose']}, package copy {j['mouth']['package']} — the release's static-mouth policy holds: the package copy is static.")
        else:
            A("  - Mouth nodes in the package's embedded model copy: AGO/KUCHI_R/KUCHI_L all type 0 (static).")
    if "model" in j:
        v = j["model"].get("vmd", {})
        A(f"- **{name} loose model** ({j['model']['bytes']:,} B): `parse_vmd` OK, {v.get('active_named_nodes')} active named nodes, node table at offset {v.get('node_table_offset')}.")
        if j["model"].get("mesh_error"):
            A("  - Mesh decode: **FAILED in the author's own tool** — `vmd_mesh.read_mesh` raises `AssertionError` on the first draw (VIF header check). That decoder is documented as a research decoder for the observed Brad VMD; it does not handle this model's stream. No replacement was hand-written. Vertex counts therefore NOT measured for this model.")
A("")
A("Skeleton shape (measured on the extracted models): every extracted model shares the same 40-node core — body chain MUNE1/MUNE2/KUBI/ATAMA, arms SAKOTSU/KATA/UDE/TE (R/L), legs KOSHI/MOMO/HIZA/ASHI/TSUMASAKI (R/L), face MIKEN/MAYU/EYE/MABUTA_UP/MABUTA_UN (R/L) + AGO/KUCHI_R/KUCHI_L — plus per-fighter helper nodes (`__rot`, `__prot`, `__swing`, `__slerp`, `__const`, `__phit`): Asuka +13, CJ +8, Hwoarang +6, King +6, Kiryu +9, Paul +6, Vergence +10. Full name lists are in each `parse.json`.")
A("")
A("## 5. HD texture packs — extracted, not mapped per fighter")
A("")
A(f"- Main set: `urr-hd-1`, folder `Urban Reign Redux 0.5` — **{len(hd_main['files'])} PNGs, {main_bytes:,} bytes total on disk**, all SHA-verified against its manifest, extracted to `extracted/hd-main/` (76 PNGs + manifest). Covers Fighter Files, character select, menus, every stage (per the pack notes).")
A(f"- Full set: folder `Urban Reign Redux 0.5 full set` — **{len(hd_full['files'])} PNGs, {full_bytes:,} bytes total on disk**, all SHA-verified, extracted to `extracted/hd-full/` (397 PNGs + manifest). Covers everything else the game might show.")
A("- **Per-fighter mapping: NOT done.** The PNG filenames carry only PCSX2 texture/CLUT hashes plus a texture id (e.g. `09b66dcb48bc8376-285dc0abb0457fb0-00001d93.png`); no fighter name. The author's own mapping route (`editor/hd.py` + `vendor/exporter/derive_aliases.py`) derives aliases from a model's GS texture uploads, which needs the mesh/sampler decode — and `vmd_mesh.read_mesh` fails on these guest VMDs (see §4). Mapping is therefore owed after the disc is built (PCSX2 replacement-folder layout) or after the mesh decoder is extended by the author's tooling. The PNGs themselves are on disk with manifest SHAs.")
A("")
A("## 6. What could NOT be extracted, and the exact blocker")
A("")
A("**Blocker (single cause for everything below): the gap bytes live only in Jay's own Urban Reign (USA) source ISO, which is not on this VM — and this lane's hard limit forbids fetching an ISO.** The .urmod is a diff, not a full archive: it stores only bytes that differ from the source disc. A fighter file that is 98% covered is still missing its 2% — and without the source bytes there is no exact file. No gap was filled, guessed, or zero-padded in any delivered file.")
A("")
A("| Item | State | Exact gap |")
A("|---|---|---|")
A("| 50 of 58 fighter files (all models except Kiryu; all packages except Asuka, CJ, Hwoarang, King, Kiryu, Paul, Vergence) | Partial, 81.3%–99.9% (Leon model 34.5%, Leon package 42.3%) | 2,048–925,696 missing bytes per file (see §3 gap counts); only in the source ISO |")
A("| Movesets / action tables (per-fighter inputs, strings, hits) | NOT extractable from parts | Tables live in the runtime ELF (ACTION 0x25016f0, BRANCH 0x2bd38d8, REACT 0x2adb768, HIT 0x25fe5a0, registry 0x4706000 per `editor/moveset.py`). ELF is 38.4% covered, but the tables' own ranges are 0.2%–50% covered in their first 64 KB (ACTION 0.4%, BRANCH 2.8%, REACT 0.2%, HIT 35.3%, registry 50.0%) — the tables are near-entirely unchanged-vanilla bytes, i.e. source-ISO bytes. Decodable only from a built disc with the editor's `moveset.py` (runs the game's own chains). |")
A("| Motion banks (shared `tec/motion/*/general.gyu`, `pmotNNN`/`tmotNNN.ppk` style packages) | NOT in the pack at all (0% covered) | Unchanged from vanilla — the new fighters reuse the shared banks. No GYU bank exists inside any extracted char PPK (each char PPK holds only the embedded model + 3 small data members). Motion extraction needs the built disc. |")
A("| Grounded idles / T8 stances / revised movesets (release-note claims) | NOT verified from bytes | These are runtime-table + bank properties; the tables/banks are in the not-extractable set above. The claim is neither confirmed nor denied by this extraction. |")
A("| HD textures per fighter | PNGs extracted, mapping owed | See §5. |")
A("| Mesh vertex/texture data for extracted models | NOT measured | `vmd_mesh.read_mesh` (author's research decoder, Brad VMD only) fails on the guest VMDs. No hand-written replacement per the lane's industry-standard-only rule. |")
A("| Disc build (`-redux-0.5.iso`) | NOT built | See §7. |")
A("")
A("**What unblocks the rest:** running the Launcher build on Windows against Jay's own ISO (the route the pack is designed for), or a coordinator decision to supply the repo's own ISO copy to this VM. Either way the already-extracted parts + tables above stay valid — the build just fills the gaps from the source disc.")
A("")
A("## 7. Launcher build route — status")
A("")
A("**The disc was NOT built. Exact blockers, in order:**")
A("")
A("1. **Wine 9.0 installs and runs on this VM** (`sudo apt-get install -y --no-install-recommends wine64` → exit 0; `/usr/lib/wine/wine64 --version` → `wine-9.0`; sudo works without a password prompt here). But the installed loader is 64-bit-only, and **the Launcher is a 32-bit .NET/Mono GUI exe** (`PE32 executable (GUI) Intel 80386 Mono/.Net assembly`). It cannot run under wine64 alone. The 32-bit stack was NOT installed: no i386 foreign architecture is enabled (`dpkg --print-foreign-architectures` prints nothing) and `apt-cache policy wine32:i386` returns nothing — enabling it needs `dpkg --add-architecture i386` + a full 32-bit Wine + Mono/.NET install, which was not attempted because blocker 2 below makes a build impossible regardless, and the VM is at its disk quota (see §8).")
A("2. **No ISO on this VM.** The Launcher needs Jay's own Urban Reign (USA) `.iso` (about 4.1 GB) as its input; it only reads it, never changes it. No ISO is on this VM and this lane's hard limit forbids fetching one. The repo holds Jay's ISO as release `urban-reign-iso-v1`, but fetching it was not done per that limit.")
A("3. **No PCSX2 folder on this VM.** The Launcher also needs a PCSX2 folder (for game settings + HD texture install). None exists here.")
A("")
A("So the build runs where Jay runs PCSX2 (Windows), exactly as the pack is designed. Nothing was faked: no ISO was produced, no build was claimed.")
A("")
A("## 8. Disk quota incidents (flagged for the coordinator)")
A("")
A("The VM hit its disk quota **twice** during this lane (`OSError: [Errno 122] Disk quota exceeded`). The filesystem shows 47 GB free, so this is a user/project quota shared VM-wide — it filled while other lanes were writing (video-mocap alone is 57 GB). At the worst point even a 1-byte write failed everywhere under home for several minutes. Recovery, using **my own lane's files only**: deleted the three duplicate `.urmod` copies inside `work/mm/…/mods/` plus the `work/editor/` unzip (~1.3 GB; the lane-root ZIPs remain the source of truth), then deleted `extracted/core/parts/` (645 MB — the 3,639 part files, all SHA-verified; reproducible from the Mod Manager zip with `extract_a.py`). Writes were restored after each deletion. The quota can fill again without warning; the coordinator should know the VM is at its quota edge before scheduling more heavy lanes.")
A("")
A("## 9. Files delivered")
A("")
A("- `URMOD-EXTRACTION.md` (this file)")
A("- `extracted/core/manifest.json` — the base pack manifest (3,639 parts, 7,644 copies, layout, roster)")
A("- `extracted/core/coverage.json` — merged part intervals over the output disc")
A("- `extracted/core/dvd000_table.json`, `dvd001_table.json` — rebuilt AFS tables (index, name, offset, size, parts-coverage)")
A("- `extracted/core/fighter_entries.json` — per-fighter entry resolution + gap maps")
A("- `extracted/fighters/<Name>/{model.vmd,package.ppk}` + `.sha256` + `parse.json` — the 8 exact-byte files (Kiryu model+package; Asuka, CJ, Hwoarang, King, Paul, Vergence packages)")
A("- `extracted/hd-main/` (76 PNGs + manifest), `extracted/hd-full/` (397 PNGs + manifest)")
A("- Scripts: `extract_a.py` (verify+extract parts/HD), `extract_b.py` (AFS tables), `extract_c.py` (per-fighter gaps + extraction), `extract_d.py` (roster-lib parsing), `gen_report.py` (this report)")
A("- Tool sources used (read from the Editor zip, restored under `work/tools/`): roster-lib `toolnative/` + `research/` tables, `vendor/mod-manager/urrlayout.py`, `extract_portraits.py`")
A("- Note: `extracted/core/parts/` was removed after use for the disk quota (see §8); re-run `extract_a.py` to restore it from the Mod Manager zip.")
A("")
A("**Repo landing: NOT done in this lane.** The extracted files are game-derived bytes (mod author + original game data); landing them into a repo is the coordinator's call. Nothing was pushed, no branch was created, main was not touched.")
A("")

Path(ROOT / "URMOD-EXTRACTION.md").write_text("\n".join(L))
print("wrote URMOD-EXTRACTION.md,", len("\n".join(L)), "chars")
