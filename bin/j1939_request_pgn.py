#!/usr/bin/python
#
from __future__ import print_function

_name = ""
__version__ = "1.0.0"
__date__ = "12/21/2017"
__exp__ = "(expirimental)"  # (Release Version)
title = "%s Version: %s %s %s" % (_name, __version__, __date__, __exp__)

import j1939


def request_pgn_single(requested_pgn, channel='can0', bustype='socketcan', length=4, src=0, dest=0x17):

    countdown = 10
    result = None

    if not isinstance(requested_pgn, int):
        raise ValueError("pgn must be an integer.")

    bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01)
    pgn = j1939.PGN()
    pgn.value = 0xea00 + dest # request_pgn mem-object
    aid = j1939.ArbitrationID(pgn=pgn, source_address=src, destination_address=dest)

    pgn0 = requested_pgn & 0xff
    pgn1 = (requested_pgn >> 8) & 0xff
    pgn2 = (requested_pgn >> 16) & 0xff

    data = [pgn0, pgn1, pgn2]
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)

    pdu.display_radix='hex'

    bus.send(pdu)

    while countdown:
        pdu = bus.recv(timeout=1)
        if pdu and (pdu.pgn == 0xe800 or pdu.pgn == requested_pgn):
            result = list(pdu.data) 
            break # got what I was waiting for

        if pdu: 
            countdown -= 1

    bus.shutdown()

    if  not result:
        raise IOError(" no CAN response")


    return result


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




    lLevel = logging.DEBUG
    jlogger = logging.getLogger("j1939")
    ch = logging.StreamHandler()
    ch.setLevel(lLevel)
    jlogger.addHandler(ch)

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

    print ("request_pgn_single(pgn=0x%04x (%d), src=0x%02x, dest=0x%02x)" % (pgn, pgn, source, dest))

    val = request_pgn_single(pgn, length=4, src=source, dest=dest)

    print("returned PGN = %s" % val)

