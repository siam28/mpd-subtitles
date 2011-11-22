#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
### Miscellaneous I/O Utils #####
# Version 0.1 by Scott Garrett #
# Wintervenom [(at)] gmail.com #
################################
# Changelog:
#
# 0.1
#   Initial version.

import codecs
import difflib
import glob
import os
import re



class ReadError(Exception):
    pass



class NothingFound(Exception):
    pass



def read(file, encodings=('utf-8', 'utf-16', 'ascii', 'latin_1')):
    """ Read a file, attempting to detect encoding.
    Raise a ReadError if it couldn't be read. """
    for encoding in encodings:
        try:
            with codecs.open(file, 'r', encoding) as f:
                contents = f.read()
            break
        except:
            pass
    try:
        return contents
    except UnboundLocalError:
        raise ReadError("Unknown file encoding. Tried: %s" % str(encodings))



def fuzzypath(destination, accuracy=0.9):
    """ Return the most similar path to destination.
    Raise NothingFound if none was found. """
    # We need a path to start at.
    path = destination.pop(0)
    for part in destination:
        ls = glob.glob(os.path.join(path, '*'))
        # Look for the closest match to the target path (part).
        try:
            part = os.path.join(path, part)
            path = difflib.get_close_matches( part, ls, 1, accuracy)[0]
        except IndexError:
            raise NothingFound("No similar path found.")
    return path



def sanitize(string, replacement='_'):
    """ Replace non-word characters in a string. """
    return re.sub(r'[^\w\-\. ]', replacement, string)



