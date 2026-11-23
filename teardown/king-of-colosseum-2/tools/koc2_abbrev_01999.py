#!/usr/bin/env python3
"""koc2_abbrev_01999.py — short forms for file 01999 (WrestlerData).

WHY: the KoC2 font is full-width only (see koc2_fullwidth.py), so
01999's fixed-width fields hold HALF as many characters as in
half-width ASCII: family/given 6 chars (12 bytes), nickname/finisher
16 chars (32 bytes). Values over the limit need explicit short forms.

- family/given: truncated to the first 6 chars, EXCEPT the entries
  in NAME_SPECIAL (multi-word names where truncation would cut
  mid-word or leave a trailing space).
- nickname/finisher: hand rewordings in NICK / FIN (truncation would
  cut words in half). Every value is <= its limit — verified by the
  builder at build time.

Keys are the ASCII English strings from work/translations-01999.json
('en' values); lookup happens BEFORE full-width conversion.

KoC2 English lane, 2026-11-20.
"""

LIMITS = {"family": 6, "given": 6, "nickname": 16, "finisher": 16}

NAME_SPECIAL = {
    "family": {
        "Black Master": "MASTER",
        "Tengu Kaiser": "KAISER",
        "Rich Man 2": "RICH 2",
        "Hirai Jr.": "HIRAI",
    },
    "given": {
        "Demon World": "DEMON",
        "Z Shinsuke": "SHINSU",
        "Big Joe": "JOE",
        "The Man": "MAN",
        "Super S": "SUPER",
    },
}

NICK = {
    "Blue-Eyed Fighting Spirit": "BLUE EYED SPIRIT",
    "Brawling Choi Borg": "BRAWLING BORG",
    "Brawling Strong Style": "BRAWLING STYLE",
    "Center Stage Prodigy": "STAGE PRODIGY",
    "Center Stage Rising Star": "RISING STAR",
    "Cheerful Black Cat": "BLACK CAT",
    "Chosen Child of God": "CHILD OF GOD",
    "Conspiracy Nobleman": "PLOT NOBLEMAN",
    "Dark Fierce Tiger": "FIERCE TIGER",
    "Demon World Strong Style": "DEMON STRONG",
    "Demon World's Boss": "DEMON BOSS",
    "Demon World's Dragon": "DEMON DRAGON",
    "Demon World's Great Sword": "DEMON SWORD",
    "Demon World's Kyushu Man": "KYUSHU MAN",
    "Demon World's President": "DEMON PRESIDENT",
    "Demon World's Rampaging Criminal": "DEMON RAMPAGER",
    "Demon World's Rogue": "DEMON ROGUE",
    "Destruction Dragon": "DESTROY DRAGON",
    "Destructive Beast": "DESTRUCT BEAST",
    "Flame Flying Dragon": "FLAME DRAGON",
    "Flying Muay Thai Warrior": "MUAY THAI ACE",
    "Genius Karate Boy": "KARATE GENIUS",
    "Genkai Flying Fish": "FLYING FISH",
    "Hard-Hitting Fighter": "HARD HITTER",
    "Heisei Blond Wolf": "BLOND WOLF",
    "Heisei Scarred Man": "SCARRED MAN",
    "Hell Burial Warrior": "HELL WARRIOR",
    "Hot Wind Flying Beast": "FLYING BEAST",
    "Indomitable Fierce Bull": "FIERCE BULL",
    "Kind-Hearted Rogue": "KIND ROGUE",
    "Kurama Sky Legend": "SKY LEGEND",
    "Ladies' Man Among Men": "LADIES MAN",
    "Leg Technique Magician": "LEG MAGICIAN",
    "Lightning Warrior": "LIGHTNING",
}

NICK.update({
    "Made in Australia": "AUSSIE MADE",
    "Messenger from Death": "DEATH MESSENGER",
    "Midsummer Lion King": "SUMMER LION",
    "NJPW's Secret Weapon": "SECRET WEAPON",
    "NOAH's Heavy Tank": "HEAVY TANK",
    "Natural Born Master": "BORN MASTER",
    "New Century Super Beast": "CENTURY BEAST",
    "North Sea Rising Star": "NORTH SEA STAR",
    "Philadelphia Monkey": "PHILLY MONKEY",
    "Pumpkin Star Warrior": "PUMPKIN STAR",
    "Reformed Delinquent": "EX DELINQUENT",
    "Revolutionary Warrior": "REVOLUTIONARY",
    "Ring's Flying Squirrel": "FLYING SQUIRREL",
    "Ring's Funky Dancer": "FUNKY DANCER",
    "Rising Dragon of Storms": "STORM DRAGON",
    "Roaring Fighting General": "FIGHT GENERAL",
    "Runaway Express Mohamed": "RUNAWAY EXPRESS",
    "Selfless Preacher": "HOLY PREACHER",
    "Silent Fighting Spirit": "SILENT SPIRIT",
    "Silent Man of Action": "SILENT ACTION",
    "Slaughter Green Beret": "GREEN BERET",
    "Soaring Dragon Warrior": "SOARING DRAGON",
    "Steel Pheromone Body": "STEEL BODY",
    "Sun's Child Prodigy": "SUN CHILD",
    "Super Generation Flagbearer": "NEXT GEN LEADER",
    "Super Spicy Tonpachi": "SPICY TONPACHI",
    "Tarnished Silver Technician": "SILVER TECH",
    "Technical Soldier": "TECH SOLDIER",
    "Terrifying Killing Machine": "KILLING MACHINE",
    "Unfinished Great Talent": "GREAT TALENT",
    "WJ's Kamikaze Captain": "KAMIKAZE CAPTAIN",
    "Wind Forest Fire Mountain": "FURIN KAZAN",
    "World's Fierce Eagle": "FIERCE EAGLE",
})

