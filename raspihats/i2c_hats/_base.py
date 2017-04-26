"""
This module contains the I2CHat base class.
"""
import sys
import time
import smbus
import threading
from enum import Enum
from ._frame import Command, Frame, DecodeException

class ResponseException(Exception):
    """Raised when there's a problem with the I2C-HAT response."""


class I2CHat(object):
    """Implements basic functionality common to all I2C-HATs.

    Args:
        address (int): I2C bus address, valid range depends of base_address
        base_address (int): I2C-HAT family starting address
        board_name (str): I2C-HAT expected board name

    Raises:
        ValueError: If address is not in range

    (*) - attribute value read directly from I2C-HAT

    """

    _i2c_bus_lock = threading.Lock()
    _i2c_bus = None
    try:
        _i2c_bus = smbus.SMBus(1)     # default for Raspberry Pi
    except:
        print("I2C port not found!")

    def __init__(self, address, base_address=None, board_name=None):
        self._address = address
        self._frame_id = 0x1F - 1
        self._transfer_time = None

        if base_address == None:
            if not 0 <= address <= 127:
                raise ValueError("I2C address should be in range[0, 127]")
        else:
            if address & base_address != base_address:
                raise ValueError("I2C address should be in range[" + hex(base_address) + ", " + hex(base_address + 0x0F) + "]")

        if board_name != None:
            if self.name not in board_name:
                raise Exception("unexpected board name '" + self.name + "', expecting '" + board_name + "'")

    def __str__(self):
        string = self.__class__.__name__
        base = 'I2CHat'
        if base not in string:
            string += base
        string += "@" + hex(self._address)
        return string

    def _generate_frame_id_(self):
        """Generate new frame Id, increments current frame Id, wraps to 0xFF.

        Returns:
            int: The new frame Id

        """
        self._frame_id += 1
        self._frame_id &= 0xFF
        return self._frame_id

    def _transfer_(self, request_frame, response_data_size, response_expected=True, number_of_tries=5):
        """Tries a number of times to send a request frame and to get a response frame over I2C bus.

        Args:
            request_frame (Frame): Request frame to be sent over the I2C bus
            response_data_size (int): Expected response data size, this is the payload data size
            response_expected (bool): True if a respose is expected
            number_of_tries (int): Number of tries to get the response

        Returns:
            Frame: The response frame

        Raises:
            ResponseException: After all attempts to get a response have failed

        """
        with I2CHat._i2c_bus_lock:
            try_cnt = 1
            while True:
                try:
                    request_data = request_frame.encode()

                    # NOTE: write_i2c_block_data function is used to send commands to the I2C-HAT
                    I2CHat._i2c_bus.write_i2c_block_data(self._address, request_data[0], request_data[1:])

                    if not response_expected:
                        return

                    # NOTE: read_i2c_block_data function sends a i2c_write first, this write has a length of one, and the dummy_byte as payload, this
                    # write will be ignored by the I2C-HAT, after this a i2c_read will be issued, this i2c_read is used for reading the response
                    dummy_byte = 0xFF
                    expected_response_size = Frame.ID_SIZE + Frame.CMD_SIZE + response_data_size + Frame.CRC_SIZE
                    response_data = I2CHat._i2c_bus.read_i2c_block_data(self._address, dummy_byte, expected_response_size)

                    # build response frame
                    response_frame = Frame(request_frame.id, request_frame.cmd)
                    response_frame.decode(response_data)
                    self._transfer_time = time.time()
                    return response_frame

                except (IOError, DecodeException) as ex:
                    if try_cnt >= number_of_tries:
                        if isinstance(ex, IOError):
                            raise ResponseException("no response")
                        else:
                            raise ResponseException(str(ex))
                    time.sleep(0.01)
                    try_cnt += 1

    def _get_u32_value_(self, cmd):
        """Generic get for a unsigned32 value.

        Args:
            cmd (int): Command byte value

        Returns:
            int: The desired unsigned32 value

        Raises:
            ResponseException: If response has bad data length

        """
        request = self._request_frame_(cmd, [])
        response = self._transfer_(request, 4)
        data = response.data
        if len(data) != 4:
            raise ResponseException('invalid response data length')
        return data[0] + (data[1] << 8) + (data[2] << 16) + (data[3] << 24)

    def _set_u32_value_(self, cmd, value):
        """Generic set for a unsigned32 value.

        Args:
            cmd (int): Command byte value
            value (int): Value to be set

        Returns:
            int: The desired unsigned32 value

        Raises:
            ResponseException: I response
        """
        data = [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF]
        request = self._request_frame_(cmd, data)
        response = self._transfer_(request, 4)
        if data != response.data:
            raise ResponseException('invalid response data')

    def _request_frame_(self, cmd, data = []):
        """Build request frame, taking care of new frame Id generation.

        Args:
            cmd (int): Frame command byte value
            data (List[int]): Frame payload data

        Returns:
            Frame: The new Frame built with specified parameters

        """
        return Frame(self._generate_frame_id_(), cmd, data)

    @property
    def transfer_time(self):
        """:obj:`float`: Last valid transfer time stamp."""
        return self._transfer_time

    @property
    def address(self):
        """:obj:`int`: I2C bus address."""
        return self._address

    @property
    def name(self):
        """:obj:`string`: Name(*)."""
        request = self._request_frame_(Command.GET_BOARD_NAME)
        response = self._transfer_(request, 25)
        board_name = ''
        for byte in response.data:
            if byte == 0:
                break;
            board_name += chr(byte)
        return board_name

    @property
    def fw_version(self):
        """:obj:`string`: Firmware version(*)."""
        request = self._request_frame_(Command.GET_FIRMWARE_VERSION)
        response = self._transfer_(request, 3)
        data = response.data
        return 'v' + chr(data[0] + 0x30) + '.' + chr(data[1] + 0x30)  + '.' + chr(data[2] + 0x30)

    @property
    def status(self):
        """:obj:`StatusWord`: Status word(*)."""
        return StatusWord(self._get_u32_value_(Command.GET_STATUS_WORD))

    def reset(self):
        """Sends a reset request to the I2C-HAT."""
        request = self._request_frame_(Command.RESET)
        self._transfer_(request, 0, False)

