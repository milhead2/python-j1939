from __future__ import print_function
import j1939
import logging
import inspect
import sys

logger = logging.getLogger("j1939")
#
# for responding to seed/key requests provide your own keyGenerator
# class..
# mine is returned in a SeedToKey meghod of a Genkey class that sits elsewhere
# on my PYTHONPATH and is propriatiry
#
# TODO: use a better baseclass override model.
#
try:
    import genkey
    security250 = genkey.GenKey(speed=250)
    security500 = genkey.GenKey(speed=500)
    logger.info("Private Genkey Loaded")
except:
    # Stuff in a fake genKey responder.  Pretty much just needs a
    # reference to any class that can convert a Seed to a Key..  For
    # obvious reasons I'm not posting mine
    logger.warning("Genkey Not loaded, This one will generate garbage keys")
    class Genkey:
        def SeedToKey(self, seed):
            return 0x12345678

    security = Genkey()

def set_mem_object(pointer, extension, value, channel='can0', bustype='socketcan', length=4, src=0, dest=0x17, speed=250, bus=None, timeout=10):
    countdown = timeout
    result = -1
    close = False

    logger.debug("------------------------------- Set Mem Object: speed={}, security250={}, security500={}".format(speed, security250, security500))

    keygetFunction = None

    if int(speed) == 250:
        keygetFunction = security250.SeedToKey
        logger.debug("PI02f speed=500, keygetFunction={}".format(keygetFunction))
    elif int(speed) == 500:
        keygetFunction = security500.SeedToKey
        logger.debug("PI02f speed=500, keygetFunction={}".format(keygetFunction))
    else:
        logger.debug("PI02f speed=Unknown, keygetFunction={}".format(keygetFunction))
        pass

    logger.debug("------------------------------- keygetFunction={}".format(keygetFunction))

    # only watch for the memory object pgn's
    filt = [{'pgn':0xd800, 'source':dest},{'pgn':0xd400, 'source':dest}]

    if bus is None:
        bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01, keygen=keygetFunction, broadcast=False, j1939_filters=filt)
        node = j1939.Node(bus, j1939.NodeName(), [src])
        bus.connect(node)
        close = True

    pLow = pointer & 0x0000FF
    pMid = (pointer >> 8) & 0x0000FF
    pHigh = (pointer >> 16) & 0x0000FF
			
    dm14data = [length, 0x15, pLow, pMid, pHigh, extension, 0xff, 0xff]

    dm14pgn = j1939.PGN(pdu_format=0xd9, pdu_specific=dest)
    dm14aid = j1939.ArbitrationID(pgn=dm14pgn, source_address=src, destination_address=dest)
    dm14pdu = j1939.PDU(timestamp=0.0, arbitration_id=dm14aid, data=dm14data, info_strings=None)
    dm14pdu.display_radix='hex'

    bus.send(dm14pdu)

    sendBuffer = []
    #sendBuffer.append(length)
    #for i in range(0, length):
    #    sendBuffer.append(0)

    logger.info("---------------## length=%d, value=%s " % (length, value))
    if isinstance(value, int) and length < 8:
        logger.info("-----value")
        if length < 8:
            sendBuffer.append(length)
            for i in range(0, length):
                sendBuffer.append((value >> (8*i)) & 0xff)
        else:
            raise ValueError("Don't know how to send a %d byte integer" % length)

    elif isinstance(value, list):
        # if sending a list use the exact list elements as the data
        logger.info("-----list of {} byte(s)".format(len(value)))
        sendBuffer.append(len(value))
        for i in range(len(value)):
            logger.info("---------------## b[{}]=0x{:02x}".format(i, value[i]))
            sendBuffer.append(value[i])

    elif isinstance(value, str):
        logger.info("-----str, value={}, len(value)={}. length={}".format(value, len(value), length))
        assert(len(value) <= length)
        sendBuffer.append(length+1)
        for i in range(len(value)):
            sendBuffer.append(ord(value[i]))

    else:
        raise ValueError("Data type not supported.")

    logger.info("---------------## sendBuffer=%s ", sendBuffer)

    dm16pgn = j1939.PGN(pdu_format=0xd7, pdu_specific=dest)
    dm16aid = j1939.ArbitrationID(pgn=dm16pgn, source_address=src, destination_address=dest)
    dm16pdu = j1939.PDU(timestamp=0.0, arbitration_id=dm16aid, data=sendBuffer)
    dm16pdu.display_radix='hex'

    logger.info("----------------## PDU=%s ", dm16pdu)

    # Wait around for a while looking for the second proceed
    while countdown:
        countdown -= 1
        rcvPdu = bus.recv(timeout=0.25)
        if rcvPdu:
            rcvPdu.display_radix='hex'
            logger.debug("received PDU: %s", rcvPdu)
            if rcvPdu.pgn == 0xd800:
                if rcvPdu.data[0]==1 and rcvPdu.data[1]==0x11:
                    if rcvPdu.data[6] == 0xff and rcvPdu.data[7] == 0xff:
                        bus.send(dm16pdu)
                        logger.info('Sent %s', dm16pdu)
                elif rcvPdu.data[0]==0 and rcvPdu.data[1]==0x19:
                    logger.info("Value Sent")
                    result = 1
                    break
                elif rcvPdu.data[0]==0 and rcvPdu.data[1]==0x1B:
                    logger.info("Rejected")
                    result = 0
                    break
    if close:
        bus.shutdown()
    return result

