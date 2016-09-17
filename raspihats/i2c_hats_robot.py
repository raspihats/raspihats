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
    """Get name of I2C-Hat. The exported robotframework keyword is 'Get Name'.
    
        Args:
            i2c_hat (I2CHat): board
        
        Returns:
            string: The name of the board
    """
    return i2c_hat.name

def get_status(i2c_hat):
    return i2c_hat.status

def reset(i2c_hat):
    i2c_hat.reset()
    
def cwdt_get_period(i2c_hat):
    return i2c_hat.cwdt.period

def cwdt_set_period(i2c_hat, value):
    i2c_hat.cwdt.period = value
    
def do_get_labels(i2c_hat):
    return i2c_hat.do.labels

def do_get_power_on_value(i2c_hat):
    return i2c_hat.do.power_on_value

def do_set_power_on_value(i2c_hat, value):
    i2c_hat.do.power_on_value = value
    
def do_get_safety_value(i2c_hat):
    return i2c_hat.do.safety_value

def do_set_safety_value(i2c_hat, value):
    i2c_hat.do.safety_value = value
    
def do_get_value(i2c_hat):
    return i2c_hat.do.value

def do_set_value(i2c_hat, value):
    i2c_hat.do.value = value
    
def do_get_channel(i2c_hat, index):
    return i2c_hat.do.channels[index]

def do_set_channel(i2c_hat, index, value):
    i2c_hat.do.channels[index] = value

def di_get_labels(i2c_hat):
    return i2c_hat.di.labels

def di_get_value(i2c_hat):
    return i2c_hat.di.value

def di_get_channel(i2c_hat, index):
    return i2c_hat.di.channels[index]

def di_get_counter(i2c_hat, index, counter_type):
    if counter_type == 0:
        value = i2c_hat.di.f_counters[index]
    else:
        value = i2c_hat.di.r_counters[index]
    return value

def di_reset_counter(i2c_hat, index, counter_type):
    if counter_type == 0:
        i2c_hat.di.f_counters[index] = 0
    else:
        i2c_hat.di.r_counters[index] = 0
        
def di_reset_counters(i2c_hat):
    i2c_hat.di.reset_counters()