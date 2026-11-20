#!/usr/bin/env python3
"""KoC2 Milestone 2: translate file 02010 (master string table, 4021 strings).

Builds work/translations-02010.json: {physical_index: english_text}.
Translate by PHYSICAL index (see docs/FILE-02010-FORMAT.md).
Feed the result to tools/koc2_strings_build.py — never hand-edit strings.

Name sources: data/koc2-roster-romanized.json (FAQ-backed + machine readings
reviewed/corrected 2026-11-19) + EXTRA_NAMES below (non-roster names that
appear in the theme/narration categories).
"""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, '..')
sys.path.insert(0, HERE)

# ---------------------------------------------------------------- names
# Corrections to machine (pykakasi) readings, reviewed 2026-11-19.
# Japanese names are given in WESTERN order (given family) to match the FAQ.
FIX = {
 'アンドレィ・ジルバ': 'Andrei Zilba', 'ウォルフ・バーン': 'Wolf Burn',
 'エドワード・アイフル': 'Edward Eiffel', 'カルロス・クラウザー': 'Carlos Krauser',
 'ケイン・ハーロック': 'Kane Harlock', 'キース・ラーニング': 'Keith Learning',
 'ジャイアント・ロシュモフ': 'Giant Roshumov', 'チョータ・ポポビッチ': 'Chota Popovich',
 'ネイマン・ショーンズ': 'Neiman Shones', 'ベイク・ゲルハルト': 'Bake Gerhardt',
 'ベーム・シュトゥルム': 'Boehm Sturm', 'ボーン・クライ': 'Bone Cry',
 'マイク・アント': 'Mike Ant', 'ミスターフェイク': 'Mister Fake',
 'ムハンマド・ダリ': 'Muhammad Dari', 'ランドル・ロビィコフ': 'Randall Robikov',
 'リカルド・マローナ': 'Ricardo Marona', 'ルガール・ロブハンキン': 'Rugal Robhankin',
 'レオモンド・スパイキー': 'Leomond Spiky', 'レビン・ガッシュ': 'Levin Gash',
 'ロナウド・トバル': 'Ronaldo Tobar', 'ヴァイティング・パイソン': 'Viting Python',
 'ワルサーＫＹＯＴＯ': 'Walther KYOTO', '下山\u3000龍飛': 'Tatsuhi Shimoyama',
 '冴刃\u3000明': 'Akira Saeba', '國奥\u3000麒樹真': 'Kikimasa Kunioku',
 '安藤\u3000障二': 'Shoji Ando', '愚零斗孤士': 'Gureito Koshi',
 '愚零斗孤士ズキン': 'Gureito Koshi Zukin', '木原\u3000文人': 'Fumihito Kihara',
 '梨田\u3000秀吉': 'Hideyoshi Nashida', '梶原\u3000丈': 'Jo Kajiwara',
 '榊\u3000四五朗': 'Shigoro Sakaki', '田上\u3000明': 'Akira Taue',
 '田中\u3000秀和': 'Hidekazu Tanaka', '矢吹\u3000光世': 'Mitsuyo Yabuki',
 '帽子カリー・マスク': 'Hat Curry Mask', 'オッキー沖田': 'Okky Okita',
 'Ｓ・ドルフィン': 'S. Dolphin', 'Ｓ・Ｓ・マシン': 'S.S. Machine',
 # corrections to earlier FAQ-fuzzy/override readings
 '武藤\u3000敬司': 'Keiji Muto', '崔\u3000リョウジ': 'Ryoji Sai',
 '富豪２夢路': 'Fugo 2 Yumeji', '富豪２亀路': 'Fugo 2 Kameji',
 '保坂\u3000秀樹': 'Hideki Hosaka', '黒毛和牛太': 'Kuroge Wagyuta',
 'えぼすさん': 'Ebisu-san', '魔界１号': 'Makai No. 1',
 '魔界２号': 'Makai No. 2', '魔界４号': 'Makai No. 4',
 '魔界５号': 'Makai No. 5', '黒師無双': 'Kokushi Muso',
 'カサ黒師無双': 'Kokushi Muso w/ Hat',
}

# Names that appear in cats 22/23/24 but are NOT in the roster (non-playable
# wrestlers, referees, generic labels, kanji variants of roster names).
EXTRA_NAMES = {
 '星野\u3000勘太郎': 'Kantaro Hoshino', '村上\u3000和成': 'Kazunari Murakami',
 '柳澤\u3000龍志': 'Ryuji Yanagisawa', '魔界１号': 'Makai No. 1',
 '魔界２号': 'Makai No. 2', '魔界４号': 'Makai No. 4', '魔界５号': 'Makai No. 5',
 'エンセン井上': 'Ensen Inoue', '小原\u3000道由': 'Michiyoshi Ohara',
 '矢野\u3000通': 'Toru Yano', '田口\u3000隆祐': 'Ryusuke Taguchi',
 '山本\u3000尚文': 'Naofumi Yamamoto', '長尾\u3000浩志': 'Hiroshi Nagao',
 '後藤\u3000洋央紀': 'Hirooki Goto', '坂口\u3000征二': 'Seiji Sakaguchi',
 '木村\u3000健悟': 'Kengo Kimura', '木戸\u3000修': 'Osamu Kido',
 '山崎\u3000一夫': 'Kazuo Yamazaki', '平田\u3000淳嗣': 'Junji Hirata',
 '小林\u3000邦昭': 'Kuniaki Kobayashi',
 'ドルゴルスレン・スミヤバザル': 'Dolgorsuren Sumiyabazar',
 'ドルゴルスレン・セルジブデ': 'Dolgorsuren Serjibude',
 'ブラック・タイガー': 'Black Tiger', 'ブラックタイガー': 'Black Tiger',
 'ブラック・キャット': 'Black Cat', '青柳\u3000政司': 'Masashi Aoyagi',
 'マイティ井上': 'Mighty Inoue', 'マイケル・モデスト': 'Michael Modest',
 'バイソン・スミス': 'Bison Smith', 'ドノバン・モーガン': 'Donovan Morgan',
 'リチャード・スリンガー': 'Richard Slinger', 'グレート・ムタ': 'Great Muta',
 '黒師無双': 'Kokushi Muso', '石狩\u3000太一': 'Taichi Ishikari',
 '河野\u3000真幸': 'Masayuki Kono', 'ビッグ・ジョン・テンタ': 'Big John Tenta',
 'ザ・グラジエーター': 'The Gladiator', 'ジョージ・ハインズ': 'George Hines',
 'ハシフ・カーン': 'Hashif Khan', '大谷\u3000晋二郎': 'Shinjiro Otani',
 '田中\u3000将斗': 'Masato Tanaka', '高岩\u3000竜一': 'Ryuichi Takaiwa',
 '星川\u3000尚浩': 'Naohiro Hoshikawa', '佐藤\u3000耕平': 'Kohei Sato',
 'テングカイザー': 'Tengu Kaiser', '藤原\u3000喜明': 'Yoshiaki Fujiwara',
 '坂田\u3000亘': 'Wataru Sakata', '横井\u3000宏考': 'Hirotaka Yokoi',
 '小笠原\u3000和彦': 'Kazuhiko Ogasawara', '崔\u3000リョウジ': 'Ryoji Sai',
 '富豪２夢路': 'Fugo 2 Yumeji', '富豪２亀路': 'Fugo 2 Kameji',
 '保坂\u3000秀樹': 'Hideki Hosaka', '黒毛和牛太': 'Kuroge Wagyuta',
 '葛西\u3000純': 'Jun Kasai', '佐々木\u3000義人': 'Yoshihito Sasaki',
 '山笠Ｚ”信介': 'Shinsuke Z Yamagasa', '高橋\u3000冬樹': 'Fuyuki Takahashi',
 'トム・ハワード': 'Tom Howard', 'ザ・プレデター': 'The Predator',
 'マット・ガファリ': 'Matt Gaffari', 'スティーブ・コリノ': 'Steve Corino',
 'Ｃ・Ｗ・アンダーソン': 'C.W. Anderson', 'キング・アダモ': 'King Adamo',
 'ヴァンサック・アシッド': 'Vansack Acid', '高山\u3000善廣': 'Yoshihiro Takayama',
 '長州\u3000力': 'Riki Choshu', '天龍\u3000源一郎': 'Genichiro Tenryu',
 'パワー・ウォリアー': 'Power Warrior', '大森\u3000隆男': 'Takao Omori',
 '越中\u3000詩郎': 'Shiro Koshinaka', '石井\u3000智宏': 'Tomohiro Ishii',
 '宇和野\u3000貴史': 'Takashi Uwano', '高智\u3000政光': 'Masamitsu Takachi',
 '中嶋\u3000勝彦': 'Katsuhiko Nakajima', 'マサ・サイトー': 'Masa Saito',
 '保永\u3000昇男': 'Nobuo Yasunaga', '近藤\u3000有己': 'Yuki Kondo',
 'ＫＥＩ\u3000山宮': 'KEI Yamamiya', '山宮恵一郎': 'Keiichiro Yamamiya',
 '窪田\u3000幸生': 'Yukio Kubota', '石川\u3000英司': 'Eiji Ishikawa',
 '田村\u3000潔司': 'Kiyoshi Tamura', '上山\u3000龍紀': 'Ryuki Ueyama',
 '大久保\u3000一樹': 'Kazuki Okubo', '長南\u3000亮': 'Ryo Chonan',
 '佐々木\u3000恭介': 'Kyosuke Sasaki', 'えぼすさん': 'Ebisu-san',
 '藤波\u3000辰巳': 'Tatsumi Fujinami', '藤波辰巳': 'Tatsumi Fujinami',
 '小橋\u3000健太': 'Kenta Kobashi', '小橋健太': 'Kenta Kobashi',
 '真田\u3000信久': 'Nobuhisa Sanada', '真田信久': 'Nobuhisa Sanada',
 '佐野\u3000なおき': 'Naoki Sano', '飯塚\u3000孝之': 'Takayuki Iizuka',
 '荒谷\u3000信孝': 'Nobutaka Aratani', '野上\u3000彰': 'Akira Nogami',
 'クラッシャーバンバンヒライ': 'Crusher Bam Bam Hirai',
 'ミツ・ヒライＪｒ．': 'Mitsu Hirai Jr.', 'Ｍｒ．ＯＴＡＮＩ': 'Mr. OTANI',
 'ＭＡＳＡ・ＴＡＮＡＫＡ': 'MASA TANAKA', 'オージー・ビーフ': 'Aussie Beef',
 'サル・ザ・マン': 'Saru the Man', 'サムライ・シロー': 'Samurai Shiro',
 '渡辺\u3000大介': 'Daisuke Watanabe', 'アックス・ノーガン': 'Axe Nogan',
 'ケルベロス・ボヘミア': 'Cerberus Bohemia',
 'ホーネット・ビースト': 'Hornet Beast', 'ディー・ロウ・ブラウン': 'D-Lo Brown',
 'ブキャナン': 'Buchanan', 'ジャマール': 'Jamal', 'ブラスターズ': 'Blasters',
 'ケンタウロス・ボヘミア': 'Centauros Bohemia',
 'ビッグ・ザ・Ｇ・ブル': 'Big The G. Bull', '榊\u3000四五郎': 'Shigoro Sakaki',
 '獣神サンダーライガー': 'Jyushin Thunder Liger',
 '鈴木鼓太郎': 'Kotaro Suzuki', '桜木“ジェット”旅人': 'Sakuragi "Jet" Tabibito',
 'さだ・・・ｓａｎ': 'Sada...san', '若き航海士': 'Young Sailor',
 '若き獅子': 'Young Lion', 'ヤングライオン': 'Young Lion',
 'あすなろ戦士': 'Asunaro Warrior', 'ヤングマグマ': 'Young Magma',
 '新人レスラー': 'Rookie Wrestler', '中堅レスラー': 'Mid-Card Wrestler',
 'ベテランレスラー': 'Veteran Wrestler', 'デスマッチレスラー': 'Deathmatch Wrestler',
 'ジュニアヘビー': 'Junior Heavyweight', 'ヘビー': 'Heavyweight',
 '外国人レスラー': 'Foreign Wrestler', 'アメリカ': 'America',
 'カナダ': 'Canada', 'ヨーロッパ': 'Europe', 'ロシア': 'Russia',
 'オランダ': 'Netherlands', 'サモア': 'Samoa', 'モンゴル': 'Mongolia',
 '総合格闘家': 'MMA Fighter', 'ブラジリアン柔術': 'Brazilian Jiu-Jitsu',
 'キックボクサー': 'Kickboxer', '空手家': 'Karateka', 'ボクサー': 'Boxer',
 '謎の男': 'Mysterious Man', 'メキシコ': 'Mexico',
 '未確認生命体': 'Unidentified Lifeform', '動物': 'Animal',
 'メジャー級の選手': 'Major League Wrestler', 'マッチョ系': 'Macho Type',
 '汎用': 'Generic', 'エル・サムライ': 'El Samurai',
 'ケンドー・カシン': 'Kendo Kashin', 'カズ・ハヤシ': 'Kaz Hayashi',
 '宮本\u3000和志': 'Kazushi Miyamoto', 'ターメリック': 'Turmeric',
 'マスカラ兄弟': 'Mascara Brothers', 'テキサン兄弟': 'Texan Brothers',
 'ステイシー一族': 'Stacy Family', 'ロシア軍団': 'Russian Army',
 'ＭＷＡ': 'MWA', 'グラップラー': 'Grappler', 'ストライカー': 'Striker',
 'バーリトゥーダー': 'Vale Tudo Fighter', 'ルチャドール': 'Luchador',
 'アメリカンレスラー': 'American Wrestler', '太陽ケア': 'Taiyo Kea',
 'Ｇ・ロシュモフ': 'G. Roshumov', 'Ｓ・ジェイムス': 'S. James',
 'ラッシャー木村': 'Rusher Kimura', '永源\u3000遙': 'Haruka Eigen',
 '百田\u3000光雄': 'Mitsuo Momota', 'スコーピオ': 'Scorpio',
 'ハンク・フォレスト': 'Hank Forest', 'ドン・ローガン': 'Don Logan',
 '佐々木\u3000有生': 'Yusei Sasaki', '廣戸\u3000聡一': 'Soichi Hiroto',
 'ＷＩＬＤⅡ': 'WILD II', 'ＷＩＬＤ': 'WILD',
 'マスク・ド・パンサーⅡ': 'Mask Do Panther II',
}

