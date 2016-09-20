from ._i2c_hat import Command, I2CHatModule, I2CHatResponseException


class DigitalInputs(I2CHatModule):
    """Attributes and methods needed for operating the digital inputs channels.
    
    Args:
        i2c_hat (:obj:`raspihats._i2c_hat.I2CHat`): I2CHat instance
        labels (:obj:`list` of :obj:`str`): Labels of digital input channels
        
    Attributes:
        channels (:obj:`list` of :obj:`bool`): List like object, provides single channel access to digital inputs.
        counters (:obj:`list` of :obj:`int`): List like object, provides single channel access to digital input counters.
        
    """
    
    def __init__(self, i2c_hat, labels):
        I2CHatModule.__init__(self, i2c_hat, labels)
        outer_instance = self
        
        class Channels(object):
            def __getitem__(self, index):
                index = outer_instance._validate_channel_index(index)
                request = outer_instance._i2c_hat._request_frame_(Command.DI_GET_CHANNEL_STATE, [index])
                response = outer_instance._i2c_hat._transfer_(request, 2)
                data = response.data
                if len(data) != 2 or data[0] != index:
                    raise I2CHatResponseException('unexpected format')
                return data[1] > 0
            
            def __len__(self):
                return len(outer_instance.labels)
        
        class Counters(object):
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
                
            def __len__(self):
                return len(outer_instance.labels)
                
        self.channels = Channels()
        self.r_counters = Counters(1)
        self.f_counters = Counters(0)
    
    @property
    def value(self):
        """:obj:`int`: The value of all the digital inputs, 1 bit represents 1 channel."""

        return self._i2c_hat._get_u32_value_(Command.DI_GET_ALL_CHANNEL_STATES)
    
    def reset_counters(self):
        """Resets all digital input channel counters of all types(falling and rising edge).
        
        Raises:
            I2CHatResponseException: If the response hasn't got the expected format
        
        """
        request = self._i2c_hat._request_frame_(Command.DI_RESET_ALL_COUNTERS)
        response = self._i2c_hat._transfer_(request, 0)
        data = response.data
        if len(data) != 0:
            raise I2CHatResponseException('unexpected format')


class DigitalOutputs(I2CHatModule):
    """Attributes and methods needed for operating the digital outputs channels.

    Args:
        i2c_hat (:obj:`raspihats._i2c_hat.I2CHat`): I2CHat instance
        labels (:obj:`list` of :obj:`str`): Labels of digital output channels
        
    Attributes:
        channels (:obj:`list` of :obj:`bool`): List like object, provides single channel access to digital outputs.
        
    """
    
    def __init__(self, i2c_hat, labels):
        I2CHatModule.__init__(self, i2c_hat, labels)
        outer_instance = self
        
        class Channels(object):
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
                value = int(value)
                if not (0 <= value <= 1):
                    raise ValueError("'" + str(value) + "' is not a valid value, use: 0 or 1, True or False")
                data = [index, value]
                request = outer_instance._i2c_hat._request_frame_(Command.DO_SET_CHANNEL_STATE, data)
                response = outer_instance._i2c_hat._transfer_(request, 2)
                if data != response.data:
                    raise I2CHatResponseException('unexpected format')
                
            def __len__(self):
                return len(outer_instance.labels)
        
        self.channels = Channels()
        
    @property
    def value(self):
        """:obj:`int`: The value of all the digital outputs, 1 bit represents 1 channel."""
        
        return self._i2c_hat._get_u32_value_(Command.DO_GET_ALL_CHANNEL_STATES)

    @value.setter
    def value(self, value):
        self._validate_value(value)
        self._i2c_hat._set_u32_value_(Command.DO_SET_ALL_CHANNEL_STATES, value)
        
    @property
    def power_on_value(self):
        """:obj:`int`: Power On Value, this is loaded to outputs at power on."""
        
        return self._i2c_hat._get_u32_value_(Command.DO_GET_POWER_ON_VALUE)

    @power_on_value.setter
    def power_on_value(self, value):
        self._validate_value(value)
        self._i2c_hat._set_u32_value_(Command.DO_SET_POWER_ON_VALUE, value)

    @property
    def safety_value(self):
        """:obj:`int`: Safety Value, this is loaded to outputs at Cwdt Timeout."""
        
        return self._i2c_hat._get_u32_value_(Command.DO_GET_SAFETY_VALUE)

    @safety_value.setter
    def safety_value(self, value):
        self._validate_value(value)
        self._i2c_hat._set_u32_value_(Command.DO_SET_SAFETY_VALUE, value)
        