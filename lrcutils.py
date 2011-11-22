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

import operator
import re



# Timestamp to match when parsing LRCs.
TIMESTAMP = re.compile(r'\[(?:\d+:)?(?:\d+:)?\d+(?:\.\d+)?\]')
METASTAMP = re.compile(r'\[(\w{2}): *(.+)? *\]')



class ReadError(Exception):
    pass



class NothingFound(Exception):
    pass



def secstostamp(seconds):
    m, s = divmod(float(seconds), 60)
    h, m = divmod(m, 60)
    if h == 0:
        return '[%02d:%05.2f]' % (m, s)
    return '[%02d:%02d:%05.2f]' % (h, m, s)



def stamptosecs(timestamp):
    timestamp = re.sub(r'[^\d\.]', ' ', timestamp).split()
    seconds = float(timestamp[-1])
    for n in xrange(1, 3, 1):
        try:
            seconds += float(timestamp[-1 - n]) * 60 ** n
        except IndexError:
            pass
    return seconds



def parselrc(rawlrc, splitlines=True, skiptimeless=True):
    """ Read and parse an LRC lyrics file.
    Return a list with the display times at x[n][0]
    and the lines at x[n][1]. """
    if splitlines:
        lyrics = [(-1, ('',))]
    else:
        lyrics = [(-1, '')]
    metadata = {}
    # Be pedantic and use square brackets for sound descriptions.
    rawlrc = re.sub(r'\(\* *([^()]+\b) *\*\)', '[\g<1>]', rawlrc)
    rawlrc = re.sub(r'\* *([^*]+\b) *\*', '[\g<1>]', rawlrc)
    rawlrc = re.sub(r'\{ *([^{}]+\b) *\}', '[\g<1>]', rawlrc)
    rawlrc = re.sub(r'\s+[/|]\s+', '|', rawlrc)
    # Remove LRC Enhanced word timestamps.
    rawlrc = re.sub(r'<(?:\w+:?)*(?:.\w+)?> *', '', rawlrc)
    # Expand tabs out.
    rawlrc = rawlrc.expandtabs().strip()
    # XOSD can't display the music note characters, so replace them with
    # something close.
    rawlrc = re.sub(ur'[\u2669\u266A\u266B\u266C\u266D\u266E\u266F]', '#',
                    rawlrc)
    for line in rawlrc.split('\n'):
        # Grab the timestamps in a list...
        times = TIMESTAMP.findall(line)
        # ...and strip from the beginning of the line.
        line = TIMESTAMP.sub('', line.strip())
        # Ignore lines without a timestamp.
        if len(times) == 0:
            info = METASTAMP.split(line)
            if len(info) == 4:
                metadata[info[1]] = info[2]
                continue
            elif skiptimeless:
                continue
            else:
                times = ['[0]']
        # Convert timestamps to seconds and append it and the line to the
        # lyrics list.
        for time in times:
            time = stamptosecs(time)
            if splitlines:
                lyrics.append((time, line.split('|')))
            else:
                lyrics.append((time, line))
    lyrics.sort(key=operator.itemgetter(0))
    # Add a dummy line so we won't have to bounds-check.
    if splitlines:
        lyrics.append((float('inf'), ('',)))
    else:
        lyrics.append((float('inf'), ''))
    return metadata, lyrics



def makelrc(lyrics, pack=True):
    lrc = []
    for time, line in lyrics:
        if type(time) in (float, int):
            time = secstostamp(time)
        elif type(time) != str:
            raise ValueError('Timestamp should be float/int (seconds) or' \
                             'string (stamp).')
        if pack:
            try:
                idx = [i[1] for i in lrc].index(line)
                lrc[idx][0].append(time)
            except ValueError:
                lrc.append([[time], line])
        else:
            lrc.append([[time], line])
    lrc.sort(key=operator.itemgetter(0))
    for times, line in lrc:
        yield '%s%s\n' % (''.join(times), line)



