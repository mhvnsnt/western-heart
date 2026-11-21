#!/usr/bin/env python3
"""koc2_translate_01999.py — translate KC2FIRE.000 file 01999 (WrestlerData).

441 wrestler records (190 distinct wrestlers, up to 4 costume sets each).
Fixed-width Shift-JIS fields, translated in place (see
koc2_file01999_build.py):
  family   +0x04, 12 bytes  (max 12 ASCII chars)
  given    +0x13, 12 bytes  (max 12 ASCII chars)
  nickname +0x28, 32 bytes  (max 32 ASCII chars)
  finisher +0x49, 32 bytes  (max 32 ASCII chars)
Field limits verified from the raw file: 11 records use the full 12
bytes of family/given with no NUL terminator, so the game reads them
fixed-width; the builder writes text + NUL-pad (12-char values match
the original no-NUL layout).

Sources:
- family/given: koc2_translate_02010.PARTS (romanized roster split)
  + PARTS_ADD below (katakana/foreign names the roster split missed).
- nickname: NICK dict below (183 hand translations — nicknames are
  idiomatic phrases; the 02010 segmenter only covered 13/183).
- finisher: the patched 02008 move translator + FIN_OVERRIDE below.
  NOTE: several finisher strings are TRUNCATED in the game data (the
  32-byte field couldn't hold the full Japanese name, e.g.
  'ノーザンライトスープレックスホー' for '...ホールド'). The English
  is 1 byte/char so the FULL move name fits — FIN_OVERRIDE restores
  the full name; verified against the 02008 move table.

Display order: fields stay semantically correct (family=family,
given=given). The game displays family-first, so match screens read
"Fujinami Tatsumi" (Japanese order) while the 02010 roster lists read
Western order ("Tatsumi Fujinami"). Accepted inconsistency — swapping
fields would mislabel the data.

Usage: python3 tools/koc2_translate_01999.py
Writes work/translations-01999.json + work/translation-review-01999.txt.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import koc2_translate_02010 as T10  # noqa: E402
import koc2_translate_02008 as T08  # noqa: E402
import koc2_translate_02008_patch as P08  # noqa: E402

WORK = os.path.join(HERE, "..", "work")
DATA = os.path.join(HERE, "..", "data")

# Patched 02008 translator (same setup as the patch runner).
T08.TERM.update(P08.TERM_ADD)
T08.WHOLE.update(P08.WHOLE_ADD)
T08.TERM.update(P08.TERM_ADD2)
T08.WHOLE.update(P08.WHOLE_ADD2)
T08.TERM.update(P08.TERM_ADD3)
T08.WHOLE.update(P08.WHOLE_ADD3)
T08.TERM.update(P08.TERM_ADD4)
T08.WHOLE.update(P08.WHOLE_ADD4)
T08._TERM_KEYS = sorted(T08.TERM, key=len, reverse=True)
T08._WHOLE_KEYS = sorted(T08.WHOLE, key=len, reverse=True)
_orig_move = T08.translate_move


def translate_move(ja):
    en = _orig_move(ja)
    if en is None:
        en = _orig_move(ja.translate(P08._FW))
    return en

# Family/given parts the roster split missed (katakana/foreign names,
# trainees, full-width spellings). Western order is NOT applied here —
# these are the parts themselves.
PARTS_ADD = {
    # family (50)
    "ともき": "Tomoki", "アシッド": "Acid", "アダモ": "Adamo",
    "アンダーソン": "Anderson", "ウルフ": "Wolf", "オージー": "Aussie",
    "カシン": "Kashin", "キャット": "Cat",
    "グラジエータ": "Gladiator", "コリノ": "Corino",
    "サムライ": "Samurai", "ジョー": "Joe",
    "スリンガー": "Slinger", "タイガー": "Tiger",
    "テングカイザ": "Tengu Kaiser", "テンタ": "Tenta",
    "ディー・ロウ": "D-Lo", "ノートン": "Norton",
    "ハインズ": "Hines", "ハシフ": "Hashif",
    "ハヤシ": "Hayashi", "ハワード": "Howard",
    "バートン": "Barton", "バーネット": "Burnett",
    "パワー": "Power", "ヒライ": "Hirai",
    "ヒライＪｒ．": "Hirai Jr.", "ヒロ": "Hiro",
    "プレデター": "Predator", "マイティ": "Mighty",
    "マサ": "Masa", "マシン": "Machine", "ムタ": "Muta",
    "ヨネ": "Yone", "ライガー": "Liger",
    "和牛太": "Wagyuta", "太陽": "Taiyo", "孤士": "Koshi",
    "富豪２": "Rich Man 2", "山笠": "Yamagasa",
    "嵐": "Arashi", "練習生": "Trainee", "黒師": "Black Master",
    "１号": "No. 1", "２号": "No. 2", "４号": "No. 4",
    "５号": "No. 5", "Ｌｏｗｋｉ": "Lowki",
    "ＯＴＡＮＩ": "Otani", "ＴＡＮＡＫＡ": "Tanaka",
    # given (45)
    "ウォリアー": "Warrior", "エル": "El", "カズ": "Kazu",
    "カーン": "Khan", "キング": "King",
    "クラッシャー": "Crusher", "グレート": "Great",
    "ケア": "Kea", "ケンドー": "Kendo", "サイトー": "Saito",
    "ザ": "The", "ザ・マン": "The Man", "ジョシュ": "Josh",
    "ジョージ": "George", "スコット": "Scott",
    "スティーブ": "Steve", "スパイク": "Spike",
    "スーパー・ス": "Super S", "トム": "Tom",
    "ビッグ・ジョ": "Big Joe", "ビーフ": "Beef",
    "ブラウン": "Brown", "ブラック": "Black", "ブルー": "Blue",
    "マイク": "Mike", "ミツ": "Mitsu",
    "モハメド": "Mohamed", "ラッシャー": "Rusher",
    "リチャード": "Richard", "ヴァンサック": "Vansack",
    "夢路": "Yumeji", "宏孝": "Hirotaka",
    "愚零斗": "Gureito", "無双": "Muso",
    "獣神サンダー": "Jushin", "順嗣": "Junji",
    "魔界": "Demon World", "黒毛": "Kuroge",
    "３号": "No. 3", "Ｃ・Ｗ": "C.W.", "ＭＡＳＡ": "Masa",
    "Ｍｒ．": "Mr.", "Ｚ”信介": "Z Shinsuke",
}

# Finishers the move translator can't do: truncated in the game data
# (full name restored — verified against the 02008 move table), plus
# names missing from the move table.
FIN_OVERRIDE = {
    # truncated in the 32-byte field (full name restored)
    "エベレストジャーマンスープレック": "Everest German Suplex",
    "ランニングネックブリーカードロッ": "Running Neckbreaker Drop",
    "ロコモーショントリプルスープレッ": "Locomotion Triple Suplex",
    "ワンハンドクラッチ・エクスプロイ": "One-Hand Clutch Exploder",
    "垂直落下式リバースブレーンバスタ":
        "Vert. Drop Reverse Brainbuster",
    "富士山ジャーマンスープレックスホ": "Mt. Fuji German Suplex Hold",
    "ノーザンライトスープレックスホー": "Northern Lights Suplex Hold",
    # not in the 02008 move table
    "アートバープレス": "Art Bar Press",
    "サマーソルトドロップ": "Somersault Drop",
    "スペシャル流星キック": "Special Meteor Kick",
    "ターメリックボンバー": "Turmeric Bomber",
    "フライングソーセージ": "Flying Sausage",
    "ローダウン": "Lowdown",
    "練習生": "Trainee",
    "豪腕走打": "Strong-Arm Rush",
    "連続ベリートゥーバック": "Consecutive Belly to Back",
    "閃光妖術": "Flash Sorcery",
    "雪崩式ゴリ・サンダー": "Avalanche Gori Thunder",
    "高角度ジャーマンスープレックスホ": "High-Angle German Suplex Hold",
    "魔界風車固め": "Demon World Windmill Hold",
    "Ｐ．Ｋ": "P.K.",
}

# Nicknames — 183 hand translations (nicknames are idiomatic phrases;
# the 02010 segmenter only covered 13 of them). All values fit the
# 32-byte field (longest: 29 chars).
NICK = {
    "いぶし銀": "Tarnished Silver",
    "いぶし銀テクニシャン": "Tarnished Silver Technician",
    "ど真ん中の新星": "Center Stage Rising Star",
    "ど真ん中の申し子": "Center Stage Prodigy",
    "ひかえろ王": "King Hold Back",
    "みんなの太陽": "Everyone's Sun",
    "アースクエイク": "Earthquake",
    "エアリアルプレーヤー": "Aerial Player",
    "オレンジクラッシュ": "Orange Crush",
    "オーストラリア産": "Made in Australia",
    "クレイジーモンキー": "Crazy Monkey",
    "グレネードファイター": "Grenade Fighter",
    "ゴールデンレフト": "Golden Left",
    "サモアの島崎": "Samoan Shimazaki",
    "ジェラシーファイター": "Jealousy Fighter",
    "ジュニアのカリスマ": "Junior Charisma",
    "ジュニアの反逆児": "Junior Rebel",
    "ジュニアの巨人": "Junior Giant",
    "ジョイントクラッシャー": "Joint Crusher",
    "スターネス": "Starness",
    "スパイク大好き": "Spike Lover",
    "スパイダー・ＮＩＮＪＹＡ": "Spider NINJYA",
    "スーパーフライ": "Superfly",
    "タフネスハート": "Toughness Heart",
    "ダイナミックＴ": "Dynamic T",
    "テクニカルソルジャー": "Technical Soldier",
    "デンジャラスＫ": "Dangerous K",
    "ドロップキックマスター": "Dropkick Master",
    "ナチュラルボーンマスター": "Natural Born Master",
    "ネバーサレンダー": "Never Surrender",
    "ノアの番人": "NOAH's Guardian",
    "ノアの盟主": "NOAH's Leader",
    "ノアの重戦車": "NOAH's Heavy Tank",
    "ノーフィアー": "No Fear",
    "ハングリーウルフ": "Hungry Wolf",
    "バチバチファイター": "Hard-Hitting Fighter",
    "バーニング": "Burning",
    "パワーモンスター": "Power Monster",
    "ファイヤーソード": "Fire Sword",
    "フィラデルフィアモンキー": "Philadelphia Monkey",
    "フライングタンク": "Flying Tank",
    "マッスルエリート": "Muscle Elite",
    "マッスルボルケーノ": "Muscle Volcano",
    "マッチョドラゴン": "Macho Dragon",
    "ムービースター": "Movie Star",
    "ヤング・パンサー": "Young Panther",
    "リングのファンキーダンサー": "Ring's Funky Dancer",
    "リングのムササビ": "Ring's Flying Squirrel",
    "レヴォリューション": "Revolution",
    "ワイルドハート": "Wild Heart",
    "一匹狼": "Lone Wolf",
    "不屈の猛牛": "Indomitable Fierce Bull",
    "不言実行の実力者": "Silent Man of Action",
    "世界の荒鷲": "World's Fierce Eagle",
    "五輪の星": "Olympic Star",
    "人生バックドロップ": "Life Backdrop",
    "人間魚雷二世": "Human Torpedo II",
    "伝説の巨人": "Legendary Giant",
    "侍ファイター": "Samurai Fighter",
    "全日本的愛": "All Japan Love",
    "力道山ジュニア": "Rikidozan Jr.",
    "北斗の流星": "Hokuto Meteor",
    "北海の新星": "North Sea Rising Star",
    "十字職人": "Cross Craftsman",
    "千両役者": "Star Performer",
    "南海の野獣": "South Seas Beast",
    "南瓜星戦士": "Pumpkin Star Warrior",
    "吠える闘将": "Roaring Fighting General",
    "喧嘩ストロングスタイル": "Brawling Strong Style",
    "喧嘩崔ボーグ": "Brawling Choi Borg",
    "国産": "Homegrown",
    "土曜日の怪人": "Saturday Phantom",
    "地獄葬戦士": "Hell Burial Warrior",
    "天才空手少年": "Genius Karate Boy",
    "太陽の天才児": "Sun's Child Prodigy",
    "孤高の天才": "Solitary Genius",
    "寡黙な重鎮": "Silent Veteran",
    "寡黙な闘志": "Silent Fighting Spirit",
    "平成の生傷男": "Heisei Scarred Man",
    "平成の金髪狼": "Heisei Blond Wolf",
    "弾丸戦士": "Bullet Warrior",
    "彷徨える海賊": "Wandering Pirate",
    "心優しき無頼漢": "Kind-Hearted Rogue",
    "怒りの獣神": "Raging Beast God",
    "怪物": "Monster",
    "恐れ知らずのリーダー": "Fearless Leader",
    "戦慄の殺人マシーン": "Terrifying Killing Machine",
    "新世紀の超獣": "New Century Super Beast",
    "新日本の秘密兵器": "NJPW's Secret Weapon",
    "新日本プロレスのエース": "NJPW Ace",
    "暗黒の猛虎": "Dark Fierce Tiger",
    "暴走特急モハメッド": "Runaway Express Mohamed",
    "更正不良中年": "Reformed Delinquent",
    "未完の大器": "Unfinished Great Talent",
    "東洋の悪魔": "Oriental Devil",
    "格闘モンスター": "Fighting Monster",
    "次代の衝撃": "Next-Gen Impact",
    "死神からの使者": "Messenger from Death",
    "殺戮グリーンベレー": "Slaughter Green Beret",
    "流星番長": "Meteor Boss",
}

NICK.update({
    "湘南の鷹": "Shonan Hawk",
    "激辛トンパチ": "Super Spicy Tonpachi",
    "激辛番長": "Super Spicy Boss",
    "火の玉小僧": "Fireball Kid",
    "炎の刃": "Flame Blade",
    "炎の番人": "Flame Guardian",
    "炎の飛龍": "Flame Flying Dragon",
    "無我の説法家": "Selfless Preacher",
    "熱風飛獣": "Hot Wind Flying Beast",
    "燃える向上心": "Burning Ambition",
    "狂戦士": "Mad Warrior",
    "狂犬": "Mad Dog",
    "狂犬野郎": "Mad Dog Bastard",
    "猛牛": "Fierce Bull",
    "獄門鬼": "Hell Gate Demon",
    "玄海のトビウオ": "Genkai Flying Fish",
    "甲斐の怪力": "Kai's Strongman",
    "男の中の色男": "Ladies' Man Among Men",
    "真夏の獅子王": "Midsummer Lion King",
    "破壊獣": "Destructive Beast",
    "破壊王": "Destruction King",
    "破壊竜": "Destruction Dragon",
    "稲妻戦士": "Lightning Warrior",
    "空飛ぶムエタイ戦士": "Flying Muay Thai Warrior",
    "空飛ぶ天才児": "Flying Prodigy",
    "空駆ける牙": "Sky-Racing Fang",
    "突撃コング": "Charging Kong",
    "突貫小僧": "Rushing Kid",
    "策略男爵": "Scheming Baron",
    "粉砕隊長": "Smashing Captain",
    "紅顔の蹴撃手": "Red-Faced Kicker",
    "練習生": "Trainee",
    "翔龍戦士": "Soaring Dragon Warrior",
    "若虎": "Young Tiger",
    "草魂": "Grass Soul",
    "華麗なる天才": "Gorgeous Genius",
    "蒙古狼星": "Mongol Wolf Star",
    "蒼き彗星": "Blue Comet",
    "虎ハンター": "Tiger Hunter",
    "褐色爆弾": "Brown Bomber",
    "謀略仮面": "Scheming Mask",
    "豪傑": "Hero",
    "豪刀": "Great Sword",
    "豪腕継承": "Strong-Arm Heir",
    "赤鬼": "Red Demon",
    "超世代の旗手": "Super Generation Flagbearer",
    "超新星": "Supernova",
    "超竜": "Super Dragon",
    "足技の魔術師": "Leg Technique Magician",
    "蹴撃戦士": "Kicking Warrior",
    "遊牧王": "Nomad King",
    "選ばれし神の子": "Chosen Child of God",
    "重撃大王": "Heavy Blow King",
    "野人": "Wildman",
    "野生の熊": "Wild Bear",
    "鋼鉄のフェロモンボディ": "Steel Pheromone Body",
    "閃光": "Flash",
    "陰謀貴公子": "Conspiracy Nobleman",
    "陽気なクロネコ": "Cheerful Black Cat",
    "青い目の闘魂": "Blue-Eyed Fighting Spirit",
    "青春ハリケーン": "Youth Hurricane",
    "静寂の貴公子": "Silent Nobleman",
    "革命戦士": "Revolutionary Warrior",
    "鞍馬山天空伝": "Kurama Sky Legend",
    "風林火山": "Wind Forest Fire Mountain",
    "風雲昇り龍": "Rising Dragon of Storms",
    "鬼軍曹": "Demon Sergeant",
    "魂の蹴撃手": "Soul Kicker",
    "魔界の九州男児": "Demon World's Kyushu Man",
    "魔界の暴走凶悪犯": "Demon World's Rampaging Criminal",
    "魔界の無頼漢": "Demon World's Rogue",
    "魔界の番長": "Demon World's Boss",
    "魔界の総裁": "Demon World's President",
    "魔界の豪刀": "Demon World's Great Sword",
    "魔界の龍": "Demon World's Dragon",
    "魔界ストロングスタイル": "Demon World Strong Style",
    "黒の総帥": "Black Commander",
    "ＫＨＪ": "KHJ",
    "Ｍｒ．セントーン": "Mr. Senton",
    "Ｍｒ．Ｈ５０": "Mr. H50",
    "Ｓｉｒ．Ｐｒｏｍｅｎａｄｅ": "Sir Promenade",
    "Ｔｈｅ　Ｅｎｆｏｒｃｅｒ": "The Enforcer",
    "ＷＪの特攻隊長": "WJ's Kamikaze Captain",
})

# Field byte limits (ASCII = 1 byte/char).
LIMITS = {"family": 12, "given": 12, "nickname": 32, "finisher": 32}


def translate_part(ja):
    """One family/given part: PARTS, then PARTS_ADD, then segmenter."""
    if ja == "":
        return ""
    if ja in T10.PARTS:
        return T10.PARTS[ja]
    if ja in PARTS_ADD:
        return PARTS_ADD[ja]
    return T10.seg_translate(ja)


def translate_nick(ja):
    if ja == "":
        return ""
    if ja in NICK:
        return NICK[ja]
    return T10.translate(ja)


def translate_finisher(ja):
    if ja == "":
        return ""
    if ja in FIN_OVERRIDE:
        return FIN_OVERRIDE[ja]
    return translate_move(ja)


def main():
    survey = json.load(open(os.path.join(DATA, "koc2-file01999-survey.json")))
    recs = survey["wrestler_records"]
    out = {}
    failures = {}
    overflows = {}
    for field in ("family", "given", "nickname", "finisher"):
        failures[field] = set()
        overflows[field] = set()
    fn = {"family": translate_part, "given": translate_part,
          "nickname": translate_nick, "finisher": translate_finisher}
    for rec in recs:
        idx = rec["record"]
        entry = {"ja": {}, "en": {}}
        for field in ("family", "given", "nickname", "finisher"):
            ja = rec[field]
            entry["ja"][field] = ja
            en = fn[field](ja)
            entry["en"][field] = en
            if ja and en is None:
                failures[field].add(ja)
            elif en and len(en) > LIMITS[field]:
                overflows[field].add((ja, en, len(en)))
        out[str(idx)] = entry

    os.makedirs(WORK, exist_ok=True)
    json.dump(out, open(os.path.join(WORK, "translations-01999.json"), "w"),
              ensure_ascii=False, indent=1)
    # Review file: one line per record, compact.
    lines = []
    for rec in recs:
        idx = rec["record"]
        e = out[str(idx)]
        en = e["en"]
        lines.append(
            f"{idx:3d} {rec['family'] or '-'} {rec['given'] or '-'} "
            f"| {en['family'] or '-'} {en['given'] or '-'} "
            f"| nick: {en['nickname'] or '-'} "
            f"| fin: {en['finisher'] or '-'}")
    open(os.path.join(WORK, "translation-review-01999.txt"), "w").write(
        "\n".join(lines) + "\n")

    # Summary.
    total = 0
    done = 0
    for idx, e in out.items():
        for field in ("family", "given", "nickname", "finisher"):
            if e["ja"][field]:
                total += 1
                if e["en"][field] is not None:
                    done += 1
    print(f"records: {len(out)}  fields: {done}/{total} translated")
    for field in ("family", "given", "nickname", "finisher"):
        nf = len(failures[field])
        no = len(overflows[field])
        print(f"  {field}: {nf} failed, {no} overflow")
        for ja in sorted(failures[field]):
            print(f"    FAIL {ja}")
        for ja, en, n in sorted(overflows[field]):
            print(f"    OVERFLOW {ja} -> {en} ({n} chars)")


if __name__ == "__main__":
    main()
