# raspihats package

This python package provides the necessary code to interface the Raspberry Pi add-on boards from [raspihats.com][raspihats]:

Typical usage often looks like this:

```
#!/usr/bin/env python
# In this setup there are two I2C-HATs stacked, one DI16ac and one DQ10rly.
from raspihats.i2c_hats import DI16ac, DQ10rly

di16ac = DI16ac(0x40)   # 0x40 is the I2C bus address
dq10rly = DQ10rly(0x50) # 0x50 is the I2C bus address

while True:
    state = di16ac.di.channels[0]           # get digital input channel 0
    dq10rly.dq.channels[0] = state          # set digital output channel 0
    dq10rly.dq.channels[1] = not state      # set digital output channel 1
```
## IRQ feature(from library v2.3.0)

> Starting from hardware revision 2.0, DI16ac I2C-HAT and DI6acDQ6rly I2C-HAT can trigger an IRQ line that's connected to GPIO21 of the Raspberry Pi.

> Firmware 3.0.0 completed the block along CiA 401: the edge masks (0x6007/0x6008) persist in the board's EEPROM, and the volatile global enable (0x6005) gates capture — arm it after every board reset, write 0 to disarm in one transaction (capture queue dumped, IRQ line released, masks untouched). A communication-watchdog timeout disarms the block the same way, so a dead controller is never held on the line.

### Firmware 3.0.0 and newer

The IRQ line is a level — low exactly while captures pend — so a single-threaded loop with no callbacks or queues is all a host needs:

```
import RPi.GPIO as GPIO
from raspihats.i2c_hats import DI6acDQ6rly

IRQ_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

board = DI6acDQ6rly(0x60)   # 0x60 is the I2C bus address
print(str(board.name) + ' ' + str(board.fw_version))
print('Use Ctrl+C to stop program.')

# commission once - the edge masks persist in the board's EEPROM
board.di.irq_reg.rising_edge_control = 0x3F     # rising edges, all 6 channels
board.di.irq_reg.falling_edge_control = 0x3F    # falling edges, all 6 channels

# arm - the global enable is volatile, a board reset always starts disarmed
board.di.irq_reg.capture = 0
board.di.irq_reg.global_enable = 1

try:
    while True:
        # the IRQ line is a level: low exactly while captures pend. Wait for
        # a falling edge only while it is high; the timeout re-checks the
        # level (and keeps Ctrl+C responsive), so a capture stored while the
        # line was already low is never missed.
        if GPIO.input(IRQ_PIN):
            GPIO.wait_for_edge(IRQ_PIN, GPIO.FALLING, timeout=200)
            continue
        # line is low: read one capture - (states << 16) | edge_status, 0
        # means empty - the board releases the line once the queue is drained
        capture = board.di.irq_reg.capture
        if capture == 0:
            continue
        status = capture & 0xFFFF
        states = capture >> 16
        for channel in range(len(board.di.channels)):
            if status & (0x01 << channel):
                print('IRQ on channel: %d, state: %d' % (channel, (states >> channel) & 0x01))
except KeyboardInterrupt:
    pass
finally:
    # one write disarms: queue dumped, line released, masks keep the commissioning
    board.di.irq_reg.global_enable = 0
    GPIO.cleanup()
```

### Older firmware (before 3.0.0)

On older firmware there is no global enable — the block is live as soon as an edge mask is non-zero — and the masks are volatile, so arm them at every start. Disarm by zeroing the masks **and** clearing the capture queue: leftover captures keep the IRQ line asserted. The level check on the queue timeout is essential here too — a capture stored while the line is already low makes no new falling edge, so an edge-only sleep can strand events forever:

```
import queue
import RPi.GPIO as GPIO
from raspihats.i2c_hats import DI6acDQ6rly

IRQ_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# the ISR just hands the event to the main thread
event_queue = queue.Queue(maxsize = 20)
GPIO.add_event_detect(IRQ_PIN, GPIO.FALLING, callback=event_queue.put)

board = DI6acDQ6rly(0x60)   # 0x60 is the I2C bus address
print(str(board.name) + ' ' + str(board.fw_version))
print('Use Ctrl+C to stop program.')

# volatile on this firmware: arm the masks at every start
board.di.irq_reg.rising_edge_control = 0x3F     # rising edges, all 6 channels
board.di.irq_reg.falling_edge_control = 0x3F    # falling edges, all 6 channels
board.di.irq_reg.capture = 0

try:
    while True:
        try:
            # the timeout keeps Ctrl+C responsive and doubles as a line check
            event_queue.get(block=True, timeout=0.2)
        except queue.Empty:
            # captures stored while the line was already low make no new
            # falling edge - look at the level on every timeout
            if GPIO.input(IRQ_PIN):
                continue
        # drain the capture queue; each entry is (states << 16) | edge_status,
        # 0 means empty - the board releases the line once drained
        while True:
            capture = board.di.irq_reg.capture
            if capture == 0:
                break
            status = capture & 0xFFFF
            states = capture >> 16
            for channel in range(len(board.di.channels)):
                if status & (0x01 << channel):
                    print('IRQ on channel: %d, state: %d' % (channel, (states >> channel) & 0x01))
except KeyboardInterrupt:
    pass
finally:
    # no global enable on this firmware: disarm by zeroing the masks, then
    # clear the queue - leftover captures would keep the IRQ line asserted
    board.di.irq_reg.rising_edge_control = 0
    board.di.irq_reg.falling_edge_control = 0
    board.di.irq_reg.capture = 0
    GPIO.remove_event_detect(IRQ_PIN)
    GPIO.cleanup()
```

## Listing attributes and methods(from v2.0.0)

```
from raspihats.i2c_hats import DI6acDQ6rly

board = DI6acDQ6rly(0x60)     # 0x60 is the I2C bus address

board.name                    # get board name, in this case 'DI6acDQ6rly'
board.status.value            # get status word
board.reset()                 # reset board
board.restore_factory_defaults()  # restore factory defaults (CiA 301 0x1011): formats the EEPROM and resets, every persistent register falls back to its default

# cwdt - Communication WatchDog Timer
board.cwdt.period             # get CommunicationWatchDogTimer(CWDT) period
board.cwdt.period = 1         # set CWDT period, any value greather than 0 enables the CWDT
board.cwdt.period = 0         # 0 disables the CWDT

# di - Digital Inputs
board.di.value                # get all digital input channel states, bit 0 represents channel 0 state and so on ..
board.di.channels[0]          # get digital input channel 0 state, access using channel index
board.di.channels['I0']       # get digital input channel 0 state, access using channel label
board.di.r_counters[0]        # get digital input channel 0 rising edge counter
board.di.r_counters['I0']     # get digital input channel 0 rising edge counter
board.di.r_counters[0] = 0    # reset digital input channel 0 rising edge counter
board.di.r_counters['I0'] = 0 # reset digital input channel 0 rising edge counter
board.di.f_counters[0]        # get digital input channel 0 falling edge counter
board.di.f_counters['I0']     # get digital input channel 0 falling edge counter
board.di.f_counters[0] = 0    # reset digital input channel 0 falling edge counter
board.di.f_counters['I0'] = 0 # reset digital input channel 0 falling edge counter
board.di.reset_counters()     # reset all counters(rising and falling edge) for all channels
board.di.labels               # get digital input labels
# Polarity (CiA 401 0x6002) -- per-bit invert applied before the filter, persistent
board.di.polarity             # get digital input polarity, bit 0 represents channel 0 and so on ..
board.di.polarity = 0x01      # set digital input polarity, channel 0 inverted
# Filters (CiA 401 0x6003) -- per-channel filter time in milliseconds, persistent
board.di.filters[0]           # get digital input channel 0 filter time in ms
board.di.filters[0] = 2       # set digital input channel 0 filter time in ms, 1..65535
# IRQ block (firmware >= 3.0.0) -- see the IRQ feature section above
board.di.irq_reg.rising_edge_control     # get/set rising edge mask (CiA 401 0x6007), persistent
board.di.irq_reg.falling_edge_control    # get/set falling edge mask (CiA 401 0x6008), persistent
board.di.irq_reg.capture                 # read one capture entry, 0 = queue empty; write 0 to clear the queue
board.di.irq_reg.global_enable           # volatile arming bit (CiA 401 0x6005), 0 after reset; write 0 to disarm

# dq - Digital Outputs
board.dq.value                # get all digital output channel states, bit 0 represents channel 0 and so on ..
board.dq.value = 0            # set all digital output channel states
board.dq.channels[0]          # get digital output channel 0 state, access using channel index
board.dq.channels[0] = 0      # set digital output channel 0 state
board.dq.channels['Q0']       # get digital output channel 0 state, access using channel label
board.dq.channels['Q0'] = 0   # set digital output channel 0 state
# PowerOnValue -- loaded to Digital Outputs at board power on
board.dq.power_on_value       # get digital output channels PowerOnValue, bit 0 represents channel 0 and so on ..
board.dq.power_on_value = 0   # set digital output channels PowerOnValue
# SafetyValue -- loaded to Digital Outputs at CWDT timeout
board.dq.safety_value         # get digital output channels SafetyValue, bit 0 represents channel 0 and so on ..
board.dq.safety_value = 0     # set digital output channels SafetyValue
# SafetyMask (CiA 401 0x6206) -- per bit: 1 = load the SafetyValue at CWDT timeout, 0 = hold last state, persistent
board.dq.safety_mask          # get digital output channels SafetyMask
board.dq.safety_mask = 0x3F   # set digital output channels SafetyMask, all channels apply the SafetyValue
# Polarity (CiA 401 0x6202) -- per-bit invert applied at the pin, the bus value stays logical, persistent
board.dq.polarity             # get digital output polarity, bit 0 represents channel 0 and so on ..
board.dq.polarity = 0         # set digital output polarity, careful: writing this flips live pins instantly
board.dq.labels               # get digital output labels
```

