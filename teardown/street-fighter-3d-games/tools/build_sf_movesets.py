# Build authentic SF->Tekken moveset JSONs (schema v2) for Western Heart.
# Akuma-in-T7 pattern: SF motion inputs kept (qcf/dp/charge), framed on Tekken logic.
# Frame data in seconds (SF 60fps -> seconds). Damage scaled to WH 100HP.
import json, os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'game/assets/movesets')

def mv(name, inp, sf_command, su, act, rec, dmg, limb, cls='special',
       heavy=False, knock=2.2, soul=10, anim=None, note=None):
    d = {
        'name': name, 'input': inp,
        'sf_move': name, 'sf_command': sf_command,
        'startup': round(su, 3), 'active': round(act, 3), 'recovery': round(rec, 3),
        'damage': dmg, 'limb': limb, 'heavy': heavy, 'knock': knock,
        'soulGain': soul,
        'anim_ref': anim or f"sf:{inp.replace('+','-').replace(',','-').replace('~','-')}",
        'input_slots': [inp], 'move_class': cls,
    }
    if note: d['wh_note'] = note
    return d

HDR = ('SF 60fps -> seconds; damage scaled to WH 100HP; Akuma-in-T7 translation: '
       'SF motions kept, Tekken whiff/juggle/throw-break logic')

def fighter(fid, display, base, src, moves):
    return {
        'fighter': fid, 'display': display,
        'tekken_base': base,
        'proxy': False, 'sf_authentic': True,
        'sf_game_source': src,
        'proxy_note': None,
        'variant': 1, 'moves': moves,
        'frame_convention': HDR, 'schema_version': 2,
    }

F = {}

F['sf-zangief'] = fighter('sf-zangief', 'ZANGIEF (SF authentic)', 'Zangief (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Standing Jab','1','LP',0.067,0.05,0.3,6,'armL','strike'),
 '2': mv('Body Blow','2','MP',0.083,0.05,0.35,8,'armR','strike'),
 '3': mv('Low Kick','3','LK',0.1,0.05,0.4,8,'legL','strike'),
 '4': mv('Standing Short','4','MK',0.083,0.05,0.35,9,'legR','strike'),
 'f+1': mv('Overhead Chop','f+1','f+LP',0.25,0.05,0.5,11,'armL','strike',knock=3.0),
 'f+2': mv('Headbutt','f+2','f+MP',0.2,0.05,0.45,12,'armR','strike',heavy=True,knock=3.2),
 'qcf+2': mv('Green Hand (Banishing Flat)','qcf+2','236+P',0.267,0.1,0.45,14,'armR','special',heavy=True,knock=3.5,soul=15,note='Advancing arm smash, armor through one hit (Banishing Flat).'),
 'hcb,f+1+2': mv('Spinning Piledriver','hcb,f+1+2','63214+P',0.083,0.05,0.6,22,'armR','throw',heavy=True,knock=4.0,soul=20,anim='sf:zangief:spinning-piledriver',note='Iconic 360 command throw. Tekken translation: breakable, 1+2 break.'),
 '1+2,1+2,1+2': mv('Double Lariat','1+2,1+2,1+2','PPP',0.15,0.3,0.55,16,'armR','special',heavy=True,knock=3.8,soul=15,anim='sf:zangief:double-lariat',note='Rapid spin lariat; upper-body invuln vs projectiles.'),
 'f,F+2': mv('Running Bear Grab','f,F+2','66+K (run)',0.35,0.05,0.6,18,'armR','throw',knock=3.5,soul=15,anim='sf:zangief:running-bear-grab'),
 'b+1+2': mv('Final Atomic Buster','b+1+2','360+P (ultra)',0.12,0.05,0.9,30,'armR','throw',heavy=True,knock=5.0,soul=25,anim='sf:zangief:fab',note='Super: double SPD into atomic buster. Soul-cost move.'),
})