# Quoted version suffixes in cats 0/15: "Name“SUFFIX”" -> "Name (English)".
SUFFIX = {
 '０１Ｖｅｒ': '01 Ver', '０２Ｖｅｒ': '02 Ver', '０２ｖｅｒ': '02 Ver',
 '０３ｖｅｒ': '03 Ver', '０４Ｖｅｒ': '04 Ver', '１９９４Ｖｅｒ': '1994 Ver',
 'ＩＷＧＰＶｅｒ': 'IWGP Ver', 'ＭドラゴンＶｅｒ': 'M Dragon Ver',
 'ＮＢＭＶｅｒ': 'NBM Ver', '短髪Ｖｅｒ': 'Short Hair Ver',
 '長髪Ｖｅｒ': 'Long Hair Ver', '髪ありＶｅｒ': 'With Hair Ver',
 '髪Ｖｅｒ': 'Hair Ver', '坊主Ｖｅｒ': 'Shaved Ver', '坊主ｖｅｒ': 'Shaved Ver',
 '金髪Ｖｅｒ': 'Blonde Ver', '髭なしＶｅｒ': 'No Beard Ver',
 'スキンＶｅｒ': 'Skin Ver', 'オレンジＶｅｒ': 'Orange Ver',
 'アフロＶｅｒ': 'Afro Ver', 'イエローＶｅｒ': 'Yellow Ver',
 '夏男Ｖｅｒ': 'Summer Man Ver', '超世代Ｖｅｒ': 'Super Generation Ver',
 '超世代ｖｅｒ': 'Super Generation Ver', '四天王Ｖｅｒ': 'Four Heavenly Kings Ver',
 '聖鬼軍Ｖｅｒ': 'Seiki-gun Ver', '革命Ｖｅｒ': 'Revolution Ver',
 '海外Ｖｅｒ': 'Overseas Ver', '男だＶｅｒ': 'Otoko da Ver',
 'あすなろＶｅｒ': 'Asunaro Ver', 'ノーフィアーＶｅｒ': 'No Fear Ver',
 'ハセケンＶｅｒ': 'Haseken Ver', 'バク進Ｖｅｒ': 'Bakushin Ver',
 'ジェイソンＶｅｒ': 'Jason Ver', 'レトロＶｅｒ': 'Retro Ver',
 'ジェット': 'Jet',
}

# Parenthetical contents: （X） -> (English).
PAREN = {
 '指テ': 'Finger Tape', '甲テ': 'Back-of-Hand Tape', '毛': 'Hairy',
 '毛＆指テ': 'Hairy & Finger Tape', '毛＆甲テ': 'Hairy & Back-of-Hand Tape',
 '細': 'Slim', '中': 'Medium', '太': 'Heavy', '恭': 'Kyo',
 'ＰＷＦ': 'PWF', 'ＵＮ': 'UN', 'インター': 'Inter', '三本巻き': '3 Belts',
 '手': 'Handclap', 'Ｃ': 'Chorus', 'ｔｙｐｅＣ': 'type C',
 '山崎': 'Yamazaki', '田村': 'Tamura',
}

