#! /usr/bin/env python

'''Just a few utility functions'''

from copy import copy
from numpy import array, random, diag, interp, vstack



def matInterp(x, xp, fp):
    '''Like numpy.interp, but works with an array for fp.
    Interpolates whole rows of fp.'''
    vec = [interp(x, xp, fp[:,jj]) for jj in range(fp.shape[1])]
    return array(vec)



def prettyVec(vec, prec=4):
    st = '%%.%df' % prec
    return ('[' +
            ' '.join([st % xx if isinstance(xx,float) else repr(xx) for xx in vec]) +
            ']')



def randUniformPoint(ranges):
    '''
    Given the ranges of the different parameters, chooses random values for
    each parameter. The ranges of parameters are in a list of tuples.

    '''

    parameters = []  # List of the chosen values for the parameters
    for rang in ranges:
        # Chooses random values for each parameter (initial state)
        if isinstance(rang[0], bool):  # If range is (true, false),
                       # choose true or false
            parameters.append(random.uniform(0,1) > .5)
        else:
            parameters.append(random.uniform(rang[0], rang[1]))
    return parameters



def randGaussianPoint(center, ranges, stddev = .1, crop=True):
    '''
    Return a random sampling of a Gaussian distribution specified by
    the given'center', 'ranges', and desired 'stddev' along each
    dimension.  stddev is given as a fraction of the total range.

    The ranges of parameters are in a list of tuples.
    '''

    covar = diag([((x[1]-x[0]) * stddev) ** 2 for x in ranges])
    ret = random.multivariate_normal(center, covar)

    # crop to min/max values
    if crop:
        for ii in range(len(ret)):
            ret[ii] = max(ranges[ii][0], min(ranges[ii][1], ret[ii]))

    return ret


def phys2unif(X, ranges):
    '''Map a vector (or an array of vectors, one in each row) from a
    physical space to a uniform space (each dimension has values only
    in [0,1].'''
    ret = copy(X)
    ret -= array([x[0] for x in ranges])
    ret /= array([x[1]-x[0] for x in ranges])
    return ret


def unif2phys(X, ranges):
    '''Reverse the effects of phys2unif'''
    ret = copy(X)
    ret *= array([x[1]-x[0] for x in ranges])
    ret += array([x[0] for x in ranges])
    return ret


def writeArray(ff, arr):
    '''Write array arr to file object ff in human readable format.''' 
    for row in arr:
        ff.write('%s\n' % ' '.join([str(x) for x in row]))

def readArray(ff):
    '''Read array from file object ff in writeArray format.'''
    
    for ii,line in enumerate(ff):
        #print 'line', ii, 'is', line
        nums = [float(xx) for xx in line.split()]
        if ii == 0:
            ll = len(nums)
            ret = array(nums)
        else:
            if len(nums) != ll:
                raise Exception('Row %s contained unexpected number of fields' % line)
            ret = vstack((ret, array(nums)))

    return ret
