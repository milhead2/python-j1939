import logging
import inspect

logger = logging.getLogger("j1939")

class PGN(object):

    def __init__(self, reserved_flag=False, data_page_flag=False, pdu_format=0, pdu_specific=0):
        self.reserved_flag = reserved_flag
        self.data_page_flag = data_page_flag
        self.pdu_format = pdu_format
        self.pdu_specific = pdu_specific

    @property
    def is_pdu1(self):
        result =  (((self.pdu_format & 0xFF) < 240) or self.reserved_flag)
        logger.debug("PGN is_pdu1 {:04x}: {}".format(self.pdu_format, result))
        logger.debug("            (self.pdu_format & 0xFF) < 240 {:04x}: {}".format(self.pdu_format, (self.pdu_format & 0xFF) < 240))
        logger.debug("            self.reserved_flag {:04x}: {}".format(self.pdu_format, self.reserved_flag))
        logger.debug("            self.data_page_flag {:04x}: {}".format(self.pdu_format, self.data_page_flag))
        return result

    @property
    def is_pdu2(self):
        return not self.is_pdu1

    @property
    def is_destination_specific(self):
        result = self.is_pdu1
        logger.debug("PGN is_destination_specific {:04x}: {}".format(self.value, result))
        return result

    @property
    def value(self):
        _pgn_flags_byte = ((self.reserved_flag << 1) + self.data_page_flag)
        return int("%.2x%.2x%.2x" % (_pgn_flags_byte, self.pdu_format, self.pdu_specific), 16)

    @value.setter
    def value(self, value):
        self.reserved_flag = (value & 0x080000) >> 17
        self.data_page_flag = (value & 0x040000) >> 16
        self.pdu_format = (value & 0x03FF00) >> 8
        self.pdu_specific = value & 0x0000FF
        #MIL logger.debug("PGN.@valueSetter, value=0x%08x, pdu_format=0x%08x" % (value, self.pdu_format))

    @staticmethod
    def from_value(pgn_value):
        logger.debug("PGN.@from_value, pgn_value=0x%08x" % (pgn_value))
        pgn = PGN()
        pgn.reserved_flag = (pgn_value & 0x080000) >> 17
        pgn.data_page_flag = (pgn_value & 0x040000) >> 16
        pgn.pdu_format = (pgn_value & 0x03FF00) >> 8
        pgn.pdu_specific = pgn_value & 0x0000FF
        return pgn

    @staticmethod
    def from_can_id(canid):
        logger.info("{} staticmethod: canid=0x{:08x}".format(inspect.stack()[0][3], canid))
        canid = canid>>8
        pgn = PGN()
        
        pgn.reserved_flag = (canid & 0x080000) >> 17
        pgn.data_page_flag = (canid & 0x040000) >> 16
        pgn.pdu_format = (canid & 0x03FF00) >> 8
        pgn.pdu_specific = canid & 0x0000FF
        logger.info("{} staticmethod: PGN Creation, res={}, dp={}, pdu_format=0x{:02x}, pdu_specific=0x{:02x}".format(inspect.stack()[0][3],
                pgn.reserved_flag, 
                pgn.data_page_flag, 
                pgn.pdu_format, 
                pgn.pdu_specific))

        return pgn

    def __str__(self):
        retval = ("0x%.5x " % ((((self.pdu_format)<<8) | (self.pdu_specific)) & 0x3FFFF))

        if self.reserved_flag:
            retval += "R "
        else:
            retval += "  "

        if self.data_page_flag:
            retval += "P "
        else:
            retval += "  "

        if 0:
            if self.is_destination_specific:
                retval += "DS "
            else:
                retval += "!DS"

        return retval
