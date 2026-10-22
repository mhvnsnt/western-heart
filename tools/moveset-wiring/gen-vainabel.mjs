#!/usr/bin/env node
// gen-vainabel.mjs — Bass Armstrong (DOA4) → Vain Abel full Tekken-notation moveset.
// INPUT-TO-MOVE FIDELITY LAW: every DOA input becomes one specific Tekken input.
// DOA P/K + directions → 1/2/3/4 + directions. F+P throws → 1+3-family.
// F+G holds → Tekken reversal slots. Frame data follows Tekken conventions (60fps).
// Usage: node gen-vainabel.mjs [existing-vainabel.json] > vainabel.json
import { readFileSync } from 'fs';

const S = (v) => v; // startup seconds @60fps
// [key, input, name, doa_move, doa_input, startup, dmg, limb, hit_level, class, knock, soul, note]
const MOVES = [
["1","1","Palm Jab","Palm Jab","P",0.167,7,"armL","high","strike",2.2,8,"DOA P; i10 jab"],
["2","2","Cross Punch","Cross Punch","PP",0.2,8,"armR","high","strike",2.2,8,"DOA PP 2nd hit as standalone 2"],
["1,2","1,2","Combo Gong (2-hit)","Combo Gong","PP",0.183,14,"armR","high,high","strike",2.6,9,""],
["1,2,1","1,2,1","Combo Gong","Combo Gong","PPP",0.2,21,"armL","high,high,high","strike",3.0,10,""],
["1,2,d+1","1,2,d+1","Combo Hammer","Combo Hammer","PP2P",0.217,20,"armR","high,high,low","strike",3.0,10,""],
["1,2,3","1,2,3","Combo High Kick","Combo High Kick","PPK",0.217,22,"legR","high,high,high","strike",3.2,10,""],
["1,3","1,3","Triple Hit (2-hit)","Combo Triple Hit","PK",0.183,15,"legL","high,mid","strike",2.6,9,""],
["1,3,2","1,3,2","Combo Triple Hit","Combo Triple Hit","PKP",0.2,22,"armR","high,mid,high","strike",3.0,10,""],
["1,3,4","1,3,4","Combo Kick Rush","Combo Kick Rush","PKK",0.217,24,"legR","high,mid,mid","strike",3.2,10,""],
["f+1","f+1","Wild Swing","Wild Swing","6P",0.217,12,"armR","mid","strike",2.8,8,""],
["f+1,2","f+1,2","Wild Swing Combo","Wild Swing","6PP",0.2,22,"armL","mid,high","strike",3.0,10,""],
["f+1,2,3","f+1,2,3","Combo Stomp Kick","Combo Stomp Kick","6PK",0.217,26,"legR","mid,high,mid","strike",3.4,10,""],
["u/f+1","u/f+1","Elbow Rush","Elbow Rush","9P",0.233,13,"armR","mid","strike",2.8,8,""],
["u/f+1,2","u/f+1,2","Elbow Rush Combo","Elbow Rush","9PP",0.217,24,"armL","mid,high","strike",3.0,10,""],
["u/f+1,2,3","u/f+1,2,3","Elbow Gong","Elbow Gong","9PKP",0.233,30,"armL","mid,high,mid","strike",3.6,11,""],
["u/f+1,2,d+3","u/f+1,2,d+3","Elbow Hammer","Elbow Hammer","9PK2P",0.25,32,"armR","mid,high,low","strike",3.8,11,""],
["u/f+1,3","u/f+1,3","Elbow Stomp Combo","Elbow Stomp Combo","hold-9 PK",0.25,26,"legR","mid,high","strike",3.4,10,"hold 9P version"],
["b+1","b+1","Stun Gun Chop","Stun Gun Chop","4P",0.233,13,"armL","high","strike",2.8,8,""],
["b+1,2","b+1,2","Stun Gun Chop (2-hit)","Stun Gun Chop","4PP",0.217,24,"armR","high,high","strike",3.0,10,""],
["b+1,2,1","b+1,2,1","Stun Gun Chop (full)","Stun Gun Chop","4PPP",0.233,32,"armL","high,high,high","strike",3.6,11,""],
["b+1,2,1+2","b+1,2,1+2","Hell Smasher","Hell Smasher","4PPP+K",0.25,38,"legR","high,high,high,mid","strike",4.2,12,"heavy"],
["u+1","u+1","One Hand Hammer","One Hand Hammer","8P",0.25,18,"armR","high","strike",3.4,10,"overhead"],
["u/b+1","u/b+1","Mongolian Head Butt","Mongolian Head Butt","7P hold-P",0.283,20,"head","high","strike",3.8,10,""],
["d+1","d+1","Throat Strike","Throat Strike","2P",0.233,12,"armR","mid","strike",2.8,8,""],
["d+1,2","d+1,2","Throat Strike Combo","Throat Strike","2PP",0.217,22,"armL","mid,high","strike",3.0,10,""],
["d/b+1","d/b+1","Power Gong","Power Gong","1P",0.267,14,"armL","mid","strike",3.0,9,""],
["d/b+1,2","d/b+1,2","Power Gong Combo","Power Gong","1PP",0.25,26,"armR","mid,high","strike",3.4,10,""],
["d/b+1,2,1+2","d/b+1,2,1+2","Gong Hell Combo","Gong Hell Combo","1PP+K",0.267,34,"legR","mid,high,mid","strike",4.0,12,"heavy"],
["d/f+1","d/f+1","Muscle Drive","The Muscle Man","hold-3 P",0.267,14,"armR","mid","strike",3.0,9,""],
["d/f+1,2","d/f+1,2","The Muscle Man","The Muscle Man","hold-3 PP",0.25,26,"armL","mid,high","strike",3.4,10,""],
["f,f+1","f,f+1","Smash Gong","Smash Gong","66P",0.25,20,"armR","mid","strike",3.6,10,""],
["d/f,d/f+1","d/f,d/f+1","Buffalo Rage","Buffalo Rage","33P",0.283,16,"armR","mid","strike",3.2,9,""],
["d/f,d/f+1,2","d/f,d/f+1,2","Buffalo Rage Combo","Buffalo Rage","33PP",0.267,28,"armL","mid,high","strike",3.6,11,""],
["qcf+1","qcf+1","Rolling Hell Smasher","Rolling Hell Smasher","236P",0.283,22,"armR","mid","strike",4.4,11,"launcher-lite"],
["b,f+1","b,f+1","Diving Hammer","Diving Hammer","46 hold-P",0.3,24,"armR","mid","strike",4.2,11,"heavy"],
["qcb+1","qcb+1","Rolling Axe","Rolling Axe","214P",0.3,22,"armL","mid","strike",4.0,11,""],
["f,f,f+1","f,f,f+1","Flying Body Press","Flying Body Press","running P",0.3,25,"body","mid","strike",4.4,12,"heavy; while running"],
["1+2","1+2","Hell Stab","Hell Stab","P+K",0.233,16,"armL","mid","strike",3.2,9,""],
["f+1+2","f+1+2","Mad Lariat","Mad Lariat","6P+K",0.25,18,"armL","mid","strike",3.4,10,""],
["f+1+2,1","f+1+2,1","Mad Lariat Combo","Mad Lariat","6P+KP",0.233,30,"armR","mid,high","strike",3.8,11,""],
["b+1+2","b+1+2","Muscle Elbow","Muscle Elbow","4P+K",0.267,20,"armL","mid","strike",3.6,10,""],
["d/f+1+2","d/f+1+2","Bear Crash","Bear Crash","3P+K",0.283,22,"armR","mid","strike",3.8,10,""],
["d/b+1+2","d/b+1+2","Linebacker","Linebacker","1 hold-P hold-K",0.333,25,"body","mid","strike",4.4,12,"heavy"],
["f,f+1+2","f,f+1+2","Flying Cross Chop","Flying Cross Chop","66P+K",0.3,24,"armL","mid","strike",4.2,11,"heavy"],
["d+1+2","d+1+2","Buffalo Train","Buffalo Train","2P+K",0.283,18,"armL","mid","strike",3.4,10,""],
["d+1+2,1","d+1+2,1","Buffalo Train Combo","Buffalo Train","2P+KP",0.267,30,"armR","mid,high","strike",3.8,11,""],
["d+1+2,1,3","d+1+2,1,3","Bass Special","Bass Special","2P+KP+K",0.283,40,"legR","mid,high,mid","strike",4.4,12,"heavy"],
["f+3","f+3","Knee Hammer","Knee Hammer","6K",0.25,16,"legR","mid","strike",3.2,9,""],
["f+3,1","f+3,1","Knee Hammer Combo","Knee Hammer","6KP",0.233,28,"armR","mid,high","strike",3.6,11,""],
["f+3,4","f+3,4","Knee Destroyer","Knee Destroyer","6KK",0.25,30,"legR","mid,high","strike",3.8,11,""],
["u+3","u+3","Jumping Knee","Jumping Knee","8K",0.267,20,"legR","high","strike",3.6,10,""],
["u/f+3","u/f+3","High Stomp Kick","High Stomp Kick","9K",0.283,22,"legR","high","strike",3.8,10,""],
["d/f+3","d/f+3","Bass Punch","Bass Punch","3K",0.267,16,"legR","mid","strike",3.2,9,""],
["d/f+3,1","d/f+3,1","Bass Punch Combo","Bass Punch","3KP",0.25,28,"armR","mid,high","strike",3.6,11,""],
["d/f+3,4","d/f+3,4","Kick Rush","Kick Rush","3KK",0.267,30,"legR","mid,mid","strike",3.8,11,""],
["d/b+3","d/b+3","Rising Palm","Rising Palm","1K",0.267,16,"legR","low","strike",3.0,9,""],
["d/b+3,1","d/b+3,1","Rising Palm Combo","Rising Palm","1KP",0.25,28,"armR","low,high","strike",3.6,11,""],
["f,f+3","f,f+3","Brawler Kick","Brawler Kick","66K",0.283,22,"legR","high","strike",3.8,10,""],
["3+4","3+4","Drop Kick","Drop Kick","F+K",0.3,24,"legR","mid","strike",4.2,11,"heavy"],
["f+3+4","f+3+4","Front Roll Kick","Front Roll Kick","6F+K",0.3,24,"legR","mid","strike",4.2,11,""],
["b+3+4","b+3+4","Sumo Stomp","Sumo Stomp","4 hold-F hold-K",0.333,26,"legR","low","strike",4.4,12,"heavy"],
["d+3+4","d+3+4","Low Drop Kick","Low Drop Kick","2F+K",0.3,22,"legR","low","strike",4.0,11,""],
["u/f+1~jump","u/f+1","Leaping Hammer","Leaping Hammer","jumping P",0.25,18,"armR","high","strike",3.4,10,"while jumping over obstacle"],
["u/f+3~jump","u/f+3","Leaping Drop Kick","Leaping Drop Kick","jumping K",0.267,20,"legR","high","strike",3.6,10,"while jumping over obstacle"],
["1+2~bt","1+2","Turning Lariat","Turning Lariat","P+K to foe behind",0.283,20,"armL","mid","strike",3.6,10,"back-turned"],
["b+1+2~bt","b+1+2","Turning Muscle Elbow","Turning Muscle Elbow","4P+K to foe behind",0.3,22,"armL","mid","strike",3.8,10,"back-turned"],
["u/b+3~bt","u/b+3","Turning Middle Kick","Turning Middle Kick","7K to foe behind",0.283,20,"legR","mid","strike",3.6,10,"back-turned"],
["ws3+4","ws3+4","Rising Low Drop Kick","Rising Low Drop Kick","F+K while getting up",0.3,22,"legR","low","strike",4.0,11,"while rising"],
// ---- throws: F+P -> 1+3 family, Tekken directional throws ----
["1+3","1+3","Bass Slammer","Bass Slammer","F+P",0.2,40,"armR","throw","throw",5.5,12,""],
["2+4","2+4","Canyon Dunk","Canyon Dunk","F+P foe's back to slope",0.2,42,"armR","throw","throw",5.5,12,"slope"],
["2+4~v","2+4","T.F.B.D.","T.F.B.D.","F+P slope with cliff",0.2,46,"armR","throw","throw",5.8,12,"cliff"],
["f+1+3","f+1+3","Bass Tornado","Bass Tornado","6F+P",0.217,42,"armR","throw","throw",5.5,12,""],
["f+1+3~wall","f+1+3","Wild Bull Head Butt","Wild Bull Head Butt","66F+P next to wall",0.233,50,"head","throw","throw",5.8,13,"wall"],
["f+2+4","f+2+4","Dynamite Lariat","Dynamite Lariat","46F+P",0.233,45,"armL","throw","throw",5.6,12,""],
["f+2+4~wall","f+2+4","Atomic Hammer Crash","Atomic Hammer Crash","46F+P next to wall",0.233,52,"armL","throw","throw",5.8,13,"wall"],
["u+1+3","u+1+3","Flying Body Scissors","Flying Body Scissors","8F+P",0.217,43,"legR","throw","throw",5.5,12,""],
["d/f+1+3","d/f+1+3","Super Freak","Super Freak","41236F+P",0.25,48,"armR","throw","throw",5.8,13,""],
["d/f+1+3~hold","d/f+1+3","Dancing Freak","Dancing Freak","41236 hold-F hold-P",0.267,50,"armR","throw","throw",5.8,13,"held version"],
["d/f+2+4","d/f+2+4","Freaky Bomb","Freaky Bomb","41236 double-hold",0.283,55,"armR","throw","throw",6.0,14,"heaviest throw"],
["qcf+1+3","qcf+1+3","Oklahoma Stampede","Oklahoma Stampede","236F+P",0.233,45,"armR","throw","throw",5.6,13,"throw combo starter"],
["qcb+1+3","qcb+1+3","Manhattan Driver","Manhattan Driver","214F+P",0.233,45,"armR","throw","throw",5.6,13,"throw combo starter"],
["b+1+3","b+1+3","Push Away","Push Away","4F+P",0.217,38,"armR","throw","throw",5.2,12,"throw combo starter"],
["b+1+3~wall","b+1+3","Bear Press","Bear Press","4F+P next to wall",0.217,46,"armR","throw","throw",5.6,13,"wall"],
["b+2+4","b+2+4","Argentine Back Breaker","Argentine Back Breaker","4F+P to foe's back",0.217,45,"armR","throw","throw",5.6,13,"back"],
["b+1+3~back","b+1+3","Dangerous Back Drop","Dangerous Back Drop","F+P to foe's back",0.2,45,"armR","throw","throw",5.6,13,"back"],
["b+1+3~backwall","b+1+3","Locomotion Back Drop","Locomotion Back Drop","F+P wall behind foe",0.2,50,"armR","throw","throw",5.8,13,"wall, back"],
["f+1+3~back","f+1+3","Reverse Power Bomb","Reverse Power Bomb","46F+P to foe's back",0.233,48,"armR","throw","throw",5.8,13,"back"],
["1+3~back","1+3","Spin Around","Spin Around","F+P to foe behind",0.2,40,"armR","throw","throw",5.5,12,"behind"],
["1+3~pushaside","1+3","Push Aside","Push Aside","F+P behind foe, back to foe",0.2,35,"armR","throw","throw",5.0,11,"behind"],
["d+1+3","d+1+3","Bass Bomb","Bass Bomb","2F+P to crouching foe",0.217,42,"armR","throw","throw",5.5,12,"crouching"],
["d+2+4","d+2+4","Double Arm Driver","Double Arm Driver","3F+P to crouching foe",0.217,44,"armR","throw","throw",5.6,12,"crouching"],
["d/f+2+4","d/f+2+4","Spiral Bomb","Spiral Bomb","33F+P to crouching foe",0.233,46,"armR","throw","throw",5.6,13,"crouching"],
["d/b+1+3","d/b+1+3","T.F.B.B.","T.F.B.B.","64F+P while crouching",0.233,48,"armR","throw","throw",5.8,13,"crouching"],
["d/b+1+3~wall","d/b+1+3","T.F.B.C.","T.F.B.C.","64F+P wall while crouching",0.233,52,"armR","throw","throw",5.8,13,"wall, crouching"],
["d/b+1+3~ceil","d/b+1+3","T.F.B.A.","T.F.B.A.","64F+P ceiling while crouching",0.233,55,"armR","throw","throw",6.0,14,"ceiling, crouching"],
["d/b+2+4","d/b+2+4","Calf Branding","Calf Branding","2F+P to crouching foe's back",0.217,44,"armR","throw","throw",5.6,12,"crouching back"],
["u/b+1+3","u/b+1+3","One Leg Standing Head Butt","One Leg Standing Head Butt","66F+P",0.233,46,"head","throw","throw",5.6,13,""],
["u/f+1+3","u/f+1+3","Running Neck Breaker Drop","Running Neck Breaker Drop","F+P while running",0.217,44,"armR","throw","throw",5.6,12,"running"],
["u/f+1+3~back","u/f+1+3","Running Face Buster","Running Face Buster","F+P running behind foe",0.217,46,"armR","throw","throw",5.6,13,"running, back"],
["d/f+1+3~air","d/f+1+3","Barrel Throw","Barrel Throw","F+P to foe in air",0.233,40,"armR","throw","throw",5.5,12,"air"],
["d/f+1+3~cliff","d/f+1+3","Tandem Dive","Tandem Dive","F+P near cliff",0.233,50,"armR","throw","throw",5.8,13,"cliff"],
["d+1+3~g1","d+1+3","Ground Throw 1","Ground Throw 1","2F+P face-up feet",0.217,40,"armR","throw","throw",5.2,11,"grounded"],
["d+1+3~g2","d+1+3","Ground Throw 2","Ground Throw 2","2F+P face-up head",0.217,40,"armR","throw","throw",5.2,11,"grounded"],
["d+1+3~g3","d+1+3","Ground Throw 3","Ground Throw 3","2F+P face-up side",0.217,40,"armR","throw","throw",5.2,11,"grounded"],
["d+1+3~g4","d+1+3","Ground Throw 4","Ground Throw 4","2F+P face-down feet",0.217,40,"armR","throw","throw",5.2,11,"grounded"],
["d+1+3~g5","d+1+3","Ground Throw 5","Ground Throw 5","2F+P face-down head",0.217,40,"armR","throw","throw",5.2,11,"grounded"],
["d+1+3~g6","d+1+3","Ground Throw 6","Ground Throw 6","2F+P face-down side",0.217,40,"armR","throw","throw",5.2,11,"grounded"],
["d/f+1+3~hug","d/f+1+3","Bear Hug","Bear Hug","3P+KF+P or 7PF+P",0.233,48,"armR","throw","throw",5.8,13,""],
["d/f+1+3~hugwall","d/f+1+3","Bear Wall","Bear Wall","wall 3P+KF+P or 7PF+P",0.233,52,"armR","throw","throw",5.8,13,"wall"],
["qcf+1+3~back","qcf+1+3","Face Crusher","Face Crusher","236F+P to foe's back",0.233,46,"armR","throw","throw",5.6,13,"back; throw combo starter"],
["d/f+2+4~back","d/f+2+4","Grizzly Rancher","Grizzly Rancher","41236 hold to foe's back",0.267,50,"armR","throw","throw",5.8,13,"back; throw combo starter"],
["d/f+2+4~backwall","d/f+2+4","Grizzly Crash","Grizzly Crash","41236 hold wall behind foe",0.267,55,"armR","throw","throw",6.0,14,"wall, back; throw combo"],
["hcf+1+3~air","hcf+1+3","Catching Hammer Throw","Catching Hammer Throw","41236F+P to foe in air",0.25,46,"armR","throw","throw",5.6,13,"air; throw combo starter"],
["u/b+1+3~hug","u/b+1+3","Bear Hug (alt)","Bear Hug","7PF+P",0.233,48,"armR","throw","throw",5.8,13,"alt input"],
["u/b+1+3~hugwall","u/b+1+3","Bear Wall (alt)","Bear Wall","7PF+P next to wall",0.233,52,"armR","throw","throw",5.8,13,"alt input, wall"],
// ---- throw-combo follow-ups (exact inputs, Tekken chaining) ----
["f+1+3~po","f+1+3","Push Away Follow-up","Push Away","6F+P after 4F+P",0.2,20,"armR","throw","throw",4.5,8,"throw combo follow-up"],
["b+1+3~gb","b+1+3","Get Behind Follow-up","Get Behind","4F+P after 4F+P",0.2,22,"armR","throw","throw",4.5,8,"throw combo follow-up"],
["d+1+3~f5","d+1+3","F5 Slam","F5","22F+P after 4F+P",0.217,30,"armR","throw","throw",5.2,10,"throw combo finisher"],
["1+3~ok","1+3","Oklahoma Stampede Slam","Oklahoma Stampede","F+P after 236F+P",0.2,25,"armR","throw","throw",5.0,9,"throw combo follow-up"],
["d+1+3~md","d+1+3","Manhattan Driver Slam","Manhattan Driver","2F+P after 214F+P",0.217,25,"armR","throw","throw",5.0,9,"throw combo follow-up"],
["u+1+3~md","u+1+3","Manhattan Driver Drop","Manhattan Driver","8F+P after 2F+P",0.217,28,"armR","throw","throw",5.2,10,"throw combo finisher"],
["f+1+3~kp","f+1+3","Kitchen Push Away Slam","Kitchen Push Away","6F+P after 214F+P",0.2,24,"armR","throw","throw",5.0,9,"throw combo follow-up"],
["1+3~fc","1+3","Face Crusher Slam","Face Crusher","F+P after 236F+P (back)",0.2,26,"armR","throw","throw",5.2,9,"throw combo follow-up"],
["d+1+3~gr","d+1+3","Grizzly Rancher Slam","Grizzly Rancher","2F+P after 41236 hold",0.217,28,"armR","throw","throw",5.2,10,"throw combo follow-up"],
["1+3~cht","1+3","Catching Hammer Slam","Catching Hammer Throw","F+P after 41236F+P (air)",0.2,26,"armR","throw","throw",5.2,9,"throw combo follow-up, air"],
// ---- holds -> Tekken reversal slots ----
["b+1+2~p","b+1+2","Half Lock Suplex","Half Lock Suplex","7F vs high punch",0.033,35,"armR","reversal","reversal",4.5,10,"parry: high punch"],
["b+1+2~k","b+1+2","Rolling Press","Rolling Press","7F vs high kick",0.033,35,"armR","reversal","reversal",4.5,10,"parry: high kick"],
["b+2+4~p","b+2+4","Power Pressure","Power Pressure","4F vs mid punch",0.033,38,"armR","reversal","reversal",4.6,10,"parry: mid punch"],
["b+2+4~pwall","b+2+4","Blast Through","Blast Through","4F wall vs mid punch",0.033,42,"armR","reversal","reversal",4.8,11,"parry: mid punch, wall"],
["f+1+2~k","f+1+2","Jurassic Toss","Jurassic Toss","6F vs mid kick",0.033,38,"armR","reversal","reversal",4.6,10,"parry: mid kick"],
["d/b+1+2~p","d/b+1+2","Guillotine Drop","Guillotine Drop","1F vs low punch",0.033,35,"armR","reversal","reversal",4.5,10,"parry: low punch"],
["d/b+1+2~k","d/b+1+2","Giant Hammer Throw","Giant Hammer Throw","1F vs low kick",0.033,35,"armR","reversal","reversal",4.5,10,"parry: low kick"],
["b+1+2~jp","b+1+2","Iron Hammer Press","Iron Hammer Press","4F vs jumping punch",0.033,38,"armR","reversal","reversal",4.6,10,"parry: jumping punch"],
["f+1+2~jk","f+1+2","Buzz Crush","Buzz Crush","6F vs jumping kick",0.033,38,"armR","reversal","reversal",4.6,10,"parry: jumping kick"],
// ---- down attack ----
["u+1+2","u+1+2","Double Knee Drop","Double Knee Drop","8P+K to downed foe",0.25,20,"legR","grounded","strike",3.8,10,"down attack"],
];

