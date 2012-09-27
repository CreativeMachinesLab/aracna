import serial
import time
from numpy.ma.core import *
from random import randint

from constants import *

class Commander:
    def __init__(self, port="COM7", numServos=8):
        self.ser = serial.Serial(port, 38400)
        
        self.numServos = numServos
        
        #For debugging purposes only
        self.failedPackets = 0
        self.successfulPackets = 0
        self.startTime = time.clock()
        
    
    '''Prints the runtime in seconds'''    
    def tic(self):
        self.startTime = time.clock()
    def toc(self):
        print str(time.clock() - self.startTime)
    
    def __writeCommand(self,command, args=None):
        '''Writes out a command to ArbotiX.
            command -- the command from the constants.py file
            args -- an iterable list of args. Must be castable to a String'''
        commandToWrite = command
        if args is not None:
            for arg in args:
                commandToWrite += str(arg) + ","
        commandToWrite = commandToWrite.strip(",")
        commandToWrite = commandToWrite + COMMAND_END
        print "Command: " + commandToWrite
        self.ser.write(commandToWrite)
    
    def helloBoard(self):
        '''Tests the communication channel with the ArbotiX. Blocks until the
        ArbotiX successfully replies with the hello message.'''
        reply = ''
        self.failedPackets = -1
        while reply != HELLO:
            self.failedPackets += 1
            self.__writeCommand(HELLO)
            reply = self.ser.readline()
        print self.failedPackets
    
    def query(self):
        '''Requests information regarding servo positions from ArbotiX. Returns
        a list of length self.numServos representing the servo positions.'''
        self.__writeCommand(QUERY)
        reply = self.ser.readline()
        
        if reply[:2] != QUERY:
            raise Exception("did not receive QUERY")
        
        reply = [int(pos) for pos in reply[2:-2].split(SEPARATOR)]
        if len(reply) != self.numServos:
            raise Exception("invalid reply--expected " + str(self.numServos) + " items but got " + str(len(reply)))
        
        return [int(pos) for pos in reply[2:-2].split(SEPARATOR)]
    
    def commandPos(self, posVector):
        '''Commands ArbotiX to move servos to the given goal position.'''
        if len(posVector) != self.numServos:
            raise Exception("invalid position vector--expected " + str(self.numServos) + " items but got " + str(len(posVector)))
        
        self.__writeCommand(POSITION, posVector)
        reply = self.ser.readline()
        
        if reply[:2] != POSITION:
            raise Exception("did not receive POSITION, instead got\n" +reply +" as reply.")
        
        reply = [int(pos) for pos in reply[2:-2].split(SEPARATOR)]
        if len(reply) != self.numServos:
            raise Exception("invalid reply--expected " + str(self.numServos) + " items but got " + str(len(posVector)))
        
        return reply
    
    def __setSingleServo(self, servoId, param, val):
        '''Framework for setting a single parameter for a single servo'''
        self.__writeCommand(param, args=[servoId,val])
        reply = self.ser.readline()
        
        if reply[:2] != param:
            raise Exception("did not receive " + str(param))
        
        reply = [int(pos) for pos in reply[2:-2].split(SEPARATOR)]
        if len(reply) != 2:
            raise Exception("invalid reply--expected 2 values but got " + str(len(reply)))
        
        return reply
    
    def setVelocity(self, servoId, velocity):
        '''Sets the velocity of servo. velocity is in the range [0,1023]'''
        return self.__setSingleServo(servoId, VELOCITY, velocity)
    
    def setTorque(self, servoId, torque):
        '''Sets the torque of servo. torque is in the range [0,1023]'''
        return self.__setSingleServo(servoId, TORQUE, torque)
    
    def executeMotionFunction(self, motionFunction, **kwargs):
        '''Commands ArbotiX to move servos according to a motion function.
        motionFunction -- f(t)->[posVec]
        commandTimes -- the times (in seconds) that the servos should be commanded.
                        to achieve smoother motion, increase the resolution of the domain
                     -- if domain is None, the function will be commanded at 
        domain -- the domain over which to command the robot. The command rate will be
                  the maximum frequency (the command rate for ArbotiX <--> Python)'''
        if "commandTimes" in kwargs.keys(): #Command in steps
            domain = kwargs.get("commandTimes")
            for i in range(len(domain)):
                currentTime = domain[i]
                print self.commandPos(motionFunction(currentTime))
                if i < len(domain) - 1:
                    time.sleep(domain[i+1] - currentTime)
                    
        elif "domain" in kwargs.keys(): #Command continuously (or near-continuously)
            startDomain, endDomain = kwargs.get("domain")
            duration = endDomain - startDomain
            
            startTime = time.time()
            curTime = startTime
            endTime = startTime + duration
            
            while curTime < endTime:
                curTime = time.time()
                timeInterp = (curTime - startTime) + startDomain
                print "time: " + str(timeInterp)
                print "pos: " + str(motionFunction(timeInterp))
                self.commandPos(motionFunction(timeInterp))
            
def randomFunction(f, startTime, endTime, variance=50, dt = 2):
    '''Takes in an existing function and perturbs it a little to make a new one'''
    t = randint(startTime+dt, endTime-dt)
    y0 = f(t)
    y = randint(-variance,variance)+y0
    y = y if y < 1024 else 1024
    y = y if y >= 0 else 0
    return smoothPoint(f,y,t,dt) #XXX: what if we go out of the domain or range?
         
def smoothPoint(f, y, t, dt):
    '''Uses a straight-line approximation to bring points within
    distance dt closer to y=f(t).'''
    y0 = f(t-dt)
    y1 = f(t+dt)
    
    # h(x) is the new function middle we will substitute
    h = lambda x : y0+(y-y0)*(x-t-dt)*2/dt if x < t else y+(y1-y)*(x-t)*2/dt
    
    # g(x) is the old function with the new part substituted in
    g = lambda x : f(x) if t > x+dt or t < x-dt else h(x)
    return g

#------------------------------------------------------------------------------------#
#                                    Demo main functions                             #
#------------------------------------------------------------------------------------#

def sinWaveMotion():
    '''One possible demo function to move the servos in sin and cosine waves'''
    robot = Commander(port="COM6")
    r = 512
    dur = 10
    sinF = lambda t : int(r * (sin(t)) + r)
    cosF = lambda t : int(r * (cos(t)) + r)
    f = lambda t: (sinF(t), sinF(t), sinF(t), sinF(t), cosF(t), cosF(t), cosF(t), cosF(t))
    robot.executeMotionFunction(motionFunction=f, domain=(0,20))
    
def randomMotion():
    '''Uses randomFunction() to generate new motions'''
    startTime = 0
    endTime = 20
    variance = 1
    dt = 2
    
    fInit = lambda t: 512
    fVec = [fInit] * 8
    for i in range(100):
        for j in range(len(fVec)):
            f = fVec[j]
            fVec[j] = randomFunction(f, startTime, endTime)
    
    mf = lambda t: (int(fVec[0](t)),int(fVec[1](t)),int(fVec[2](t)),int(fVec[3](t)),
                    int(fVec[4](t)),int(fVec[5](t)),int(fVec[6](t)),int(fVec[7](t)))
    
    robot = Commander(port="COM6")
    robot.helloBoard()
    robot.executeMotionFunction(mf,domain=(startTime,endTime))
    
    
if __name__ == '__main__':
    robot = Commander(port="COM6")
    robot.commandPos([512]*8)