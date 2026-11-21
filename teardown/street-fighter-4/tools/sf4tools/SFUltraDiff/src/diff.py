import bac,bcm
import json
import sys
import util
import difflib
from collections import OrderedDict
OUT = "../../../sf4tools-gh-pages/"
BASE = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Super Street Fighter IV - Arcade Edition\\"

HEADER = '''---
layout: default
---

'''
FOOTER = ''''''
def diffCollectionsHeader(col1,col2,log,level=0):
    removedSet = set(col1.keys()).difference(set(col2.keys()))
    addedSet = set(col2.keys()).difference(set(col1.keys()))
    bothSet = set(col2.keys()).intersection(set(col1.keys()))
    if level == 0:
        log.write('<ul class="nav nav-pills">')
        for removed in removedSet:
            fancyName = removed
            try:
                fancyName = col1[removed]["Name"]
            except Exception:
                pass
            log.write("<li class='bg-danger'><a href='#change-{0}{1}'><span class='glyphicon glyphicon-minus'></span>Removed {1}</a></li>".format(removed,fancyName))
        for added in addedSet:
            fancyName = added
            try:
                fancyName = col2[added]["Name"]
            except Exception:
                pass
            log.write("<li class='bg-success'><a href='#change-{0}{1}'><span class='glyphicon glyphicon-plus'></span>Added {1}</a></li>".format(added,fancyName))
        for both in bothSet:
            if repr(col1[both]) == repr(col2[both]):
                continue
            fancyName = both
            try:
                fancyName = col2[both]["Name"]
            except Exception:
                pass
            log.write("<li class='bg-warning'><a href='#change-{0}{1}'><span class='glyphicon glyphicon-pencil'></span>Changed {1}</a></li>".format(both,fancyName))
        log.write("</ul>")
def diffCollections(col1,col2,log,level=0):
    removedSet = set(col1.keys()).difference(set(col2.keys()))
    addedSet = set(col2.keys()).difference(set(col1.keys()))
    bothSet = set(col2.keys()).intersection(set(col1.keys()))
    for removed in removedSet:
        fancyName = removed
        try:
            fancyName = col1[removed]["Name"]
        except Exception:
            pass
        log.write("<div class='panel panel-danger'>");
        log.write("<span class='anchor'  id='change-{0}{1}'></span><div class='panel-heading'>Removed {1}</div>".format(removed,fancyName))
        log.write("<div class='panel-body'><pre>")
        log.write(json.dumps(col1[removed],indent=5))
        log.write("</pre></div></div>")
    for added in addedSet:
        fancyName = added
        try:
            fancyName = col2[added]["Name"]
        except Exception:
            pass
        log.write("<div class='panel panel-success'>");
        
        log.write("<span class='anchor'  id='change-{0}{1}'></span><div class='panel-heading'>Added {1}</div>".format(added,fancyName))
        log.write("<div class='panel-body'><pre>")
        log.write(json.dumps(col2[added],indent=5))
        log.write("</pre></div></div>")

    for both in set(col2.keys()).intersection(set(col1.keys())):
        if repr(col1[both]) == repr(col2[both]):
            continue
        fancyName = both
        
        try:
            fancyName = col2[both]["Name"]
        except Exception:
            pass

        log.write("<div class='panel panel-warning'>");
        log.write("<span class='anchor'  id='change-{0}{1}'></span><div class='panel-heading'>Changed {1}</div><div class='panel-body'>".format(both,fancyName))
        if type(col1[both]) is dict or type(col1[both]) is OrderedDict:
            diffCollections(col1[both],col2[both],log,level+1)
        else:
            if type(col1[both]) is list:
                differ = difflib.HtmlDiff()
                log.write(differ.make_table(json.dumps(col1[both],indent=5).splitlines(),json.dumps(col2[both],indent=5).splitlines()))
            else:
                log.write("<div class='container-fluid'>")

                log.write("<div class='col-md-5'>Old<br />")
                log.write("<pre>")
                log.write( json.dumps(col1[both],indent=5))
                log.write("</pre></div>")
                log.write("<div class='col-md-5'>New<br />")
                log.write("<pre>")
                log.write( json.dumps(col2[both],indent=5))
                log.write("</pre></div>")
                log.write("</div>")
        log.write("</div></div>")        
def getVersionData():
    paths = []
    names = []
    paths.append("resource\\battle\\chara")
    names.append("Super")
    paths.append("dlc\\03_character_free\\battle\\regulation\\latest")
    names.append("AE")
    paths.append("patch\\battle\\regulation\\latest_ae")
    names.append("AE2012")
    paths.append("patch\\battle\\regulation\\v101")
    names.append("AE2012 v1.01")
    paths.append("patch\\battle\\regulation\\v104")
    names.append("AE2012 v1.04")
    paths.append("dlc\\04_ae2\\battle\\regulation\\ae2")
    names.append("Ultra v1.01")
    paths.append("patch_ae2_tu1\\battle\\regulation\\ae2_109")
    names.append("Ultra v1.02")
    paths.append("patch_ae2_tu1b\\battle\\regulation\\ae2_109b")
    names.append("Ultra v1.03")
    paths.append("patch_ae2_tu2\\battle\\regulation\\ae2_110")
    names.append("Ultra v1.04")
    paths.append("patch_ae2_tu3\\battle\\regulation\\ae2_111")
    names.append("Ultra v1.05")
    return paths, names
