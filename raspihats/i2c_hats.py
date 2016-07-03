"""
This module contains the I2CHats classes.
"""
from .i2c_hat_modules import DigitalInputs, DigitalOutputs

class Di16(DigitalInputs):
    """This class exposes all operations supported by the Rly10 I2C-HAT, it inherits functionality from DigitalInputs class."""
    
    BASE_ADDRESS = 0x40
    """I2C start address for Di16 I2C-HATs, valid range is [0x40 .. 0x4F]."""
    
    BOARD_NAME = "Di16 I2C-HAT"
    """Expected board name response for the get_board_name() method."""
    
    __labels__ = [
        'Di1.1', 'Di1.2', 'Di1.3', 'Di1.4',
        'Di2.1', 'Di2.2', 'Di2.3', 'Di2.4',
        'Di3.1', 'Di3.2', 'Di3.3', 'Di3.4',
        'Di4.1', 'Di4.2', 'Di4.3', 'Di4.4',
        ]
    
    def __init__(self, address):
        """Construct a Di16 object, setting the I2C port and I2C-HAT address.
        
        Args:
            address(int): I2C address, valid range is [0x40, 0x4F]
            
        """
        DigitalInputs.__init__(self, self.__labels__, address, Di16.BASE_ADDRESS, Di16.BOARD_NAME)

class Rly10(DigitalOutputs):
    """This class exposes all operations supported by the Rly10 I2C-HAT, it inherits functionality from DigitalOutputs class."""
    
    BASE_ADDRESS = 0x50
    """I2C start address for Di16 I2C-HATs, valid range is [0x50 .. 0x5F]."""
    
    BOARD_NAME = "Rly10 I2C-HAT"
    """Expected board name response for the get_board_name() method."""
    
    __labels__ = ['Rly1', 'Rly2', 'Rly3', 'Rly4', 'Rly5', 'Rly6', 'Rly7', 'Rly8', 'Rly9', 'Rly10']
    
    def __init__(self, address):
        """Construct a Rly10 object, setting the I2C port and I2C-HAT address.
        
        Args:
            address(int): I2C address, valid range is [0x50, 0x5F]
                        
        """
        DigitalOutputs.__init__(self, self.__labels__, address, Rly10.BASE_ADDRESS, Rly10.BOARD_NAME)

class Di6Rly6(DigitalInputs, DigitalOutputs):
    """This class exposes all operations supported by the Di6Rly6 I2C-HAT, it inherits functionality from DigitalInputs and DigitalOutputs classes."""
    
    BASE_ADDRESS = 0x60
    """I2C start address for Di16 I2C-HATs, valid range is [0x60 .. 0x6F]."""
    
    BOARD_NAME = "Di6Rly6 I2C-HAT"
    """Expected board name response for the get_board_name() method."""
    
    __di_labels__ = ['Di1.1', 'Di1.2', 'Di1.3', 'Di1.4', 'Di1.5', 'Di1.6']
    __do_labels__ = ['Rly1', 'Rly2', 'Rly3', 'Rly4', 'Rly5', 'Rly6']
    
    def __init__(self, address):
        """Construct a Di6Rly6 object, setting the I2C port and I2C-HAT address.
        
        Args:
            address(int): I2C address, valid range is [0x60, 0x6F]
            
        """
        DigitalInputs.__init__(self, self.__di_labels__, address, Di6Rly6.BASE_ADDRESS, Di6Rly6.BOARD_NAME)
        DigitalOutputs.__init__(self, self.__do_labels__, address, Di6Rly6.BASE_ADDRESS, Di6Rly6.BOARD_NAME)