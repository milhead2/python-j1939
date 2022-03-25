import logging
import inspect


from j1939.pgn import PGN
from j1939.constants import *
import logging
logger = logging.getLogger("j1939")

class ArbitrationID(object):

    def __init__(self, priority=7, pgn=None, source_address=0, destination_address=None):
        """
        :param int priority:
            Between 0 and 7, where 0 is highest priority.

        :param :class:`can.protocols.j1939.PGN`/int pgn:
            The parameter group number.

        :param int source_address:
            Between 0 and 255.

        :param int destinaion_address:
            Between 0 and 255. Will trrow a ValueError if PGN does not allow a dest

        """
        self._pgn = None
        self.priority = priority
        self.destination_address_value = None

        logger.debug("ArbitrationID:__init__: self._pgn=%s, type %s" % (pgn, type(pgn)))

        if pgn is None:
            self._pgn = PGN()
        elif pgn and isinstance(pgn, int):
            self._pgn = PGN.from_value(pgn)
        elif pgn and isinstance(pgn, PGN):
            self._pgn = pgn
        else:
            ValueError("pgn must have convertable type")


        #self.pgn = pgn

        logger.debug("ArbitrationID:__init__: self._pgn=%s, type %s" % (self._pgn, type(self._pgn)))
        if self._pgn:
            if self._pgn.is_destination_specific:
                if destination_address is None:
                    self.destination_address_value = DESTINATION_ADDRESS_GLOBAL
                else:
                    if destination_address >= 0 and destination_address <= 255:
                        self.destination_address_value = destination_address
                        if  self.destination_address_value != self._pgn.pdu_specific:
                                logger.debug("self._pgn=%s, self.destination_address_value = %x, pgn.pdu_specific = %x" %
                                        (self._pgn, self.destination_address_value, self._pgn.pdu_specific))
#                        assert( self.destination_address_value == pgn.pdu_specific)
                    else:
                        raise ValueError("destination address must be in range (0-255)")

        self.source_address = source_address

    @property
    def can_id(self):
        logger.info("{} property: self._pgn.is_destination_specific={}/pgn={}".format(inspect.stack()[0][3], self._pgn.is_destination_specific, self._pgn))

        if self._pgn.is_destination_specific:
            logger.info("can_id: self._pgn.is_destination_specific, dest={}, pgn_value={}, pdu_format=0x{:04x}, pdu_specific=0x{:02x}, pri={}".format(
                    self.destination_address_value,
                    self._pgn.value,
                    self._pgn.pdu_format,
                    self._pgn.pdu_specific,
                    self.priority))

            if self.destination_address_value:
                logger.info("can_id: self.destination_address_value: pgn_value: {:04x}".format(self._pgn.value))
                logger.info("         (self._pgn.value & 0x3ff00): {:04x}".format((self._pgn.value & 0x3ff00)))
                logger.info("         (self.destination_address_value): {:04x}".format((self.destination_address_value)))
                retval = (self.source_address +
                         ((self._pgn.value & 0x3ff00) + (self.destination_address_value) << 8) +
                         (self.priority << 26))
            else:
                logger.info("can_id: NOT self.destination_address_value:")
                retval = (self.source_address +
                         ((self._pgn.value & 0x3ff00) << 8)+
                         (self.priority << 26))

            logger.info("can_id: retval=0x{:08x}".format(retval))
            return retval
        else:
            logger.info("can_id: NOT! self._pgn.is_destination_specific")
            return (self.source_address + (self._pgn.value << 8) + (self.priority << 26))

    @can_id.setter
    def can_id(self, canid):
        """
        Int between 0 and (2**29) - 1
        """
        logger.info("{} setter: canid=0x{:08x}".format(inspect.stack()[0][3], canid))
        self.priority = (canid & 0x1C000000) >> 26
        self._pgn = PGN().from_can_id(canid)
        self.source_address = canid & 0x000000FF
        if self._pgn.is_destination_specific:
            self.destination_address_value = (canid & 0x0000FF00) >> 8


        logger.info("{} setter: canid=0x{:08x}, priority={:x}, pdu_format={:x}, pdu_specific={:x}, src={:x}".format(inspect.stack()[0][3],
                canid,
                self.priority,
                self._pgn.pdu_format,
                self._pgn.pdu_specific,
                self.source_address))
    @property
    def destination_address(self):
        if self._pgn.is_destination_specific:
            return self.destination_address_value
        else:
            return None

    @destination_address.setter
    def destination_address(self, value):
        if not self._pgn.is_destination_specific:
            raise ValueError("PGN is not dest specific: {:04x}".format(self._pgn))
        else:
            self.destination_address_value = value


    @property
    def pgn(self):
        return self._pgn

    @pgn.setter
    def pgn(self, other):
        if other is None:
            self._pgn = PGN()
        elif not isinstance(other, PGN):
            self._pgn = PGN.from_value(other)
        else:
            self._pgn = other

    def __str__(self):
        logger.debug("arbitrationid.__str__: ids:%d, pri:%s, pgn:%s, dest:%s, src:%s, ids:%d" %
                (self._pgn.is_destination_specific, self.priority, self._pgn, self.destination_address_value, self.source_address, self._pgn.is_destination_specific))

        if self._pgn.is_destination_specific:
            if self.destination_address_value is not None:
                retval = "PRI=%d PGN=%6s DST=0x%.2x SRC=0x%.2x" % (
                    self.priority, self._pgn, self.destination_address_value, self.source_address)
            else:
                retval = "PRI=%d PGN=%6s DST=NONE(error) SRC=0x%.2x" % (
                    self.priority, self._pgn, self.source_address)
        else:
            retval = "PRI=%d PGN=%6s          SRC=0x%.2x" % (self.priority, self._pgn, self.source_address)
        return retval
