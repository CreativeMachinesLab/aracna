#! /usr/bin/env python

import sys
from SineModel import SineModel5
from RunManager import RunManager
from Motion import scaleTime



USAGE = '''Usage:
./jimRuns.py <gait type> <gait specifier>

Example:
  ./jimRuns.py -SineModel5 "400 2.0936276321011063 0.40692057680126537 0.70168527110547441 0.29694496659796576"'''



def usage():
    print USAGE
    sys.exit(1)



def main():
    MIN_ARGS = 4
    
    if len(sys.argv) >= MIN_ARGS:
        if len(sys.argv) > 2 and sys.argv[1] == '-SineModel5':
            sineModel5Params = [eval(xx) for xx in sys.argv[2].split()]
            print 'Using SineModel5 with params: ', sineModel5Params
            
            motionFunction = lambda time: SineModel5().model(time,
                                                             parameters = sineModel5Params)
        elif len(sys.argv) > 2 and sys.argv[1] == '-neatFiltFile':
            raise Exception('not yet')
            filtFile = sys.argv[2]
            currentState = None
        else:
            usage()

        runName = sys.argv[3]

        if len(sys.argv) > 4:
            timeScale = float(sys.argv[4])
        else:
            timeScale = 1
    else:
        usage()

    motionFunctionScaled = scaleTime(motionFunction, timeScale)

    runman = RunManager()

    print 'Run name is:', runName
    
    for ii in range(1):
        print
        print 'Iteration', ii
        runman.run_function_and_log(motionFunctionScaled, runSeconds = 10, timeScale = 1, logFilename = 'log_%s.txt' % runName)
        #try:
        #except:
        #    print '*** Something failed, skipping'



if __name__ == '__main__':
    main()
