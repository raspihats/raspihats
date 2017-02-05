"""
This module contains the I2CFrame class and related classes.
"""
from .. import crc16


class I2CFrameDecodeException(Exception):
    """Raised when I2C Frame decoding fails."""

class I2CFrame(object):
    """The I2CFrame is used for communication over the I2C bus:

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

    def __init__(self, id, cmd, data = []):
        self.id = id
        self.cmd = cmd
        self.data = data

    def encode(self):
        """Encode the frame fields: Id, Command, Data and Crc to a list of ints.

        Returns:
            :obj:`list` of :obj:`int`: List of frame bytes, raw data that can be transmitted over the I2C bus

        """
        data = [self.id, self.cmd] + self.data
        crc = crc16.modbus(data)
        return data + [(crc & 0xFF), ((crc >> 8) & 0xFF)]

    def decode(self, data):
        """Decode raw data from I2C bus. It's used to decode the I2C-HATs response. The fields Id and Command should already be set
        because a valid I2C-HAT response always has the same Id and Command bytes as the request.

        Args:
            data (:obj:`list` of :obj:`int`): Raw I2C data to be decoded

        Raises:
            :obj:`I2CFrameDecodeException`: If the response frame Crc check fails, or has an unexpected Id or Command

        """
        crc = crc16.modbus(data[:-2])
        if crc != (data[-1] << 8) + data[-2]:
            raise I2CFrameDecodeException('crc check failed')
        if self.id != data[0]:
            raise I2CFrameDecodeException('unexpected id')
        if self.cmd != data[1]:
            raise I2CFrameDecodeException('unexpected command')
        self.data = data[2:-2]
