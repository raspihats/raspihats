from ._i2c_hat import Command, I2CHatModule, I2CHatResponseException


class DigitalInputs(I2CHatModule):
    """Attributes and methods needed for operating the digital inputs channels."""
    
    def __init__(self, i2c_hat, labels):
        """Construct a DigitalInputs object.
        
        Args:
            i2c_hat (I2CHat): board
            labels (List[str]): Labels of digital input channels as written on the board
        """
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
                
        self.channels = Channels()
        self.r_counters = Counters(1)
        self.f_counters = Counters(0)
    
    @property
    def value(self):
        """Getter for .value attributte
        
        Returns:
            int: The value of all the digital inputs, 1 bit represents 1 channel
        """
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
    """Attributes and methods needed for operating the digital outputs channels."""
    
    def __init__(self, i2c_hat, labels):
        """Construct a DigitalOutputs object.
        
        Args:
            i2c_hat (I2CHat): board
            labels (List[str]): Labels of digital input channels

        """
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
        
        self.channels = Channels()
        
    def _validate_value(self, value):
        max_value = (0x01 << len(self.labels)) - 1
        if not (0 <= value <= max_value):
            raise ValueError("'" + str(value) + "' is not a valid value, is [0x00 .. " + hex(max_value) + "]")
        
    @property
    def power_on_value(self):
        """Getter for .power_on_value attributte
        
        Returns:
            int: The power on value
        """
        return self._i2c_hat._get_u32_value_(Command.DO_GET_POWER_ON_VALUE)

    @power_on_value.setter
    def power_on_value(self, value):
        """Setter for .power_on_value attributte
        
        Args:
            value (int): new power on value
        """
        self._validate_value(value)
        self._i2c_hat._set_u32_value_(Command.DO_SET_POWER_ON_VALUE, value)

    @property
    def safety_value(self):
        """Getter for .safety_value attributte
        
        Returns:
            int: The safety value
        """
        return self._i2c_hat._get_u32_value_(Command.DO_GET_SAFETY_VALUE)

    @safety_value.setter
    def safety_value(self, value):
        """Setter for .safety_value attributte
        
        Args:
            value (int): new safety value
        """
        self._validate_value(value)
        self._i2c_hat._set_u32_value_(Command.DO_SET_SAFETY_VALUE, value)

    @property
    def value(self):
        """Getter for .value attributte
        
        Returns:
            int: The value of all the digital outputs, 1 bit represents 1 channel
        """
        return self._i2c_hat._get_u32_value_(Command.DO_GET_ALL_CHANNEL_STATES)

    @value.setter
    def value(self, value):
        """Getter for .value attributte.
        
        Args:
            value (int): The desired value of all the digital outputs, 1 bit represents 1 channel
        """
        self._validate_value(value)
        self._i2c_hat._set_u32_value_(Command.DO_SET_ALL_CHANNEL_STATES, value)
        