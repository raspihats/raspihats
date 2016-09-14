
# Digital Outputs Commands
CMD_DO_SET_POWER_ON_VALUE = 0x30
CMD_DO_GET_POWER_ON_VALUE = 0x31
CMD_DO_SET_SAFETY_VALUE = 0x32
CMD_DO_GET_SAFETY_VALUE = 0x33
CMD_DO_SET_ALL_CHANNEL_STATES = 0x34
CMD_DO_GET_ALL_CHANNEL_STATES = 0x35
CMD_DO_SET_CHANNEL_STATE = 0x36
CMD_DO_GET_CHANNEL_STATE = 0x37


class DigitalOutputs(object):
    """Extends the basic functionality by adding the required attributes and methods needed for operating
    the digital outputs channels.
    
    Note:
        The relay digital output channels are labeled Rlyx(x - relay number, starting from Rly1).
        The methods that operate on a single channel use the ``channel label`` or the ``channel index``
        (starting from 0) as channel parameter. Methods that operate on all channels use the ``int compact value``
        (all the digital output channels data states encoded as one channel state per bit) or a ``dict`` (all the
        channel labels as string keys and states as bool values) as input parameters or as returned values. 
    
    """
    def __init__(self, channel_labels, i2c_hat):
        """Construct a DigitalOutputs object, setting the I2C-HAT channel_labels, address, base_address and
        the I2C port.
        
        Args:
            channel_labels (List[str]): Labels of digital input channels

        """
        self.__do_channel_labels = channel_labels
        self.__i2c_hat = i2c_hat
        
        class Channel(object):
            def __init__(self, i2c_hat):
                self.__i2c_hat = i2c_hat
            
            def __getitem__(self, index):
                request = self.__i2c_hat._request_frame_(CMD_DO_GET_CHANNEL_STATE, [index])
                response = self.__i2c_hat._transfer_(request, 2)
                data = response.get_data()
                if len(data) != 2 or data[0] != index:
                    raise I2CHatResponseException('unexpected format')
                return data[1] > 0
            
            def __setitem__(self, index, value):
                data = [index, int(value)]
                request = self.__i2c_hat._request_frame_(CMD_DO_SET_CHANNEL_STATE, data)
                response = self.__i2c_hat._transfer_(request, 2)
                if data != response.get_data():
                    raise I2CHatResponseException('unexpected format')
        
        self.channel = Channel(i2c_hat)
        
    @property
    def power_on_value(self):
        return self.__i2c_hat._get_u32_value_(CMD_DO_GET_POWER_ON_VALUE)

    @power_on_value.setter
    def power_on_value(self, value):
        self.__i2c_hat._set_u32_value_(CMD_DO_SET_POWER_ON_VALUE, value)

    @property
    def safety_value(self):
        return self.__i2c_hat._get_u32_value_(CMD_DO_GET_SAFETY_VALUE)

    @safety_value.setter
    def safety_value(self, value):
        self.__i2c_hat._set_u32_value_(CMD_DO_SET_SAFETY_VALUE, value)

    @property
    def value(self):
        return self.__i2c_hat._get_u32_value_(CMD_DO_GET_ALL_CHANNEL_STATES)

    @value.setter
    def value(self, value):
        self.__i2c_hat._set_u32_value_(CMD_DO_SET_ALL_CHANNEL_STATES, value)
        