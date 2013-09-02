'''

@date: 24 September 2010

'''

"""
Given the time since the robot started running (type float?), returns a
list of length 9 that denotes the position each motor should be at
at the given time. Motors 0, 2, 4, and 6 are the lower/base motors;
1, 3, 5, and 7 are the outer motors; 8 is the motor in the center of the
robot. Motor positions are of type int, [0, 1023], 512 being lying flat.

"""

import math
from numpy import interp



def lInterp(time, theDomain, val1, val2):
    ret = []
    for ii in range(len(val1)):
        ret.append(interp([time], theDomain, [val1[ii], val2[ii]])[0])
    return ret



def scaleTime(function, scale):
    fscale = float(scale)
    return lambda time: function(time * fscale)



def positionIt(time):
    # Make the outer arm go up and down, limited range until we figure
    # out range of robot. Starts out lying flat.

    if (time < 5):
        inner = float(interp([time], [0, 5], [512, 800])[0])
        outer = float(interp([time], [0, 5], [512,  40])[0])

        position = [inner, outer, inner, outer, inner, outer, inner, outer, 512]
        position = [inner, outer, 512, 512, inner, outer, 512, 512, 512]

    elif (time < 10):
        inner = float(interp([time-5], [0, 5], [800, 512])[0])
        outer = float(interp([time-5], [0, 5], [ 40, 150])[0])

        position = [inner, outer, inner, outer, inner, outer, inner, outer, 512]
        position = [inner, outer, 512, 512, inner, outer, 512, 512, 512]

    else:

        assert False
        #outerMotor = int(round(512 + (238 * abs(math.sin(time)))))  # TODO: Scale time correctly?
        outerMotor = int(round(512 + (238 * (math.sin(time)))))  # TODO: Scale time correctly?

        position = [512, outerMotor, 512, outerMotor, 512, outerMotor, 512,
                        outerMotor, 512]

    position = [int(round(xx,0)) for xx in position]
    return position