F['sf-blanka'] = fighter('sf-blanka', 'BLANKA (SF authentic)', 'Blanka (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Feral Jab','1','LP',0.067,0.05,0.3,6,'armL','strike'),
 '2': mv('Wild Fang','2','MP',0.083,0.05,0.35,8,'armR','strike'),
 '3': mv('Amazon Kick','3','LK',0.1,0.05,0.4,9,'legL','strike'),
 '4': mv('Beast Heel','4','MK',0.117,0.05,0.45,10,'legR','strike'),
 'b+1': mv('Rock Crusher','b+1','b+LP',0.15,0.05,0.4,10,'armL','strike',knock=3.0),
 '1,1,1,1': mv('Electric Thunder','1,1,1,1','rapid PPP',0.2,0.4,0.5,12,'armR','special',knock=3.2,soul=15,anim='sf:blanka:electric-thunder',note='Body-wide shock field; anti-rushdown. Tekken translation: multi-hit pressure string.'),
 'b~f+2': mv('Rolling Attack','b~f+2','[b]f+P',0.183,0.15,0.5,15,'armR','special',heavy=True,knock=4.0,soul=15,anim='sf:blanka:rolling-attack',note='Charge move: horizontal cannonball.'),
 'd~u+4': mv('Vertical Roll','d~u+4','[d]u+K',0.2,0.15,0.5,14,'legR','special',knock=3.8,soul=12,anim='sf:blanka:vertical-roll',note='Charge move: rising arc, anti-air.'),
 'qcb+2': mv('Backstep Roll','qcb+2','214+P',0.25,0.1,0.45,13,'armR','special',knock=3.2,soul=12,anim='sf:blanka:backstep-roll',note='Evasive roll into hop strike; cancellable.'),
 '1+3': mv('Wild Bite Throw','1+3','close LP+LK',0.083,0.05,0.5,14,'armR','throw',knock=3.5,soul=10),
 'b+1+2': mv('Ground Shave Rolling','b+1+2','[b]f+PPP (super)',0.3,0.3,0.7,28,'armR','special',heavy=True,knock=4.5,soul=25,anim='sf:blanka:ground-shave',note='Super: full-screen rolling charge.'),
})

F['sf-vega'] = fighter('sf-vega', 'VEGA (SF authentic)', 'Vega (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Claw Jab','1','LP',0.067,0.05,0.28,7,'armL','strike'),
 '2': mv('Crystal Slash','2','MP',0.083,0.05,0.32,9,'armR','strike'),
 '3': mv('Sweeping Kick','3','LK',0.1,0.07,0.4,9,'legL','strike'),
 '4': mv('Crimson Kick','4','MK',0.117,0.05,0.4,10,'legR','strike'),
 'df+2': mv('Claw Poke','df+2','df+MP',0.183,0.05,0.42,10,'armR','strike',knock=2.6,note='Long-range claw poke — Vega reach advantage.'),
 'b~f+1': mv('Rolling Crystal Flash','b~f+1','[b]f+P',0.3,0.2,0.5,15,'armL','special',knock=3.4,soul=15,anim='sf:vega:crystal-flash',note='Rolling ground approach into claw slash.'),
 'd~u+2': mv('Flying Barcelona Attack','d~u+2','[d]u+P',0.4,0.15,0.55,16,'armR','special',knock=3.8,soul=15,anim='sf:vega:barcelona',note='Wall/cage dive. Branch: +1 claw strike, +1+3 Izuna Drop.'),
 'd~u+2,1+3': mv('Izuna Drop','d~u+2,1+3','Barcelona -> LP+LK',0.45,0.1,0.6,20,'armR','throw',heavy=True,knock=4.2,soul=18,anim='sf:vega:izuna-drop',note='Airborne command grab off the Barcelona dive.'),
 'd~u+1+2': mv('Sky High Claw','d~u+1+2','[d]u+PP',0.35,0.12,0.5,15,'armR','special',knock=3.6,soul=12,anim='sf:vega:sky-high-claw'),
 'qcb+4': mv('Scarlet Terror','qcb+4','214+K',0.25,0.1,0.45,13,'legR','special',knock=3.2,soul=12,anim='sf:vega:scarlet-terror',note='Backflip kick, evasive.'),
 'b+1+2': mv('Bloody High Claw','b+1+2','[d]u+PPP (ultra)',0.4,0.2,0.8,30,'armR','special',heavy=True,knock=4.5,soul=25,anim='sf:vega:bloody-high-claw',note='Super: soaring claw dive from the wall.'),
})

