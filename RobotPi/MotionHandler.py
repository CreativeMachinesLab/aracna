'''
Created on Mar 13, 2012

@author: Eric Gold
'''

import bisect
from types import FunctionType
from operator import itemgetter
from numpy import interp

def lInterp(time, theDomain, val1, val2):
    ret = []
    for ii in range(len(val1)):
        ret.append(interp([time], theDomain, [val1[ii], val2[ii]])[0])
    return ret

class PiecewiseMotionFunction:
    '''PiecewiseMotionFunction is a container for storing a motion function.
    A motion function is a mapping of times to servo positions.
    For those that are mathematically inclined, the times are the domain and the
    position tuples are the range of this function.
    '''
    
    def __init__(self, numServos, times, positions, linInterp=True, cycle=True):
        '''Constructor
        numSeros --- the number of motors this function is designed for
        times --- a list of floating-point values (usually starting from 0) of
                  times that the function is defined on. The units should be
                  seconds.
        positions --- a list of tuples of positions for each servo at the
                      specified time. The index of each tuple corresponds with
                      the time from the times array. Note: to if cycle is true,
                      the last position tuple must equal the first position.
        linInterp --- use linear interpolation to smooth the motion function. If
                    false, gets the vector of the nearest time-point.
        cycle --- allow the motion function to "wrap around." If a time is given
                that exceeds the domain of the function, then use modulo
                division to find the proper time. If false, just use the last
                time available.
        '''
        self.numServos = numServos
        self.maxTime = times[-1]
        
        if len(times) != len(positions):
            raise Exception("times has length " + str(len(times)) + " but positions has length " + str(len(positions)))
        self.motionFnct = []
        for i in range(len(times)):
            if len(positions[i]) != numServos:
                raise Exception("time " + times[i] + " has wrong number of servos.")
            else: self.motionFnct.append((times[i],positions[i]))
        self.motionFnct = sorted(self.motionFnct, key=itemgetter(0))
        
        self.linInterp = linInterp
        self.cycle = cycle
    
    def getPos(self, time):
        '''Returns the position vector at the specified time.'''
        time = time % self.maxTime if self.cycle else time
        i0 = self.__findLE(time)
        i1 = i0 + 1 if i0 < len(self.motionFnct) - 1 else i0
        diff0 = abs(time - self.motionFnct[i0][0])
        diff1 = abs(time - self.motionFnct[i1][0])
        if self.linInterp:
            total = diff0 + diff1
            w0 = diff1 / total
            w1 = diff0 / total
            vect = [0] * self.numServos
            for i in range(self.numServos):
                vect[i] = w0 * self.motionFnct[i0][1][i] + w1 * self.motionFnct[i1][1][i]
            return tuple(vect)
        else:
            if diff0 <= diff1: return self.motionFnct[i0][1]
            else: return self.motionFnct[i1][1]
    
    def __findLE(self, x):
        '''Find the index of the rightmost item less than or equal to x'''
        a = [t for (t,_) in self.motionFnct]
        i = bisect.bisect_right(a, x)
        if i < len(a):
            return i - 1
        raise ValueError

class SmoothMotionFunction:
    def __init__(self, startFnct, endFnct, seconds, frequency, numServos):
        '''Initialize a smooth motion function as a piecewise motion function.
        startFnct --- a function of the time in seconds
        endFnct --- a function of the time in seconds
        seconds --- the duration of a single motion cycle
        frequency --- the precision to use for this function (in Hz)
        numServos --- the number of servos this function is designed for'''
        
        seconds = float(seconds)
        frequency = float(frequency)
        
        self.motionFnct = []
        self.times = []
        self.duration = seconds
        self.frequency = frequency
        t = 0.0
        while t < seconds:
            posS = startFnct(t) if isinstance(startFnct, FunctionType) else startFnct
            posE = endFnct(t) if isinstance(endFnct, FunctionType) else endFnct
            goal = lInterp(t, [0, seconds], posS, posE)
            self.motionFnct.append(goal)
            self.times.append(t)
            
            t += 1 / frequency
        
        t = seconds
        posS = startFnct(t) if isinstance(startFnct, FunctionType) else startFnct
        posE = endFnct(t) if isinstance(endFnct, FunctionType) else endFnct
        goal = lInterp(t, [0, seconds], posS, posE)
        self.motionFnct.append(goal)
        self.times.append(t)
        
if __name__ == "__main__":
    mf = PiecewiseMotionFunction(2,[0,1,2,3,4],[(0.,0.),(0.,1.),(1.,2.),(3.,2.),(0.,0.)])
    print str(mf.getPos(7.5))