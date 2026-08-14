"""
This module contains the I2C-HATs classes.
"""
import smbus2
from ..protocol import BOARDS
from ._base import I2CHat, Cwdt, Irq, ResponseException
from ._digital import DigitalOutputs, DigitalInputs

def set_i2c_port(i2c_port):
    """Set the I2C port number.

    The bus is process-wide state shared by every I2CHat instance, so this
    has to be called before the first board is constructed.

    Args:
        i2c_port (int): I2C port number

    """
    if I2CHat._i2c_bus is not None:
        I2CHat._i2c_bus.close()
    I2CHat.I2C_PORT = i2c_port
    I2CHat._i2c_bus = smbus2.SMBus(i2c_port)

class Di16(I2CHat):
    """This class exposes all operations supported by the Di16 I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x40, 0x4F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        di (:obj:`raspihats.i2c_hats._digital.DigitalInputs`): provides access to DigitalInputs.

    """

    _INFO = BOARDS['Di16']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _labels = list(_INFO.labels['di'])

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

    _INFO = BOARDS['Rly10']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _labels = list(_INFO.labels['dq'])

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

    _INFO = BOARDS['Di6Rly6']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _di_labels = list(_INFO.labels['di'])
    _dq_labels = list(_INFO.labels['dq'])

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

    _INFO = BOARDS['DI16ac']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _labels = list(_INFO.labels['di'])


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

    _INFO = BOARDS['DQ16oc']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _labels = list(_INFO.labels['dq'])

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

    _INFO = BOARDS['DQ10rly']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _labels = list(_INFO.labels['dq'])

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

    _INFO = BOARDS['DQ8rly']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _labels = list(_INFO.labels['dq'])

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.dq = DigitalOutputs(self, self._labels)

class DQ5rly(I2CHat):
    """This class exposes all operations supported by the DQ5rly I2C-HAT.

    Args:
        address (:obj:`int`): I2C bus address, valid range is [0x50, 0x5F]

    Attributes:
        cwdt (:obj:`raspihats.i2c_hats._base.Cwdt`): provides access to CommunicationWatchDogTimer.
        dq (:obj:`raspihats.i2c_hats._digital.DigitalOutputs`): provides access to DigitalOutputs.
    """

    _INFO = BOARDS['DQ5rly']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _labels = list(_INFO.labels['dq'])

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

    _INFO = BOARDS['DI6acDQ6rly']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _di_labels = list(_INFO.labels['di'])
    _dq_labels = list(_INFO.labels['dq'])

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

    _INFO = BOARDS['DI6acDQ6ssr']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _di_labels = list(_INFO.labels['di'])
    _dq_labels = list(_INFO.labels['dq'])

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

    _INFO = BOARDS['DI6dwDQ6ssr']
    _BASE_ADDRESS = _INFO.base_address
    _BOARD_NAME = _INFO.board_name
    _di_labels = list(_INFO.labels['di'])
    _dq_labels = list(_INFO.labels['dq'])

    def __init__(self, address):
        I2CHat.__init__(self, address, self._BASE_ADDRESS, self._BOARD_NAME)
        self.cwdt = Cwdt(self)
        self.irq = Irq(self)
        self.di = DigitalInputs(self, self._di_labels)
        self.dq = DigitalOutputs(self, self._dq_labels)