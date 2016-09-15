from ._i2c_hat import Command, I2CHatModule


class DigitalInputs(I2CHatModule):
    """Extends the basic functionality by adding the required attributes and methods needed for operating the digital inputs channels.
    
    Note:
        The digital input channels are separated in blocks and labeled Dix.y (x - block number, y - channel
        number). The methods that operate on a single channel use the ``channel label`` (starting from Di1.1)
        or the ``channel index`` (starting from 0) as channel parameter. Methods that operate on all channels can
        return an ``int compact value`` that contains all the digital input channels states from all blocks, one
        channel per bit, for example, Di16 I2C-HAT has 4 input blocks, in this case bit0 of the compact value
        reflects state of Di1.1, bit1 - Di1.2, .. bit4 - Di2.1 an so on...
    
    """
    
    def __init__(self, i2c_hat, labels):
        """Construct a DigitalInputs object, setting the channel_labels, I2C-HAT address and base_address and the I2C port.
        
        Args:
            labels (List[str]): Labels of digital input channels as written on the board
            address (int): I2C address, valid range is dependent of base_address
            base_address (int): I2C-HAT family base address
            board_name (str): I2C-HAT board name
        """
        I2CHatModule.__init__(self, i2c_hat, labels)
        outer_instance = self
        
        class Channel(object):
            def __getitem__(self, index):
                index = outer_instance._validate_channel_index(index)
                request = outer_instance._i2c_hat._request_frame_(Command.DI_GET_CHANNEL_STATE, [index])
                response = outer_instance._i2c_hat._transfer_(request, 2)
                data = response.data
                if len(data) != 2 or data[0] != index:
                    raise I2CHatResponseException('unexpected format')
                return data[1] > 0
        
        class Counter(object):
            def __init__(self, counter_type):
                self.__counter_type = counter_type
            
            def __getitem__(self, index):
                index = outer_instance._validate_channel_index(index)
                request = outer_instance._i2c_hat._request_frame_(Command.DI_GET_COUNTER, [index, self.__counter_type])
                response = outer_instance._i2c_hat._transfer_(request, 6)
                data = response.data
                if (len(data) != 1 + 1 + 4) or (index != data[0]) or (self.__counter_type != data[1]):
                    raise I2CHatResponseException('unexpected format')
                return data[2] + (data[3] << 8) + (data[4] << 16) + (data[5] << 24)
            
            def __setitem__(self, index, value):
                index = outer_instance._validate_channel_index(index)
                if value != 0:
                    raise ValueError("only '0' is valid, it will reset the counter")
                request = outer_instance._i2c_hat._request_frame_(Command.DI_RESET_COUNTER, [index, self.__counter_type])
                response = outer_instance._i2c_hat._transfer_(request, 2)
                data = response.data
                if (len(data) != 2) or (index != data[0]) or (self.__counter_type != data[1]):
                    raise I2CHatResponseException('unexpected format')
                
        self.channel = Channel()
        self.r_counter = Counter(1)
        self.f_counter = Counter(0)
    
    @property
    def value(self):
        return self._i2c_hat._get_u32_value_(Command.DI_GET_ALL_CHANNEL_STATES)
    
    def reset_counters(self):
        """Send a I2C request request to reset all digital input channel counters of all types(falling and
        rising edge).
        
        Raises:
            I2CHatResponseException: If the response hasn't got the expected format
        
        """
        request = self._i2c_hat._request_frame_(Command.DI_RESET_ALL_COUNTERS)
        response = self._i2c_hat._transfer_(request, 0)
        data = response.data
        if len(data) != 0:
            raise I2CHatResponseException('unexpected format')


class DigitalOutputs(I2CHatModule):
    """Extends the basic functionality by adding the required attributes and methods needed for operating
    the digital outputs channels.
    
    Note:
        The relay digital output channels are labeled Rlyx(x - relay number, starting from Rly1).
        The methods that operate on a single channel use the ``channel label`` or the ``channel index``
        (starting from 0) as channel parameter. Methods that operate on all channels use the ``int compact value``
        (all the digital output channels data states encoded as one channel state per bit) or a ``dict`` (all the
        channel labels as string keys and states as bool values) as input parameters or as returned values. 
    
    """
    def __init__(self, i2c_hat, labels):
        """Construct a DigitalOutputs object, setting the I2C-HAT channel_labels, address, base_address and
        the I2C port.
        
        Args:
            channel_labels (List[str]): Labels of digital input channels

        """
        I2CHatModule.__init__(self, i2c_hat, labels)
        outer_instance = self
        
        class Channel(object):
            def __getitem__(self, index):
                index = outer_instance._validate_channel_index(index)
                request = outer_instance._i2c_hat._request_frame_(Command.DO_GET_CHANNEL_STATE, [index])
                response = outer_instance._i2c_hat._transfer_(request, 2)
                data = response.data
                if len(data) != 2 or data[0] != index:
                    raise I2CHatResponseException('unexpected format')
                return data[1] > 0
            
            def __setitem__(self, index, value):
                index = outer_instance._validate_channel_index(index)
                data = [index, int(value)]
                request = outer_instance._i2c_hat._request_frame_(Command.DO_SET_CHANNEL_STATE, data)
                response = outer_instance._i2c_hat._transfer_(request, 2)
                if data != response.data:
                    raise I2CHatResponseException('unexpected format')
        
        self.channel = Channel()
        
    @property
    def power_on_value(self):
        return self._i2c_hat._get_u32_value_(Command.DO_GET_POWER_ON_VALUE)

    @power_on_value.setter
    def power_on_value(self, value):
        self._i2c_hat._set_u32_value_(Command.DO_SET_POWER_ON_VALUE, value)

    @property
    def safety_value(self):
        return self._i2c_hat._get_u32_value_(Command.DO_GET_SAFETY_VALUE)

    @safety_value.setter
    def safety_value(self, value):
        self._i2c_hat._set_u32_value_(Command.DO_SET_SAFETY_VALUE, value)

    @property
    def value(self):
        return self._i2c_hat._get_u32_value_(Command.DO_GET_ALL_CHANNEL_STATES)

    @value.setter
    def value(self, value):
        self._i2c_hat._set_u32_value_(Command.DO_SET_ALL_CHANNEL_STATES, value)
        