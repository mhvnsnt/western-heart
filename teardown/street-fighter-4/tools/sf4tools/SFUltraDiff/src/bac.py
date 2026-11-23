import os, struct, sys
import pprint
import difflib
import json
import fnmatch
import hashlib
import bcm
from collections import OrderedDict, defaultdict
from util import *
class BACFile(OrderedDict):
    def toJSON(self):
        return json.dumps(self, indent=5)
    @staticmethod
    def readNames(filename):
        global MODE
        f = open(filename, "rb")
        #print( "----------------------------------------- ", filename)
        TAG = f.read(4)
        if(TAG != b"#BAC"):
            raise Exception("Don't think this is a BAC File..." + str(TAG))
        EndianFlag = struct.unpack("H", f.read(2))[0]
        if(EndianFlag == 0xFFFE):
            MODE = "<"
        else:
            MODE = ">"
        f.seek(12)
        HEADER = struct.unpack(MODE + "HHHH5I", f.read(28))
        json.dumps(HEADER, indent=5)

        ScriptNames = readNameOffsetTable(f, HEADER[6], HEADER[0], MODE)
        VFXScriptNames = readNameOffsetTable(f, HEADER[7], HEADER[1], MODE)
        return ScriptNames,VFXScriptNames
        
    def __init__(self, filename):
        super(BACFile, self).__init__()
        global MODE,ScriptNames,VFXScriptNames,ChargeNames,InputNames,MoveNames,CancelListNames
        f = open(filename, "rb")
        #print( "----------------------------------------- ", filename)
        TAG = f.read(4)
        if(TAG != b"#BAC"):
            raise Exception("Don't think this is a BAC File..." + str(TAG))
        EndianFlag = struct.unpack("H", f.read(2))[0]
        if(EndianFlag == 0xFFFE):
            MODE = "<"
        else:
            MODE = ">"
        f.seek(12)
        HEADER = struct.unpack(MODE + "HHHH5I", f.read(28))
        json.dumps(HEADER, indent=5)

        '''Read Unknown FloatData'''
        self["Floats"] = []
        for i in range(0, 0x1C):
            self["Floats"].append(struct.unpack(MODE + "6f", f.read(24)))

        ScriptNames = readNameOffsetTable(f, HEADER[6], HEADER[0], MODE)
        VFXScriptNames = readNameOffsetTable(f, HEADER[7], HEADER[1], MODE)
        ChargeNames,InputNames,MoveNames,CancelListNames = bcm.BCMFile.readNames((filename[0:-4]+".bcm"))
        '''Read Scripts'''
        self["HitBoxUsage"] = defaultdict(set)
        self["Scripts"] = OrderedDict()
        for i in range(0,HEADER[0]):
            f.seek(HEADER[4]+i*4)
            offset = struct.unpack(MODE + "I", f.read(4))[0]
            if offset == 0:
                continue
            self["Scripts"][ScriptNames[i]] = self.readScript(f,offset,ScriptNames[i])

        '''Read VFXScripts'''
        self["VFXScripts"] = OrderedDict()
        for i in range(0,HEADER[1]):
            f.seek(HEADER[5]+i*4)
            offset = struct.unpack(MODE + "I", f.read(4))[0]
            if offset == 0:
                continue
            self["VFXScripts"][VFXScriptNames[i]] = self.readScript(f,offset,VFXScriptNames[i])
        '''Read HitBoxTable'''
        self["HitboxTable"] = OrderedDict()
        for i in range(0,HEADER[2]):
            f.seek(HEADER[8]+i*4)
            offset = struct.unpack(MODE + "I", f.read(4))[0]
            if offset == 0:
                continue
            f.seek(offset)

            hitbox = OrderedDict()
            hitbox["Name"] = list(self["HitBoxUsage"][i])
            #print( self["HitBoxUsage"][i])
            self["HitboxTable"][i] = hitbox
            for j in range(0,12):
                data = OrderedDict()
                hitbox[j] = data
                data["Name"] = ["HIT_STANDING","HIT_CROUCHING","HIT_AIR",
        "BLOCK_STANDING","BLOCK_CROUCHING","BLOCK_AIR?",
        "COUNTERHIT_STANDING","COUNTERHIT_CROUCHING","COUNTERHIT_AIR",
        "UNKNOWN_STANDING","UNKNOWN_CROUCHING","UNKNOWN_AIR"][j]
                data["Damage"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["Stun"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["Effect"] = ["HIT","SCRIPT","BLOCK","BLOCK2","BLOW","BLOW2","BOUND","BOUND2"][struct.unpack(MODE + "h", f.read(2))[0]]
                data["OnHit"] = struct.unpack(MODE + "h", f.read(2))[0]
                if data["Effect"] == "HIT":
                    idx = 0x83
                elif data["Effect"] == "BLOCK":
                    idx = 0x44
                elif data["Effect"] == "BLOW":
                    idx = 0xC0
                elif data["Effect"] == "BOUND":
                    idx = 0x1A
                else:
                    idx = 0
                data["OnHit"] = enum(dict(enumerate(ScriptNames)),data["OnHit"]+idx)
                data["SelfHitstop"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["SelfShaking"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["TargetHitstop"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["TargetShaking"] = struct.unpack(MODE + "h", f.read(2))[0]

                data["HitGFX"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["Unknown1"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["Unknown2"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["Unused"] = struct.unpack(MODE + "h", f.read(2))[0]

                data["HitGFX2"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["Unused"] = struct.unpack(MODE + "3h", f.read(6))

                data["HitSFX"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["HitSFX2"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["TargetSFX"] = struct.unpack(MODE + "h", f.read(2))[0]

                data["ArcadeScore"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["SelfMeter"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["TargetMeter"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["JuggleStart"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["TargetAnimationTime"] = struct.unpack(MODE + "h", f.read(2))[0]
                data["MiscFlag"] = struct.unpack(MODE + "i", f.read(4))[0]

                data["VelocityX"] = struct.unpack(MODE + "f", f.read(4))[0]
                data["VelocityY"] = struct.unpack(MODE + "f", f.read(4))[0]
                data["VelocityZ"] = struct.unpack(MODE + "f", f.read(4))[0]
                data["PushbackDistance"] = struct.unpack(MODE + "f", f.read(4))[0]
                data["AccelerationX"] = struct.unpack(MODE + "f", f.read(4))[0]
                data["AccelerationY"] = struct.unpack(MODE + "f", f.read(4))[0]
                data["AccelerationZ"] = struct.unpack(MODE + "f", f.read(4))[0]

        self.pop("HitBoxUsage", None)


    def readScript(self,f,offset,name):
        global MODE,ScriptNames,VFXScriptNames,ChargeNames,InputNames,MoveNames,CancelListNames
        f.seek(offset)
        script = OrderedDict()
        script["Name"] = name
        script["FirstHitboxFrame"] = struct.unpack(MODE + "H", f.read(2))[0]
        script["LastHitboxFrame"] = struct.unpack(MODE + "H", f.read(2))[0]
        script["IASAFrame"] = struct.unpack(MODE + "H", f.read(2))[0]
        script["TotalFrames"] = struct.unpack(MODE + "H", f.read(2))[0]

        script["UnknownFlags1"] = struct.unpack(MODE + "I", f.read(4))[0]
        script["UnknownFlags2"] = struct.unpack(MODE + "HH", f.read(4))[0]
        script["UnknownFlags3"] = struct.unpack(MODE + "H", f.read(2))[0]
        
        CommandListCount = struct.unpack(MODE + "H", f.read(2))[0]

        #script["HeaderSize"] = 
        struct.unpack(MODE + "I", f.read(4))[0]
        BaseOffset = f.tell()

        script["CommandLists"] = OrderedDict()
        for i in range(0,CommandListCount):
            f.seek(BaseOffset+12*i)

            #commandList = OrderedDict()
            commandList = []
            type = ["FLOW","ANIMATION","TRANSITION","STATE","SPEED","PHYSICS","CANCELS","HITBOX","INVINC","HURTBOX","ETC","TARGETLOCK","SFX"][struct.unpack(MODE + "H", f.read(2))[0]]
            CommandCount = struct.unpack(MODE + "H", f.read(2))[0]
            script["CommandLists"][type] = commandList

            FrameOffset = struct.unpack(MODE + "I", f.read(4))[0]
            DataOffset = struct.unpack(MODE + "I", f.read(4))[0]
            
            for j in range(0,CommandCount):
                command = OrderedDict()
                f.seek(BaseOffset+ FrameOffset+12*i+j*4)
                command["StartFrame"] = struct.unpack(MODE + "H", f.read(2))[0]
                command["EndFrame"] = struct.unpack(MODE + "H", f.read(2))[0]

                commandList.append(command)
            f.seek(BaseOffset+DataOffset+12*i)
            for j in range(0,CommandCount):
                command = commandList[j]
                if type == "FLOW":
                    command["Type"] = enum(FlowType,struct.unpack(MODE + "h", f.read(2))[0])
                    command["Input"] = struct.unpack(MODE + "H", f.read(2))[0]
                    command["TargetScript"] = enum(dict(enumerate(ScriptNames)),struct.unpack(MODE + "h", f.read(2))[0])
                    command["TargetScriptFrame"] = struct.unpack(MODE + "h", f.read(2))[0]
                elif type == "ANIMATION":
                    command["Animation"] = struct.unpack(MODE + "H", f.read(2))[0]
                    command["AnimationType"] = enum(AnimationType,struct.unpack(MODE + "B", f.read(1))[0])
                    command["Unknown"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["AnimationFrameStart"] = struct.unpack(MODE + "h", f.read(2))[0]
                    command["AnimationFrameEnd"] = struct.unpack(MODE + "h", f.read(2))[0]
                elif type == "TRANSITION":
                    command["Flag1"] = struct.unpack(MODE + "HH", f.read(4))
                    command["Floats"] = struct.unpack(MODE + "5fI", f.read(24))
                elif type == "STATE":
                    command["Flag1"] = flags(StateFlags,struct.unpack(MODE + "I", f.read(4))[0])
                    command["Flag2"] = struct.unpack(MODE + "I", f.read(4))[0]
                elif type == "SPEED":
                    command["Multiplier"] = struct.unpack(MODE + "f", f.read(4))[0]
                elif type == "CANCELS":
                    command["Condition"] = struct.unpack(MODE + "I", f.read(4))[0]
                    command["CancelList"] = enum(dict(enumerate(CancelListNames)),struct.unpack(MODE + "I", f.read(4))[0])
                elif type == "HURTBOX":
                    command["X"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Y"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Rotation"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Width"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Height"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["FloatUnknown"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Unknown1"] = struct.unpack(MODE + "I", f.read(4))[0]
                    command["Unused"] = struct.unpack(MODE + "H", f.read(2))[0]
                    command["UnknownBytes"] = struct.unpack(MODE + "BB", f.read(2))[0]
                elif type == "PHYSICS":
                    command["VelocityX"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["VelocityY"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Unknown1"] = struct.unpack(MODE + "I", f.read(4))[0]
                    command["Flags"] = struct.unpack(MODE +"I", f.read(4))[0]
                    command["AccelerationX"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["AccelerationY"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["UnknownBytes"] = struct.unpack(MODE + "2I", f.read(8))
                elif type == "ETC":
                    
                    command["CommandType"] = enum({0:"CONTROL",5:"GFX",6:"GFX2"},struct.unpack(MODE + "H", f.read(2))[0])
                    if command["CommandType"] == "CONTROL":
                        command["ControlType"] = enum({0:"UNKNOWN",2:"VFX_SCRIPT",5:"SUPERFLASH",6:"THROW_TECH",\
                                        11:"STICK_MOVEMENT",12:"AIR_TRACKING",13:"MOVE_TO_WALL", 14:"TELEPORT", 15:"DROP_KNIFE",28:"ANGRY_SCAR"}, \
                                        struct.unpack(MODE + "H", f.read(2))[0])
                    else:
                        command["ControlType"] = struct.unpack(MODE + "H", f.read(2))[0]
                    command["RawParams"] = struct.unpack(MODE + "7I", f.read(28))
                elif type == "HITBOX":
                    command["X"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Y"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Z?"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Width"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Height"] = struct.unpack(MODE + "f", f.read(4))[0]
                    command["Depth?"] = struct.unpack(MODE + "I", f.read(4))[0]
                    command["ID"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["Juggle"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["Type"] = ["PROXIMITY","NORMAL","GRAB","PROJECTILE","REFLECT"][struct.unpack(MODE + "B", f.read(1))[0]]
                    command["HitLevel"] = ["MID","OVERHEAD","LOW","UNBLOCKABLE","AIR_ONLY"][struct.unpack(MODE + "B", f.read(1))[0]]
                    command["HitFlags"] = flags(HitboxFlags,struct.unpack(MODE + "H", f.read(2))[0])
                    command["Unknown1"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["Unknown2"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["Hits"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["JugglePotential"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["JuggleIncrement"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["JuggleIncrementLimit"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["HitboxEffect"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["Unknown3"] = struct.unpack(MODE + "B", f.read(1))[0]
                    command["Unused2"] = struct.unpack(MODE + "H", f.read(2))[0]
                    command["HitboxData"] = struct.unpack(MODE + "I", f.read(4))[0]
                    if command["Type"] != "PROXIMITY":
                        self["HitBoxUsage"][command["HitboxData"]].add("{0}#{1}".format(name,command["ID"]))

                elif type == "INVINC":
                    command["Flags"] = flags(VulFlags,struct.unpack(MODE + "I", f.read(4))[0])
                    command["Exception"] = flags(BodyFlags,struct.unpack(MODE + "I", f.read(4))[0])
                    command["Unknown"] = struct.unpack(MODE + "4B2H", f.read(8))
                elif type == "TARGETLOCK":
                    command["Type"] = struct.unpack(MODE + "i", f.read(4))[0]
                    command["Script"] = struct.unpack(MODE + "i", f.read(4))[0]
                    command["Unknown"] = struct.unpack(MODE + "2i", f.read(8))
                elif type == "SFX":
                    command["Type"] = struct.unpack(MODE + "H", f.read(2))[0]
                    command["Sound"] = struct.unpack(MODE + "H", f.read(2))[0]
                    command["Unknown"] = struct.unpack(MODE + "3i", f.read(12))
                else:
                    raise Exception(type)
        return script
def doAll():
    for char in os.listdir(PC_PATH):
        print( char)
        #print( "PC")
        versions = defaultdict(list)
        versions_data = {}
        for file in findFiles(char,'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Super Street Fighter IV - Arcade Edition\\',".bac"):
            test = BACFile(file)
            test_text = json.dumps(test.Floats, indent=5).splitlines()+json.dumps(test.Scripts, indent=5).splitlines()+json.dumps(test.VFXScripts, indent=5).splitlines()
            m = hashlib.md5()
            m.update(repr(test_text))
            if  m.hexdigest not in versions.keys():
                f = open("../out/"+char+".bac_"+m.hexdigest()+".txt","w")
                for line in test_text:
                    f.write(line)
                    f.write("\n")
            f.close()
            versions[m.hexdigest()].append(file)
        #print( "XBOX")
        for file in findFiles(char,'Z:\\SF4 Engine STuff\\XBOX AE\\',".bac"):
            test = BACFile(file)
            test_text = json.dumps(test.Floats, indent=5).splitlines()+json.dumps(test.Scripts, indent=5).splitlines()+json.dumps(test.VFXScripts, indent=5).splitlines()
            m = hashlib.md5()
            m.update(repr(test_text))
            if  m.hexdigest not in versions.keys():
                f = open("../out/"+char+".bac_"+m.hexdigest()+".txt","w")
                for line in test_text:
                    f.write(line)
                    f.write("\n")
                f.close()
            versions[m.hexdigest()].append(file)


        print( json.dumps(versions, indent=5))

def doChar(c):
    pc = BACFile(PC_PATH + c + "\\" + c + ".bac")
    f = open("../json/"+c+".json.txt", "w")
    pctxt = pc.toJSON()
    print( "Writing diff")
    f.write(pctxt)
    f.close()
    print( "DONE")
def diffChar(c):
    pc = BACFile(PC_PATH + c + "\\" + c + ".bac")
    xbox = BACFile(XBOX_PATH + c + "\\" + c + ".bac")
    htmlDiff = difflib.HtmlDiff()
    f = open("diff.txt", "w")
    pctxt = json.dumps(pc.Floats, indent=5).splitlines()+json.dumps(pc.Scripts, indent=5).splitlines()+json.dumps(pc.VFXScripts, indent=5).splitlines()+json.dumps(pc.HitboxTable, indent=5).splitlines()
    xboxtxt = json.dumps(xbox.Floats, indent=5).splitlines()+json.dumps(xbox.Scripts, indent=5).splitlines()+json.dumps(xbox.VFXScripts, indent=5).splitlines()+json.dumps(xbox.HitboxTable, indent=5).splitlines()
    print( "Writing diff")
    f.write(htmlDiff.make_file(pctxt,xboxtxt,context=True, numlines=30))
    f.close()
    print( "DONE")
