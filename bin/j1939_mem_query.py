#!/usr/bin/python
#
from __future__ import print_function

_name = "Simple J1939 memory object query"
__version__ = "1.0.0"
__date__ = "12/20/2017"
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

'''
1532554003.434215    PRI=7 PGN=0xff9a               SRC=0x17    d3 ff ff ff ff ff ff ff
1532554003.434771    PRI=6 PGN=0xd041      DST=0x41 SRC=0x17    a1 ff ff ff ff ff ff ff
1532554003.863598    PRI=7 PGN=0xd917      DST=0x17 SRC=0x18    0a 13 11 00 00 e9 ff ff
1532554003.868833    PRI=6 PGN=0xd818      DST=0x18 SRC=0x17    0a 11 ff ff ff ff ff ff
1532554003.901772    PRI=7 PGN=0xd718      DST=NONE(error) SRC=0x17    ff 59 30 31 2e 30 34 2e 32 30 00
1532554003.908125    PRI=7 PGN=0xd917      DST=0x17 SRC=0x18    ff 09 00 00 00 00 ff ff
1532554003.939402    PRI=7 PGN=0xff9a               SRC=0x17    d3 ff ff ff ff ff ff ff
1532554003.939959    PRI=6 PGN=0xd041      DST=0x41 SRC=0x17    9c ff ff ff ff ff ff ff
1532554003.940621    PRI=6 PGN=0xfec1               SRC=0x17    00 00 00 00 00 00 00 00
1532554003.941260    PRI=6 PGN=0xfefc               SRC=0x17    ff ff ff ff ff ff ff ff
'''


def get_mem_object(bus=None, length=4, src=0, dest=0x17, pointer=0, extension=0):
    countdown = 10
    result = None

    pgn = j1939.PGN()
    pgn.value = 0xd917
    aid = j1939.ArbitrationID(pgn=pgn, source_address=src, destination_address=dest)

    data = [length, 0x13, pointer, 0x00, 0x00, extension, 0xff, 0xff]
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)
    pdu.display_radix='hex'

    bus.send(pdu)

    while countdown:
        pdu = bus.recv()
        if pdu.pgn == 0xd700:
            value = list(pdu.data)
            length = value[0]
            if length == 1:
                result = value[1]
            if length == 2:
                result = (value[2] << 8) + value[1]
            if length == 4:
                result = (value[4] << 24) + (value[3] << 16) + (value[2] << 8) + value[1]
            break # got what I was waiting for

        countdown -= 1

    if (result == None):
        raise IOError(" no CAN response")

    return result

def getStringVal(s):
    if s.startswith("0x"):
        return int(s[2:],base=16)
    else:
        return int(s, base=10)



if __name__ == "__main__":

    #lLevel = logging.WARN
    #jlogger = logging.getLogger("j1939")
    #jlogger.setLevel(lLevel)
    #ch = logging.StreamHandler()
    #jlogger.addHandler(ch)

    parser = argparse.ArgumentParser(description='''\
           example: %(prog)s -d 0x21 0xe9 -p 0x15
           
                    will query a E9_15 Memory value '''
                                     ,epilog=title)

    parser.add_argument("-t", "--test",
                        action="store_true", default=False,
                        help="run the test cases and ignore input parameters")

    parser.add_argument("-s", "--src",
                        default="0",
                        help="j1939 source address decimal or hex, default is 0")

    parser.add_argument("-d", "--dest",
                      default="0x17",
                      help="CAN destination, default is 0x17")

    parser.add_argument("-l", "--length",
                      default="4",
                      help="length in bytes (default: 4)")

    parser.add_argument("-c", "--channel",
                  default="can0",
                  help="Memory object pointer offset to request in decimal or 0xHex")

    parser.add_argument("extension",
                  default=None,
                  help="Memory object extension prefix to request in decimal or 0xHex")

    parser.add_argument("pointer",
                  default=None,
                  help="Memory object pointer offset to request in decimal or 0xHex")


    args = parser.parse_args()


    if args.test:
        # queries a couple objects but setting up the full stack and bus for
        # each takes a long time.
        if 1:
            start = timeit.default_timer()
            for p, e in [(0x15, 0xe9), (0x00, 0xf1), (0x50, 0xe9), (0x75, 0xe9)]:
                val = j1939.utils.get_mem_object(length=4, src=0, dest=0x17, pointer=p, extension=e)
                print("0x%02x-0x%02x = %d" % (p, e, val))
            print("elapsed = %s s" % (timeit.default_timer() - start))


        if 1:
            # queries the same objects but in a single bus instance, should be a tad faster.
            start = timeit.default_timer()
            try:
                jbus = j1939.Bus(channel='can0', bustype='socketcan', timeout=0.01)
                for p, e in [(0x15, 0xe9), (0x00, 0xf1), (0x50, 0xe9), (0x75, 0xe9)]:
                    val = get_mem_object(jbus, length=4, src=0, dest=0x17, pointer=p, extension=e)
                    print("0x%02x-0x%02x = %d" % (p, e, val))
            except:
                traceback.print_exc()
                pass

            jbus.shutdown()

            print("elapsed = %s s" % (timeit.default_timer() - start))

    else:

        if (args.pointer==None or args.extension==None):
            raise ValueError("pointer and extension are required!")

        source = getStringVal(args.src)
        dest = getStringVal(args.dest)
        ptr = getStringVal(args.pointer)
        length = getStringVal(args.length)
        ext = getStringVal(args.extension)
        channel = args.channel
        print ("get_mem_object_single(src=0x%02x, dest=0x%02x, pointer=0x%02x, extension/space=0x%02x, len=%d" % (source, dest, ptr, ext, length))

        val = j1939.utils.get_mem_object(ptr, ext, length=length, src=source, dest=dest, channel=channel)
        print(val)
        out = ''
        if isinstance(val, list):
                for x in val:
                    out+=chr(x)
                print(out)
        #print("0x%02x-0x%02x = %d (0x%08x)" % (ptr, ext, val, val))

