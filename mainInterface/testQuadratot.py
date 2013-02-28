from Robot import *
from RobotConstants import POS_READY
from math import *

import copy

'''
Created on Jan 31, 2013

@author: Eric Gold
'''

def sinWaveMotion():
    '''Returns a sine wave motion function'''
    r = 300
    sinF = lambda t : int(r * (sin(t)) + r)
    cosF = lambda t : int(r * (cos(t)) + r)
    f1   = lambda t : int(r * (sin(t*10)) + r)
    f2   = lambda t : int(r * (sin(t) + cos(t)) + r)
    #f = lambda t: (sinF(t), sinF(t), sinF(t), sinF(t), f2(t), f1(t), cosF(t), sinF(t), f2(t))
    
    temp = copy.copy(POS_READY)
    temp[0] = cosF
    f = lambda t: temp
    return f

def sinWave():
    r = 300
    p = 5
    f = lambda t: (sin(t/p)*r+r,40,770,40,770,40,770,40,512)
    return f
   
if __name__ == '__main__':
    robot = Robot()
    f = sinWave()
    print "Beginning run"
    robot.run(f,runSeconds=50)
    
