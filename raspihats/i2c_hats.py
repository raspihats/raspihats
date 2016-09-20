"""
This module contains the I2C-HATs classes.
"""
from ._i2c_hat import I2CHat, Cwdt
from ._digital import DigitalOutputs, DigitalInputs

def set_i2c_port(i2c_port):
    """Set the I2C port number.
            
    Args:
        i2c_port (int): I2C port number
    
    """
    import smbus
    I2CHat._i2c_bus = smbus.SMBus(i2c_port)

class Di16(I2CHat):
    """This class exposes all operations supported by the Di16 I2C-HAT.
    
    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x40, 0x4F]

    Attributes:
        cwdt (:obj:`raspihats._i2c_hat.Cwdt`): provides access to CommunicationWatchDogTimer.
        di (:obj:`raspihats._digital.DigitalInputs`): provides access to DigitalInputs.
    
    """

    __BASE_ADDRESS = 0x40
    __BOARD_NAME = 'Di16 I2C-HAT'
    __labels = [
        'Di1.1', 'Di1.2', 'Di1.3', 'Di1.4',
        'Di2.1', 'Di2.2', 'Di2.3', 'Di2.4',
        'Di3.1', 'Di3.2', 'Di3.3', 'Di3.4',
        'Di4.1', 'Di4.2', 'Di4.3', 'Di4.4',
    ]
    
    def __init__(self, address):
        I2CHat.__init__(self, address, self.__BASE_ADDRESS, self.__BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.di = DigitalInputs(self, self.__labels)

class Rly10(I2CHat):
    """This class exposes all operations supported by the Rly10 I2C-HAT.
    
    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x50, 0x5F]

    Attributes:
        cwdt (:obj:`raspihats._i2c_hat.Cwdt`): provides access to CommunicationWatchDogTimer.
        do (:obj:`raspihats._digital.DigitalOutputs`): provides access to DigitalOutputs.
    """
    
    __BASE_ADDRESS = 0x50    
    __BOARD_NAME = 'Rly10 I2C-HAT'
    __labels = ['Rly1', 'Rly2', 'Rly3', 'Rly4', 'Rly5', 'Rly6', 'Rly7', 'Rly8', 'Rly9', 'Rly10']
    
    def __init__(self, address):
        I2CHat.__init__(self, address, self.__BASE_ADDRESS, self.__BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.do = DigitalOutputs(self, self.__labels)

class Di6Rly6(I2CHat):
    """This class exposes all operations supported by the Di6Rly6 I2C-HAT.
    
    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x60, 0x6F]

    Attributes:
        cwdt (:obj:`raspihats._i2c_hat.Cwdt`): provides access to CommunicationWatchDogTimer.
        di (:obj:`raspihats._digital.DigitalInputs`): provides access to DigitalInputs.
        do (:obj:`raspihats._digital.DigitalOutputs`): provides access to DigitalOutputs.
    
    """
    
    __BASE_ADDRESS = 0x60
    __BOARD_NAME = 'Di6Rly6 I2C-HAT'
    __di_labels = ['Di1.1', 'Di1.2', 'Di1.3', 'Di1.4', 'Di1.5', 'Di1.6']
    __do_labels = ['Rly1', 'Rly2', 'Rly3', 'Rly4', 'Rly5', 'Rly6']
    
    def __init__(self, address):
        I2CHat.__init__(self, address, self.__BASE_ADDRESS, self.__BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.di = DigitalInputs(self, self.__di_labels)
        self.do = DigitalOutputs(self, self.__do_labels)
