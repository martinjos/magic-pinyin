# 
# addligs.py - add "magic pinyin" ligatures to a Chinese font
# Copyright (C) 2012 Martincode (https://github.com/martincode)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

# To use: import into the fontforge user interface (see http://fontforge.org/)

# vertical:   -184 - 1638
# horizontal: 0 (80) - 2048 (2048-80) (padlock?)

import types
import fontforge
import psMat

#print "Start of script"

#f = fontforge.open("myfont.sfd")
f = fontforge.fonts()[0]

initials = ("", "b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j", "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w")
vowels = ("i", "u", "a", "o", "e", "ia", "ua", "ai", "uai", "ao", "iao", "ie", "uo", "ei", "ui", "ou", "iu", "io")
tones = (("one", "hyphen", 0.5, 1), ("two", "slash", 0.33, 1),
	 ("three", "V", 0, 0.67), ("four", "backslash", 0.33, 1))

#coda_vowels = ("a", "e", "ia", "ua", "ie", "ue") # wrong
codas = ("n", "ng")
full_codas = (("a", "n"), ("e", "n"), ("ia", "n"), ("ua", "n"), ("i", "n"), ("u", "n"), ("a", "ng"), ("e", "ng"), ("ia", "ng"), ("ua", "ng"), ("i", "ng"), ("o", "ng"))

ucolon_initials = ("n", "l")
ucolon_vowels = ("u:", "u:a", "u:e")

all_initials = initials
all_vowels = vowels + ucolon_vowels
all_codas = codas

#initials = ("", "x", "zh")
#vowels = ("u", "u:", "u:e")
#codas = ("", "n",)
#tones = (("two", "slash", 0.33, 1),)

#initials = ("b",)
#vowels = ("i",)
#tones = (("3", "V"),)

class G:
    vsep2 = 200
    vsep3 = 140
    bearing = 200 # 80
    width = 2048.0
    lower = -184
    upper = 1638
    height = upper - lower
    min_old_width = 1245
    tone_rel_width = 1.0/3
    #tsep = 100
    tsep = 0
    tone_width = (width - tsep - 2*bearing) * tone_rel_width
    nontone_width = width - tsep - 2*bearing - tone_width

    # glyph.left_side_bearing
    # glyph.right_side_bearing
    # glyph.width

    #print "g.tone_width is " + str(g.tone_width)

    pos = 0xe100

    #print "Just before getting subtables"

    subs = ()
    bodyTemps = ()

g = G()

g.subs = f.getLookupSubtables("'liga' Standard Ligatures lookup 0")

def splitChars(s):
    temp = [s[i] for i in range(0, len(s))]
    try:
	idx = temp.index(":")
	temp[idx] = "colon"
	#print temp
    except:
	pass
    return temp

def upperSplitChars(s):
    return splitChars(s.upper())

def createNewChar(f, pos, name):
    temp = f.createChar(pos, name)
    f.removeGlyph(temp)
    return f.createChar(pos, name)

def copypos(src, targ, into=False):
    #f.selection.select(src)
    if type(src) is types.StringType:
	srcGlyph = f[src]
	#if src[0:9] == "mjs_comp_":
	    #print "Source is " + src + " at position " + str(f[src].unicode) + " ("+f[src].glyphname+")"
    else:
	srcGlyph = src
    if type(targ) is types.StringType and src[0:9] == "mjs_comp_":
	targGlyph = f[targ]
    else:
	targGlyph = targ
    #f.selection.select(targ)
    f.selection.select(srcGlyph) # for some reason, using the glyphs is more reliable than using the names
    f.copy()
    f.selection.select(targGlyph)
    if into:
	f.pasteInto()
    else:
	f.paste()

#print "Just before allocating temporary space"

temp1 = createNewChar(f, g.pos, "mjs_temp1")
temp2 = createNewChar(f, g.pos+1, "mjs_temp2")
temp3 = createNewChar(f, g.pos+2, "mjs_temp3")
temp4 = createNewChar(f, g.pos+3, "mjs_temp4")
Ucolon = createNewChar(f, g.pos+4, "Ucolon")
temp1.width = g.width # top/whole
temp2.width = g.width # middle/bottom
temp3.width = g.width # bottom
temp4.width = g.width # tones
Ucolon.width = g.width # u:
g.bodyTemps = (temp1, temp2, temp3)

g.pos += 5

copypos("equal", Ucolon)
Ucolon.width = f["U"].width
Ucolon.transform(psMat.scale(1, 1))
#Ucolon.transform(psMat.translate(Ucolon.right_side_bearing/2-75, 700)) # centre(-ish)
Ucolon.transform(psMat.translate(Ucolon.right_side_bearing/2, 250)) # centre(-ish)
copypos("U", Ucolon, True)
Ucolon.width = f["U"].width
Ucolon.left_side_bearing = f["U"].left_side_bearing
Ucolon.right_side_bearing = f["U"].right_side_bearing
Ucolon.unlinkRef()

for c in all_initials + all_vowels + all_codas:
    if len(c) > 1:
	chars = upperSplitChars(c)
	compName = "mjs_comp_"+"_".join(chars)
	comp = createNewChar(f, g.pos, compName)
	#comp = createNewChar(f, -1, compName)
	#print "Created " + compName + " at position " + str(comp.unicode)
	f.selection.select(comp)
	try:
	    idx = chars.index("colon")
	    chars.remove("colon")
	    chars[idx-1] = "Ucolon"
	except:
	    pass
	comp.addPosSub(g.subs[0], chars)
	f.build()
	#comp.removePosSub(g.subs[0])
	comp.unlinkRef() # necessary for u: somehow
	g.pos += 1

#print "Just before creating glyphs"

def generateGlyphs(elems, tones):

    global g

    maxWidth = g.min_old_width
    composName = ""
    compos = ()
    for j in range(0,len(elems)):
	if len(elems[j]) == 1:
	    source = elems[j].upper()
	    #print "Looking up "+elems[j]+" (1 letter)"
	else:
	    source = "mjs_comp_"+"_".join(upperSplitChars(elems[j]))
	    #print "Looking up "+elems[j]+" (> 1 letter) with "+source
	copypos(source, g.bodyTemps[j])
	g.bodyTemps[j].left_side_bearing = 0
	g.bodyTemps[j].right_side_bearing = 0
	if g.bodyTemps[j].width > maxWidth:
	    maxWidth = g.bodyTemps[j].width

	composName += "_" + "_".join(splitChars(elems[j]))
	compos += tuple(splitChars(elems[j]))

    if len(composName) > 0:
	composName = composName[1:len(composName)]

    namebase = "mjs_pinyin_"+composName
    name = namebase + "_space"
    newch = createNewChar(f, g.pos, name)
    newch.width = g.width

    if len(elems)==2:
	vseps = g.vsep2
	vsep = g.vsep2
    elif len(elems)==3:
	vseps = 2 * g.vsep3
	vsep = g.vsep3
    else:
	vseps = 0
	vsep = 0

    hscaling = (g.width - 2 * g.bearing) / maxWidth
    vscaling = (g.height - vseps) / (len(elems) * f.capHeight)

    #print "temp1.width = "+str(temp1.width)+", temp2.width = "+str(temp2.width)+", hscaling = "+str(hscaling)

    vpos = g.upper - (g.height - vseps) / len(elems)
    
    for j in range(0,len(elems)):
	g.bodyTemps[j].transform(psMat.scale(hscaling, vscaling))
	g.bodyTemps[j].width = g.width
	g.bodyTemps[j].transform(
	    psMat.translate(g.bodyTemps[j].right_side_bearing/2, 0)) # centre
	g.bodyTemps[j].transform(psMat.translate(0, vpos)) # move to position
	copypos(g.bodyTemps[j], newch, j!=0)
	vpos -= vsep + (g.height - vseps) / len(elems)

    newch.width = g.width

    newch.addPosSub(g.subs[0], compos + ("space",))

    g.pos += 1

    for t in tones:

	body_width = g.width - g.tsep - g.tone_width # should still have bearing

	tname = namebase + "_"+t[0]+"_space"
	tnewch = createNewChar(f, g.pos, tname)
	tnewch.width = g.width

	copypos(newch, tnewch)
	tnewch.transform(psMat.translate(-g.bearing, 0))
	tnewch.transform(psMat.scale(g.nontone_width / (g.width - 2*g.bearing), 1))
	tnewch.transform(psMat.translate(g.bearing, 0))

	copypos(t[1], temp4)
	temp4.left_side_bearing = 0
	temp4.right_side_bearing = 0

	hscaling = g.tone_width / temp4.width
	vscaling = g.height * (t[3] - t[2]) / f.capHeight

	#print "hscaling is " + str(hscaling)

	temp4.transform(psMat.scale(hscaling, vscaling))
	temp4.width = g.width
	temp4.transform(psMat.translate(g.width - g.tone_width - g.bearing, g.lower +
					t[2] * g.height)) 

	copypos(temp4, tnewch, True)

	tnewch.width = g.width

	tnewch.addPosSub(g.subs[0], compos + (t[0], "space"))

	g.pos += 1

def collapseTuple(lis):
    while 1:
	try:
	    lis.remove("")
	except:
	    break
    return tuple(lis)

for i in initials:
    for v in vowels:
	generateGlyphs(collapseTuple([i, v]), tones)

#g.pos += len(initials) * len(vowels) * (1 + len(tones)) # only if skipping the above loop

for i in initials:
    for c in full_codas:
	    generateGlyphs(collapseTuple(list((i,) + c)), tones)

for i in ucolon_initials:
    for v in ucolon_vowels:
	for c in ("",) + codas:
	    generateGlyphs(collapseTuple([i, v, c]), tones)

generateGlyphs(("e", "r"), tones)
generateGlyphs(("r",), ())

#print "After creating glyphs"

#f.removeGlyph(temp1)
#f.removeGlyph(temp2)
#f.removeGlyph(temp3)
#f.removeGlyph(temp4)
