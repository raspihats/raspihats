"""
This module facilitates the raspihats.i2c_hats package integration with robotframework.
All the following functions will be loaded as keywords by robotframework.

Example:

*** Settings ***
Documentation       Test Suite using DI6acDQ6rly I2C-HAT.
Library             raspihats.i2c_hats.robot

*** Test Cases ***

Set Global Variables
    ${i2c_hat_temp}         New DI6acDQ6rly     ${0x60}
    Set Global Variable     ${i2c_hat}          ${i2c_hat_temp}

Board Name
    ${name}                     Get Name    ${i2c_hat}
    Should Be Equal As Strings  ${name}     DI6acDQ6rly I2C-HAT

Read Digital Input
    ${state}    DI Get Channel      ${i2c_hat}      ${0}
    Should Be Equal As Integers     ${state}        ${0}

"""
from . import Di16, Rly10, Di6Rly6, DI16ac, DQ10rly, DQ8rly, DQ16oc, DI6acDQ6rly, DI6acDQ6ssr, DI6dwDQ6ssr

irq_pin = None

def init_irq_pin(pin=21):
    """Initializes the IRQ pin as input with Pull UP enabled. The exported robotframework keyword is 'Init Irq Pin'.

        Args:
            pin (I2CHat): IRQ Pin
    """
    import RPi.GPIO as GPIO
    global irq_pin

    irq_pin = pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(irq_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_irq_pin_state():
    """Gets the IRQ pin state. The exported robotframework keyword is 'Get Irq Pin State'.

        Returns:
            bool: IRQ pin state
    """
    import RPi.GPIO as GPIO
    global irq_pin

    return GPIO.input(irq_pin)

def exit():
    """Clean Up. The exported robotframework keyword is 'Exit'."""
    import RPi.GPIO as GPIO
    GPIO.cleanup()

def new_Di16(adr):
    """New instance of class Di16. The exported robotframework keyword is 'New Di16'.

        Args:
            adr (int): i2c address

        Returns:
            Di16: A new instance of Di16
    """
    return Di16(adr)

def new_Rly10(adr):
    """New instance of class Rly10. The exported robotframework keyword is 'New Rly10'.

        Args:
            adr (int): i2c address

        Returns:
            Rly10: A new instance of Rly10
    """
    return Rly10(adr)

def new_Di6Rly6(adr):
    """New instance of class Di6Rly6. The exported robotframework keyword is 'New Di6Rly6'.

        Args:
            adr (int): i2c address

        Returns:
            Di6Rly6: A new instance of Di6Rly6
    """
    return Di6Rly6(adr)

def new_DI16ac(adr):
    """New instance of class DI16ac. The exported robotframework keyword is 'New DI16ac'.

        Args:
            adr (int): i2c address

        Returns:
            DI16ac: A new instance of DI16ac
    """
    return DI16ac(adr)

def new_DQ10rly(adr):
    """New instance of class DQ10rly. The exported robotframework keyword is 'New DQ10rly'.

        Args:
            adr (int): i2c address

        Returns:
            DQ10rly: A new instance of DQ10rly
    """
    return DQ10rly(adr)

def new_DQ8rly(adr):
    """New instance of class DQ8rly. The exported robotframework keyword is 'New DQ8rly'.

        Args:
            adr (int): i2c address

        Returns:
            DQ8rly: A new instance of DQ8rly
    """
    return DQ8rly(adr)

def new_DQ16oc(adr):
    """New instance of class DQ16oc. The exported robotframework keyword is 'New DQ16oc'.

        Args:
            adr (int): i2c address

        Returns:
            DQ16oc: A new instance of DQ16oc
    """
    return DQ16oc(adr)

def new_DI6acDQ6rly(adr):
    """New instance of class DI6acDQ6rly. The exported robotframework keyword is 'New DI6acDQ6rly'.

        Args:
            adr (int): i2c address

        Returns:
            DI6acDQ6rly: A new instance of DI6acDQ6rly
    """
    return DI6acDQ6rly(adr)

def new_DI6acDQ6ssr(adr):
    """New instance of class DI6acDQ6ssr. The exported robotframework keyword is 'New DI6acDQ6ssr'.

        Args:
            adr (int): i2c address

        Returns:
            DI6acDQ6ssr: A new instance of DI6acDQ6ssr
    """
    return DI6acDQ6ssr(adr)

def new_DI6dwDQ6ssr(adr):
    """New instance of class DI6dwDQ6ssr. The exported robotframework keyword is 'New DI6dwDQ6ssr'.

        Args:
            adr (int): i2c address

        Returns:
            DI6dwDQ6ssr: A new instance of DI6dwDQ6ssr
    """
    return DI6dwDQ6ssr(adr)

def get_name(i2c_hat):
    """Gets the I2C-HAT name. The exported robotframework keyword is 'Get Name'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            string: The name of the board
    """
    return i2c_hat.name

def get_firmware_version(i2c_hat):
    """Gets the I2C-HAT name. The exported robotframework keyword is 'Get Firmware Version'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            string: The firmware version
    """
    return i2c_hat.fw_version

def get_status(i2c_hat):
    """Gets the I2C-HAT status word. The exported robotframework keyword is 'Get Status'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            int: The status word
    """
    return i2c_hat.status.value

def reset(i2c_hat):
    """Resets the I2C-HAT. The exported robotframework keyword is 'Reset'."""
    i2c_hat.reset()

def cwdt_get_period(i2c_hat):
    """Gets the I2C-HAT CommunicationWatchdogTimer period. The exported robotframework keyword is 'CWDT Get Period'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            int: The CommunicationWatchdogTimer period
    """
    return i2c_hat.cwdt.period

def cwdt_set_period(i2c_hat, value):
    """Sets the I2C-HAT CommunicationWatchdogTimer period. The exported robotframework keyword is 'CWDT Set Period'.

        Args:
            i2c_hat (I2CHat): board
            value (int): period in seconds
    """
    i2c_hat.cwdt.period = value

def do_get_labels(i2c_hat):
    """Gets the I2C-HAT digital outputs labels. The exported robotframework keyword is 'DO Get Labels'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            list[sring]: The labels of the digital outputs
    """
    return i2c_hat.dq.labels

def do_get_power_on_value(i2c_hat):
    """Gets the I2C-HAT digital outputs power on value. The exported robotframework keyword is 'DO Get Power On Value'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            int: The power on value of the digital outputs
    """
    return i2c_hat.dq.power_on_value

def do_set_power_on_value(i2c_hat, value):
    """Sets the I2C-HAT digital outputs power on value. The exported robotframework keyword is 'DO Set Power On Value'.

        Args:
            i2c_hat (I2CHat): board
            value (int): desired power on value
    """
    i2c_hat.dq.power_on_value = value

def do_get_safety_value(i2c_hat):
    """Gets the I2C-HAT digital outputs safety value. The exported robotframework keyword is 'DO Get Safety Value'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            int: The safety value of the digital outputs
    """
    return i2c_hat.dq.safety_value

def do_set_safety_value(i2c_hat, value):
    """Sets the I2C-HAT digital outputs safety value. The exported robotframework keyword is 'DO Set Safety Value'.

        Args:
            i2c_hat (I2CHat): board
            value (int): desired safety value
    """
    i2c_hat.dq.safety_value = value

def do_get_value(i2c_hat):
    """Gets the I2C-HAT digital outputs value(all channels). The exported robotframework keyword is 'DO Get Value'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            int: The value(all channels) of the digital outputs
    """
    return i2c_hat.dq.value

def do_set_value(i2c_hat, value):
    """Sets the I2C-HAT digital outputs value(all channels). The exported robotframework keyword is 'DO Set Value'.

        Args:
            i2c_hat (I2CHat): board
            value (int): desired digital outputs value(all channels)
    """
    i2c_hat.dq.value = value

def do_get_channel(i2c_hat, index):
    """Gets the I2C-HAT digital output channel value. The exported robotframework keyword is 'DO Get Channel'.

        Args:
            i2c_hat (I2CHat): board
            index (int): channel index

        Returns:
            boolean: The value of the digital output channel
    """
    return i2c_hat.dq.channels[index]

def do_set_channel(i2c_hat, index, value):
    """Sets the I2C-HAT digital output channel value. The exported robotframework keyword is 'DO Set Channel'.

        Args:
            i2c_hat (I2CHat): board
            index (int): channel index
            value (boolean): desired digital output value

        Returns:
            boolean: The value of the digital output channel
    """
    i2c_hat.dq.channels[index] = value

def di_get_labels(i2c_hat):
    """Gets the I2C-HAT digital inputs labels. The exported robotframework keyword is 'DI Get Labels'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            list[sring]: The labels of the digital inputs
    """
    return i2c_hat.di.labels

def di_get_value(i2c_hat):
    """Gets the I2C-HAT digital inputs value(all channels). The exported robotframework keyword is 'DI Get Value'.

        Args:
            i2c_hat (I2CHat): board

        Returns:
            int: The value(all channels) of the digital inputs
    """
    return i2c_hat.di.value

def di_get_channel(i2c_hat, index):
    """Gets the I2C-HAT digital input channel value. The exported robotframework keyword is 'DI Get Channel'.

        Args:
            i2c_hat (I2CHat): board
            index (int): channel index

        Returns:
            boolean: The value of the digital input channel
    """
    return i2c_hat.di.channels[index]

def di_get_counter(i2c_hat, index, counter_type):
    """Gets the I2C-HAT digital input channel counter value. The exported robotframework keyword is 'DI Get Counter'.

        Args:
            i2c_hat (I2CHat): board
            index (int): channel index
            counter_type (int): type of counter(0 - falling edge, 1 - rising edge)

        Returns:
            int: The value of the digital input channel counter
    """
    if not (0 <= counter_type <= 1):
        raise ValueError("'" + str(counter_type) + "' is not a valid counter type, use: 0 - falling edge, 1 - rising edge")
    if counter_type == 0:
        value = i2c_hat.di.f_counters[index]
    else:
        value = i2c_hat.di.r_counters[index]
    return value

def di_reset_counter(i2c_hat, index, counter_type):
    """Resets the I2C-HAT digital input channel counter value. The exported robotframework keyword is 'DI Reset Counter'.

        Args:
            i2c_hat (I2CHat): board
            index (int): channel index
            counter_type (int): type of counter(0 - falling edge, 1 - rising edge)
    """
    if not (0 <= counter_type <= 1):
        raise ValueError("'" + str(counter_type) + "' is not a valid counter type, use: 0 - falling edge, 1 - rising edge")
    if counter_type == 0:
        i2c_hat.di.f_counters[index] = 0
    else:
        i2c_hat.di.r_counters[index] = 0

def di_reset_all_counters(i2c_hat):
    """Resets all the I2C-HAT digital input channel counter values. The exported robotframework keyword is 'DI Reset All Counters'.

        Args:
            i2c_hat (I2CHat): board
    """
    i2c_hat.di.reset_counters()

def di_get_irq_reg_rising_edge_control(i2c_hat):
    return i2c_hat.di.irq_reg.rising_edge_control

def di_set_irq_reg_rising_edge_control(i2c_hat, value):
    i2c_hat.di.irq_reg.rising_edge_control = value

def di_get_irq_reg_falling_edge_control(i2c_hat):
    return i2c_hat.di.irq_reg.falling_edge_control

def di_set_irq_reg_falling_edge_control(i2c_hat, value):
    i2c_hat.di.irq_reg.falling_edge_control = value

def di_get_irq_reg_capture(i2c_hat):
    return i2c_hat.di.irq_reg.capture

def di_set_irq_reg_capture(i2c_hat, value):
    i2c_hat.di.irq_reg.capture = value
