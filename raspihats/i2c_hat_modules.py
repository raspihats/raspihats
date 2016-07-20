"""
This module contains the I2CHat base class and extensions.
"""
import sys
import time
import smbus
import threading
from .i2c_frame import I2CFrame
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue

# General Board Commands
CMD_GET_BOARD_NAME = 0x10
CMD_GET_FIRMWARE_VERSION = 0x11
CMD_GET_STATUS_WORD = 0x12
CMD_RESET = 0x13

# Communication WatchDog Commands
CMD_CWDT_SET_PERIOD = 0x14
CMD_CWDT_GET_PERIOD = 0x15
CMD_CWDT_SET_STATE = 0x16

# Digital Inputs Commands
CMD_DI_GET_ALL_CHANNEL_STATES = 0x20
CMD_DI_GET_CHANNEL_STATE = 0x21
CMD_DI_GET_COUNTER = 0x22
CMD_DI_RESET_COUNTER = 0x23
CMD_DI_RESET_ALL_COUNTERS = 0x24

# Digital Outputs Commands
CMD_DO_SET_POWER_ON_VALUE = 0x30
CMD_DO_GET_POWER_ON_VALUE = 0x31
CMD_DO_SET_SAFETY_VALUE = 0x32
CMD_DO_GET_SAFETY_VALUE = 0x33
CMD_DO_SET_ALL_CHANNEL_STATES = 0x34
CMD_DO_GET_ALL_CHANNEL_STATES = 0x35
CMD_DO_SET_CHANNEL_STATE = 0x36
CMD_DO_GET_CHANNEL_STATE = 0x37

class I2CHatResponseException(Exception):
    """Raised when there's a problem with the I2C-HAT response."""

