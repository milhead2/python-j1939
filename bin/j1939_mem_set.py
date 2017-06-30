from __future__ import print_function


_name = "J1939 Memory-Object Writer"
__version__ = "1.0.0"
__date__ = "06/22/2017"
__exp__ = "(sabot)"  # (Release Version)
title = "%s Version: %s %s %s" % (_name, __version__, __date__, __exp__)



import j1939

#
# for responding to seed/key requests provide your own keyGenerator
# class..
# mine is returned in a SeedToKey meghod of a Genkey class that sits elsewhere
# on my PYTHONPATH
#
# TODO: use a better baseclass override model.
#
try:
    import genkey
    security = genkey.GenKey()
    print("Genkey Loaded")
except:
    # Stuff in a fake genKey responder.  Pretty much just needs a
    # reference to any class that can convert a Seed to a Key..  For
    # obvious reasons I'm not posting mine
    print("Genkey Not loaded, This one will generate garbage keys")
    class Genkey:
        def SeedToKey(self, seed):
            return 0x12345678;

    security = Genkey()

def set_mem_object_single(channel='can0', bustype='socketcan', length=4, src=0, dest=0x17, pointer=0, extension=0, value=0):
    #from can.interfaces.interface import *

    countdown = 10
    result = -1

    bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01, keygen=security.SeedToKey)


    #dm14pgn = j1939.PGN()
    dm14data = [length, 0x15, pointer, 0x00, 0x00, extension, 0xff, 0xff]

    dm14pgn = j1939.PGN(pdu_format=0xd9, pdu_specific=dest)
    #dm14pgn = j1939.PGN().value = 0xd917
    #print ("dm14pgn=", dm14pgn)
    #print ("dm14pgn.destination_address_value=", dm14pgn.destination_address_value)
    #print ("dm14pgn.pdu_specific=", dm14pgn.pdu_specific)
    dm14aid = j1939.ArbitrationID(pgn=dm14pgn, source_address=src, destination_address=dest)
    dm14pdu = j1939.PDU(timestamp=0.0, arbitration_id=dm14aid, data=dm14data, info_strings=None)
    dm14pdu.display_radix='hex'


    bus.send(dm14pdu)

    sendBuffer = [length, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
    if length == 1:
        sendBuffer[1] = value;
    elif length == 2:
        sendBuffer[1] = value & 0xff
        sendBuffer[2] = (value >> 8) & 0xff
    elif length == 3:
        sendBuffer[1] = value & 0xff
        sendBuffer[2] = (value >> 8) & 0xff
        sendBuffer[3] = (value >> 16) & 0xff
    elif length == 4:
        sendBuffer[1] = value & 0xff
        sendBuffer[2] = (value >> 8) & 0xff
        sendBuffer[3] = (value >> 16) & 0xff
        sendBuffer[4] = (value >> 24) & 0xff
    else:
        raise ValueError("Don't know how to send a %d byte object" % length)

    dm16pgn = j1939.PGN(pdu_format=0xd7, pdu_specific=dest)
    dm16aid = j1939.ArbitrationID(pgn=dm16pgn, source_address=src, destination_address=dest)
    dm16pdu = j1939.PDU(timestamp=0.0, arbitration_id=dm16aid, data=sendBuffer)
    dm16pdu.display_radix='hex'


    # Wait around for a while looking for the second proceed

    countdown=10
    proceedCount = 0;
    while countdown:
        countdown -= 1
        rcvPdu = bus.recv(2)
        if rcvPdu:
            rcvPdu.display_radix='hex'
            #print("received PDU: %s", rcvPdu)
            if rcvPdu.pgn == 0xd800:
                if rcvPdu.data[0]==1 and rcvPdu.data[1]==0x11:
                    proceedCount += 1
                    if proceedCount == 2:
                        bus.send(dm16pdu)
                if rcvPdu.data[0]==0 and rcvPdu.data[1]==0x19:
                    print("Value Sent")
                    break;


    bus.shutdown()

    return result


if __name__ == "__main__":

    import timeit
    import argparse

    parser = argparse.ArgumentParser(description=title)

    parser.add_argument("-l", "--length", default="1", help="number of bytes in the object (1-4) default=1")
    parser.add_argument("-s", "--source", default="0", help="source address (0-254) default=0")
    parser.add_argument("-d", "--destination", default="0x17", help="destination address (0-254) default=17")
    parser.add_argument("-p", "--pointer", default="0x58", help="j1939 pointer (0-0xffffff) default=0x58")
    parser.add_argument("-e", "--extension", default="0xe9", help="j1939 pointer extension (0-0xffffff) default=0x58")
    parser.add_argument('value')
    args = parser.parse_args()

    length = int(args.length,0)
    src = int(args.source,0)
    dest = int(args.destination,0)
    ext = int(args.extension,0)
    ptr = int(args.pointer,0)
    value = int(args.value,0)

    print("Attepting to set %2X/%02X to %d" % (ext, ptr, value))
    #value = hex(int(args.value,0))

    # queries a couple objects but setting up the full stack and bus for
    # each takes a long time.
    start = timeit.default_timer()
    val = set_mem_object_single(length=length, src=src, dest=dest, pointer=ptr, extension=ext, value=value)
    #set_mem_object_single(length=1, src=0, dest=0x17, pointer=0x66, extension=0xea, value=127)
    print("elapsed = %s s" % (timeit.default_timer() - start))
