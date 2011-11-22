#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
### Miscellaneous MPD Utils #####
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

import mpd
import socket



def mpdconnect(client, host=('localhost', 6600), password=None):
    """ Connect and authunticate to an MPD server.
    socket.error raised if connection failed;
    mpd.CommandError raised if authuntication failed. """
    client.connect(host[0], host[1])
    if password:
        client.password(password)



def mpdreconnect(client, host, password, tries=None):
    """ Connect to an MPD server, retrying upon fail. """
    try:
        return client.status()
    except mpd.ConnectionError:
        try:
            client.disconnect()
        except (mpd.ConnectionError), error:
            print(str(error))
        while True:
            try:
                print('Connecting to %s:%d...' % (host[0], host[1]))
                mpdconnect(client, host, password)
            except socket.error, error:
                print('Connection failed: %s' % str(error))
                time.sleep(5)
                continue
            except mpd.CommandError:
                print('Authuntication failed: %s' % str(error))
                return False
            if tries:
                tries -= 1
                if tries == 0:
                    print("Couldn't connect to MPD server.")
                    return False
            break
        print('Connected.')
        return client.status()



