import logging

from j1939.pgn import PGN
from j1939.constants import *
import logging
logger = logging.getLogger(__name__)

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
        logger.debug("can_id property: self._pgn.is_destination_specific=%s\npgn=%s" % (self._pgn.is_destination_specific, self._pgn))

        if self._pgn.is_destination_specific:
            logger.debug("can_id: self._pgn.is_destination_specific, dest=%s, pgn_value=%s, pdu_format=0x%x, pdu_specific=0x%x, pri=%s" %
                    (self.destination_address_value,
                    self._pgn.value,
                    self._pgn.pdu_format,
                    self._pgn.pdu_specific,
                    self.priority))

            if self.destination_address_value:
                retval = (self.source_address +
                         ((self._pgn.value & 0xff00) + (self.destination_address_value) << 8)+
                         (self.priority << 26))
            else:
                retval = (self.source_address +
                         ((self._pgn.value & 0xff00) << 8)+
                         (self.priority << 26))

            logger.debug("can_id: retval=0x%08x" % (retval))
            return retval
        else:
            logger.debug("can_id: NOT! self._pgn.is_destination_specific")
            return (self.source_address + (self._pgn.value << 8) + (self.priority << 26))

    @can_id.setter
    def can_id(self, canid):
        """
        Int between 0 and (2**29) - 1
        """
        logger.debug("can_id setter: canid=0x%08x" % (canid))
        self.priority = (canid & 0x1C000000) >> 26
        self._pgn = PGN().from_can_id(canid)
        self.source_address = canid & 0x000000FF
        if self._pgn.is_destination_specific:
            self.destination_address_value = (canid & 0x0000FF00) >> 8


        logger.debug("can_id: canid=0x%08x, priority=%x, pdu_format=%x, pdu_specific=%x, src=%x" %
                (canid,
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
