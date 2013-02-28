import math, pdb, sys
import random
import os
import shutil
import string
import numpy
from datetime import datetime
from copy import copy
from time import sleep
from RobotConstants import MIN_INNER, MAX_INNER, MIN_OUTER, MAX_OUTER, MIN_CENTER, MAX_CENTER, NORM_CENTER

class simrun:
    ''' simulation running '''

    def __init__(self):
        self.filename = "output.txt"
        self.freq_threshold = 216 # 9 servos, 12 seconds at 2Hz
        
    def runSim(self, gaitFunction, filename):

        try:
            os.remove('/home/sean/simtest/input.txt')
        except:
            pass

        ff = file('input.txt', "w")
        timeMax = 12.0
        timeDiv = 1.0/60.0
        divs = int(timeMax/timeDiv)
        t = 0.0

        for i in xrange(0,divs):
            gait = gaitFunction[0](t)
            length = len(gait)
            t = t+timeDiv
            if t == timeMax:
                ff.write(str(t) + ' ')

                for ii in xrange(0, length):
                    ff.write(str(gait[ii]) + ' ')

            else:
                ff.write(str(t) + ' ')
                for ii in xrange(0,length):
                    ff.write(str(gait[ii]) + ' ')
                ff.write('\n')
                           
        ff.close()    
        os.system('./crossSim -i input.txt -o output.txt -n')
        outputData = self.getOutput()
        dist = self.getDist(outputData)
        counter = self.freqcheck(outputData)
        if counter > self.freq_threshold:
            dist = dist*0.5
        elif counter > self.freq_threshold*0.8:
            dist = dist*0.8
        
        shutil.move('/home/sean/simtest/input.txt', '/home/sean/simtest/%s' % filename)
        return dist

    def getOutput(self):
        outputRaw= file(self.filename,"r")
        outputData = [line.split() for line in outputRaw]
        return outputData

    def getDist(self, outputData):
        outputColLen = len(outputData)-1
        outputRowLen = len(outputData[1])-1
        posBeg = [outputData[1][outputRowLen-2], outputData[1][outputRowLen-1], outputData[1][outputRowLen]]
        posEnd = [outputData[outputColLen][outputRowLen-2], outputData[outputColLen][outputRowLen-1], outputData[outputColLen][outputRowLen]]

        # finds the distance the robot travelled using x and y '
        xdist = float(posEnd[0])-float(posBeg[0])
        zdist = float(posEnd[2])-float(posBeg[2])
#        zdist = float(self.posEnd[2])-float(self.posBeg[2])
        return math.sqrt(math.pow(xdist,2)+math.pow(zdist,2))

    def freqcheck(self, data):
      	'''checks for the number of inflection points in the servo positions'''
        pos = numpy.zeros(shape=(720,10))
        for i in range(720):
            for ii in range(10):
                pos[i][ii] = float(data[i+1][ii])
        counter = 0
        for i in range(720): # 720 lines in the data file (12 seconds at 60Hz)
            # [time servo servo servo servo servo servo servo servo servo]
            if  (i != 0 and i != 1) and ((pos[i][1]-pos[i-1][1] > 0 and pos[i-1][1]-pos[i-2][1] < 0) or (pos[i][1]-pos[i-1][1] < 0 and pos[i-1][1]-pos[i-2][1] > 0)):
                counter += 1
            if  (i != 0 and i != 1) and ((pos[i][2]-pos[i-1][2] > 0 and pos[i-1][2]-pos[i-2][2] < 0) or (pos[i][2]-pos[i-1][2] < 0 and pos[i-1][2]-pos[i-2][2] > 0)):
		counter += 1
            if  (i != 0 and i != 1) and ((pos[i][3]-pos[i-1][3] > 0 and pos[i-1][3]-pos[i-2][3] < 0) or (pos[i][3]-pos[i-1][3] < 0 and pos[i-1][3]-pos[i-2][3] > 0)):
		counter += 1
            if  (i != 0 and i != 1) and ((pos[i][4]-pos[i-1][4] > 0 and pos[i-1][4]-pos[i-2][4] < 0) or (pos[i][4]-pos[i-1][4] < 0 and pos[i-1][4]-pos[i-2][4] > 0)):
		counter += 1
            if  (i != 0 and i != 1) and ((pos[i][5]-pos[i-1][5] > 0 and pos[i-1][5]-pos[i-2][5] < 0) or (pos[i][5]-pos[i-1][5] < 0 and pos[i-1][5]-pos[i-2][5] > 0)):
		counter += 1
            if  (i != 0 and i != 1) and ((pos[i][6]-pos[i-1][6] > 0 and pos[i-1][6]-pos[i-2][6] < 0) or (pos[i][6]-pos[i-1][6] < 0 and pos[i-1][6]-pos[i-2][6] > 0)):
		counter += 1
            if  (i != 0 and i != 1) and ((pos[i][7]-pos[i-1][7] > 0 and pos[i-1][7]-pos[i-2][7] < 0) or (pos[i][7]-pos[i-1][7] < 0 and pos[i-1][7]-pos[i-2][7] > 0)):
		counter += 1
            if  (i != 0 and i != 1) and ((pos[i][8]-pos[i-1][8] > 0 and pos[i-1][8]-pos[i-2][8] < 0) or (pos[i][8]-pos[i-1][8] < 0 and pos[i-1][8]-pos[i-2][8] > 0)):
		counter += 1
            if  (i != 0 and i != 1) and ((pos[i][9]-pos[i-1][9] > 0 and pos[i-1][9]-pos[i-2][9] < 0) or (pos[i][9]-pos[i-1][9] < 0 and pos[i-1][9]-pos[i-2][9] > 0)):
		counter += 1
        return counter

    def cropPosition(self, position, cropWarning = False):
        # crops the given positions to their apropriate min/max values.
        #Requires a vector of length 9 to be sure the IDs are in the assumed order.'''
        ret = copy(position)
        for ii in [0, 2, 4, 6]:
            ret[ii] = max(MIN_INNER, min(MAX_INNER, ret[ii]))
            ret[ii+1] = max(MIN_OUTER, min(MAX_OUTER, ret[ii+1]))
        ret[8] = max(MIN_CENTER, min(MAX_CENTER, ret[8]))

        if cropWarning and ret != position:
            print 'Warning: cropped %s to %s' % (repr(position), repr(ret))

        return ret

    
