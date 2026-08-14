The I2C-HAT wire protocol
=========================

:mod:`raspihats.protocol` is the single definition of the I2C-HAT frame
format, command set and protocol constants. It performs no I/O and imports
nothing that touches a bus, so it can be used to build a different transport
- an async daemon, a test harness, a non-Python client - or simply to
validate a configuration on a machine that has no boards attached.

.. code-block:: python

   from raspihats.protocol import Command, Frame, DecodeException, crc16_modbus

Stability commitment
--------------------

``raspihats.protocol`` is public API under semantic versioning:

* new commands, registers, board entries and constants may be **added** in a
  minor release;
* the frame layout, the CRC algorithm, and the value of any existing
  ``Command``, ``IrqRegister``, ``StatusWordBits`` or ``CounterType`` member
  will only change in a **major** release.

Anything reachable only as ``raspihats.i2c_hats._frame`` or
``raspihats.i2c_hats._base`` carries a leading underscore and gets no such
promise. ``_frame`` is kept as a compatibility re-export and will not gain
anything new; import from ``raspihats.protocol`` instead.

The firmware is the authority. ``REGISTER-MAP.md`` in the ``i2c-hat``
firmware repository carries the same map annotated with the firmware version
each command first appeared in, per board.

Frame layout
------------

Both directions use the same frame::

    [ Id | Command | Data ... | Crc lo | Crc hi ]
        1      1        n         1        1

* **Id** - differs from one request to the next; the board echoes it.
* **Command** - the opcode; the board echoes it.
* **Data** - payload, may be empty.
* **Crc** - CRC-16/MODBUS over Id + Command + Data, **little-endian**.

The smallest valid frame is therefore ``Frame.MIN_SIZE`` (4) bytes. Channel
data travels as unsigned 32-bit little-endian bitmasks, bit *N* being channel
*N*.

The transport contract
----------------------

Everything in this section is a requirement on *any* implementer, not a
convention of this package.

Frame ids
^^^^^^^^^

Ids increment per request and are masked with
:data:`~raspihats.protocol.FRAME_ID_MASK` (0x7F). This is not cosmetic: the
Raspberry Pi I2C peripheral has a bug affecting the most significant bit of
the first byte, so an id above 0x7F can come back corrupted and every
response will look like an id mismatch.

Request and response
^^^^^^^^^^^^^^^^^^^^

A transaction is two steps - a STOP-terminated write, then a read:

.. code-block:: python

   request = frame.encode()
   bus.write_i2c_block_data(address, request[0], request[1:])

   size = Frame.ID_SIZE + Frame.CMD_SIZE + RESPONSE_DATA_SIZE[cmd] + Frame.CRC_SIZE
   response = bus.read_i2c_block_data(address, 0xFF, size)

The frame's first byte becomes the SMBus "command" byte and the rest the
block. On the read, ``0xFF`` is a dummy byte the board ignores.

**The caller must know the response size before it reads**, which is why
:data:`~raspihats.protocol.RESPONSE_DATA_SIZE` is part of the public surface.
Over-reading returns 0xEE filler, which fails the CRC check by design.

Clock stretching is **required** - the boards stretch, up to a hard ceiling of
50 ms. The Raspberry Pi kernel aborts a transfer stretched beyond about 35 ms,
so a retry is always safe.

Echo semantics
^^^^^^^^^^^^^^

The board returns the request's id and command, and for several commands
echoes the request payload back. A mismatched echo means the write did not
take, and callers verify it. This is protocol behaviour, not a client
convention. One case is deliberately subtle: with a non-default write mask
(CiA 401 0x6208), a bulk output write echoes the value it *received*, so read
the output value back if you need the truth.

The status word is read-to-clear
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The status word is a **latched event register, cleared by reading it** - every
bit, ``CWDT_TIMEOUT`` included. Bench-verified across five firmware generations
on 2026-08-14, by watching a board go ``0x09`` (POR + CWDT) to ``0x08`` to
``0x00`` over successive reads once its watchdog was disabled.

``CWDT_TIMEOUT`` can look sticky, but only because an unfed watchdog re-trips
and sets it again between reads. Disable the watchdog and it clears like the
rest.

