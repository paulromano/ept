#!/usr/bin/env python

import re

def fileReSeek(fh, regex):
    """
    Seek to a position in the file open on handle fh that matches
    the regular expression regex and return a MatchObject. If no
    match is found, return None.
    """

    p = re.compile(regex)
    while True:
        line = fh.readline()
        if line == '':
            return None
        match = p.match(line)
        if match:
            return match