class I2CHat(threading.Thread):
    """Implements basic functionality common to all I2C-HATs."""
        
    i2c_bus_lock = threading.Lock()
    try:
        i2c_bus = smbus.SMBus(1)     # default for Raspberry Pi
    except:
        print("I2C port not found!")
        i2c_bus = None

    @staticmethod
    def set_i2c_port(i2c_port):
        """Set the I2C port number.
                
        Args:
            i2c_port (int): I2C port number
        
        """
        I2CHat.i2c_bus = smbus.SMBus(i2c_port)
    
    def __init__(self, address, base_address=None, board_name=None):
        """Build I2CHat object setting the I2C bus and I2C address.
        
        Args:
            address (int): I2C address, valid range is dependent of base_address
            base_address (int): I2C-HAT base address
            board_name (str): I2C-HAT board name
            
        Raises:
            ValueError: If address is not in range
            
        """
    
        threading.Thread.__init__(self)
        
        if base_address == None:
            if not 0 <= address <= 127:
                raise ValueError("I2C address should be in range[0, 127]")
        else:
            if address & base_address != base_address:
                raise ValueError("I2C address should be in range[" + hex(base_address) + ", " + hex(base_address + 0x0F) + "]")

        self.address = address
        self.frame_id = 0x1F - 1
        
        if board_name != None:
            actual_board_name = self.get_board_name()
            if actual_board_name not in board_name:
                raise Exception("Unexpected board name: " + actual_board_name + ", expecting: " + board_name)
        
        self.cmd_queue = queue.Queue()
        self.ex_queue = queue.Queue()
        
    def __str__(self):
        """Returns the string representation."""
        
        return self.get_board_name() + " adr: " + hex(self.address)
    
    def __lower_case_labels__(self, labels):
        """Lower case labels.
        
        Args:
            list: labels
        
        Returns:
            list: The lower case labels
            
        """
        
        lower_case_labels = []
        for label in labels:
            lower_case_labels.append(label.lower())
        
        return lower_case_labels

    def _generate_frame_id_(self):
        """Generate new frame Id, increments current frame Id, wraps to 0xFF.
        
        Returns:
            int: The new frame Id
            
        """
        self.frame_id += 1
        self.frame_id &= 0xFF
        return self.frame_id
    
    def _transfer_(self, _request_frame_, response_data_size, response_expected = True, number_of_tries = 5):
        """Tries a number of times to send a request frame and to get a response frame over I2C bus.
        
        Args:
            _request_frame_ (I2CFrame): Request frame to be sent over the I2C bus
            response_data_size (int): Expected response data size, this is the payload data size
            response_expected (bool): True if a respose is expected
            number_of_tries (int): Number of tries to get the response
            
        Returns:
            I2CFrame: The response frame
            
        Raises:
            I2CHatResponseException: After all attempts to get a response have failed
            
        """
        with I2CHat.i2c_bus_lock:
            exceptions = []
            try_cnt = 0
            while True:
                try:
                    request_data = _request_frame_.encode()
                    # print request_data
                    
                    # NOTE: write_i2c_block_data function is used to send commands to the I2C-HAT
                    I2CHat.i2c_bus.write_i2c_block_data(self.address, request_data[0], request_data[1:])
                    
                    if not response_expected:
                        return
                     
                    # NOTE: read_i2c_block_data function sends a i2c_write first, this write has a length of one, and the dummy_byte as payload, this
                    # write will be ignored by the I2C-HAT, after this a i2c_read will be issued, this i2c_read is used for reading the response        
                    dummy_byte = 0xFF
                    expected_response_size = I2CFrame.ID_SIZE + I2CFrame.CMD_SIZE + response_data_size + I2CFrame.CRC_SIZE
                    response_data = I2CHat.i2c_bus.read_i2c_block_data(self.address, dummy_byte, expected_response_size)
                    # print response_data
                    
                    # build response frame
                    response_frame = I2CFrame(_request_frame_.get_id(), _request_frame_.get_cmd())
                    response_frame.decode(response_data)
                    return response_frame
                except Exception as ex:
                    exceptions.append(ex)
                    try_cnt += 1
                    if try_cnt < number_of_tries:
                        time.sleep(0.01)
                    else:
                        message = ""
                        for i in range(0, len(exceptions)):
                            message += "try: " + str(i + 1) + " result: " + str(exceptions[i]) + "\n"
                        raise I2CHatResponseException(message)
                
    def _get_u32_value_(self, cmd):
        """Generic get for a unsigned32 value.
        
        Args:
            cmd (int): Command byte value
        
        Returns:
            int: The desired unsigned32 value
            
        Raises:
            I2CHatResponseException: If response has bad data length
            
        """
        request = self._request_frame_(cmd, [])
        response = self._transfer_(request, 4)
        data = response.get_data()
        if len(data) != 4:
            raise I2CHatResponseException('unexpected format')
        return data[0] + (data[1] << 8) + (data[2] << 16) + (data[3] << 24)

    def _set_u32_value_(self, cmd, value):
        """Generic set for a unsigned32 value.
        
        Args:
            cmd (int): Command byte value
            value (int): Value to be set
        
        Returns:
            int: The desired unsigned32 value
            
        Raises:
            I2CHatResponseException: If response has unexpected format
        """
        data = [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF]
        request = self._request_frame_(cmd, data)
        response = self._transfer_(request, 4)
        if data != response.get_data():
            raise I2CHatResponseException('unexpected format')

    def _request_frame_(self, cmd, data = []):
        """Build request frame, taking care of new frame Id generation.
        
        Args:
            cmd (int): Frame command byte value
            data (List[int]): Frame payload data 
        
        Returns:
            I2CFrame: The new I2CFrame built with specified parameters
            
        """
        return I2CFrame(self._generate_frame_id_(), cmd, data)
    
    def get_address(self):
        """Get the I2C bus address of this object.
        
        Returns:
            int: The I2C address
            
        """
        return self.address

    def get_board_name(self):
        """Send a request over the I2C bus to get the board name.
        
        Returns:
            string: The board name
        
        """
        request = self._request_frame_(CMD_GET_BOARD_NAME)
        response = self._transfer_(request, 25)
        board_name = ''    
        for byte in response.get_data():
            if byte == 0:
                break;
            board_name += chr(byte)
        return board_name

    def get_firmware_version(self):
        """Send a request over the I2C bus to get the firmware version.
        
        Returns:
            string: The firmware version
        
        """
        request = self._request_frame_(CMD_GET_FIRMWARE_VERSION)
        response = self._transfer_(request, 3)
        data = response.get_data()
        return 'v' + chr(data[0] + 0x30) + '.' + chr(data[1] + 0x30)  + '.' + chr(data[2] + 0x30)
    
    def get_status_word(self):
        """Send a request over the I2C bus to get the StatusWord value.
        
        Returns:
            int: The StatusWord value
        
        """
        return self._get_u32_value_(CMD_GET_STATUS_WORD)
    
    def reset(self):
        """Send a request over the I2C bus to reset the I2C-HAT."""
        request = self._request_frame_(CMD_RESET)
        self._transfer_(request, 0, False)
        
    def run(self):
        """This thread feeds the CommunicationWatchdogTimer."""
        
        # clear queue
        while not self.cmd_queue.empty():
            self.cmd_queue.get()
        
        run_flag = True
        feed_period = 0.0
        feed_time = 0.0
        while run_flag:
            if time.time() - feed_time > feed_period:
                try:
                    # feed CWDT and read period
                    feed_time = time.time()
                    feed_period = self.get_cwdt_period() * 0.5
                except Exception as e:
                    # communication lost
                    self.ex_queue.put(e)
                    run_flag = False
            try:
                # start_time = time.time()
                cmd = self.cmd_queue.get(block=True, timeout=0.01)
                if 'stop' in cmd:
                    run_flag = False
                if 'update' in cmd:
                    feed_period = 0 # this forces a read/update of the CWDT period
            except queue.Empty:
                pass
            
    def cwdt_start_feed_thread(self, period=4):
        """Starts the CommunicationWatchdogTimer feed thread and sets the I2C-HAT board CommunicationWatchdogTimer period.
        
        Args:
            period (float): CommunicationWatchdogTimer period in seconds
        
        Raises:
            ValueError: If period is not greather than zero, a period greather than is required zero to enable the CommunicationWatchdogTimer on the I2C-HAT board.
        
        """
        if period <= 0:
            raise ValueError("Period should be greather than zero to enable the CommunicationWatchdogTimer on the I2C-HAT board")
        self.set_cwdt_period(period)
        self.start()
                
    def cwdt_stop_feed_thread(self):
        """Sends comand to stop the CommunicationWatchdogTimer feed thread disables it."""
        
        self.set_cwdt_period(0)
        self.cmd_queue.put('stop')
    
    def cwdt_is_feed_thread_running(self):
        """Gets running status of the CommunicationWatchdogTimer feed thread."""
        
        return self.ex_queue.empty()

    def cwdt_get_period(self):
        """Sends a request over the I2C bus to get the CommunicationWatchdogTimer(CWDT) period.
        
        Returns:
            float: The CommunicationWatchdogTimer period value in seconds
        
        """
        return float(self._get_u32_value_(CMD_CWDT_GET_PERIOD)) / 1000

    def cwdt_set_period(self, value):
        """Sends a request over the I2C bus to set the CommunicationWatchdogTimer(CWDT) period.
        The I2C-HAT CWDT will be disabled if the period is set to zero, a value greather than zero will enable it. 
        
        Args:
            value(float): The CommunicationWatchdogTimer period value in seconds
        
        """
        self._set_u32_value_(CMD_CWDT_SET_PERIOD, int(value * 1000))
        self.cmd_queue.put('update') # command for CWDT thread to update/read the CWDT period
        
