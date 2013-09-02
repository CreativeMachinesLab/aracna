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

Enumeration 

Analog to the enum type in other languages

"""

class Enumeration( object ):
    """ An Enumeration Class """
    def __init__( self, enums ):
        """ Default Constructor
        mapping -- (key, value[, description) tuple key must be a string 
                   should start with a capital letter"""
        self._values = {}
        self._descriptions = {}
        values = set()
        for enum in enums:
            key, value, description = None, None, None
            # deconstruct parameters
            if len( enum ) == 2:
                key, value = enum
            else:
                key, value, description = enum
            # check for duplicate data
            if value in values:
                raise Exception( "Duplicate Value in Enumeration" )
            # store persistant data
            self._values[ key ] = value
            self._descriptions[ key ] = description
            # add to value set to ensure non-duplicate values
            values.add( value )
        # populate the attributes of the class
        for key, value in self._values.items():
            object.__setattr__( self, key, value )
    def __getitem__( self, key ):
        """ Lookup an item based on a string 
        key -- string

        Returns the value associated with the key
        Throws KeyError
        """
        return self._values[ key ]
    def items( self ):
        """ Get items in the enumeration
        
        Returns all members of the Enumeration in the form of 
        a (key, value, description) tuple list
        """
        result = []
        for key in self._values:
            description = None
            value = self._values[ key ]
            if key in self._descriptions:
                description = self._descriptions[ key ]
            result.append( (key, value, description) )
        return result
    def key( self, value ):
        """ Get the key associated with a given value
        Returns key as a string
        Throws KeyError if key is not associated with a value
        """
        for key, val in self._values.items():
            if val == value:
                return key
        raise KeyError( "Cannot find associated key in enumeration" )
    def description( self, key=None, value=None ):
        """ Get the description associated with the key or value
        key -- key as a string 
        value -- value 
        
        Note: only key or value may be specified
        
        Returns description string or None
        throws LookupError if neither key or value are specified
        throws LookupError if both key and value are specified
        throws KeyError if associated description could not be found
        """
        if value == None and key == None:
            raise LookupError( "Must provide either a key or a value" )
        if value != None and key != None:
            raise LookupError( "Must provide either a key or a value" )
        # if value is specified lookup the associated key
        if value != None:
            key = self.key( value )
        # find the key
        for key in self._descriptions:
            return self._descriptions[ key ]
        raise KeyError( "Cannot find associated description" )
    def keys( self ):
        """ Return the keys in the enumeration as a list of strings """
        return self._values.keys()
    def values( self ):
        """ Return the values in the enumeration as a list of values """
        return self._values.values()
    def __iter__( self ):
        """ Return the iterator for the Enumeration """
        return iter( self._values )
    def __len__( self ):
        """ Return the number of elements in the enumeration """
        return len( self._values )
    def __repr__( self ):
        return "Enumeration( %r )" % (self.items())
