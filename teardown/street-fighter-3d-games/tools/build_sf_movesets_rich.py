#!/usr/bin/env python3
"""SF EX+α / EX2 Plus movelists -> Tekken-style WH movesets (schema v2).

Akuma-in-T7 pattern: SF move data (names, motions) kept verbatim; inputs
translated into WH Tekken notation (1=LP, 2=MP, 1+2=HP, 3=LK, 4=MK, 3+4=HK;
motions qcf/dp/qcb/hcb/charge/360/720 preserved literally).

Provenance per move:
  sf_move   - name verbatim from source
  sf_input  - original SF command verbatim from source
  sf_source - "binary:SLUS_005.48" (verbatim strings from the game executable,
              165-move list in teardown/street-fighter-ex-plus-alpha/.../move-names.txt)
              or "guide:<name>" (period game guides for inputs)
Frame data: ESTIMATED from archetype (marked per schema honesty rule) —
            real OVL move-data decode is open work (see TEARDOWN.md 2c).
anim_ref: Tekken-bank proxies until SF animation data is decoded from
          PL/*.PAC (see sf-teardown-pull PR 1 docs).

Sources:
  binary   = SLUS_005.48 verbatim name table (teardown docs)
  dlh      = dlh.net Street Fighter EX Plus Alpha move guide (Kao_Megura data set)
  megura   = Kao_Megura GameFAQs EX+α Move List & Guide (faqs/4203)
  scwiki   = SuperCombo Wiki "Street Fighter EX2 Plus" character pages
  25th     = 25th Anniversary Collector Set movelist (chaosdemon, GameFAQs)
  capcom   = Capcom Fighting Collection 2 movelist (TBO, GameFAQs)
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'game', 'assets', 'movesets')

SF_BUTTON_MAP = ("1=LP, 2=MP, 1+2=HP, 3=LK, 4=MK, 3+4=HK; "
                 "3P(all punches)=1+2, 3K(all kicks)=3+4; "
                 "motions preserved: qcf/dp/qcb/hcb/charge/360/720; "
                 "Akuma-in-T7 pattern")

FRAME_NOTE = ("frame data estimated from archetype; SF move names/commands verified "
              "(see sf_source); real frame data pending OVL decode (TEARDOWN.md 2c)")

def M(name, inp, sf_move, sf_input, cat, game, source, anim,
      startup=0.183, active=0.033, recovery=0.45, damage=12, limb='armR',
      heavy=False, knock=2.2, move_class='special', slots=None, note=None, throw=False):
    return {"name": name, "input": inp, "sf_move": sf_move, "sf_input": sf_input,
            "sf_category": cat, "sf_game": game, "sf_source": source,
            "startup": startup, "active": active, "recovery": recovery,
            "damage": damage, "limb": limb, "heavy": heavy, "knock": knock,
            "soulGain": 8, "anim_ref": anim, "input_slots": slots or [inp],
            "move_class": move_class,
            "note": note or FRAME_NOTE}

def normals(fighter_id, tag, base_anim, proxy_moves):
    """Standard 18 normals: standing/crouching/jumping x LP/MP/HP/LK/MK/HK."""
    spec = [
        ('Standing Jab (LP)', '1', 'armL', 0.167, 0.033, 0.35, 5, False),
        ('Standing Strong (MP)', '2', 'armR', 0.183, 0.033, 0.40, 8, False),
        ('Standing Fierce (HP)', '1+2', 'armR', 0.200, 0.05, 0.45, 12, True),
        ('Standing Short (LK)', '3', 'legL', 0.183, 0.033, 0.40, 6, False),
        ('Standing Forward (MK)', '4', 'legR', 0.200, 0.05, 0.45, 9, False),
        ('Standing Roundhouse (HK)', '3+4', 'legR', 0.217, 0.05, 0.50, 13, True),
        ('Crouching Jab', 'd/f+1', 'armL', 0.167, 0.033, 0.33, 5, False),
        ('Crouching Strong', 'd/f+2', 'armR', 0.183, 0.033, 0.40, 8, False),
        ('Crouching Fierce', 'd/f+1+2', 'armR', 0.217, 0.05, 0.50, 13, True),
        ('Crouching Short', 'd/f+3', 'legL', 0.167, 0.033, 0.33, 6, False),
        ('Crouching Forward', 'd/f+4', 'legR', 0.183, 0.05, 0.42, 9, False),
        ('Crouching Roundhouse', 'd/f+3+4', 'legR', 0.217, 0.05, 0.53, 14, True),
        ('Jumping Jab', 'u+1', 'armL', 0.15, 0.067, 0.30, 5, False),
        ('Jumping Strong', 'u+2', 'armR', 0.167, 0.067, 0.33, 8, False),
        ('Jumping Fierce', 'u+1+2', 'armR', 0.183, 0.067, 0.38, 12, True),
        ('Jumping Short', 'u+3', 'legL', 0.15, 0.067, 0.30, 6, False),
        ('Jumping Forward', 'u+4', 'legR', 0.167, 0.067, 0.35, 9, False),
        ('Jumping Roundhouse', 'u+3+4', 'legR', 0.183, 0.067, 0.40, 13, True),
    ]
    d = {}
    for i, (nm, inp, limb, st, ac, rc, dmg, hv) in enumerate(spec):
        key = inp if inp not in d else f"{inp}-{i}"
        d[key] = M(f"{tag} {nm}", inp, nm, "standard 6-button", "normal",
                   "sfex+alpha", "guide:canon-6-button-layout", base_anim,
                   startup=st, active=ac, recovery=rc, damage=dmg, limb=limb,
                   heavy=hv, knock=2.0, move_class='strike')
    return d

DATA = {}

# ---------------------------------------------------------------- RYU
ryu = normals('sf-ryu', 'RYU', 't3:jin', None)
ryu.update({
 'f+4': M("RYU Senpu Kyaku (overhead)", "f+4", "Sempu-Kyaku", "f + MK",
          "command-normal", "sfex+alpha", "binary:SLUS_005.48 / guide:dlh",
          "t3:jin", startup=0.217, active=0.05, recovery=0.47, damage=10, limb='legR', heavy=True, knock=2.8),
 'qcf+1+2': M("RYU Hado Ken (fireball)", "qcf+1+2", "Hado-Ken", "qcf + P",
              "special", "sfex+alpha", "binary:SLUS_005.48 / guide:dlh", "t3:jin",
              startup=0.217, active=0.067, recovery=0.60, damage=12, limb='armR', heavy=False, knock=2.6),
 'f,d,df+1+2': M("RYU Sho Ryu Ken (DP)", "f,d,df+1+2", "Shoryu-Ken", "f,d,df + P",
                 "special", "sfex+alpha", "binary:SLUS_005.48 / guide:dlh", "t3:jin",
                 startup=0.067, active=0.117, recovery=0.60, damage=16, limb='armR', heavy=True, knock=4.0),
 'qcb+3+4': M("RYU Tatsumaki Senpu Kyaku (hurricane)", "qcb+3+4", "Tatsumaki-Sempu-Kyaku", "qcb + K (x3)",
              "special", "sfex+alpha", "binary:SLUS_005.48 / guide:dlh", "t3:jin",
              startup=0.167, active=0.217, recovery=0.50, damage=14, limb='legR', heavy=True, knock=3.2),
 'u,qcb+3+4': M("RYU air Tatsumaki Senpu Kyaku", "u,qcb+3+4", "Tatsumaki-Sempu-Kyaku", "qcb + K (air)",
                "special", "sfex+alpha", "guide:dlh", "t3:jin",
                startup=0.167, active=0.217, recovery=0.40, damage=12, limb='legR', heavy=True, knock=3.0),
 'qcf,qcf+1+2': M("RYU Shinku Hado Ken (Lv1+)", "qcf,qcf+1+2", "Shinku-Hado-Ken", "qcf,qcf + P",
                  "super", "sfex+alpha", "binary:SLUS_005.48 / guide:dlh", "t3:jin",
                  startup=0.183, active=0.167, recovery=0.72, damage=24, limb='armR', heavy=True, knock=4.5),
 'qcb,qcb+3+4': M("RYU Shinku Tatsumaki Senpu Kyaku (Lv1+)", "qcb,qcb+3+4", "Shinku-Tatsumaki", "qcb,qcb + K",
                   "super", "sfex+alpha", "binary:SLUS_005.48 / guide:dlh", "t3:jin",
                   startup=0.217, active=0.283, recovery=0.65, damage=26, limb='legR', heavy=True, knock=5.0),
 'qcf,qcf+3+4': M("RYU Shin Sho Ryu Ken (Lv3) [EX2+]", "qcf,qcf+3+4", "Shin Sho Ryu Ken", "qcf,qcf + KKK",
                  "super", "sfex2plus", "guide:scwiki", "t3:jin",
                  startup=0.100, active=0.400, recovery=0.72, damage=34, limb='armR', heavy=True, knock=6.0),
 'qcb+1+2': M("RYU Fire Hado Ken (Lv) [EX2+]", "qcb+1+2", "Fire Hadou Ken", "qcb + P (hits twice)",
             "special", "sfex2plus", "guide:scwiki", "t3:jin",
             startup=0.217, active=0.067, recovery=0.60, damage=15, limb='armR', heavy=True, knock=3.0),
})
DATA['sf-ryu'] = ("RYU (SF EX)", "Ryu (SF)", "jin", ryu,
    "SFEX+alpha + EX2 Plus move data. Binary-verbatim special names; guide inputs. "
    "Shin Sho Ryu Ken / Fire Hado Ken flagged EX2+ (not in the EX+alpha binary list).")

# ---------------------------------------------------------------- KEN
ken = normals('sf-ken', 'KEN', 't3:jin', None)
ken.update({
 'qcf+1+2': M("KEN Hadou Ken", "qcf+1+2", "Hado-Ken", "qcf + P",
              "special", "sfex2plus", "guide:scwiki", "t3:jin",
              startup=0.217, active=0.067, recovery=0.60, damage=12, limb='armR', knock=2.6),
 'f,d,df+1+2': M("KEN Sho Ryu Ken (DP)", "f,d,df+1+2", "Shoryu-Ken", "f,d,df + P",
                 "special", "sfex2plus", "guide:scwiki", "t3:jin",
                 startup=0.067, active=0.117, recovery=0.60, damage=16, limb='armR', heavy=True, knock=4.0),
 'qcb+3+4': M("KEN Tatsumaki Senpu Kyaku", "qcb+3+4", "Tatsumaki-Sempu-Kyaku", "qcb + K",
              "special", "sfex2plus", "guide:scwiki", "t3:jin",
              startup=0.167, active=0.217, recovery=0.50, damage=14, limb='legR', heavy=True, knock=3.2),
 'qcb+1+2': M("KEN Roll (Zenpo Tenshin)", "qcb+1+2", "Zenpo-Tenshin", "qcb + P",
              "special", "sfex2plus", "guide:scwiki / binary:SLUS_005.48", "t3:jin",
              startup=0.10, active=0.40, recovery=0.35, damage=0, limb='armR', knock=0.0, move_class='special',
              note=FRAME_NOTE + "; evasion roll, no damage"),
 'qcf,qcf+1+2': M("KEN Sho Ryu Reppa (Lv1+)", "qcf,qcf+1+2", "Shoryu-Reppa", "qcf,qcf + P",
                  "super", "sfex2plus", "binary:SLUS_005.48 / guide:scwiki", "t3:jin",
                  startup=0.100, active=0.333, recovery=0.72, damage=26, limb='armR', heavy=True, knock=5.0),
 'qcf,qcf+3+4': M("KEN Shin Ryu Ken (Lv2+)", "qcf,qcf+3+4", "Shinryu-Ken", "qcf,qcf + K",
                   "super", "sfex2plus", "binary:SLUS_005.48 / guide:scwiki", "t3:jin",
                   startup=0.133, active=0.400, recovery=0.72, damage=30, limb='armR', heavy=True, knock=5.5),
 'qcb,qcb+3+4': M("KEN Shippu Jinrai Kyaku (Lv3)", "qcb,qcb+3+4", "Shippu Jinrai Kyaku", "qcb,qcb + K",
                   "super", "sfex2plus", "guide:scwiki", "t3:jin",
                   startup=0.150, active=0.450, recovery=0.72, damage=32, limb='legR', heavy=True, knock=5.5),
})
DATA['sf-ken'] = ("KEN (SF EX)", "Ken (SF)", "jin", ken,
    "SFEX2 Plus move data (guide:scwiki). EX+alpha binary holds Shoryu-Reppa/Shinryu-Ken/"
    "Zenpo-Tenshin strings; roll inputs follow the EX2 FAQ.")

# ---------------------------------------------------------------- AKUMA
akuma = normals('sf-akuma', 'AKUMA', 't3:heihachi', None)
akuma.update({
 'f+2': M("AKUMA Senpu Kyaku (overhead)", "f+2", "Senpu Kyaku", "f + MP",
          "command-normal", "sfex+alpha", "guide:dlh", "t3:heihachi",
          startup=0.200, active=0.05, recovery=0.45, damage=9, limb='legR', knock=2.6),
 'u,d+4': M("AKUMA Tenma Kujinkyaku (air d+MK)", "u,d+4", "Tenma-Kujinkyaku", "Jump, d + MK",
            "command-normal", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
            startup=0.150, active=0.083, recovery=0.30, damage=11, limb='legR', heavy=True, knock=3.0),
 'qcb+1+2': M("AKUMA Zenpo Tenshin (roll)", "qcb+1+2", "Zenpo-Tenshin", "qcb + P",
              "special", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
              startup=0.10, active=0.40, recovery=0.35, damage=0, limb='armR', knock=0.0,
              note=FRAME_NOTE + "; evasion roll, no damage"),
 'f,d,df+3+4': M("AKUMA Ashura Sen Ku (forward)", "f,d,df+3+4", "Asyura-Senku(forwards)", "f,d,df + 3P/3K",
                 "special", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
                 startup=0.10, active=0.45, recovery=0.40, damage=0, limb='armR', knock=0.0,
                 note=FRAME_NOTE + "; teleport, no damage"),
 'b,d,db+3+4': M("AKUMA Ashura Sen Ku (backward)", "b,d,db+3+4", "Asyura-Senku(backwards)", "b,d,db + 3P/3K",
                 "special", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
                 startup=0.10, active=0.45, recovery=0.40, damage=0, limb='armR', knock=0.0,
                 note=FRAME_NOTE + "; teleport, no damage"),
 'qcf+1+2': M("AKUMA Go Hado Ken", "qcf+1+2", "Gou-Hado-Ken", "qcf + P",
              "special", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
              startup=0.200, active=0.067, recovery=0.58, damage=14, limb='armR', knock=2.8),
 'f,d,df+1+2': M("AKUMA Go Sho Ryu Ken (DP)", "f,d,df+1+2", "Gou-Shoryu-Ken", "f,d,df + P",
                 "special", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
                 startup=0.067, active=0.117, recovery=0.60, damage=18, limb='armR', heavy=True, knock=4.2),
 'hcb+1+2': M("AKUMA Shakunetsu Hado Ken (red fireball)", "hcb+1+2", "Shakunetsu-Hado-Ken", "hcb + P",
              "special", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
              startup=0.267, active=0.083, recovery=0.65, damage=16, limb='armR', heavy=True, knock=3.2),
 'u,qcf+1+2': M("AKUMA Zanku Hado Ken (air)", "u,qcf+1+2", "Zankuu-Hado-Ken", "Jump, qcf + P",
                "special", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
                startup=0.217, active=0.067, recovery=0.40, damage=13, limb='armR', knock=2.8),
 'qcb+3+4': M("AKUMA Tatsumaki Zanku Kyaku", "qcb+3+4", "Tatsumaki-Zankuu-Kyaku", "qcb + K",
              "special", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
              startup=0.150, active=0.233, recovery=0.50, damage=16, limb='legR', heavy=True, knock=3.4),
 'qcb,qcb+1+2': M("AKUMA Messatsu Go Hado (Lv1+)", "qcb,qcb+1+2", "Messatsu-Gou-Hado", "qcb,qcb + P",
                   "super", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
                   startup=0.167, active=0.167, recovery=0.72, damage=28, limb='armR', heavy=True, knock=4.8),
 'qcf,d,df+1+2': M("AKUMA Messatsu Go Shoryu (Lv1+)", "qcf,d,df+1+2", "Messatsu-Gou-Shoryu", "qcf,d,df + P",
                    "super", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
                    startup=0.083, active=0.350, recovery=0.72, damage=30, limb='armR', heavy=True, knock=5.2),
 'u,qcf,qcf+1+2': M("AKUMA Tenma Go Zanku (air Lv1+)", "u,qcf,qcf+1+2", "Tenma-Gou-Zankuu", "Jump, qcf,qcf + P",
                     "super", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
                     startup=0.183, active=0.133, recovery=0.55, damage=26, limb='armR', heavy=True, knock=4.5),
 '1,1,f,3,2': M("AKUMA Shun Goku Satsu (Lv3)", "1,1,f,3,2", "Shungoku-Satsu", "LP,LP,f,LK,HP",
                "super", "sfex+alpha", "guide:dlh / binary:SLUS_005.48", "t3:heihachi",
                startup=0.167, active=0.500, recovery=0.83, damage=40, limb='armR', heavy=True, knock=6.5,
                move_class='throw', note=FRAME_NOTE + "; instant command grab, Lv3 required"),
})
DATA['sf-akuma'] = ("AKUMA (SF EX)", "Akuma (SF)", "heihachi", akuma,
    "SFEX+alpha move data: 12 named specials/supers verified BOTH in the SLUS_005.48 binary "
    "verbatim list and the dlh EX+alpha guide. Akuma-in-T7 pattern reference implementation.")

# ---------------------------------------------------------------- ZANGIEF
gief = normals('sf-zangief', 'ZANGIEF', 't3:king', None)
gief.update({
 '1+3': M("ZANGIEF Iron Claw (throw)", "1+3", "Iron Claw", "When close, b/f + MP/HP",
          "throw", "sfex+alpha", "guide:megura", "t3:king",
          startup=0.167, recovery=0.50, damage=14, limb='armR', heavy=True, knock=3.5, move_class='throw'),
 '2+4': M("ZANGIEF German Suplex (throw)", "2+4", "German Suplex", "When close, b/f + MK/HK",
          "throw", "sfex+alpha", "guide:megura", "t3:king",
          startup=0.167, recovery=0.52, damage=15, limb='armR', heavy=True, knock=3.8, move_class='throw'),
 '3+4-back': M("ZANGIEF Stomach Block (behind throw)", "3+4", "Stomach Block", "When close, b/f + MK/HK from behind",
               "throw", "sfex+alpha", "guide:megura / binary:SLUS_005.48", "t3:king",
               startup=0.167, recovery=0.50, damage=16, limb='armR', heavy=True, knock=4.0, move_class='throw'),
 '1+2': M("ZANGIEF Double Lariat", "1+2", "Double Lariat", "PPP",
          "special", "sfex+alpha", "guide:megura / binary:SLUS_005.48", "t3:king",
          startup=0.150, active=0.233, recovery=0.50, damage=16, limb='armR', heavy=True, knock=3.5),
 '3+4': M("ZANGIEF Quick Double Lariat", "3+4", "Quick Double Lariat", "KKK",
          "special", "sfex+alpha", "guide:megura / binary:SLUS_005.48", "t3:king",
          startup=0.133, active=0.200, recovery=0.47, damage=15, limb='legR', heavy=True, knock=3.2),
 '360+2': M("ZANGIEF Spinning Piledriver (throw)", "360+2", "Spinning Pile Driver", "When close, rotate 360 + P",
            "special", "sfex+alpha", "guide:megura / binary:SLUS_005.48", "t3:king",
            startup=0.033, recovery=0.55, damage=22, limb='armR', heavy=True, knock=5.0, move_class='throw'),
 '360+4': M("ZANGIEF Russian Suplex (throw)", "360+4", "Russian Suplex", "Rotate 360 + K",
            "special", "sfex+alpha", "guide:megura / binary:SLUS_005.48", "t3:king",
            startup=0.050, recovery=0.55, damage=20, limb='armR', heavy=True, knock=4.8, move_class='throw'),
 'u,d+1+2': M("ZANGIEF Flying Body Attack (air d+HP)", "u,d+1+2", "Flying Body Attack", "In air, d + HP",
              "command-normal", "sfex+alpha", "guide:megura / binary:SLUS_005.48", "t3:king",
              startup=0.150, active=0.100, recovery=0.35, damage=13, limb='armR', heavy=True, knock=3.2),
 'qcf,qcf+3+4': M("ZANGIEF Super Stomping (Lv1+)", "qcf,qcf+3+4", "Super Stomping", "qcf,qcf + K",
                   "super", "sfex+alpha", "guide:megura / binary:SLUS_005.48", "t3:king",
                   startup=0.183, active=0.167, recovery=0.60, damage=22, limb='legR', heavy=True, knock=4.5),
 'qcb+4': M("ZANGIEF Chuudan (during Super Stomping)", "qcb+4", "Chuudan", "qcb + K during Super Stomping",
            "super", "sfex+alpha", "guide:megura", "t3:king",
            startup=0.117, active=0.067, recovery=0.40, damage=10, limb='legR', knock=2.8),
 '720+2': M("ZANGIEF Final Atomic Buster (throw, Lv1+)", "720+2", "Final Atomic Buster", "When close, rotate 720 + P",
            "super", "sfex+alpha", "guide:megura / binary:SLUS_005.48", "t3:king",
            startup=0.033, recovery=0.70, damage=30, limb='armR', heavy=True, knock=6.0, move_class='throw'),
 '720+1+2': M("ZANGIEF Final Atomic Buster Lv3 (throw)", "720+1+2", "Final Atomic Buster Lv3", "When close, rotate 720 + PPP at Level 3",
              "super", "sfex+alpha", "guide:megura / binary:SLUS_005.48", "t3:king",
              startup=0.033, recovery=0.75, damage=38, limb='armR', heavy=True, knock=7.0, move_class='throw'),
 'qcb,qcb+3+4': M("ZANGIEF Aerial Russian Slam (Lv1+) [EX2+]", "qcb,qcb+3+4", "Aerial Russian Slam", "qcb,qcb + K",
                   "super", "sfex2plus", "guide:scwiki", "t3:king",
                   startup=0.150, active=0.183, recovery=0.65, damage=24, limb='armR', heavy=True, knock=5.0, move_class='throw'),
})
DATA['sf-zangief'] = ("ZANGIEF (SF EX)", "Zangief (SF)", "king", gief,
    "SFEX+alpha move data: 8 specials/supers verified in the SLUS_005.48 binary verbatim list; "
    "inputs from the Kao_Megura EX+alpha guide. Aerial Russian Slam flagged EX2+.")

# ---------------------------------------------------------------- BLANKA
blanka = normals('sf-blanka', 'BLANKA', 't3:bryan', None)
blanka.update({
 'd/f+1+2': M("BLANKA Amazon River Run (slide)", "d/f+1+2", "Amazon River Run", "df + HP",
              "command-normal", "sfex2plus", "guide:scwiki", "t3:bryan",
              startup=0.217, active=0.067, recovery=0.50, damage=11, limb='armR', knock=2.6),
 'f+2': M("BLANKA Rock Crush", "f+2", "Rock Crush", "f + MP",
          "command-normal", "sfex2plus", "guide:scwiki", "t3:bryan",
          startup=0.183, active=0.05, recovery=0.42, damage=9, limb='armR', knock=2.4),
 '1+3': M("BLANKA Wild Fang (throw)", "1+3", "Wild Fang", "When close, b/f + HP",
          "throw", "sfex2plus", "guide:scwiki", "t3:bryan",
          startup=0.167, recovery=0.50, damage=14, limb='armR', heavy=True, knock=3.5, move_class='throw'),
 'mash+1': M("BLANKA Electric Thunder (mash P)", "mash+1", "Electric Thunder", "Tap P rapidly",
             "special", "sfex+alpha", "guide:scwiki / guide:25th", "t3:bryan",
             startup=0.117, active=0.217, recovery=0.45, damage=18, limb='armR', heavy=True, knock=3.0),
 'd,u+3+4': M("BLANKA Vertical Rolling (charge)", "d,u+3+4", "Vertical Rolling", "Charge d,u + K",
              "special", "sfex+alpha", "guide:scwiki / guide:25th", "t3:bryan",
              startup=0.117, active=0.117, recovery=0.55, damage=16, limb='legR', heavy=True, knock=4.0,
              note=FRAME_NOTE + "; charge: hold d, then u+K"),
 'b,f+1+2': M("BLANKA Rolling Attack (charge)", "b,f+1+2", "Rolling Attack", "Charge b,f + P",
              "special", "sfex+alpha", "guide:scwiki / guide:25th", "t3:bryan",
              startup=0.117, active=0.117, recovery=0.55, damage=16, limb='armR', heavy=True, knock=4.2,
              note=FRAME_NOTE + "; charge: hold b, then f+P"),
 'b,f+3+4': M("BLANKA Backstep Rolling (charge)", "b,f+3+4", "Backstep Rolling", "Charge b,f + K (press P to abort)",
              "special", "sfex+alpha", "guide:scwiki / guide:25th", "t3:bryan",
              startup=0.150, active=0.133, recovery=0.55, damage=14, limb='legR', heavy=True, knock=3.8,
              note=FRAME_NOTE + "; charge: hold b, then f+K"),
 'f+3+4': M("BLANKA Surprise Forward (hop)", "f+3+4", "Surprise Forward", "Press KKK (f+KKK)",
            "special", "sfex2plus", "guide:scwiki", "t3:bryan",
            startup=0.10, active=0.25, recovery=0.30, damage=0, limb='legR', knock=0.0,
            note=FRAME_NOTE + "; evasive hop, no damage"),
 'b+3+4': M("BLANKA Surprise Back (hop)", "b+3+4", "Surprise Back", "Press ub~db + KKK",
            "special", "sfex2plus", "guide:scwiki", "t3:bryan",
            startup=0.10, active=0.25, recovery=0.30, damage=0, limb='legR', knock=0.0,
            note=FRAME_NOTE + "; evasive hop, no damage"),
 'b,f,b,f+1+2': M("BLANKA Ground Shave Rolling (Lv1+)", "b,f,b,f+1+2", "Ground Shave Rolling", "Charge b,f,b,f + P",
                   "super", "sfex+alpha", "guide:scwiki / guide:25th", "t3:bryan",
                   startup=0.100, active=0.283, recovery=0.65, damage=26, limb='armR', heavy=True, knock=5.0,
                   note=FRAME_NOTE + "; hold P after landing to delay roll"),
 'db,df,db,uf+1+2': M("BLANKA Shout of Earth (Lv1+) [EX+alpha]", "db,df,db,uf+1+2", "Shout of Earth",
                      "Charge db,df,db,uf + P", "super", "sfex+alpha", "guide:25th-era canon",
                      "t3:bryan", startup=0.150, active=0.333, recovery=0.70, damage=28, limb='armR', heavy=True, knock=5.5,
                      note=FRAME_NOTE + "; EX+alpha-era super per period movelists"),
 'b,f,b,f+3+4': M("BLANKA Jungle Beat (Lv1+) [EX2+]", "b,f,b,f+3+4", "Jungle Beat", "Charge b,f,b,f + K",
                   "super", "sfex2plus", "guide:scwiki", "t3:bryan",
                   startup=0.117, active=0.267, recovery=0.65, damage=26, limb='legR', heavy=True, knock=5.0),
 'u,qcf,qcf+1+2': M("BLANKA Beast Hurricane (air Lv1+) [EX2+]", "u,qcf,qcf+1+2", "Beast Hurricane", "In air, qcf,qcf + P",
                     "super", "sfex2plus", "guide:scwiki", "t3:bryan",
                     startup=0.167, active=0.283, recovery=0.55, damage=27, limb='armR', heavy=True, knock=5.2),
 'qcf,qcf+3+4': M("BLANKA Super Electric Thunder (Meteor, Lv3) [EX2+]", "qcf,qcf+3+4", "Super Electric Thunder",
                  "qcf,qcf + KKK", "meteor", "sfex2plus", "guide:scwiki", "t3:bryan",
                  startup=0.083, active=0.450, recovery=0.75, damage=38, limb='armR', heavy=True, knock=6.5),
})
DATA['sf-blanka'] = ("BLANKA (SF EX)", "Blanka (SF)", "bryan", blanka,
    "SFEX move data: EX+alpha specials from period guides; EX2 Plus supers/meteor from "
    "SuperCombo Wiki verbatim. EX2+ entries flagged. EX+alpha-era Shout of Earth kept.")

# ---------------------------------------------------------------- VEGA (claw)
vega = normals('sf-vega', 'VEGA', 't3:xiaoyu', None)
vega.update({
 'd/f+4': M("VEGA Piece of Mercury", "d/f+4", "Piece of Mercury", "df + MK",
            "command-normal", "sfex2plus", "guide:capcom-era canon", "t3:xiaoyu",
            startup=0.200, active=0.05, recovery=0.45, damage=9, limb='legR', knock=2.6),
 'd/f+3+4': M("VEGA Cosmic Heel", "d/f+3+4", "Cosmic Heel", "df + HK",
              "command-normal", "sfex2plus", "guide:capcom-era canon", "t3:xiaoyu",
              startup=0.233, active=0.05, recovery=0.50, damage=13, limb='legR', heavy=True, knock=3.0),
 '1+3': M("VEGA Rainbow Suplex (throw)", "1+3", "Rainbow Suplex", "f/n + LP+LK",
          "throw", "sfex+alpha", "guide:scwiki-era canon", "t3:xiaoyu",
          startup=0.167, recovery=0.50, damage=13, limb='armR', heavy=True, knock=3.5, move_class='throw'),
 '2+4': M("VEGA Crescent Line (back throw)", "2+4", "Crescent Line", "b + LP+LK",
          "throw", "sfex+alpha", "guide:scwiki-era canon", "t3:xiaoyu",
          startup=0.167, recovery=0.50, damage=14, limb='armR', heavy=True, knock=3.6, move_class='throw'),
 'u,1+3': M("VEGA Stardust Drop (air throw)", "u,1+3", "Stardust Drop", "In air, LP+LK",
            "throw", "sfex+alpha", "guide:scwiki-era canon", "t3:xiaoyu",
            startup=0.117, recovery=0.40, damage=15, limb='armR', heavy=True, knock=4.0, move_class='throw'),
 '1+2': M("VEGA Back Slash (flip)", "1+2", "Back Slash", "3P",
          "special", "sfex+alpha", "guide:capcom", "t3:xiaoyu",
          startup=0.10, active=0.30, recovery=0.30, damage=0, limb='armR', knock=0.0,
          note=FRAME_NOTE + "; invulnerable back flip, no damage"),
 '3+4': M("VEGA Short Back Slash (flip)", "3+4", "Short Back Slash", "3K",
          "special", "sfex+alpha", "guide:capcom", "t3:xiaoyu",
          startup=0.10, active=0.25, recovery=0.28, damage=0, limb='legR', knock=0.0,
          note=FRAME_NOTE + "; short invulnerable back flip, no damage"),
 'b,f+1+2': M("VEGA Rolling Crystal Flash (charge)", "b,f+1+2", "Rolling Crystal Flash", "Charge b,f + P",
              "special", "sfex+alpha", "guide:capcom", "t3:xiaoyu",
              startup=0.133, active=0.200, recovery=0.50, damage=15, limb='armR', heavy=True, knock=3.2,
              note=FRAME_NOTE + "; charge: hold b, then f+P; ends with claw uppercut"),
 'd,u+1+2': M("VEGA Sky High Claw (charge)", "d,u+1+2", "Sky High Claw", "Charge d,u + P",
              "special", "sfex+alpha", "guide:capcom", "t3:xiaoyu",
              startup=0.150, active=0.133, recovery=0.55, damage=16, limb='armR', heavy=True, knock=4.0,
              note=FRAME_NOTE + "; charge: hold d, then u+P; wall rebound, claw first"),
 'd,u+3+4': M("VEGA Flying Barcelona Attack (charge)", "d,u+3+4", "Flying Barcelona Attack", "Charge d,u + K, then P",
              "special", "sfex+alpha", "guide:capcom", "t3:xiaoyu",
              startup=0.150, active=0.200, recovery=0.55, damage=17, limb='armR', heavy=True, knock=4.2,
              note=FRAME_NOTE + "; wall leap; follow with Claw Attack (1+2) or Izuna Drop (f+1+2 near)"),
 'f+1+2-air': M("VEGA Izuna Drop (off wall, throw)", "f+1+2", "Izuna Drop", "(after wall leap, near opponent) b/f + P",
                "special", "sfex+alpha", "guide:capcom", "t3:xiaoyu",
                startup=0.050, recovery=0.50, damage=22, limb='armR', heavy=True, knock=5.0, move_class='throw'),
 'd/b,f+3+4': M("VEGA Scarlet Terror (charge) [EX2+]", "d/b,f+3+4", "Scarlet Terror", "Charge db,f + K",
                 "special", "sfex2plus", "guide:capcom", "t3:xiaoyu",
                 startup=0.117, active=0.133, recovery=0.50, damage=15, limb='legR', heavy=True, knock=4.0,
                 note=FRAME_NOTE + "; flip-kick anti-air; added to EX roster in EX2"),
 'db,df,db,uf+3+4': M("VEGA Rolling Izuna Drop (Lv1+)", "db,df,db,uf+3+4", "Rolling Izuna Drop", "Charge db,df,db,uf + K, then P near opp.",
                      "super", "sfex+alpha", "guide:capcom", "t3:xiaoyu",
                      startup=0.100, active=0.250, recovery=0.65, damage=28, limb='armR', heavy=True, knock=5.5,
                      move_class='throw', note=FRAME_NOTE + "; wall dive into command suplex"),
 'b,f,b,f+3+4': M("VEGA Scarlet Mirage (Lv2+) [EX2+]", "b,f,b,f+3+4", "Scarlet Mirage", "Charge b,f,b,f + K",
                   "super", "sfex2plus", "guide:capcom", "t3:xiaoyu",
                   startup=0.133, active=0.283, recovery=0.70, damage=30, limb='legR', heavy=True, knock=5.8),
 'b,f,b,f+1+2': M("VEGA Red Impact (Lv3) [EX2+]", "b,f,b,f+1+2", "Red Impact", "Charge b,f,b,f + P at Level 3",
                   "super", "sfex2plus", "guide:capcom", "t3:xiaoyu",
                   startup=0.117, active=0.300, recovery=0.72, damage=34, limb='armR', heavy=True, knock=6.0),
})
DATA['sf-vega'] = ("VEGA (SF EX)", "Vega (SF)", "xiaoyu", vega,
    "SFEX claw-Vega move data: Capcom Fighting Collection 2 period movelist (TBO) + EX2-era "
    "Scarlet Terror/Scarlet Mirage/Red Impact flagged EX2+. Wall-dive follow-ups chained via notes.")

# ---------------------------------------------------------------- EMIT
os.makedirs(OUT, exist_ok=True)
for fid, (display, tekken_base, t3_source, moves, source_note) in DATA.items():
    doc = {
        "fighter": fid,
        "display": display,
        "tekken_base": tekken_base,
        "t3_source": t3_source,
        "proxy": False,
        "proxy_note": ("Real SF move data (names/commands). anim_ref uses the Tekken-bank proxy "
                       "until SF animations are decoded from PL/*.PAC; frame data estimated from archetype."),
        "schema_version": 2,
        "sf_translation_contract": SF_BUTTON_MAP,
        "sf_move_provenance": source_note,
        "frame_convention": "SFEX 60fps -> seconds; damage scaled SFEX 144HP -> WH 100HP (x0.69)",
        "moves": moves,
    }
    with open(os.path.join(OUT, f"{fid}.json"), "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
    print(f"{fid}: {len(moves)} moves -> {OUT}/{fid}.json")
