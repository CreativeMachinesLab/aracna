import serial
import time

from constants import *

class Commander:
    def __init__(self, port="COM7", numServos=8):
        self.ser = serial.Serial(port, 38400, timeout=0.015)
        
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
                commandToWrite.append(str(arg) + ",")
        commandToWrite = commandToWrite[:-1] + COMMAND_END
        self.ser.write(commandToWrite)
    
    def helloBoard(self):
        '''Tests the communication channel with the ArbotiX. Blocks until the
        ArbotiX successfully replies with the hello message.'''
        reply = ''
        self.failedPackets = -1
        while reply != HELLO + COMMAND_END:
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
            raise Exception("did not receive POSITION")
        
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
    
    def executeMotionFunction(self, motionFunction, domain):
        '''Commands ArbotiX to move servos according to a motion function.
        motionFunction -- f(t)->[posVec]
        domain -- the times (in seconds) that the servos should be commanded.
                  to achieve smoother motion, increase the resolution of the domain'''
        
        for i in range(len(domain)):
            currentTime = domain[i]
            print self.commandPos(motionFunction(currentTime))
            if i < len(domain) - 1:
                time.sleep(domain[i+1] - currentTime)

if __name__ == '__main__':
    pass