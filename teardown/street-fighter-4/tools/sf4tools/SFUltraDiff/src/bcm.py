import os, struct, sys
import pprint
import difflib
import json
import fnmatch
import hashlib
import bac
from util import *
from collections import OrderedDict,defaultdict

class BCMFile(OrderedDict):
    def toJSON(self):
        return json.dumps(self, indent=5)
    @staticmethod
    def readNames(filename):
        global MODE,PRETTY
        f = open(filename,"rb")
        #print( "----------------------------------------- ",filename)
        TAG = f.read(4)
        if(TAG != b"#BCM"):
            raise Exception(b"Don't think this is a BCM File..."+TAG)
        EndianFlag = struct.unpack("H",f.read(2))[0]
        if(EndianFlag == 0xFFFE):
            MODE = "<"
        else:
            MODE = ">"
        struct.unpack(MODE+"HHHHH",f.read(10))

        HEADER = struct.unpack(MODE+"4H8I",f.read(40))
        #hexprint((HEADER))

        ChargeNames = readNameOffsetTable(f,HEADER[5],HEADER[0],MODE)
        InputNames = readNameOffsetTable(f,HEADER[7],HEADER[1],MODE)
        MoveNames = readNameOffsetTable(f,HEADER[9],HEADER[2],MODE)
        CancelListNames = readNameOffsetTable(f,HEADER[11],HEADER[3],MODE)
        return ChargeNames,InputNames,MoveNames,CancelListNames
     
    def __init__(self,filename):
        print( filename)
        super(BCMFile, self).__init__()
        global MODE
        f = open(filename,"rb")
        #print( "----------------------------------------- ",filename)
        TAG = f.read(4)
        if(TAG != b"#BCM"):
            raise Exception(b"Don't think this is a BCM File..."+TAG)
        EndianFlag = struct.unpack("H",f.read(2))[0]
        if(EndianFlag == 0xFFFE):
            MODE = "<"
        else:
            MODE = ">"
        struct.unpack(MODE+"HHHHH",f.read(10))

        HEADER = struct.unpack(MODE+"4H8I",f.read(40))
        #hexprint((HEADER))

        ChargeNames = readNameOffsetTable(f,HEADER[5],HEADER[0],MODE)
        InputNames = readNameOffsetTable(f,HEADER[7],HEADER[1],MODE)
        MoveNames = readNameOffsetTable(f,HEADER[9],HEADER[2],MODE)
        CancelListNames = readNameOffsetTable(f,HEADER[11],HEADER[3],MODE)
        ScriptNames,VFXScriptNames = bac.BACFile.readNames(filename[0:-4]+".bac")
        #print( ChargeNames)
        #print( InputNames)
        #print( MoveNames)
        #print( CancelListNames)
        '''Read Charges'''
        f.seek(HEADER[4])
        self["Charges"] = OrderedDict()
        for i in range(0,HEADER[0]):
            charge = {}
            #charge["Name"] = ChargeNames[i]
            charge["Input"] = struct.unpack(MODE+"H",f.read(2))[0]
            charge["Unknown1"] = struct.unpack(MODE+"H",f.read(2))[0]
            charge["MoveFlags"] = struct.unpack(MODE+"H",f.read(2))[0]
            charge["Frames"] = struct.unpack(MODE+"H",f.read(2))[0]
            charge["Frames2"] = struct.unpack(MODE+"H",f.read(2))[0]
            charge["Unknown3"] = struct.unpack(MODE+"H",f.read(2))[0]
            charge["StorageIndex"] = struct.unpack(MODE+"I",f.read(4))[0]
            self["Charges"][ChargeNames[i]] = charge
        '''Read Inputs'''

        self["Inputs"] = {}
        for i in range(0,HEADER[1]):
            f.seek(HEADER[6]+i*0xC4)
            input = []
            #input["Name"] = InputNames[i]
            count =  struct.unpack(MODE+"I",f.read(4))[0]
            for j in range(0,count):
                entry = {}
                entry["Type"] = struct.unpack(MODE+"H",f.read(2))[0]
                entry["Buffer"] = struct.unpack(MODE+"H",f.read(2))[0]
                entry["Input"] = struct.unpack(MODE+"H",f.read(2))[0]

                entry["MoveFlags"] = struct.unpack(MODE+"H",f.read(2))[0]
                entry["Flags"] = struct.unpack(MODE+"H",f.read(2))[0]
                entry["Requirement"] = struct.unpack(MODE+"H",f.read(2))[0]
                if PRETTY:
                    entry["Type"] = ["NORMAL","CHARGE","360","MASH"][entry["Type"]]
                    entry["Input"] = flags(InputEnum,entry["Input"])
                    entry["Requirement"] = flags({0:"Normal",1:"Lenient",2:"Mash"},entry["Requirement"])
                input.append(entry)
            self["Inputs"][InputNames[i]] = input
        '''Read MOVES'''

        self["Moves"] = OrderedDict()
        for i in range(0,HEADER[2]):
            f.seek(HEADER[8]+i*0x54)
            move= OrderedDict()
            #charge["Name"] = ChargeNames[i]
            move["Input"] = flags(InputEnum,struct.unpack(MODE+"H",f.read(2))[0])
            move["MoveFlags"] = flags(MoveFlags,struct.unpack(MODE+"H",f.read(2))[0])
            move["PositionRestriction"] = enum({0:"NONE",1:"FAR",2:"CLOSE",3:"HIGH",4:"LOW"},struct.unpack(MODE+"H",f.read(2))[0])
            move["Restriction"] = flags(RestrictionFlags,struct.unpack(MODE+"H",f.read(2))[0])

            move["Unknown1"] = struct.unpack(MODE+"H",f.read(2))[0]
            move["StateRestriction"] = flags({0:"NONE",4:"AIR"},struct.unpack(MODE+"H",f.read(2))[0])
            move["Unknown2"] = struct.unpack(MODE+"H",f.read(2))[0]
            move["MiscRestriction"] = struct.unpack(MODE+"B",f.read(1))[0]

            move["Unknown3"] = struct.unpack(MODE+"B",f.read(1))[0]
            move["UltraRestriction"] = struct.unpack(MODE+"B",f.read(1))[0]
            move["UltraRestriction?"] = struct.unpack(MODE+"3B",f.read(3))[0]
            move["PositionRestrictionDistance"] = struct.unpack(MODE+"f",f.read(4))[0]

            move["EXRequirement"] = struct.unpack(MODE+"h",f.read(2))[0]
            move["EXCost"] = struct.unpack(MODE+"h",f.read(2))[0]
            move["UltraRequirement"] = struct.unpack(MODE+"h",f.read(2))[0]
            move["UltraCost"] = struct.unpack(MODE+"h",f.read(2))[0]

            move["InputMotion"] = struct.unpack(MODE+"i",f.read(4))[0]
            if move["InputMotion"] != -1:
               move["InputMotion"] = InputNames[move["InputMotion"]]
            move["Script"] = enum(dict(enumerate(ScriptNames)),struct.unpack(MODE+"I",f.read(4))[0])
           
            if not PRETTY:
                move["AIMoveFeatures"] = struct.unpack(MODE+"I",f.read(4))[0]
                move["AIMinRange"] = struct.unpack(MODE+"f",f.read(4))[0]
                move["AIMaxrange"] = struct.unpack(MODE+"f",f.read(4))[0]
                move["AIUnknown1"] = struct.unpack(MODE+"I",f.read(4))[0]

                move["CPUPassiveMove"] = struct.unpack(MODE+"I",f.read(4))[0]
                move["CPUCounterMove"] = struct.unpack(MODE+"H",f.read(2))[0]
                move["CPUVsStand"] = struct.unpack(MODE+"H",f.read(2))[0]
                move["CPUVsAir"] = struct.unpack(MODE+"H",f.read(2))[0]

                move["CPUVsDown"] = struct.unpack(MODE+"H",f.read(2))[0]
                move["CPUVsStunned"] = struct.unpack(MODE+"H",f.read(2))[0]
                move["CPUProbeMove"] = struct.unpack(MODE+"H",f.read(2))[0]
                move["CPUVsVeryClose"] = struct.unpack(MODE+"H",f.read(2))[0]

                move["CPUVsClose"] = struct.unpack(MODE+"H",f.read(2))[0]
                move["CPUVsMidRange"] = struct.unpack(MODE+"H",f.read(2))[0]
                move["CPUVsFar"] = struct.unpack(MODE+"H",f.read(2))[0]
                move["CPUVsVeryFar"] = struct.unpack(MODE+"H",f.read(2))[0]
            if PRETTY:
                pass
            

            self["Moves"][MoveNames[i]] = move
        '''Read Cancels'''

        self["CancelLists"] = {}
        for i in range(0,HEADER[3]):
            f.seek(HEADER[10]+i*0x8)
            cancellist = []
            count = struct.unpack(MODE+"HH",f.read(4))[0]
            offset =  struct.unpack(MODE+"I",f.read(4))[0]
            f.seek(offset-8,1)
            for j in range(0,count):
                index = struct.unpack(MODE+"H",f.read(2))[0]
                #print( index)
                if index > -1 and index < len(MoveNames):
                    cancellist.append(MoveNames[index])
                else:
                    cancellist.append(index)
            self["CancelLists"][CancelListNames[i]] = cancellist
    def toFile(self,filename,console=True):
        out = open(filename,"wb")
        out.write(b"#BCM")
        MODE = "<"
        if console:
            MODE = ">"
        out.write(struct.pack(MODE+"H",0xFFFE))
        
        out.write(struct.pack(MODE+"5H",40, 1, 1, 0, 0))
        out.seek(40,1)
        
        HEADER = []
        HEADER.append(len(self["Charges"]))
        HEADER.append(len(self["Inputs"]))
        HEADER.append(len(self["Moves"]))
        HEADER.append(len(self["CancelLists"]))
        
        #
        # Write Charges
        #
        if len(self["Charges"]) == 0:
            HEADER.append(0)
        else:
            HEADER.append(out.tell())
            for name,charge in self["Charges"].items():
                out.write(struct.pack(MODE+"6HI", \
                    charge["Input"],charge["Unknown1"],charge["MoveFlags"],charge["Frames"],charge["Frames2"],charge["Unknown3"],charge["StorageIndex"]))
        #
        # Write Inputs
        #
        
        #
        # Write Moves
        #
        if len(self["Moves"]) == 0:
            HEADER.append(0)
        else:
            HEADER.append(out.tell())
            for name,move in self["Moves"].items():
                out.write(struct.pack(MODE+"4H4H4Bf4HiIIffIIHHHHHHHHHHH",\
                   move["Input"],move["MoveFlags"],move["PositionRestriction"],move["Restriction"],\
                   move["Unknown1"],move["StateRestriction"],move["Unknown2"],move["MiscRestriction"],\
                   move["Unknown3"],move["UltraRestriction"],move["UltraRestriction?"],move["PositionRestrictionDistance"],\
                   move["EXRequirement"],move["EXCost"],move["UltraRequirement"],move["UltraCost"],\
                   move["AIMoveFeatures"],move["AIMinRange"],move["AIMaxrange"],move["AIUnknown1"],\
                   move["CPUPassiveMove"],move["CPUCounterMove"],move["CPUVsStand"],move["CPUVsAir"],\
                   move["CPUVsDown"],move["CPUVsStunned"],move["CPUProbeMove"],move["CPUVsVeryClose"],\
                   move["CPUVsClose"],move["CPUVsMidRange"],move["CPUVsFar"],move["CPUVsVeryFar"]))
                    

                
                
        for i in range(0,6):
            HEADER.append(0)
        out.seek(0x10)
        out.write(struct.pack(MODE+"4H8I",*HEADER))
        out.close()
        
    
