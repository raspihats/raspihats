"""Public wire-protocol surface for the raspihats I2C-HAT boards.

This module is the single definition of the I2C-HAT frame format, command
set and protocol constants. Everything else in the package - and any other
implementation of the transport - builds on it.

It exists so that a second transport (an async daemon, a test harness, a
non-Python client) can speak the protocol without reimplementing it and
without importing anything that touches a bus. Nothing here performs I/O,
and nothing here imports ``smbus2``; the module is importable on any
machine, which is what makes offline configuration validation possible.

Stability commitment
--------------------

``raspihats.protocol`` is public API under semantic versioning:

* new commands, registers, board entries and constants may be **added** in a
  minor release;
* the frame layout, the CRC algorithm, and the value of any existing
  ``Command``, ``IrqRegister``, ``StatusWordBits`` or ``CounterType`` member
  will only change in a **major** release.

Everything reachable as ``raspihats.i2c_hats._frame`` or
``raspihats.i2c_hats._base`` carries a leading underscore and gets no such
promise - import from here instead.

The firmware is the authority for all of it; ``REGISTER-MAP.md`` in the
``i2c-hat`` firmware repository carries the same map with the firmware
version each command first appeared in.
"""
from collections import namedtuple
try:
    from enum import Enum
except ImportError:
    from enum34 import Enum
from . import crc16


def crc16_modbus(data):
    """CRC-16/MODBUS over a list of byte values.

    Args:
        data (:obj:`list` of :obj:`int`): Bytes to checksum

    Returns:
        :obj:`int`: The 16-bit checksum

    """
    return crc16.modbus(data)


class Command(Enum):
    """I2C-HAT commands.

    Command values are frozen for the whole 3.x series. Opcodes absent from
    this enum are absent on purpose: 0x25-0x29 (counter status, encoders)
    and 0x40-0x48 (analog) are allocated in the firmware's ``commands.h``
    but implemented by no released board, and a board answers an unknown
    command with 0xEE filler that fails the CRC check.
    """

    # common board commands
    GET_BOARD_NAME              = 0x10
    GET_FIRMWARE_VERSION        = 0x11
    GET_STATUS_WORD             = 0x12
    RESET                       = 0x13

    # Communication WatchDog commands
    CWDT_SET_PERIOD             = 0x14
    CWDT_GET_PERIOD             = 0x15
    IRQ_GET_REG                 = 0x16
    IRQ_SET_REG                 = 0x17
    # CiA 301 0x1011: guarded by the 'load' signature payload
    RESTORE_FACTORY_DEFAULTS    = 0x18
    # guarded by the 'boot' signature payload; board re-enumerates at the
    # ROM bootloader's I2C address (0x3E on F0 boards, 0x56 on G0)
    ENTER_BOOTLOADER            = 0x19
    # CiA 301 0x1020 configuration signature
    CONFIG_SET_SIGNATURE        = 0x1A
    CONFIG_GET_SIGNATURE        = 0x1B

    # Digital Inputs commands
    DI_GET_ALL_CHANNEL_STATES   = 0x20
    DI_GET_CHANNEL_STATE        = 0x21
    DI_GET_COUNTER              = 0x22
    DI_RESET_COUNTER            = 0x23
    DI_RESET_ALL_COUNTERS       = 0x24
    # CiA 401 alignment: 0x6003 filter constant, 0x6002 change polarity
    DI_SET_CHANNEL_FILTER       = 0x2A
    DI_GET_CHANNEL_FILTER       = 0x2B
    DI_SET_POLARITY             = 0x2C
    DI_GET_POLARITY             = 0x2D

    # Digital Outputs commands
    DQ_SET_POWER_ON_VALUE       = 0x30
    DQ_GET_POWER_ON_VALUE       = 0x31
    DQ_SET_SAFETY_VALUE         = 0x32
    DQ_GET_SAFETY_VALUE         = 0x33
    DQ_SET_ALL_CHANNEL_STATES   = 0x34
    DQ_GET_ALL_CHANNEL_STATES   = 0x35
    DQ_SET_CHANNEL_STATE        = 0x36
    DQ_GET_CHANNEL_STATE        = 0x37
    # CiA 401 alignment: 0x6202 change polarity, 0x6206 error mode (safety mask)
    DQ_SET_POLARITY             = 0x38
    DQ_GET_POLARITY             = 0x39
    DQ_SET_SAFETY_MASK          = 0x3A
    DQ_GET_SAFETY_MASK          = 0x3B
    # CiA 401 0x6208 filter mask output, volatile
    DQ_SET_WRITE_MASK           = 0x3C
    DQ_GET_WRITE_MASK           = 0x3D


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
        data (:obj:`list` of :obj:`int` or optional): Payload data bytes

    Attributes:
        id (:obj:`int`): ID byte
        cmd (:obj:`int`): Command byte
        data (:obj:`list` of :obj:`int`): Payload data bytes

    """

    # byte size for fields
    ID_SIZE = 1
    CMD_SIZE = 1
    CRC_SIZE = 2

    # smallest valid frame: id, command and crc, with no payload
    MIN_SIZE = ID_SIZE + CMD_SIZE + CRC_SIZE

    def __init__(self, id, cmd, data=None):
        self.id = id
        self.cmd = Command(cmd)
        self.data = [] if data is None else data

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
            :obj:`DecodeException`: If the response frame is shorter than a
                valid frame, if its Crc check fails, or if it has an
                unexpected Id or Command

        """
        # A short read is a transport glitch, not a programming error: it has
        # to raise DecodeException so the caller's retry loop catches it.
        if len(data) < self.MIN_SIZE:
            raise DecodeException(
                'response too short, ' + str(len(data)) + ' bytes, expecting at least ' + str(self.MIN_SIZE))
        crc = crc16.modbus(data[:-2])
        crc_in = (data[-1] << 8) + data[-2]
        if crc != crc_in:
            raise DecodeException('crc check failed, ' + hex(crc) + '!=' + hex(crc_in) + ' data:' + str([hex(x) for x in data]))
        if self.id != data[0]:
            raise DecodeException('unexpected id')
        if self.cmd.value != data[1]:
            raise DecodeException('unexpected command')
        self.data = data[2:-2]