F['sf-ryu'] = fighter('sf-ryu', 'RYU (SF authentic)', 'Ryu (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Straight Jab','1','LP',0.05,0.05,0.25,6,'armL','strike'),
 '2': mv('Seichu Nidan Tsuki','2','MP',0.083,0.05,0.35,8,'armR','strike'),
 '3': mv('Low Short','3','LK',0.083,0.05,0.32,7,'legL','strike'),
 '4': mv('Roundhouse Kick','4','HK',0.183,0.05,0.5,13,'legR','strike',knock=3.4),
 'df+3': mv('Crouching Medium Kick','df+3','2+MK',0.117,0.05,0.4,9,'legL','strike',note='The classic footsie poke; cancels into Hadouken.'),
 'qcf+2': mv('Hadouken','qcf+2','236+P',0.217,0.05,0.816,8,'armR','special',soul=8,anim='sf:ryu:hadouken',note='Fireball. Tekken (Akuma) translation: projectile, chip damage, sidestep beats it.'),
 'hcb+2': mv('Shakunetsu Hadouken','hcb+2','63214+P',0.3,0.05,0.9,12,'armR','special',soul=12,anim='sf:ryu:shakunetsu',note='Flaming multi-hit fireball.'),
 'f,d,df+1': mv('Shoryuken','f,d,df+1','623+P',0.05,0.2,0.7,14,'armR','special',heavy=True,knock=3.8,soul=12,anim='sf:ryu:shoryuken',note='Invincible anti-air uppercut (3f startup, SFIV data).'),
 'qcb+3': mv('Tatsumaki Senpuukyaku','qcb+3','214+K',0.183,0.25,0.6,12,'legL','special',knock=3.4,soul=12,anim='sf:ryu:tatsumaki',note='Hurricane kick; advances, juggle filler.'),
 '1+3': mv('Seoi Throw','1+3','close LP+LK',0.083,0.05,0.5,12,'armR','throw',knock=3.2),
 'qcf,qcf+2': mv('Shinkuu Hadouken','qcf,qcf+2','236236+P (super)',0.15,0.3,1.0,26,'armR','special',heavy=True,knock=4.2,soul=25,anim='sf:ryu:shinkuu',note='Super fireball, 5 hits.'),
})

F['sf-ken'] = fighter('sf-ken', 'KEN (SF authentic)', 'Ken (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Quick Jab','1','LP',0.05,0.05,0.25,6,'armL','strike'),
 '2': mv('Fire Fist Hook','2','MP',0.083,0.05,0.35,9,'armR','strike'),
 '3': mv('Low Short','3','LK',0.083,0.05,0.32,7,'legL','strike'),
 '4': mv('Axe Kick','4','MK',0.15,0.05,0.45,11,'legR','strike'),
 'f+4': mv('Thunder Kick','f+4','f+MK',0.283,0.05,0.5,12,'legR','strike',knock=3.2),
 'qcf+2': mv('Hadouken','qcf+2','236+P',0.217,0.05,0.816,8,'armR','special',soul=8,anim='sf:ken:hadouken'),
 'f,d,df+2,2': mv('Shoryuken','f,d,df+2,2','623+P,P',0.05,0.25,0.75,16,'armR','special',heavy=True,knock=3.8,soul=12,anim='sf:ken:shoryuken',note='Flaming multi-hit dragon punch.'),
 'qcb+4': mv('Tatsumaki Senpuukyaku','qcb+4','214+K',0.183,0.3,0.6,14,'legR','special',knock=3.4,soul=12,anim='sf:ken:tatsumaki',note='Multi-hit hurricane kick, wall carry.'),
 'qcf+3,3,3': mv('Jinrai Kick','qcf+3,3,3','236+K,K,K',0.2,0.3,0.6,15,'legL','special',knock=3.4,soul=14,anim='sf:ken:jinrai',note='Triple rising kick string.'),
 '1+3': mv('Knee Bash Hold','1+3','close LP+LK',0.083,0.05,0.5,12,'legR','throw',knock=3.2),
 'f,d,df,f,d,df+2': mv('Shoryureppa','f,d,df,f,d,df+2','623623+P (super)',0.1,0.4,1.1,28,'armR','special',heavy=True,knock=4.5,soul=25,anim='sf:ken:shoryureppa',note='Super: triple dragon punch chain.'),
})

