#!/usr/bin/python
#

_name = "Simple J1939 memory object query"
__version__ = "1.1.0"
__date__ = "3/25/22"
__exp__ = "()"  # (Release Version)
title = "%s Version: %s %s %s" % (_name, __version__, __date__, __exp__)

import sys
MIN_PYTHON = (3, 5)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

import j1939.utils

if __name__ == "__main__":
    # import traceback
    # import timeit
    # import time
    # import textwrap
    # import inspect
    import argparse
    import logging



if __name__ == "__main__":


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

    parser.add_argument("--speed",
                      default="250",
                      help="CAN bitrate {250|500}, default is 250")

    parser.add_argument("--log",
                      default="WARNING",
                      help="Set LogLevel to DEBUG|INFO|(WARNING)|ERROR|CRITICAL for this app, j1939 and can")

    parser.add_argument("-l", "--length",
                      default="4",
                      help="length in bytes (default: 4)")

    parser.add_argument("-c", "--channel",
                  default="can0",
                  help="Memory object pointer offset to request in decimal or 0xHex")
    
    parser.add_argument("-b", "--bustype",
                  default="socketcan",
                  help="This depends on the channel for pcan use PCAN_USBBUS1")

    parser.add_argument("extension",
                  default=None,
                  help="Memory object extension prefix to request in decimal or 0xHex")

    parser.add_argument("pointer",
                  default=None,
                  help="Memory object pointer offset to request in decimal or 0xHex")


    args = parser.parse_args()

    # assuming loglevel is bound to the string value obtained from the
    # command line argument. Convert to upper case to allow the user to
    # specify --log=DEBUG or --log=debug
    numeric_level = getattr(logging, args.log.upper())
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(args.log))
    logging.basicConfig(level=numeric_level)

    logger = logging.getLogger("j1939")
    logger.setLevel(numeric_level)

    logger = logging.getLogger("can")
    logger.setLevel(numeric_level)

    if (args.pointer==None or args.extension==None):
        raise ValueError("pointer and extension are required!")

    source = int(args.src, 0)
    dest = int(args.dest, 0)
    ptr = int(args.pointer, 0)
    length = int(args.length, 0)
    ext = int(args.extension, 0)
    speed = int(args.speed, 0)
    channel = args.channel
    bustype = args.bustype
    logging.info ("get_mem_object_single(src=0x%02x, dest=0x%02x, pointer=0x%02x, extension/space=0x%02x, len=%d" % (source, dest, ptr, ext, length))

    val = j1939.utils.get_mem_object(ptr, ext, length=length, src=source, dest=dest, channel=channel, bustype=bustype, speed=speed)
    print("{}".format(val))
    out = ''
    if isinstance(val, list):
            for x in val:
                out+=chr(x)
            print(out)

#(1648235377.698487) can0 1CD94100#0413000000F1FFFF
#(1648235377.712659) can0 18D80041#0411FFFFFFFFFFFF
#(1648235377.712660) can0 1CD70041#0400000000FFFFFF
#(1648235377.712661) can0 18D80041#0019FFFFFFFFFFFF