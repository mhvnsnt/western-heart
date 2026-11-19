#!/usr/bin/env python3
"""Romanize the 363 KoC2 roster names (Task 9).

Sources:
  - stage-bannon/assets/moves/koc2-roster.json (363 Japanese names)
  - Jerrold Ng KoC2 FAQ/Movelist v1.0 (GameFAQs), HEAD LIST section by chuchu33
    (https://gamefaqs.gamespot.com/ps2/921208-king-of-colosseum-ii/faqs/32818)
    -- authoritative English spellings for the roster heads; transcribed below.
  - pykakasi (Hepburn) for the machine pass.

Method: pykakasi romaji, normalized (long vowels collapsed, order-insensitive),
is matched against the FAQ head list. Where a FAQ name matches, the FAQ
spelling wins (it fixes kanji readings pykakasi gets wrong, e.g. Marufuji
Naomichi not Seidou, Mutoh not Muto, Jyushin not Jushin). Unmatched names keep
the machine romaji and are flagged for review.
"""
import json, re, os, unicodedata, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROSTER = os.environ.get('KOC2_ROSTER') or os.path.expanduser(
    '~/workspace/grok-declined-items/lane-koc2/stage-bannon/assets/moves/koc2-roster.json')

# FAQ HEAD LIST base names (version parentheticals stripped), transcribed from
# the Jerrold Ng FAQ, HEAD LIST section (NJPW / WJ / FREE / ORIGINALS / NOAH /
# AJPW / ZERO-ONE columns) plus the TEMPLATE MENU wrestler samples.
FAQ_NAMES = """Tatsumi Fujinami Masahiro Chono Yuji Nagata Manabu Nakanishi
Hiroyoshi Tenzan Tadao Yasuda Osamu Nishimura Yutaka Yoshie Shinya Makabe
Hiroshi Tanahashi Shinsuke Nakamura Blue Wolf Kantaro Hoshino Kazunari Murakami
Ryushi Yanagisawa Makai Mask 1 Makai Mask 2 Katsuyori Shibata Makai Mask 4
Mitsuya Nagai Makai Mask 5 Michiyoshi Ohara Tatsutoshi Gotoh Hiro Saito
Jyushin Thunder Liger Battle Liger El Samurai Koji Kanemoto AKIRA Akira Nogami
Minoru Tanaka Masayuki Naruse Masahito Kakihara Jado Gedo Wataru Inoue
Katsushi Takemura Toru Yano Ryusuke Taguchi Naofumi Yamamoto Hiroshi Nagao
Hirooki Gotoh Seiji Sakaguchi Kengo Kimura Osamu Kido Kazuo Yamazaki
Super Strong Machine Junji Hirata Kuniaki Kobayashi Scott Norton Josh Barnett
Mike Barton Black Cat Black Tiger Riki Choshu Tomohiro Ishii Takashi Uwano
Kuniyoshi Wada Masa Saito Norio Honaga Yoshihiro Takayama Genichiro Tenryu
Kensuke Sasaki Power Warrior Takao Omori Shiro Koshinaka Katsuhiko Nakajima
Kiyoshi Tamura Yoshiaki Yatsu Akebono Dragon Kid Masaaki Mochizuki Yoji Anjoh
MIKAMI Yuki Ishikawa Kintaro Kanemura Ebessan Kuishinbo Kamen Atsushi Onita
Katsuhisa Fujii Kazuyuki Fujita Minoru Fujita KEI Yamamiya Yoshiaki Fujiwara
Ryuji Yamakawa Norihisa Yamamoto Jinsei Shinzaki Hiromitsu Kanehara Katsumi Usuda
Takehiro Murahama Giant Baba Osamu Tachihikari Great Kabuki Akira Maeda
Sanshiro Takagi Masaaki Satake Kodoh Fuyuki Hayato Mach Sakurai Nobuhiko Takada
CIMA Heat Ryuki Ueyama Super Delfin GAMMA Jumbo Tsuruta Gran Naniwa
Hidehiko Yoshida Naoya Ogawa Hakushi Tarzan Goto Antonio Inoki Kaoru Uno
Great Sasuke Alexander Otsuka Tsuyoshi Kohsaka Tiger Mask Tiger Mask III
Tiger Mask IV Mister Pogo Daijiro Matsui Mr. Gannosuke Kenzo Suzuki Minoru Suzuki
Tetsuhiro Kuroda Mitsuyoshi Sato Hayabusa Dick Togo TAKA Michinoku Magnum TOKYO
Animal Warrior Hulk Hogan Abdullah The Butcher Vanderlei Silva Mike Tyson
Royce Gracie Volk Han Keiji Sakoda Gilbert Yvel Curry Man Carlos Newton
Heath Herring Juventud Guerrera Quinton Rampage Jackson Ken Shamrock Terry Funk
Terry Gordy Antonio Rodrigo Nogueira Goldberg Bob Sapp Gary Albright Gerard Gordeau
Jimmy Miller Andre The Giant Jason DeLucia Johnny Ace Stan Hansen Steve Williams
Vader Dynamite Kid Dan Severn Peter Aerts Shota Chochoshivli Ric Flair
Dan Henderson Donovan Morgan Hawk Warrior Rickson Gracie Nathan Jones Kimo
Matt Ghaffari Bison Smith Dory Funk Jr. Mike Modest Bruiser Brody Rick Steiner
Fritz Von Erich Brian Clark Brian Adams Mike Bernardo Gary Goodridge Renzo Gracie
Aleksandr Karelin Ernesto Hoost Jerome LeBanner Don Frye Bas Rutten Mark Hunt
Mark Coleman Mark Kerr Dos Caras Dos Caras Jr. Mil Mascaras Brock Lesnar
Tiger Jeet Singh Mirko Crocop Filipovic Mister Fred Eddie Everett Muhammad Ali
Ryan Gracie Andrei Kopylov Ricardo Arona Igor Vovchancyn Leonardo Spanky
Kevin Nash Fedor Emelianenko Renato Sobral Wild Pegasus Mas Oyama Chyna
Kamen Rider Mitsuharu Misawa Kenta Kobashi Akira Taue Jun Akiyama Yoshinari Ogawa
Takeshi Rikioh Takeshi Morishima Tamon Honda Masao Inoue Takuma Sano Akitoshi Saito
Jun Izumida IZU Daisuke Ikeda Kentaro Shiga Mohammed Yone Takashi Sugiura
Kishin Kawabata Masashi Aoyagi Tsuyoshi Kikuchi Yoshinobu Kanemaru Naomichi Marufuji
Makoto Hashi KENTA Kotaro Suzuki Satoru Asako Rusher Kimura Haruka Eigen
Mitsuo Momota Mighty Inoue Scorpio Richard Slinger Keiji Mutoh Great Muta
Kokushimusou Toshiaki Kawada Satoshi Kojima Great Koji Taiyo Kea Masanobu Fuchi
Hiroshi Hase Arashi Nobutaka Araya Kendo Kashin Shigeo Okumura Nobukazu Hirai
Tomoaki Honma Kazushi Miyamoto Kaz Hayashi Ryuji Hijikata Taichi Ishikari
Masayuki Kono Big John Tenta The Gladiator Gigantes George Hines Hideki Hosaka
D-Lo Brown Buchanan Jamal Shinya Hashimoto Hashif Khan SHOGUN Shinjiro Ohtani
Masato Tanaka Tatsuhito Takaiwa Naohiro Hoshikawa Kohei Sato Tengu Kaiser
Wataru Sakata Hirotaka Yokoi Kazuhiko Ogasawara Ryouji Sai Fugofugo Yumeji
Kuroge Wagyuta Jun Kasai Yoshihito Sasaki Shinsuke Z Yamagasa Fuyuki Takahashi
Tom Howard The Predator Steve Corino C.W. Anderson Samoa Joe King Adamo Low Ki
Vansack Acid Gran Hamada Yoshiaki Fujiwara Hulk Ogan Scott Steiner Kintaro Kanemura
Hulk Ogan""".split('\n')
# The block above is line-wrapped; names are multi-word, so keep a manual list.
FAQ_NAMES = [
    'Tatsumi Fujinami', 'Masahiro Chono', 'Yuji Nagata', 'Manabu Nakanishi',
    'Hiroyoshi Tenzan', 'Tadao Yasuda', 'Osamu Nishimura', 'Yutaka Yoshie',
    'Shinya Makabe', 'Hiroshi Tanahashi', 'Shinsuke Nakamura', 'Blue Wolf',
    'Kantaro Hoshino', 'Kazunari Murakami', 'Ryushi Yanagisawa', 'Makai Mask 1',
    'Makai Mask 2', 'Katsuyori Shibata', 'Makai Mask 4', 'Mitsuya Nagai',
    'Makai Mask 5', 'Michiyoshi Ohara', 'Tatsutoshi Gotoh', 'Hiro Saito',
    'Jyushin Thunder Liger', 'Battle Liger', 'El Samurai', 'Koji Kanemoto',
    'AKIRA', 'Akira Nogami', 'Minoru Tanaka', 'Masayuki Naruse',
    'Masahito Kakihara', 'Jado', 'Gedo', 'Wataru Inoue', 'Katsushi Takemura',
    'Toru Yano', 'Ryusuke Taguchi', 'Naofumi Yamamoto', 'Hiroshi Nagao',
    'Hirooki Gotoh', 'Seiji Sakaguchi', 'Kengo Kimura', 'Osamu Kido',
    'Kazuo Yamazaki', 'Super Strong Machine', 'Junji Hirata', 'Kuniaki Kobayashi',
    'Scott Norton', 'Josh Barnett', 'Mike Barton', 'Black Cat', 'Black Tiger',
    'Riki Choshu', 'Tomohiro Ishii', 'Takashi Uwano', 'Kuniyoshi Wada',
    'Masa Saito', 'Norio Honaga', 'Yoshihiro Takayama', 'Genichiro Tenryu',
    'Kensuke Sasaki', 'Power Warrior', 'Takao Omori', 'Shiro Koshinaka',
    'Katsuhiko Nakajima', 'Kiyoshi Tamura', 'Yoshiaki Yatsu', 'Akebono',
    'Dragon Kid', 'Masaaki Mochizuki', 'Yoji Anjoh', 'MIKAMI', 'Yuki Ishikawa',
    'Kintaro Kanemura', 'Ebessan', 'Kuishinbo Kamen', 'Atsushi Onita',
    'Katsuhisa Fujii', 'Kazuyuki Fujita', 'Minoru Fujita', 'KEI Yamamiya',
    'Yoshiaki Fujiwara', 'Ryuji Yamakawa', 'Norihisa Yamamoto', 'Jinsei Shinzaki',
    'Hiromitsu Kanehara', 'Katsumi Usuda', 'Takehiro Murahama', 'Giant Baba',
    'Osamu Tachihikari', 'Great Kabuki', 'Akira Maeda', 'Sanshiro Takagi',
    'Masaaki Satake', 'Kodoh Fuyuki', 'Hayato Mach Sakurai', 'Nobuhiko Takada',
    'CIMA', 'Heat', 'Ryuki Ueyama', 'Super Delfin', 'GAMMA', 'Jumbo Tsuruta',
    'Gran Naniwa', 'Hidehiko Yoshida', 'Naoya Ogawa', 'Hakushi', 'Tarzan Goto',
    'Antonio Inoki', 'Kaoru Uno', 'Great Sasuke', 'Alexander Otsuka',
    'Tsuyoshi Kohsaka', 'Tiger Mask', 'Tiger Mask III', 'Tiger Mask IV',
    'Mister Pogo', 'Daijiro Matsui', 'Mr. Gannosuke', 'Kenzo Suzuki',
    'Minoru Suzuki', 'Tetsuhiro Kuroda', 'Mitsuyoshi Sato', 'Hayabusa',
    'Dick Togo', 'TAKA Michinoku', 'Magnum TOKYO', 'Animal Warrior', 'Hulk Hogan',
    'Abdullah The Butcher', 'Vanderlei Silva', 'Mike Tyson', 'Royce Gracie',
    'Volk Han', 'Keiji Sakoda', 'Gilbert Yvel', 'Curry Man', 'Carlos Newton',
    'Heath Herring', 'Juventud Guerrera', 'Quinton Rampage Jackson',
    'Ken Shamrock', 'Terry Funk', 'Terry Gordy', 'Antonio Rodrigo Nogueira',
    'Goldberg', 'Bob Sapp', 'Gary Albright', 'Gerard Gordeau', 'Jimmy Miller',
    'Andre The Giant', 'Jason DeLucia', 'Johnny Ace', 'Stan Hansen',
    'Steve Williams', 'Vader', 'Dynamite Kid', 'Dan Severn', 'Peter Aerts',
    'Shota Chochoshivli', 'Ric Flair', 'Dan Henderson', 'Donovan Morgan',
    'Hawk Warrior', 'Rickson Gracie', 'Nathan Jones', 'Kimo', 'Matt Ghaffari',
    'Bison Smith', 'Dory Funk Jr.', 'Mike Modest', 'Bruiser Brody', 'Rick Steiner',
    'Fritz Von Erich', 'Brian Clark', 'Brian Adams', 'Mike Bernardo',
    'Gary Goodridge', 'Renzo Gracie', 'Aleksandr Karelin', 'Ernesto Hoost',
    'Jerome LeBanner', 'Don Frye', 'Bas Rutten', 'Mark Hunt', 'Mark Coleman',
    'Mark Kerr', 'Dos Caras', 'Dos Caras Jr.', 'Mil Mascaras', 'Brock Lesnar',
    'Tiger Jeet Singh', 'Mirko Crocop Filipovic', 'Mister Fred', 'Eddie Everett',
    'Muhammad Ali', 'Ryan Gracie', 'Andrei Kopylov', 'Ricardo Arona',
    'Igor Vovchancyn', 'Leonardo Spanky', 'Kevin Nash', 'Fedor Emelianenko',
    'Renato Sobral', 'Wild Pegasus', 'Mas Oyama', 'Chyna', 'Kamen Rider',
    'Mitsuharu Misawa', 'Kenta Kobashi', 'Akira Taue', 'Jun Akiyama',
    'Yoshinari Ogawa', 'Takeshi Rikioh', 'Takeshi Morishima', 'Tamon Honda',
    'Masao Inoue', 'Takuma Sano', 'Akitoshi Saito', 'Jun Izumida', 'IZU',
    'Daisuke Ikeda', 'Kentaro Shiga', 'Mohammed Yone', 'Takashi Sugiura',
    'Kishin Kawabata', 'Masashi Aoyagi', 'Tsuyoshi Kikuchi', 'Yoshinobu Kanemaru',
    'Naomichi Marufuji', 'Makoto Hashi', 'KENTA', 'Kotaro Suzuki', 'Satoru Asako',
    'Rusher Kimura', 'Haruka Eigen', 'Mitsuo Momota', 'Mighty Inoue', 'Scorpio',
    'Richard Slinger', 'Keiji Mutoh', 'Great Muta', 'Kokushimusou',
    'Toshiaki Kawada', 'Satoshi Kojima', 'Great Koji', 'Taiyo Kea',
    'Masanobu Fuchi', 'Hiroshi Hase', 'Arashi', 'Nobutaka Araya', 'Kendo Kashin',
    'Shigeo Okumura', 'Nobukazu Hirai', 'Tomoaki Honma', 'Kazushi Miyamoto',
    'Kaz Hayashi', 'Ryuji Hijikata', 'Taichi Ishikari', 'Masayuki Kono',
    'Big John Tenta', 'The Gladiator', 'Gigantes', 'George Hines', 'Hideki Hosaka',
    'D-Lo Brown', 'Buchanan', 'Jamal', 'Shinya Hashimoto', 'Hashif Khan',
    'SHOGUN', 'Shinjiro Ohtani', 'Masato Tanaka', 'Tatsuhito Takaiwa',
    'Naohiro Hoshikawa', 'Kohei Sato', 'Tengu Kaiser', 'Wataru Sakata',
    'Hirotaka Yokoi', 'Kazuhiko Ogasawara', 'Ryouji Sai', 'Fugofugo Yumeji',
    'Kuroge Wagyuta', 'Jun Kasai', 'Yoshihito Sasaki', 'Shinsuke Z Yamagasa',
    'Fuyuki Takahashi', 'Tom Howard', 'The Predator', 'Steve Corino',
    'C.W. Anderson', 'Samoa Joe', 'King Adamo', 'Low Ki', 'Vansack Acid',
    'Gran Hamada', 'Scott Steiner', 'Hulk Ogan',
]