F['sf-chunli'] = fighter('sf-chunli', 'CHUN-LI (SF authentic)', 'Chun-Li (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Quick Palm','1','LP',0.05,0.05,0.25,6,'armL','strike'),
 '2': mv('Eagle Talon','2','MP',0.083,0.05,0.32,8,'armR','strike'),
 '3': mv('Lightning Toe','3','LK',0.083,0.05,0.3,7,'legL','strike'),
 '4': mv('Whirlwind Kick','4','MK',0.117,0.05,0.4,10,'legR','strike'),
 '3,3,3,3': mv('Hyakuretsukyaku (Lightning Kicks)','3,3,3,3','rapid K',0.15,0.4,0.55,14,'legR','special',knock=3.2,soul=15,anim='sf:chunli:lightning-kicks',note='Multi-hit pressure string; frame advantage on block.'),
 'qcb+2': mv('Kikkoken','qcb+2','214+P',0.25,0.05,0.7,8,'armR','special',soul=8,anim='sf:chunli:kikkoken',note='Short-range fireball.'),
 'd~u+3': mv('Spinning Bird Kick','d~u+3','[d]u+K',0.283,0.3,0.6,14,'legL','special',knock=3.4,soul=12,anim='sf:chunli:sbk',note='Charge: advancing multi-hit spin, armored.'),
 'f+4': mv('Hazanshu','f+4','f+K (overhead)',0.283,0.05,0.5,11,'legR','strike',knock=3.2,note='Overhead flip kick.'),
 '1+3': mv('Koshu Tosho Throw','1+3','close LP+LK',0.083,0.05,0.5,12,'armR','throw',knock=3.2),
 'qcf,qcf+3': mv('Hoyokusen','qcf,qcf+3','236236+K (super)',0.12,0.4,1.0,26,'legR','special',heavy=True,knock=4.2,soul=25,anim='sf:chunli:hoyokusen',note='Super: lightning kick barrage into launcher.'),
})

F['sf-guile'] = fighter('sf-guile', 'GUILE (SF authentic)', 'Guile (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Jab','1','LP',0.05,0.05,0.25,6,'armL','strike'),
 '2': mv('Straight Punch','2','MP',0.083,0.05,0.32,8,'armR','strike'),
 '3': mv('Knee Bazooka','3','LK',0.1,0.05,0.35,8,'legL','strike'),
 '4': mv('Rolling Sobat','4','MK',0.15,0.05,0.45,11,'legR','strike'),
 'f+3': mv('Spinning Back Knuckle','f+3','f+HP',0.25,0.05,0.45,12,'armR','strike',knock=3.0),
 'df+3': mv('Crouching Medium Kick','df+3','2+MK',0.117,0.05,0.4,10,'legL','strike',note='Long-range crouch poke; the Guile wall.'),
 'b~f+2': mv('Sonic Boom','b~f+2','[b]f+P',0.167,0.05,0.65,8,'armR','special',soul=8,anim='sf:guile:sonic-boom',note='Fastest fireball recovery in the set; zoning core. Charge input kept (Akuma pattern).'),
 'd~u+4': mv('Flash Kick','d~u+4','[d]u+K',0.067,0.2,0.75,15,'legR','special',heavy=True,knock=3.8,soul=12,anim='sf:guile:flash-kick',note='Invincible anti-air somersault kick.'),
 'f+4': mv('Upside Down Kick','f+4','f+HK',0.3,0.05,0.5,12,'legR','strike',knock=3.2),
 '1+3': mv('Dragon Suplex','1+3','close LP+LK',0.083,0.05,0.5,14,'armR','throw',knock=3.5),
 'b~f,b~f+2': mv('Sonic Hurricane','b~f,b~f+2','[b]f[b]f+P (super)',0.2,0.3,1.0,26,'armR','special',heavy=True,knock=4.2,soul=25,anim='sf:guile:sonic-hurricane',note='Super: giant lingering sonic boom.'),
})

