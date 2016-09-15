"""
This module contains the I2CHat base class and extensions.
"""
import sys
import time
import smbus
import threading
from ._i2c_frame import I2CFrame
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue

class Command(object) :
    # General Board Commands
    GET_BOARD_NAME = 0x10
    GET_FIRMWARE_VERSION = 0x11
    GET_STATUS_WORD = 0x12
    RESET = 0x13
    
    # Communication WatchDog Commands
    CWDT_SET_PERIOD = 0x14
    CWDT_GET_PERIOD = 0x15
    CWDT_SET_STATE = 0x16
    
    # Digital Inputs Commands
    DI_GET_ALL_CHANNEL_STATES = 0x20
    DI_GET_CHANNEL_STATE = 0x21
    DI_GET_COUNTER = 0x22
    DI_RESET_COUNTER = 0x23
    DI_RESET_ALL_COUNTERS = 0x24
    
    # Digital Outputs Commands
    DO_SET_POWER_ON_VALUE = 0x30
    DO_GET_POWER_ON_VALUE = 0x31
    DO_SET_SAFETY_VALUE = 0x32
    DO_GET_SAFETY_VALUE = 0x33
    DO_SET_ALL_CHANNEL_STATES = 0x34
    DO_GET_ALL_CHANNEL_STATES = 0x35
    DO_SET_CHANNEL_STATE = 0x36
    DO_GET_CHANNEL_STATE = 0x37



class I2CHatResponseException(Exception):
    """Raised when there's a problem with the I2C-HAT response."""

class I2CHat(object):
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
        
        if base_address == None:
            if not 0 <= address <= 127:
                raise ValueError("I2C address should be in range[0, 127]")
        else:
            if address & base_address != base_address:
                raise ValueError("I2C address should be in range[" + hex(base_address) + ", " + hex(base_address + 0x0F) + "]")

        self.__address = address
        self.__frame_id = 0x1F - 1
        
        if board_name != None:
            if self.name not in board_name:
                raise Exception("Unexpected board name: " + self.name + ", expecting: " + board_name)
        
    def __str__(self):
        """Returns the string representation."""
        
        return self.name + " adr: " + hex(self.__address)

    def _generate_frame_id_(self):
        """Generate new frame Id, increments current frame Id, wraps to 0xFF.
        
        Returns:
            int: The new frame Id
            
        """
        self.__frame_id += 1
        self.__frame_id &= 0xFF
        return self.__frame_id
    
    def _transfer_(self, request_frame, response_data_size, response_expected = True, number_of_tries = 5):
        """Tries a number of times to send a request frame and to get a response frame over I2C bus.
        
        Args:
            request_frame (I2CFrame): Request frame to be sent over the I2C bus
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
                    request_data = request_frame.encode()
                    # print request_data
                    
                    # NOTE: write_i2c_block_data function is used to send commands to the I2C-HAT
                    I2CHat.i2c_bus.write_i2c_block_data(self.__address, request_data[0], request_data[1:])
                    
                    if not response_expected:
                        return
                     
                    # NOTE: read_i2c_block_data function sends a i2c_write first, this write has a length of one, and the dummy_byte as payload, this
                    # write will be ignored by the I2C-HAT, after this a i2c_read will be issued, this i2c_read is used for reading the response        
                    dummy_byte = 0xFF
                    expected_response_size = I2CFrame.ID_SIZE + I2CFrame.CMD_SIZE + response_data_size + I2CFrame.CRC_SIZE
                    response_data = I2CHat.i2c_bus.read_i2c_block_data(self.__address, dummy_byte, expected_response_size)
                    # print response_data
                    
                    # build response frame
                    response_frame = I2CFrame(request_frame.id, request_frame.cmd)
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
        data = response.data
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
        if data != response.data:
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
    
    @property
    def address(self):
        """Read I2C bus address.
        
        Returns:
            int: The I2C bus address value.
        
        """
        return self.__address
    
    @property
    def name(self):
        """Send a request over the I2C bus to get the board name.
        
        Returns:
            string: The board name
        
        """
        request = self._request_frame_(Command.GET_BOARD_NAME)
        response = self._transfer_(request, 25)
        board_name = ''    
        for byte in response.data:
            if byte == 0:
                break;
            board_name += chr(byte)
        return board_name

    @property
    def fw_version(self):
        """Send a request over the I2C bus to get the firmware version.
        
        Returns:
            string: The firmware version
        
        """
        request = self._request_frame_(Command.GET_FIRMWARE_VERSION)
        response = self._transfer_(request, 3)
        data = response.data
        return 'v' + chr(data[0] + 0x30) + '.' + chr(data[1] + 0x30)  + '.' + chr(data[2] + 0x30)
    
    @property
    def status(self):
        """Send a request over the I2C bus to get the StatusWord value.
        
        Returns:
            int: The StatusWord value
        
        """
        return self._get_u32_value_(Command.GET_STATUS_WORD)
    
    def reset(self):
        """Send a request over the I2C bus to reset the I2C-HAT."""
        request = self._request_frame_(Command.RESET)
        self._transfer_(request, 0, False)


class I2CHatModule(object):
    
    def __init__(self, i2c_hat, labels = None):
        self._i2c_hat = i2c_hat
        self.__labels = labels
        if labels != None:
            self.__lc_labels = [l.lower() for l in labels]
    
    def _validate_channel_index(self, index):
        if self.__labels == None:
            raise Exception()
        
        label = None
        if isinstance(index, int):
            if not (0 <= index < len(self.__labels)):
                raise ValueError("'" + str(index) + "' is not a valid channel index")
        elif isinstance(index, str):
            label = index
            try:
                index = self.__lc_labels.index(label.lower())
            except ValueError:
                raise ValueError("'" + label + "' is not a valid channel label")
        else:
            raise ValueError("index type is '" + type(index) + "', expecting 'int' or 'str'")
        return index
    
    @property
    def labels(self):
        return self.__labels


class CwdtFeedThread(threading.Thread):
    """Implements basic functionality common to all I2C-HATs."""
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.cmd_queue = queue.Queue()
        self.ex_queue = queue.Queue()
    
    def stop(self):
        """Send command to stop the thread that is feeding the CommunicationWatchdogTimer."""
        self.cmd_queue.put('stop')
        
    def update(self):
        """Send command to thread to update it's copy of CommunicationWatchdogTimer period."""
        self.cmd_queue.put('update')
    
    def run(self):
        """Feeds the CommunicationWatchdogTimer."""
        
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
            
