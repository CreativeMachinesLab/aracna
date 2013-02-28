#! /usr/bin/env python

import os, dynamixel, time, random
import datetime
import pdb

from Motion import positionIt
from RobotParams import MIN_INNER, MAX_INNER, MIN_OUTER, MAX_OUTER, MIN_CENTER, MAX_CENTER
from Robot import initialize



def main():
    net, actuators = initialize()

    for actuator in actuators:
        actuator.moving_speed = 90
        actuator.synchronized = True
        actuator.torque_enable = True
        actuator.torque_limit = 1000
        actuator.max_torque = 1000

    print 'Starting in 1 sec... ',
    time.sleep(1)
    print 'go.'

    time0 = datetime.datetime.now()
    while True:
        timeDiff = datetime.datetime.now() - time0
        seconds  = timeDiff.seconds + timeDiff.microseconds/1e6

        goal = positionIt(seconds)

        print 'At %3.3f, commanding:' % seconds,

        for ii,actuator in enumerate(actuators):
            gg = goal[ii]
            gg = max(min(gg, servoMax), servoMin)
            actuator.goal_position = gg
            print round(gg, 3),
        net.synchronize()
        print

        #for actuator in actuators[:8]:
        #    actuator.read_all()
        #    time.sleep(0.01)
        #for actuator in actuators[:8]:
        #    print actuator.cache[dynamixel.defs.REGISTER['Id']], actuator.cache[dynamixel.defs.REGISTER['CurrentPosition']]
        time.sleep(.025)

    

        
        
if __name__ == '__main__':
    main()
