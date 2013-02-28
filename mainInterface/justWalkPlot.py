#! /usr/bin/env python

'''
Just walks.
'''

import sys
import pdb
import time
from SineModel import SineModel5
from Robot import Robot
from Strategy import *
from wii.WiiTrackFastClient import WiiTrackFastClient



def savePosition(wiiTrack, posAgeList):
    position,age = wiiTrack.getPosAge()
    print 'savePosition:', position, age
    if position is None:
        return '-1 -1 %f' % age
    else:
        posAgeList.append((position, age))
        print len(posAgeList)
        return ' '.join([str(x) for x in position + [age]])



def main22():
    if len(sys.argv) > 2 and sys.argv[1] == '-filt':
        filtFile = sys.argv[2]
        strategy = FileStrategy(filtFile = filtFile)
        motionFunction, logInfo = strategy.getNext()
    elif len(sys.argv) > 2 and sys.argv[1] == '-sine':
        sineModel5Params = [eval(xx) for xx in sys.argv[2].split()]
        print 'Using SineModel5 with params: ', sineModel5Params
        motionFunction = lambda time: SineModel5().model(time,
                                                         parameters = sineModel5Params)
    else:
        #filtFile = '../results/hyperneatTo20gens_101/neat_110115_175446_00014_008_filt'
        filtFile = '../results/hyperneatTo20gens_101/neat_110115_175446_00004_007_filt'
        strategy = FileStrategy(filtFile = filtFile)
        motionFunction, logInfo = strategy.getNext()
    	

    
    #runman = RunManager()
    #runman.do_many_runs(strategy, SineModel5.typicalRanges)

    #timeScale = .3
    #motionFunctionScaled = scaleTime(motionFunction, timeScale)
    wiiTrack = WiiTrackFastClient("localhost", 8080)
    time.sleep(.5)
    position,age = wiiTrack.getPosAge()
    if age is None:
        raise Exception('Could not get position from wiiTrack.')

    robot = Robot(loud = True)
    bucket = []

    def foo():
        savePosition(wiiTrack, bucket)

    robot.run(motionFunction, runSeconds = 8, resetFirst = False,
              interpBegin = 2, interpEnd = 2, extraLogInfoFn = foo)
    
    print bucket    


    
if __name__ == '__main__':
    main22()
