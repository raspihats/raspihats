#!/usr/bin/env python3
"""Hardware smoke test for the raspihats package, run on the Pi bench.

Not collected by pytest on purpose - it needs real boards on a real bus.

The 3.2.0 changes are a refactor plus defect fixes, so what needs proving on
hardware is that the transport path still behaves identically against real
firmware, and that the new inert board table agrees with what the boards
themselves report. Both are read-only questions, which is why this runs
read-only by default.

Usage::

    python3 tests/bench_smoke.py                 # read-only, safe on any bus
    python3 tests/bench_smoke.py --scan 0x40-0x6f
    python3 tests/bench_smoke.py --write         # adds a volatile write round-trip

``--write`` exercises exactly one register, ``dq.write_mask`` (CiA 401
0x6208), which is volatile and restored to its previous value immediately.
It never changes an output state, never writes EEPROM, and is skipped on
firmware that does not implement it.

Nothing here ever writes to a relay, a persistent register, or the
configuration signature.
"""
import argparse
import sys

sys.path.insert(0, __file__.rsplit('/tests/', 1)[0])

import raspihats
from raspihats import protocol
from raspihats.i2c_hats import I2CHat, ResponseException
import raspihats.i2c_hats as boards


GREEN, RED, YELLOW, DIM, RESET = '\033[32m', '\033[31m', '\033[33m', '\033[2m', '\033[0m'

results = {'pass': 0, 'fail': 0, 'skip': 0}


def check(label, fn):
    """Run one read, print the value, record pass/fail/skip."""
    try:
        value = fn()
    except ResponseException as ex:
        # A board that does not implement a command answers 0xEE filler,
        # which surfaces as a CRC failure - that is "not supported", not a bug.
        results['skip'] += 1
        print('  %s- %-22s not supported (%s)%s' % (DIM, label, ex, RESET))
        return None
    except Exception as ex:
        results['fail'] += 1
        print('  %sX %-22s %s: %s%s' % (RED, label, type(ex).__name__, ex, RESET))
        return None
    results['pass'] += 1
    print('  %s+%s %-22s %s' % (GREEN, RESET, label, value))
    return value


def assert_equal(label, actual, expected):
    if actual == expected:
        results['pass'] += 1
        print('  %s+%s %-22s %s' % (GREEN, RESET, label, actual))
    else:
        results['fail'] += 1
        print('  %sX %-22s %r != expected %r%s' % (RED, label, actual, expected, RESET))


def discover(low, high):
    """Return [(address, board_name)] for every I2C-HAT that answers."""
    found = []
    for address in range(low, high + 1):
        try:
            name = I2CHat(address).name
        except Exception:
            continue
        if name:
            found.append((address, name))
    return found


