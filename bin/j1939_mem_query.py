from __future__ import print_function

import j1939

if __name__ == "__main__":
    import traceback
    import timeit
    import time

def get_mem_object_single(channel='can0', bustype='socketcan', length=4, src=0, dest=0x17, pointer=0, extension=0):
    #from can.interfaces.interface import *

    countdown = 10
    result = -1

    bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01)
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

    bus.shutdown()

    return result

def get_mem_object(bus=None, length=4, src=0, dest=0x17, pointer=0, extension=0):
    countdown = 10
    result = -1

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

    return result

if __name__ == "__main__":

    # queries a couple objects but setting up the full stack and bus for
    # each takes a long time.
    start = timeit.default_timer()
    for p, e in [(0x15, 0xe9), (0x00, 0xf1), (0x50, 0xe9), (0x75, 0xe9)]:
        val = get_mem_object_single(length=4, src=0, dest=0x17, pointer=p, extension=e)
        print("0x%02x-0x%02x = %d" % (p, e, val))
    print("elapsed = %s s" % (timeit.default_timer() - start))


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


    start = timeit.default_timer()
    time.sleep(5)
    print("elapsed = %s s" % (timeit.default_timer() - start))
