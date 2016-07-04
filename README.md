# raspihats package

This package provides the necessary code to interface the Raspberry Pi HATs(addon boards) from [**raspihats.com**](http://www.raspihats.com/).


Typical usage often looks like this:

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

## Note:

Every **I2CHat** object is practically a thread, this thread is used to feed the communication watchdog(CWDT). Failing to feed the CWDT will result in a CWDT timeout which depending on the I2CHat type can have different consequences.
By default the CWDT is disabled and the feed thread is not started, advanced users can enable both using the _cwdt_start_feed_thread()_.

## Installation:
### Install dependencies
The python-smbus package
```sh
$ sudo apt-get install python-smbus
# or if using python 3
$ sudo apt-get install python3-smbus
```

### Install from repository
```sh
$ git clone git@github.com:raspihats/raspihats.git
$ cd raspihats
$ sudo python setup.py install
# or if using python 3
$ sudo python3 setup.py install
```

### Install using pip
```sh
$ sudo pip install raspihats
# or if using python 3
$ sudo pip3 install raspihats
```

Checkout [**raspihats.com**](http://www.raspihats.com/)