def exercise(address, board_name, allow_write):
    info = protocol.board_info(board_name)
    print('\n%s0x%02X  %s%s' % ('\033[1m', address, board_name, RESET))

    if info is None:
        results['fail'] += 1
        print('  %sX unknown board - not in protocol.BOARDS%s' % (RED, RESET))
        return

    cls = getattr(boards, info.name, None)
    if cls is None:
        results['fail'] += 1
        print('  %sX no class named %s in raspihats.i2c_hats%s' % (RED, info.name, RESET))
        return

    # R4 against hardware: the inert table must agree with the real board.
    low, high = info.address_range
    assert_equal('address in range', low <= address <= high, True)

    board = cls(address)
    assert_equal('reported name', board.name, info.board_name)

    # F4: version components above 9 must render as numbers, not punctuation.
    version = check('fw_version', lambda: board.fw_version)
    if version is not None:
        parts = version.lstrip('v').split('.')
        assert_equal('version is numeric', all(p.isdigit() for p in parts), True)

    # NOTE: reading the status word clears its CWDT_TIMEOUT bit.
    status = check('status word', lambda: board.status)
    if status is not None:
        check('status bits', lambda: status.bits)

    check('cwdt period (s)', lambda: board.cwdt.period)
    check('config_signature', lambda: hex(board.config_signature))

    if 'di' in info.labels:
        assert_equal('di channel count', len(board.di.channels), info.channel_count('di'))
        assert_equal('di labels', list(board.di.labels), list(info.labels['di']))
        check('di value', lambda: hex(board.di.value))
        check('di polarity', lambda: hex(board.di.polarity))
        check('di filter[0] ms', lambda: board.di.filters[0])
        # CounterType is new in 3.2.0 - prove both selectors still read.
        check('di r_counter[0]', lambda: board.di.r_counters[0])
        check('di f_counter[0]', lambda: board.di.f_counters[0])
        check('di channel[0]', lambda: board.di.channels[0])

    if info.has_irq:
        check('irq rising mask', lambda: hex(board.di.irq_reg.rising_edge_control))
        check('irq falling mask', lambda: hex(board.di.irq_reg.falling_edge_control))
        # Volatile from firmware 3.0.0; 0 here on an unarmed board is correct.
        check('irq global_enable', lambda: board.di.irq_reg.global_enable)
    elif 'di' in info.labels:
        print('  %s- irq module             absent on this model%s' % (DIM, RESET))

    if 'dq' in info.labels:
        assert_equal('dq channel count', len(board.dq.channels), info.channel_count('dq'))
        assert_equal('dq labels', list(board.dq.labels), list(info.labels['dq']))
        check('dq value', lambda: hex(board.dq.value))
        check('dq power_on_value', lambda: hex(board.dq.power_on_value))
        check('dq safety_value', lambda: hex(board.dq.safety_value))
        check('dq safety_mask', lambda: hex(board.dq.safety_mask))
        check('dq polarity', lambda: hex(board.dq.polarity))
        mask = check('dq write_mask', lambda: hex(board.dq.write_mask))

        if allow_write and mask is not None:
            round_trip_write_mask(board, info)


def round_trip_write_mask(board, info):
    """Write, read back and restore the volatile write mask.

    Chosen because it is the only register that is both writable and
    volatile: it resets to all-ones on its own, and it gates bulk writes
    without changing any output state.
    """
    original = board.dq.write_mask
    probe = ((1 << info.channel_count('dq')) - 1) ^ 0x01   # clear channel 0 only
    try:
        board.dq.write_mask = probe
        read_back = board.dq.write_mask
        assert_equal('write_mask round-trip', hex(read_back), hex(probe))
    finally:
        board.dq.write_mask = original
        assert_equal('write_mask restored', hex(board.dq.write_mask), hex(original))


def parse_range(text):
    low, _, high = text.partition('-')
    return int(low, 0), int(high or low, 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--scan', default='0x40-0x6f', metavar='LOW-HIGH',
                        help='I2C address range to probe (default: 0x40-0x6f)')
    parser.add_argument('--write', action='store_true',
                        help='also round-trip the volatile dq.write_mask register')
    args = parser.parse_args()

    # NOTE: __version__ comes from the *installed distribution* metadata, which
    # is not necessarily the code being imported - running from PYTHONPATH over
    # an older install makes them disagree. Print the path so the log is never
    # ambiguous about what was actually exercised.
    print('raspihats %s  |  %s' % (raspihats.__version__, raspihats.__file__))
    print('protocol.BOARDS: %d models, %d with IRQ'
          % (len(protocol.BOARDS),
             sum(1 for i in protocol.BOARDS.values() if i.has_irq)))

    low, high = parse_range(args.scan)
    print('scanning 0x%02X-0x%02X ...' % (low, high))
    found = discover(low, high)

    if not found:
        print('%sno boards answered - check the bus and the wiring%s' % (RED, RESET))
        return 1

    print('found %d board(s): %s' % (len(found),
                                     ', '.join('0x%02X %s' % (a, n) for a, n in found)))
    if args.write:
        print('%swrite mode: dq.write_mask will be written and restored%s' % (YELLOW, RESET))

    for address, board_name in found:
        exercise(address, board_name, args.write)

    print('\n%d passed, %d failed, %d not supported'
          % (results['pass'], results['fail'], results['skip']))
    return 1 if results['fail'] else 0


if __name__ == '__main__':
    sys.exit(main())
