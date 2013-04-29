#! /usr/bin/env python

from math import sin, pi
from MotionModel import MotionModel



class SineModel5(MotionModel):
    '''A five parameter motion model using a Sine wave central
    pattern.'''


    '''Typical ranges for the five model parameters, useful for
    generating neighbors, etc.'''

    typicalRanges = [(0, 400),
                     (.5, 8),
                     (-2, 2),
                     (-1, 1),
                     (-1, 1)]

    def model(self, time, parameters, croppingFunction = None):
        '''Returns the computed servo locations given the time and model parameters'''

        if len(parameters) != 5:
            raise Exception('sineModel expected parameter vector of length 5, got' + repr(parameters))

        pFloat = [float(xx) for xx in parameters]
        #amp, tau, scaleInOut, flipFB, flipLR = pFloat
        amp, tau, scaleInOut, multFB, multLR = pFloat

        centerConst = 512
        ret = [centerConst] * 9

        #offset = 512
        offsetInner = 800
        offsetOuter = 40

        # Compute base sine wave
        base = amp * sin(2*pi*time/tau)

        idxInner = [0, 2, 4, 6]
        idxOuter = [1, 3, 5, 7]

        idxLR    = [6, 7, 0, 1]
        idxFront = [0, 1, 2, 3]
        idxBack  = [4, 5, 6, 7]

        idxLR    = [6, 7, 0, 1]
        idxLeft  = [6, 7, 0, 1]
        idxRight = [2, 3, 4, 5]

        for ii in idxInner:
            ret[ii] = base
        for ii in idxOuter:
            ret[ii] = base * scaleInOut

        #if flipFB:
        #    for ii in idxFB:
        #        ret[ii] = -ret[ii]
        #if flipLR:
        #    for ii in idxLR:
        #        ret[ii] = -ret[ii]
        for ii in range(len(idxFront)):
            ret[idxFront[ii]] = multFB * ret[idxBack[ii]]
        for ii in range(len(idxLeft)):
            ret[idxLeft[ii]] = multLR * ret[idxRight[ii]]

        for ii in idxInner:
            ret[ii] += offsetInner
        for ii in idxOuter:
            ret[ii] += offsetOuter

        if croppingFunction:
            croppingFunction(ret)

        return ret



def main():
    theta = [1.5, 5, 2, False, False]
    for step in range(0,20):
        tt = step / 4.
        motors = sineModel(tt, theta)
        print tt, motors



if __name__ == '__main__':
    main()
