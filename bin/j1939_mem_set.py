from __future__ import print_function


_name = "J1939 Memory-Object Writer"
__version__ = "1.0.1"
__date__ = "02/27/2018"
__exp__ = "()"  # (Release Version)
title = "%s Version: %s %s %s" % (_name, __version__, __date__, __exp__)

import sys
import genkey
import j1939.utils


if __name__ == "__main__":
    import logging
    import timeit
    import argparse

    examples = """
examples:
    # write the characters 'ERASE' to extension E9 ponter ED
    $ python j1939_mem_set.py -d 0x17 0xe9 0xed ERASE

    # Illuminate 'N' Telltale, write a byte (1) to extension EA pointer 6B
    $ python j1939_mem_set.py -d 0x17 0xea 0x6b 1

    # extinguish 'N' Telltale, 
    $ python j1939_mem_set.py -d 0x17 0xea 0x6b 0

    # Set B1/C4 Odometer to 200km (200=1km)
    $ python j1939_mem_set.py --destination=0x17 --length=4 0xf1 0x00 20000

    # Write 7 bytes of Backlight Settings.  Note the array has to have no spaces
    $ python j1939_mem_set.py -d 0x17 0xe9 0x01 [0x85,0x00,0x00,0x20,0x01,0x80,0x69]
    #                                  ptr  off  b0   b1   b2   b3   b4   b5   b6 


"""


    #import logging
    #import logging.handlers

    parser = argparse.ArgumentParser(description=title, formatter_class=argparse.RawDescriptionHelpFormatter, epilog=examples)

    parser.add_argument("-l", "--length", default="1", help="number of bytes in the object (1-4) default=1")
    parser.add_argument("-t", "--timeout", default="1000", help="ms before the request times out (default=1000 or 1s)")
    parser.add_argument("-s", "--source", default="0", help="source address (0-254) default=0")
    parser.add_argument("-d", "--destination", default="0x17", help="destination address (0-254) default=17")
    parser.add_argument("-c", "--channel", default="can0", help="Generally can0 on workstations or can1 on bbb/pbb targets")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Generate debugging output")
    parser.add_argument(      "--string", action="store_true", default=False, help="Treat an integer parameter as a string")
    parser.add_argument(      "--speed", default=250, help="CAN baudrate 250 or 500, (default 250)")

    parser.add_argument("extension",
                  default=None,
                  help="Memory object extension prefix to request in decimal or 0xhex")

    parser.add_argument("pointer",
                  default=None,
                  help="Memory object pointer offset to request in decimal or 0xhex")


    parser.add_argument('value',
                  default=None,
                  help="numeric or string value, if not a single byte, be sure to specify length.")

    args = parser.parse_args()

    if args.verbose:
        lLevel = logging.DEBUG
    else:
        lLevel = logging.WARN

    jlogger = logging.getLogger("j1939")
    jlogger.setLevel(lLevel)    
    ulogger = logging.getLogger("utils")
    ulogger.setLevel(lLevel)    
    clogger = logging.getLogger("can")
    clogger.setLevel(lLevel)    

    length = int(args.length,0)
    src = int(args.source,0)
    dest = int(args.destination,0)
    ext = int(args.extension,0)
    ptr = int(args.pointer,0)
    timeout = int(args.timeout,0)
    value = args.value

    # 
    # Try first to pull out a numeric ir byte list argument, otherwise set it as a string.
    # 
    try:
        if args.string:
            value = args.value
            length = len(value)
            print("Attepting to set 0x{:02x}/0x{:02x} to string {}, dlc={}".format(ext, ptr, value, len(value)))
        elif args.value.startswith('['):
            print ("processing array")
            ar = args.value[1:-1]
            print ("array = {}".format(ar))
            elements = ar.split(',')
            print ("elements = {}".format(elements))
            value = [int(s,0) for s in elements]
            print ("elements = {}".format(elements))
            length = len(value)
            print("Attepting to set 0x{:02x}/0x{:02x} to {}, dlc={}".format(ext, ptr, value, len(value)))
        else:
            value = int(args.value,0)
            print("Attepting to set 0x{:02x}/0x{:02x} to {}, dlc={}".format(ext, ptr, value, len(value)))

    except ValueError:
        if length < len(value):
            length = len(value)


    #value = hex(int(args.value,0))

    # queries a couple objects but setting up the full stack and bus for
    # each takes a long time.
    start = timeit.default_timer()
    val = j1939.utils.set_mem_object(ptr, ext, value, speed=args.speed, channel=args.channel, length=length, src=src, dest=dest, timeout=timeout)
    #set_mem_object_single(length=1, src=0, dest=0x17, pointer=0x66, extension=0xea, value=127)
    print("elapsed = %s s" % (timeit.default_timer() - start))
    print("return val = {}".format(int(val!=1)))
    sys.exit(val!=1)