# Whole-string overrides: enums, titles, catchphrases, narration, named themes.
WHOLE = {
 # cat 1 styles
 'ストロング': 'Strong', 'テクニック': 'Technique', 'アマレス': 'Amateur',
 'パワー': 'Power', 'ルチャ': 'Lucha', 'シューティング': 'Shoot',
 'ミステリアス': 'Mysterious', '骨法': 'Koppo', '柔術': 'Jiu-Jitsu',
 'ボクシング': 'Boxing', '総合系': 'MMA Style', 'フリーファイター': 'Free Fighter',
 'グラウンド': 'Ground',
 # cat 2 body types
 'ノーマル（細）': 'Normal (Slim)', 'ノーマル（中）': 'Normal (Medium)',
 'ノーマル（太）': 'Normal (Heavy)', 'デブ（中）': 'Fat (Medium)',
 'デブ（太）': 'Fat (Heavy)', 'マッスル': 'Muscle', 'ジャイアント': 'Giant',
 'グッドシェイプ': 'Good Shape', 'レボリューション': 'Revolution',
 'クラッシャー': 'Crusher', 'レスラーマッスル': 'Wrestler Muscle',
 'ダイナミック': 'Dynamic', 'セイバー': 'Saber',
 # cat 3 sizes
 'ＳＳ': 'SS', 'Ｓ': 'S', 'Ｍ': 'M', 'Ｌ': 'L', 'ＬＬ': 'LL',
 # cat 4 costume types
 'ノーマル': 'Normal', '柔道着': 'Judo Gi', 'パンタロン': 'Pantalon',
 '忍者': 'Ninja', 'もんぺ': 'Monpe', '裾入れジーンズ': 'Tucked Jeans',
 'ジャージ': 'Jersey', 'トランクス': 'Trunks', '総裁スーツ': 'President Suit',
 'ケロ': 'Kero', '木原': 'Kihara',
 # cat 5 boolean
 'なし': 'None', 'あり': 'Yes',
 # cat 19/20 titles & weapons
 'ＩＷＧＰヘビー': 'IWGP Heavyweight', '旧ＩＷＧＰヘビー': 'Old IWGP Heavyweight',
 'ＩＷＧＰジュニア': 'IWGP Junior Heavyweight', 'ＩＷＧＰタッグ': 'IWGP Tag Team',
 'ＩＷＧＰジュニアタッグ': 'IWGP Junior Tag Team',
 '三冠ヘビー（三本巻き）': 'Triple Crown Heavyweight (3 Belts)',
 '三冠ヘビー（ＰＷＦ）': 'Triple Crown Heavyweight (PWF)',
 '三冠ヘビー（ＵＮ）': 'Triple Crown Heavyweight (UN)',
 '三冠ヘビー（インター）': 'Triple Crown Heavyweight (Inter)',
 '世界タッグ（ＰＷＦ）': 'World Tag Team (PWF)',
 '世界タッグ（インター）': 'World Tag Team (Inter)',
 '世界ジュニア': 'World Junior Heavyweight', 'アジアタッグ': 'Asia Tag Team',
 'アジアタッグ②': 'Asia Tag Team 2',
 'キングオブパンクラス\u3000無差別級': 'King of Pancrase Openweight',
 'キングオブパンクラス\u3000ヘビー級': 'King of Pancrase Heavyweight',
 'キングオブパンクラス\u3000ライトヘビー級': 'King of Pancrase Light Heavyweight',
 'キングオブパンクラス\u3000ミドル級': 'King of Pancrase Middleweight',
 'キングオブパンクラス\u3000ウェルター級': 'King of Pancrase Welterweight',
 'ＧＨＣヘビー': 'GHC Heavyweight', 'ＧＨＣタッグ': 'GHC Tag Team',
 'ＧＨＣジュニアヘビー': 'GHC Junior Heavyweight', 'ＮＷＦヘビー': 'NWF Heavyweight',
 'ＧＨＣジュニアタッグ': 'GHC Junior Tag Team',
 '天下一ヘビー': 'Tenkaichi Heavyweight', '天下一タッグ': 'Tenkaichi Tag Team',
 '天下一Ｊｒ．': 'Tenkaichi Jr.', 'ＷＭＧヘビー': 'WMG Heavyweight',
 'ＷＭＧタッグ': 'WMG Tag Team', 'Ｕ−３０無差別級': 'U-30 Openweight',
 'チェーン': 'Chain', 'ブルロープ': 'Bull Rope', 'バット': 'Bat',
 '竜殺し刀': 'Dragon Slayer Sword', 'コジコジ刀': 'Kojikoji Sword',
 '木刀': 'Wooden Sword', '椅子': 'Chair', '火祭り刀': 'Fire Festival Sword',
 '破邪の小太刀': 'Short Sword of Evil-Breaking',
 # cat 21 entrance catchphrases
 '大谷のぼり': 'Otani Banner', 'タオル': 'Towel',
 '炎の飛龍': 'Flame Flying Dragon', '昭和のラストチャレンジャー': "Showa's Last Challenger",
 '右腕に全てを込めて': 'Everything in My Right Arm',
 '唸れ豪腕リキラリアット': 'Roar, Powerful Riki Lariat',
 '美しく、そして強くあれ': 'Beautiful, and Strong',
 'プロレス・ラブ': 'Pro-Wrestling Love', 'クロスウイザード': 'Cross Wizard',
 '２１世紀のミスタープロレス': '21st Century Mr. Pro-Wrestling',
 '華麗に決めてやる': "I'll Finish It in Style",
 '地獄へお連れいたしましょう': 'Let Me Take You to Hell',
 '首かっ切って見せます': "I'll Cut Your Head Off",
 '拝ませて頂きます': 'Behold!', '全てを黒く塗り潰せ': 'Paint It All Black',
 '夏はまかせろ、俺がＧ１男だ': "Summer Is Mine, I'm the G1 Man",
 '己の道を突き進め': 'Forge Ahead on Your Own Path',
 '今、新たな刀を抜く時': 'Now, the Time to Draw a New Sword',
 'その全てをぶつけろ': 'Put Everything Into It',
 '力こそ全て、叩き潰すのみ': 'Power Is Everything, Crush Them All',
 'この試合に全てを賭ける': 'Betting Everything on This Match',
 '新時代の主役は俺だ': "I'm the Star of the New Era",
 'プロレス界の革命児': 'The Revolutionary of Pro-Wrestling',
 'ザ・トップオブ・ジュニア': 'The Top of the Juniors',
 'ジュニア最強の称号をひっさげ': 'Bearing the Title of Strongest Junior',
 '最強外国人の称号を胸に': 'With the Title of Strongest Foreigner in My Heart',
 'その強さに文句無し': 'No Complaints About That Strength',
 'ミスター無我、今夜も無我満開': 'Mr. Muga, in Full Bloom Again Tonight',
 '巨星復活、世界の巨人': 'The Giant Star Returns, the Giant of the World',
 '昭和の怪物、風雲昇り龍': 'Showa Monster, Rising Dragon of the Storm',
 '世界の不沈艦': "The World's Unsinkable Battleship",
 '王道継承': "Heir to the King's Road",
 '新日本プロレスの全てを背負い': 'Carrying All of New Japan Pro-Wrestling',
 '全日本プロレスの全てを背負い': 'Carrying All of All Japan Pro-Wrestling',
 '灼熱の太陽の如く': 'Like the Blazing Sun', 'デンジャラスＫ': 'Dangerous K',
 'ＵＷＦ最後の継承者': 'The Last Heir of UWF',
 '闘魂伝承': 'The Fighting Spirit Lives On',
 'アイアムプロレスラー': 'I Am Pro-Wrestler',
 '新世紀、大巨人伝説': 'New Century, Legend of the Great Giant',
 '波瀾万丈の人生劇場': "A Stormy Life's Drama",
 '戦慄の暴走王': 'The Terrifying Rampaging King',
 'その右肘に魂を宿し': 'A Soul Dwells in That Right Elbow',
 'その魂を握りしめ': 'Clutching That Soul Tight',
 '燃え盛れ、バーニング': 'Burn Bright, Burning',
 '新世代革命児': 'The Revolutionary of the New Generation',
 '恐れ知らずのノーフィアー': 'Fearless No Fear',
 '恐れ知らずのこの男': 'This Fearless Man',
 '破壊なくして創造なし': 'No Destruction, No Creation',
 '破壊王': 'The Destruction King', '不滅の闘魂': 'The Undying Fighting Spirit',
 '完全無欠の怪物': 'The Perfect Monster', '４５０戦無敗': '450 Matches Undefeated',
 '己の信ずるまま': 'As I Believe',
 '時は来た、天下は俺が取る': "The Time Has Come, I'll Take the World",
 '戦慄のアルティメットチャンピオン': 'The Terrifying Ultimate Champion',
 'そぴえ立つ、アパッチタワー': 'Towering, the Apache Tower',
 'アイアムＵＷＦ': 'I Am UWF', 'ザ・ビースト野獣襲来': 'The Beast Attacks',
 '柔術マジシャン': 'Jiu-Jitsu Magician', 'ファイティングビースト': 'Fighting Beast',
 '野人よ、その力を解き放て': 'Wild Man, Unleash Your Power',
 'ノーフィアー': 'No Fear', '新日本のエースはこの男': "This Man Is NJPW's Ace",
 '猪突猛牛、その角を突き立てろ': 'Charging Bull, Drive Those Horns In',
 '豪腕継承、その右腕に魂を宿せ': 'Heir to the Powerful Arm, Let a Soul Dwell in That Right Arm',
 '驚異のフライングタンク': 'The Amazing Flying Tank', 'ど真ん中': 'Dead Center',
 '皇帝戦士': 'The Emperor Warrior',
 'ど真ん中を突き進め': 'Charge Straight Down the Middle',
 '超新星': 'Supernova', 'スーパールーキー': 'Super Rookie',
 '進化を続ける格闘超新星': 'The Ever-Evolving Fighting Supernova',
 'ビッシビシいくぞ': "Let's Lay It In Hard",
 '魔界の暴走テロリスト': 'The Rampaging Terrorist of Makai',
 '世紀末覇王、北斗の名のもとに': 'End-of-Century Champion, in the Name of Hokuto',
 'アイアムど真ん中': 'I Am Dead Center', '蒙古襲来': 'The Mongol Invasion',
 '生粋の大和魂': 'The True Yamato Spirit',
 'ダイナミックＴ大噴火か': 'Dynamic T Eruption?',
 '脅威の太鼓腹魔人': 'The Terrifying Big-Bellied Demon',
 '殺戮グリーンベレー': 'The Killing Green Beret',
 '焼きつくせバーニングハート': 'Burn It All, Burning Heart',
 '振りかざせ、炎の刃': 'Raise High the Flaming Blade',
 '弾丸戦士': 'The Bullet Warrior',
 '鉄人、その魂を熱く燃やし': 'Iron Man, Burning His Soul Hot',
 '恐れ知らずの斧爆弾': 'The Fearless Axe Bomb',
 '箱舟を守護する番人': 'The Guardian of the Ark',
 '箱舟が誇る重戦車': 'The Heavy Tank the Ark Is Proud Of',
 'プロレスファンタジー': 'Pro-Wrestling Fantasy',
 '東北に夢を運べ': 'Carry Dreams to Tohoku', '黒船来襲': 'The Black Ships Attack',
 '魔界から送り込まれた刺客': 'The Assassin Sent from Makai',
 '魔界の番長こと': 'The Boss of Makai', '理不尽大王': 'The King of Unreason',
 '黒のカリスマ': 'The Black Charisma', '新日本の総帥': "NJPW's Supreme Commander",
 '極楽浄土': 'Paradise', '新日本の未来を背負え': "Carry NJPW's Future",
 '脅威のパワフルモンスター': 'The Terrifying Powerful Monster',
 '流星に願いをかけろ': 'Make a Wish on a Shooting Star',
 'ノアジュニア最強宣言': 'NOAH Junior Strongest Declaration',
 'ジュニアのカリスマ': 'The Junior Charisma',
 '伝説の虎戦士': 'The Legendary Tiger Warrior',
 '揺るがぬ心、不動心': 'Unshakable Heart, Immovable Mind',
 'ハイブリッドの風が吹き荒れる': 'The Hybrid Wind Rages',
 'ＲＯＷＤＹ': 'ROWDY', 'ぬるま湯とは言わせない': "Don't Call It Lukewarm",
 '王道番長': "The King's Road Boss", '激辛爆弾': 'The Extra-Spicy Bomb',
 'その魂を熱く燃やし': 'Burning That Soul Hot',
 'その一足が大地を揺るがす': 'Each Step Shakes the Earth',
 'アンダー３０に未来を託せ': 'Entrust the Future to the Under-30s',
 '喧嘩上等': 'Bring It On', '夏に舞え、青春バタフライ': 'Dance in Summer, Youth Butterfly',
 'オレンジクラッシュ': 'Orange Crush', '柔の道は、男の道': "The Gentle Way Is the Man's Way",
 '策略仮面': 'The Scheming Mask',
 'カボチャ星、王道州より': "From Planet Pumpkin, King's Road State",
 '全てを凌駕する超人類': 'The Superhuman Who Surpasses All',
 '極寒の皇帝': 'The Freezing Emperor',
 '冷徹なるプロレスハンター': 'The Cold-Blooded Pro-Wrestling Hunter',
 '一族の誇りを背負い': 'Carrying the Pride of the Family',
 'ハイブリッドマスター': 'Hybrid Master',
 '世界を征した寝技師': 'The Grappler Who Conquered the World',
 '海を越え超人がやってきた': 'The Superman Has Crossed the Sea',
 '驚異のＩＱレスラー': 'The Amazing IQ Wrestler',
 'サムライ魂を胸に、やってやるって': "With Samurai Spirit in My Heart, I'll Do It",
 'ノアの盟主、その魂を握りしめ': "NOAH's Leader, Clutching That Soul",
 'ノーザンライト革命児': 'The Northern Light Revolutionary',
 '２１世紀の超獣': '21st Century Super Beast',
 '天下統一、ゼロワン道中記': 'Unify the World, ZERO-ONE Travelogue',
 # cat 22 named themes (bases; paren variants handled generically)
 'ＤＲＡＧＯＮ\u3000ＳＵＰＬＥＸ': 'DRAGON SUPLEX', 'ｎＷｏクラッシュ': 'nWo Crush',
 'ＭＩＳＳＩＯＮ\u3000ＢＬＯＷ': 'MISSION BLOW', 'テンザン〜時空〜': 'TENZAN ~Jiku~',
 '怒りの獣神': 'Angry Jyushin', 'スパルタンＸ': 'Spartan X', 'ＢＬＡＺＩＮ': 'BLAZIN',
 'ＳＴＥＲＮＮＥＳＳ': 'STERNNESS', 'ＴＲＡＮＳ\u3000ＭＡＧＩＣ': 'TRANS MAGIC',
 'ＭＵＴＡ': 'MUTA', 'Ｈｏｌｙ\u3000Ｗａｒ\u3000２１': 'Holy War 21',
 'ＲＵＳＨ！！': 'RUSH!!', '爆勝宣言': 'Bakusho Declaration',
 '前奏〜爆勝宣言': 'Prelude ~ Bakusho Declaration',
 'ＢＥＬＩＥＶＥ\u3000Ｓ‐ＲＯＡＤ': 'BELIEVE S-ROAD', 'パワーホール': 'Power Hall',
 'ＴＨＥ\u3000ＷＯＲＬＤ': 'THE WORLD', 'ＴＨＵＮＤＥＲ\u3000ＳＴＯＲＭ': 'THUNDER STORM',
 'Ｄ−ＰＯＷＥＲ': 'D-POWER', 'ＵＷＦメインテーマ': 'UWF Main Theme',
 'ＦＬＡＭＥ\u3000ＯＦ\u3000ＭＩＮＤ': 'FLAME OF MIND',
 # cat 23/24 entrance narration lines
 'さぁ、１＋１が３にも４にもなる好タッグ、今日も阿吽の呼吸を見せつけていくのでありましょうか':
  'Now, a great tag team where 1+1 becomes 3 or 4 — will they show their perfect harmony again today?',
 'さぁ、魅力的なユニットが姿を現しました。館内のファンも大声援を送っております':
  'Now, an exciting unit has appeared. The fans in the arena are cheering loudly.',
 'さぁ、タッグの頂点を目指して手を組んだ男達。今入ってまいりました':
  'Now, the men who joined forces aiming for the top of the tag division. They are entering now.',
 'さぁ、ガッチリ手を組んだこの男達。果たしてどんな戦いを見せるのでありましょうか':
  'Now, these men have joined forces tight. What kind of fight will they show us?',
 'さぁ、強烈なユニットが結成されました。その姿をいま現します。':
  'Now, a powerful unit has been formed. They appear before us now.',
 'さぁ、強力なタッグが結成されました。いま二つの魂が一つになってまいります':
  'Now, a strong tag team has been formed. Two souls are becoming one.',
 'さぁ、プロレス界の至宝、こんじきに輝くＩＷＧＰベルトを腰に今チャンピオンが入場してまいります':
  'Now, the champion enters, wearing the golden IWGP belt, the treasure of pro-wrestling.',
 'さぁ、その腰に輝くは伝説のＮＷＦ。ＮＷＦの新たな歴史はこの男が刻んでまいります':
  'Now, shining at his waist is the legendary NWF. This man will carve a new history for the NWF.',
 '腰に巻かれるベルトとともに、今二つの魂をひとつにして、チャンピオンチームが入ってまいりました':
  'With their belts around their waists, two souls as one, the champion team has entered.',
 'さぁ、ジュニアの頂点の証でありますこのベルトを腰に、今チャンピオンが入ってまいります':
  'Now, the champion enters, wearing this belt, the proof of being at the top of the juniors.',
 '通常の入場実況を再生': 'Play normal entrance commentary',
 'グローバルオナードクラウン。世界規模の崇高なる王者が、ＧＨＣのベルトを腰に入場してまいります':
  'Global Honored Crown. The noble champion of the world enters, wearing the GHC belt.',
 'ＰＷＦ、インター、ＵＮ、この三本のベルトを持つ王者、三冠ヘビー級チャンピオンが今入ってまいりました':
  'The champion holding all three belts — PWF, Inter, and UN — the Triple Crown Heavyweight Champion has entered.',
 '問答無用の天下一王者、いまチャンピオンが堂々の入場であります':
  'The undisputed Tenkaichi champion now makes a grand entrance.',
 'ＷＭＧワールド・マグマ・ザ・グレーテスト、プロレス界のド真ん中を突き進む王者が入場してまいります':
  'WMG — World Magma the Greatest — the champion charging down the dead center of pro-wrestling enters now.',
}

