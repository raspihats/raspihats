"""
This module contains the I2C-HATs classes.
"""
from ._base import I2CHat, Cwdt, Irq, ResponseException
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
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        di (:obj:`raspihats.i2c_hats._digital.DigitalInputs`): provides access to DigitalInputs.

    """

    _BASE_ADDRESS = 0x40
    _BOARD_NAME = 'Di16 I2C-HAT'
    _labels = [
        'Di1.1', 'Di1.2', 'Di1.3', 'Di1.4',
        'Di2.1', 'Di2.2', 'Di2.3', 'Di2.4',
        'Di3.1', 'Di3.2', 'Di3.3', 'Di3.4',
        'Di4.1', 'Di4.2', 'Di4.3', 'Di4.4',
    ]

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.di = DigitalInputs(self, self._labels)

class Rly10(I2CHat):
    """This class exposes all operations supported by the Rly10 I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x50, 0x5F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        dq (:obj:`raspihats.i2c_hats._digital.DigitalOutputs`): provides access to DigitalOutputs.
    """

    _BASE_ADDRESS = 0x50
    _BOARD_NAME = 'Rly10 I2C-HAT'
    _labels = ['Rly1', 'Rly2', 'Rly3', 'Rly4', 'Rly5', 'Rly6', 'Rly7', 'Rly8', 'Rly9', 'Rly10']

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.dq = DigitalOutputs(self, self._labels)

class Di6Rly6(I2CHat):
    """This class exposes all operations supported by the Di6Rly6 I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x60, 0x6F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        di (:obj:`raspihats.i2c_hats._digital.DigitalInputs`): provides access to DigitalInputs.
        dq (:obj:`raspihats.i2c_hats._digital.DigitalOutputs`): provides access to DigitalOutputs.

    """

    _BASE_ADDRESS = 0x60
    _BOARD_NAME = 'Di6Rly6 I2C-HAT'
    _di_labels = ['Di1.1', 'Di1.2', 'Di1.3', 'Di1.4', 'Di1.5', 'Di1.6']
    _dq_labels = ['Rly1', 'Rly2', 'Rly3', 'Rly4', 'Rly5', 'Rly6']

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.di = DigitalInputs(self, self._di_labels)
        self.dq = DigitalOutputs(self, self._dq_labels)

class DI16ac(I2CHat):
    """This class exposes all operations supported by the DI16ac I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x40, 0x4F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        di (:obj:`raspihats.i2c_hats._digital.DigitalInputs`): provides access to DigitalInputs.

    """

    _BASE_ADDRESS = 0x40
    _BOARD_NAME = 'DI16ac I2C-HAT'
    _labels = ['I0', 'I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8', 'I9', 'I10', 'I11', 'I12', 'I13', 'I14', 'I15']


    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.irq = Irq(self)
        self.di = DigitalInputs(self, self._labels)

class DQ16oc(I2CHat):
    """This class exposes all operations supported by the DQ16oc I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x50, 0x5F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        dq (:obj:`raspihats.i2c_hats._digital.DigitalOutputs`): provides access to DigitalOutputs.
    """

    _BASE_ADDRESS = 0x50
    _BOARD_NAME = 'DQ16oc I2C-HAT'
    _labels = ['Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15']

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.dq = DigitalOutputs(self, self._labels)

class DQ10rly(I2CHat):
    """This class exposes all operations supported by the DQ10rly I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x50, 0x5F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        dq (:obj:`raspihats.i2c_hats._digital.DigitalOutputs`): provides access to DigitalOutputs.
    """

    _BASE_ADDRESS = 0x50
    _BOARD_NAME = 'DQ10rly I2C-HAT'
    _labels = ['Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9']

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.dq = DigitalOutputs(self, self._labels)

class DQ8rly(I2CHat):
    """This class exposes all operations supported by the DQ8rly I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x50, 0x5F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        dq (:obj:`raspihats.i2c_hats._digital.DigitalOutputs`): provides access to DigitalOutputs.
    """

    _BASE_ADDRESS = 0x50
    _BOARD_NAME = 'DQ8rly I2C-HAT'
    _labels = ['Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7']

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.dq = DigitalOutputs(self, self._labels)

class DI6acDQ6rly(I2CHat):
    """This class exposes all operations supported by the DI6acDQ6rly I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x60, 0x6F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        di (:obj:`raspihats.i2c_hats._digital.DigitalInputs`): provides access to DigitalInputs.
        dq (:obj:`raspihats.i2c_hats._digital.DigitalOutputs`): provides access to DigitalOutputs.

    """

    _BASE_ADDRESS = 0x60
    _BOARD_NAME = 'DI6acDQ6rly I2C-HAT'
    _di_labels = ['I0', 'I1', 'I2', 'I3', 'I4', 'I5']
    _dq_labels = ['Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5']

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.irq = Irq(self)
        self.di = DigitalInputs(self, self._di_labels)
        self.dq = DigitalOutputs(self, self._dq_labels)

class DI6acDQ6ssr(I2CHat):
    """This class exposes all operations supported by the DI6acDQ6ssr I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x60, 0x6F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        di (:obj:`raspihats.i2c_hats._digital.DigitalInputs`): provides access to DigitalInputs.
        dq (:obj:`raspihats.i2c_hats._digital.DigitalOutputs`): provides access to DigitalOutputs.

    """

    _BASE_ADDRESS = 0x70
    _BOARD_NAME = 'DI6acDQ6ssr I2C-HAT'
    _di_labels = ['I0', 'I1', 'I2', 'I3', 'I4', 'I5']
    _dq_labels = ['Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5']

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.irq = Irq(self)
        self.di = DigitalInputs(self, self._di_labels)
        self.dq = DigitalOutputs(self, self._dq_labels)


class DI6dwDQ6ssr(I2CHat):
    """This class exposes all operations supported by the DI6dwDQ6ssr I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x60, 0x6F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        di (:obj:`raspihats.i2c_hats._digital.DigitalInputs`): provides access to DigitalInputs.
        dq (:obj:`raspihats.i2c_hats._digital.DigitalOutputs`): provides access to DigitalOutputs.

    """

    _BASE_ADDRESS = 0x80
    _BOARD_NAME = 'DI6dwDQ6ssr I2C-HAT'
    _di_labels = ['I0', 'I1', 'I2', 'I3', 'I4', 'I5']
    _dq_labels = ['Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5']

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.irq = Irq(self)
        self.di = DigitalInputs(self, self._di_labels)
        self.dq = DigitalOutputs(self, self._dq_labels)