F['sf-mbison'] = fighter('sf-mbison', 'M. BISON (SF authentic)', 'M. Bison (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Psycho Jab','1','LP',0.067,0.05,0.3,6,'armL','strike'),
 '2': mv('Psycho Fist','2','MP',0.1,0.05,0.35,9,'armR','strike'),
 '3': mv('Low Scissor','3','LK',0.1,0.05,0.35,8,'legL','strike'),
 '4': mv('Hell Attack Kick','4','MK',0.117,0.05,0.4,10,'legR','strike'),
 'df+2': mv('Crouching Fierce','df+2','2+HP',0.15,0.05,0.45,12,'armR','strike',knock=3.0),
 'b~f+2': mv('Psycho Crusher','b~f+2','[b]f+P',0.217,0.2,0.55,16,'armR','special',heavy=True,knock=4.0,soul=15,anim='sf:mbison:psycho-crusher',note='Full-body torpedo; armored pressure.'),
 'b~f+3': mv('Double Knee Press (Scissor Kick)','b~f+3','[b]f+K',0.2,0.1,0.5,14,'legL','special',knock=3.4,soul=12,anim='sf:mbison:scissor-kick',note='Fast double mid-lunge; Bison pressure loop.'),
 'd~u+3': mv('Head Stomp','d~u+3','[d]u+K',0.3,0.1,0.55,14,'legR','special',knock=3.6,soul=12,anim='sf:mbison:head-stomp',note='Air stomp; branches into Devils Reverse on hit.'),
 'd~u+3,2': mv("Devil's Reverse",'d~u+3,2','Head Stomp -> P',0.35,0.1,0.6,13,'armR','special',knock=3.4,soul=10,anim='sf:mbison:devils-reverse'),
 'f,d,df+3+4': mv('Bison Warp (Teleport)','f,d,df+3+4','623+KK',0.05,0.05,0.4,0,'legR','special',soul=6,anim='sf:mbison:warp',note='Positional teleport. Tekken translation: repositioning special, no damage.'),
 '1+3': mv('Psycho Throw','1+3','close LP+LK',0.083,0.05,0.5,13,'armR','throw',knock=3.4),
 'b~f,b~f+3': mv('Nightmare Booster','b~f,b~f+3','[b]f[b]f+K (super)',0.25,0.3,1.0,28,'legL','special',heavy=True,knock=4.5,soul=25,anim='sf:mbison:nightmare-booster',note='Super: scissor kick into psycho crusher finale.'),
})

F['sf-sagat'] = fighter('sf-sagat', 'SAGAT (SF authentic)', 'Sagat (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Tiger Jab','1','LP',0.067,0.05,0.3,7,'armL','strike'),
 '2': mv('Tiger Elbow','2','MP',0.1,0.05,0.35,9,'armR','strike'),
 '3': mv('Low Tiger Kick','3','LK',0.1,0.05,0.4,9,'legL','strike'),
 '4': mv('Tiger Knee Kick','4','MK',0.133,0.05,0.45,11,'legR','strike'),
 'qcf+2': mv('Tiger Shot','qcf+2','236+P',0.233,0.05,0.7,9,'armR','special',soul=8,anim='sf:sagat:tiger-shot',note='High fireball; low variant on qcf+4.'),
 'qcf+4': mv('Ground Tiger Shot','qcf+4','236+K',0.25,0.05,0.7,9,'legR','special',soul=8,anim='sf:sagat:ground-tiger-shot',note='Low fireball.'),
 'f,d,df+2': mv('Tiger Uppercut','f,d,df+2','623+P',0.083,0.2,0.8,16,'armR','special',heavy=True,knock=4.0,soul=12,anim='sf:sagat:tiger-uppercut',note='Towering anti-air uppercut.'),
 'f,d,df+4': mv('Tiger Knee Crush','f,d,df+4','623+K',0.2,0.15,0.55,14,'legR','special',knock=3.6,soul=12,anim='sf:sagat:tiger-knee-crush',note='Flying knee; crushes lows.'),
 '1+3': mv('Tiger Carry Throw','1+3','close LP+LK',0.083,0.05,0.5,13,'armR','throw',knock=3.4),
 'qcf,qcf+2': mv('Tiger Cannon','qcf,qcf+2','236236+P (super)',0.2,0.2,1.0,27,'armR','special',heavy=True,knock=4.2,soul=25,anim='sf:sagat:tiger-cannon',note='Super: giant tiger shot.'),
})

