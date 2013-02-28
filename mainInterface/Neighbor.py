#! /usr/bin/env python

'''
date: 20 October 2010

'''
"""
2) neighbor selection (uniform change of one parameter, gaussian
change of one parameter, gaussian change of multiple parameters, ...)

"""

import math, pdb, sys
import random
from copy import copy

class Neighbor:
    @staticmethod
    def uniform(ranges, parameters):
        """
        Uniform change of one parameter: Given a list of parameters, picks a
        random parameter to change, randomly changes it, and returns a new 
        list.
    
        """
        ret = copy(parameters)

        index = random.randint(0, len(parameters) - 1)

        #print ranges
        if isinstance(ranges[index][0], bool):
            ret[index] = (random.uniform(0,1) > .5)
        else:
            ret[index] = random.uniform(ranges[index][0], ranges[index][1])

        #print '  ** Neighbor new', ret
        return ret

    @staticmethod
    def uniform_slight(ranges, parameters):
        """
        Given a list of parameters, picks a random parameter to change, and
        decreases or increases it slightly.
    
        """
        ret = copy(parameters)
        print '  ** Neighbor old', ret
        index = random.randint(0, len(parameters) - 1)
        print ranges
        if isinstance(ranges[index][0], bool):
            ret[index] = (random.uniform(0,1) > .5)
        else:
            if random.randint(0, 1) == 0:  # decrease slightly
                ret[index] = ret[index] - (.1 * (ranges[index][1] - ranges[index][0]))
            else:  # increase slightly
                ret[index] = ret[index] + (.1 * (ranges[index][1] - ranges[index][0]))
    
        print '  ** Neighbor new', ret
        return ret
    
    @staticmethod
    def gaussian(ranges, parameters):
        """
        Gaussian change of all parameter:
        Given a list of parameters, randomly changes all parameters based on a
        Gaussian distribution, and returns a new list.
    
        """
        ret = copy(parameters)
        index = random.randint(0, len(parameters) - 1)
    
        for index in range(len(parameters)):
            if isinstance(ranges[index][0], bool):
                ret[index] = (random.uniform(0,1) > .5)
            else:
                while True:
                    changeTo = random.gauss(ret[index], .05 * (ranges[index][1] - 
                                                           ranges[index][0]))
                    # Check that randomly generated number is in range
                    if ranges[index][0] <= changeTo <= ranges[index][1]:
                        ret[index] = changeTo
                        break
    
        return ret
    
    @staticmethod
    def gradient(ranges, parameters, epsilon):
        """
        Given a list of parameters, returns a randomly generated policy nearby
        such that each parameter is changed randomly by +epsilon * range, 0, 
        or -epsilon * range.
    
        """
        ret = copy(parameters)
        for index in range(len(parameters)):
            param = random.choice((0, 1, 2))
            if param == 0:  # decrease by epsilon*range
                ret[index] = ret[index] - (epsilon * (ranges[index][1] - \
                                                          ranges[index][0]))
            if param == 1:  # increase by epsilon*range
                ret[index] = ret[index] - (epsilon * (ranges[index][1] - \
                                                          ranges[index][0]))
            else:  # don't change this param
                pass
        return ret

    @staticmethod
    def uniform_spread(ranges, parameters, index, number = 10, includeOrig = False):
        """
        Returns a list of the specified number of neighbors, obtained
        by linearly interpolating the parameter in position index
        between the minimum and maximum values allowed by ranges.

        Examples:

        >>> Neighbor.uniform_spread([(0,10), (40,50)], [5, 45], 0, number=3)
        [[0.0, 45], [5.0, 45], [10.0, 45]]
        >>> Neighbor.uniform_spread([(0,10), (40,50)], [5, 45], 1, number=3)
        [[5, 40.0], [5, 45.0], [5, 50.0]]
        >>> Neighbor.uniform_spread([(0,10), (40,50)], [4, 45], 0, number=3, includeOrig=True)
        [[0.0, 45], [4, 45], [5.0, 45], [10.0, 45]]
        """

        ret = []

        includeFinished = False
        for ii in range(number):
            pp = copy(parameters)

            pp[index] = ranges[index][0] + float(ii)/(number-1) * (ranges[index][1] - ranges[index][0])
            if includeOrig and not includeFinished and pp[index] > parameters[index]:
                # if we've passed the original point, include it here
                ret.append(copy(parameters))
                includeFinished = True
                
            ret.append(pp)


        return ret



if __name__ == "__main__":
    import doctest
    doctest.testmod()
            

    # [JBY] This can be put in a unit test instead
    # Testing Neighbor.gradient function...
    ranges = [(0, 400), (.5, 8), (-2, 2), (-1, 1), (-1, 1)]

    parameters = []  # List of the chosen values for the parameters
    for rang in ranges:
        # Chooses random values for each parameter (initial state)
        if isinstance(rang[0], bool):  # If range is (true, false),
            # choose true or false
            parameters.append(random.uniform(0,1) > .5)
        else:
            parameters.append(random.uniform(rang[0], rang[1]))
    print parameters
    print Neighbor.gradient(ranges, parameters, .05)
    print Neighbor.gaussian(ranges, parameters)

