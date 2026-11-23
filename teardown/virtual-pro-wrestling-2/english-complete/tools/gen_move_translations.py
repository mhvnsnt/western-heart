#!/usr/bin/env python3
"""gen_move_translations.py — build translations/0063.json .. 0069.json
and 006A.json from Japanese-text -> English maps. Each map entry is
applied to EVERY index holding that Japanese text (move names repeat
heavily across slots). For 0064 indices 415-417, Beta 3 blanked the
real names to "なしでＯＫ"; those three are matched against the CLEAN
text instead (see RESTORE).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from akitext_py import parse as akitext_parse

MAPS = {
'0063': {
'なしでＯＫ': 'None',
'片手ガード': 'One-Hand Guard',
'ぶっとびやられ': 'Blown-Away Reaction',
'キャッチ（パンチ）': 'Catch (Punch)',
'中段ガード': 'Mid Guard',
'キャッチされるも延髄斬り': 'Enzui-giri While Caught',
'しゃがみ避け・バック組み状態': 'Crouch Dodge - Back Grapple',
'ガード': 'Guard',
'フィニッシュ': 'Finish',
'すかして・バック組み状態': 'Dodge - Back Grapple',
'上段ガード': 'High Guard',
'胸板ヒットダウン': 'Chest Hit Down',
'キャッチスロー・パンチで返す': 'Catch Throw - Return with Punch',
'上段十字ガード': 'High Cross Guard',
'頭突きヒットダウン': 'Headbutt Hit Down',
'耐えてリバースヘッドバットダウン': 'Endure - Reverse Headbutt Down',
'ジャンピングハイキック': 'Jumping High Kick',
'キャッチスロー・キックで返す': 'Catch Throw - Return with Kick',
'逆転逆水平チョップ': 'Reversal Reverse Horizontal Chop',
'上段ヒットダウン': 'High Hit Down',
'首筋押さえ前のめりダウン': 'Neck-Hold Forward Fall Down',
'正面両手ガード': 'Front Two-Hand Guard',
'中段ヒットダウン': 'Mid Hit Down',
'両手ガード防御で立ち直り': 'Two-Hand Guard Defense Recovery',
'ココナッツクラッシュフィニッシュ': 'Coconut Crush Finish',
'耐えて・バック組み状態': 'Endure - Back Grapple',
'反撃ヘッドバット': 'Counter Headbutt',
'十字クロスガード': 'Cross Guard',
'腹部ヒットダウン': 'Stomach Hit Down',
'かがませ突っ込みニーリフト': 'Bent-Over Charging Knee Lift',
'返し': 'Reversal',
'右側頭部ヒットＫＯダウン': 'Right Head Hit KO Down',
'キャッチ小内刈り': 'Catch Kouchi-gari',
'アキレス腱固め': 'Achilles Lock',
'バックボディソバットダウン': 'Back Body Sobat Down',
'左側頭部ＫＯダウン': 'Left Head KO Down',
'右側頭部ＫＯダウン': 'Right Head KO Down',
'右側頭部ヒットダウン': 'Right Head Hit Down',
'しゃがみ避け・タックル': 'Crouch Dodge - Tackle',
'左側頭部ヒットダウン': 'Left Head Hit Down',
'ふりほどく': 'Shake Off',
'ふりたおし投げダウン': 'Shake-Down Throw Down',
'腕取りショルダーアームブリーカー': 'Arm-Grab Shoulder Arm Breaker',
'上段やられダウン': 'High Reaction Down',
},
'0064': {
'片手ガード': 'One-Hand Guard',
'中段やられダウン': 'Mid Reaction Down',
'キャッチスロー・パンチで返す': 'Catch Throw - Return with Punch',
'ガード': 'Guard',
'フィニッシュ': 'Finish',
'返し': 'Reversal',
'中段ガード': 'Mid Guard',
'ひるみタックル倒し': 'Flinch Tackle Takedown',
'キャッチスロー・キックで返す': 'Catch Throw - Return with Kick',
'キャッチされるも延髄キック': 'Enzui Kick While Caught',
'キャッチ小内刈り': 'Catch Kouchi-gari',
'アキレス腱固め': 'Achilles Lock',
'ジャンピングニールキック「%204式」': 'Jumping Knee Kick (%204 Style)',
'右わきばらヒットＫＯダウン': 'Right Flank Hit KO Down',
'ジャンピングニールキック': 'Jumping Knee Kick',
'構えつき爆殺ミドルキック': 'Stance Explosive Middle Kick',
'アキレス腱固め＜左＞': 'Achilles Lock <Left>',
'正面両手ガード': 'Front Two-Hand Guard',
'横っ面ヒットダウン': 'Cheek Hit Down',
'逆襲張り手ダウン': 'Counter Slap Down',
'両手ガード': 'Two-Hand Guard',
'左側頭部ヒットダウン': 'Left Head Hit Down',
'しゃがみ避け・タックル': 'Crouch Dodge - Tackle',
'片足ガード': 'One-Leg Guard',
'左ももヒットＫＯダウン': 'Left Thigh Hit KO Down',
'キックガード': 'Kick Guard',
'大袈裟よけ': 'Exaggerated Dodge',
'下段ガード': 'Low Guard',
'ジャンピングハイキック': 'Jumping High Kick',
'しゃがみ避け': 'Crouch Dodge',
'ぶっとびダウン': 'Blown-Away Down',
'しゃがみ避け・バック組み状態': 'Crouch Dodge - Back Grapple',
'ボディガード': 'Body Guard',
'ボディヒットダウン': 'Body Hit Down',
'すかし避け': 'Dodge',
'キャッチ（キック）': 'Catch (Kick)',
'ジャンプ避け': 'Jump Dodge',
'キャッチ・キック': 'Catch Kick',
'肩投げ返し': 'Shoulder Throw Reversal',
'ラリアット返し': 'Lariat Reversal',
'みぞおちキック': 'Solar Plexus Kick',
'高速ネックブリーカー返し': 'High-Speed Neckbreaker Reversal',
'ひねりジャンプ避け': 'Twist Jump Dodge',
'どてっ腹キック': 'Belly Kick',
'リバース人工衛星シザース': 'Reverse Satellite Scissors',
'背中キック': 'Back Kick',
'切り返しエビ固め': 'Counter Shrimp Hold',
'投げ捨てパワーボム': 'Throw-Away Powerbomb',
'リバースパワースラム': 'Reverse Powerslam',
'スライディングすかし': 'Sliding Dodge',
'リバースフランケンホイップ': 'Reverse Franken Whip',
'リバースドロップキック': 'Reverse Dropkick',
'リバース各レスラーのバック組み技': 'Reverse Any Back Grapple',
'耐えてスタナー': 'Endure Stunner',
'まわってまわってバックドロップ': 'Spin-Around Backdrop',
'回転脱出': 'Spin Escape',
'モンキーフリップ': 'Monkey Flip',
'ニーリフト': 'Knee Lift',
'なしでＯＫ': 'None',
'エプロンから場外ひきずり降ろし': 'Drag Down from Apron to Outside',
'歴史的ボディスラム': 'Historic Bodyslam',
'投げられず突き放し': 'Not Thrown - Push Away',
'アンドレ・払い腰': 'Andre - Harai-goshi',
'投げられず突き飛ばし': 'Not Thrown - Shove',
'歴史的バックドロップ': 'Historic Backdrop',
'投げられずヒッププッシュ': 'Not Thrown - Hip Push',
'アンドレ・ジャーマンスープレックス': 'Andre - German Suplex',
},
'0065': {
'延髄斬り': 'Enzui-giri',
'ジャンピングドロップキック': 'Jumping Dropkick',
'キャッチ顔面落とし': 'Catch Face Drop',
'スウェイして下段受け流し': 'Sway Low Parry',
'背面エルボー＜ツープラ用＞': 'Back Elbow <2P>',
'逆水平チョップ＜ツープラ用＞': 'Reverse Horizontal Chop <2P>',
'プロレス前蹴り＜ツープラ用＞': 'Pro Wrestling Front Kick <2P>',
'ケンカキック＜ツープラ用＞': 'Street Fight Kick <2P>',
'中段サイドキック＜ツープラ用＞': 'Mid Side Kick <2P>',
'キチンシンク＜ツープラ用＞': 'Kitchen Sink <2P>',
'何もしない': 'Do Nothing',
'アホ掌打素振り': 'Idiot Palm-Strike Practice',
'左右に腰ふりダンス': 'Hip-Sway Dance',
},
'0066': {
'正拳ガッツポーズ': 'Straight-Fist Guts Pose',
'返し': 'Reversal',
'マウント腕ひしぎ逆十字固め': 'Mount Armbar Cross Hold',
'＜仰返＞返し三角絞め': '<Face-Up> Reversal Triangle Choke',
'エビですりぬけ': 'Shrimp Slip-Through',
'エプロン上キック−左': 'Apron Kick - Left',
'エプロン上キック−右': 'Apron Kick - Right',
'シュート系組み打撃−Ｎ': 'Shoot Grapple Strike - N',
'ガード': 'Guard',
'フィニッシュ': 'Finish',
'シュート系組み打撃−上': 'Shoot Grapple Strike - Up',
'シュート系組み打撃−下': 'Shoot Grapple Strike - Down',
'シュート系組み打撃−左': 'Shoot Grapple Strike - Left',
'シュート系組み打撃−右': 'Shoot Grapple Strike - Right',
},
'0067': {
'共通': 'Common',
'ダッシュジャンピングドロップキック': 'Dash Jumping Dropkick',
'ダッシュロードロップキック': 'Dash Low Dropkick',
'ダッシュローキック': 'Dash Low Kick',
'ダッシュケンカキック': 'Dash Street Fight Kick',
'ダッシュステップキック': 'Dash Step Kick',
'ダッシュギロチンドロップ': 'Dash Guillotine Drop',
'ダッシュニードロップ': 'Dash Knee Drop',
'レッグエルボードロップ': 'Leg Elbow Drop',
'蹴り返す': 'Kick Back',
'抱え上げ片足ヒザ砕き': 'Lifted One-Leg Knee Crusher',
'なしでＯＫ': 'None',
'ワキ固め': 'Armpit Lock',
'しゃがみ避け': 'Crouch Dodge',
'フロントネックロック': 'Front Neck Lock',
'キャッチ抱え落とし': 'Catch Lift Drop',
'キャッチボディスラム': 'Catch Bodyslam',
},
'0068': {
'正面ダブルインパクト組み技［かたぐるま式］': "Front Double Impact Grapple [Fireman's Carry]",
'背面ダブルインパクト組み技［かたぐるま式］': "Back Double Impact Grapple [Fireman's Carry]",
'正面ダブルインパクト組み技［ﾌﾞﾚｲﾝﾊﾞｽﾀｰ式］': 'Front Double Impact Grapple [Brainbuster]',
'背面ダブルインパクト組み技［ﾌﾞﾚｲﾝﾊﾞｽﾀｰ式］': 'Back Double Impact Grapple [Brainbuster]',
'ダブルインパクト抱え返し技＜正面＞': 'Double Impact Lift Reversal <Front>',
'飛び技迎撃打撃': 'Flying Move Counter Strike',
'ポストへの反撃打撃': 'Counter Strike to the Post',
},
'0069': {
'前方回転エビ固め': 'Forward Roll Shrimp Hold',
'雪崩式腕ひしぎ逆十字固め': 'Avalanche Armbar',
'回転エビ固め': 'Rolling Shrimp Hold',
'無間': 'Mugen',
},
'006A': {
'男前 T-Shirt': 'Handsome T-Shirt',
'色男 T-Shirt': "Ladies' Man T-Shirt",
'大味塊 T-Shirt': 'Big & Bold T-Shirt',
},
}

# Beta 3 blanked these three real move names to "なしでＯＫ"; restore
# from the clean ROM's text.
RESTORE = {
'0064': {
415: ('フランケン返しエビ固め', 'Franken Reversal Shrimp Hold'),
416: ('自爆「のぼり」', "Self-Destruct 'Nobori'"),
417: ('リバースフランケンボム', 'Reverse Franken Bomb'),
},
}


def decode(b):
    # errors='replace': Beta 3's 0068 holds mis-packed offset-table bytes
    # as strings; they can't decode as Shift_JIS and won't match any key.
    return b.decode('shift_jis', errors='replace') if b is not None else None


def main():
    for hexid, mapping in MAPS.items():
        blob = open(os.path.join(ROOT, 'work', 'beta3-%s.bin' % hexid), 'rb').read()
        strings, _ = akitext_parse(blob)
        clean = None
        if hexid in RESTORE:
            cblob = open(os.path.join(ROOT, 'work', 'clean-%s.bin' % hexid), 'rb').read()
            clean, _ = akitext_parse(cblob)
        table = {}
        used = set()
        for i, s in enumerate(strings):
            t = decode(s)
            if t in mapping:
                table[str(i)] = mapping[t]
                used.add(t)
        # restores from clean text
        for idx, (jp, en) in RESTORE.get(hexid, {}).items():
            assert decode(clean[idx]) == jp, (hexid, idx, decode(clean[idx]))
            table[str(idx)] = en
        missing = set(mapping) - used
        if missing:
            print(f'{hexid}: WARNING — map entries not found in Beta 3 file: {sorted(missing)}')
        out = os.path.join(ROOT, 'translations', hexid + '.json')
        json.dump(table, open(out, 'w', encoding='utf-8'),
                  ensure_ascii=False, sort_keys=True)
        print(f'{hexid}: {len(table)} entries -> {out}')


if __name__ == '__main__':
    main()