VERSION_WORDS = {
    'スキン': 'Skin', '短髪': 'Short Hair', '長髪': 'Long Hair',
    'レトロ': 'Retro', 'ジェイソン': 'Jason', '金髪': 'Blond',
    'アフロ': 'Afro', 'オレンジ': 'Orange', '黄色': 'Yellow',
}

# Katakana loanwords -> the English word the FAQ uses. pykakasi gives phonetic
# readings (gureeto, buruu); the FAQ gives the English spelling (Great, Blue).
# Applied as substring matches for words of 2+ kana; 'ザ' (The) is whole-token
# only, because it occurs inside other words (クラウザー, カイザー).
LOANWORDS = {
    'グレート': 'Great', 'ブルー': 'Blue', 'スーパー': 'Super',
    'マスク': 'Mask', 'タイガー': 'Tiger', 'ドラゴン': 'Dragon',
    'サンダー': 'Thunder', 'ライガー': 'Liger', 'ミスター': 'Mister',
    'ミスタ': 'Mister', 'ザ': 'The', 'キング': 'King', 'ジャイアント': 'Giant',
    'ブラック': 'Black', 'ホワイト': 'White', 'レッド': 'Red',
    'ゴールド': 'Gold', 'シルバー': 'Silver', 'ダイナマイト': 'Dynamite',
    'キッド': 'Kid', 'ジュニア': 'Jr.', 'シニア': 'Sr.',
    'マシン': 'Machine', 'ストロング': 'Strong', 'バトル': 'Battle',
    'エル': 'El', 'サムライ': 'Samurai', 'パワー': 'Power',
    'ウォリアー': 'Warrior', 'ホーク': 'Hawk', 'アニマル': 'Animal',
    'デビル': 'Devil', 'エンジェル': 'Angel', 'モンスター': 'Monster',
    'ビッグ': 'Big', 'リトル': 'Little', 'ミドル': 'Middle',
    'ドクター': 'Dr.', 'パンサー': 'Panther', 'ウイニング': 'Winning',
    'アステカ': 'Azteca', 'カイザー': 'Kaiser', 'ジェット': 'Jet',
    'セイバー': 'Saber', 'デルタ': 'Delta', 'ジョー': 'Joe',
    'スター': 'Star', 'バイソン': 'Bison', 'ダイナミック': 'Dynamic',
    'チーター': 'Cheetah', 'ジェネラル': 'General', 'ボンバー': 'Bomber',
    'スモール': 'Small', 'スタミナ': 'Stamina', 'ゴールデン': 'Golden',
    'ハンマー': 'Hammer', 'アイアン': 'Iron', 'ブラスター': 'Blaster',
    'アックス': 'Axe', 'スティール': 'Steel', 'スコーピオ': 'Scorpio',
    'ジョージ': 'George', 'マスター': 'Master', 'ベア': 'Bear', 'ベアー': 'Bear',
    'ワイリー': 'Wiley', 'マイク': 'Mike', 'マイティ': 'Mighty',
    'ラッシャー': 'Rusher', 'シューズ': 'Shoes', 'ビクトリー': 'Victory',
    'ハンター': 'Hunter', 'ヘラクレス': 'Hercules', 'サクソン': 'Saxon',
    'グラジエーター': 'Gladiator', 'ミステリアス': 'Mysterious',
    'ヒューストン': 'Houston', 'カルロス': 'Carlos', 'ウォルフ': 'Wolf',
    'アブドル': 'Abdul', 'デンジャー': 'Danger', 'エドワード': 'Edward',
    'キース': 'Keith', 'ケリー': 'Kelly', 'テキサン': 'Texan', 'ボギー': 'Bogey',
    'ケンタウロ': 'Centaur', 'サム': 'Sam', 'ポップ': 'Pop', 'ジョン': 'John',
    'ピース': 'Peace', 'ジャクソン': 'Jackson', 'フレージア': 'Freesia',
    'スティル': 'Still', 'ジェイムス': 'James', 'スティーブ': 'Steve',
    'ディック': 'Dick', 'スレンダー': 'Slender', 'ブラウン': 'Brown',
    'ディー': 'D', 'ロウ': 'Lo', 'トミー': 'Tommy', 'アンダーソン': 'Anderson',
    'ローガン': 'Logan', 'ナイト': 'Night', 'ニクソン': 'Nixon',
    'ステイシー': 'Stacy', 'ライアン': 'Ryan', 'ヴォイス': 'Voice',
    'ハイチ': 'Haiti', 'ハリー': 'Harry', 'ハンク': 'Hank', 'フォレスト': 'Forest',
    'バット': 'Bat', 'サファリ': 'Safari', 'バッファロー': 'Buffalo',
    'ルイス': 'Lewis', 'バード': 'Bird', 'ブル': 'Bull', 'ブランチ': 'Branch',
    'ノルディック': 'Nordic', 'ブリッツ': 'Blitz', 'フォン': 'Von',
    'エルリック': 'Elric', 'ウルフ': 'Wolf', 'ブレンダン': 'Brendan',
    'クランク': 'Crank', 'ダイモス': 'Deimos', 'ブレード': 'Blade',
    'ゲルハルト': 'Gerhardt', 'ベイビー': 'Baby', 'バッド': 'Bad',
    'エッジ': 'Edge', 'シュトゥルム': 'Sturm', 'ホーネット': 'Hornet',
    'ゴースト': 'Ghost', 'ボス': 'Boss', 'クライ': 'Cry', 'ポール': 'Paul',
    'サバンナ': 'Savannah', 'オールマン': 'Allman', 'マスカラ': 'Mascara',
    'イーグル': 'Eagle', 'コンドル': 'Condor', 'マッスル': 'Muscle',
    'マッド': 'Mad', 'ミクロ': 'Micro', 'プロポリス': 'Propolis',
    'ミステリー': 'Mystery', 'マン': 'Man', 'ライオン': 'Lion',
    'ライダー': 'Rider', 'リック': 'Rick', 'スパイキー': 'Spiky',
    'ロシアン': 'Russian', 'エンペラー': 'Emperor', 'ピョートル': 'Pyotr',
    'ロナウド': 'Ronaldo', 'ワイルド': 'Wild', 'ファントム': 'Phantom',
    'パイソン': 'Python', 'アシッド': 'Acid', 'カリー': 'Curry',
    'ボルドー': 'Bordeaux', 'ジミー': 'Jimmy', 'ミラン': 'Milan',
    'グラン': 'Gran', 'クリントン': 'Clinton', 'ジョンソン': 'Johnson',
    'ドゥガン': 'Dugan', 'ドルフィン': 'Dolphin', 'ジム': 'Jim',
    'ネイマン': 'Neiman', 'カール': 'Carl', 'ヘッド': 'Head',
}

