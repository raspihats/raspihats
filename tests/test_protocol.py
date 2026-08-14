"""Unit tests for :mod:`raspihats.protocol`. No hardware, no I2C bus.

These pin the wire format and the public protocol surface. A change here that
is not a deliberate protocol change is a bug - see the stability commitment in
``docs/protocol.rst``.

Run with::

    python3 -m pytest tests/ -v
"""
import sys
import subprocess

import pytest

from raspihats.protocol import (
    BOARDS, BoardInfo, Command, CounterType, DecodeException, Frame,
    FRAME_ID_MASK, IrqRegister, RESPONSE_DATA_SIZE, StatusWordBits,
    CWDT_PERIOD_DISABLED, CWDT_PERIOD_MAX,
    ENTER_BOOTLOADER_SIGNATURE, RESTORE_FACTORY_DEFAULTS_SIGNATURE,
    board_info, crc16_modbus,
)


# --------------------------------------------------------------------------
# CRC
# --------------------------------------------------------------------------

def _crc16_modbus_bitwise(data):
    """Independent, table-free CRC-16/MODBUS.

    Deliberately a different algorithm from the shipped table-driven one, so
    agreement between the two is evidence rather than tautology.
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte & 0xFF
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def test_crc_check_value():
    """The standard CRC-16/MODBUS check value for b'123456789'."""
    assert crc16_modbus([ord(c) for c in '123456789']) == 0x4B37


def test_crc_matches_independent_implementation():
    data = []
    for i in range(256):
        data.append((i * 37 + 11) & 0xFF)
        assert crc16_modbus(data) == _crc16_modbus_bitwise(data)


def test_crc_of_empty_data():
    assert crc16_modbus([]) == 0xFFFF


# --------------------------------------------------------------------------
# Frame encoding - golden vectors
# --------------------------------------------------------------------------

# (id, command, payload) -> exact bytes on the wire.
# CRC is little-endian and covers id + command + payload.
# Cross-checked against the bitwise CRC above; the firmware's
# core/frame/{frame,crc16}.cpp is the ultimate oracle.
GOLDEN = [
    (0x01, Command.GET_BOARD_NAME, []),
    (0x01, Command.GET_FIRMWARE_VERSION, []),
    (0x02, Command.GET_STATUS_WORD, []),
    (0x03, Command.RESET, []),
    (0x04, Command.CWDT_SET_PERIOD, [0xE8, 0x03, 0x00, 0x00]),           # 1000 ms
    (0x05, Command.RESTORE_FACTORY_DEFAULTS, RESTORE_FACTORY_DEFAULTS_SIGNATURE),
    (0x06, Command.ENTER_BOOTLOADER, ENTER_BOOTLOADER_SIGNATURE),
    (0x07, Command.IRQ_SET_REG, [IrqRegister.DI_GLOBAL_ENABLE.value, 0x01, 0x00, 0x00, 0x00]),
    (0x08, Command.DI_GET_COUNTER, [0x03, CounterType.RISING.value]),
    (0x09, Command.DQ_SET_ALL_CHANNEL_STATES, [0x0F, 0x00, 0x00, 0x00]),
    (0x7F, Command.DQ_SET_CHANNEL_STATE, [0x02, 0x01]),
]


@pytest.mark.parametrize('id_, cmd, payload', GOLDEN)
def test_encode_layout_and_crc(id_, cmd, payload):
    encoded = Frame(id_, cmd, list(payload)).encode()
    body = [id_, cmd.value] + list(payload)
    crc = _crc16_modbus_bitwise(body)
    assert encoded == body + [crc & 0xFF, (crc >> 8) & 0xFF]
    assert len(encoded) == Frame.MIN_SIZE + len(payload)


@pytest.mark.parametrize('id_, cmd, payload', GOLDEN)
def test_encode_decode_round_trip(id_, cmd, payload):
    encoded = Frame(id_, cmd, list(payload)).encode()
    decoded = Frame(id_, cmd)
    decoded.decode(encoded)
    assert decoded.data == list(payload)


def test_command_accepts_raw_byte_value():
    assert Frame(1, 0x10).cmd is Command.GET_BOARD_NAME


def test_unknown_command_value_rejected():
    with pytest.raises(ValueError):
        Frame(1, 0xFE)


# --------------------------------------------------------------------------
# Frame decoding - failure modes
# --------------------------------------------------------------------------

@pytest.mark.parametrize('short', [[], [0x01], [0x01, 0x10], [0x01, 0x10, 0x00]])
def test_decode_short_response_raises_decode_exception(short):
    """R8/F1: a truncated read must be retryable, not an IndexError.

    The transport retries on DecodeException; an IndexError escapes the retry
    loop and turns a recoverable bus glitch into a crash.
    """
    frame = Frame(0x01, Command.GET_STATUS_WORD)
    with pytest.raises(DecodeException):
        frame.decode(short)


def test_decode_bad_crc():
    encoded = Frame(0x01, Command.GET_STATUS_WORD, [1, 2, 3, 4]).encode()
    encoded[-1] ^= 0xFF
    with pytest.raises(DecodeException):
        Frame(0x01, Command.GET_STATUS_WORD).decode(encoded)


def test_decode_unexpected_id():
    encoded = Frame(0x02, Command.GET_STATUS_WORD, [1, 2, 3, 4]).encode()
    with pytest.raises(DecodeException):
        Frame(0x01, Command.GET_STATUS_WORD).decode(encoded)


def test_decode_unexpected_command():
    encoded = Frame(0x01, Command.DI_GET_POLARITY, [1, 2, 3, 4]).encode()
    with pytest.raises(DecodeException):
        Frame(0x01, Command.DQ_GET_POLARITY).decode(encoded)


def test_decode_all_filler_bytes_fails_crc():
    """An unknown or rejected command answers 0xEE filler by design.

    The board still ACKs its address, so this arrives as a CRC failure rather
    than an OSError - which is how a host tells 'the board is there and said
    no' from 'the board is absent'.
    """
    frame = Frame(0x01, Command.GET_STATUS_WORD)
    with pytest.raises(DecodeException):
        frame.decode([0xEE] * 8)


def test_frame_default_payload_is_not_shared():
    """F2: a mutable default argument would leak payload between frames."""
    first = Frame(1, Command.RESET)
    first.data.append(0xAA)
    assert Frame(2, Command.RESET).data == []


def test_frame_id_mask_keeps_msb_clear():
    """The Raspberry Pi I2C peripheral corrupts the MSb of the first byte."""
    assert FRAME_ID_MASK == 0x7F
    for i in range(300):
        assert (i & FRAME_ID_MASK) <= 0x7F


# --------------------------------------------------------------------------
# Protocol constants
# --------------------------------------------------------------------------

def test_response_data_size_covers_every_command():
    missing = [c.name for c in Command if c not in RESPONSE_DATA_SIZE]
    assert missing == [], 'commands with no documented response size: %s' % missing


def test_commands_without_a_response_are_the_guarded_ones():
    silent = {c for c, size in RESPONSE_DATA_SIZE.items() if size is None}
    assert silent == {Command.RESET,
                      Command.RESTORE_FACTORY_DEFAULTS,
                      Command.ENTER_BOOTLOADER}


def test_command_values_are_unique():
    values = [c.value for c in Command]
    assert len(values) == len(set(values))


def test_reserved_opcodes_are_absent():
    """0x25-0x29 and 0x40-0x48 are allocated in firmware but unimplemented."""
    values = {c.value for c in Command}
    for opcode in list(range(0x25, 0x2A)) + list(range(0x40, 0x49)):
        assert opcode not in values


def test_status_word_bits():
    assert StatusWordBits.POR_RESET.value == 0x01
    assert StatusWordBits.SOFT_RESET.value == 0x02
    assert StatusWordBits.IWD_RESET.value == 0x04
    assert StatusWordBits.CWDT_TIMEOUT.value == 0x08
    assert StatusWordBits.DI_IRQ_CAPTURE_QUEUE_FULL.value == 0x10


def test_irq_registers():
    assert IrqRegister.DI_FALLING_EDGE_CONTROL.value == 0x20
    assert IrqRegister.DI_RISING_EDGE_CONTROL.value == 0x21
    assert IrqRegister.DI_CAPTURE.value == 0x22
    assert IrqRegister.DI_GLOBAL_ENABLE.value == 0x23


def test_counter_type_selectors():
    assert CounterType.FALLING.value == 0
    assert CounterType.RISING.value == 1


def test_cwdt_limits():
    assert CWDT_PERIOD_DISABLED == 0
    assert CWDT_PERIOD_MAX == 0xFFFFFFFF


def test_guard_signatures_are_ascii_payloads():
    assert RESTORE_FACTORY_DEFAULTS_SIGNATURE == [ord(c) for c in 'load']
    assert ENTER_BOOTLOADER_SIGNATURE == [ord(c) for c in 'boot']


# --------------------------------------------------------------------------
# Board capability data
# --------------------------------------------------------------------------

EXPECTED_CHANNELS = {
    'Di16':        {'di': 16},
    'Rly10':       {'dq': 10},
    'Di6Rly6':     {'di': 6, 'dq': 6},
    'DI16ac':      {'di': 16},
    'DQ16oc':      {'dq': 16},
    'DQ10rly':     {'dq': 10},
    'DQ8rly':      {'dq': 8},
    'DQ5rly':      {'dq': 5},
    'DI6acDQ6rly': {'di': 6, 'dq': 6},
    'DI6acDQ6ssr': {'di': 6, 'dq': 6},
    'DI6dwDQ6ssr': {'di': 6, 'dq': 6},
}

#: Only these four carry the IRQ module. A host must reject an
#: interrupt-driven configuration that names any other board.
IRQ_MODELS = {'DI16ac', 'DI6acDQ6rly', 'DI6acDQ6ssr', 'DI6dwDQ6ssr'}


def test_every_model_is_present():
    assert set(BOARDS) == set(EXPECTED_CHANNELS)


@pytest.mark.parametrize('model', sorted(EXPECTED_CHANNELS))
def test_channel_counts(model):
    info = BOARDS[model]
    assert {s: info.channel_count(s) for s in info.labels} == EXPECTED_CHANNELS[model]


@pytest.mark.parametrize('model', sorted(EXPECTED_CHANNELS))
def test_labels_are_unique_and_non_empty(model):
    for section, labels in BOARDS[model].labels.items():
        assert len(set(labels)) == len(labels)
        assert all(labels)


def test_irq_capability():
    assert {m for m, i in BOARDS.items() if i.has_irq} == IRQ_MODELS


def test_every_board_has_a_watchdog():
    assert all(info.has_cwdt for info in BOARDS.values())


def test_address_ranges_span_the_four_jumpers():
    for info in BOARDS.values():
        low, high = info.address_range
        assert low == info.base_address
        assert high - low == 0x0F
        assert 0 <= low <= 127 and 0 <= high <= 127


def test_reported_board_names_are_unique():
    names = [info.board_name for info in BOARDS.values()]
    assert len(names) == len(set(names))


def test_board_lookup_by_reported_name():
    assert board_info('DI16ac I2C-HAT') is BOARDS['DI16ac']
    assert board_info('nonexistent') is None


def test_board_info_is_immutable():
    info = BOARDS['DQ10rly']
    assert isinstance(info, BoardInfo)
    with pytest.raises(AttributeError):
        info.base_address = 0x60


def test_channel_count_of_absent_section_is_zero():
    assert BOARDS['DQ10rly'].channel_count('di') == 0


# --------------------------------------------------------------------------
# Import hygiene
# --------------------------------------------------------------------------

def test_protocol_imports_without_smbus2():
    """A host must be able to validate a configuration off-machine.

    Run in a subprocess with smbus2 blocked, because the transport modules
    may already be imported in this one.
    """
    code = (
        'import sys\n'
        'class Block:\n'
        '    def find_spec(self, name, path=None, target=None):\n'
        '        if name == "smbus2":\n'
        '            raise ImportError("smbus2 is blocked for this test")\n'
        '        return None\n'
        'sys.meta_path.insert(0, Block())\n'
        'import raspihats.protocol as p\n'
        'assert "smbus2" not in sys.modules\n'
        'assert p.BOARDS and p.Command.GET_BOARD_NAME.value == 0x10\n'
        # prove the blocker actually bites, so this test cannot pass vacuously
        'try:\n'
        '    import smbus2\n'
        'except ImportError:\n'
        '    pass\n'
        'else:\n'
        '    raise AssertionError("blocker inert - test proves nothing")\n'
        'print("ok")\n'
    )
    out = subprocess.check_output([sys.executable, '-c', code], text=True)
    assert out.strip() == 'ok'


def test_legacy_frame_module_still_re_exports():
    """Existing code importing the private module keeps working."""
    from raspihats.i2c_hats import _frame
    assert _frame.Command is Command
    assert _frame.Frame is Frame
    assert _frame.DecodeException is DecodeException


def test_legacy_aliases_point_at_the_public_enums():
    from raspihats.i2c_hats._base import Irq, StatusWord
    assert StatusWord.Bits is StatusWordBits
    assert Irq.RegName is IrqRegister


def test_status_word_bits_dict_keys_are_bare_member_names():
    """Caught on the bench: aliasing the enum changed these keys.

    ``StatusWord.bits`` used to build its keys by str()-ing the member and
    stripping a 'Bits.' prefix. Once Bits became an alias of StatusWordBits
    that produced 'StatusWordPOR_RESET' instead of 'POR_RESET' - a silent
    change to a dict that scripts index by name.
    """
    from raspihats.i2c_hats._base import StatusWord

    assert set(StatusWord(0).bits) == {b.name for b in StatusWordBits}
    assert StatusWord(0x09).bits == {
        'POR_RESET': True,
        'SOFT_RESET': False,
        'IWD_RESET': False,
        'CWDT_TIMEOUT': True,
        'DI_IRQ_CAPTURE_QUEUE_FULL': False,
    }
