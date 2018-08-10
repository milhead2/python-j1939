#!/usr/bin/python
#
from __future__ import print_function

_name = "get_ecu_block"
__version__ = "1.1.0"
__date__ = "8/2/2018"
__exp__ = "(expirimental)"  # (Release Version)
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
                    default="0x17",
                    help="CAN destination, default is 0x17")

parser.add_argument("-t", "--timeout",
                    default="10",
                    help="larger numbers give the dest more time to respond")

args = parser.parse_args()


source = int(args.src, 0)
dest = int(args.dest, 0)
timeout = int(args.timeout, 0)

#expects a BAM back pretty
val = j1939.utils.request_pgn(0xfeda, src=source, dest=dest, timeout=timeout)

fieldCount = val[0]
print ("%d elements in list" % fieldCount)

res=""
for c in val[1:]:
    res += chr(c)

res2=res.split('*')
print (res2)

print("Destination Address:     %d (0x%x)" % (23, 23))
print("Number of ID items:      %d (0x%x)" % (fieldCount, fieldCount))
print("Model Number:            %s " % (res2[0]))
print("Vendor Part Number:      %s" % (res2[1]))
print("Hardware Serial Number:  %s" % (res2[2]))
print("VIN:                     %s" % (res2[3]))
print("Hardware Part Number:    %s" % (res2[4]))
print("ECU Part Number:         %s" % (res2[5]))
print("Program Version:         %s" % (res2[6]))
print("Software Version Number: %s" % (res2[7]))
print("Software Part Number:    %s" % (res2[8]))
print("Checksum:                0x%s" % (res2[9]))



