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

Dynamixel unit test module

"""

import unittest

import dynamixel
import dynamixel_network
import event_handler
import stream
import defs

class MockStream( stream.Stream ):
    """ Mock Stream implementation """
    
    def __init__( self, data = "" ):
        """ Constructor """
        stream.Stream.__init__( self )
        self.ibuffer = data
        self.obuffer = ""
    def append(self, data ):
        """ Append data to incoming stream """
        self.ibuffer += data
    
    def flush( self ):
        """ Flush the stream"""
        pass
    def read( self, count ):
        """ Reads from a given stream
        
        count - number of bytes to read

        Returns a string of length count or less
        """
        if len( self.ibuffer ) > 0:
            to_read = min( count, len( self.ibuffer ) )
            buf = self.ibuffer[:to_read]
            self.ibuffer = self.ibuffer[to_read:]
            return buf
        else:
            raise stream.TimeoutException()
    def write( self, buf ):
        """ Writes to a stream
        
        buf - a string
        """
        self.obuffer += buf
    def write_byte( self, byte ):
        """ Write a single byte
        
        byte - a string """
        return self.write( byte )
    def read_byte( self ):
        """ Read a single byte

        Returns a string """
        return self.read( 1 )
    def get_read_timeout( self ):
        """ Get the Read Timeout """
        return 0        
    def set_read_timeout( self, value ):
        """ Set the Read Timeout """
        pass        
    def get_write_timeout( self ):
        """ Get the Write Timeout """
        return 0        
    def set_write_timeout( self, value ):
        """ Set the Write Timeout """
        pass        
    
    read_timeout = property( get_read_timeout, set_read_timeout )
    write_timeout = property( get_write_timeout, set_write_timeout )
        
def make_packet( ident, err, data, length = None ):
    """ Create a packet for testing """
    ## 
    ## Status packet returned from dynamixel serve
    ## 0     1     2     3     4     5     5 + data-length
    ## 0xFF  0xFF  id    len   err/inst   data  checksum
    if length == None:
        length = len( data ) + 2
    obuffer = '\xFF\xFF' + chr( ident ) + chr( length ) + chr( err )
    chksum = 0
    chksum = (chksum + ident) & 0xFF
    chksum = (chksum + length) & 0xFF
    chksum = (chksum + err) & 0xFF
    for byte in data:
        chksum = (chksum + byte) & 0xFF
        obuffer += chr( byte )
    chksum = (~chksum) & 0xFF
    obuffer += chr( chksum )
    return obuffer
    

class EventHandlerTest(unittest.TestCase):
    """ Test cases for the EventHandler """
    def setUp( self ):
        """ Setup """      
        self.is_called = False
        self.is_called = False
        self.is_called_2 = False
        self.obj = None
        self.obj2 = None
        self.sender = None
        self.sender2 = None
        
        
    def test_add( self ):
        """ Test a single add and call"""
        self.handler = event_handler.EventHandler()
        self.handler += self.do_call
        self.clear()
        self.handler( self, None )
        self.assertTrue( self.is_called )
        self.assertTrue( self.sender == self)
        self.assertTrue( self.obj == None )
        
    def test_multi_add( self ):
        """ Test Multi-add and call """
        self.handler = event_handler.EventHandler()
        self.handler += self.do_call
        self.handler += self.do_call2
        self.clear()        
        self.handler( self, None )
        self.assertTrue( self.is_called and self.is_called_2)
        self.assertTrue( self.sender == self)
        self.assertTrue( self.obj == None )
        self.assertTrue( self.sender2 == self)
        self.assertTrue( self.obj2 == None )

    def test_sub( self ):
        """ Test Multi-add and call """
        self.handler = event_handler.EventHandler()
        self.handler += self.do_call
        self.handler += self.do_call2
        self.handler -= self.do_call2
        self.clear()        
        self.handler( self, None )
        self.assertTrue( self.is_called and not self.is_called_2)
        self.assertTrue( self.sender == self)
        self.assertTrue( self.obj == None )
        
    def clear( self ):
        """ Reset test """
        self.is_called = False
        self.is_called_2 = False
        self.obj = None
        self.obj2 = None
        self.sender = None
        self.sender2 = None

    def do_call( self, sender, obj ):
        """ Target method """
        self.is_called = True
        self.sender = sender
        self.obj = obj
    
    def do_call2( self, sender, obj ):
        """ Target method """
        self.is_called_2 = True
        self.sender2 = sender
        self.obj2 = obj

class DynamixelInterfaceTest(unittest.TestCase):
    """ Test cases for the DynamixelInterface """
    def setUp( self ):      
        """ Reset the interface """
        self.reset()
    def reset( self ):
        """ Reset the interface """
        self.has_errors = False
        self.error_codes = []
        
    def test_read_packet( self ):
        "Ensure read packet reads the appropriate data"
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        
        self.reset()
        # verify packet w/o errors    
        packet = make_packet(1, 0, [0, 1, 2, 3] )
        istream.append( packet )
        
        (ident, data) = iface.read_packet()
        self.assertTrue( ident == 1)
        self.assertTrue( data == [0, 1, 2, 3] )
        self.assertTrue( self.has_errors == False )
        # verify packet w/ errors        
        self.reset()
        packet = make_packet(1, defs.ERROR_STATUS.InputVoltage, [0, 1, 2, 3] )
        istream.append( packet )
        (ident, data) = iface.read_packet()
        self.assertTrue( ident == 1)
        self.assertTrue( data == [0, 1, 2, 3] )
        self.assertTrue( self.has_errors == True )

    def test_read_ping( self ):
        "Test ping also tests await packet and write instruction"
        
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        
        # test for no response
        self.reset()   
        # verify ping failed
        self.assertFalse( iface.ping( 1 ) )
        chksum = (~(1 + 2 + 1)) & 0xFF
        # verify outgoing packet is well formed
        self.assertEqual( istream.obuffer, "\xFF\xFF\x01\x02\x01\xfb" )
        # create mock ping response
        # create an ignored packet
        istream.append( make_packet( 0, 0, []))
        # create the ping response
        istream.append( make_packet( 1, 0, []))
        # ping again and verify ping came back
        self.assertTrue( iface.ping( 1 ) )

    def test_scan_ids(self ):
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        
        # test for no response
        self.reset()   
        # verify ping failed
        istream.append( make_packet( 1, 0, []))
        self.assertTrue( iface.scan_ids( 1, 10 ) == [1] )

    def test_read_data( self ):
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        
        # test for no response
        self.reset()   
        # verify read data
        istream.append( make_packet( 1, 0, [0x20]))
        result = iface._read_data( 1, 0x2b, 1 )
        self.assertEqual( istream.obuffer, ''.join((map(chr,[0xff,0xff,0x1,0x4,0x2,0x2b,0x1,0xcc]))))
        self.assertEqual( result, [0x20])
        
    def test_read_register( self ):
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        
        # test for no response
        self.reset()   
        # verify read data
        istream.append( make_packet( 1, 0, [0x20]))
        result = iface.read_register( 1, 0x2b)
        self.assertEqual( istream.obuffer, ''.join((map(chr,[0xff,0xff,0x1,0x4,0x2,0x2b,0x1,0xcc]))))
        self.assertEqual( result, 0x20)       

    def test_read_registers( self ):
        """ Full range test for read registers"""
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        self.reset()   
        istream.append( make_packet( 1, 0, [0x20]))
        # dummy packet full range of eeprom
        istream.append( make_packet( 1, 0, range(0,50) ))
        result = iface.read_registers( 1, defs.REGISTER.ModelNumber, defs.REGISTER.Punch)
        # assert only the number of registers are returned
        self.assertEqual( len( result ), len(defs.REGISTER.values()) )
        # TODO possibly add test for values of registers in future
    
    def test_write_data( self ):
        """ Test writing data to eeprom """
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        
        self.reset()   
        # verify write as per Spec
        iface.write_data( dynamixel_network.DynamixelInterface.BROADCAST_ID, 0x3,[0x1], False )
        self.assertEqual( istream.obuffer, ''.join((map(chr,[0xff,0xff,0xfe,0x4,0x3,0x3,0x1,0xf6]))))
    def test_write_register( self ):
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        
        self.reset()   
        
        # verify write as per variant of spec
        iface.write_register( 0x1, 0x3,0x1, True )
        self.assertEqual( istream.obuffer, ''.join((map(chr,[0xff,0xff,0x1,0x4,0x4,0x3,0x1,0xf2]))))
                
    def test_action( self ):
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        
        self.reset()   
        # verify outgoing action command
        iface.action(  )
        self.assertEqual( istream.obuffer, ''.join((map(chr,[0xff,0xff,0xfe,0x2,0x5,0xfa]))))

    def test_sync_write( self ):
        istream = MockStream()
        iface = dynamixel_network.DynamixelInterface( istream )
        iface.dynamixel_error += self.error_handler
        
        self.reset()   
        # verify outgoing action command
        iface.sync_write(0x1e, 4, [0X00, 0X10, 0X00, 0X50, 0X01, 
                                   0X01, 0X20, 0X02, 0X60, 0X03, 0X02,  
                                   0X30,  0X00,  0X70,  0X01,  0X03,  
                                   0X20,  0X02,  0X80, 0X03])
        expected = ''.join((map(chr, [0XFF, 0XFF, 0XFE, 0X18, 0X83, 0X1E, 
                                      0X04, 0X00, 0X10, 0X00, 0X50, 0X01, 
                                      0X01, 0X20, 0X02, 0X60, 0X03, 0X02,  
                                      0X30,  0X00,  0X70,  0X01,  0X03,  
                                      0X20,  0X02,  0X80, 0X03, 0X12])))
        self.assertEqual( istream.obuffer,  expected)

                        
    
    def error_handler(self, sender, (ident, error_status)):
        """ Error handler hook """
        self.has_errors = True
        self.error_codes.append( error_status )


class DynamixelNetwork(unittest.TestCase):
    """ Test cases for the DynamixelNetwork """
    def setUp( self ):      
        """ Reset the interface """
        self.reset()
    def reset( self ):
        """ Reset the interface """
        self.has_errors = False
        self.error_codes = []
    def test_scan(self):
        """ Test a scan of registers"""
        istream = MockStream()
        iface = dynamixel_network.DynamixelNetwork( istream )
        iface.dynamixel_error += self.error_handler
        self.reset()   
        # ping response
        istream.append( make_packet( 1, 0, []))
        # read register response
        istream.append( make_packet( 1, 0, [1,2,3,4]))
        # scan for one servo
        iface.scan( 1, 1 )
        # get by id
        dyn = iface[1]
        # assert initial read registers are ok
        self.assertEqual( dyn.moving_speed, 1027 )
        self.assertEqual( dyn.goal_position, 513 )
        self.assertFalse(self.has_errors )
        
    def test_reset(self):
        """ Test a reset call"""
        istream = MockStream()
        iface = dynamixel_network.DynamixelNetwork( istream )
        iface.dynamixel_error += self.error_handler
        self.reset()   
        # ping response
        istream.append( make_packet( 1, 0, []))
        # read register response
        istream.append( make_packet( 1, 0, [1,2,3,4]))
        # scan for one servo
        iface.scan( 1, 1 )
        # get by id
        dyn = iface[1]
        istream.obuffer=''
        istream.append( make_packet(0x01,0x00,[]))
        dyn.reset(1)
        self.assertEqual( istream.obuffer, ''.join(map(chr,[0xff,0xff,0x1,0x2,0x6,0xf6])))
        self.assertFalse(self.has_errors )        
        
    def test_set_attr(self):
        """ Test setting an attribute"""
        istream = MockStream()
        iface = dynamixel_network.DynamixelNetwork( istream )
        iface.dynamixel_error += self.error_handler
        self.reset()   
        # ping response
        istream.append( make_packet( 1, 0, []))
        # read register response
        istream.append( make_packet( 1, 0, [1,2,3,4]))
        # scan for one servo
        iface.scan( 1, 1 )
        # get by id
        dyn = iface[1]
        dyn.synchronized = False
        istream.obuffer=''
        istream.append( make_packet(0x01,0x00,[]))
        dyn.goal_position = 0x3FF
        self.assertEqual( istream.obuffer, ''.join(map(chr,[0xFF, 0xFF, 0x01, 0x05, 0x03, 0x1E, 0xFF, 0x03, 0xD6]))) 
        self.assertFalse(self.has_errors )

    def test_get_attr(self):
        """ Test getting an attribute"""
        istream = MockStream()
        iface = dynamixel_network.DynamixelNetwork( istream )
        iface.dynamixel_error += self.error_handler
        self.reset()   
        # ping response
        istream.append( make_packet( 1, 0, []))
        # read register response
        istream.append( make_packet( 1, 0, [1,2,3,4]))
        # scan for one servo
        iface.scan( 1, 1 )
        # get by id
        dyn = iface[1]
        dyn.synchronized = False
        istream.obuffer=''
        istream.append( make_packet(0x01,0x00,[0x20,0x00]))
        value = dyn.current_position
        self.assertEqual( value, 0x20) 


                        
    def error_handler(self, sender, (ident, error_status)):
        """ Error handler hook """
        self.has_errors = True
        self.error_codes.append( error_status )
            
if __name__ == '__main__':
    unittest.main()
