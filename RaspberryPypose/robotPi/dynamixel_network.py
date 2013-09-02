#!/usr/bin/env python2.6
"""
This is a Python version of the ForestMoon Dynamixel library originally
written in C# by Scott Ferguson.

The Python version was created by Patrick Goebel (mailto:patrick@pirobot.org)
for the Pi Robot Project which lives at http://www.pirobot.org.

The original license for the C# version is as follows:

This software was written and developed by Scott Ferguson.
The current version can be found at http://www.forestmoon.com/Software/.
This free software is distributed under the GNU General Public License.
See http://www.gnu.org/licenses/gpl.html for details.
This license restricts your usage of the software in derivative works.

* * * * * 

Dynamixel Network module

"""

import defs
import stream
import event_handler
import time
import dynamixel

class DynamixelInterface(object):
    """ Interface to Dynamixel CM-5 """
    BROADCAST_ID = 254
    def __init__(self, strm):
        """ Constructor
        stream - an open Stream
        """
        self._stream = strm
        self.dynamixel_error = event_handler.EventHandler()
        self._in_error_handler = False
        self._error_count_1st_header_byte = 0
        self._error_count_2nd_header_byte = 0
        self._error_count_3rd_header_byte = 0
        self._error_count_invalid_length = 0
        self._error_count_unexpected_ident = 0
        self._error_count_unexpected_length = 0
        self._response_total_elapsed = 0
        self._response_max_elapsed = 0
        self._response_count = 0

    @staticmethod
    def error_text(error_type):
        """ Returns a list of the textual representation 
        of the ERROR_STATUS value """
        text = []
        for key, value, description in defs.ERROR_STATUS.items():
            if (error_type & value) != 0:
                text.append(description)
        return text

    @staticmethod
    def register_length(reg):
        """ Returns the register length"""
        if reg in [defs.REGISTER.ModelNumber, 
                   defs.REGISTER.CWAngleLimit, defs.REGISTER.CCWAngleLimit,
                   defs.REGISTER.MaxTorque, defs.REGISTER.DownCalibration,
                   defs.REGISTER.UpCalibration, defs.REGISTER.GoalPosition,
                   defs.REGISTER.MovingSpeed, defs.REGISTER.TorqueLimit,
                   defs.REGISTER.CurrentPosition, defs.REGISTER.CurrentSpeed,
                   defs.REGISTER.CurrentLoad, defs.REGISTER.Punch]:
            return 2
        else:
            return 1
    @staticmethod
    def register_reserved( addr ):
        """ Test to see if a register is reserved """
        return addr in [0xA,0x13]

    
    def enter_toss_mode(self):
        """ Try to put the CM-5 into Toss Mode 

        Returns true on success
        """
        state = 0
        buf = ""
        save_timeout = self._stream.read_timeout
        while state < 5:
            try:
                if state == 0:
                    # send a CR and look for a response from a CM-5 
                    # in manage mode
                    self._stream.write_byte('\r')
                    state = 1
                elif state == 1:
                    # look for a response from a CM-5
                    buf += self._stream.read_byte() 
                    if len(buf) >= 3 and buf[-3:] == "[CM":
                        # a CM-5 that has just been put into manage mode
                        # will respond to the first CR with a version 
                        # string, e.g. "[CM-5 Version 1.15]" lengthen the
                        # timeout because the CM-5 will scan for Dynamixels
                        self._stream.read_timeout = 750
                        state = 2
                    if len(buf) >= 3 and buf[-3:] == "[CI":
                        # a CM-5 in manage mode that has already scanned 
                        # will respond with a prompt string containing the
                        # ID of the current Dynamixel, e.g. "[CID:001(0x01)]"
                        # restore the shorter timeout
                        self._stream.read_timeout = save_timeout
                        state = 3
                elif state == 2:
                    buf += self._stream.read_byte() 
                    if len(buf) >= 3 and buf[-3:] == "[CI":
                        # a CM-5 in manage mode that has already scanned 
                        # will respond with a prompt string containing the
                        # ID of the current Dynamixel, e.g. "[CID:001(0x01)]"
                        # restore the shorter timeout
                        self._stream.read_timeout = save_timeout
                        state = 3
                elif state == 3:
                    buf += self._stream.read_byte()
                    if len(buf) >= 2 and buf[-2:] == "] ":
                        # found the end of the CID prompt
                        # put the CM-5 in Toss Mode
                        self._stream.write_byte('t')
                        self._stream.write_byte('\r')
                        state = 4
                elif state == 4:
                    buf += self._stream.read_byte()
                    if len(buf) >= 9 and buf[-9:] == "Toss Mode":
                        # found the "Toss Mode" response verification
                        # we're good to go
                        state = 5
            except stream.TimeoutException:
                self._stream.read_timeout = save_timeout
                if state > 1:
                    raise Exception("CM-5 detected but not in Managed Mode")
                break
        print "%d : %d" % (self._stream.read_timeout,
                           self._stream.write_timeout)
        return state == 5

    def dump_statistics(self):
        """ Return a list of textual statistics
        
        Returns a list of strings
        """
        
        result = []
        if self._response_count != 0:
            avg_response_time = self._response_total_elapsed / \
                float(self._response_count)
            result.append("Average ms per Dynamixel response: %.1F" % \
                               (avg_response_time))
            result.append("Maximum ms per Dynamixel response: %d" % \
                           (self._response_max_elapsed))
        if self._error_count_1st_header_byte > 0:
            result.append("1st Header Byte: %d" % \
                               (self._error_count_1st_header_byte))
        if self._error_count_2nd_header_byte > 0:
            result.append("2nd Header Byte: %d" % \
                           (self._error_count_2nd_header_byte))
        if self._error_count_3rd_header_byte > 0:
            result.append("3rd Header Byte: %d" % \
                               (self._error_count_3rd_header_byte))
        if self._error_count_invalid_length > 0:
            result.append("Invalid Length: %d" % \
                               (self._error_count_invalid_length))
        if self._error_count_unexpected_ident > 0:
            result.append("Unexpected ID: %d" % \
                               (self._error_count_unexpected_ident))
        if self._error_count_unexpected_length > 0:
            result.append("Unexpected Length: %d" % \
                               (self._error_count_unexpected_length))
        return result

    def read_packet(self):
        """Read packet

        Returns tuple (packet type identifier, packet)
        """

        retry = True
        # read packet is only ever called immediately following a write 
        # instruction (sent packet ) so we can use this opportunity to 
        # time the response from dynamixel 
        start_time = time.time()

        # set an invalid id for error return cases
        ident = 0xFF
        ## 
        ## Status packet returned from dynamixel serve
        ## 0     1     2     3     4     5     5 + data-length
        ## 0xFF  0xFF  id    len   err   data  checksum

        # first header byte
        byte = ord(self._stream.read_byte())

        # update statistics
        end_time = time.time()
        elapsed_time = (end_time - start_time)
        self._response_total_elapsed += elapsed_time
        self._response_count += 1
        self._response_max_elapsed = max(self._response_max_elapsed, \
                                              elapsed_time)
        
        if byte != 0xFF:
            self._error_count_1st_header_byte += 1
            return (ident, None)

        # 2nd header byte
        byte = ord(self._stream.read_byte())
        if byte != 0xFF:
            self._error_count_2nd_header_byte += 1
            return (ident, None)
        
        # id or third header
        byte = ord(self._stream.read_byte())
        if byte == 0xFF:
            self._error_count_3rd_header_byte += 1
            byte = ord(self._stream.read_byte())

        ident = byte

        # packet length includes data-length + 2
        length = ord(self._stream.read_byte()) 

        if length < 0:
            self._error_count_invalid_length += 1

        error_status = ord(self._stream.read_byte())
        data = ""
        # remove error and checksum bytes
        length -= 2
        if length > 0:
            while length > 0:
                buf = self._stream.read(length)
                length -= len(buf)
                data += buf
        data = [ord(byte) for byte in data]
        # XXX below code/comment was in the original code
        # get the checksum byte
        # CONSIDER: Could validate the checksum and reject the packet
        checksum = ord(self._stream.read_byte())
        # let anyone listing know about any errors reported in the packet
        # use the InErrorHandler flag to avoid recursion from the 
        # user's handler
        if error_status != 0 and not self._in_error_handler:
            self._in_error_handler = True
            self.dynamixel_error(self, (ident, error_status))
            self._in_error_handler = False
        return (ident, data)

    def await_packet(self, ident, length):
        """ Read a packet validing the id and length
        Retries until a valid packet is founnd

        ident - packet identifier
        length - packet length
        """
        if ident == DynamixelInterface.BROADCAST_ID:
            return None
        while True:
            (pid, data) = self.read_packet()
            plen = 0
            # validate the id and length
            if data:
                plen = len(data)
            if pid == ident and plen == length:
                return data
            if pid != ident:
                self._error_count_unexpected_ident += 1
            if plen != length:
                self._error_count_unexpected_length += 1
            
    def write_instruction(self, ident, instruction, params=None):
        """Send a command packet instruction 

        ident - the id of the destination dynamixel or BROADCAST_ID to send to all
        ins - instruction to send
        param - parameters to send (list of bytes) or None
        
        """
        cmd = []
        #
        # command packet sent to Dynamixel servo:
        # 0      1      2    3        4            4 + data-length
        # [0xFF] [0xFF] [id] [length] [...data...] [checksum]
        #
        # header bytes & id        
        if params == None:
            params = []
        if not isinstance(params, list):
            raise Exception( "Params must be a list")
        cmd.append(0xFF)
        cmd.append(0xFF)
        cmd.append(ident)
        # length is data-length + 2
        cmd.append(len(params) + 2)        
        cmd.append(instruction)
        # parameter bytes
        cmd = cmd + params
        # checksum
        chksum = 0
        for byte in cmd[2:]:
            chksum += byte
            chksum &= 0xFF
        chksum = (~chksum) & 0xFF
        cmd.append(chksum)
        # convert from bytes to a string
        cmd = ''.join([chr(c & 0xFF) for c in cmd])
        # write the string
        self._stream.write(cmd)
        self._stream.flush()

    def ping(self, ident):
        """ Check the presence of a specific dynamixel on the network
        
        ident - identifier of a dynamixel to ping
        """
        self.write_instruction(ident, defs.INSTRUCTION.Ping)
        try:
            self.await_packet(ident, 0)
        except stream.TimeoutException:
            return False
        return True

    def _read_data(self, ident, start_address, count):
        """Read register data from a Dynamixel.
        
        id - the id of the dynamixel to read
        start_address - the starting register to read from
        count - the number of bytes to read

        Note:
        Some logical registers are one byte long and some are two.
        The count is for the number of bytes, not the number of registers.
        """
        
        return_packet = None
        retry = True
        # the start address and count from the parameters of the command
        # packet
        cmd = [start_address, count]
        while retry:
            self.write_instruction(ident, defs.INSTRUCTION.ReadData, cmd)
            try:
                return_packet = self.await_packet(ident, count)
                retry = False
            except stream.TimeoutException:
                print "TIMEOUT accessing servo ID: %d" % (ident)
                self._stream.flush()
        return return_packet

    def read_register(self, ident, register):
        """Read the value of one logical register
        
        ident - the id of the Dynamixel to read
        reg - logical register to read
        
        Returns the integer value of the logical register

        Note:
        this takes into account the byte length of the logical 
        register"""
        data = self._read_data(ident, register,
                                DynamixelInterface.register_length(register))
        if len(data) == 1:
            return data[0]
        return (data[1] << 8) + data[0]

    def read_registers(self, ident, first_register, last_register):

        """ Read the values of multiple logical registers

        ident - the id of the dynamixel
        first_register - first logical register to read/address
        last_register - the last logical register to read/address
        
        returns:
        a list of register values

        Note:
        this function takes into account the byte length of the 
        logical register
        """
        # this function was cleaned up for clarity
        
        register_length = DynamixelInterface.register_length(last_register)
        # calc number of bytes as delta based on addresses
        byte_count = last_register + register_length - first_register
       
        # read data from servo
        data = self._read_data(ident, first_register, byte_count)
        if len( data ) != byte_count:
            raise Exception( "Data received (%d) shorter than requested data (%d)" % (len(data), byte_count))
        # resulting values
        result = []

        regs = defs.REGISTER.values()
        regs.sort()
        # index of first and last register
        first = regs.index( first_register )
        last = regs.index( last_register )
        
        # offset to read from
        offset = 0
        for i in xrange( first, last + 1 ):
            reg = regs[ i ]
            # calc the length; note this skips reserved registers
            length = DynamixelInterface.register_length( reg )
            # calc offset
            offset  = reg - first_register
            # reconstruct the value
            if length == 1:
                result.append(data[ offset ])
            else:
                result.append((data[ offset + 1] << 8) + \
                                   data[offset])
        return result

    def write_data(self, ident, start_address, params, deferred):
        """Write register data
        
        ident - dynamixel to write to
        start_address - the starting register to write to
        params - list of bytes to be written
        deferred - if true the dynamixel will store the request 
                   until the action  command is received
                   """
        if not isinstance(params, list):
            raise Exception( "Params must be a list")
        cmd = []
        cmd.append(start_address)
        cmd = cmd + params
        inst = None
        if deferred:
            inst = defs.INSTRUCTION.RegWrite
        else:
            inst = defs.INSTRUCTION.WriteData
        self.write_instruction(ident, inst, cmd)
        if not deferred:
            self.await_packet(ident, 0)

    def write_register(self, ident, register, value, deferred):
        """Write data to one logical register
        
        ident - dynamixel to write to
        register - the register to write to
        value - the integer value to write
        deferred - if true the dynamixel will store the request until the action 
                   command is received
                   """
        if not isinstance( value, int):
            raise ValueError( "Expected value to by an integer")
        if DynamixelInterface.register_length(register) == 1:
            self.write_data(ident, register, [ value ], deferred)
        else:
            values = [ value & 0xFF, (value >> 8) & 0xFF ]
            self.write_data(ident, register, values, deferred)

    def action(self):
        """Broadcasta an action instruction for all dynamixels 
        with deferred writes pending

        """
        self.write_instruction(DynamixelInterface.BROADCAST_ID,
                                 defs.INSTRUCTION.Action, None)
    
    def sync_write(self, start_address, number_of_dynamixels, params):
        """ Write to multiple registers on multiple Dynamixels 
        using one instruction.

        start_address = starting register to write to
        number_of_dynamixels - the number of dynamixels being addressed
        params - the data being written including the id and data for each
        dynamixel

        Note:
        This function provides the most efficient way of updating the same 
        registers on each of many different Dynaixels with different values 
        at the same time.

    The length of the 'parms' data will determine the number of sequential 
        registers being written to.

    For each Dynamixel the 'parms' data must include the id followed 
        by the register data.
        """
        if len(params) % number_of_dynamixels != 0:
            raise ValueError("Dynamixel SyncWrite params length error")
        length = len(params) / number_of_dynamixels - 1
        cmd = []
        cmd.append(start_address)
        cmd.append(length)
        cmd = cmd + params
        self.write_instruction(DynamixelInterface.BROADCAST_ID,
                                 defs.INSTRUCTION.SyncWrite, cmd)


    def scan_ids(self, start_id, end_id):
        """Determine which ids are present
        start_id - first id to start (must be less than end_id)
        end_id - last id to search (0-253)

        Returns a list of ids on the network

        Scanning for all possible IDs (0 thru 254) can be time consuming.
        So if the range can be constrained to predetermined values it can 
        speed up the process.

        throws ValueError on arguments out of range
        """
        if end_id > 253 or end_id < 0:
            raise ValueError("end_id must be 0 to 233")
        if start_id > end_id or start_id < 0:
            raise ValueError("start_id must be 0 to end_id")
        ids = []
        for ident in xrange(start_id, end_id + 1):
            if self.ping(ident):
                ids.append(ident)
        return ids
    
