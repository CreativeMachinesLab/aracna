#!/usr/bin/env python

'''Converts _filt files to _cmd files'''

import sys
import pdb
from numpy import array, hstack, vstack, linspace, flatnonzero

from RobotConstants import *
from Motion import *
from util import matInterp, writeArray



def main():
    if len(sys.argv) < 2:
        print 'need name of file'
        exit(1)
    
    # load original positions
    ff = open(sys.argv[1], 'r')
    for ii,line in enumerate(ff):
        #print 'line', ii, 'is', line
        nums = [float(xx) for xx in line.split()]
        if ii == 0:
            positions = array(nums)
        else:
            positions = vstack((positions, array(nums)))
    ff.close()

    # assume 1 sec interp on beginning, 2 sec at end
    interpBegin = 1
    runSeconds  = 9
    interpEnd   = 2

    totalTime = interpBegin + runSeconds + interpEnd   # 12 for normal runs
    
    times = linspace(0,totalTime,positions.shape[0])
    
    origFn = lambda time: matInterp(time, times, positions)

    # interpolate the starting positions
    for ii in flatnonzero(times < interpBegin):
        # for each index of one of these times, interpolate the function

        posOrig = positions[ii,:]
        posNew  = lInterp(times[ii], [0, interpBegin], POS_READY, posOrig)
        positions[ii,:] = posNew

    # interpolate the ending positions
    for ii in flatnonzero(times > (totalTime - interpEnd)):
        # for each index of one of these times, interpolate the function

        posOrig = positions[ii,:]
        posNew  = lInterp(times[ii], [totalTime - interpEnd, totalTime], posOrig, POS_READY)
        positions[ii,:] = posNew


    timeAndPos = vstack((times, positions.T)).T
    # print out positions
    writeArray(sys.stdout, timeAndPos)



if __name__ == '__main__':
    main()