## Change Log

### v2.5.0
  - Added support for new board, DQ5rly I2C-HAT

### v2.4.0
  - Switched to smbus2 to communicate over I2C
  - Removed I2C clock stretching timeout script, RaspberryPi OS sets by default an acceptable value for the I2C clock stretching timeout.
  - Added support for new boards: 
    - DI6acDQ6ssr I2C-HAT
    - DI6dwDQ6ssr I2C-HAT

### v2.3.0
  - Added IRQ support

### v2.2.3
  - enum34 is loaded for python<3.4
  - Setup script warning if it's not run with sudo(used to setup I2C ClockStretchTimeout)

### v2.2.2
  - Bug fix in setup script, BCM2835 platform hardware is now recognized.
  - Bug fix in robotframework interface, status.value is now returned by get_status()


### v2.2.1
  - Added StatusWord class. To get raw int value use board.status.value, to get beautiful string representation use str(board.status).

### v2.1.1
  - String representation of I2CHat object doesn't use an I2C bus transfer any more.
  - Improved exception messages

#### v2.1.0
  - Improved exception handling

### v2.0.1
  - Fixed I2C clock stretch timeout setup script

### v2.0.0
  - Attributes are now used for accessing board parameters, rather then methods
  - Added support for new boards:
    - [DI16ac I2C-HAT][di16ac-i2c-hat] (replacement for Di16 I2C-HAT)
    - [DQ10rly I2C-HAT][dq10rly-i2c-hat] (replacement for Rly10 I2C-HAT)
    - [DQ16oc I2C-HAT][dq16oc-i2c-hat]
    - [DI6acDQ6rly I2C-HAT][di6acdq6rly-i2c-hat] (replacement for Di6Rly6 I2C-HAT)

### v1.1.1
  - Added support for new boards:
    - Di16
    - Rly10
    - Di6Rly6

## Installation

```
$ pip install raspihats
```

Checkout [raspihats.com][raspihats]!

[raspihats]:                        https://raspihats.com
[di16ac-i2c-hat]:                   https://raspihats.com/shop/di16ac-i2c-hat/
[dq10rly-i2c-hat]:                  https://raspihats.com/shop/dq10rly-i2c-hat/
[dq16oc-i2c-hat]:                    https://raspihats.com/shop/dq16oc-i2c-hat/
[di6acdq6rly-i2c-hat]:              https://raspihats.com/shop/di6acdq6rly-i2c-hat/