# Explicit overrides for names the rules get wrong (gimmick versions of known
# wrestlers; FAQ spellings confirmed against the HEAD LIST).
OVERRIDES = {
    'チャップス丸藤　正道１': 'Naomichi Marufuji (Chaps version 1)',
    'チャップス丸藤　正道２': 'Naomichi Marufuji (Chaps version 2)',
    'ツノ天山　広吉': 'Hiroyoshi Tenzan (Tsuno Ver.)',
    'カサ黒師無双': 'Kokushimusou w/ Hat',
    'ハシフ・カーン帽子': 'Hashif Khan w/ Headdress',
    '武藤　敬司': 'Keiji Mutoh',
    '後藤　達俊': 'Tatsutoshi Gotoh',
    '後藤　洋央紀': 'Hirooki Gotoh',
    '高山　善廣': 'Yoshihiro Takayama',
    '高岩　竜一': 'Tatsuhito Takaiwa',
    '越中　詩郎': 'Shiro Koshinaka',
    '田中　将斗': 'Masato Tanaka',
    'リチャード・スリンガー': 'Richard Slinger',
    '井上　亘': 'Wataru Inoue',
    '井上　亘マスク': 'Wataru Inoue Mask',
    '山宮　恵一郎': 'Keiichiro Yamamiya',
    '山笠Ｚ”信介': 'Shinsuke Z Yamagasa',
    '橋本　真也ハチマキ１': 'Shinya Hashimoto w/ Headband 1',
    '橋本　真也ハチマキ２': 'Shinya Hashimoto w/ Headband 2',
    '佐々木　義人': 'Yoshihito Sasaki',
    '保永　昇男': 'Norio Honaga',
    '廣戸　聡一': 'Soichi Hiroto',
    '女子レスラー': 'Female Wrestler',
    '宇宙人': 'Alien',
    'バンダナ佐々木　健介': 'Kensuke Sasaki w/ Bandana',
    '仮面小島　聡': 'Satoshi Kojima (w/ Mask)',
    '桜木“ジェット”旅人': 'Sakuragi "Jet" Tabibito',
    'Ｇ・Ｏ＝ブライト': 'G.O. Bright',
    '対ヘビー級用ライガー': 'Liger (Anti-Heavyweight Ver.)',
    'ムタズキン': 'Muta Head Cover',
    'ムタドクロズキン': 'Muta Head Cover (Skull)',
    'ムタメカズキン': 'Muta Head Cover (Mecha)',
    'ムタグレーズキン': 'Muta Head Cover (Grey)',
    'ムタスパイダーズキン': 'Muta Head Cover (Spider)',
    '外道': 'Gedo',
    '力皇　猛': 'Takeshi Rikioh',
    '土方　隆司': 'Ryuji Hijikata',
    '大谷　晋二郎': 'Shinjiro Ohtani',
    '小原　道由': 'Michiyoshi Ohara',
    '近藤　有己': 'Yuki Kondo',
    '鈴木　鼓太郎': 'Kotaro Suzuki',
    '馳　浩': 'Hiroshi Hase',
    '魔界１号': 'Makai Mask 1',
    '魔界２号': 'Makai Mask 2',
    '魔界４号': 'Makai Mask 4',
    '魔界５号': 'Makai Mask 5',
}

