"""
This module contains the I2C-HATs classes.
"""
from ._i2c_hat import I2CHat, Cwdt
from ._digital import DigitalOutputs, DigitalInputs

class Di16(I2CHat):
    """This class exposes all operations supported by the Rly10 I2C-HAT, it inherits functionality from DigitalInputs class."""
    
    BASE_ADDRESS = 0x40
    """I2C start address for Di16 I2C-HATs, valid range is [0x40 .. 0x4F]."""
    
    BOARD_NAME = "Di16 I2C-HAT"
    """Expected board name response for the get_board_name() method."""
    
    __labels = [
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
        I2CHat.__init__(self, address, self.BASE_ADDRESS, self.BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.di = DigitalInputs(self, self.__labels)

class Rly10(I2CHat):
    """This class exposes all operations supported by the Rly10 I2C-HAT, it inherits functionality from DigitalOutputs class."""
    
    BASE_ADDRESS = 0x50
    """I2C start address for Di16 I2C-HATs, valid range is [0x50 .. 0x5F]."""
    
    BOARD_NAME = "Rly10 I2C-HAT"
    """Expected board name response for the get_board_name() method."""
    
    __labels = ['Rly1', 'Rly2', 'Rly3', 'Rly4', 'Rly5', 'Rly6', 'Rly7', 'Rly8', 'Rly9', 'Rly10']
    
    def __init__(self, address):
        """Construct a Rly10 object, setting the I2C port and I2C-HAT address.
        
        Args:
            address(int): I2C address, valid range is [0x50, 0x5F]
                        
        """
        I2CHat.__init__(self, address, self.BASE_ADDRESS, self.BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.do = DigitalOutputs(self, self.__labels)
 

class Di6Rly6(I2CHat):
    """This class exposes all operations supported by the Di6Rly6 I2C-HAT, it inherits functionality from DigitalInputs and DigitalOutputs classes."""
    
    BASE_ADDRESS = 0x60
    """I2C start address for Di16 I2C-HATs, valid range is [0x60 .. 0x6F]."""
    
    BOARD_NAME = "Di6Rly6 I2C-HAT"
    """Expected board name response for the get_board_name() method."""
    
    __di_labels = ['Di1.1', 'Di1.2', 'Di1.3', 'Di1.4', 'Di1.5', 'Di1.6']
    __do_labels = ['Rly1', 'Rly2', 'Rly3', 'Rly4', 'Rly5', 'Rly6']
    
    def __init__(self, address):
        """Construct a Di6Rly6 object, setting the I2C port and I2C-HAT address.
        
        Args:
            address(int): I2C address, valid range is [0x60, 0x6F]
            
        """
        I2CHat.__init__(self, address, self.BASE_ADDRESS, self.BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.di = DigitalInputs(self, self.__di_labels)
        self.do = DigitalOutputs(self, self.__do_labels)