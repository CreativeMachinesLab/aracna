#! /usr/bin/env python

'''
Moves the given servos in a sine wave motion.
'''

import sys
import argparse
from numpy import *

from Robot import Robot



def sineMotion(ids, commandRate, offset, amp, freq):
    robot = Robot(expectedIds = ids, commandRate = commandRate, cropMethod = None)

    nIds = len(ids)
    motionFunction = lambda time: [offset + amp * sin(2 * pi * time * freq) for ii in range(nIds)]

    robot.run(motionFunction, runSeconds = 10, interpBegin = 1, resetFirst = False)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Commands a sine motion pattern for the given motors for 10 seconds.')
    parser.add_argument('--rate', metavar = 'RATE', type = float, default = 40,
                        help='Frequency at which to command the servos, in Hz (default: 40)')
    parser.add_argument('--freq', metavar = 'FREQUENCY', type = float, default = .5,
                        help='Frequency of the sine wave (default: .5)')
    parser.add_argument('--amp', metavar = 'AMPLITUDE', type = float, default = 200,
                        help='Amplitude of the sine wave (default: 200)')
    parser.add_argument('--offset', type = float, default = 512,
                        help='Baseline of the sine wave (default: 512)')
    parser.add_argument('ids', metavar='servoID', type = int, nargs='+',
                        help='IDs of the servos to command')
    args = parser.parse_args()
    
    sineMotion(ids = args.ids,
               commandRate = args.rate,
               offset = args.offset,
               amp = args.amp,
               freq = args.freq)

