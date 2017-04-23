"""
This module contains the I2C Frame class and related classes.
"""
from enum import Enum
from .. import crc16

class Command(Enum):
    """I2C-HAT commands"""

    # common board commands
    GET_BOARD_NAME = 0x10
    GET_FIRMWARE_VERSION = 0x11
    GET_STATUS_WORD = 0x12
    RESET = 0x13

    # Communication WatchDog commands
    CWDT_SET_PERIOD = 0x14
    CWDT_GET_PERIOD = 0x15
    CWDT_SET_STATE = 0x16

    # Digital Inputs commands
    DI_GET_ALL_CHANNEL_STATES = 0x20
    DI_GET_CHANNEL_STATE = 0x21
    DI_GET_COUNTER = 0x22
    DI_RESET_COUNTER = 0x23
    DI_RESET_ALL_COUNTERS = 0x24

    # Digital Outputs commands
    DQ_SET_POWER_ON_VALUE = 0x30
    DQ_GET_POWER_ON_VALUE = 0x31
    DQ_SET_SAFETY_VALUE = 0x32
    DQ_GET_SAFETY_VALUE = 0x33
    DQ_SET_ALL_CHANNEL_STATES = 0x34
    DQ_GET_ALL_CHANNEL_STATES = 0x35
    DQ_SET_CHANNEL_STATE = 0x36
    DQ_GET_CHANNEL_STATE = 0x37

class DecodeException(Exception):
    """Raised when I2C Frame decoding fails."""

class Frame(object):
    """The Frame is used for communication over the I2C bus:

    +----+---------+------+------------------------------------------------------------------------------------------+
    | #  | Field   | Size | Description                                                                              |
    +====+=========+======+==========================================================================================+
    | 1. | Id      | 1    | Diferent from one request to another, I2C-HAT responds with the same Id byte.            |
    +----+---------+------+------------------------------------------------------------------------------------------+
    | 2. | Command | 1    | Defines the action to be taken by the I2C-HAT which responds with the same Command byte. |
    +----+---------+------+------------------------------------------------------------------------------------------+
    | 3. | Data    | n    | Payload data.                                                                            |
    +----+---------+------+------------------------------------------------------------------------------------------+
    | 4. | Crc     | 2    | Modbus CRC16 for data integrity.                                                         |
    +----+---------+------+------------------------------------------------------------------------------------------+

    Args:
        id (:obj:`int`): ID byte
        cmd (:obj:`int`): Command byte
        data (:obj:`list` of :obj:`int`): Payload data bytes

    Attributes:
        id (:obj:`int`): ID byte
        cmd (:obj:`int`): Command byte
        data (:obj:`list` of :obj:`int`): Payload data bytes

    """

    # byte size for fields
    ID_SIZE = 1
    CMD_SIZE = 1
    CRC_SIZE = 2

    def __init__(self, id, cmd, data=[]):
        self.id = id
        self.cmd = Command(cmd)
        self.data = data

    def encode(self):
        """Encode the frame fields: Id, Command, Data and Crc to a list of ints.

        Returns:
            :obj:`list` of :obj:`int`: List of frame bytes, raw data that can be transmitted over the I2C bus

        """
        data = [self.id, self.cmd.value] + self.data
        crc = crc16.modbus(data)
        return data + [(crc & 0xFF), ((crc >> 8) & 0xFF)]

    def decode(self, data):
        """Decode raw data from I2C bus. It's used to decode the I2C-HATs response. The fields Id and Command should already be set
        because a valid I2C-HAT response always has the same Id and Command bytes as the request.

        Args:
            data (:obj:`list` of :obj:`int`): Raw I2C data to be decoded

        Raises:
            :obj:`DecodeException`: If the response frame Crc check fails, or has an unexpected Id or Command

        """
        crc = crc16.modbus(data[:-2])
        if crc != (data[-1] << 8) + data[-2]:
            raise DecodeException('Crc check failed')
        if self.id != data[0]:
            raise DecodeException('Unexpected id')
        if self.cmd.value != data[1]:
            raise DecodeException('Unexpected command')
        self.data = data[2:-2]
