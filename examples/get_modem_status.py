#!/usr/bin/python
#
from __future__ import print_function

_name = "get_modem_block"
__version__ = "1.0.0"
__date__ = "2/18/2019"
__exp__ = "(experimental)"  # (Release Version)
title = "%s Version: %s %s %s" % (_name, __version__, __date__, __exp__)

import argparse
import j1939.utils

parser = argparse.ArgumentParser(description='''\
        example: %(prog)s -d 0x17 
        
                will request ecu block from destination '''
                                    ,epilog=title)

parser.add_argument("-s", "--src",
                    default="0xff",
                    help="j1939 source address decimal or hex, default is 0")

parser.add_argument("-d", "--dest",
                    default="0x41",
                    help="CAN destination, default is 0x41")

parser.add_argument("-t", "--timeout",
                    default="20",
                    help="larger numbers give the dest more time to respond")

args = parser.parse_args()


source = int(args.src, 0)
dest = int(args.dest, 0)
timeout = int(args.timeout, 0)

#expects a BAM back pretty
val = j1939.utils.request_pgn(0xffb8, src=source, dest=dest, timeout=timeout)

#print(val)

print("Destination Address:       %d (0x%x)" % (dest, dest))
print("Modem ping status:         %d" % (val[0] & 0xF))
print("Modem registration status: %d" % ((val[0] & 0xF0) >> 4))
print("Modem signal strength:     %d" % (val[1] & 0x7))
print("Modem responding:          %s" % ("true" if (((val[1] & 0x18) >> 3) == 1) else "false"))
if val[2] == 255:
    print("Modem RSRQ:                Not available")
else:
    print("Modem RSRQ:               %0.1f dB" % (val[2]/2 - 20.0))

if val[3] == 255:
    print("Modem RSRP:                Not available")
else:
    print("Modem RSRP:               %0.1f dBm" % (val[3] - 140.0))