class StatusWord(object):
    """Models Status Word

    Args:
        value (int): Status Word raw integer value

    Attributes:
        value (int): Status Word raw integer value.
    """

    class Bits(Enum):
        """Status Word bit masks"""
        POR_RESET = 0x01
        SOFT_RESET = 0x02
        IWD_RESET = 0x04
        CWDT_TIMEOUT = 0x08

    def __init__(self, value):
        self.value = value

    def __str__(self):
        """Human readable string describing the Status Word."""
        string = "status:" + hex(self.value)
        if (self.value & 0x0F) != 0x00:
            string += " ["
            for bit in self.Bits:
                if (self.value & bit.value) != 0x00:
                    string += str(bit) + ", "
            string = string[:-2]
            string += "]"
        return string

class Functionality(object):
    """I2C-HAT functionality base.

    Args:
        i2c_hat (:obj:`raspihats.i2c_hats._base.I2CHat`): I2CHat instance
        labels (:obj:`list` of :obj:`str` or optional): Channel labels

    """

    def __init__(self, i2c_hat, labels=None):
        self._i2c_hat = i2c_hat
        self._labels = labels
        if labels != None:
            self._lc_labels = [l.lower() for l in labels]

    def _validate_channel_index(self, index):
        if self._labels == None:
            raise Exception('no labels defined')

        label = None
        if isinstance(index, int):
            if not (0 <= index < len(self._labels)):
                raise IndexError("'" + str(index) + "' is not a valid channel index")
        elif isinstance(index, str):
            label = index
            try:
                index = self._lc_labels.index(label.lower())
            except ValueError:
                raise ValueError("'" + label + "' is not a valid channel label")
        else:
            raise ValueError("index type is '" + type(index) + "', expecting 'int' or 'str'")
        return index

    def _validate_value(self, value):
        max_value = (0x01 << len(self._labels)) - 1
        if not (0 <= value <= max_value):
            raise ValueError("'" + str(value) + "' is not a valid value, range is [0x00 .. " + hex(max_value) + "]")

    @property
    def labels(self):
        """:obj:`list` of :obj:`str`: Channel Labels."""
        return self._labels

class Cwdt(Functionality):
    """Provides attributes and methods for operating the I2C-HAT CommunicationWatchdogTimer module.

    Args:
        i2c_hat (:obj:`raspihats.i2c_hats._base.I2CHat`): I2CHat instance

    (*) - attribute value read directly from I2C-HAT

    """

    def __init__(self, i2c_hat):
        Functionality.__init__(self, i2c_hat)

    @property
    def period(self):
        """:obj:`float`: The CommunicationWatchdogTimer period value in seconds(*)."""
        return float(self._i2c_hat._get_u32_value_(Command.CWDT_GET_PERIOD)) / 1000

    @period.setter
    def period(self, value):
        if value < 0:
            raise ValueError("period should be greather than zero to enable the CommunicationWatchdogTimer on the I2C-HAT board")
        self._i2c_hat._set_u32_value_(Command.CWDT_SET_PERIOD, int(value * 1000))
