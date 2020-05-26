import time
import j1939

if __name__ == "__main__":

    # code to broadcast a DM1 message at 1 Hz
    # 18FECAFE#FFFF00000000FFFF

    channel = 'can0'
    bustype = 'socketcan'
    sourceaddr = 0xFE
    destaddr = 0xFF


    bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01, broadcast=False)

    data = [0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF]
    pgn = j1939.PGN()
    pgn.value = 0xFECA # DM1 
    aid = j1939.ArbitrationID(pgn=pgn, source_address=sourceaddr, destination_address=destaddr)
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)

    while True:
        bus.send(pdu) 
        time.sleep(1)
        