def rebuildIndex():
    paths, names = getVersionData()
    global OUT, BASE
    index = open(OUT+"_includes\\table.html","w")
    charcount = 0
    for char in os.listdir(BASE+"\\dlc\\04_ae2\\battle\\regulation\\ae2"):
        if charcount % 15 == 0:
            index.write( """	<tr>
		<th class="brright">Character</th>
		<th class="vertical" ><div>Super</div></th>
		<th class="vertical" colspan="2"><div>AE</div></th>
		<th class="vertical" colspan="2"><div>AE2012</div></th>
		<th class="vertical" colspan="2"><div>AE2012 v1.01</div></th>
		<th class="vertical" colspan="2" ><div>AE2012 v1.04</div></th>
		<th class="vertical" colspan="2"><div>Ultra v1.01</div></th>
		<th class="vertical" colspan="2"><div>Ultra v1.02</div></th>
		<th class="vertical" colspan="2"><div>Ultra v1.03</div></th>
		<th class="vertical" colspan="2"><div>Ultra v1.04</div></th>
		<th class="vertical" ><div>Ultra v1.05</div></th>
	</tr>""")
    
        charcount += 1
        print(char)
        index.write("<tr><th>{0}</th>".format(char))
        i = 0
        while i < len(names)-1:
            found = False
            for g in range(i+1,len(names)):
                name = names[i]+"_TO_"+names[g]
                pname = names[i]+" > "+names[g]
                if not os.path.exists(OUT+"characters\\"+char+"\\"+name+".html"):
                    pass
                    #index.write('<td colspan="2">&#8212;</td>')
                else:
                    found = True
                    index.write('<td colspan="{1}" class="success"><a href="{{{{ site.baseurl }}}}{0}">{2}</a></td>'.format("characters/"+char+"/"+name+".html",(g-i)*2,pname))
                    i = g-1
                    break
            if not found:
                index.write('<td colspan="{0}">&#8212;</td>'.format(2))
            i += 1
        index.write("</tr>")
    index.close()
def compareChar(char, index=None):
    html = "<tr>"
    postfix = char+"\\"+char
    
    global BASE, OUT
    if not os.path.exists(OUT+"characters\\"+char):
        os.makedirs(OUT+"characters\\"+char)
    paths, names = getVersionData() 
    
    bacs = []
    bcms = []
 
    namescopy = list(names)
    for i,version in enumerate(list(paths)):

        if not os.path.isfile(BASE+version+"\\"+postfix+".bac"):
            
            print char,"doesn't have",namescopy[i]
            paths.remove(version)
            names.remove(namescopy[i])
            continue
        if os.path.isfile( "../json/"+char+"_"+namescopy[i]+".bac.json"):
            pass
        print("\t"+namescopy[i])
        tmp = bac.BACFile(BASE+version+"\\"+postfix+".bac")
        log = open("../json/"+char+"_"+namescopy[i]+".bac.json","w")
        log.write(tmp.toJSON())
        bacs.append(tmp)
        log.close()
        
        tmp = bcm.BCMFile(BASE+version+"\\"+postfix+".bcm")
        log = open("../json/"+char+"_"+namescopy[i]+".bcm.json","w")
        log.write(tmp.toJSON())
        #tmp.toFile("../out/"+char+"_"+names[i]+".bcm")
        bcms.append(tmp)
        log.close()
        
    
    for i in range(0,len(paths)-1):
        
        name = names[i]+"_TO_"+names[i+1]
        
        print "\tDoing ",name
        log = open(OUT+"characters\\"+char+"\\"+name+".html","w")
        log.write(HEADER.format(char,name))
        if len(bacs) < 2 or len(bcms) < 2:
            return;
        firstBAC= bacs[i]
        secondBAC = bacs[i+1]
        firstBCM= bcms[i]
        secondBCM = bcms[i+1]
        for k in firstBCM.keys():
            log.write("<a class='anchor' id='"+k+"'></a><h2>"+k+"</h2>")
            if type(firstBCM[k]) is list:
                pass
            else:
                diffCollectionsHeader(firstBCM[k],secondBCM[k],log)
        for k in firstBAC.keys():
            log.write("<a class='anchor' id='"+k+"'></a><h2>"+k+"</h2>")
            if type(firstBAC[k]) is list:
                pass
            else:
                diffCollectionsHeader(firstBAC[k],secondBAC[k],log)
        for k in firstBCM.keys():
            log.write("<a></a><h2>"+k+"</h2>")
            if type(firstBCM[k]) is list:
                if repr(firstBCM[k]) != repr(secondBCM[k]):
                    log.write("<div class='container-fluid'>")
                    log.write("<div class='col-md-5'>Old<br />")
                    log.write("<pre>")
                    log.write( json.dumps(firstBCM[k],indent=5))
                    log.write("</pre></div>")
                    log.write("<div class='col-md-5'>New<br />")
                    log.write("<pre>")
                    log.write( json.dumps(secondBCM[k],indent=5))
                    log.write("</pre></div>")
                    log.write("</div>")
            else:
                diffCollections(firstBCM[k],secondBCM[k],log)

        for k in firstBAC.keys():
            log.write("<a></a><h2>"+k+"</h2>")
            if type(firstBAC[k]) is list:
                if repr(firstBAC[k]) != repr(secondBAC[k]):
                    log.write("<div class='container-fluid'>")
                    log.write("<div class='col-md-6'>Old<br />")
                    log.write("<pre>")
                    log.write( json.dumps(firstBAC[k],indent=5))
                    log.write("</pre></div>")
                    log.write("<div class='col-md-6'>New<br />")
                    log.write("<pre>")
                    log.write( json.dumps(secondBAC[k],indent=5))
                    log.write("</pre></div>")
                    log.write("</div>")
            else:
                diffCollections(firstBAC[k],secondBAC[k],log)
        log.write(FOOTER)
        log.close()


import os

#compareChar("RYU")
#compareChar("SGT")

#for char in os.listdir("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Super Street Fighter IV - Arcade Edition\\dlc\\04_ae2\\battle\\regulation\\ae2"):
#   print(char)
#   compareChar(char)

rebuildIndex()
