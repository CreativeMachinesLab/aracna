#! /usr/bin/env python

'''
@date: 31 October 2010

Explores each parameter dimension separately.

Starts with a random location, or the one specified on the command line, if applicable
'''

import sys
from SineModel import SineModel5
from RunManager import RunManager
from Neighbor import Neighbor
from util import randUniformPoint



def main():
    runman = RunManager()

    # Choose initialState, either from user-inputted parameters or randomly
    if len(sys.argv) > 1:
        initialState = [eval(xx) for xx in sys.argv[1].split()]
    else:
        initialState = randUniformPoint(SineModel5.typicalRanges)

    runman.explore_dimensions(initialState, SineModel5.typicalRanges, pointsPerDim = 9, repetitions = 2)



if __name__ == '__main__':
    main()
