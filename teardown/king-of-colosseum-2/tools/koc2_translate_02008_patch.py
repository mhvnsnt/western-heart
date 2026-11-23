#!/usr/bin/env python3
"""koc2_translate_02008_patch.py — Round 1 additions for the 02008
move-name translator (1011 failures after the base run).

Adds missing TERM/WHOLE entries to koc2_translate_02008, normalizes
full-width Latin letters (e.g. Ｌｏｗｋｉ -> Lowki) before translation,
then re-runs the base main(). Also diffs the result against the
previous translations-02008.json and reports any CHANGED entries
(new keys must not alter previously successful translations).

Usage: python3 tools/koc2_translate_02008_patch.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import koc2_translate_02008 as T  # noqa: E402

WORK = os.path.join(HERE, "..", "work")

# Full-width Latin/digits -> ASCII (the base segmenter only passes
# through ord(c) < 128; full-width letters like Ｌｏｗｋｉ stuck it).
_FW = str.maketrans(
    "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
    "０１２３４５６７８９",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789")

TERM_ADD = {
    # particles / grammar
    "に移行": "Transition", "へ移行する": "Transition",
    "に移行する": "Transition", "を外して": "Break",
    # katakana moves
    "ギロチンドロップ": "Guillotine Drop",
    "エクスプロイダー": "Exploder",
    "フラッシングエルボー": "Flushing Elbow",
    "スピアー": "Spear", "シザース": "Scissors",
    "サンセットフリップ": "Sunset Flip", "フォール": "Fall",
    "スレッジハンマー": "Sledgehammer", "ブロー": "Blow",
    "ケンカキック": "Brawl Kick", "ミノルスペシャル": "Minoru Special",
    "連打": "Flurry", "キャプチュード": "Captured",
    "ポジション": "Position", "ピンポイント": "Pinpoint",
    "レイス式": "Race-Style",
    "コジコジエルボー": "Koji-Koji Elbow", "踏みつけ": "Stomp",
    "ドライビング": "Driving",
    "ファイヤーマンズキャリー": "Fireman's Carry",
    "ラッシュ": "Rush", "シャイニング": "Shining",
    "ベリートゥバック": "Belly to Back",
    "コンビネーション": "Combination", "クランチ": "Crunch",
    "ブーツ": "Boots", "キチンシンク": "Kitchen Sink",
    "アックスボンバー": "Axe Bomber",
    "コンプリートショット": "Complete Shot",
    "マンハッタンドロップ": "Manhattan Drop",
    "リフトアップ": "Lift-Up",
    "スパインバスター": "Spinebuster",
    "ピースクラッシャー": "Peace Crusher",
    "ブルドッキング": "Bulldogging",
    "リアリティーチェック": "Reality Check",
    "アナコンダ": "Anaconda", "アレビンズ": "Alevins",
    "クラッシュ": "Crash", "ペンデュラム": "Pendulum",
    "バイアグラドライバー": "Viagra Driver",
    "春樹スペシャル": "Haruki Special",
    "アトミックドロップ": "Atomic Drop",
    "ノータッチ": "No-Touch", "ラウンディング": "Rounding",
    "ショーンキャプチャー": "Shawn Capture",
    "ゼロ戦": "Zero Fighter", "サファリプレス": "Safari Press",
    "キンニクバスター": "Muscle Buster",
    "バーニングハンマー": "Burning Hammer",
    "カット": "Cut", "フルネルソン": "Full Nelson",
    "マウント": "Mount",
    "ストラングルホールド": "Stranglehold",
    "ノーフィアー": "No Fear",
    "フィニッシュ宣言": "Finishing Declaration",
    "ロングホーン": "Longhorn", "ホーン": "Horn",
    "メイヤー": "Mayor",
    "コジカッター": "Koji Cutter",
    "ハンギングツリー": "Hanging Tree",
    "ハンギングボム": "Hanging Bomb",
    "ギロチン式": "Guillotine-Style",
    "ヒライエンド": "Hirai End",
    "サイレントデス": "Silent Death",
    "マイクボトム": "Mike Bottom",
    "ブルズ": "Bull's",
    "ハイチ": "Haichi",
    "メルトダウン": "Meltdown", "ディスティニー": "Destiny",
    "アックスギロチン": "Axe Guillotine",
    "トライアングル": "Triangle",
    "パート": "Part", "アルゼンチン": "Argentine",
    "アメリカン": "American", "ロシアン": "Russian",
    "モンゴリアン": "Mongolian",
    "ムエタイ": "Muay Thai", "ミクロ": "Micro",
    "スパイク": "Spike",
    # kanji segments
    "顔面": "Face", "ニーリフト": "Knee Lift",
    "首投げ": "Neck Throw",
    "俵返し": "Tawara Gaeshi",
    "起き上がり小法師": "Daruma",
    "引き起こす": "Pull Up",
    "火の玉": "Fireball",
    "水平": "Horizontal",
    "喉輪": "Throat",
    "馬乗り": "Mounted", "腕極め": "Arm-Locked",
    "膝": "Knee", "蹴り": "Kick",
    "振り下ろし": "Overhead",
    "後頭部": "Back of Head",
    "脇腹": "Side",
    "下から": "From Below",
    "威嚇": "Intimidation",
    "火祭り": "Fire Festival", "刀": "Sword",
    "腕取り": "Arm Grab", "足掛け": "Leg Hook",
    "倒し": "Takedown",
    "逆さ": "Inverted",
    "突き上げ": "Thrust-Up",
    "谷落とし": "Valley Drop",
    "足をかけて": "Leg Hook",
    "熱血": "Hot-Blooded",
    "爆殺": "Explosive",
    "骨法流": "Koppo-Style",
    "浴びせ蹴り": "Shower Kick",
    "毒霧": "Poison Mist",
    "掴み": "Grab",
    "足を取り": "Leg Grab",
    "軸足払い": "Pivot Foot Sweep",
    "ニールキック": "Kneel Kick",
}

WHOLE_ADD = {
    "俺が田上だ": "I Am Taue",
    "下からパンチ": "Uppercut",
}

# ---------- round 2 (472 failures left after round 1) ----------
TERM_ADD2 = {
    "ハンマーブロー": "Hammer Blow", "ハンマー": "Hammer",
    "スマッシュ": "Smash", "バイス": "Vice", "リフト": "Lift",
    "押さえ込み": "Pin", "脳天": "Top of Head",
    "アバランシュ": "Avalanche", "攻防": "Exchange",
    "ポセイドン": "Poseidon", "エッジ": "Edge",
    "ランサー": "Lancer", "テイクダウン": "Takedown",
    "ラグビータックル": "Rugby Tackle",
    "馬飛び式": "Leapfrog-Style",
    "クロスチョップ": "Cross Chop",
    "フォーアーム": "Forearm",
    "大ちゃん": "Dai-chan", "ワンダフル": "Wonderful",
    "背面": "Back", "マウンテンボム": "Mountain Bomb",
    "ブロックバスター": "Blockbuster",
    "ジョニーマジック": "Johnny Magic",
    "マシンガン": "Machine Gun",
    "張り手": "Slap", "胸": "Chest",
    "ウイザード": "Wizard",
    "フィッシャーマンズ": "Fisherman's",
    "みちのくドライバー": "Michinoku Driver",
    "デッドエンド": "Dead End", "タイアップ": "Tie-Up",
    "頭": "Head", "捻り": "Twist", "足": "Leg",
    "ノートン": "Norton", "胴": "Body",
    "胴絞め": "Body Squeeze",
    "ハーフネルソン": "Half Nelson", "クロー": "Claw",
    "アンド": "and", "ブリッジ": "Bridge",
    "ＫＡＺ": "KAZ", "ミッション": "Mission",
    "サムアップ": "Thumbs Up",
    "タモンズ": "Tamon's", "シューター": "Shooter",
    "十字固め": "Crucifix Pin",
    "腿": "Thigh", "スーパーフライ": "Superfly",
    "ハヤテ": "Hayate", "パウンド": "Pound",
    "恥ずかし": "Shy", "炎": "Flame", "コマ": "Top",
    "足一本": "One-Leg", "背負い": "Shoulder Throw",
    "軸足": "Pivot Foot", "腕回し": "Arm Swing",
    "サイン": "Sign", "フェイント": "Feint",
    "ベレー": "Beret",
    "皇帝戦士": "Emperor Warrior",
    "木刀": "Wooden Sword", "急所": "Vital Point",
    "龍式": "Dragon-Style", "デスブランド": "Death Brand",
    "スターネスダスト": "Starness Dust",
    "ジョン": "John", "ベリートゥベリー": "Belly to Belly",
    "アメイズインパクト": "Amaze Impact",
    "肘": "Elbow", "ライガーボム": "Liger Bomb",
    "ワンハンド": "One-Hand", "ホイップ": "Whip",
    "＆": "&", "号": "No.",
    "柔術": "Jiu-Jitsu", "空手": "Karate",
    "グー": "Rock", "馳": "Galloping", "ムタ": "Muta",
    "アリ": "Ant", "ブレインキック": "Brain Kick",
    "クレイジーサイクロン": "Crazy Cyclone",
    "フットボール": "Football", "マッケンロー": "McEnroe",
    "ゴールデンレフト": "Golden Left",
    "魔性": "Demonic", "スイクルデス": "Suicycle Death",
    "片足取らせ": "One-Leg",
    "延髄蹴り": "Medulla Kick",
    "延髄斬り": "Medulla Slash",
    "火炎": "Flame", "攻撃": "Attack",
    "パウダー": "Powder", "鬼葬": "Demon Burial",
    "毒針": "Poison Needle", "スルー": "Through",
    "ダウン": "Down", "チョコ": "Choco", "コロネ": "Cornet",
    "フラップジャック": "Flapjack", "文": "Mon",
    "スクラップバスター": "Scrap Buster",
    "スパインボム": "Spine Bomb", "パワード": "Powered",
    "プレス式": "Press-Style",
    "ターボドロップ": "Turbo Drop", "吊り": "Hang",
    "組み付き": "Grapple", "腕": "Arm",
    "グリ": "Grind", "ウオッシュ": "Wash",
    "カーフブランディング": "Calf Branding",
    "拝み渡り": "Prayer Crossing",
    "志賀式": "Shiga-Style", "プッシュ": "Push",
    "スティンクフェイス": "Stink Face",
    "バンクラッシュ": "Bang Crash",
    "シャリマティー": "Shalimati",
    "サマーソルトキック": "Somersault Kick",
    "多角系": "Multi-Angle",
    "横なぶり式": "Side-Tease Style",
    "コジコジカッター": "Koji-Koji Cutter",
    "アストロ": "Astro", "アイコノクラズム": "Iconoclasm",
    "スタンド": "Stand", "キー": "Key",
    "ブサイク": "Ugly Face",
}

WHOLE_ADD2 = {
    # word-order cases: "XへのY" = "Y to the X" (segmenter can't reorder)
    "後頭部へのドロップキック": "Dropkick to the Back of the Head",
    "顔面へのドロップキック": "Dropkick to the Face",
    "ブサイクへの膝蹴り": "Knee Kick to the Ugly Face",
    "膝にエルボー": "Elbow to the Knee",
    "顔張リ手": "Face Slap",  # variant kana (リ for り) in the game data
    "ビッシビシいくぞ": "Let's Go Hard!",
    "ドルフィンスペシャル１号": "Dolphin Special No. 1",
    "ドルフィンスペシャル２号": "Dolphin Special No. 2",
    "ハヤテスペシャル１号": "Hayate Special No. 1",
    "ハヤテスペシャル２号": "Hayate Special No. 2",
}

# ---------- round 3 (226 failures left after round 2; long tail) ----------
TERM_ADD3 = {
    "を返して": "Roll-Through",
    "ボンバー": "Bomber", "始動": "Start",
    "アトミック": "Atomic",
    "胸張り手": "Chest Slap",  # beats base '胸張り': 'Chest Out'
    "フェースクラッシャー": "Face Crusher",
    "イン": "in", "ひねり": "Twisting",
    "腰投げ": "Hip Throw",
    "オーバーヘッドキック": "Overhead Kick",
    "踏みにじる": "Trample",
    "フィストドロップ": "Fist Drop",
    "のしかかり": "Smother",
    "アースクエイクドロップ": "Earthquake Drop",
    "足卍": "Leg Manji",
    "バイパー": "Viper",
    "グランドクロス": "Grand Cross", "ループ": "Loop",
    "ペイン": "Pain", "クロスフェイス": "Crossface",
    "オブ": "of", "ＪＡＤＯ": "JADO",
    "アップ": "Up", "延髄": "Medulla",
    "スプリング式": "Spring-Style",
    "野人": "Wildman", "フロッグ式": "Frog-Style",
    "突撃": "Charging", "ナガイ": "Nagai",
    "殺し": "Killer", "ディープインパクト": "Deep Impact",
    "月面水爆": "Moon Surface H-Bomb",
    "カンクーン": "Cancun", "トペ": "Tope",
    "倒立トペ": "Handstand Tope",
    "スライディングキック": "Sliding Kick",
    "空牙": "Kuga", "フロム": "From", "トゥー": "to",
    "唾": "Spit", "スタンガン": "Stun Gun",
    "拷問ロープいじめ": "Torture Rope Bullying",
    "膠着": "Stalemate", "払う": "Sweep",
    "股割き": "Leg Split", "砕き": "Crush",
    "カニバサミ": "Crab Scissors",
    "ゴールデンゲートスピン": "Golden Gate Spin",
    "太鼓の乱れ打ち": "Wild Drum Beating",
    "ハイヤーデモリッション": "Higher Demolition",
    "サンドイッチ": "Sandwich",
    "シーソーバスター": "Seesaw Buster",
    "俺ごと": "With Me", "刈れ": "Mow Down",
    "刈龍怒": "Mowing Dragon Rage",
    "スターネス": "Starness",
    "斧爆弾": "Axe Bomb", "予告": "Announcement",
    "担ぐぞ": "I'll Carry You",
    "稲妻": "Lightning", "筋肉": "Muscle",
    "猛牛": "Fierce Bull", "振り向き": "Turn-Around",
    "若手": "Young Wrestler", "マッチョ": "Macho",
    "ラブ": "Love", "獣神": "Beast God",
    "ベルト": "Belt", "バートン": "Burton",
    "武蔵": "Musashi", "パンサー": "Panther",
    "ジークンドー": "Jeet Kune Do",
    "の構え": "Stance",
    "屈伸運動": "Stretching",
    "上空": "Skyward", "吹き": "Blow",
    "魔界": "Demon World", "首斬り": "Neck Slash",
    "力一杯": "Full-Power",
    "ポージング": "Posing", "マッスル": "Muscle",
    "跨ぎ": "Straddle", "カリーダンス": "Curry Dance",
    "アニマル": "Animal", "フォレスト": "Forest",
    "ケンケン": "Hop",
    "黒師": "Black Master", "念仏": "Prayer",
    "拝み": "Bow",
    "閃光魔術": "Flash Magic",
    "龍魂左腕": "Dragon Soul Left Arm",
    "糸巻き": "Thread-Winding",
    "真田": "Sanada",
    "太鼓腹": "Drum Belly", "叩き": "Slap",
    "ぐるぐる": "Spinning",
    "垂直落下": "Vertical Drop",
    "ドゥガンアップ": "Dugan Up",
    "コリノ": "Korino", "一番": "Number One",
    "竜殺し刀": "Dragon-Slayer Sword",
    "歩き": "Walk",
    "威風堂々": "Majestic", "広げ": "Spread",
    "会場見回し": "Surveying the Arena",
    "手を腰": "Hands on Hips",
    "富豪": "Rich Man", "見回し": "Survey",
    "ドクター": "Doctor", "片手": "One Hand",
    "あげ": "Up",
    "ガンつけ": "Death Stare",
    "シャドーボクシング": "Shadowboxing",
    "キッス": "Kiss", "太陽": "Sun",
    "ゼロセン": "Zero-Sen",
    "理不尽": "Unreasonable",
    "モハメド": "Mohamed", "テング": "Tengu",
    "アダモ": "Adamo",
    "コジコジポーズ": "Koji-Koji Pose",
    "飛行機": "Airplane",
    "掻きむしり": "Scratching",
    "サミング": "Thumbing",
    "ランカシャーエルボー": "Lancashire Elbow",
    "腹": "Belly", "バット": "Butt",
    "唐竹割り": "Bamboo Split",
    "突っ張り": "Thrust", "電車道": "Train",
    "肩掴み": "Shoulder Grab",
    "噛みつき": "Bite", "凶器": "Weapon",
    "頚動脈": "Carotid Artery",
    "足取らせ": "Leg Grab",
    "こすり": "Rub",
    "鉄拳制裁": "Iron Fist Punishment",
    "ワンツー": "One-Two", "冴刃": "Saeba",
    "喧嘩屋": "Brawler", "マッハ": "Mach",
    "組み": "Grapple",
    "突き放し": "Shove-Off",
    "ジルバ": "Zilba", "潰し": "Crush",
    "金本": "Kanemoto",
    "振りぬき": "Swing-Through",
    "を引っ張る": "Pull",
    "手首": "Wrist", "ベン": "Ben",
    "シュミット式": "Schmidt-Style",
    "フィニッシュ用": "Finishing",
    "オクラホマスタンピート": "Oklahoma Stampede",
    "ハインズ": "Hines",
    "ファイヤーサンダー": "Fire Thunder",
    "ターンバック": "Turnback",
    "網打ち式": "Net-Strike Style",
    "コジコジドライバー": "Koji-Koji Driver",
    "ゴリラーマンズ": "Gorilla-Man's",
    "ショットガン": "Shotgun",
    "ジャックスラム": "Jack Slam",
    "歳": "Years Old",
    "クラッチ式": "Clutch-Style",
    "フィッシャーマン": "Fisherman",
    "侍": "Samurai",
    "ジャックハマー": "Jackhammer",
    "ハーフハッチ": "Half Hatch",
    "サドン": "Sudden",
    "魔神風車": "Demon God Windmill",
    "ブロック": "Block",
    "エアープレーンスピン": "Airplane Spin",
    "アルゼンチン式": "Argentine-Style",
    "背骨折り": "Backbreaker",
    "チャタヌガチュチュ": "Chattanooga Choo Choo",
    "オリンピック予選": "Olympic Qualifier",
    "スパイシー": "Spicy", "ファイブ": "Five",
    "コースター": "Coaster",
    "ベアハッグ": "Bear Hug",
    "スロイダー": "Sloider",
    "ウンターグルフ": "Untergulf",
    "嵐": "Storm", "ヤスティ": "Yasti",
    "トス": "Toss", "ハイジャック": "Hijack",
    "スパイラル": "Spiral", "ワイルド": "Wild",
    "コンプリートダスト": "Complete Dust",
    "ビルディングボム": "Building Bomb",
    "バイソンテニエル": "Bison Teniel",
    "アッサム": "Assam", "バート": "Bart",
    "ジャンボ": "Jumbo", "ライド": "Ride",
    "対角線": "Diagonal",
    "歌舞伎役者": "Kabuki Actor",
    "横抱え式": "Side-Carry Style",
    "肩車式": "Shoulder-Ride Style",
    "首かっきり": "Neck Snap",
    "バーニングソード": "Burning Sword",
    "グランドキャニオン": "Grand Canyon",
    "押え込み": "Pin",
    "ボルケーノ": "Volcano",
    "バイ": "Bye", "バレー": "Valley",
    "ミリオンダラーバスター": "Million Dollar Buster",
}

WHOLE_ADD3 = {
    "炎のコマ": "Flame Top",
    "後頭部へ逆水平チョップ":
        "Reverse Horizontal Chop to the Back of the Head",
    "肩口にエルボー": "Elbow to the Shoulder",
    "ブサイクへの顔面潰し": "Ugly Face Crush",
    "背中にエルボーバット": "Elbow Butt to the Back",
    "１０時１０分チョップ": "10:10 Chop",
}

# ---------- round 4 (7 failures left after round 3) ----------
TERM_ADD4 = {
    "ムーンサルト": "Moonsault",
    "ブレーン": "Brain",
    "サファリ": "Safari",
    "アウト": "Out",
    "バッシュ": "Bash",
    "式": "Style",
    "イラプション": "Eruption",
}

WHOLE_ADD4 = {
    "ジャイアントＳ・Ｔ・Ｆ": "Giant S.T.F.",
}


def main():
    prev = {}
    prev_path = os.path.join(WORK, "translations-02008.json")
    if os.path.exists(prev_path):
        with open(prev_path, encoding="utf-8") as f:
            prev = json.load(f)
    T.TERM.update(TERM_ADD)
    T.WHOLE.update(WHOLE_ADD)
    T.TERM.update(TERM_ADD2)
    T.WHOLE.update(WHOLE_ADD2)
    T.TERM.update(TERM_ADD3)
    T.WHOLE.update(WHOLE_ADD3)
    T.TERM.update(TERM_ADD4)
    T.WHOLE.update(WHOLE_ADD4)
    # re-sort longest-match keys after the update
    T._TERM_KEYS = sorted(T.TERM, key=len, reverse=True)
    T._WHOLE_KEYS = sorted(T.WHOLE, key=len, reverse=True)
    # wrap translate_move with full-width Latin normalization as a
    # FALLBACK ONLY: the base TERM already holds full-width keys
    # (ＤＤＴ, ＳＴＯ, ...) that must win first — normalizing first
    # broke them ('DDT' -> 'D D T', 58 regressions in round 1).
    orig_translate_move = T.translate_move

    def wrapped(ja):
        en = orig_translate_move(ja)
        if en is None:
            en = orig_translate_move(ja.translate(_FW))
        return en

    T.translate_move = wrapped
    T.main()
    # diff check: no previously successful entry may change
    with open(prev_path, encoding="utf-8") as f:
        new = json.load(f)
    changed = [(k, prev[k], new[k]) for k in prev
               if k in new and prev[k] != new[k]]
    print(f"previous: {len(prev)}, now: {len(new)}, "
          f"changed old entries: {len(changed)}")
    for k, a, b in changed[:20]:
        print(f"  CHANGED {k}: {a!r} -> {b!r}")


if __name__ == "__main__":
    main()
