import logging
from can import Message

from .arbitrationid import ArbitrationID
from .constants import pgn_strings, PGN_AC_ADDRESS_CLAIMED
from .nodename import NodeName

logger = logging.getLogger(__name__)

RADIX_DECIMAL=10
RADIX_HEX=16

class PDU(object):

    """
    A PDU is a higher level abstraction of a CAN message.
    J1939 ensures that long messages are taken care of.
    """

    def __init__(self, timestamp=0.0, arbitration_id=None, data=None, info_strings=None):
        """
        :param float timestamp:
            Bus time in seconds.
        :param :class:`can.protocols.j1939.ArbitrationID` arbitration_id:

        :param bytes/bytearray/list data:
            With length up to 1785.
        """
        if data is None:
            data = []
        if info_strings is None:
            info_strings = []
        self.timestamp = timestamp
        if arbitration_id:
            assert(isinstance(arbitration_id, ArbitrationID))
        self.arbitration_id = arbitration_id
        self._data = self._check_data(data)
        self.info_strings = info_strings
        self.radix=RADIX_DECIMAL

    def __eq__(self, other):
        """Returns True if the pgn, data, source and destination are the same"""
        if other is None:
            return False
        if self.pgn != other.pgn:
            return False
        if self._data != other.data:
            return False
        if self.source != other.source:
            return False
        if self.destination != other.destination:
            return False
        return True

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def pgn(self):
        if self.arbitration_id.pgn.is_destination_specific:
            return self.arbitration_id.pgn.value & 0xFF00
        else:
            return self.arbitration_id.pgn.value

    @property
    def destination(self):
        """Destination address of the message"""
        return self.arbitration_id.destination_address

    @destination.setter
    def destination(self, destination):
        """Destination address of the message"""
        self.arbitration_id.destination_address = destination

    @property
    def source(self):
        """Source address of the message"""
        return self.arbitration_id.source_address

    @source.setter
    def source(self, source):
        """Source address of the message"""
        self.arbitration_id.source_address = source

    @property
    def is_address_claim(self):
        return self.pgn == PGN_AC_ADDRESS_CLAIMED

    @property
    def arbitration_id(self):
        return self._arbitration_id

    @arbitration_id.setter
    def arbitration_id(self, other):
        if other is None:
            self._arbitration_id = ArbitrationID()
        elif isinstance(other, ArbitrationID):
            self._arbitration_id = other
        else:
            assert(0)

    def _check_data(self, value):
        assert isinstance(value, (list, bytearray)), 'Needs to be list received {}, {}'.format(type(value), value)
        assert len(value) <= 1785, 'Too much data to fit in a j1939 CAN message. Got {0} bytes'.format(len(value))
        if len(value) > 0:
            for element in value:
                if isinstance(element, str):
                    element = int(element)
                #logger.warn("!!! element=%s type(element)=%s" % (element, type(element)))
                assert element >= 0, 'Data values must be between 0 and 255, element={}'.format(element)
                assert element <= 255, 'Data values must be between 0 and 255'
        return value

    def data_segments(self, segment_length=8):
        retval = []
        for i in range(0, len(self.data), segment_length):
            retval.append(self.data[i:i + min(segment_length, (len(self.data) - i))])
        return retval

    def check_equality(self, other, fields, debug=False):
        """
        :param :class:`~can.protocols.j1939.PDU` other:
        :param list[str] fields:
        """

        logger.debug("check_equality starting")

        retval = True
        for field in fields:
            try:
                own_value = getattr(self, field)
            except AttributeError:
                logger.warning("'%s' not found in 'self'" % field)
                return False

            try:
                other_value = getattr(other, field)
            except AttributeError:
                logger.debug("'%s' not found in 'other'" % field)
                return False

            if debug:
                self.info_strings.append("%s: %s, %s" % (field, own_value, other_value))
            if own_value != other_value:
                return False

        logger.debug("Messages match")
        return retval

    @property
    def display_radix(self):
        return self.radix

    @display_radix.setter
    def display_radix(self, radix):
        if radix is None:
            self.radix=RADIX_DECIMAL
        if isinstance(radix, str):
            if radix.lower()=='decimal':
                self.radix=RADIX_DECIMAL
            if radix.lower()=='hex':
                self.radix=RADIX_HEX
            else:
                raise ValueError("Only 'hex' or 'decimal' are legitimate choices: %s" % radix)


    def __str__(self):
        """

        :return: A string representation of this message.

        """
        #logger.info("PI07: stringify PDU")

        if self.radix == RADIX_HEX:
            data_string = " ".join("{:02x}".format(byte) for byte in self.data)
        else:
            data_string = " ".join("{:3d}".format(byte) for byte in self.data)
        return "{s.timestamp:15.6f}    {s.arbitration_id}    {data}".format(s=self, data=data_string)
