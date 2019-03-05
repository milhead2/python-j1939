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
val = j1939.utils.request_pgn(0xffb2, src=source, dest=dest, timeout=timeout)

fieldCount = val[0]
print ("%d elements in list" % fieldCount)

res=""
for c in val[1:]:
    res += chr(c)

res2=res.split('*')
#print (res2)

print("Destination Address:     %d (0x%x)" % (dest, dest))
print("Number of ID items:      %d (0x%x)" % (fieldCount, fieldCount))
print("Modem IMEI:              %s" % (res2[0]))
print("Modem ICCID:             %s" % (res2[1]))