def get_mem_object(pointer, extension, channel='can0', bustype='socketcan', length=4, src=0, dest=0x17, bus=None, speed=250, timeout=10):
    logger.info("{}: begin".format(inspect.stack()[0][3]))
    countdown = timeout
    result = None
    close = False

    if bus is None:
        bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01, broadcast=False)
        node = j1939.Node(bus, j1939.NodeName(), [src])
        bus.connect(node)
        close = True

    pgn = j1939.PGN()
    pgn.value = 0xd900 + dest # Request a DM14 mem-object
    aid = j1939.ArbitrationID(pgn=pgn, source_address=src, destination_address=dest)

    # Get the 3 bytes of the pointer and put them in the correct locations
    pointer0 = pointer & 0xff
    pointer1 = (pointer & 0xff00) >> 8
    pointer2 = (pointer & 0xff0000) >> 16

    data = [length, 0x13, pointer0, pointer1, pointer2, extension, 0xff, 0xff]
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)
    assert(pdu != None)
    pdu.display_radix='hex'
    logger.info("{}: Sending Request PDU: {}".format(inspect.stack()[0][3], pdu))
    bus.send(pdu)

    #
    # Wait for the response
    #
    while countdown:
        pdu = bus.recv(timeout=1)
        if pdu is not None:
            logger.info("{}: Received PDU: {}".format(inspect.stack()[0][3], pdu))
            logger.info(pdu)
            if pdu.pgn == 0xd700:
                value = list(pdu.data)
                length = value[0]
                if length == 1:
                    result = value[1]
                elif length == 2:
                    result = (value[2] << 8) + value[1]
                elif length == 4:
                    result = (value[4] << 24) + (value[3] << 16) + (value[2] << 8) + value[1]
                else:
                    result = value[1:]

                #logger.info("{}: d700 received, result: {}/0x{:08x}".format(inspect.stack()[0][3], result, result))
                
                break # got what I was waiting for

        countdown -= 1

    if close:
        logger.info("{}: Closing Bus".format(inspect.stack()[0][3]))
        bus.shutdown()

    if result is None:
        raise IOError(" no CAN response")


    return result

def request_pgn(requested_pgn, channel='can0', speed=250, bustype='socketcan', length=4, src=0, dest=0x17, bus=None, timeout=10):
    countdown = timeout
    result = None
    close = False

    keygetFunction = None
    if speed == 250:
        keygetFunction = security250.SeedToKey
    if speed == 500:
        keygetFunction = security500.SeedToKey

    if not isinstance(requested_pgn, int):
        raise ValueError("pgn must be an integer.")

    if bus is None:
        bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01, keygen=keygetFunction, broadcast=False)
        node = j1939.Node(bus, j1939.NodeName(), [src])
        bus.connect(node)
        close = True
        
    pgn = j1939.PGN()
    pgn.value = 0xea00 + dest # request_pgn mem-object
    aid = j1939.ArbitrationID(pgn=pgn, source_address=src, destination_address=dest)

    pgn0 = requested_pgn & 0xff
    pgn1 = (requested_pgn >> 8) & 0xff
    pgn2 = (requested_pgn >> 16) & 0xff

    data = [pgn0, pgn1, pgn2]
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)

    pdu.display_radix='hex'

    bus.send(pdu)
    maxPdu = 50
    while countdown:
        pdu = bus.recv(timeout=1)
        if pdu and (pdu.pgn == 0xe800 or pdu.pgn == requested_pgn):
            result = list(pdu.data) 
            break # got what I was waiting for

        elif pdu:
            maxPdu -=1
            if maxPdu <= 0:
                raise IOError('Bus too busy')
        elif pdu is None:
            countdown -= 1
        else:
            raise Exception('WHAT HAPPENED')
    if close:
        bus.shutdown()
    if not result:
        raise IOError(" no CAN response")
    return result


def send_pgn(requested_pgn, data, channel='can0', speed=250, bustype='socketcan', length=4, src=0, dest=0x17, bus=None, timeout=10):
    countdown = timeout
    result = None
    close = False

    keygetFunction = None
    if speed == 250:
        keygetFunction = security250.SeedToKey
    if speed == 500:
        keygetFunction = security500.SeedToKey

    if not isinstance(requested_pgn, int):
        raise ValueError("pgn must be an integer.")
    if bus is None:
        bus = j1939.Bus(channel=channel, bustype=bustype, timeout=0.01, keygen=keygetFunction)
        close = True
        
    pgn = j1939.PGN()
    if requested_pgn < 0xf000:
        requested_pgn |= dest
    pgn.value = requested_pgn#0xea00 + dest # request_pgn mem-object
    aid = j1939.ArbitrationID(pgn=pgn, source_address=src, destination_address=dest)

    logger.info(data)
    pdu = j1939.PDU(timestamp=0.0, arbitration_id=aid, data=data, info_strings=None)

    pdu.display_radix='hex'

    bus.send(pdu)
    if close:
        bus.shutdown()
    if 0: #leaving in miller's if 0
        while countdown:
            pdu = bus.recv(timeout=1)
            if pdu and (pdu.pgn == 0xe800 or pdu.pgn == requested_pgn):
                result = list(pdu.data)
                break # got what I was waiting for
            if pdu:
                countdown -= 1
        if not result:
            raise IOError(" no CAN response")
        return result