def doAll():
    for char in os.listdir(PC_PATH):
        print( char)
        #print( "PC")
        versions = defaultdict(list)
        versions_data = {}
        for file in findFiles(char,'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Super Street Fighter IV - Arcade Edition\\',".bcm"):
            test = BCMFile(file)
            test_text = json.dumps(test.Charges, indent=5).splitlines()+json.dumps(test.Inputs, indent=5).splitlines()+json.dumps(test.Moves, indent=5).splitlines()+json.dumps(test.CancelLists, indent=5).splitlines()
            m = hashlib.md5()
            m.update(repr(test_text))
            versions[m.hexdigest()].append(file)
            f = open("../out/"+char+"_"+m.hexdigest()+".txt","w")
            for line in test_text:
                f.write(line)
                f.write("\n")
            f.close()
        #print( "XBOX")
        for file in findFiles(char,'Z:\\SF4 Engine STuff\\XBOX AE\\',".bcm"):
            test = BCMFile(file)
            test_text = json.dumps(test.Charges, indent=5).splitlines()+json.dumps(test.Inputs, indent=5).splitlines()+json.dumps(test.Moves, indent=5).splitlines()+json.dumps(test.CancelLists, indent=5).splitlines()
            m = hashlib.md5()
            m.update(repr(test_text))
            versions[m.hexdigest()].append(file)
            f = open("../out/"+char+"_"+m.hexdigest()+".txt","w")
            for line in test_text:
                f.write(line)
                f.write("\n")
            f.close()
        #print( json.dumps(versions, indent=5))

def doChar(c):
    pc = BCMFile(PC_PATH+c+"\\"+c+".bcm")
    xbox = BCMFile(XBOX_PATH+c+"\\"+c+".bcm")
    #print( json.dumps(pc.CancelLists, indent=5))
    print( "DIFF")
    htmlDiff = difflib.HtmlDiff()
    f = open("diff.html","w")
    pctxt = json.dumps(pc.Charges, indent=5).splitlines()+json.dumps(pc.Inputs, indent=5).splitlines()+json.dumps(pc.Moves, indent=5).splitlines()+json.dumps(pc.CancelLists, indent=5).splitlines()
    xboxtxt = json.dumps(xbox.Charges, indent=5).splitlines()+json.dumps(xbox.Inputs, indent=5).splitlines()+json.dumps(xbox.Moves, indent=5).splitlines()+json.dumps(xbox.CancelLists, indent=5).splitlines()
    f.write(htmlDiff.make_file(pctxt,xboxtxt))
    f.close()