// [input, hits[], doa string]
const STRINGS = [
["1,2,1",["1","1,2","1,2,1"],"PPP (Combo Gong)"],
["1,2,d+1",["1","1,2","1,2,d+1"],"PP2P (Combo Hammer)"],
["1,2,3",["1","1,2","1,2,3"],"PPK (Combo High Kick)"],
["1,3,2",["1","1,3","1,3,2"],"PKP (Combo Triple Hit)"],
["1,3,4",["1","1,3","1,3,4"],"PKK (Combo Kick Rush)"],
["f+1,2",["f+1","f+1,2"],"6PP (Wild Swing)"],
["f+1,2,3",["f+1","f+1,2","f+1,2,3"],"6PK (Combo Stomp Kick)"],
["u/f+1,2",["u/f+1","u/f+1,2"],"9PP (Elbow Rush)"],
["u/f+1,2,3",["u/f+1","u/f+1,2","u/f+1,2,3"],"9PKP (Elbow Gong)"],
["u/f+1,2,d+3",["u/f+1","u/f+1,2","u/f+1,2,d+3"],"9PK2P (Elbow Hammer)"],
["u/f+1,3",["u/f+1","u/f+1,3"],"hold-9 PK (Elbow Stomp Combo)"],
["b+1,2,1",["b+1","b+1,2","b+1,2,1"],"4PPP (Stun Gun Chop)"],
["b+1,2,1+2",["b+1","b+1,2","b+1,2,1","b+1,2,1+2"],"4PPP+K (Hell Smasher)"],
["d+1,2",["d+1","d+1,2"],"2PP (Throat Strike)"],
["d/b+1,2",["d/b+1","d/b+1,2"],"1PP (Power Gong)"],
["d/b+1,2,1+2",["d/b+1","d/b+1,2","d/b+1,2,1+2"],"1PP+K (Gong Hell Combo)"],
["d/f+1,2",["d/f+1","d/f+1,2"],"hold-3 PP (The Muscle Man)"],
["d/f,d/f+1,2",["d/f,d/f+1","d/f,d/f+1,2"],"33PP (Buffalo Rage)"],
["f+1+2,1",["f+1+2","f+1+2,1"],"6P+KP (Mad Lariat)"],
["d+1+2,1",["d+1+2","d+1+2,1"],"2P+KP (Buffalo Train)"],
["d+1+2,1,3",["d+1+2","d+1+2,1","d+1+2,1,3"],"2P+KP+K (Bass Special)"],
["f+3,1",["f+3","f+3,1"],"6KP (Knee Hammer)"],
["f+3,4",["f+3","f+3,4"],"6KK (Knee Destroyer)"],
["d/f+3,1",["d/f+3","d/f+3,1"],"3KP (Bass Punch)"],
["d/f+3,4",["d/f+3","d/f+3,4"],"3KK (Kick Rush)"],
["d/b+3,1",["d/b+3","d/b+3,1"],"1KP (Rising Palm)"],
["b+1+3,f+1+3",["b+1+3","f+1+3"],"4F+P, 6F+P (Push Away throw combo)"],
["b+1+3,b+1+3",["b+1+3","b+1+3"],"4F+P, 4F+P (Get Behind throw combo)"],
["b+1+3,d+1+3",["b+1+3","d+1+3"],"4F+P, 22F+P (F5 throw combo)"],
["qcf+1+3,1+3",["qcf+1+3","1+3"],"236F+P, F+P (Oklahoma Stampede throw combo)"],
["qcb+1+3,d+1+3,u+1+3",["qcb+1+3","d+1+3","u+1+3"],"214F+P, 2F+P, 8F+P (Manhattan Driver throw combo)"],
["qcb+1+3,f+1+3",["qcb+1+3","f+1+3"],"214F+P, 6F+P (Kitchen Push Away throw combo)"],
["qcf+1+3,1+3",["qcf+1+3","1+3"],"236F+P, F+P (Face Crusher throw combo, back)"],
["d/f+1+3,d+1+3",["d/f+2+4~back","d+1+3"],"41236 hold, 2F+P (Grizzly Rancher throw combo, back)"],
["d/f+1+3,d+1+3~wall",["d/f+2+4~backwall","d+1+3"],"41236 hold, 2F+P (Grizzly Crash throw combo, wall back)"],
["hcf+1+3,1+3",["hcf+1+3~air","1+3"],"41236F+P, F+P (Catching Hammer Throw combo, air)"],
["d/f+1+3~hug2",["d/f+1+3~hug"],"3P+KF+P / 7PF+P (Bear Hug)"],
["d/f+1+3~hugwall2",["d/f+1+3~hugwall"],"wall Bear Hug (Bear Wall)"],
];