# Names the fuzzy matcher gets wrong (reviewed 2026-11-19): superficial
# similarity to a different FAQ wrestler. These stay machine romanization.
FUZZY_REJECT = {
    'エイジ・ナコタ', 'オオカミ', 'ケイン・ハーロック', 'ダイナミック・キッド',
    'ミスターフェイク', 'ムハンマド・ダリ', '侍', '田中　秀和', 'ＩＳＡＭＩ',
    'リカルド・マローナ', 'カリー・マスク', 'カルロス・ヒューストン',
    'ジェネラル・ボルドー', 'ジミー・ミラン', 'ジョン・ピース',
    'ディック・スレンダー', 'ブリッツ・フォン・エルリック', 'ホーネット・ゴースト',
    'マイク・アント', 'マスター・トーゴー',
}


def norm(s):
    """Lowercase alphanumeric squash for fuzzy matching."""
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    # collapse long vowels the way Hepburn-without-macrons does
    s = re.sub(r'ou', 'o', s)
    s = re.sub(r'oo', 'o', s)
    s = re.sub(r'uu', 'u', s)
    s = re.sub(r'aa', 'a', s)
    s = re.sub(r'ee', 'e', s)
    return re.sub(r'[^a-z0-9]', '', s)


def main():
    from pykakasi import kakasi
    kks = kakasi()

    def roma_raw(text):
        # NFKC first so full-width ASCII (Ｍｒ．, ＷＡＫＡ, Ｖｅｒ) behaves like
        # half-width for the boundary rules below.
        text = unicodedata.normalize('NFKC', text)
        # Insert spaces at script boundaries so mixed tokens (オッキー沖田,
        # ＷＡＫＡゆきぐに, Ｍｒ．芦屋) tokenize into separate words.
        text = re.sub(r'([ァ-ヴー])([一-鿿ぁ-ん])', r'\1 \2', text)
        text = re.sub(r'([一-鿿ぁ-ん])([ァ-ヴー])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z0-9.])([一-鿿ぁ-んァ-ヴー])', r'\1 \2', text)
        text = re.sub(r'([一-鿿ぁ-んァ-ヴー])([A-Za-z])', r'\1 \2', text)
        # Loanwords: replace katakana English words with the English spelling
        # (longest first), so pykakasi never sees them. 'ザ' is whole-token
        # only (it occurs inside クラウザー, カイザー, ...).
        for kata in sorted(LOANWORDS, key=len, reverse=True):
            if len(kata) < 2:
                continue
            text = text.replace(kata, ' ' + LOANWORDS[kata] + ' ')
        toks = re.split(r'([ 　・])', text)
        toks = [(' ' + LOANWORDS['ザ'] + ' ') if t == 'ザ' else t for t in toks]
        text = ''.join(toks)
        parts = []
        for r in kks.convert(text):
            o, h = r['orig'], r['hepburn']
            if o in ('・', '　', ' ', '･'):
                parts.append(' ')
            else:
                parts.append(h)
        s = ''.join(parts)
        s = s.replace('・', ' ').replace('　', ' ')
        # full-width digits / roman numerals / Ver
        s = unicodedata.normalize('NFKC', s)
        s = s.replace('Ⅲ', 'III').replace('Ⅳ', 'IV').replace('Ⅱ', 'II')
        return re.sub(r'\s+', ' ', s).strip()

    def roma_title(text):
        s = roma_raw(text)
        # Long-vowel collapse (standard no-macron Hepburn) -- ONLY on lowercase
        # romaji words pykakasi produced. Capitalized English loanwords must
        # not be touched ('Cheetah' -> 'Chetah', 'Steel' -> 'Stel').
        words = []
        for w in s.split(' '):
            if re.fullmatch(r'[a-z]+', w):
                w = re.sub(r'ou', 'o', w)
                w = re.sub(r'oo', 'o', w)
                w = re.sub(r'uu', 'u', w)
                w = re.sub(r'aa', 'a', w)
                w = re.sub(r'ee', 'e', w)
            words.append(w)
        s = ' '.join(words)
        # Title Case, preserving all-caps tokens (KENTA, IZU, CIMA...)
        out = []
        for w in s.split(' '):
            if w.isupper() and len(w) > 1:
                out.append(w)
            elif re.fullmatch(r'[ivxIVX]+', w):
                out.append(w.upper())
            else:
                out.append(w[:1].upper() + w[1:] if w else w)
        return ' '.join(out)

    def roma_version(v):
        v = unicodedata.normalize('NFKC', v)
        m = re.fullmatch(r'(.+?)Ver', v)
        if m:
            stem = m.group(1)
            if stem in VERSION_WORDS:
                return VERSION_WORDS[stem] + ' Ver'
            if re.fullmatch(r'[0-9]+', stem):
                return stem + ' Ver'
            return roma_title(stem) + ' Ver'
        return roma_title(v)

    d = json.load(open(ROSTER))
    wrestlers = d['wrestlers']
    # fix the 2 hex-escaped names (cp932)
    for e in wrestlers:
        m = re.fullmatch(r'<0x([0-9a-f]+)>', e['name'])
        if m:
            e['name'] = bytes.fromhex(m.group(1)).decode('cp932')

    # FAQ lookup: normalized full name -> FAQ spelling (also reversed 2-token
    # order, since Japanese names are Family-Given and the FAQ is Given-Family);
    # normalized last token -> FAQ names for family matching.
    faq_by_norm = {}
    faq_family = {}
    for f in FAQ_NAMES:
        faq_by_norm[norm(f)] = f
        toks = f.split()
        if len(toks) == 2:
            faq_by_norm[norm(toks[1] + ' ' + toks[0])] = f
        fam = norm(toks[-1])
        faq_family.setdefault(fam, []).append(f)

    # Roster family-name uniqueness (family match is only safe when the family
    # is unique in the roster too -- e.g. two different Wadas must not both
    # become 'Kuniyoshi Wada').
    roster_fam = collections.Counter()
    for e in wrestlers:
        if re.search(r'[ 　]', e['name']):
            fam = re.split(r'[ 　]', e['name'])[0]
            roster_fam[norm(roma_raw(fam))] += 1

    out = []
    stats = {'faq_full': 0, 'faq_family': 0, 'faq_fuzzy': 0, 'override': 0,
             'machine': 0}
    import difflib
    for e in wrestlers:
        ja = e['name']
        machine = roma_title(ja)
        # strip a trailing version suffix before matching, re-append after
        ver = ''
        vm = re.search(r'\sVer\s?([0-9]+)$', machine)
        if vm:
            ver = ' Ver ' + vm.group(1)
            machine = machine[:vm.start()]
        m_norm = norm(machine)
        name, source = machine, 'machine-pykakasi'
        if ja in OVERRIDES:
            name, source = OVERRIDES[ja], 'override'
            stats['override'] += 1
        elif m_norm in faq_by_norm:
            name, source = faq_by_norm[m_norm], 'faq-full'
            stats['faq_full'] += 1
        else:
            # Family match: ONLY for person names (Family[space]Given) whose
            # family is unique in both the FAQ list and the roster.
            fam_match = None
            if re.search(r'[ 　]', ja):
                fam_ja = re.split(r'[ 　]', ja)[0]
                fam_roma = norm(roma_raw(fam_ja))
                if (fam_roma in faq_family and len(faq_family[fam_roma]) == 1
                        and roster_fam.get(fam_roma, 0) == 1):
                    fam_match = faq_family[fam_roma][0]
            if fam_match:
                name, source = fam_match, 'faq-family'
                stats['faq_family'] += 1
            elif ja not in FUZZY_REJECT:
                # fuzzy pass: katakana phonetics (sukopio vs scorpio) defeat
                # exact matching; accept a close FAQ name only if it is
                # clearly the best (margin over runner-up).
                scored = sorted(
                    ((difflib.SequenceMatcher(None, m_norm, norm(f)).ratio(), f)
                     for f in FAQ_NAMES),
                    reverse=True)
                best_r, best = scored[0]
                second_r = scored[1][0] if len(scored) > 1 else 0.0
                if best_r >= 0.70 and best_r - second_r >= 0.08:
                    name, source = best, 'faq-fuzzy'
                    stats['faq_fuzzy'] += 1
                else:
                    stats['machine'] += 1
            else:
                stats['machine'] += 1
        if ver and source != 'override':
            name = name + ver
            machine = machine + ver
        versions = [{'ja': v, 'romaji': roma_version(v)} for v in e.get('versions', [])]
        out.append({'name_ja': ja, 'name_romaji': name, 'source': source,
                    'machine_romaji': machine, 'versions': versions})

    res = {
        'source': 'koc2-roster.json (363 names) + Jerrold Ng KoC2 FAQ HEAD LIST '
                  '(GameFAQs) + pykakasi machine pass',
        'counts': {'total': len(out), **stats},
        'wrestlers': out,
    }
    with open(os.path.join(HERE, 'koc2-roster-romanized.json'), 'w') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps(res['counts'], indent=1))
    print('\nFAQ-family overrides (machine reading differed):')
    n = 0
    for e in out:
        if e['source'] == 'faq-family' and norm(e['machine_romaji']) != norm(e['name_romaji']):
            print(f"  {e['name_ja']}: machine '{e['machine_romaji']}' -> FAQ '{e['name_romaji']}'")
            n += 1
            if n >= 30:
                break
    print('\nFAQ-fuzzy matches (review):')
    for e in out:
        if e['source'] == 'faq-fuzzy':
            print(f"  {e['name_ja']}: machine '{e['machine_romaji']}' -> FAQ '{e['name_romaji']}'")
    print(f"\nMachine-only names (no FAQ match): {stats['machine']}")
    for e in out:
        if e['source'] == 'machine-pykakasi':
            print(f"  {e['name_ja']} -> {e['name_romaji']}")


if __name__ == '__main__':
    main()