class DigitalInputs(I2CHat):
    """Extends the basic functionality by adding the required attributes and methods needed for operating the digital inputs channels.
    
    Note:
        The digital input channels are separated in blocks and labeled Dix.y (x - block number, y - channel
        number). The methods that operate on a single channel use the ``channel label`` (starting from Di1.1)
        or the ``channel index`` (starting from 0) as channel parameter. Methods that operate on all channels can
        return an ``int compact value`` that contains all the digital input channels states from all blocks, one
        channel per bit, for example, Di16 I2C-HAT has 4 input blocks, in this case bit0 of the compact value
        reflects state of Di1.1, bit1 - Di1.2, .. bit4 - Di2.1 an so on...
    
    """
    def __init__(self, channel_labels, address, base_address, board_name):
        """Construct a DigitalInputs object, setting the channel_labels, I2C-HAT address and base_address and the I2C port.
        
        Args:
            channel_labels (List[str]): Labels of digital input channels as written on the board
            address (int): I2C address, valid range is dependent of base_address
            base_address (int): I2C-HAT family base address
            board_name (str): I2C-HAT board name
            
        """
        I2CHat.__init__(self, address, base_address, board_name)
        self.__di_channel_labels__ = channel_labels
        
    def __di_check_channel_index_or_label__(self, channel):
        """Check channel index or channel label to make sure is valid.
        
        Args:
            channel (int or str): The channel index or the channel label as written on the board
            
        Returns:
            int: The valid channel index for internal use
        
        Raises:
            IndexError: If index is not in range
            ValueError: If channel label is invalid, or if channel param is not int or str
        
        """
        if isinstance(channel, int):
            if not 0 <= channel < len(self.__di_channel_labels__):
                raise IndexError('invalid channel index')
            return channel
        elif isinstance(channel, str):
            try:
                return self.__lower_case_labels__(self.__di_channel_labels__).index(channel.lower())
            except ValueError:    
                raise ValueError('invalid channel label')
        else:
            raise ValueError('int or str expected')

    def __di_check_counter_type__(self, counter_type):
        """Make sure counter type is valid.
            
        Args:
            counter_type (int or str) : In case of int the allowed values are 0(falling edge) and 1(rising edge),
                in case of str it should contain words like 'falling' or 'rising', case insesitive  
        
        Returns:
            int: The counter type for internal use
        
        Raises:
            ValueError: If counter type is invalid
        
        """
        if isinstance(counter_type, int):
            if not 0 <= counter_type <= 1:
                raise Exception('counter type out of range')
        elif isinstance(counter_type, str):
            counter_type = counter_type.lower()
            if 'rising' in counter_type:
                counter_type = 1
            elif 'falling' in counter_type:
                counter_type = 0
            else:
                raise ValueError('failed to get counter type from str')
        else:
            raise ValueError('expecting int or str input param')
        return counter_type
        
    def di_get_channel_count(self):
        """Get the number of available digital input channels.
        
        Returns:
            int: The number of available digital input channels
        
        """
        return len(self.__di_channel_labels__)
    
    def di_get_labels(self):
        """Get the board labels of the digital input channels.
        
        Returns:
            List[str]: The labels of the digital input channels
        
        """
        return self.__di_channel_labels__
    
    def di_get_all_states(self, tuple_output = False):
        """Send a I2C request to get all the digital input channels states.
        
        Args:
            ret_tuple (bool): If ``False`` than the int compact value will be returned, if ``True`` than a
                tuple will be returned
        
        Returns:
            int or tuple:
            - The ``int`` compact value, every bit represents a channel state.
            - The ``tuple`` composed of the int compact value and a dict with the channel labels as string
                keys and channel states as bool values.

        """
        states = {}
        value = self._get_u32_value_(CMD_DI_GET_ALL_CHANNEL_STATES)
        if tuple_output == False:
           return value
        else :
            for i in range(0, len(self.__di_channel_labels__)):
                key = self.__di_channel_labels__[i]
                states[key] = ((value >> i) & 0x01) > 0
            return value, states

    def di_get_state(self, channel):
        """Send a I2C request to get specific digital input channel state.
        
        Args:
            channel (int or str): The channel index or the channel label
        
        Returns:
            bool: The channel state
        
        Raises:
            I2CHatResponseException: If the response hasn't got the expected format
        
        """
        channel_index = self.__di_check_channel_index_or_label__(channel)
        request = self._request_frame_(CMD_DI_GET_CHANNEL_STATE, [channel_index])
        response = self._transfer_(request, 2)
        data = response.get_data()
        if len(data) != 2 or data[0] != channel_index:
            raise I2CHatResponseException('unexpected format')
        return data[1] > 0

    def di_get_counter(self, channel, counter_type):
        """Send a I2C request to get the digital input channel counter value for specified counter type.
        
        Args:
            channel (int or str): The channel index or the channel label
            counter_type (int or str) : In case of int the allowed values are 0(falling edge) and 1(rising edge),
                in case of str it should contain words like 'falling' or 'rising', case insesitive  
        
        Raises:
            I2CHatResponseException: If the response hasn't got the expected format
        
        """
        channel_index = self.__di_check_channel_index_or_label__(channel)
        counter_type = self.__di_check_counter_type__(counter_type)
        request = self._request_frame_(CMD_DI_GET_COUNTER, [channel_index, counter_type])
        response = self._transfer_(request, 6)
        data = response.get_data()
        if len(data) != 1 + 1 + 4 or channel != data[0] or counter_type != data[1] :
            raise I2CHatResponseException('unexpected format')
        return data[2] + (data[3] << 8) + (data[4] << 16) + (data[5] << 24)

    def di_reset_counter(self, channel, counter_type):
        """Send a I2C request to reset the digital input channel counter value for specified counter type.
        
        Args:
            channel (int or str): The channel index or the channel label
            counter_type (int or str) : In case of int the allowed values are 0(falling edge) and 1(rising edge),
                in case of str it should contain words like 'falling' or 'rising', case insesitive  
            
        Raises:
            I2CHatResponseException: If the response hasn't got the expected format
        
        """
        channel_index = self.__di_check_channel_index_or_label__(channel)
        counter_type = self.__di_check_counter_type__(counter_type)
        request = self._request_frame_(CMD_DI_RESET_COUNTER, [channel_index, counter_type])
        response = self._transfer_(request, 2)
        data = response.get_data()
        if len(data) != 2 or channel != data[0] or counter_type != data[1] :
            raise I2CHatResponseException('unexpected format')

    def di_reset_all_counters(self):
        """Send a I2C request request to reset all digital input channel counters of all types(falling and
        rising edge).
        
        Raises:
            I2CHatResponseException: If the response hasn't got the expected format
        
        """
        request = self._request_frame_(CMD_DI_RESET_ALL_COUNTERS)
        response = self._transfer_(request, 0)
        data = response.get_data()
        if len(data) != 0:
            raise I2CHatResponseException('unexpected format')

