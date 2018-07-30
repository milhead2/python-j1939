from __future__ import print_function


_name = "J1939 Memory-Object Writer"
__version__ = "1.0.1"
__date__ = "02/27/2018"
__exp__ = "()"  # (Release Version)
title = "%s Version: %s %s %s" % (_name, __version__, __date__, __exp__)



import j1939.utils


if __name__ == "__main__":

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

"""

    import timeit
    import argparse

    import logging
    import logging.handlers

    parser = argparse.ArgumentParser(description=title, formatter_class=argparse.RawDescriptionHelpFormatter, epilog=examples)

    parser.add_argument("-l", "--length", default="1", help="number of bytes in the object (1-4) default=1")
    parser.add_argument("-s", "--source", default="0", help="source address (0-254) default=0")
    parser.add_argument("-d", "--destination", default="0x17", help="destination address (0-254) default=17")

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

    length = int(args.length,0)
    src = int(args.source,0)
    dest = int(args.destination,0)
    ext = int(args.extension,0)
    ptr = int(args.pointer,0)
    value = args.value

    # 
    # Try first to pull out a numeric argument, otherwise set it as a string.
    # 
    try:
        value = int(args.value,0)
        print("Attepting to set %2X/%02X to %s" % (ext, ptr, value))
    except ValueError:
        if length < len(value):
            length = len(value)


    #value = hex(int(args.value,0))

    # queries a couple objects but setting up the full stack and bus for
    # each takes a long time.
    start = timeit.default_timer()
    val = j1939.utils.set_mem_object(ptr, ext, value, length=length, src=src, dest=dest)
    #set_mem_object_single(length=1, src=0, dest=0x17, pointer=0x66, extension=0xea, value=127)
    print("elapsed = %s s" % (timeit.default_timer() - start))
