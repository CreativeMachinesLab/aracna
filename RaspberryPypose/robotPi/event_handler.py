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

Event handler module

"""


class EventHandler( object ):
    """ Analog to C#'s event handler """
    def __init__( self ):
        """ Default constructor """
        self._observers = set( [] )

    def __call__( self, sender, args ):
        """ Call all observering methods """
        for observer in self._observers:
            observer( sender, args )

    def __iadd__( self, listener ):
        """ Add a listener """
        self._observers.add( listener )
        return self

    def __isub__( self, listener ):
        """ Remove a listener """
        self._observers.remove( listener )
        return self   