F['sf-dhalsim'] = fighter('sf-dhalsim', 'DHALSIM (SF authentic)', 'Dhalsim (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Yoga Spear','1','LP',0.1,0.05,0.4,7,'armL','strike',note='Stretch limb — extreme range poke.'),
 '2': mv('Stretch Fist','2','MP',0.133,0.05,0.45,9,'armR','strike',note='Stretch limb.'),
 '3': mv('Yoga Knee','3','LK',0.1,0.05,0.35,8,'legL','strike'),
 '4': mv('Stretch Kick','4','MK',0.15,0.05,0.45,10,'legR','strike',note='Stretch limb.'),
 'df+2': mv('Yoga Uppercut','df+2','2+HP',0.15,0.05,0.45,11,'armR','strike',knock=3.0),
 'hcf+2': mv('Yoga Fire','hcf+2','632+P',0.25,0.05,0.85,8,'armR','special',soul=8,anim='sf:dhalsim:yoga-fire',note='Slow arcing fireball; zoning core.'),
 'hcb+2': mv('Yoga Flame','hcb+2','63214+P',0.3,0.2,0.7,13,'armR','special',knock=3.4,soul=12,anim='sf:dhalsim:yoga-flame',note='Flame breath, mid-range wall.'),
 'f,d,df+1+2': mv('Yoga Teleport','f,d,df+1+2','623+PP',0.05,0.05,0.4,0,'armR','special',soul=6,anim='sf:dhalsim:yoga-teleport',note='Teleport behind/above opponent.'),
 '1+3': mv('Yoga Smash Throw','1+3','close LP+LK',0.083,0.05,0.5,12,'armR','throw',knock=3.2),
 'hcb,hcb+2': mv('Yoga Inferno','hcb,hcb+2','6321463214+P (super)',0.25,0.4,1.1,27,'armR','special',heavy=True,knock=4.2,soul=25,anim='sf:dhalsim:yoga-inferno',note='Super: sustained flame pillar.'),
})

F['sf-cammy'] = fighter('sf-cammy', 'CAMMY (SF authentic)', 'Cammy (SF) — Akuma-pattern translation', 'SF EX / SFIV source move data', {
 '1': mv('Delta Jab','1','LP',0.05,0.05,0.25,6,'armL','strike'),
 '2': mv('Delta Hook','2','MP',0.083,0.05,0.32,8,'armR','strike'),
 '3': mv('Delta Toe','3','LK',0.083,0.05,0.3,7,'legL','strike'),
 '4': mv('Delta Heel','4','MK',0.1,0.05,0.38,9,'legR','strike'),
 'df+3': mv('Crouching Medium Kick','df+3','2+MK',0.117,0.05,0.38,9,'legL','strike'),
 'qcf+4': mv('Spiral Arrow','qcf+4','236+K',0.2,0.1,0.5,13,'legR','special',knock=3.4,soul=12,anim='sf:cammy:spiral-arrow',note='Low spinning drill kick; closes distance.'),
 'f,d,df+4': mv('Cannon Spike','f,d,df+4','623+K',0.067,0.15,0.7,15,'legR','special',heavy=True,knock=3.8,soul=12,anim='sf:cammy:cannon-spike',note='Rising anti-air kick.'),
 'qcb+2': mv('Quick Spin Knuckle','qcb+2','214+P',0.283,0.1,0.5,12,'armR','special',knock=3.2,soul=10,anim='sf:cammy:spin-knuckle',note='Spin-through backfist; passes projectiles.'),
 '1+3': mv('Frankensteiner','1+3','close LP+LK',0.1,0.05,0.5,14,'legR','throw',knock=3.6),
 'qcf,qcf+4': mv('Spin Drive Smasher','qcf,qcf+4','236236+K (super)',0.15,0.3,1.0,26,'legR','special',heavy=True,knock=4.2,soul=25,anim='sf:cammy:spin-drive',note='Super: spiral arrow into cannon spike.'),
})

for fid, data in F.items():
    with open(os.path.join(OUT, fid + '.json'), 'w') as f:
        json.dump(data, f, indent=1)
    print('wrote', fid, len(data['moves']), 'moves')
