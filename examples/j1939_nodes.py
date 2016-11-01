from __future__ import print_function

from time import sleep

import can
import j1939
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



my_address = 0x09



def send_j1939():
    logger.debug("send_j1939, debug")
    logger.info("send_j1939, info")
    bus = j1939.Bus(channel='can0', bustype='socketcan',timeout=0.1)

    node1 = j1939.Node(bus, j1939.NodeName(0), [0x48])
    node2 = j1939.Node(bus, j1939.NodeName(0), [0x52])

    bus.connect(node1)
    bus.connect(node2)

    pgn_get = j1939.PGN(reserved_flag=False, data_page_flag=False, pdu_format=0xd9, pdu_specific=17)
    data = [0x10, 0x13, 0x11, 0x00, 0x00, 0xe9, 0xff, 0xff]

    node1.send_parameter_group(pgn_get, data, destination_device_name=19)

    if 0:
        pgn = j1939.PGN(reserved_flag=True,
                        pdu_specific=j1939.DESTINATION_ADDRESS_GLOBAL)

        arbitration_id = j1939.ArbitrationID(pgn=pgn, source_address=my_address)

        msg = j1939.PDU(arbitration_id=arbitration_id,
                        data=[0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80])

    sleep(0.5)
    node1.start_address_claim()
    sleep(0.5)

    if 0:
        try:
            bus.send(msg)
            logging.debug("Message sent on {}".format(bus.channel_info))
        except can.CanError:
            logging.debug("Message NOT sent")

    sleep(1)
    bus.flush_tx_buffer()
    bus.shutdown()

if __name__ == "__main__":
    send_j1939()
