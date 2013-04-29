import os
from datetime import datetime
from time import sleep
from types import FunctionType
from copy import copy
from numpy import array

import dynamixel
from Motion import lInterp, scaleTime

'''
Much inspiration taken from http://code.google.com/p/pydynamixel/
'''



'''Min and max values for the QuadraTot robot, based on some tests.

Note that these values will avoid collisions only for each servo
individually.  More complex collisions are still possible given
certain vectors of motor position.
'''

from ConstantsQuadratot import *



import inspect
def fileLine():
    """Returns the current line number in our program."""
    #print dir(inspect.currentframe().f_back.f_back)
    #print inspect.currentframe().f_back.f_back.f_code.co_filename

    return inspect.currentframe().f_back.f_back.f_code.co_filename, inspect.currentframe().f_back.f_back.f_lineno
    #return inspect.getouterframes( inspect.currentframe() )[1].f_back.f_lineno




class RobotFailure(Exception):
    pass



class RobotQuadratot():
    ''''''

    def __init__(self, silentNetFail = False, expectedIds = None, commandRate = 40,
                 loud = False, skipInit = False):
        '''Initialize the robot.
        
        Keyword arguments:

        silentNetworkFail -- Whether or not to fail silently if the
                             network does not find all the dynamixel
                             servos.

        nServos -- How many servos are connected to the robot,
                   i.e. how many to expect to find on the network.

        commandRate -- Rate at which the motors should be commanded,
                   in Hertz.  Default: 40.
        '''

        # The number of Dynamixels on the bus.
        self.expectedIds   = expectedIds if expectedIds is not None else range(9)
        self.nServos       = len(self.expectedIds)
        self.silentNetFail = silentNetFail

        self.sleep = 1. / float(commandRate)
        self.loud  = loud

        #if self.nServos != 9:
        #    pass
        #    #raise Exception('Unfortunately, the RobotQuadratot class currently assumes 9 servos.')

        # Default baud rate of the USB2Dynamixel device.
        self.baudRate = 1000000

        if not skipInit:
            self.initServos()


    def initServos(self):
        # Set your serial port accordingly.
        if os.name == "posix":
            possibilities = ['/dev/ttyUSB0', '/dev/ttyUSB1']
            portName = None
            for pos in possibilities:
                if os.path.exists(pos):
                    portName = pos
            if portName is None:
                raise Exception('Could not find any of %s' % repr(possibilities))
        else:
            portName = "COM11"

        serial = dynamixel.SerialStream(port = portName,
                                        baudrate = self.baudRate,
                                        timeout = 1)
        self.net = dynamixel.DynamixelNetwork(serial)

        #print 'Prescan...'
        #print self.net.get_dynamixels()

        print "Scanning for Dynamixels...",
        self.net.scan(min(self.expectedIds), max(self.expectedIds))

        self.actuators   = []
        self.actuatorIds = []

        for dyn in self.net.get_dynamixels():
            print dyn.id,
            self.actuatorIds.append(dyn.id)
            self.actuators.append(self.net[dyn.id])
        print "...Done"

        if len(self.actuators) != self.nServos and not self.silentNetFail:
            raise RobotFailure('Expected to find %d servos on network, but only got %d (%s)'
                               % (self.nServos, len(self.actuators), repr(self.actuatorIds)))

        for actuator in self.actuators:
            #actuator.moving_speed = 90
            #actuator.synchronized = True
            #actuator.torque_enable = True
            #actuator.torque_limit = 1000
            #actuator.max_torque = 1000

            actuator.moving_speed = 250
            actuator.synchronized = True
            actuator.torque_enable = True
            actuator.torque_limit = 1000
            actuator.max_torque = 1000
            actuator.ccw_compliance_margin = 3
            actuator.cw_compliance_margin  = 3

        self.net.synchronize()

        #print 'options are:'
        #for op in dir(self.actuators[0]):
        #    print '  ', op
        #for ac in self.actuators:
        #    print 'Voltage at', ac, 'is', ac.current_voltage, 'load is', ac.current_load
        #    ac.read_all()

        self.currentPos = None
        self.resetClock()

        
    def run(self, motionFunction, runSeconds = 10, resetFirst = True,
            interpBegin = 0, interpEnd = 0, timeScale = 1, logFile = None,
            extraLogInfoFn = None):
        '''Run the robot with a given motion generating function.

        Positional arguments:
        
        motionFunction -- Function used to generate the desired motor
                          positions.  This function must take a single
                          argument -- time, in seconds -- and must
                          return the desired length 9 vector of motor
                          positions.  The current implementation
                          expects that this function will be
                          deterministic.
        
        Keyword arguments:

        runSeconds -- How many seconds to run for.  This is in
                      addition to the time added for interpBegin and
                      interpEnd, if any.  Default: 10

        resetFirst -- Begin each run by resetting the robot to its
                      base position, currently implemented as a
                      transition from CURRENT -> POS_FLAT ->
                      POS_READY.  Default: True

        interpBegin -- Number of seconds over which to interpolate
                      from current position to commanded positions.
                      If this is not None, the robot will spend the
                      first interpBegin seconds interpolating from its
                      current position to that specified by
                      motionFunction.  This should probably be used
                      for motion models which do not return POS_READY
                      at time 0.  Affected by timeScale. Default: None

        interpEnd -- Same as interpBegin, but at the end of motion.
                      If interpEnd is not None, interpolation is
                      performed from final commanded position to
                      POS_READY, over the given number of
                      seconds. Affected by timeScale.  Default: None
                      
        timeScale -- Factor by which time should be scaled during this
                      run, higher is slower. Default: 1
                      
        logFile -- File to log time/positions to, should already be
                      opened. Default: None

        extraLogInfoFn -- Function to call and append info to every
                      line the log file. Should return a
                      string. Default: None
        '''

        #net, actuators = initialize()

        #def run(self, motionFunction, runSeconds = 10, resetFirst = True
        #    interpBegin = 0, interpEnd = 0):

        if self.loud:
            print 'Starting motion.'

        failures = self.pingAll()
        if failures:
            self.initServos()
            failures = self.pingAll()
            if failures:
                raise RobotFailure('Could not communicate with servos %s at beginning of run.' % repr(failures))

        self.resetClock()
        self.currentPos = self.readCurrentPosition()

        if logFile:
            #print >>logFile, '# time, servo goal positions (9), servo actual positions (9), robot location (x, y, age)'
            print >>logFile, '# time, servo goal positions (9), robot location (x, y, age)'

        # Reset the robot position, if desired
        if resetFirst:
            self.interpMove(self.readCurrentPosition(), POS_FLAT, 3)
            self.interpMove(POS_FLAT, POS_READY, 3)
            #self.interpMove(POS_READY, POS_HALFSTAND, 4)
            self.currentPos = POS_READY
            self.resetClock()

        # Begin with a segment smoothly interpolated between the
        # current position and the motion model.
        if interpBegin is not None:
            self.interpMove(self.currentPos,
                            scaleTime(motionFunction, timeScale),
                            interpBegin * timeScale,
                            logFile, extraLogInfoFn)
            self.currentPos = motionFunction(self.time)

        # Main motion segment
        self.interpMove(scaleTime(motionFunction, timeScale),
                        scaleTime(motionFunction, timeScale),
                        runSeconds * timeScale,
                        logFile, extraLogInfoFn)
        self.currentPos = motionFunction(self.time)

        # End with a segment smoothly interpolated between the
        # motion model and a ready position.
        if interpEnd is not None:
            self.interpMove(scaleTime(motionFunction, timeScale),
                            POS_READY,
                            interpEnd * timeScale,
                            logFile, extraLogInfoFn)

        failures = self.pingAll()
        if failures:
            # give it a second chance
            sleep(1)
            failures = self.pingAll()
            if failures:
                raise RobotFailure('Servos %s may have died during run.' % repr(failures))

        
    def interpMove(self, start, end, seconds, logFile=None, extraLogInfoFn=None):
        '''Moves between start and end over seconds seconds.  start
        and end may be functions of the time.'''

        self.updateClock()
        
        timeStart = self.time
        timeEnd   = self.time + seconds

        ii = 0
        tlast = self.time
        while self.time < timeEnd:
            print 'time:', self.time
            ii += 1
            posS = start(self.time) if isinstance(start, FunctionType) else start
            posE =   end(self.time) if isinstance(end,   FunctionType) else end
            goal = lInterp(self.time, [timeStart, timeEnd], posS, posE)
            print goal
            cmdPos = self.commandPosition(goal)
            if logFile:
                extraInfo = ''
                if extraLogInfoFn:
                    extraInfo = extraLogInfoFn()
                print >>logFile, self.time, ' '.join([str(x) for x in cmdPos]),
                #print >>logFile, ' '.join(str(ac.current_position) for ac in self.actuators),
                print >>logFile, extraInfo

            #volts = ['%d: %s' % (ii,ac.current_voltage) for ii,ac in enumerate(self.actuators)]
            #print ' '.join(volts)

            #[ac.read_all() for ac in self.actuators]
            #positions = ['%d: %s' % (ii,ac.cache[dynamixel.defs.REGISTER['CurrentPosition']]) for ii,ac in enumerate(self.actuators)]
            #print ' '.join(positions)
            #print ''.join(['x' if ac.led else ' ' for ac in self.actuators])
                
            #sleep(self.sleep)
            #sleep(float(1)/100)
            self.updateClock()
            secElapsed = self.time - tlast
            tosleep = self.sleep - secElapsed
            #if tosleep > 0:
                #sleep(tosleep)
            self.updateClock()
            tlast = self.time

        
