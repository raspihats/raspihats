from .i2c_hats import Di16, Di6Rly6, Rly10
"""
This module facilitates the raspihats.i2c_hats package integration with robotframework.
All the following functions will be loaded as keywords by robotframework.

Example:

*** Settings ***
Documentation       Test Suite for Di6Rly6 I2C-HAT.
Library             raspihats.i2c_hats_robot

*** Test Cases ***

Set Global Variables
    ${i2c_hat_temp}     New Di6Rly6     ${0x60}
    Set Global Variable     ${i2c_hat}      ${i2c_hat_temp}

Board Name
    ${name}     Get Name    ${i2c_hat}
    Should Be Equal As Strings      ${name}     Di6Rly6 I2C-HAT
    
Read Digital Input
    ${state}    DO Get Channel      ${i2c_hat}      ${5}
    Should Be Equal As Strings      ${state}    ${False}
    Should Be Equal As Integers     ${state}    ${0}

"""

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
            D6Rly6: A new instance of Di6Rly6
    """
    return Di6Rly6(adr)

def get_name(i2c_hat):
    """Gets the I2C-HAT name. The exported robotframework keyword is 'Get Name'.
    
        Args:
            i2c_hat (I2CHat): board
        
        Returns:
            string: The name of the board
    """
    return i2c_hat.name

def get_status(i2c_hat):
    """Gets the I2C-HAT status word. The exported robotframework keyword is 'Get Status'.
    
        Args:
            i2c_hat (I2CHat): board
        
        Returns:
            int: The status word
    """
    return i2c_hat.status

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
    return i2c_hat.do.labels

def do_get_power_on_value(i2c_hat):
    """Gets the I2C-HAT digital outputs power on value. The exported robotframework keyword is 'DO Get Power On Value'.
    
        Args:
            i2c_hat (I2CHat): board
            
        Returns:
            int: The power on value of the digital outputs
    """
    return i2c_hat.do.power_on_value

def do_set_power_on_value(i2c_hat, value):
    """Sets the I2C-HAT digital outputs power on value. The exported robotframework keyword is 'DO Set Power On Value'.
    
        Args:
            i2c_hat (I2CHat): board
            value (int): desired power on value
    """
    i2c_hat.do.power_on_value = value
    
def do_get_safety_value(i2c_hat):
    """Gets the I2C-HAT digital outputs safety value. The exported robotframework keyword is 'DO Get Safety Value'.
    
        Args:
            i2c_hat (I2CHat): board
            
        Returns:
            int: The safety value of the digital outputs
    """
    return i2c_hat.do.safety_value

def do_set_safety_value(i2c_hat, value):
    """Sets the I2C-HAT digital outputs safety value. The exported robotframework keyword is 'DO Set Safety Value'.
    
        Args:
            i2c_hat (I2CHat): board
            value (int): desired safety value
    """
    i2c_hat.do.safety_value = value
    
def do_get_value(i2c_hat):
    """Gets the I2C-HAT digital outputs value(all channels). The exported robotframework keyword is 'DO Get Value'.
    
        Args:
            i2c_hat (I2CHat): board
            
        Returns:
            int: The value(all channels) of the digital outputs
    """
    return i2c_hat.do.value

def do_set_value(i2c_hat, value):
    """Sets the I2C-HAT digital outputs value(all channels). The exported robotframework keyword is 'DO Set Value'.
    
        Args:
            i2c_hat (I2CHat): board
            value (int): desired digital outputs value(all channels)
    """
    i2c_hat.do.value = value
    
def do_get_channel(i2c_hat, index):
    """Gets the I2C-HAT digital output channel value. The exported robotframework keyword is 'DO Get Channel'.
    
        Args:
            i2c_hat (I2CHat): board
            index (int): channel index
            
        Returns:
            boolean: The value of the digital output channel
    """
    return i2c_hat.do.channels[index]

def do_set_channel(i2c_hat, index, value):
    """Sets the I2C-HAT digital output channel value. The exported robotframework keyword is 'DO Set Channel'.
    
        Args:
            i2c_hat (I2CHat): board
            index (int): channel index
            value (boolean): desired digital output value
            
        Returns:
            boolean: The value of the digital output channel
    """
    i2c_hat.do.channels[index] = value

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