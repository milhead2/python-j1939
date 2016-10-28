from __future__ import print_function

import can
import j1939
import time
import threading


if __name__ == "__main__":

    #from can.interfaces.interface import *

    filters = [{'pgn':0xd900},{'pgn':0xd800},{'pgn':0xd700},{'pgn':0xd400}]
    filters = []

    bus = j1939.Bus(channel='can0', bustype='socketcan', j1939_filters=filters, timeout=0.01)
    node = j1939.Node(bus, j1939.NodeName(), [17, 18])

    print ("bus: ", bus)
    node.start_address_claim()
    node.claim_address(17)

    time.sleep(5)
    
    pgn = j1939.PGN()
    pgn.value = 0xd900
    print ("pgn: ", pgn)
    aid = j1939.ArbitrationID(priority=7, pgn=pgn, source_address=0x51, destination_address=0x17)
    print("aid: ", aid)
    if pgn.is_destination_specific:
        print("Destination Specific. dest=0x{:02x}".format(aid.destination_address))



    data = [0x10, 0x13, 0x11, 0x00, 0x00, 0xe9, 0xff, 0xff]
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)
    pdu.display_radix='hex'
    print("pdu: ", pdu)

    print("can Id: 0x{:08x}".format(pdu.arbitration_id.can_id))

    bus.send(pdu)
    
    if 1:
        try:
            for msg in bus:
                msg.display_radix = 'hex'
                print(msg)
        except KeyboardInterrupt:
            bus.shutdown()
            print()
            
    time.sleep(0.5)
    bus.shutdown()