class Cwdt(I2CHatModule):
    
    def __init__(self, i2c_hat):
        I2CHatModule.__init__(self, i2c_hat)
        self.__feed_thread = CwdtFeedThread()
    
    def start_feed_thread(self):
        """Starts the CommunicationWatchdogTimer feed thread and sets the I2C-HAT board CommunicationWatchdogTimer period.
        
        Args:
            period (float): CommunicationWatchdogTimer period in seconds
        
        Raises:
            ValueError: If period is not greather than zero, a period greather than is required zero to enable the CommunicationWatchdogTimer on the I2C-HAT board.
        
        """
        if period < 0:
            raise ValueError("Period should be greather than zero to enable the CommunicationWatchdogTimer on the I2C-HAT board")
        self.set_cwdt_period(period)
        #self.start()
                
    def stop_feed_thread(self):
        """Sends comand to stop the CommunicationWatchdogTimer feed thread disables it."""
        
        self.set_cwdt_period(0)
        self.cwdt_feed_thread.stop()

    @property
    def period(self):
        """Sends a request over the I2C bus to get the CommunicationWatchdogTimer(CWDT) period.
        
        Returns:
            float: The CommunicationWatchdogTimer period value in seconds
        
        """
        return float(self._i2c_hat._get_u32_value_(Command.CWDT_GET_PERIOD)) / 1000

    @period.setter
    def period(self, value):
        """Sends a request over the I2C bus to set the CommunicationWatchdogTimer(CWDT) period.
        The I2C-HAT CWDT will be disabled if the period is set to zero, a value greather than zero will enable it. 
        
        Args:
            value(float): The CommunicationWatchdogTimer period value in seconds
        
        """
        if value < 0:
            raise ValueError("Period should be greather than zero to enable the CommunicationWatchdogTimer on the I2C-HAT board")
        
        self._i2c_hat._set_u32_value_(Command.CWDT_SET_PERIOD, int(value * 1000))
        #self.cwdt_feed_thread.update() # command for CWDT thread to update/read the CWDT period