The consequence is what matters: the status word is **consumed** by whoever
reads it first. If a daemon polls it for diagnostics, a user script that also
reads it sees zeros and concludes the board never reset - and vice versa. One
reader per board, and it should cache what it saw.

Retry policy
^^^^^^^^^^^^

Retryable: ``IOError`` and
:class:`~raspihats.protocol.DecodeException`. This package retries 5 times,
10 ms apart.

Distinguishing the two failures is worth doing in a diagnostic layer:

* an **absent** board does not ACK its address, so the transfer fails with an
  ``OSError``;
* a board that **rejects** a request still ACKs, and the read returns 0xEE
  filler for every byte - so it arrives as a CRC failure. A response of all
  0xEE means "the board is there and said no", which is also how an
  unimplemented command answers.

.. note::

   The 0xEE filler is a property of **current** firmware. Bench-verified on
   2026-08-14: a DQ10rly on v2.1.0 answers an unimplemented command with clean
   0xEE, but the same board family on v1.1.3 returns *arbitrary* bytes
   (``af 50 8a f5 37 aa 99 bb``). Both fail the CRC check, which is what makes
   them safe - but only the newer one is identifiable as a deliberate refusal.

   So treat "all 0xEE" as a *hint* for diagnostics, never as the test for
   whether a command is supported. The test is the CRC failure itself.

``Frame.decode`` raises ``DecodeException`` - never ``IndexError`` - on a
short read, so a truncated response is retried like any other bad frame.

Response sizes
--------------

Payload sizes only; add ``Frame.ID_SIZE + Frame.CMD_SIZE + Frame.CRC_SIZE``
(4 bytes) for the read length. ``-`` means the board sends no response at all.

========================  ======  ========  =========================================
Command                   Opcode  Response  Notes
========================  ======  ========  =========================================
GET_BOARD_NAME            0x10    25        NUL-padded ASCII
GET_FIRMWARE_VERSION      0x11    3         major, minor, patch as integers
GET_STATUS_WORD           0x12    4         **read-to-clear** - see below
RESET                     0x13    \-        software reset
CWDT_SET_PERIOD           0x14    4         u32 ms, 0 disables, persistent
CWDT_GET_PERIOD           0x15    4
IRQ_GET_REG               0x16    5         ``[reg]`` -> ``[reg, u32]``
IRQ_SET_REG               0x17    5         ``[reg, u32]``, echoed
RESTORE_FACTORY_DEFAULTS  0x18    \-        payload must be ``b'load'``; ~1 s to erase
ENTER_BOOTLOADER          0x19    \-        payload must be ``b'boot'``
CONFIG_SET_SIGNATURE      0x1A    4
CONFIG_GET_SIGNATURE      0x1B    4
DI_GET_ALL_CHANNEL_STATES 0x20    4         bitmask
DI_GET_CHANNEL_STATE      0x21    2         ``[index]`` -> ``[index, state]``
DI_GET_COUNTER            0x22    6         ``[index, type]`` -> ``[index, type, u32]``
DI_RESET_COUNTER          0x23    2
DI_RESET_ALL_COUNTERS     0x24    0
DI_SET_CHANNEL_FILTER     0x2A    5         ``[index, u32 ms]``, echoed
DI_GET_CHANNEL_FILTER     0x2B    5
DI_SET_POLARITY           0x2C    4         echoed
DI_GET_POLARITY           0x2D    4
DQ_SET_POWER_ON_VALUE     0x30    4         echoed
DQ_GET_POWER_ON_VALUE     0x31    4
DQ_SET_SAFETY_VALUE       0x32    4         echoed
DQ_GET_SAFETY_VALUE       0x33    4
DQ_SET_ALL_CHANNEL_STATES 0x34    4         gated by the write mask
DQ_GET_ALL_CHANNEL_STATES 0x35    4
DQ_SET_CHANNEL_STATE      0x36    2         bypasses the write mask
DQ_GET_CHANNEL_STATE      0x37    2
DQ_SET_POLARITY           0x38    4         echoed
DQ_GET_POLARITY           0x39    4
DQ_SET_SAFETY_MASK        0x3A    4         echoed
DQ_GET_SAFETY_MASK        0x3B    4
DQ_SET_WRITE_MASK         0x3C    4         volatile, echoed
DQ_GET_WRITE_MASK         0x3D    4
========================  ======  ========  =========================================

