from __future__ import print_function

import can
import j1939
import time
import threading

import logging

lLevel = logging.DEBUG

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


if __name__ == "__main__":

    #from can.interfaces.interface import *

    filters = [{'pgn':0xd900},{'pgn':0xd800},{'pgn':0xd700},{'pgn':0xd400}]

    bus = j1939.Bus(channel='can0', bustype='socketcan', j1939_filters=filters, timeout=0.01)
    node = j1939.Node(bus, j1939.NodeName(), [19])
    bus.connect(node)

    logger.info("bus: %s"
    node.start_address_claim()
    node.claim_address(18)

    time.sleep(5)
    
    pgn = j1939.PGN()
    pgn.value = 0xd900
    logger.info("pgn: ", pgn)
    aid = j1939.ArbitrationID(priority=7, pgn=pgn, source_address=0x19, destination_address=0x17)
    logger.info("aid: ", aid)
    if pgn.is_destination_specific:
        logger.info("Destination Specific. dest=0x{:02x}".format(aid.destination_address))



    data = [0x10, 0x13, 0x11, 0x00, 0x00, 0xe9, 0xff, 0xff]
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)
    pdu.display_radix='hex'
    logger.info("pdu: ", pdu)

    logger.info("can Id: 0x{:08x}".format(pdu.arbitration_id.can_id))

    bus.send(pdu)
    
    if 0:
        try:
            for msg in bus:
                msg.display_radix = 'hex'
                logger.info(msg)
        except KeyboardInterrupt:
            bus.shutdown()
            logger.info()
            
    time.sleep(2)
    bus.shutdown()

