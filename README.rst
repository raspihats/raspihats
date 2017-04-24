raspihats package
=================

This package provides the necessary code to interface the Raspberry Pi HATs(add-on boards) from raspihats.com_:

Typical usage often looks like this:

.. code-block:: python

    #!/usr/bin/env python
    # In this setup there are two I2C-HATs stacked, one DI16ac and one DQ10rly.
    from raspihats.i2c_hats import DI16ac, DQ10rly

    di16ac = DI16ac(0x40)   # 0x40 is the I2C bus address
    dq10rly = DQ10rly(0x50) # 0x50 is the I2C bus address

    while True:
        state = di16ac.di.channels[0]          # get digital input channel 0
        dq10rly.dq.channels[0] = state          # set digital output channel 0
        dq10rly.dq.channels[1] = not state      # set digital output channel 1

Listing attributes and methods(from v2.0.0)
-------------------------------------------

.. code-block:: python

    #!/usr/bin/env python
    from raspihats.i2c_hats import DI6acDQ6rly

    board = DI6acDQ6rly(0x60)     # 0x60 is the I2C bus address

    board.name                    # get board name, in this case 'DI6acDQ6rly'
    board.status                  # get status word
    board.reset()                 # reset board

    # cwdt - Communication WatchDog Timer
    board.cwdt.period             # get CommunicationWatchDogTimer(CWDT) period
    board.cwdt.period = 1         # set CWDT period, any value greather than 0 enables the CWDT
    board.cwdt.period = 0         # 0 disables the CWDT

    # di - Digital Inputs
    board.di.value                # get all digital input channel states, bit 0 represents channel 0 state and so on ..
    board.di.channels[0]          # get digital input channel 0 state, access using channel index
    board.di.channels['I0']       # get digital input channel 0 state, access using channel label
    board.di.r_counters[0]        # get digital input channel 0 raising edge counter
    board.di.r_counters['I0']     # get digital input channel 0 raising edge counter
    board.di.r_counters[0] = 0    # reset digital input channel 0 raising edge counter
    board.di.r_counters['I0'] = 0 # reset digital input channel 0 raising edge counter
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

Change Log
----------

v2.1.0
~~~~~~
  - Improved exception handling

v2.0.1
~~~~~~
  - Fixed I2C clock stretch timeout setup script

v2.0.0
~~~~~~
  - Attributes are now used for accessing board parameters, rather then methods
  - Added support for new boards:

    - DI16ac_ (replacement for Di16_)
    - DQ10rly_ (replacement for Rly10_)
    - DQ16oc_
    - DI6acDQ6rly_  (replacement for Di6Rly6_)

v1.1.1
~~~~~~
  - Added support for new boards:

    - Di16_
    - Rly10_
    - Di6Rly6_

.. code-block:: python

    #!/usr/bin/env python
    # In this setup there are two I2C-HATs stacked, one Di16 and one Rly10.
    from raspihats.i2c_hats import Di16, Rly10

    di16 = Di16(0x40)   # 0x40 is the I2C bus address
    rly10 = Rly10(0x50) # 0x50 is the I2C bus address
    # The I2C-HAT address high nibble is fixed(0x4 for Di16, 0x5 for Rly10), the low nibble
    # value is set using the on-board address jumper, range is [0x0 .. 0xF].

    while True:
        state = di16.di_get_channel_state('Di1.1')
        rly10.do_set_channel_state('Rly1', state)
        rly10.do_set_channel_state('Rly2', not state)


Installation
------------

Install dependencies
~~~~~~~~~~~~~~~~~~~~

The python-smbus package

.. code-block:: console

    $ sudo apt-get install python-smbus
    # or if using python 3
    $ sudo apt-get install python3-smbus


Install from repository
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    # Make sure you have git, pip and setuptools installed
    $ git clone git@github.com:raspihats/raspihats.git
    $ cd raspihats
    $ sudo python setup.py install
    # or if using python 3
    $ sudo python3 setup.py install


Install using pip
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    # Make sure you have pip and setuptools installed
    $ sudo pip install raspihats
    # or if using python 3
    $ sudo pip3 install raspihats


Checkout raspihats.com_

.. _raspihats.com:  http://www.raspihats.com
.. _Di16:           http://raspihats.com/product/di16/
.. _Rly10:          http://raspihats.com/product/rly10/
.. _Di6Rly6:        http://raspihats.com/product/di6rly6/
.. _DI16ac:         http://raspihats.com/product/di16ac/
.. _DQ10rly:        http://raspihats.com/product/dq10rly/
.. _DQ16oc:         http://raspihats.com/product/dq16oc/
.. _DI6acDQ6rly:    http://raspihats.com/product/di6acdq6rly/
