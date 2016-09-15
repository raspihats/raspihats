"""
This module contains the I2CFrame class and related classes.
"""
from .crc16 import calc


class I2CFrameDecodeException(Exception):
    """Raised when I2CFrame.decode() fails."""

class I2CFrame(object):
    """The I2CFrame is used for reliable communication over the I2C bus:
    
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
    
    """
    
    # byte size for fields
    ID_SIZE = 1
    CMD_SIZE = 1
    CRC_SIZE = 2

    def __init__(self, id_, cmd, data = []):
        """Build I2CFrame object setting Id, Command, and Data Fields, check if all values are valid uint8 first.
        
        Args:
            fid(int): Frame ID byte
            cmd(int): Frame Command byte
            data(List[int]): Payload data bytes
        
        """
        self.__check_uint8(id_)
        self.__check_uint8(cmd)
        self.__check_uint8(data)
        
        self.__id = id_
        self.__cmd = cmd
        self.__data = data
        
    def __check_uint8(self, data):
        """Check if data is valid uint8 value or a list of uint8 values.
        
        Args:
            data(int or List[int]): A uint8 value or a list of uint8 values
        
        Raises:
            ValueError: If data is not a uint8 valid value, or a list of uint8 values
            
        """
        if isinstance(data, int):
            data = [data]
        for byte in data:
            if not 0 <= byte <= 0xFF:
                raise ValueError("expecting uint8 value")

    @property
    def id(self):
        """Get the frame Id byte.
        
        Returns:
            int: The frame Id byte value
            
        """
        return self.__id

    @property
    def cmd(self):
        """Get the frame Command byte.
        
        Returns:
            int: The frame Command byte value
            
        """
        return self.__cmd

    @property
    def data(self):
        """Get the frame payload data.
        
        Returns:
            List[int]: The Data field which conatins the payload data bytes
            
        """
        return self.__data
    
    def encode(self):
        """Encode the frame fields: Id, Command, Data and Crc to a list of ints.
        
        Returns:
            List[int]: List of frame bytes, raw data that can be transmitted over the I2C bus
            
        """
        data = [self.__id, self.__cmd] + self.__data
        crc = calc(data) 
        return data + [(crc & 0xFF), ((crc >> 8) & 0xFF)]
    
    def decode(self, data):
        """Decode raw data from I2C bus. It's used to decode the I2C-HATs response. The fields Id and Command should already be set
        because a valid I2C-HAT response always has the same Id and Command bytes as the request. 
        
        Args:
            data (List[int]): Raw I2C data to be decoded
        
        Raises:
            I2CFrameDecodeException: If the response frame Crc check fails, or has an unexpected Id or Command
            
        """
        self.__check_uint8(data)
        crc = calc(data[:-2])
        if crc != (data[-1] << 8) + data[-2]:
            raise I2CFrameDecodeException('Crc check failed')
        if self.__id != data[0]:
            raise I2CFrameDecodeException('unexpected Id')
        if self.__cmd != data[1]:
            raise I2CFrameDecodeException('unexpected Command')
        self.__data = data[2:-2]