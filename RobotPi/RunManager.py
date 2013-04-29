import math, pdb, sys
import random
from datetime import datetime
from copy import copy
from time import sleep
from RobotQuadratot import RobotQuadratot, RobotFailure
from SineModel import SineModel5
from Neighbor import Neighbor
from util import prettyVec
from wii.WiiTrackClient import WiiTrackClient
from wii.WiiTrackFastClient import WiiTrackFastClient



def getLogPosString(wiiTrack):
    position,age = wiiTrack.getPosAge()
    if position is None:
        return '-1 -1 %f' % age
    else:
        return ' '.join([str(x) for x in position + [age]])



class RunManager:
    '''Manage runs..'''

    def __init__(self):
        self.robot = RobotQuadratot(commandRate = 40, loud = False)
        self.statesSoFar = set()  # Keeps track of the states tested so far
        
    def run_robot(self, currentState):
        '''
        Runs the robot with currentState parameters and returns the
        distance walked.  If currentState is a function, calls that
        function instead of passing to a motion model.
        '''

        if hasattr(currentState, '__call__'):
            # is a function
            motionModel = currentState
        else:
            # is a parameter vector
            model = SineModel5()
            motionModel = lambda time: model.model(time,
                                                   parameters = currentState)

        # Reset before measuring
        self.robot.readyPosition()

        wiiTrack = WiiTrackClient("localhost", 8080)
        beginPos = wiiTrack.getPosition()
        if beginPos is None:
            # Robot walked out of sensor view
            self.manual_reset('Robot has walked outisde sensor view.  Please place back in center and push enter to continue.')
            print 'Retrying last run'
            return self.run_robot(currentState)

        if not self.robot.shimmy():
            self.manual_reset('Shimmy failed.  Fix and restart.')
            return self.run_robot(currentState)

        try:
            self.robot.run(motionModel, runSeconds = 9, resetFirst = False,
                           interpBegin = 1, interpEnd = 2)
        except RobotFailure as ee:
            print ee
            override = self.manual_reset('Robot run failure.  Fix something and push enter to continue, or enter a fitness to manually enter it.')
