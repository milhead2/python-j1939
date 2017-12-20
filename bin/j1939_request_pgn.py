from __future__ import print_function

import j1939

import logging

lLevel = logging.DEBUG

logger = logging.getLogger()
logger.setLevel(lLevel)
ch = logging.StreamHandler()
fh = logging.FileHandler('/tmp/j1939_request_pgn.log')
fh.setLevel(lLevel)
ch.setLevel(lLevel)
formatter = logging.Formatter('%(asctime)s | %(name)20s | %(threadName)20s | %(levelname)5s | %(message)s')
chformatter = logging.Formatter('%(name)25s | %(threadName)10s | %(levelname)5s | %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(chformatter)
logger.addHandler(ch)
logger.addHandler(fh)




if __name__ == "__main__":
    import traceback
    import timeit
    import time


def request_pgn(channel='can0', bustype='socketcan', src=0, dest=0x17, reqPGN=0x00feda):
    #from can.interfaces.interface import *

    countdown = 10
    result = -1

    bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01)

    nodename = j1939.NodeName(0)
    nodename.arbitrary_address_capable = 1

    node1 = j1939.Node(bus, j1939.NodeName(0), [0])
    bus.connect(node1)


    pgn = j1939.PGN()
    pgn.value = 0xea00 | dest
    aid = j1939.ArbitrationID(pgn=pgn, source_address=src, destination_address=dest)

    data = [((reqPGN>>0)&0xff), ((reqPGN>>8)&0xff), ((reqPGN>>16)&0xff)]
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)
    pdu.display_radix='hex'

    bus.send(pdu)

    while countdown:
        pdu = bus.recv()
        if pdu and pdu.pgn == reqPGN:
            return pdu;
            break # got what I was waiting for

        countdown -= 1

    bus.shutdown()

    return None

if __name__ == "__main__":

    # queries a couple objects but setting up the full stack and bus for
    # each takes a long time.
    start = timeit.default_timer()
    if request_pgn(src=0, dest=0x27):
        print("Returned Success!")
    else:
        print("Returned None!")

    print("elapsed = %s s" % (timeit.default_timer() - start))



    # just a blurb to see
    start = timeit.default_timer()
    time.sleep(1)
    print("elapsed = %s s" % (timeit.default_timer() - start))