class DynamixelNetwork (DynamixelInterface):
    """ An abstract model of a Dynamixel network represented as a 
    collection of Dynamixel objects.
    """

    def __init__(self, strm):
        """ The Constructor
        stream - the stream to exchange command and status packets with 
        the dynamixel network
        """
        DynamixelInterface.__init__(self, strm)
        self._stopped = False
        self._dynamixel_map = {}

    def __getitem__(self, ident):
        """ array access to the dynamixels, indexed by id
        
        ident - id to retrieve

        returns the dynamixel object with that id or None if none 
        present on the network
        """
        if ident in self._dynamixel_map:
            return self._dynamixel_map[ ident ]
        else:
            return None

    def get_dynamixels(self):
        """ A list of dynamixels present on the network """
        return self._dynamixel_map.values()

    dynamixels = property(get_dynamixels)

    def scan(self, start_id, end_id):
        """
        Scan the network to discover the Dynamixels present.

        start_id - the id for the start of the search
        end_id - the id for the end of the search

        Note:
        function builds an internal list of Dynamixels present on the network.
        Typically call this function only once per DynamixelNetwork instance
        it will rebuild the list and create new Dynamixel instances to fill it,
        any previously retrieved Dynamixels.
        for all possible IDs (0 thru 254) can be time consuming.
        So if the range can be constrained to predetermined values it can 
        speed up the process.
        """
        self._dynamixel_map = {}
        ids = self.scan_ids(start_id, end_id)
        for ident in ids:
            self._dynamixel_map[ ident ] = dynamixel.Dynamixel(ident, self)


    def _get_stopped(self):
        """Get if the dynamixels are stopped"""
        return self._stopped

    def _set_stopped(self, value):
        """Stop all dynamixels and prevent further movement
        activity for the dynamixels that are synchronized
        """
        if value:
            for (ident, servo) in self._dynamixel_map.items():
                servo.stop()
            self.synchronize()
        self._stopped = value

    stopped = property(_get_stopped, _set_stopped)

    def synchronize(self):
        """Send GoalPosition and MovingSpeed data for all 
        Dynamixels in Synchronized mode.

        This function collects all the changed GoalPosition and 
        MovingSpeed data that has been stored for each Dynamixel 
        flagged as Synchronized and sends it all out at once
        using a SyncWrite instruction.

        If the network is 'Stopped', no data is sent.
        """
        data = None
        count = 0
        for (ident, servo) in self._dynamixel_map.items():
            if servo.changed:
                if not self.stopped:
                    count += 1
                    if count == 1:
                        data = []
                    data.append(servo.id)
                    data.append(servo.goal_position & 0xFF)
                    data.append(servo.goal_position >> 8)
                    data.append(servo.moving_speed & 0xFF)
                    data.append(servo.moving_speed >> 8)
                    servo.changed = False
        if count != 0:
            self.sync_write(defs.REGISTER.GoalPosition, count, data)


    def broadcast_register(self, reg, value):
        """Write the value of one logical register to all Dynamixels.
        reg - The logical register to write.
        value - The integer value to write.
        
        Updates the cache value of the register for all Dynamixels.
        """
        for (ident, servo) in self._dynamixel_map.items():
            servo[ reg ] = value
        self.write_register(DynamixelInterface.BROADCAST_ID, reg,
                             value, False)

    def dynamixel_id_change(self, servo, new_id):
        """ Prepare for a pending change in the Id of a dynamixel
        
        Note: you must change the dynamixel object to new_id
        """
        if new_id in self._dynamixel_map:
            raise ValueError("Dynamixel Id %d already in use" % (new_id))
        del self._dynamixel_map[ servo.id ]
        self._dynamixel_map[ new_id ] = servo
