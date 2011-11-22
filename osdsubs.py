#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
### XOSD Subtitles ##############
# Version 0.1 by Scott Garrett #
# Wintervenom [(at)] gmail.com #
################################
# Dependencies:
#
# pyosd (Python XOSD bindings)
#   http://repose.cx/pyosd/
#
# python-xlib
#   http://python-xlib.sourceforge.net
#
#################################
# Changelog:
#
# 0.1
#   Initial version.
#
#################################
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

import Xlib
import Xlib.display
import pyosd
import re
import textwrap



ATTRSTAMP = re.compile(r'\[\w:[\w ,-\.]+\]')



class OSD(object):
    """ XOSD subtitle display. """
    def __init__(self):
        self.invert = False
        self.colors = ['gray', 'red', 'green', 'yellow', 'blue', 'magenta',
                       'cyan', 'white']
        self.defaultcolor = 3
        self.xroot = Xlib.display.Display().screen().root
        # Get horizontal sceen resolution.
        self.hres = self.xroot.get_geometry().width
        # How many characters can fit in a line at this resolution?
        self.maxcpl = int(self.hres / 22.4)
        self.osd = []
        # We can display five simutaneous events at a time.
        for n in xrange(0, 5, 1):
            self.osd.append(pyosd.osd(lines=3))
            self.osd[n].set_font('-*-dejavu sans mono-bold-r-*-*-36' \
                                 '-*-*-*-*-*-iso10646-1')
            self.osd[n].set_outline_offset(4)


    def display(self, lines):
        # OSDs will be displayed on the bottom by default, so we want the
        # last lines to be on the bottom.
        if not self.invert:
            lines.reverse()
        # Make lines with position stamps the last to be dealt with so we can
        # make sure that centered lines raise the Y-offset, since they will
        # always be allotted the full witdh of the screen.
        lines.sort(key=lambda item: item.lstrip().startswith('[p:'))
        # Upper-, middle-, and lower-left/right/center offsets.
        offset = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        # Clear what's already being displayed.
        for n in xrange(0, 5, 1):
            self.osd[n].hide()
            self.osd[n].scroll(2)
            self.osd[n].hide()
        # No point in bothering with blank lines...
        l = len(lines)
        if (lines[0].strip() == '' and l == 1) or l == 0:
            return None
        for index, line in enumerate(lines):
            # ...or trying to dislay more events than we have OSDs for.
            if index > 4:
                break
            # Default formatting of current OSD.
            pos = [0, 1]    #-1: left/top, 0: center, 1: right/bottom.
            timeout = 10    # Hide the OSD if idle longer than this.
            color = self.defaultcolor  # OSD color.
            attrs = ATTRSTAMP.findall(line)
            for attr in attrs:
                # We just want the attribute character and the values.
                attr = re.sub('[^\w-]', ' ', attr).split()
                # Set [p]osition.
                if attr[0] == 'p':
                    for n in (0, 1):
                        try:
                            # Keep value in bounds.
                            pos[n] = max(-1, min(1, int(attr[1 + n])))
                        except (ValueError, IndexError):
                            pass
                # Set [c]olor.
                if attr[0] == 'c':
                    try:
                        color = max(0, min(7, int(attr[1])))
                    except ValueError:
                        # Maybe it was specified as an initial.
                        try:
                            'wrgybmca'.index(attr[1].lower())
                        except ValueError:
                            pass
                # Set [t]imeout.
                if attr[0] == 't':
                    try:
                        timeout = max(0, min(60, float(attr[1])))
                    except (IndexError, ValueError):
                        pass
            if self.invert:
                pos[1] = pos[1] * -1
            # Left- and right-aligned events get displayed on the same Y-offset,
            # so we'll halve the maximum number of character per line.
            maxcpl = self.maxcpl
            if pos[0] != 0:
                maxcpl /= 2
            # Remove the stamps and wrap the text to fit in the OSD.
            line = ATTRSTAMP.sub('', line.strip())
            line = textwrap.wrap(line, maxcpl)
            l = len(line)
            if l == 0:
                l = 1
            # Apply formatting to OSD.
            self.osd[index].set_colour(self.colors[color])
            self.osd[index].set_align(1 + pos[0])
            self.osd[index].set_pos((0, 2, 1)[1 + pos[1]])
            self.osd[index].set_timeout(timeout)
            self.osd[index].set_vertical_offset(offset[1+pos[1]][1+pos[0]] * 44)
            # Raise the Y-offset up however many lines the text was.
            offset[1 + pos[1]][1 + pos[0]] += l
            # Centered OSDs get the whole screen-width.
            if pos[0] == 0:
                for n in (0, 2):
                    if pos[1] == 1:
                        offset[1 + pos[1]][n] += l
                    else:
                        offset[1 + pos[1]][n] += 3
            # Display the OSD.
            for l in line:
                self.osd[index].scroll(1)
                self.osd[index].display(l, line=2)