#
#        currentPos = None
#
#        if resetFirst:
#            currentPos = self.currentPostion()
#            time0 = datetime.datetime.now()
#            seconds = 0
#            
#            while seconds < 10:
#                timeDiff = datetime.datetime.now() - time0
#                seconds  = timeDiff.seconds + timeDiff.microseconds/1e6
#
#                if seconds < 3:
#                    goal = lInterp(seconds, [0, 3], startingPos, POS_FLAT)
#                elif seconds < 6:
#                    goal = lInterp(seconds, [3, 6], POS_FLAT, POS_READY)
#                elif seconds < 10:
#                    goal = lInterp(seconds, [6, 10], POS_READY, POS_HALFSTAND)
#                else:
#                    break
#
#                self.commandPosition(goal)
#                sleep(self.sleep)
#                
#            currentPos = POS_HALFSTAND
#
#        if interpBegin is not None:
#            if currentPos is None:
#                currentPos = self.currentPostion()
#
#            time0 = datetime.datetime.now()
#            seconds = 0
#            
#            while seconds < interpBegin:
#                timeDiff = datetime.datetime.now() - time0
#                seconds  = timeDiff.seconds + timeDiff.microseconds/1e6
#
#                goal = lInterp(seconds, [0, interpBegin], currentPos, motionFunction(seconds))
#
#                self.commandPosition(goal)
#                time.sleep(self.sleep)
#
    def resetClock(self):
        '''Resets the robot time to zero'''
        self.time0 = datetime.now()
        self.time  = 0.0

    def updateClock(self):
        '''Updates the Robots clock to the current time'''
        timeDiff  = datetime.now() - self.time0
        self.time = timeDiff.seconds + timeDiff.microseconds/1e6

    def tic(self):
        self.updateClock()
        self.tictime = self.time

    def toc(self):
        self.updateClock()
        print 'Elapsed (%s:%s):' % fileLine(), self.time - self.tictime

    def readyPosition(self, persist = False):
        if persist:
            self.resetClock()
            while self.time < 2.0:
                self.commandPosition(POS_READY)
                sleep(.1)
                self.updateClock()
        else:
            self.commandPosition(POS_READY)
            sleep(2)

    def commandPosition(self, position, crop = True, cropWarning = False):
        '''Command the given position

        commandPosition will command the robot to move its servos to
        the given position vector.  This vector is cropped to
        the physical limits of the robot and converted to integer

        Positional arguments:
        position -- A length 9 vector of desired positions.

        Keyword arguments:
        cropWarning -- Whether or not to print a warning if the
                       positions are cropped.  Default: False.
        '''

        if len(position) != self.nServos:
            raise Exception('Expected postion vector of length %d, got %s instead'
                            % (self.nServos, repr(position)))

        if crop:
            goalPosition = self.cropPosition([int(xx) for xx in position], cropWarning)
        else:
            goalPosition = [int(xx) for xx in position]

        if self.loud:
            posstr = ', '.join(['%4d' % xx for xx in goalPosition])
            print '%.2fs -> %s' % (self.time, posstr)
        
        for ii,actuator in enumerate(self.actuators):
            actuator.goal_position = goalPosition[ii]
        self.net.synchronize()

        #[ac.read_all() for ac in self.actuators]
        #positions = ['%d: %s' % (ii,ac.cache[dynamixel.defs.REGISTER['CurrentPosition']]) for ii,ac in enumerate(self.actuators)]
        #print ' '.join(positions)
        print ''.join(['x' if ac.led else ' ' for ac in self.actuators]) + '  ' ,
        print ' '.join(['%.1f' % ac.current_voltage for ac in self.actuators])

        return goalPosition
    

    def cropPosition(self, position, cropWarning = False):
        '''Crops the given positions to their appropriate min/max values.
        
        Requires a vector of length 9 to be sure the IDs are in the
        assumed order.'''

        if len(position) != self.nServos:
            raise Exception('cropPosition expects a vector of length %d' % self.nServos)

        ret = copy(position)
        for ii in [0, 2, 4, 6]:
            ret[ii]   = max(MIN_INNER, min(MAX_INNER, ret[ii]))
            ret[ii+1] = max(MIN_OUTER, min(MAX_OUTER, ret[ii+1]))
        ret[8] = max(MIN_CENTER, min(MAX_CENTER, ret[8]))

        if cropWarning and ret != position:
            print 'Warning: cropped %s to %s' % (repr(position), repr(ret))
            
        return ret

    def readCurrentPosition(self):
        ret = []
        if len(self.actuators) != self.nServos:
            raise RobotFailure('Lost some servos, now we only have %d' % len(self.actuators))
        for ac in self.actuators:
            #ac.read_all()
            #ret.append(ac.cache[dynamixel.defs.REGISTER['CurrentPosition']])
            ret.append(ac.current_position)
            #sleep(.001)
        return ret

    def pingAll(self):
        failures = []
        for ii in self.actuatorIds:
            result = self.net.ping(ii)
            if result is False:
                failures.append(ii)
        return failures

    def printStatus(self):
        pos = self.readCurrentPosition()
        print 'Positions:', ' '.join(['%d:%d' % (ii,pp) for ii,pp in enumerate(pos)])


    def shimmy(self):
        '''Moves through a set of checks and makes sure the robot is
        still moving.'''

        self.commandPosition(POS_READY)
        sleep(.8)

        success = True
        success &= self.checkMove(POS_READY,   POS_CHECK_1)
        success &= self.checkMove(POS_CHECK_1, POS_CHECK_2)
        success &= self.checkMove(POS_CHECK_2, POS_CHECK_3)
        success &= self.checkMove(POS_CHECK_3, POS_CHECK_2)
        success &= self.checkMove(POS_CHECK_2, POS_CHECK_1)
        success &= self.checkMove(POS_CHECK_1, POS_READY)

        return success

    def checkMove(self, aa, bb):
        aa = array(aa)
        bb = array(bb)
        self.commandPosition(aa)

        posAA = array(self.readCurrentPosition())

        self.commandPosition(bb)

        sleep(.4)
        posBB = array(self.readCurrentPosition())

        success = True
        success &= all( abs((aa-bb) - (posAA-posBB)) < 50)
        success &= all( abs(aa - posAA) < 50)
        success &= all( abs(bb - posBB) < 50)

        if not success and False:
            print 'shimmy errors'
            print (aa-bb) - (posAA-posBB)
            print aa - posAA
            print bb - posBB
        return success
        

