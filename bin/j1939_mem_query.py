from __future__ import print_function

import can
import j1939
import time
import threading

import logging

lLevel = logging.WARN

logger = logging.getLogger()
logger.setLevel(lLevel)
ch = logging.StreamHandler()
fh = logging.FileHandler('/tmp/j1939_nodes.log')
fh.setLevel(lLevel)
ch.setLevel(lLevel)
formatter = logging.Formatter('%(asctime)s | %(name)20s | %(threadName)20s | %(levelname)5s | %(message)s')
chformatter = logging.Formatter('%(name)25s | %(threadName)10s | %(levelname)5s | %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(chformatter)
logger.addHandler(ch)
logger.addHandler(fh)

def get_mem_object(channel='can0', bustype='socketcan', length=4, src=0, dest=0x17, pointer=0, extension=0):
    #from can.interfaces.interface import *

    countdown = 5
    result = -1

    bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01)
    pgn = j1939.PGN()
    pgn.value = 0xd917
    #logger.info("pgn: %s" % pgn)
    aid = j1939.ArbitrationID(pgn=pgn, source_address=src, destination_address=dest)
    #logger.info("aid: %s" % aid)
    #if pgn.is_destination_specific:
    #    logger.info("Destination Specific. dest=0x{:02x}".format(aid.destination_address))

#    PRI=6 PGN=0xd917      DST=0x17 SRC=0x00    08 13 15 00 00 e9 ff ff
#    PRI=6 PGN=0xd800      DST=0x00 SRC=0x17    02 11 ff ff ff ff ff ff
#    PRI=7 PGN=0xd700      DST=0x00 SRC=0x17    02 00 01 ff ff ff ff ff
#    PRI=6 PGN=0xd800      DST=0x00 SRC=0x17    00 19 ff ff ff ff ff ff

    data = [length, 0x13, pointer, 0x00, 0x00, extension, 0xff, 0xff]
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)
    pdu.display_radix='hex'
    logger.info("pdu: %s" % pdu)

    #logger.info("can Id: 0x{:08x}".format(pdu.arbitration_id.can_id))

    bus.send(pdu)

    while countdown:
        #print("Waiting for PDU")
        pdu = bus.recv()
        #print("received pdu: %s, pgn = 0x%04x" % (pdu, pdu.pgn))
        if pdu.pgn == 0xd700:
            value = list(pdu.data)
            length = value[0]
            if length == 1:
                result = value[1]
            if length == 2:
                result = (value[2] << 8) + value[1]
            if length == 4:
                result = (value[4] << 24) + (value[3] << 16) + (value[2] << 8) + value[1]
            #print("length = %d" % length)
            #print("value = %s" % value)
            #rint("decoded value = %d" % (result))




        countdown -= 1

    bus.shutdown()

    return result

if __name__ == "__main__":

    for p, e in [(0x15, 0xe9), (0x00, 0xf1), (0x50, 0xe9), (0x75, 0xe9)]:
        val = get_mem_object(length=4, src=0, dest=0x17, pointer=p, extension=e)
        print("0x%02x-0x%02x = %d" % (p, e, val))
