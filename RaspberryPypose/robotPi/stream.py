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
Stream interface

"""

class Stream( object ):
    """ Stream Interface class"""
    def flush( self ):
        """ Flush the stream"""
        raise NotImplementedError()
    def read( self, count ):
        """ Reads from a given stream
        
        count - number of bytes to read

        Returns a string of length count or less
        """
        raise NotImplementedError()
    def write( self, buf ):
        """ Writes to a stream
        
        buf - a string
        """
        raise NotImplementedError()
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
        raise NotImplementedError()        
    def set_read_timeout( self, value ):
        """ Set the Read Timeout """
        raise NotImplementedError()        
    def get_write_timeout( self ):
        """ Get the Write Timeout """
        raise NotImplementedError()        
    def set_write_timeout( self, value ):
        """ Set the Write Timeout """
        raise NotImplementedError()        
    read_timeout = property( get_read_timeout, set_read_timeout )
    write_timeout = property( get_write_timeout, set_write_timeout )

class TimeoutException( Exception ):
    """ Timeout exception """
    def __init__( self, msg=None ):
        """ Default constructor """
        Exception.__init__( self )
        self.msg = msg
    def __str__( self ):
        """ Get the string representation of the Exception """
        return repr( self )
    def __repr__( self ):
        """ Get the object representation of the Exception """
        return "TimeoutError( %r )" % (self.msg)