#            print 'Retrying last run'
#            return self.run_robot(currentState)
            try:
                manualDist = float(override)
                return manualDist
            except ValueError:
                print 'Retrying last run'
                return self.run_robot(currentState)
            

        endPos = wiiTrack.getPosition()
        if endPos is None:
            # Robot walked out of sensor view
            override = self.manual_reset('Robot has walked outisde sensor view.  Please place back in center\nand push enter to retry or enter manual fitness override to skip.')
            try:
                manualDist = float(override)
                return manualDist
            except ValueError:
                print 'Retrying last run'
                return self.run_robot(currentState)

        distance_walked = self.calculate_distance(beginPos, endPos)
        #print '        walked %.2f' % distance_walked

        if not self.robot.shimmy():
            ret = distance_walked / 2.0
            print 'Shimmy failed, returning %.2f instead of %.2f' % (ret, distance_walked)
            self.manual_reset('Shimmy failed at end, reset robot if necessary and push enter to continue.')
            return ret
        else:
            return distance_walked
            
    def run_function_and_log(self, motionFunction, runSeconds, timeScale = 1, logFilename = None):
        '''
        Runs the robot with the given motion function from 0 to
        runSeconds, logging time and position to logFileName
        '''

        # Reset before measuring
        self.robot.readyPosition()

        wiiTrack = WiiTrackFastClient("localhost", 8080)
        sleep(.5)
        beginPos = wiiTrack.getPosition()
        if beginPos is None:
            # Robot walked out of sensor view
            self.manual_reset('Robot has walked outisde sensor view.  Please place back in center and push enter to retry.')
            raise Exception

        if not self.robot.shimmy():
            print 'Shimmy failed :('
            #self.manual_reset('Shimmy failed.  Fix and push enter to retry.')
            #####HACK !!!!!!
            #raise Exception

        ff = open(logFilename, 'a')

        try:
            self.robot.run(motionFunction, runSeconds = runSeconds, resetFirst = False,
                           interpBegin = 1, interpEnd = 2, logFile = ff,
                           extraLogInfoFn = lambda: getLogPosString(wiiTrack))
        except RobotFailure as ee:
            ff.close()
            print ee
            override = self.manual_reset('Robot run failure.  Fix something and push enter to retry.')
            raise Exception
        ff.close()
        
        endPos = wiiTrack.getPosition()
        if endPos is None:
            # Robot walked out of sensor view
            override = self.manual_reset('Robot has ended outisde sensor view.  Please place back in center\nand push enter to retry.')
            raise Exception

        distance_walked = self.calculate_distance(beginPos, endPos)
        print 'Total Distance: %.2f' % distance_walked

        #if not self.robot.shimmy():
        #    letter = None
        #    while not letter in ('r', 'k'):
        #        letter = self.manual_reset('Shimmy failed at end of run, retry or keep [r/k]?')
        #    if letter == 'r':
        #        raise Exception
    
    def log_start(self, extra=None):
        logFile = open('log.txt', 'a')
        logFile.write('\n# RunManager log started at %s\n' % datetime.now().ctime())
        if extra is not None:
            logFile.write(extra)
        logFile.close()
        
    def log_write(self, string, newline=True):
        logFile = open('log.txt', 'a')
        if newline:
            string += '\n'
        logFile.write(string)
        logFile.close()
        
    def log_results(self, logInfo, currentDistance):
        """Writes to log file that keeps track of tests so far"""
        logFile = open('log.txt', 'a')

        #if hasattr(currentState, '__call__'):
        #    stats = 'function call run'
        #else:
        #    stats = ' '.join([repr(xx) for xx in currentState])
        if isinstance(logInfo, list):
            stats = ' '.join([repr(xx) for xx in logInfo])
        elif isinstance(logInfo, basestring):
            stats = logInfo
        else:
            raise Exception('Do not know how to log %s' % repr(logInfo))

        logFile.write(stats + ", " + str(currentDistance) + "\n")
        logFile.close()

    def calculate_distance(self, begin, end):
        """
        Calculates how far the robot walked given the beginning and ending
        (x, y) coordinates.
        """
        return math.sqrt(pow((end[0] - begin[0]), 2) + pow((end[1] - begin[1]), 2))

    def do_many_runs(self, strategy, ranges, limit = None):
        if limit is None:
            limit = 10000

        self.log_start(strategy.logHeader())

        for ii in xrange(limit):
            currentState, logInfo = strategy.getNext()
            
            print
            #if hasattr(currentState, '__call__'):
            #    print 'Iteration %2d: %s' % (ii+1, logStr),
            #else:
            #    print 'Iteration %2d params' % (ii+1), prettyVec(currentState),
            paramStr = logInfo if isinstance(logInfo, basestring) else prettyVec(logInfo)
            print 'Iteration %2d: %s' % (ii+1, paramStr)
            sys.stdout.flush()

            # Check if this state is new, and possibly skip it
            #if tuple(currentState) in self.statesSoFar:
            #    print '*** Duplicate iteration!'
            #    # Skip only if using random hill climbing. In other words,
            #    # comment this line out if using gradient_search:
            #    #currentState = neighborFunction(bestState)
            #    continue

            currentDistance = self.run_robot(currentState)
            #currentDistance = input('Distance walked? ')

            #self.statesSoFar.add(tuple(currentState))

            #print '        walked %.2f' % currentDistance
            print '%.2f' % currentDistance

            strategy.updateResults(currentDistance)

            #print '        best so far', prettyVec(strategy.bestState), '%.2f' % strategy.bestDist  # Prints best state and distance so far

            self.log_results(logInfo, currentDistance)



    def explore_dimensions(self, initialState, ranges, pointsPerDim = 10, repetitions = 3):
        '''For the given vector, vary each parameter separately.

        Arguments:
        initialState -- where to start
        ranges       -- parameter ranges
        pointsPerDim -- number of points along each dimension
        repetitions  -- how many measurements to make of each position
        '''

        nDimensions = len(initialState)

        self.log_start()
        self.log_write('RunManager.explore_dimensions, centered at %s' % prettyVec(initialState))

        for dimension in range(nDimensions):
            self.log_write('RunManager.explore_dimensions: dimension %d' % dimension)

            points = Neighbor.uniform_spread(ranges, initialState, dimension, number = pointsPerDim, includeOrig = True)

            for ii,point in enumerate(points):

                for tt in range(repetitions):
                    print 'Iteration dimension %d, point %d, trial %d' % (dimension, ii, tt), prettyVec(point),
                    sys.stdout.flush()
                    self.log_write('%d, %d, %d, ' % (dimension, ii, tt), newline=False)
                    
                    dist = self.run_robot(point)

                    print '%.2f' % dist
                    self.log_results(point, dist)


    def manual_reset(self, st):
        print st
        return raw_input()
