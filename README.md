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
## IRQ feature(from v2.3.0)

> Starting from hardware revision 2.0, DI16ac I2C-HAT and DI6acDQ6rly I2C-HAT can trigger an IRQ line that's connected to GPIO21 of the Raspberry Pi.

```
try:
    import Queue as queue
except ImportError:
    import queue
from time import sleep
import RPi.GPIO as GPIO
from raspihats.i2c_hats import DI16ac, DI6acDQ6rly

IRQ_PIN = 21
GPIO.setmode(GPIO.BCM)

# IRQ pin setup as input with pull-up enabled
GPIO.setup(IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# this queue is used to safely exchange information between threads
event_queue = queue.Queue(maxsize = 20)

def isr(pin):
    event_queue.put(pin)

GPIO.add_event_detect(IRQ_PIN, GPIO.FALLING, callback=isr)

# b = DI16ac(0x40)        # 0x40 is the I2C bus address
b = DI6acDQ6rly(0x60)   # 0x60 is the I2C bus address

print(str(b.name) + ' ' + str(b.fw_version))
print('Use Ctrl+C to stop program.')

# enable rising edge IRQs for Digital Input channels 0 and 2
b.di.irq_reg.rising_edge_control = 0x05

# enable falling edge IRQs for Digital Input channels 1 and 2
b.di.irq_reg.falling_edge_control = 0x06

# dump DigitalInputs IRQ CaptureQueue contents and release IRQ line by
# writing 0 to DigitalInputs IRQ Capture Register
b.di.irq_reg.capture = 0

while True:
    try:
        # wait until there is something in the queue, timeout is here because a
        # queue.get without a timeout can't be interrupted with a KeyboardInterrupt
        pin = event_queue.get(block=True, timeout=0.2)
        if pin == IRQ_PIN:
            # read the DigitalInputs IRQ Capture Register(to read the values
            # stored in the DigitalInputs IRQ CaptureQueue) until the
            # returned value is 0, this means DigitalInputs IRQ CaptureQueue
            # is empty and the IRQ line is released
            while True:
                capture = b.di.irq_reg.capture
                if capture == 0:
                    break
                status = capture & 0xFFFF
                states = (capture >> 16) & 0xFFFF
                for channel in range(0, 16):
                    mask = 0x01 << channel
                    if (status & mask) > 0:
                        print('IRQ detected on channel: %d, state: %d' %(channel, (states & mask) >> channel))
    except queue.Empty:
        pass

    except KeyboardInterrupt:
        # disable rising edge IRQs for Digital Input channels
        b.di.irq_reg.rising_edge_control = 0

        # disable falling edge IRQs for Digital Input channels
        b.di.irq_reg.falling_edge_control = 0

        GPIO.remove_event_detect(IRQ_PIN)
        GPIO.cleanup()

        break
```

## Listing attributes and methods(from v2.0.0)

```
from raspihats.i2c_hats import DI6acDQ6rly

board = DI6acDQ6rly(0x60)     # 0x60 is the I2C bus address

board.name                    # get board name, in this case 'DI6acDQ6rly'
board.status.value            # get status word
board.reset()                 # reset board

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
board.dq.labels               # get digital output labels
```

## Change Log

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
