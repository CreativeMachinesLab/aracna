#!/usr/bin/env python

"""

// This software was written and developed by Scott Ferguson.
// The current version can be found at http://www.forestmoon.com/Software/.
// Comments and suggestions are encouraged and can be sent to mailto:contact@forestmoon.com?subject=Software.
// This free software is distributed under the GNU General Public License.
// See http://www.gnu.org/licenses/gpl.html for details.
// This license restricts your usage of the software in derivative works.

The original C# version of this software was converted to Python on behalf of the
Pi Robot Project at http://www.pirobot.org

"""

"""
Dynamixel AX-12+ Module
"""
__version__ =  '1.0'

from dynamixel import Dynamixel
from dynamixel_network import DynamixelNetwork
from echo_stream import EchoStream
from serial_stream import SerialStream
from defs import ERROR_STATUS, BAUD_RATE, REGISTER, INSTRUCTION, \
                 STATUS_RETURN_LEVEL