# ---------------------------------------------------------------- terms
# Costume/enum vocabulary for longest-match segmentation. Compounds are
# built from these atoms; whole compounds listed here win over atoms.
TERM = {
 # garments
 'ロングタイツ': 'Long Tights', 'タイツ': 'Tights', 'スパッツ': 'Spats',
 'ハーフ': 'Half Pants', 'タンクトップ': 'Tank Top', 'Ｔシャツ': 'T-Shirt',
 'シャツ': 'Shirt', 'ジャージ': 'Jersey', 'ガウン': 'Gown', 'ボディ': 'Body',
 'ボディー': 'Body', 'ペイント': 'Paint', 'タトゥー': 'Tattoo',
 'リストバンド': 'Wristband', 'リスト': 'Wristband', 'グローブ': 'Gloves',
 'シューズ': 'Shoes', 'ブーツ': 'Boots', 'レガースニー': 'Leggings Knee',
 'レガース': 'Leggings', 'ニーパット': 'Knee Pad', 'ニーパッド': 'Knee Pad',
 'サポーター': 'Supporter', 'ズボン': 'Pants', 'パンタロン': 'Pantalon',
 'もんぺ': 'Monpe', 'ジーンズ': 'Jeans', 'ジャンパー': 'Jumper',
 'ジャン': 'Jacket', '羽織': 'Haori', 'チョッキ': 'Vest', 'マント': 'Mantle',
 'スーツ': 'Suit', 'コスチューム': 'Costume', 'トランクス': 'Trunks',
 'キルト': 'Kilt', '胴着': 'Dogi', 'はかま': 'Hakama', '着流し': 'Kimono',
 'トップ': 'Top', '着': 'Wear', '手': 'Hand', '足': 'Foot', '胸': 'Chest',
 '肘': 'Elbow', '腰': 'Hips', '膝': 'Knee', 'パッド': 'Pad', 'バンド': 'Band',
 'テーピング': 'Taping', 'ジャンプスーツ': 'Jumpsuit', '手袋': 'Gloves',
 '足袋': 'Tabi', 'パンツ': 'Pants', 'ワンショルダー': 'One-Shoulder',
 'ショルダー': 'Shoulder', '腰巻': 'Waist Wrap', 'スカジャン': 'Sukajan',
 'スタジャン': 'Stadium Jacket', '服': 'Suit', 'レッグウォーマー': 'Leg Warmers',
 'パワーショルダー': 'Power Shoulder', 'パワー': 'Power',
 # descriptors / modifiers
 'ノーマル': 'Normal', '無地': 'Plain', 'ライン': 'Line', 'ロング': 'Long',
 'ショート': 'Short', 'ミドル': 'Middle', 'ラバー': 'Rubber', 'ゼブラ': 'Zebra',
 'ファイヤー': 'Fire', '星': 'Star', '豹柄': 'Leopard', '花柄': 'Floral',
 'ギザギザ': 'Zigzag', '三角': 'Triangle', '横ライン': 'Side Line',
 '縦ライン': 'Vertical Line', 'ヘソ': 'Navel', 'ハイレグ': 'High-Leg',
 'ベルト': 'Belt', 'まわし': 'Mawashi', 'ハンマー': 'Hammer',
 'イニシャル': 'Initial', '目玉': 'Eyeball', '鬼': 'Demon',
 'ヒラヒラ': 'Frilly', '星条旗': 'Stars and Stripes', 'アマレス': 'Amateur',
 'ロゴ入り': 'Logo', '稲妻': 'Lightning', '総合用': 'MMA', 'ニー': 'Knee',
 'テキサス': 'Texas', '靴下つき': 'With Socks', 'サンダー': 'Thunder',
 '悪魔': 'Demon', 'ソックス': 'Socks', 'スニーカー': 'Sneakers',
 'カンフー': 'Kung Fu', '超獣': 'Super Beast', 'デブ': 'Fat', '破れ': 'Torn',
 'あきなし': 'No-Opening', '背中あき': 'Open-Back', '縁取り': 'Trimmed',
 '爆破防護': 'Blast Protection', 'チビ': 'Small', '長袖': 'Long-Sleeve',
 '肩': 'Shoulder', 'レスラー': 'Wrestler', 'マッチョ': 'Macho',
 '格闘家': 'Fighter', '腹筋無し': 'No Abs',
 '薄い胸毛': 'Light Chest Hair', '濃い胸毛': 'Heavy Chest Hair',
 '胸毛': 'Chest Hair', '薄い': 'Light', '濃い': 'Heavy', '傷跡': 'Scar',
 '傷': 'Scar', '脱臼': 'Dislocation', 'お経': 'Sutra', 'アメリカン': 'American',
 '翼': 'Wing', 'ジーザス': 'Jesus', '和風': 'Japanese-Style', '獅子': 'Lion',
 'エンセン': 'Ensen', 'スコーピオ': 'Scorpio', '青柳': 'Aoyagi',
 '横井': 'Yokoi', '長南': 'Chonan', 'ハワード': 'Howard', 'アダモ': 'Adamo',
 'エルボー': 'Elbow', '腕': 'Arm', '腕毛': 'Arm Hair',
 'オープンフィンガー': 'Open-Finger', 'ボクシング': 'Boxing',
 'ニーブレス': 'Knee Brace', 'フード付き': 'Hooded', 'フサフサ': 'Fluffy',
 'フード': 'Hood', '胸開き': 'Open-Chest', 'エリ付き': 'Collared',
 'エリ寝かし': 'Flat-Collar', 'エリ寝': 'Flat-Collar', 'エリ立ち': 'Stand-Collar',
 '袖なし': 'Sleeveless', '毛皮': 'Fur', '迷彩': 'Camo', '英国': 'British',
 'ドクロ': 'Skull', 'キマラ': 'Kimara', 'レトロ': 'Retro', '邪悪': 'Evil',
 '革': 'Leather', '入場専用': 'Entrance-Only', '入場': 'Entrance',
 '裾入れ': 'Tucked', '忍者': 'Ninja', '柔道': 'Judo', '柔術': 'Jiu-Jitsu',
 '空手': 'Karate', 'ボロボロ': 'Ragged', '成仏': 'Nirvana',
 'ふわふわ': 'Fluffy', 'えぼす': 'Ebisu', '皮パン': 'Leather Pants',
 '日の丸': 'Hinomaru', '日本': 'Japan', 'プレート': 'Plate', 'ＡＶ': 'AV',
 'ＵＮＯ': 'UNO', '室田': 'Murota', 'スパイキー': 'Spiky', '高智': 'Takachi',
 'Ｊ': 'J', '２００': '200', 'キック': 'Kick', 'アシッド': 'Acid',
 'Ｕ': 'U', 'ドクター': 'Doctor', 'ギガンテス': 'Gigantes', 'ギガント': 'Gigant',
 'ギカンテス': 'Gigantes', '富豪': 'Fugo', 'スタミナ': 'Stamina',
 'ジェイムス': 'James', 'サファリ': 'Safari', 'アンダーソン': 'Anderson',
 '多聞': 'Tamon', '泉田': 'Izumida', '荒谷': 'Aratani', '保坂': 'Hosaka',
 'ノートン': 'Norton', '吉江': 'Yoshie', 'Ｄシルバー': 'D Silver',
 'クロニクル': 'Chronicle', 'ドルフィン': 'Dolphin', 'テンタ': 'Tenta',
 'Ｂ・タイガー': 'B. Tiger', 'Ｂタイガー': 'B. Tiger', 'ジェット': 'Jet',
 'カリー': 'Curry', 'サムライ': 'Samurai', 'セイバー': 'Saber',
 'ＲＯ＆Ｄ': 'RO&D', 'ジャマール': 'Jamal', 'ＩＳＡＭＩ': 'ISAMI',
 'エンペラーＳ': 'Emperor S', 'エンペラー': 'Emperor', 'ＢＡＴＴ': 'BATT',
 '太陽': 'Taiyo', 'モスマン': 'Mothman', 'グラジエーター': 'Gladiator',
 'ブキャナン': 'Buchanan', '大森': 'Omori', '中西': 'Nakanishi',
 '真壁': 'Makabe', '棚橋': 'Tanahashi', '柴田': 'Shibata', '中邑': 'Nakamura',
 'ライガー': 'Liger', '金本': 'Kanemoto', '成瀬': 'Naruse', '稔': 'Minoru',
 '小原': 'Obara', 'ウルフ': 'Wolf', '魔界': 'Makai', '村上': 'Murakami',
 '柳澤': 'Yanagisawa', 'バーネット': 'Barnett', '力皇': 'Rikio',
 '志賀': 'Shiga', '杉浦': 'Sugiura', 'ヨネ': 'Yone', 'ＩＺＵ': 'IZU',
 'バッファロー': 'Buffalo', '小島': 'Kojima', '奥村': 'Okumura',
 '土方': 'Hijikata', 'カシン': 'Kashin', '田中': 'Tanaka', '耕平': 'Kohei',
 '義人': 'Yoshihito', 'キングジョー': 'King Joe', '健介': 'Kensuke',
 '高山': 'Takayama', '中嶋': 'Nakajima', '船木': 'Funaki', 'みのる': 'Minoru',
 '近藤': 'Kondo', '菊田': 'Kikuta', '義生': 'Yoshio', '渋谷': 'Shibuya',
 '國奥': 'Kunioku', '謙吾': 'Kengo', '佐々木': 'Sasaki', '郷野': 'Gono',
 '田村': 'Tamura', 'パンクラス': 'Pancrase', '柏田': 'Kashiwada',
 '野川': 'Nogawa', '梶田': 'Kajita', 'ゆきぐに': 'Yukiguni', 'ミクロ': 'Micro',
 'ドッケン': 'Dokken', 'ケンタウロ': 'Centaur', 'ビースト': 'Beast',
 'ジルバ': 'Zilba', '天山': 'Tenzan', '安田': 'Yasuda', '平井': 'Hirai',
 '本間': 'Honma', 'コマンド': 'Commando', '蝶野': 'Chono', 'ヒロ': 'Hiro',
 'ＡＫＩＲＡ': 'AKIRA', '垣原': 'Kakihara', '後藤': 'Goto', '平田': 'Hirata',
 '矢野': 'Yano', '山崎': 'Yamazaki', 'キャット': 'Cat', '邪道': 'Jado',
 '長井': 'Nagai', 'バートン': 'Burton', '三沢': 'Misawa', '佐野': 'Sano',
 '金丸': 'Kanemaru', '菊地': 'Kikuchi', '川畑': 'Kawabata', 'ＫＥＮＴＡ': 'KENTA',
 '鼓太郎': 'Kotaro', '武藤': 'Muto', '川田': 'Kawada', '嵐': 'Arashi',
 'ハヤシ': 'Hayashi', 'ハインズ': 'Hines', 'ハシフ': 'Hashif',
 'Ｌｏｗｋｉ': 'Low Ki', '石井': 'Ishii', 'マサ': 'Masa', '保永': 'Yasunaga',
 '慶三': 'Keizo', 'アステカ': 'Azteca', 'リンピオ': 'Limpio', 'カニ': 'Kani',
 'ドゥガン': 'Dugan', 'ガンガン': 'Gangan', 'パンサー': 'Panther',
 'ムタ': 'Muta', '黒師': 'Kokushi', '孤士': 'Koshi', '橋本': 'Hashimoto',
 'ＳＨＯＧＵＮ': 'SHOGUN', '葛西': 'Kasai', 'デンジャー': 'Danger',
 'ミツル': 'Mitsuru', 'リベラ': 'Ribera', '南原': 'Nanbara',
 '小橋': 'Kobashi', '橋': 'Hashi', '大谷': 'Otani', '永田': 'Nagata',
 'コリノ': 'Corino', 'ワグナー': 'Wagner', 'シルバ': 'Silva',
 'アレビン': 'Arebin', 'ブライト': 'Bright', '星マーク': 'Star Mark',
 'ＵＳＡ': 'USA', 'ロトンド': 'Rotondo', 'ガファリ': 'Gafari', 'ヤン': 'Yan',
 'スミヤバザル': 'Sumiyabazar', '健想': 'Kenso',
 '和牛太': 'Wagyuta', '崔': 'Choi', '星川': 'Hoshikawa', '大久保': 'Okubo',
 '佐々木義人': 'Yoshihito Sasaki', '田中稔': 'Minoru Tanaka',
 '大和魂': 'Yamato Spirit', 'クレイジードッグス': 'Crazy Dogs',
 'キングオブザヒルズ': 'King of the Hills', 'ストロングスタイル': 'Strong Style',
 'ノア': 'NOAH', 'バーニング': 'Burning', 'ウェーブ': 'Wave',
 'スターネス': 'Starness', '男前': 'Handsome', '色男': 'Lady-Killer',
 'プロムナード': 'Promenade', '渕': 'Fuchi', '馳': 'Hase',
 'ぬるま湯': 'Lukewarm Water', 'ターメリック': 'Turmeric',
 'ＺＥＲＯ−ＯＮＥ': 'ZERO-ONE', 'ＷＪ': 'WJ', '長州': 'Choshu', 'ＷＡＲ': 'WAR',
 'レボリューション': 'Revolution', '恐れ知らず': 'Fearless',
 'Ｕ−ＦＩＬＥ': 'U-FILE', 'グラバカ': 'Grabaka', 'ＺＹＭＡ': 'ZYMA',
 'フライ': 'Fly', '美濃輪': 'Minowa', '裏ハラ': 'Urahara', '梨田': 'Nashida',
 '藤波': 'Fujinami', '秋山': 'Akiyama', '田上': 'Taue', '鶴田': 'Tsuruta',
 '天龍': 'Tenryu', '馬場': 'Baba', '西村': 'Nishimura', 'Ｔ２０００': 'T2000',
 'ヒライ': 'Hirai', '越中': 'Etchu', '司馬': 'Shiba', 'ヒクソン': 'Hickson',
 '丸藤': 'Marufuji', '彰俊': 'Akiyoshi', '新日': 'NJPW', '全日': 'AJPW',
 'ナガタロック': 'Nagata Lock', 'Ｇ−ｅｇｇｓ': 'G-eggs',
 '魔界倶楽部': 'Makai Club', '破悧魔王’Ｚ': "Harimao'Z",
 'パンサーキング': 'Panther King', '上山': 'Ueyama',
 'デンジャーベルト': 'Danger Belt', 'ベルト＆シャツ': 'Belt & Shirt',
 'レスラーＭ': 'Wrestler M', 'グッドシェイプ': 'Good Shape',
 'レスラーマッスル': 'Wrestler Muscle', 'レスラーマッチョ': 'Wrestler Macho',
 '格闘マッチョ': 'Fighting Macho', 'マッスル': 'Muscle',
 'ジャイアント': 'Giant', 'ダイナミック': 'Dynamic', 'クラッシャー': 'Crusher',
 'ストロング': 'Strong', 'テクニック': 'Technique', 'シューティング': 'Shoot',
 'ミステリアス': 'Mysterious', '骨法': 'Koppo', '総合系': 'MMA Style',
 'フリーファイター': 'Free Fighter', 'グラウンド': 'Ground', 'ルチャ': 'Lucha',
 'ケロ': 'Kero', '木原': 'Kihara', '仲田': 'Nakada', 'テング': 'Tengu',
 'ランマル': 'Ranmaru', '維震軍': 'Ishingun', 'Ｕ系': 'U-Style',
 'ＤＡＲＫ': 'DARK', 'ＢＬＡＤＥ': 'BLADE', '長袖リスト': 'Long-Sleeve Wristband',
 'ハーフリスト': 'Half Wristband', 'テーピングリスト': 'Taping Wristband',
 'ラインリスト': 'Line Wristband', 'ロングリストバンド': 'Long Wristband',
 'サポーター＆テーピング': 'Supporter & Taping',
 'ニーパット＆サポーター': 'Knee Pad & Supporter',
 'ニーブレス＆サポーター': 'Knee Brace & Supporter',
 'パッド＆サポーター': 'Pad & Supporter', 'ベルトボディ': 'Belt Body',
 'ベルト＆シャツボディ': 'Belt & Shirt Body', 'メインテーマ': 'Main Theme',
 'ＵＷＦ': 'UWF', 'ＧＨＣ': 'GHC', 'ＩＷＧＰ': 'IWGP', 'ＮＷＦ': 'NWF',
 'ヘビー': 'Heavyweight', 'レフリーシャツ': 'Referee Shirt',
 'レフリーズボン': 'Referee Pants', 'フォレスト': 'Forest',
 'ローガン': 'Logan', '谷津': 'Yatsu', '健三': 'Kenzo',
 '革靴': 'Leather Shoes', '外道': 'Gedo',
 # whole compounds (win over atoms)
 'ロングタイツ用ニーパット': 'Knee Pad for Long Tights',
 'ロングタイツ用レガースニー': 'Leggings Knee for Long Tights',
 'ロングタイツ用シューズ': 'Shoes for Long Tights',
 'ラインタイツ用シューズ': 'Shoes for Line Tights',
 '星タイツ用シューズ': 'Shoes for Star Tights',
 'ゼブラタイツ用シューズ': 'Shoes for Zebra Tights',
 'ショートレガースニー': 'Short Leggings Knee',
 'ロングニーパット': 'Long Knee Pad', 'ニーテーピング': 'Knee Taping',
 'ニーサポーター': 'Knee Supporter', 'テキサスサポーター': 'Texas Supporter',
 '大森サポーター': 'Omori Supporter', 'ロゴ入りニーパット': 'Logo Knee Pad',
 'ラインニーパット': 'Line Knee Pad', '稲妻ニーパット': 'Lightning Knee Pad',
 '総合用ニーパット': 'MMA Knee Pad', '靴下つきニーパット': 'Knee Pad with Socks',
 'ラインレガース': 'Line Leggings', '稲妻レガースシューズ': 'Lightning Leggings Shoes',
 'テング足袋': 'Tengu Tabi', 'カンフーシューズ': 'Kung Fu Shoes',
 'テキサスブーツ': 'Texas Boots', '超獣ブーツ': 'Super Beast Boots',
 'ファイヤーシューズ': 'Fire Shoes', 'サンダーシューズ': 'Thunder Shoes',
 '悪魔シューズ': 'Demon Shoes', 'ソックスシューズ': 'Socks Shoes',
 'ノーマルシューズ': 'Normal Shoes', 'ミドルシューズ': 'Middle Shoes',
 'ショートシューズ': 'Short Shoes', 'ラインシューズ': 'Line Shoes',
 'アマレスシューズ': 'Amateur Shoes', '多聞アマレスシューズ': 'Tamon Amateur Shoes',
 'ショートタイツ': 'Short Tights', 'ヘソタイツ': 'Navel Tights',
 'ハイレグタイツ': 'High-Leg Tights', 'ベルトタイツ': 'Belt Tights',
 'まわしタイツ': 'Mawashi Tights', '横ラインタイツ': 'Side Line Tights',
 '花柄タイツ': 'Floral Tights', 'ギザギザタイツ': 'Zigzag Tights',
 '三角タイツ': 'Triangle Tights', '星タイツ': 'Star Tights',
 '豹柄タイツ': 'Leopard Tights', 'ノーマルスパッツ': 'Normal Spats',
 'ラインスパッツ': 'Line Spats', 'ハンマースパッツ': 'Hammer Spats',
 'イニシャルスパッツ': 'Initial Spats', 'ラバースパッツ': 'Rubber Spats',
 '目玉スパッツ': 'Eyeball Spats', '鬼スパッツ': 'Demon Spats',
 'ロングスパッツ': 'Long Spats', '縦ラインスパッツ': 'Vertical Line Spats',
 'ヒラヒラスパッツ': 'Frilly Spats', '星条旗スパッツ': 'Stars and Stripes Spats',
 'ショートジーンズ': 'Short Jeans', 'ノーマルハーフ': 'Normal Half Pants',
 'ゼブラハーフ': 'Zebra Half Pants', 'ハーフジーンズ': 'Half Jeans',
 'ファイヤージーンズ': 'Fire Jeans', 'ノーマルロングタイツ': 'Normal Long Tights',
 'ラインロングタイツ': 'Line Long Tights', 'ファイヤーロングタイツ': 'Fire Long Tights',
 '星ロングタイツ': 'Star Long Tights', '豹柄ロングタイツ': 'Leopard Long Tights',
 'ゼブラロングタイツ': 'Zebra Long Tights', 'アマレスタイツ': 'Amateur Tights',
 'ラインワンショルダー': 'Line One-Shoulder', 'デブワンショルダー': 'Fat One-Shoulder',
 'デブラインワンショルダー': 'Fat Line One-Shoulder',
 '破れワンショルダー': 'Torn One-Shoulder',
 'ワンショルダー吉江': 'One-Shoulder Yoshie', 'ワンショルダー富豪': 'One-Shoulder Fugo',
 '無地タンクトップ': 'Plain Tank Top', 'あきなしタンクトップ': 'No-Opening Tank Top',
 '背中あきタンクトップ': 'Open-Back Tank Top',
 '縁取りタンクトップ': 'Trimmed Tank Top', 'ラインタンクトップ': 'Line Tank Top',
 '爆破防護服': 'Blast Protection Suit', '無地Ｔシャツ': 'Plain T-Shirt',
 'チビＴシャツ': 'Small T-Shirt', '長袖シャツ': 'Long-Sleeve Shirt',
 '肩サポーター': 'Shoulder Supporter', 'レスラーボディ': 'Wrestler Body',
 'デブボディ': 'Fat Body', 'ジャイアントボディ': 'Giant Body',
 'グッドシェイプボディ': 'Good Shape Body',
 'レスラーマッチョボディ': 'Wrestler Macho Body', '格闘家ボディ': 'Fighter Body',
 '格闘家ボディ腹筋無し': 'Fighter Body No Abs',
 '格闘家マッチョボディ': 'Fighter Macho Body',
 '薄い胸毛マッチョボディ': 'Light Chest Hair Macho Body',
 '濃い胸毛マッチョボディ': 'Heavy Chest Hair Macho Body',
 '濃い胸毛格闘マッチョボディ': 'Heavy Chest Hair Fighting Macho Body',
 'レスラーＭ胸': 'Wrestler M Chest',
 'レスラーＭグッドシェイプボディ': 'Wrestler M Good Shape Body',
 'レスラーＭレスラーボディ': 'Wrestler M Wrestler Body',
 'レスラーＭ薄い胸毛': 'Wrestler M Light Chest Hair',
 'レスラーＭ濃い胸毛': 'Wrestler M Heavy Chest Hair',
 'エンペラー胸': 'Emperor Chest', 'エンペラー薄い胸毛': 'Emperor Light Chest Hair',
 'エンペラー濃い胸毛': 'Emperor Heavy Chest Hair',
 '脱臼テーピング': 'Dislocation Taping', '星ペイント': 'Star Paint',
 'お経ペイント': 'Sutra Paint', 'ライガーペイント': 'Liger Paint',
 '黒師ペイント': 'Kokushi Paint', '孤士ペイント': 'Koshi Paint',
 'アメリカンタトゥー': 'American Tattoo', '翼タトゥー': 'Wing Tattoo',
 'ジーザスタトゥー': 'Jesus Tattoo', '和風タトゥー': 'Japanese-Style Tattoo',
 '獅子タトゥー': 'Lion Tattoo', '肩タトゥー': 'Shoulder Tattoo',
 '邪道タトゥー': 'Jado Tattoo', 'エンセンタトゥー': 'Ensen Tattoo',
 'スコーピオタトゥー': 'Scorpio Tattoo', '青柳タトゥー': 'Aoyagi Tattoo',
 '横井タトゥー': 'Yokoi Tattoo', '長南タトゥー': 'Chonan Tattoo',
 '葛西ボディー': 'Kasai Body', 'ハワードタトゥー': 'Howard Tattoo',
 'アダモボディー': 'Adamo Body', 'アダモタトゥー': 'Adamo Tattoo',
 'ギガンテスタトゥー': 'Gigantes Tattoo', 'ファイヤータトゥー': 'Fire Tattoo',
 'テンタタトゥー': 'Tenta Tattoo', 'ライガースーツ': 'Liger Suit',
 'パンサーキングスーツ': 'Panther King Suit', 'カニスーツ': 'Kani Suit',
 'ガンガンスーツ': 'Gangan Suit', 'えぼすスーツ': 'Ebisu Suit',
 'えぼすズボン': 'Ebisu Pants', '新日ジャージ': 'NJPW Jersey',
 'ノアジャージ': 'NOAH Jersey', '全日ジャージ': 'AJPW Jersey',
 '汎用ジャージ': 'Generic Jersey', 'ラインジャージ': 'Line Jersey',
 'ステイシージャージ': 'Stacy Jersey',
 '新日レフリーシャツ': 'NJPW Referee Shirt',
 '全日レフリーシャツ': 'AJPW Referee Shirt',
 'ノアレフリーシャツ': 'NOAH Referee Shirt',
 'パンクラスレフリーシャツ': 'Pancrase Referee Shirt',
 'ＺＥＲＯ−ＯＮＥレフリーシャツ': 'ZERO-ONE Referee Shirt',
 'ＷＪレフリーシャツ': 'WJ Referee Shirt',
 '新日レフリーズボン': 'NJPW Referee Pants',
 '全日レフリーズボン': 'AJPW Referee Pants',
 'ノアレフリーズボン': 'NOAH Referee Pants',
 'パンクラスレフリーズボン': 'Pancrase Referee Pants',
 'ＺＥＲＯ−ＯＮＥレフリーズボン': 'ZERO-ONE Referee Pants',
 '新日グローブ': 'NJPW Gloves', 'ＤＡＲＫグローブ': 'DARK Gloves',
 'ＢＬＡＤＥグローブ': 'BLADE Gloves', 'ジャマールグローブ': 'Jamal Gloves',
 'セイバーグローブ': 'Saber Gloves',
 'オープンフィンガーグローブ': 'Open-Finger Gloves',
 'ボクシンググローブ': 'Boxing Gloves', '忍者コスチューム': 'Ninja Costume',
 'テキサスコスチューム': 'Texas Costume', '柔道着': 'Judo Gi',
 '柔術着': 'Jiu-Jitsu Gi', '菊田柔術着': 'Kikuta Jiu-Jitsu Gi',
 '維震軍胴着': 'Ishingun Dogi', '青柳胴着': 'Aoyagi Dogi',
 '空手胴着': 'Karate Gi', 'ボロボロ着': 'Ragged Clothes',
 '侍はかま': 'Samurai Hakama', 'お経ズボン': 'Sutra Pants',
 '成仏ズボン': 'Nirvana Pants', 'ふわふわズボン': 'Fluffy Pants',
 'キックトランクス': 'Kick Trunks', 'アダモキルト': 'Adamo Kilt',
 '長南トランクス': 'Chonan Trunks', 'ジョンソントランクス': 'Johnson Trunks',
 '迷彩ズボン': 'Camo Pants', '邪道ジーンズ': 'Jado Jeans',
 'Ｔ２０００ズボン': 'T2000 Pants', 'Ｔ２０００ジャンプスーツ': 'T2000 Jumpsuit',
 '小原パンタロン': 'Obara Pantalon', '井上パンタロン': 'Inoue Pantalon',
 '竹村パンタロン': 'Takemura Pantalon', '丸藤パンタロン': 'Marufuji Pantalon',
 '彰俊パンタロン': 'Akiyoshi Pantalon', 'ムタズボン': 'Muta Pants',
 '黒師ズボン': 'Kokushi Pants', '孤士ズボン': 'Koshi Pants',
 '太陽パンタロン': 'Taiyo Pantalon', '橋本パンタロン': 'Hashimoto Pantalon',
 'ＳＨＯＧＵＮパンタロン': 'SHOGUN Pantalon', '葛西パンタロン': 'Kasai Pantalon',
 '中嶋パンタロン': 'Nakajima Pantalon', 'デンジャーパンタロン': 'Danger Pantalon',
 'ミツルパンタロン': 'Mitsuru Pantalon', 'リベラパンタロン': 'Ribera Pantalon',
 'パンサーパンタロン': 'Panther Pantalon', '南原パンタロン': 'Nanbara Pantalon',
 'ヤンパンタロン': 'Yan Pantalon', '井上もんぺ': 'Inoue Monpe',
 'カシンもんぺ': 'Kashin Monpe', 'テングもんぺ': 'Tengu Monpe',
 'ランマルもんぺ': 'Ranmaru Monpe', 'ケロ手': 'Kero Hand',
 '木原手': 'Kihara Hand', 'ケロ胸': 'Kero Chest', '木原胸': 'Kihara Chest',
 '仲田胸': 'Nakada Chest', 'ケロ肘': 'Kero Elbow', '木原肘': 'Kihara Elbow',
 '仲田肘': 'Nakada Elbow', 'ケロ腰': 'Kero Hips', '木原腰': 'Kihara Hips',
 '仲田腰': 'Nakada Hips', 'ケロ膝': 'Kero Knee', '木原膝': 'Kihara Knee',
 '仲田膝': 'Nakada Knee', 'ケロ足': 'Kero Foot', '木原足': 'Kihara Foot',
 '仲田足': 'Nakada Foot', 'エリ寝かしジャンパー': 'Flat-Collar Jumper',
 'フード付きガウン': 'Hooded Gown', 'フサフサガウン': 'Fluffy Gown',
 'パンサーマント': 'Panther Mantle', 'ライガーマント': 'Liger Mantle',
 '天山ガウン': 'Tenzan Gown', '袖なしガウン': 'Sleeveless Gown',
 'フード付き胸開きガウン': 'Hooded Open-Chest Gown',
 '黒師羽織': 'Kokushi Haori', 'エリ付きガウン': 'Collared Gown',
 '革ジャン': 'Leather Jacket', 'エリ立ちジャンパー': 'Stand-Collar Jumper',
 '入場Ｔシャツ': 'Entrance T-Shirt', '入場専用柔道着': 'Entrance-Only Judo Gi',
 '入場専用柔術着': 'Entrance-Only Jiu-Jitsu Gi',
 '入場専用維震軍胴着': 'Entrance-Only Ishingun Dogi',
 '入場専用梨田柔道着': 'Entrance-Only Nashida Judo Gi',
 '入場専用菊田柔術着': 'Entrance-Only Kikuta Jiu-Jitsu Gi',
 '無地エリ寝ジャンパー': 'Plain Flat-Collar Jumper',
 'エリ寝ジャンパー': 'Flat-Collar Jumper',
 'エリ立ちスタジャン': 'Stand-Collar Stadium Jacket',
 '無地革ジャン': 'Plain Leather Jacket', '邪悪革ジャン': 'Evil Leather Jacket',
 '無地ガウン': 'Plain Gown', '無地着流し': 'Plain Kimono',
 '無地フードガウン': 'Plain Hood Gown', '無地胸開きガウン': 'Plain Open-Chest Gown',
 '無地フード胸開きガウン': 'Plain Hooded Open-Chest Gown',
 '無地フサフサガウン': 'Plain Fluffy Gown', '無地チョッキ': 'Plain Vest',
 '迷彩チョッキ': 'Camo Vest', '毛皮チョッキ': 'Fur Vest',
 '英国チョッキ': 'British Vest', 'ドクロチョッキ': 'Skull Vest',
 '無地マント': 'Plain Mantle', '無地袖なしガウン': 'Plain Sleeveless Gown',
 '無地エリ付きガウン': 'Plain Collared Gown', 'キマラキルト': 'Kimara Kilt',
 '裸': 'Bare', '裸足': 'Barefoot', '足テーピング': 'Foot Taping',
 'アダモリスト': 'Adamo Wristband', 'アマレスガファリ': 'Amateur Gafari',
 'アマレスワグナー': 'Amateur Wagner', 'アマレスシルバ': 'Amateur Silva',
 'アマレスクロニクル': 'Amateur Chronicle', 'アマレスアレビン': 'Amateur Arebin',
 'アマレスブライト': 'Amateur Bright', 'アマレス星マーク': 'Amateur Star Mark',
 'アマレスＵＳＡ': 'Amateur USA', 'アマレスギガント': 'Amateur Gigant',
 'アマレスノートン': 'Amateur Norton', 'アマレス多聞': 'Amateur Tamon',
 'アマレス泉田': 'Amateur Izumida', 'アマレス荒谷': 'Amateur Aratani',
 'アマレス保坂': 'Amateur Hosaka', 'アマレスアンダーソン': 'Amateur Anderson',
 'アマレスサファリ': 'Amateur Safari', 'アマレススタミナ': 'Amateur Stamina',
 'アマレスジェイムス': 'Amateur James', 'アマレス吉江': 'Amateur Yoshie',
 'アマレスDシルバー': 'Amateur D Silver', 'アマレスロトンド': 'Amateur Rotondo',
 'サファリ\u3000': 'Safari', 'ＷＩＬＤⅡＴシャツ': 'WILD II T-Shirt',
 '汎用テーマ': 'Generic Theme', '汎用ジャージ': 'Generic Jersey',
 '汎用': 'Generic',
}