class DigitalOutputs(I2CHat):
    """Extends the basic functionality by adding the required attributes and methods needed for operating
    the digital outputs channels.
    
    Note:
        The relay digital output channels are labeled Rlyx(x - relay number, starting from Rly1).
        The methods that operate on a single channel use the ``channel label`` or the ``channel index``
        (starting from 0) as channel parameter. Methods that operate on all channels use the ``int compact value``
        (all the digital output channels data states encoded as one channel state per bit) or a ``dict`` (all the
        channel labels as string keys and states as bool values) as input parameters or as returned values. 
    
    """
    def __init__(self, channel_labels, address, base_address, board_name):
        """Construct a DigitalOutputs object, setting the I2C-HAT channel_labels, address, base_address and
        the I2C port.
        
        Args:
            channel_labels (List[str]): Labels of digital input channels
            address (int): I2C address, valid range is dependent of base_address
            base_address (int): I2C-HAT family base address
            board_name (str): I2C-HAT board name

        """
        I2CHat.__init__(self, address, base_address, board_name)
        self.__do_channel_labels__ = channel_labels
        
    def __do_check_channel_index_or_label__(self, channel):
        """Check channel index or channel label to make sure is valid.
        
        Args:
            channel (int or str): The channel index or the channel label
            
        Returns:
            int: The valid channel index for internal use
        
        Raises:
            IndexError: If index is not in range
            ValueError: If channel label is invalid, or if channel param is not int or str
        
        """
        if isinstance(channel, int):
            if not 0 <= channel < len(self.__do_channel_labels__):
                raise IndexError('invalid channel index')
            return channel
        elif isinstance(channel, str):
            try:
                return self.__lower_case_labels__(self.__do_channel_labels__).index(channel.lower())
            except ValueError:    
                raise ValueError('invalid channel label')
        else:
            raise ValueError('expecting int or str input')
    
    def __do_check_compact_value__(self, value):
        """Make sure value is in allowed range.
        
        Args:
            value(int): Value should be in range [0, n - 1], where n = number of output channels
            
        Raises:
            ValueError: If value is out of range
        
        """
        if not 0 <= value < (1 << len(self.__do_channel_labels__)):
            raise ValueError("digital output channels value out of range")
        
    def __do_compact_value_to_dict__(self, value):
        """Convert compact value to dict.
        
        Args:
            value(int): Value should be in range [0, n - 1], where n = number of output channels
            
        Returns:
            dict: This has the labels as string keys and states as boolean values
            
        Raises:
            ValueError: If value is out of range
        
        """
        self.__do_check_compact_value__(value)
        states = {}
        for i in range(0, len(self.__do_channel_labels__)):
            key = self.__do_channel_labels__[i]
            states[key] = ((value >> i) & 0x01) > 0
        return states
    
    def __do_check_value_to_be_set__(self, value):
        """Checks if value to be set is valid.
        
        Args:
            value(int or dict): Can be a int compact value in range [0, n - 1], where n = number of output
                channels, or a dict with the channel labels as string keys and states as bool values
            
        Returns:
            int: Compact value where every bit represents a channel state
            
        Raises:
            ValueError: If input value is invalid 
        
        """
        if isinstance(value, int):
            self.__do_check_compact_value__(value)
        elif isinstance(value, dict):
            value = {k.lower():v for k,v in value.items()}  # lower case for input dict keys
            expected_labels = self.__lower_case_labels__(self.__do_channel_labels__).sort()
            labels = value.keys().sort()
            if labels == expected_labels:
                states = value
                value = 0
                for i in range(0, len(self.__do_channel_labels__)):
                    key = self.__do_channel_labels__[i].lower()
                    if states[key] == True:
                        value += 0x01 << i
            else:
                raise ValueError("invalid labels")
        else:
            raise ValueError("int or dict expected")
        return value
        
    def do_get_channel_count(self):
        """Get the number of available digital output channels.

        Returns:
            int: The number of available digital output channels
            
        """
        return self.do_channel_count
    
    def do_get_labels(self):
        """Get the board labels of the digital ouput channels.
        
        Returns:
            List[str]: The labels of the digital output channels
        
        """
        return self.__do_channel_labels__
    
    def do_set_power_on_value(self, value):
        """Send a I2C request to set the PowerOn value for the digital output channels.
        
        Args:
            value(int or dict): Desired PowerOn value, can be a int compact value in range [0, n - 1],
                where n = number of output channels, or a dict with the channel labels as string keys and
                states as bool values
        
        """
        value = self.__do_check_value_to_be_set__(value)
        self._set_u32_value_(CMD_DO_SET_POWER_ON_VALUE, value)
    
    def do_get_power_on_value(self, ret_tuple = False):
        """Send a I2C request to get the PowerOn value for the digital output channels.

        Args:
            ret_tuple (bool): If ``False`` than the int compact value will be returned, if ``True`` than a tuple
                will be returned
        
        Returns:
            int or tuple:
            - The ``int`` compact value, every bit represents a channel state.
            - The ``tuple`` composed of the int compact value and a dict with the channel labels as string keys
                and states as bool values.
        
        """
        value = self._get_u32_value_(CMD_DO_GET_POWER_ON_VALUE)
        if ret_tuple == False:
            return value
        else:
            states = self.__do_compact_value_to_dict__(value)
            return value, states

    def do_set_safety_value(self, value):
        """Send a I2C request to set the Safety value for the digital output channels.
        
        Args:
            value(int or dict): Desired Safety value, can be a int compact value in range [0, n - 1],
                where n = number of output channels, or a dict with the channel labels as string keys and states as bool values
        
        """
        value = self.__do_check_value_to_be_set__(value)
        self._set_u32_value_(CMD_DO_SET_SAFETY_VALUE, value)
    
    def do_get_safety_value(self, ret_tuple = False):
        """Send a I2C request to get the Safety value for the digital output channels.
        
        Args:
            ret_tuple (bool): If ``False`` than the int compact value will be returned, if ``True`` than a tuple will be returned
        
        Returns:
            int or tuple:
            - The ``int`` compact value, every bit represents a channel state.
            - The ``tuple`` composed of the int compact value and a dict with the channel labels as string keys and states as bool values.
            
        """
        value = self._get_u32_value_(CMD_DO_GET_SAFETY_VALUE)
        if ret_tuple == False:
            return value
        else:
            states = self.__do_compact_value_to_dict__(value)
            return value, states
    
    def do_set_all_states(self, value):
        """Send a I2C request to set all the digital output channels states.
        
        Args:
            value(int or dict): Desired digital output channels values, can be a int compact value in range [0, n - 1], where n = number of output channels, or a dict with the channel labels as string keys and states as bool values
        
        """
        value = self.__do_check_value_to_be_set__(value)
        self._set_u32_value_(CMD_DO_SET_ALL_CHANNEL_STATES, value)
    
    def do_get_all_states(self, ret_tuple = False):
        """Sends a I2C request to get all the digital output channels states.
        
        Args:
            ret_tuple (bool): If ``False`` than the int compact value will be returned, if ``True`` than a tuple will be returned
        
        Returns:
            int or tuple:
            - The ``int`` compact value, every bit represents a channel state.
            - The ``tuple`` composed of the int compact value and a dict with the channel labels as string keys and states as bool values.
        
        """
        value = self._get_u32_value_(CMD_DO_GET_ALL_CHANNEL_STATES)
        if ret_tuple == False:
            return value
        else:
            states = self.__do_compact_value_to_dict__(value)
            return value, states
    
    def do_set_state(self, channel, value):
        """Send a I2C request to set a specific digital output channel state.
        
        Args:
            channel (int or str): The channel index or the channel label
            value(bool): Desired state for the digital output channel
            
        Raises:
            I2CHatResponseException: If the response hasn't got the expected format
        
        """
        channel_index = self.__do_check_channel_index_or_label__(channel)
        data = [channel_index, int(value)]
        request = self._request_frame_(CMD_DO_SET_CHANNEL_STATE, data)
        response = self._transfer_(request, 2)
        if data != response.get_data():
            raise I2CHatResponseException('unexpected format')
    
    def do_get_state(self, channel):
        """Send a I2C request to get specific digital output channel state.
        
        Args:
            channel (int or str): The channel index or the channel label
            
        Raises:
            I2CHatResponseException: If the response hasn't got the expected format
        
        """
        channel_index = self.__do_check_channel_index_or_label__(channel)
        request = self._request_frame_(CMD_DO_GET_CHANNEL_STATE, [channel_index])
        response = self._transfer_(request, 2)
        data = response.get_data()
        if len(data) != 2 or data[0] != channel_index:
            raise I2CHatResponseException('unexpected format')
        return data[1] > 0
