#!/usr/bin/env python
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

Echo Stream module

"""

import stream
import event_handler

class EchoStream( stream.Stream ):
    """A wrapper for a stream class that also has a event handler for echoing
    """
    def __init__( self, strm  ):
        """ Constructor
        strm - stream to wrap 
        """
        stream.Stream.__init__( self )
        self.writing = False
        self.echo_byte = 0
        self._stream = strm
        self.echo = event_handler.EventHandler()

    def echo_write( self, byte ):
        """ Call the echo event handler for a write """
        self.writing = True
        self.echo_byte = byte
        self.echo( self, None )

    def echo_read( self, byte ):
        """ Call the echo event handler for a read """
        self.writing = False
        self.echo_byte = byte
        self.echo( self, None )

    def flush( self ):
        """ Flush the wrapped stream """
        self._stream.Flush()

    def read( self,  count ):
        """ Read up to count bytes from the stream

        count - maximum number of bytes to read 
        """
        buf = self._stream.Read( count )
        for char in buf:
            self.echo_read( char )
        return buf

    def write( self, buf ):
        """ Write the given buffer to the wrapped stream
        
        buf - string or list of bytes to write """
        if isinstance( buf, list ):
            buf = ''.join( [chr( c ) for c in buf] )
        for char in buf:
            self.echo_write( char )
        self._stream.write( buf )     
   
    def read_byte( self ):
        """ Read a byte from the wrapped stream 
        """
        return self.read( 1 )

    def write_byte( self, byte ):
        """ Write a byte to the wrapped stream
        byte - one character string
        """
        self.write( byte )

    def get_read_timeout( self ):
        """ Get the read timeout """
        return self._stream.read_timeout

    def set_read_timeout( self, value ):
        """ Set the read timeout """
        self._stream.read_timeout = value

    def get_write_timeout( self ):
        """ Get the write timeout """
        return self._stream.read_timeout

    def set_write_timeout( self, value ):
        """ Set the write timeout """
        self._stream.read_timeout = value
    