#: Frame ids are masked to this before transmission. The Raspberry Pi I2C
#: peripheral has a bug affecting the MSb of the first byte, so the id must
#: stay in [0x00, 0x7F]. This is a requirement on every implementer of the
#: transport, not a convention of this package.
FRAME_ID_MASK = 0x7F


class StatusWordBits(Enum):
    """StatusWord bit masks (``Command.GET_STATUS_WORD``).

    ``CWDT_TIMEOUT`` is cleared by the read, so a status word read is
    destructive with respect to that bit.
    """
    POR_RESET                   = 0x01
    SOFT_RESET                  = 0x02
    IWD_RESET                   = 0x04
    CWDT_TIMEOUT                = 0x08
    DI_IRQ_CAPTURE_QUEUE_FULL   = 0x10


class IrqRegister(Enum):
    """IRQ sub-registers, addressed through ``Command.IRQ_GET_REG`` and
    ``Command.IRQ_SET_REG`` with a payload of ``[register, u32 little-endian]``.

    * ``DI_FALLING_EDGE_CONTROL`` (CiA 401 0x6008) and
      ``DI_RISING_EDGE_CONTROL`` (0x6007) are one bit per channel. They are
      **volatile below firmware 3.0.0** and **EEPROM-persistent from 3.0.0**.
    * ``DI_CAPTURE`` reads one queue entry as ``(states << 16) | edge_status``;
      0 means the queue is empty, and a real entry is never 0. Writing 0
      clears the queue - it is the only value a write accepts. Queue depth is
      128 entries; the oldest is dumped on overflow and
      ``StatusWordBits.DI_IRQ_CAPTURE_QUEUE_FULL`` is set.
    * ``DI_GLOBAL_ENABLE`` (CiA 401 0x6005) exists **only from firmware
      3.0.0**, where it is a volatile arming bit that reads 0 after every
      reset. Edges are captured only while it is 1, so a host that sets the
      edge masks and never arms this register sees nothing. A CWDT trip
      disarms it. On older firmware this sub-register answers 0xEE filler.
    """
    DI_FALLING_EDGE_CONTROL     = 0x20
    DI_RISING_EDGE_CONTROL      = 0x21
    DI_CAPTURE                  = 0x22
    DI_GLOBAL_ENABLE            = 0x23