// [input, doa_move, damage, isThrow, note]
const SPECIALS = [
["b,f,b+1+2","Taunt 1",0,false,"464F+P+K taunt"],
["d,d+1+2","Taunt 2",0,false,"22F+P+K taunt"],
["f,f,f+1+2","Vain Abel Rage Art",55,false,"rage art; Flying Cross Chop animation, cinematic"],
["f+1+2~rd","Vain Abel Rage Drive",30,false,"rage drive; Diving Hammer animation, wall splat"],
["1+2+3+4~taunt","Taunt (button)",0,false,"Taunt button alternate for Taunt 1/2"],
["1+2~win","Win Pose 1",0,false,"flex / championship belt pose"],
["2+4~win","Win Pose 2",0,false,"turnbuckle climb pose"],
["f,f~intro","Ring Intro",0,false,"wrestler ring entrance walk"],
["b,b~stance","Fighting Stance",0,false,"pro-wrestler stance"],
];

function slug(s){return s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');}

const moves = {};
for (const [key,input,name,doa_move,doa_input,startup,dmg,limb,hit_level,mclass,knock,soul,note] of MOVES) {
  const isThrow = mclass === 'throw';
  const isRev = mclass === 'reversal';
  moves[key] = {
    name: `${name} (DOA Bass ${doa_input})`,
    input, doa_source: "bass-armstrong", doa_move, doa_input,
    startup: S(startup), active: isThrow||isRev ? 0.05 : 0.033,
    recovery: isThrow ? 0.5 : isRev ? 0.4 : +(startup + 0.25).toFixed(3),
    damage: dmg, limb, heavy: dmg >= 34 || /heavy|launcher/i.test(note||''),
    knock, soulGain: soul, anim_ref: `doa:bass:${slug(name)}`,
    move_class: mclass, hit_level, input_slots: [input],
    ...(note ? { note } : {}),
  };
}
const strings = {};
STRINGS.forEach(([input,hits,doa],i)=>{ strings[i] = { input, hits, doa }; });
const specials = {};
SPECIALS.forEach(([input,doa_move,damage,isThrow,note],i)=>{ specials[i] = { input, doa_move, damage, throw: isThrow, note }; });

// merge unique entries from the existing placeholder file (passed as argv[2])
let merged = 0;
try {
  const oldPath = process.argv[2];
  if (oldPath) {
    const old = JSON.parse(readFileSync(oldPath,'utf8'));
    const seen = new Set(Object.values(moves).map(m=>m.doa_move));
    for (const [k,m] of Object.entries(old.moves||{})) {
      if (m.doa_move && !seen.has(m.doa_move) && !moves[k]) { moves[k+'~legacy'] = m; seen.add(m.doa_move); merged++; }
    }
    for (const [k,s] of Object.entries(old.specials||{})) {
      if (!Object.values(specials).some(x=>x.doa_move===s.doa_move)) { specials['l'+k] = s; merged++; }
    }
  }
} catch(e){ console.error('merge skipped:', e.message); }

const out = {
  fighter: "vainabel",
  display: "VAIN ABEL ELIAS",
  tekken_base: "Bass Armstrong (DOA4) — full Tekken-notation conversion",
  doa_source: "deadoralive.fandom.com Bass/Dead_or_Alive_4_command_list (111 named entries) + prior DOA2/DOA5/DOA6 triangulated base",
  proxy: false, proxy_note: null, schema_version: 2, variant: 8,
  moves, strings, specials,
  frame_convention: "INPUT-TO-MOVE FIDELITY LAW: DOA P/K/G+dir -> Tekken 1/2/3/4+dir. Every DOA move has one specific Tekken input. Tekken frame conventions @60fps: i10 jab 0.167, throws i12 0.2, launchers i15-i18. Damage on Tekken scale (jab 7, throws 38-55). Bass archetype: slowest striker, hardest grappler.",
  union_merge: null, hit_words: null, stance_after: null,
  conversion_note: "Bass -> Vain Abel is the TEMPLATE for all DOA->WH wiring. Bass animations used; timing/hit properties/combo structure follow Tekken conventions.",
};
process.stdout.write(JSON.stringify(out, null, 1));
console.error(`moves=${Object.keys(moves).length} strings=${Object.keys(strings).length} specials=${Object.keys(specials).length} merged_legacy=${merged} TOTAL=${Object.keys(moves).length+Object.keys(strings).length+Object.keys(specials).length}`);
