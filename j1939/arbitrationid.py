import logging

from j1939.pgn import PGN
from j1939.constants import *

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
        self.priority = priority
        self.pgn = pgn
        self.source_address = source_address
        self.destination_address_value = None
        if self.pgn.is_destination_specific:
            if destination_address is None:
                self.destination_address_value = DESTINATION_ADDRESS_GLOBAL
            else:
                if destination_address >= 0 and destination_address <= 255:
                    print("da=",destination_address)
                    self.destination_address_value = destination_address
                else:
                    raise ValueError("desttiantion address must be in range (0-255)")

    @property
    def can_id(self):
        logger.info("j1939.arbitrationid.can_id: self.pgn.is_destination_specific")
        logger.info("       self.pgn.is_destination_specific=%s" % self.pgn.is_destination_specific)
        logger.info("       self.source_address=%s" % self.source_address)
        logger.info("       self.destination_address_value=%s" % self.destination_address_value)
        logger.info("       self.pgn.value=0x%08x" % self.pgn.value)
        logger.info("       self.priority=%s" % self.priority)

        if self.pgn.is_destination_specific:
            # TODO: Not sure why I get the dest address in both the PGN and dest_addr...  In
            # any case if it's dest specificx and I have it in both, remove it from the pgn before
            # building the CAN ID
            if self.pgn.value & 0x00ff:
                return (self.source_address + (self.destination_address_value << 8) + ((self.pgn.value & 0xff00) << 8) + (self.priority << 26))
            else:
                return (self.source_address + (self.destination_address_value << 8) + (self.pgn.value << 8) + (self.priority << 26))
        else:
            return (self.source_address + (self.pgn.value << 8) + (self.priority << 26))

    @can_id.setter
    def can_id(self, value):
        """
        Int between 0 and (2**29) - 1
        """
        self.priority = (value & 0x1C000000) >> 26
        self.pgn.value = (value & 0x03FFFF00) >> 8
        self.source_address = value & 0x000000FF
        if self.pgn.is_destination_specific:
            self.destination_address_value = (value & 0x0000FF00) >> 8

    @property
    def destination_address(self):
        if self.pgn.is_destination_specific:
            return self.destination_address_value
        else:
            return None

    @destination_address. setter
    def destination_address(self, addr):
        if not self.pgn.is_destination_specific:
            raise ValueError("PGN is not dest specific: {:04x}".format(self.pgn))
        else:
            self.destination_address_value = addr


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
        if self.pgn.is_destination_specific:
            retval = "PRI=%d PGN=%6s DST=0x%.2x SRC=0x%.2x" % (
                self.priority, self.pgn, self.destination_address_value, self.source_address)
        else:
            retval = "PRI=%d PGN=%6s          SRC=0x%.2x" % (self.priority, self.pgn, self.source_address)
        return retval