class CounterType(Enum):
    """Edge counter selector, the second payload byte of
    ``Command.DI_GET_COUNTER`` and ``Command.DI_RESET_COUNTER``.

    Counters are unsigned 32-bit and wrap.
    """
    FALLING = 0
    RISING = 1


#: The CWDT period travels the wire as unsigned 32-bit **milliseconds**
#: (``Command.CWDT_SET_PERIOD`` / ``CWDT_GET_PERIOD``), and is persistent.
CWDT_PERIOD_UNIT = 'ms'

#: Writing this period disables the communication watchdog.
CWDT_PERIOD_DISABLED = 0

#: Largest CWDT period the u32 wire field can carry, in milliseconds.
CWDT_PERIOD_MAX = 0xFFFFFFFF

#: Payload that guards ``Command.RESTORE_FACTORY_DEFAULTS`` (CiA 301 0x1011).
#: Only this exact request acts; the board sends no response and needs about
#: a second to erase its EEPROM and restart.
RESTORE_FACTORY_DEFAULTS_SIGNATURE = [ord(c) for c in 'load']

#: Payload that guards ``Command.ENTER_BOOTLOADER``. The board sends no
#: response and re-enumerates at the ROM bootloader's own address - 0x3E on
#: the F0 boards, 0x56 on G0.
ENTER_BOOTLOADER_SIGNATURE = [ord(c) for c in 'boot']

#: Response payload size in bytes, per command - the number of **data** bytes,
#: excluding id, command and CRC. A transport must know this before it reads,
#: because the read length is fixed in advance:
#: ``Frame.ID_SIZE + Frame.CMD_SIZE + RESPONSE_DATA_SIZE[cmd] + Frame.CRC_SIZE``.
#: ``None`` means the board sends no response at all.
RESPONSE_DATA_SIZE = {
    Command.GET_BOARD_NAME:             25,
    Command.GET_FIRMWARE_VERSION:       3,
    Command.GET_STATUS_WORD:            4,
    Command.RESET:                      None,
    Command.CWDT_SET_PERIOD:            4,
    Command.CWDT_GET_PERIOD:            4,
    Command.IRQ_GET_REG:                5,
    Command.IRQ_SET_REG:                5,
    Command.RESTORE_FACTORY_DEFAULTS:   None,
    Command.ENTER_BOOTLOADER:           None,
    Command.CONFIG_SET_SIGNATURE:       4,
    Command.CONFIG_GET_SIGNATURE:       4,
    Command.DI_GET_ALL_CHANNEL_STATES:  4,
    Command.DI_GET_CHANNEL_STATE:       2,
    Command.DI_GET_COUNTER:             6,
    Command.DI_RESET_COUNTER:           2,
    Command.DI_RESET_ALL_COUNTERS:      0,
    Command.DI_SET_CHANNEL_FILTER:      5,
    Command.DI_GET_CHANNEL_FILTER:      5,
    Command.DI_SET_POLARITY:            4,
    Command.DI_GET_POLARITY:            4,
    Command.DQ_SET_POWER_ON_VALUE:      4,
    Command.DQ_GET_POWER_ON_VALUE:      4,
    Command.DQ_SET_SAFETY_VALUE:        4,
    Command.DQ_GET_SAFETY_VALUE:        4,
    Command.DQ_SET_ALL_CHANNEL_STATES:  4,
    Command.DQ_GET_ALL_CHANNEL_STATES:  4,
    Command.DQ_SET_CHANNEL_STATE:       2,
    Command.DQ_GET_CHANNEL_STATE:       2,
    Command.DQ_SET_POLARITY:            4,
    Command.DQ_GET_POLARITY:            4,
    Command.DQ_SET_SAFETY_MASK:         4,
    Command.DQ_GET_SAFETY_MASK:         4,
    Command.DQ_SET_WRITE_MASK:          4,
    Command.DQ_GET_WRITE_MASK:          4,
}


