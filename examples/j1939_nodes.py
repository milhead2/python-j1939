from __future__ import print_function

from time import sleep

import can
import j1939


def send_j1939():
    bus = j1939.Bus(channel='can0', bustype='socketcan',timeout=0.1)

    node1 = j1939.Node(bus, j1939.NodeName(0), [0x48])
    node2 = j1939.Node(bus, j1939.NodeName(0), [0x52])

    bus.connect(node1)
    bus.connect(node2)

    #bus.j1939_notifier.listeners.append(node1)
    #bus.j1939_notifier.listeners.append(node2)

    pgn = j1939.PGN(reserved_flag=True,
                    pdu_specific=j1939.constants.DESTINATION_ADDRESS_GLOBAL)
    arbitration_id = j1939.ArbitrationID(pgn=pgn, source_address=0x01)
    msg = j1939.PDU(arbitration_id=arbitration_id,
                    data=[0x10, 0x20, 0x30])

    sleep(1)
    node1.start_address_claim()
    sleep(1)
    try:
        bus.send(msg)
        print("Message sent on {}".format(bus.channel_info))
    except can.CanError:
        print("Message NOT sent")

    sleep(1)
    bus.flush_tx_buffer()
    bus.shutdown()

if __name__ == "__main__":
    send_j1939()
