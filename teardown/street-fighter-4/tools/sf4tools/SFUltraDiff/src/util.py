import os, struct, sys
import pprint
import difflib
import json
import fnmatch
import hashlib
from collections import OrderedDict,defaultdict
XBOX_PATH = "Z:\\SF4 Engine STuff\\XBOX AE\\battle.eaf.out\\chara\\"
PC_PATH = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Super Street Fighter IV - Arcade Edition\\resource\\battle\\chara\\"
PRETTY = True;
def hexprint(data):
    for thing in data:
        print( hex(thing),)
    print()
def readNameOffsetTable(f,offset,count,MODE):
    f.seek(offset)
    offsets = []
    names = []
    for i in range(0,count):
        offsets.append(struct.unpack(MODE+"I",f.read(4))[0])
    for offset in offsets:
        if offset == 0:
            names.append("")
        else:
            f.seek(offset)
            names.append(f.read(255).split(b"\x00")[0].decode(encoding='UTF-8'))
    return names
def findFiles(char,path,ext):
    matches = []
    for root, dirnames, filenames in os.walk(path):
        #print( filenames)
        for filename in fnmatch.filter(filenames, char+ext):
            matches.append(os.path.join(root, filename))
    return matches
InputEnum = { 0:"None",0x1:"NEUTRAL",0x2:"UP",0x4:"DOWN",0x8:"BACK",0x10:"FORWARD", \
              0x40:"LP",0x80:"MP",0x100:"HP",0x200:"LK",0x400:"MK",0x800:"HK"}
RestrictionFlags = {}
RestrictionFlags[0x00] = "NONE"
RestrictionFlags[0x01] = "PROJECTILE"
RestrictionFlags[0x04] = "WEAPON"
RestrictionFlags[0x08] = "NO_WEAPON"
RestrictionFlags[0x10] = "CLAW_MASK"
RestrictionFlags[0x20] = "CLAW_NO_MASK"
RestrictionFlags[0x40] = "STANCE"
RestrictionFlags[0x80] = "ULTRA"
MoveFlags = {}
MoveFlags[0x00] = "NONE"
MoveFlags[0x01] = "LAZY_STICK"
MoveFlags[0x02] = "STRICT_STICK"
MoveFlags[0x10] = "BUTTONS"
MoveFlags[0x20] = "ALL_BUTTONS"
MoveFlags[0x40] = "ANY_TWO"
MoveFlags[0x100] = "SUPER_JUMP_MOTION?"
MoveFlags[0x200] = "ANY_DIRECTION"
MoveFlags[0x400] = "STICK"
MoveFlags[0x1000] = "ON_PRESS"
MoveFlags[0x2000] = "ON_RELEASE"
MoveFlags[0x4000] = "UNK1" 
MoveFlags[0x8000] = "UNK2"
#BAC
FlowType = {}
FlowType[0x00] = "ALWAYS"
FlowType[0x01] = "ON_HIT"
FlowType[0x02] = "ON_BLOCK"
FlowType[0x03] = "ON_WHIFF"
FlowType[0x04] = "ON_GROUP_HIT"
FlowType[0x05] = "ON_GROUP_GUARD"
FlowType[0x06] = "ON_GROUP_WHIFF"
FlowType[0x07] = "ON_LEAVE_GROUND"
FlowType[0x08] = "ON_LAND"
FlowType[0x09] = "ON_WALL"
FlowType[0x0A] = "ON_INTO_RANGE"
FlowType[0x0B] = "ON_RELEASE"
FlowType[0x0C] = "ON_INPUT"
FlowType[0x0F] = "ON_ABSORB"
FlowType[0x10] = "ON_COUNTER_ATK"
FlowType[0x11] = "ON_KO"
FlowType[0x12] = "ON_WEAPON_CHG"
AnimationType = {}
AnimationType[0x00] = "NORMAL"
AnimationType[0x01] = "FACE"
AnimationType[0x02] = "CAMERA"
AnimationType[0x03] = "RIVAL1"
AnimationType[0x04] = "RIVEAL2"
AnimationType[0x05] = "UC1"
AnimationType[0x06] = "UC2"
StateFlags = {}
StateFlags[0x00] = "NONE"
StateFlags[0x01] = "STAND"
StateFlags[0x02] = "CROUCH"
StateFlags[0x04] = "AIR"

