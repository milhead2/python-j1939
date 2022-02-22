#!/usr/bin/python
#
from __future__ import print_function

_name = "j1939_request_pgn"
__version__ = "1.0.0"
__date__ = "12/21/2017"
__exp__ = "(expirimental)"  # (Release Version)
title = "%s Version: %s %s %s" % (_name, __version__, __date__, __exp__)

import j1939.utils



if __name__ == "__main__":

    import traceback
    import timeit
    import time
    import argparse
    import logging
    import textwrap

    def getStringValAsInt(s):
        if s.startswith("0x"):
            return int(s[2:],base=16)
        else:
            return int(s, base=10)


    logger = logging.getLogger("j1939")
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    logger.addHandler(ch)

    parser = argparse.ArgumentParser(description='''\
           example: %(prog)s -d 0x21 65223
           
                    will request a specific PGN 65223 from dest '''
                                     ,epilog=title)

    parser.add_argument("-s", "--src",
                        default="0",
                        help="j1939 source address decimal or hex, default is 0")

    parser.add_argument("-d", "--dest",
                      default="0x17",
                      help="CAN destination, default is 0x17")

    parser.add_argument("pgn",
                      default=None,
                      help="pgn to request in decimal or 0xHex")

    args = parser.parse_args()


    source = getStringValAsInt(args.src)
    dest = getStringValAsInt(args.dest)
    pgn = getStringValAsInt(args.pgn)

    print ("j1939.utils.request_pgn(pgn=0x%04x (%d), src=0x%02x, dest=0x%02x)" % (pgn, pgn, source, dest))

    val = j1939.utils.request_pgn(pgn, length=4, src=source, dest=dest)

    print("returned PGN = %s" % val)

