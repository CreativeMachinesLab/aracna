#! /usr/bin/env python

'''
Just walks.
'''

import sys
import argparse
from SineModel import SineModel5
from RunManager import RunManager
from Robot import *
from Strategy import *



def main(args):
    if args.filt:
        filtFile = args.filt
        strategy = FileStrategy(filtFile = filtFile)
        motionFunction, logInfo = strategy.getNext()
    elif args.sine:
        sineModel5Params = [eval(xx) for xx in args.sine.split()]
        print 'Using SineModel5 with params: ', sineModel5Params
        motionFunction = lambda time: SineModel5().model(time,
                                                         parameters = sineModel5Params)
    else:
        # args.gait

        strategy = TimedFileStrategy(posFile = args.gait)
        motionFunction, logInfo = strategy.getNext()



    # Old defaults    
    #filtFile = '../results/hyperneatTo20gens_101/neat_110115_175446_00014_008_filt'
    #filtFile = '../results/hyperneatTo20gens_101/neat_110115_175446_00004_007_filt'
    #filtFile = '/home/team/results/kyrre_1.txt.cut'

    #strategy = FileStrategy(filtFile = filtFile)



    #runman = RunManager()
    #runman.do_many_runs(strategy, SineModel5.typicalRanges)

    #timeScale = .3
    print 'scaling by', args.scale
    motionFunctionScaled = scaleTime(motionFunction, args.scale)

    robot = Robot()
    robot.run(motionFunctionScaled, runSeconds = 10, resetFirst = False,
              interpBegin = 2, interpEnd = 2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Commands the robot to walk')

    parser.add_argument('--gait', '-g', metavar = 'GAITFILE', type = str,
                        help='Gait file (with time as column 0)')
    parser.add_argument('--filt', '-f', metavar = 'FILTFILE', type = str,
                        help='Filt file (without time column)')
    parser.add_argument('--sine', '-s', metavar = 'SINEPARAMS', type = str,
                        help='Command gait with given SINEPARAMS. Give as a single space-separated string, like --sine "1 2 3 4 5".')
    parser.add_argument('--scale', '-t', metavar = 'TIMESCALE', type = float, default = 1,
                        help='Run gait scaled by the specified amount (default: 1)')

    args = parser.parse_args()

    hasGait = bool(args.gait)
    hasFilt = bool(args.filt)
    hasSine = bool(args.sine)
    if not hasGait and not hasFilt and not hasSine:
        parser.error('Must specify --gait, --filt, or --sine.')
    if sum([hasGait, hasFilt, hasSine]) > 1:
        parser.error('Must specify only one of {--gait, --filt, --sine}.')        

    main(args)