Opcodes 0x25-0x29 (counter status, encoders) and 0x40-0x48 (analog) are
allocated in the firmware's ``commands.h`` but implemented by no released
board. They are absent from ``Command`` on purpose - a board answers them
with 0xEE filler. Absent means no claim.

Fault response
--------------

The property this protocol exists to guarantee: **when the host stops
talking, outputs go to a known state, enforced by the board.**

Set the watchdog period (``CWDT_SET_PERIOD``, u32 ms, persistent) and the
safety value (``DQ_SET_SAFETY_VALUE``, persistent). Any valid frame feeds the
watchdog. On timeout the board applies::

    outputs = (value & ~safety_mask) | (safety_value & safety_mask)

``DQ_SET_SAFETY_MASK`` (CiA 401 0x6206, persistent, default all-ones) is
per-channel: a set bit loads the safety value, a **clear bit holds the
channel's last state**. Both behaviours are available per channel. The status
word's ``CWDT_TIMEOUT`` bit records that a trip happened, and from firmware
3.0.0 a trip also disarms the IRQ block.

The IRQ block
-------------

Present on four models only - ``DI16ac``, ``DI6acDQ6rly``, ``DI6acDQ6ssr``
and ``DI6dwDQ6ssr``. Check
:attr:`~raspihats.protocol.BoardInfo.has_irq` rather than assuming.

Sub-registers are reached through ``IRQ_GET_REG`` / ``IRQ_SET_REG``:

* ``DI_RISING_EDGE_CONTROL`` (0x21, CiA 401 0x6007) and
  ``DI_FALLING_EDGE_CONTROL`` (0x20, CiA 401 0x6008), one bit per channel.
  **Volatile below firmware 3.0.0, EEPROM-persistent from 3.0.0.**
* ``DI_CAPTURE`` (0x22) reads one queue entry as
  ``(states << 16) | edge_status``; 0 means empty and a real entry is never 0.
  Writing 0 clears the queue and is the only value a write accepts. Depth is
  128; on overflow the oldest is dumped and
  ``StatusWordBits.DI_IRQ_CAPTURE_QUEUE_FULL`` is set, so a periodic resync is
  a safety net rather than belt-and-braces.
* ``DI_GLOBAL_ENABLE`` (0x23, CiA 401 0x6005) exists **only from firmware
  3.0.0**.

.. warning::

   Firmware 3.0.0 is a breaking change for interrupt-driven hosts. Edges are
   captured **only while** ``DI_GLOBAL_ENABLE`` is 1. It is volatile, reads 0
   after every reset, and a CWDT trip clears it. A host that sets the edge
   masks and never arms it will see nothing at all.

   Arm it **last**, after the masks are in place, and re-arm after a watchdog
   trip. On firmware older than 3.0.0 this sub-register answers 0xEE filler,
   which is how a host can detect which generation it is talking to.

The interrupt line is active-low and open-drain, wired-OR across stacked
boards, with a pull-up on the Pi side. Treat it as a **level**, not an edge:
check it before sleeping, and drain every armed board on wake. From firmware
3.0.0 the line is asserted if and only if the block is armed and the queue is
non-empty; below 3.0.0 a ``DI_GET_ALL_CHANNEL_STATES`` read also released it,
which could strand queued captures.

Board capability data
---------------------

:data:`~raspihats.protocol.BOARDS` maps a model name to a
:class:`~raspihats.protocol.BoardInfo`: reported board name, base address,
per-section channel labels, and whether the model has the watchdog and the
IRQ module. It is inert data - no bus, no I/O - which is what makes it usable
for validating a configuration before any hardware is opened.

.. code-block:: python

   from raspihats.protocol import BOARDS, board_info

   info = BOARDS['DI6acDQ6rly']
   info.address_range        # (0x60, 0x6F)
   info.channel_count('dq')  # 6
   info.has_irq              # True

   board_info('DI16ac I2C-HAT')  # look up by the name the board reports

The board classes in :mod:`raspihats.i2c_hats` take their address, reported
name and channel labels from this table, so the two cannot disagree.

API reference
-------------

.. automodule:: raspihats.protocol
   :members:
   :undoc-members:
   :show-inheritance:
