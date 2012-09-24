# 
# changeligs.py - change ligatures to use a different "separator"
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

# Find all my ligatures, and change them to use a full stop (period) instead of a space
# as their "separator" (character required at end of ligature)

import fontforge

f = fontforge.fonts()[0]
subs = f.getLookupSubtables("'liga' Standard Ligatures lookup 0")

start_pos = 0xe100 + 0x19
pos = start_pos

while pos in f and len(f[pos].getPosSub(subs[0])) > 0:
    lig = list(f[pos].getPosSub(subs[0])[0][2:])
    #print lig
    if lig[-1] == "space":
	lig[-1] = "period"
	f[pos].removePosSub(subs[0])
	f[pos].addPosSub(subs[0], tuple(lig))
    else:
	print "Warning: last entry at position "+pos+" is not space"
    pos += 1

print str(pos - start_pos)
