import logging
logger = logging.getLogger(__name__)




class PGN(object):

    def __init__(self, reserved_flag=False, data_page_flag=False, pdu_format=0, pdu_specific=0):
        self.reserved_flag = reserved_flag
        self.data_page_flag = data_page_flag
        self.pdu_format = pdu_format
        self.pdu_specific = pdu_specific

    @property
    def is_pdu1(self):
        return ((self.pdu_format < 240) or self.reserved_flag or self.data_page_flag)

    @property
    def is_pdu2(self):
        return not self.is_pdu1

    @property
    def is_destination_specific(self):
        return self.is_pdu1

    @property
    def value(self):
        _pgn_flags_byte = ((self.reserved_flag << 1) + self.data_page_flag)
        return int("%.2x%.2x%.2x" % (_pgn_flags_byte, self.pdu_format, self.pdu_specific), 16)

    @value.setter
    def value(self, value):
        self.reserved_flag = (value & 0x020000) >> 17
        self.data_page_flag = (value & 0x010000) >> 16
        self.pdu_format = (value & 0x00FF00) >> 8
        self.pdu_specific = value & 0x0000FF

    @staticmethod
    def from_value(pgn_value):
        logger.debug("PGN.@from_value, pgn_value=0x%08x" % (pgn_value))
        pgn = PGN()
        pgn.reserved_flag = (pgn_value & 0x020000) >> 17
        pgn.data_page_flag = (pgn_value & 0x010000) >> 16
        pgn.pdu_format = (pgn_value & 0x00FF00) >> 8
        pgn.pdu_specific = pgn_value & 0x0000FF
        return pgn

    @staticmethod
    def from_can_id(canid):
        #logger.debug("PGN.@from_can_id, value=0x%08x" % (canid))
        canid = canid>>8
        pgn = PGN()
        #logger.debug("PGN.@from_can_id, value=0x%08x" % (canid))
        pgn.reserved_flag = (canid & 0x020000) >> 17
        pgn.data_page_flag = (canid & 0x010000) >> 16
        pgn.pdu_format = (canid & 0x00FF00) >> 8
        pgn.pdu_specific = canid & 0x0000FF
        logger.debug("PGN.@from_can_id, res=%d, dp=%d, pdu_format=0x%02x, pdu_specific=0x%02x" %
                (pgn.reserved_flag, pgn.data_page_flag, pgn.pdu_format, pgn.pdu_specific))
        return pgn

    def __str__(self):
        retval = ("0x%.4x " % ((((self.pdu_format)<<8) | (self.pdu_specific)) & 0xFFFF))

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