StateFlags[0x10] = "COUNTERHIT"

StateFlags[0x40] = "FORCE_TURN"
StateFlags[0x80] = "CAN_TURN"
StateFlags[0x100] = "FLIP"
StateFlags[0x200] = "KEEP_CMD_SIDE"
StateFlags[0x400] = "HOVERING"
StateFlags[0x800] = "IMMOVEABLE_MYSELF"
StateFlags[0x1000] = "IMMOVEABLE_TARGET"
StateFlags[0x2000] = "INVIS_MYSELF"
StateFlags[0x4000] = "INVIS_TARGET" 
StateFlags[0xF8000] = "IGNORE_PHYSICS_YZ"
StateFlags[0x100000] = "IGNORE_PHYSICS_X"
StateFlags[0x200000] = "IGNORE_COUNTER_ATK"
HitboxFlags = {}
HitboxFlags[0x00] = "NONE"
HitboxFlags[0x04] = "UNBLOCKABLE"
HitboxFlags[0x08] = "BREAK_ARMOR"
HitboxFlags[0x10] = "BREAK_COUNTER"

HitboxFlags[0x20] = "CAN_CROSSUP"

HitboxFlags[0x40] = "DONT_HIT_STANDING"
HitboxFlags[0x80] = "DONT_HIT_CROUCHING"
HitboxFlags[0x100] = "DONT_HIT_AIR"
HitboxFlags[0x200] = "DONT_HIT_FRONT"
HitboxFlags[0x400] = "DONT_HIT_JUMP_START"
HitboxFlags[0x800] = "DONT_HIT_IF_HAVE_WEAPON"
HitboxFlags[0x1000] = "DONT_HIT_IF_NO_WEAPON"
HitboxFlags[0x2000] = "GET_TARGET_SIDE"
HitboxFlags[0x4000] = "IGNORE_KO" 
HitboxFlags[0x8000] = "IGNORE_ANIM"
VulFlags = {}
VulFlags[0x00] = "NONE"
VulFlags[0x01] = "PUSH"
VulFlags[0x02] = "HIT"
VulFlags[0x04] = "THROW"
VulFlags[0x08] = "PROJECTILE"
VulFlags[0x10] = "ABSORB_HIT"
VulFlags[0x20] = "ABSORB_THROW"
VulFlags[0x40] = "DONT_HIT_STANDING"
VulFlags[0x80] = "DONT_HIT_STANDING"
BodyFlags = {}
BodyFlags[0x00] = "ALL"
BodyFlags[0x01] = "WAIST"
BodyFlags[0x02] = "STOMACH"
BodyFlags[0x04] = "CHEST"
BodyFlags[0x08] = "HEAD"
BodyFlags[0x10] = "L_SHOULDER"
BodyFlags[0x20] = "L_ELBOW"
BodyFlags[0x40] = "L_WRIST"
BodyFlags[0x80] = "L_HAND"
BodyFlags[0x100] = "L_HIP"
BodyFlags[0x200] = "L_KNEE"
BodyFlags[0x400] = "L_ANKLE"
BodyFlags[0x800] = "L_FOOT"
BodyFlags[0x1000] = "R_SHOULDER"
BodyFlags[0x2000] = "R_ELBOW"
BodyFlags[0x4000] = "R_WRIST" 
BodyFlags[0xF8000] = "R_HAND"
BodyFlags[0x100000] = "R_HIP"
BodyFlags[0x200000] = "R_KNEE"
BodyFlags[0x400000] = "R_ANKLE"
BodyFlags[0x800000] = "R_FOOT"
BodyFlags[0x1000000] = "L_ARM"
BodyFlags[0x2000000] = "L_LEG"
BodyFlags[0x4000000] = "R_ARM"
BodyFlags[0x8000000] = "R_LEG"
def flags(set,data):
    s = []
    for thing,label in set.items():
        if thing == 0 and data == 0:
            s.append(label)
        elif data & thing:
            s.append(label)
    return "|".join(s)+"="+hex(data)
def rflags(set,data):
        tmp = int(data.split("=")[-1])
        print tmp
        return tmp
def enum(set,data):
    if data in set.keys():
        return set[data]
    return data
def renum(set,data):
    set = {v:k for k, v in set.items()}
    if data in set.keys():
        return set[data]
    return data