class BoardInfo(namedtuple('BoardInfo',
                           'name board_name base_address labels has_cwdt has_irq')):
    """Inert, bus-free description of one I2C-HAT model.

    This is the same data the board classes carry, in a form that can be
    imported and read without opening a bus - which is what a host needs in
    order to validate a configuration before touching hardware.

    Attributes:
        name (:obj:`str`): Model name, as used as the key in :data:`BOARDS`
        board_name (:obj:`str`): The string the board itself reports for
            ``Command.GET_BOARD_NAME``
        base_address (:obj:`int`): Family base I2C address; the four address
            jumpers select an offset of 0x00 to 0x0F above it
        labels (:obj:`dict`): Section name (``'di'``, ``'dq'``) to a tuple of
            vendor channel labels. The tuple length is the channel count.
        has_cwdt (:obj:`bool`): Board carries the communication watchdog
        has_irq (:obj:`bool`): Board carries the IRQ module and drives the
            shared interrupt line

    """

    __slots__ = ()

    @property
    def address_range(self):
        """:obj:`tuple` of :obj:`int`: Inclusive ``(low, high)`` I2C address range."""
        return (self.base_address, self.base_address + 0x0F)

    def channel_count(self, section):
        """Number of channels in a section, 0 if the board has no such section.

        Args:
            section (:obj:`str`): ``'di'`` or ``'dq'``

        Returns:
            :obj:`int`: Channel count

        """
        return len(self.labels.get(section, ()))


def _board(name, board_name, base_address, di=None, dq=None, has_irq=False):
    labels = {}
    if di is not None:
        labels['di'] = tuple(di)
    if dq is not None:
        labels['dq'] = tuple(dq)
    return BoardInfo(name, board_name, base_address, labels, True, has_irq)


def _numbered(prefix, count, start=0):
    return tuple(prefix + str(i) for i in range(start, start + count))


#: Every I2C-HAT model the protocol covers, keyed by model name. The board
#: classes in :mod:`raspihats.i2c_hats` take their address, reported name and
#: channel labels from here, so this table and those classes cannot disagree.
#:
#: Only four models carry the IRQ module - a host must reject an
#: interrupt-driven configuration naming any other board.
BOARDS = {}
for _info in (
    # legacy models
    _board('Di16', 'Di16 I2C-HAT', 0x40,
           di=tuple('Di%d.%d' % (g, c) for g in range(1, 5) for c in range(1, 5))),
    _board('Rly10', 'Rly10 I2C-HAT', 0x50,
           dq=_numbered('Rly', 10, start=1)),
    _board('Di6Rly6', 'Di6Rly6 I2C-HAT', 0x60,
           di=tuple('Di1.%d' % c for c in range(1, 7)),
           dq=_numbered('Rly', 6, start=1)),
    # current models
    _board('DI16ac', 'DI16ac I2C-HAT', 0x40,
           di=_numbered('I', 16), has_irq=True),
    _board('DQ16oc', 'DQ16oc I2C-HAT', 0x50,
           dq=_numbered('Q', 16)),
    _board('DQ10rly', 'DQ10rly I2C-HAT', 0x50,
           dq=_numbered('Q', 10)),
    _board('DQ8rly', 'DQ8rly I2C-HAT', 0x50,
           dq=_numbered('Q', 8)),
    _board('DQ5rly', 'DQ5rly I2C-HAT', 0x50,
           dq=_numbered('Q', 5)),
    _board('DI6acDQ6rly', 'DI6acDQ6rly I2C-HAT', 0x60,
           di=_numbered('I', 6), dq=_numbered('Q', 6), has_irq=True),
    _board('DI6acDQ6ssr', 'DI6acDQ6ssr I2C-HAT', 0x60,
           di=_numbered('I', 6), dq=_numbered('Q', 6), has_irq=True),
    _board('DI6dwDQ6ssr', 'DI6dwDQ6ssr I2C-HAT', 0x60,
           di=_numbered('I', 6), dq=_numbered('Q', 6), has_irq=True),
):
    BOARDS[_info.name] = _info
del _info


def board_info(board_name):
    """Look up a board by the name it reports over the bus.

    Args:
        board_name (:obj:`str`): Value read with ``Command.GET_BOARD_NAME``

    Returns:
        :obj:`BoardInfo`: The matching board, or ``None`` if unknown

    """
    for info in BOARDS.values():
        if info.board_name == board_name:
            return info
    return None
