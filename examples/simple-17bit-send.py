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
    pgn2 = j1939.PGN()
    pgn3 = j1939.PGN()
    #pgn.value = 0xFECA # DM1 
    pgn.value = 0xFF17 # DM1 
    pgn2.value = 0x1FF17 # DM1 
    pgn3.value = 0x2FF17 # DM1 
    print("pgn.values: {}/{}".format(pgn.value, pgn2.value))
    aid = j1939.ArbitrationID(pgn=pgn, source_address=sourceaddr, destination_address=destaddr)
    aid2 = j1939.ArbitrationID(pgn=pgn2, source_address=sourceaddr, destination_address=destaddr)
    aid3 = j1939.ArbitrationID(pgn=pgn3, source_address=sourceaddr, destination_address=destaddr)
    print("aid: {}".format(aid))
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)
    pdu2 = j1939.PDU(timestamp=0.0, arbitration_id=aid2, data=data, info_strings=None)
    pdu3 = j1939.PDU(timestamp=0.0, arbitration_id=aid3, data=data, info_strings=None)
    print("pdu: {}".format(pdu))

    while True:
        print("pre send\n    {}\n    {}\n    {}".format(pdu, pdu2, pdu3))
        bus.send(pdu) 
        bus.send(pdu2) 
        bus.send(pdu3) 
        time.sleep(1)
        



