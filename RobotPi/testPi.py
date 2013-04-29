import sys
sys.path.insert(0, '/home/eric/Documents/Aracna/WindowsClone')


from RobotPi import *
from PiConstants import POS_READY
from math import *

import copy

'''
Created on Jan 31, 2013

@author: Eric Gold
'''

def sinWave():
    r = 300
    p = .5
    f = lambda t: (sin(t/p)*r+r,40,770,40,770,40,770,40)
    return f
   
if __name__ == '__main__':
    robot = RobotPi()
    f = sinWave()
    print "Beginning run"
    robot.run(f,runSeconds=50)
    
