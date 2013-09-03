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

An implementation of the Steam interface using pyserial
"""

try:
    # PySerial Module
    import serial
except:
    print "This module requires the pySerial to be installed \
to use the Serial Stream"


from stream import Stream, TimeoutException

class SerialStream( Stream ):
    """ A stream using the pyserial interface """
    def __init__( self, **kw ):
        """ Default constructor
        Creates and opens a serial port

        **kw - keyword arguments to pass into a pySerial serial port
        """
        Stream.__init__( self )
        self.port = serial.Serial( **kw )
        #self.port.open() # Seems to cause "permission denied" with PySerial 2.x
    def flush( self ):
        """ Flush the port """
        self.port.flush()
    def read( self, count ):
        """ Read up to count bytes 

        count - maximum number of bytes to read
        throws TimeoutException if read returns empty or None
        """
        buf = self.port.read( count )
        if len( buf ) == 0:
            raise TimeoutException()
        return buf
            
    def write( self, buf ):
        """ Write buf to the port 
        buf - string or list of bytes
        """
        if isinstance( buf, list ):
            buf = ''.join( [chr( c ) for c in buf] )
        self.port.write( buf )
    def get_read_timeout( self ):
        """ Get the read timeout """
        return self.port.timeout 
    def set_read_timeout( self, value ):
        """ Set the read timeout """
        self.port.timeout = value
    def get_write_timeout( self ):
        """ Get the write timeout """
        return self.port.writeTimeout 
    def set_write_timeout( self, value ):
        """ Set the write timeout """
        self.port.writeTimeout = value
    def close(self):
        self.port.close()