FIN = {
    "Argentine Back Breaker": "ARG BACKBREAKER",
    "Argentine-Style Backbreaker": "ARG BACKBREAKER",
    "Avalanche Gori Thunder": "GORI THUNDER",
    "Body Scissors Choke Sleeper": "SCISSORS SLEEPER",
    "Body Scissors Front Neck Lock": "SCISSORS LOCK",
    "Bullet Rolling Elbow": "ROLLING ELBOW",
    "Canadian Back Breaker": "CANADIAN BREAKER",
    "Chattanooga Choo Choo": "CHOO CHOO",
    "Consecutive Belly to Back": "BELLY TO BACK",
    "Cradle Backdrop Hold": "CRADLE BACKDROP",
    "Crossface of JADO": "JADO CROSSFACE",
    "Death Valley Bomb": "VALLEY BOMB",
    "Demon Windmill Hold": "DEMON WINDMILL",
    "Demon World Windmill Hold": "DEMON WINDMILL",
    "Diving Body Attack": "DIVE BODY ATTACK",
    "Diving Body Press": "DIVING PRESS",
    "Diving Elbow Drop": "DIVE ELBOW DROP",
    "Dragon Suplex Hold": "DRAGON SUPLEX",
    "Dynamite Headbutt": "DYNAMITE HEAD",
    "Everest German Suplex": "EVEREST GERMAN",
    "Figure-Four Leglock": "FIGURE FOUR",
    "Fisherman's Buster": "FISHERMAN BUSTER",
    "Flying Kneel Kick": "FLYING KNEE",
    "Flying Squirrel Press": "SQUIRREL PRESS",
    "German Suplex Hold": "GERMAN SUPLEX",
    "Heavy Bomb Moonsault Press": "MOONSAULT PRESS",
    "High Spinning Kick": "HIGH SPIN KICK",
    "High-Angle Atomic Drop": "ATOMIC DROP",
    "High-Angle Backdrop": "HI BACKDROP",
    "High-Angle Chokeslam": "HI CHOKESLAM",
    "High-Angle German Suplex Hold": "HI GERMAN SUPLEX",
    "High-Angle Throat Drop": "HI THROAT DROP",
    "High-Speed Spinebuster": "HI SPEED BUSTER",
}

FIN.update({
    "Iron Fist Punishment": "IRON FIST",
    "Jumping High Kick": "JUMP HIGH KICK",
    "King Kong Knee Drop": "KONG KNEE DROP",
    "Knee Kick to the Ugly Face": "UGLY FACE KICK",
    "Koppo-Style Shower Kick": "SHOWER KICK",
    "Lightning Leg Lariat": "LEG LARIAT",
    "Locomotion Triple Suplex": "TRIPLE SUPLEX",
    "Mt. Fuji German Suplex Hold": "FUJI GERMAN",
    "Northern Lights Bomb": "N LIGHTS BOMB",
    "Northern Lights Suplex Hold": "N LIGHTS SUPLEX",
    "Olympic Qualifier Slam": "OLYMPIC SLAM",
    "One-Hand Clutch Exploder": "CLUTCH EXPLODER",
    "Pearl Harbor Splash": "HARBOR SPLASH",
    "Reverse Boston Crab": "REV BOSTON CRAB",
    "Reverse Ippon Seoi": "REV IPPON SEOI",
    "Rolling Clutch Hold": "ROLLING CLUTCH",
    "Rounding Body Press": "ROUND BODY PRESS",
    "Running Neckbreaker Drop": "RUN NECKBREAKER",
    "Samurai Powerbomb": "SAMURAI BOMB",
    "Scorpion Deathlock": "SCORPION LOCK",
    "Shower-Down Lariat": "SHOWER LARIAT",
    "Special Meteor Kick": "METEOR KICK",
    "Spinning Frog Splash": "FROG SPLASH",
    "Straight-Down Brainbuster": "STRAIGHT BUSTER",
    "Tornado Cookie Cutter": "TORNADO CUTTER",
    "Turkish Cut Prison Hold": "TURKISH PRISON",
    "Vert. Drop Reverse Brainbuster": "VERT REV BUSTER",
    "Vertical Drop Brainbuster": "VERT DROP BUSTER",
    "Vertical Drop DDT": "VERT DROP DDT",
    "Victor-Style Armbar": "VICTOR ARMBAR",
})


def shorten(field: str, value: str) -> str:
    """Return the in-limit short form for an over-limit 01999 value.

    Raises KeyError if a nickname/finisher has no rewording (fail
    loudly — never silently truncate a phrase mid-word). Names
    truncate to the first LIMIT chars unless in NAME_SPECIAL.
    """
    limit = LIMITS[field]
    if len(value) <= limit:
        return value
    special = NAME_SPECIAL.get(field, {})
    if value in special:
        return special[value]
    if field == "nickname":
        return NICK[value]
    if field == "finisher":
        return FIN[value]
    return value[:limit]


if __name__ == "__main__":
    # Self-check: every override fits its limit.
    bad = []
    for f, d in NAME_SPECIAL.items():
        for k, v in d.items():
            if len(v) > LIMITS[f]:
                bad.append((f, k, v))
    for k, v in NICK.items():
        if len(v) > 16:
            bad.append(("nickname", k, v))
    for k, v in FIN.items():
        if len(v) > 16:
            bad.append(("finisher", k, v))
    print(f"NAME_SPECIAL={sum(len(d) for d in NAME_SPECIAL.values())} "
          f"NICK={len(NICK)} FIN={len(FIN)} over-limit={bad}")
    print("sample:", shorten("family", "Nakanishi"),
          shorten("nickname", "Terrifying Killing Machine"),
          shorten("finisher", "Northern Lights Suplex Hold"))