# ---------------------------------------------------------------- helpers
FW_DIGITS = str.maketrans('０１２３４５６７８９', '0123456789')
FW_ASCII = str.maketrans(
    'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９',
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')

def fw2hw(s):
    """Full-width ASCII/digits -> half-width; full-width space -> space."""
    return s.translate(FW_ASCII).replace('\u3000', ' ').replace('−', '-').replace('‐', '-')

def is_kanji(ch):
    return '\u4e00' <= ch <= '\u9fff'

def decode_hexdump(st):
    """'<0x...>' literal from the JSON dump -> real Japanese text."""
    if st.startswith('<0x') and st.endswith('>'):
        try:
            return bytes.fromhex(st[3:-1]).decode('cp932')
        except Exception:
            return None
    return st

def build_lookups():
    """Name lookup (Western order) + name-part dict (family/given fragments)."""
    r = json.load(open(os.path.join(WORK, 'data/koc2-roster-romanized.json')))
    lookup = {}
    for e in r['wrestlers']:
        ja, en, src = e['name_ja'], e['name_romaji'], e['source']
        if ja in FIX:
            en = FIX[ja]
        elif src == 'machine-pykakasi' and '\u3000' in ja:
            # machine output is family-first for kanji names -> flip to Western
            first = ja.split('\u3000', 1)[0]
            if any(is_kanji(c) for c in first):
                words = en.split()
                if len(words) >= 2:
                    en = ' '.join(words[1:] + words[:1])
        lookup[ja] = en
    for k, v in EXTRA_NAMES.items():
        lookup[k] = v
    # nospace variants (theme names drop the space: 藤波辰巳のテーマ)
    nospace = {}
    for k, v in list(lookup.items()):
        nk = k.replace('\u3000', '').replace(' ', '')
        nospace.setdefault(nk, v)
    # name parts: family/given fragments -> romaji (order-aware split)
    parts = {}
    for e in r['wrestlers']:
        ja = e['name_ja']
        en = lookup.get(ja, e['name_romaji'])
        if '\u3000' not in ja or '(' in en or 'w/' in en:
            continue
        fam, giv = ja.split('\u3000', 1)
        words = en.split()
        if len(words) < 2:
            continue
        # lookup is Western order: family = last word, given = rest
        parts.setdefault(fam, words[-1])
        parts.setdefault(giv, ' '.join(words[:-1]))
    for k, v in EXTRA_NAMES.items():
        if '\u3000' in k:
            fam, giv = k.split('\u3000', 1)
            words = v.split()
            if len(words) >= 2:
                parts.setdefault(fam, words[-1])
                parts.setdefault(giv, ' '.join(words[:-1]))
    # whole single-token names as parts too (Liger, Muta, ...)
    for k, v in lookup.items():
        if '\u3000' not in k and ' ' not in v and len(k) >= 2:
            parts.setdefault(k, v)
    return lookup, nospace, parts

LOOKUP, NOSPACE, PARTS = build_lookups()
SEG_KEYS = sorted(set(TERM) | set(PARTS), key=len, reverse=True)

def seg_translate(s):
    """Greedy longest-match segmentation. Returns English or None."""
    if not s:
        return ''
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in '　 ':
            i += 1
            continue
        if ch == '・':
            i += 1
            continue
        if ch == '＆':
            out.append('&')
            i += 1
            continue
        if ch in '０１２３４５６７８９0123456789':
            j = i
            while j < len(s) and s[j] in '０１２３４５６７８９0123456789':
                j += 1
            out.append(s[i:j].translate(FW_DIGITS))
            i = j
            continue
        if ch == '㌔':
            out.append('kg')
            i += 1
            continue
        if ch == '（':
            j = s.find('）', i)
            if j == -1:
                return None
            inner = s[i+1:j]
            p = PAREN.get(inner) or seg_translate(inner) or fw2hw(inner)
            out.append(f'({p})')
            i = j + 1
            continue
        matched = False
        for k in SEG_KEYS:
            if s.startswith(k, i):
                out.append(TERM.get(k, PARTS.get(k)))
                i += len(k)
                matched = True
                break
        if not matched:
            return None
    # join: digits attach with a space, '&' joins with spaces
    res = ''
    for tok in out:
        if tok == '&':
            res += ' &'
        elif res and not res.endswith(' '):
            res += ' ' + tok
        else:
            res += tok
    return res.strip()

def translate_name(st):
    """Name (+ optional trailing number / weight). Returns English or None."""
    # trailing weight: Name１５０㌔
    m = re.match(r'^(.*?)(\d+)\s*kg$', st)
    if m:
        base = translate_name(m.group(1))
        return f'{base} {m.group(2)}kg' if base else None
    m = re.match(r'^(.*?)([０-９0-9]+)㌔$', st)
    if m:
        base = translate_name(m.group(1))
        return f"{base} {m.group(2).translate(FW_DIGITS)}kg" if base else None
    # trailing number: Name１ / Name1 (but not names ending in a number legitimately)
    m = re.match(r'^(.*?)([０-９0-9]+)$', st)
    if m and m.group(1):
        base = translate_name(m.group(1))
        if base:
            return f"{base} {m.group(2).translate(FW_DIGITS)}"
    if st in LOOKUP:
        return LOOKUP[st]
    ns = st.replace('\u3000', '').replace(' ', '')
    if ns in NOSPACE:
        return NOSPACE[ns]
    return None

def translate(st):
    """Translate one physical string. Returns English or None (untranslated)."""
    if st == '':
        return None
    st = decode_hexdump(st)
    if st is None:
        return None
    if st in WHOLE:
        return WHOLE[st]
    # parenthetical suffix: Base（X） -> Base (X)
    m = re.match(r'^(.*?)（([^）]+)）$', st)
    if m:
        base, par = m.group(1), m.group(2)
        b = translate(base)
        p = PAREN.get(par) or seg_translate(par) or fw2hw(par)
        if b:
            return f'{b} ({p})'
    # quoted version suffix: Name“SUFFIX”
    m = re.match(r'^(.*?)“([^”]+)”$', st)
    if m:
        base = translate_name(m.group(1))
        suf = SUFFIX.get(m.group(2))
        if base and suf:
            return f'{base} ({suf})'
    # theme: Xのテーマ[（Y）][N]
    m = re.match(r'^(.*?)のテーマ(?:（([^）]+)）)?([０-９0-9]*)$', st)
    if m and m.group(1):
        name = translate_name(m.group(1))
        if name:
            out = f"{name}' Theme" if name.endswith('s') else f"{name}'s Theme"
        else:
            seg = seg_translate(m.group(1))
            if not seg:
                seg = None
            out = f'{seg} Theme' if seg else None
        if out:
            if m.group(3):
                out += f" {m.group(3).translate(FW_DIGITS)}"
            if m.group(2):
                p = PAREN.get(m.group(2)) or seg_translate(m.group(2)) or fw2hw(m.group(2))
                out += f' ({p})'
            return out
    # plain name
    name = translate_name(st)
    if name:
        return name
    # 用 construction: X用Y[N] -> Y for X N
    if '用' in st:
        left, right = st.rsplit('用', 1)
        num = ''
        mnum = re.match(r'^(.*?)([０-９0-9]+)$', right)
        if mnum:
            right, num = mnum.group(1), ' ' + mnum.group(2).translate(FW_DIGITS)
        l = translate(left) or seg_translate(left)
        r = translate(right) or seg_translate(right)
        if l and r:
            return f'{r} for {l}{num}'
    # segmented translation (costumes/enums)
    seg = seg_translate(st)
    if seg:
        return seg
    return None

def main():
    s = json.load(open(os.path.join(WORK, 'data/koc2-strings.json')))
    phys = json.load(open(os.path.join(WORK, 'work/strings-physical.json')))
    out = {}
    failed = []
    for k, st in phys.items():
        idx = int(k)
        if st == '':
            continue
        en = translate(st)
        if en is None:
            failed.append((idx, st))
        else:
            out[str(idx)] = en
    json.dump(out, open(os.path.join(WORK, 'work/translations-02010.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    with open(os.path.join(WORK, 'work/translation-review-02010.txt'), 'w', encoding='utf-8') as f:
        f.write(f'translated: {len(out)} / {len(phys)} physical strings\n')
        f.write(f'failed: {len(failed)}\n\n')
        for idx, st in failed:
            f.write(f'{idx}\t{st}\n')
    print(f'translated {len(out)}/{len(phys)}; failed {len(failed)}')
    for idx, st in failed[:30]:
        print(f'  FAIL {idx}: {st!r}')

if __name__ == '__main__':
    main()
