#! /usr/bin/env python

'''
date: 17 November 2010

'''
"""
Neighbor selection (uniform change of one parameter, gaussian
change of one parameter, gaussian change of multiple parameters, ...) 
"""

import math, pdb, sys, string, pickle
from numpy import *
from numpy.linalg import *
import random
from copy import copy
from util import prettyVec, readArray, matInterp

class Strategy(object):
    '''Base class for strategies.'''

    def __init__(self, initialPoint, ranges):
        self.current = initialPoint
        self.iterations = 0
        self.bestIter   = None
        self.ranges     = ranges
        
    def getNext(self):
        if getattr(self, 'separateLogInfo', False):
            next, logInfo = self._getNext()
        else:
            next = self._getNext()
            logInfo = next
        return next, logInfo

    def _getNext(self):
        raise Exception('Need to implement this')

    def updateResults(self, dist):
        '''This must be called for the last point that was handed out!'''
        raise Exception('Need to implement this')

    def logHeader(self):
        '''Override this and make it return a string to be logged'''
        return None


class OneStepStrategy(Strategy):
    """
    Base class for any methods that produce a single neighbor at a time.
    """

    def __init__(self, *args, **kwargs):
        super(OneStepStrategy, self).__init__(*args, **kwargs)
        self.bestDist  = None
        self.bestState = self.current
        
    def updateResults(self, dist):
        self.iterations += 1
        if self.bestDist is None or dist > self.bestDist:
            self.bestDist = dist
            self.bestState = self.current
            self.bestIter  = self.iterations

        print '    best (iter %3d)' % self.bestIter, prettyVec(self.bestState), '%.2f' % self.bestDist  # Prints best state and distance so far


class RandomStrategy(OneStepStrategy):
    """
    Random change of all parameters: Given a list of parameters, randomly
    changes all of them, and returns a new list.
    
    """

    def _getNext(self):
        ret = copy(self.bestState)

        if self.bestDist is not None:
            for index in range(0, len(ret)):
                #print self.ranges
                if isinstance(self.ranges[index][0], bool):
                    ret[index] = (random.uniform(0,1) > .5)
                else:
                    ret[index] = random.uniform(self.ranges[index][0], \
				                self.ranges[index][1])

        #print '  ** Neighbor new', ret
        return ret
class UniformStrategy(OneStepStrategy):
    """
    Uniform change of one parameter: Given a list of parameters, picks
    a random parameter to change, randomly changes it, and returns a
    new list.
    
    """

    def _getNext(self):
        ret = copy(self.bestState)

        if self.bestDist is not None:
            index = random.randint(0, len(self.ranges) - 1)

            #print self.ranges
            if isinstance(self.ranges[index][0], bool):
                ret[index] = (random.uniform(0,1) > .5)
            else:
                ret[index] = random.uniform(self.ranges[index][0], self.ranges[index][1])

        #print '  ** Neighbor new', ret
        return ret

    

class UniformSlightStrategy(OneStepStrategy):
    """
    Given a list of parameters, picks a random parameter to change, and
    decreases or increases it slightly.
    
    """

    def _getNext(self):
        ret = copy(self.bestState)
        print '  ** Neighbor old', ret
        index = random.randint(0, len(parameters) - 1)
        print self.ranges
        if isinstance(self.ranges[index][0], bool):
            ret[index] = (random.uniform(0,1) > .5)
        else:
            if random.randint(0, 1) == 0:  # decrease slightly
                ret[index] = ret[index] - (.1 * (self.ranges[index][1] - self.ranges[index][0]))
            else:  # increase slightly
                ret[index] = ret[index] + (.1 * (self.ranges[index][1] - self.ranges[index][0]))
    
        print '  ** Neighbor new', ret
        return ret



class GaussianStrategy(OneStepStrategy):
    """
    Gaussian change of all parameter:
    Given a list of parameters, randomly changes all parameters based on a
    Gaussian distribution, and returns a new list.
    
    """

    def _getNext(self):
        ret = copy(self.bestState)
        # return ret  # [JBY] This is a hack to reuse the same gait!
    
        index = random.randint(0, (len(self.ranges) - 1))
    
        for index in range(len(self.ranges)):
            if isinstance(self.ranges[index][0], bool):
                ret[index] = (random.uniform(0,1) > .5)
            else:
                while True:
                    changeTo = random.gauss(ret[index], .05 * (self.ranges[index][1] - 
                                                           self.ranges[index][0]))
                    # Check that randomly generated number is in range
                    if self.ranges[index][0] <= changeTo <= self.ranges[index][1]:
                        ret[index] = changeTo
                        break
    
        return ret



class GradientSampleStrategy(Strategy):
    """
    N-dimensional policy gradient algorithm. During each iteration of the main
    loop we sample t policies near currentState to estimate the gradient
    around currentState, then move currentState by an amount of eta in the
    most favorable direction. Adapted from Nate Kohl and Peter Stone,
    UT Ausin/ICRA 2004.
    
    """

    def __init__(self, *args, **kwargs):
        super(GradientSampleStrategy, self).__init__(*args, **kwargs)
        self.bestDist  = None
        self.bestState = self.current

        self.epsilon = .05
        self.numNeighbors = 8

        self.triedSoFar = []
        self.stillToTry = []

    def _getNext(self):
        if len(self.stillToTry) == 0:
            self.populateStillToTry()

        return self.stillToTry[0]

    def populateStillToTry(self):
        self.stillToTry.append(self.current)

        # Evaluate t=8 policies per iteration
        print 'Base  point is', self.current
        for i in range(self.numNeighbors):
            point = self.getEpsilonNeighbor(self.ranges, self.current, self.epsilon)
            print 'Nearby point is', point
            self.stillToTry.append(point)
        

    def updateResults(self, dist):
        '''This must be called for the last point that was handed out!'''

        self.triedSoFar.append(self.stillToTry.pop(0))
        self.triedSoFar[-1].append(dist)
        print '        Got update, policy is now', self.triedSoFar[-1]

        # If this was the last one, compute a new current location
        if len(self.stillToTry) == 0:
            self.current = self.computeNextMove(self.current, self.ranges, self.triedSoFar)
            self.triedSoFar = []
            self.stillToTry = []


    def getEpsilonNeighbor(self, parameters, epsilon):
        """
        Given a list of parameters, returns a randomly generated policy nearby
        such that each parameter is changed randomly by +epsilon * range, 0, 
        or -epsilon * range.
    
        """
        ret = copy(parameters)
        #print 'ret was', ret
        for index in range(len(ret)):
            param = random.choice((0, 1, 2))
            if param == 0:  # decrease by epsilon*range
                change = ret[index] - (epsilon * (self.ranges[index][1] - self.ranges[index][0]))
                if change < self.ranges[index][0]:  # Check that we are within range.
                    ret[index] = self.ranges[index][0]
                else:
                    ret[index] = change
            if param == 1:  # increase by epsilon*range
                change = ret[index] + (epsilon * (self.ranges[index][1] - self.ranges[index][0]))
                if change > self.ranges[index][1]:
                    ret[index] = self.ranges[index][1]
                else:
                    ret[index] = change
        #print 'returning', ret
        #print
        return ret

    def computeNextMove(self, center, samples):
        '''Returns the center of the next distribution.'''

        # Average the scores for all random policies
        adjustment = []  # Adjustment vector
        for n in range(len(self.ranges)):
             # Keep track of number of policies with pos/neg/0 perturbation
             # in dimension n
            num_epos = num_eneg = num_zero = 0
            avg_epos = avg_eneg = avg_zero = 0
            for neighbor in samples:
                if neighbor[n] > center[n]:  # positive perturbation
                    avg_epos = avg_epos + neighbor[len(neighbor) - 1]
                    num_epos = num_epos + 1
                if neighbor[n] < center[n]:  # negative perturbation
                    avg_eneg = avg_eneg + neighbor[len(neighbor) - 1]
                    num_eneg = num_eneg + 1
                if neighbor[n] == center[n]:  # zero perturbation
                    avg_zero = avg_zero + neighbor[len(neighbor) - 1]
                    num_zero = num_zero + 1

            # Finish calculating averages.        
            try:
                avg_epos = avg_epos / num_epos
            except ZeroDivisionError:
                avg_epos = 0

            try: 
                avg_eneg = avg_eneg / num_eneg
            except ZeroDivisionError:
                avg_eneg = 0

            try:
                avg_zero = avg_zero / num_zero
            except ZeroDivisionError:
                avg_zero = 0

            if avg_zero > avg_epos and avg_zero > avg_eneg:
                adjustment.append(0)
            else:
                adjustment.append(avg_epos - avg_eneg)

		# Calculate adjustment vector for each dimension, multiplying with a
		# scalar step-size eta, so that our adjustment will remain a fixed
		# size each iteration
		eta = .1
		total = 0
		for adj in adjustment:
		    total += adj ** 2
		magnitude = math.sqrt(total)
		
		for index in range(len(adjustment)):
		    adjustment[index] = (adjustment[index] / magnitude) * eta
		    adjustment[index] = adjustment[index] * (self.ranges[index][1] - self.ranges[index][0])
                    change = center[index] + adjustment[index]
                    if change < self.ranges[index][0]:  # Check that we are within range.
                        adjustment[index] = self.ranges[index][0] - center[index]
                    if change > self.ranges[index][1]:
                        adjustment[index] = self.ranges[index][1] - center[index]

        nextState = [center, adjustment]
        nextState = [sum(value) for value in zip(*nextState)]
        return nextState

class SimplexStrategy(Strategy):
    """
    Nelder-Mead Simplex Method. During each iteration of the main loop, the
    vertex of the simplex with the slowest walk is reflected over the centroid
    of the remaining points. Depending on the speed of the walk at this new
    point, the point will be either accepted, expanded, or contracted. The
    resulting point of this will determine whether the entire simplex will
    shrink or not.
    """
    
    def __init__(self, *args, **kwargs):
        super(SimplexStrategy, self).__init__(*args, **kwargs)
        self.alpha = 1 # reflection coefficient
        self.beta = .5 # contraction coefficient
        self.gamma = 2 # expansion coefficient
        self.delta = .5 # shrink coefficient
        self.numVertices = 6 # number of vertices
        self.numParam = 5 # number of parameters

        self.vertices = [] # (vertices, distance) list
        self.toTry = []
        self.transformation = 0 # 0-initialize, 1-reflect, 2-expand,
                                # 3-contract out, 4-contract in, 5-shrink
        self.bestDist = 0
        self.reflectDist = 0
        
    def _getNext(self):
        if self.transformation == 0 and len(self.toTry) == 0:
            print ' create simplex'
            self.createSimplex(self.ranges)
        elif self.transformation == 1:
            name = 'simplex_%s.pkl' %''.join(random.choice(string.ascii_letters) for ii in xrange(10))
            print ' saving %s and reflecting' % name
            f = open(name, 'w')
            pickle.dump(self, f)
            f.close()
            self.reflect(self.ranges)
        elif self.transformation == 2:
            print ' expanding'
            self.expand(self.ranges)
        elif self.transformation == 3:
            print ' contract out'
            self.contractOut(self.ranges)
        elif self.transformation == 4:
            print ' contract in'
            self.contractIn(self.ranges)
        elif self.transformation == 5:
            print ' shrink'
            self.shrink(self.ranges)
            self.transformation = 0
        return self.toTry[0]
    
    def updateResults(self, dist):
        if dist > self.bestDist:
            self.bestDist = dist
        print '               best distance: ', '%.2f'% self.bestDist
        if self.transformation == 0: #initializing new vertices
            self.vertices.append((self.toTry.pop(0), dist))
            if len(self.toTry) == 0:
                self.transformation = 1
        elif self.transformation == 1: #reflection
            self.updateReflect(dist, self.ranges)
        elif self.transformation == 2: #expansion
            self.updateExpansion(dist, self.ranges)
        elif self.transformation == 3: #contract out
            self.updateContractOut(dist, self.ranges)
        elif self.transformation == 4: #contract in
            self.updateContractIn(dist, self.ranges)
#        elif self.transformation == 5: #shrink
#            self.vertices.append((self.toTry.pop(0), dist))
#            if len(self.toTry) == 0:
#                self.transformation = 1
    
    def createSimplex(self, ranges):
        ''' picks the other vertices by changing one parameter at a time in the
            initial vector by .1 of the range '''
        self.toTry.append(self.current)
        for param in range(self.numParam):
            nextV = []
            for p in range(self.numParam):
                nextV.append(self.current[p])
            rang = ranges[param][1] - ranges[param][0]
            if (nextV[param] + (.1 * rang)) < ranges[param][1]:
                nextV[param] += .1 * rang
                self.toTry.append(nextV)
            else:
                nextV[param] -= .1 * rang
                self.toTry.append(nextV)
    
            
    def getCentroid(self, ranges):
        ''' calculates the centroid of all the vertices '''
        centroid = []
        for n in range(self.numParam):
            centroid.append(0)
        for vert in range(self.numVertices):
            for par in range(self.numParam):
                centroid[par] += (self.vertices[vert][0][par] / self.numVertices)
        return centroid

    def reflect(self, ranges):
        ''' reflects the worst point over the centroid '''
        self.vertices = sorted(self.vertices, key=lambda dist: dist[1])
        centroid = self.getCentroid(ranges)
        worst = self.vertices[0][0]
        point = []
        for p in range(self.numParam):
            point.append(centroid[p])
        for x in range(self.numParam):
            r = centroid[x] - worst[x]
            point[x] += self.alpha * r
            if point[x] < ranges[x][0]:
                point[x] = ranges[x][0]
            elif point[x] > ranges[x][1]:
                point[x] = ranges[x][1]
        self.toTry.append(point)

    def expand(self, ranges):
        ''' expands the simplex in the direction of the reflected point '''
        centroid = self.getCentroid(ranges)
        point = []
        for p in range(self.numParam):
            point.append(centroid[p])
        rpoint = self.toTry[0]
        for x in range(self.numParam):
            e = rpoint[x] - centroid[x]
            point[x] += self.gamma * e
            if point[x] < ranges[x][0]:
                point[x] = ranges[x][0]
            elif point[x] > ranges[x][1]:
                point[x] = ranges[x][1]
        self.toTry.insert(0, point)

    def contractOut(self, ranges):
        ''' contracts the simplex away from the reflected point '''
        centroid = self.getCentroid(ranges)
        point = []
        for p in range(self.numParam):
            point.append(centroid[p])
        rpoint = self.toTry[0]
        for x in range(self.numParam):
            c = rpoint[x] - centroid[x]
            point[x] += self.beta * c
            if point[x] < ranges[x][0]:
                point[x] = ranges[x][0]
            elif point[x] > ranges[x][1]:
                point[x] = ranges[x][1]
        self.toTry.insert(0, point)
    
    def contractIn(self, ranges):
        ''' contracts the simplex away from the reflected point '''
        centroid = self.getCentroid(ranges)
        point = []
        for p in range(self.numParam):
            point.append(centroid[p])
        worst = self.vertices[0][0]
        rpoint = self.toTry[0]
        for x in range(self.numParam):
            c = worst[x] - centroid[x]
            point[x] += self.beta * c
            if point[x] < ranges[x][0]:
                point[x] = ranges[x][0]
            elif point[x] > ranges[x][1]:
                point[x] = ranges[x][1]
        self.toTry.insert(0, point)

    def shrink(self, ranges):
        ''' shrinks the size of the simplex around the best vertex '''
        best = self.vertices[self.numVertices - 1][0]
        for vert in range(self.numVertices - 1):
            nextV = []
            for p in range(self.numParam):
                nextV.append(0)
            for param in range(self.numParam):
                rang = ranges[param][1] - ranges[param][0]
                dif = (best[param] - self.vertices[0][0][param]) * rang
                nextV[param] = self.vertices[0][0][param] + dif
                if nextV[param] < ranges[param][0]:
                    nextV[param] = ranges[param][0]
                elif nextV[param] > ranges[param][1]:
                    nextV[param] = ranges[param][1]
            self.toTry.append(nextV)
            self.vertices.pop(0)
    
    def updatePoint(self, point, dist):
        ''' sets the paramater vector at index point in toTry as a new vertex with 
            distance dist '''
        self.vertices.pop(0)
        self.vertices.append((self.toTry.pop(point), dist)) #expansion point
        self.toTry.pop(0)
        self.transformation = 1

    def updateReflect(self, dist, ranges):
        ''' decides what, if any, transformation should be done based on the
            distance traveled of the reflected point '''
        self.reflectDist = dist
        if dist < self.vertices[self.numVertices - 1][0] and dist > self.vertices[1][0]:
            self.vertices.pop(0)
            self.vertices.append((self.toTry.pop(0), dist))
        elif dist > self.vertices[self.numVertices - 1][0]:
            self.transformation = 2
        elif dist < self.vertices[1][0] and dist > self.vertices[0][0]:
            self.transformation = 3
        elif dist < self.vertices[0][0]:
            self.transformation = 4
    
    def updateExpansion(self, dist, ranges):
        ''' saves either the reflected point or the expansion point '''
        if dist > self.reflectDist:
            self.updatePoint(0, dist) #choose expansion point
        else:
            self. updatePoint(1, self.reflectDist) #choose reflection point
    
    def updateContractOut(self, dist, ranges):
        ''' either saves the contracted point or decides to shrink the simplex '''
        if dist >= self.reflectDist:
            self.updatePoint(0, dist)
        else:
            self.toTry = []
            self.transformation = 5
    
    def updateContractIn(self, dist, ranges):
        ''' either saves the contracted point or decides to shrink the simplex '''
        if dist > self.vertices[0][0]:
            self.updatePoint(0, dist)
        else:
            self.toTry = []
            self.transformation = 5
    

class LearningStrategy(Strategy):
    '''
    A strategy that uses supervised learning to guess which parameter vector would be good to try next.
    '''

    def __init__(self, *args, **kwargs):
        super(LearningStrategy, self).__init__(*args, **kwargs)
        self.X = []
        self.y = []
        self.theta = []

    def _getNext(self):
        '''Learn model on X and y...'''

        # 1. Learn
        # 2. Try some nearby values
        # 3. Pick best one


    def updateResults(self, dist):
        '''This must be called for the last point that was handed out!'''

        # about the same...
        self.triedSoFar.append(self.stillToTry.pop(0))
        self.triedSoFar[-1].append(dist)
        print '        Got update, policy is now', self.triedSoFar[-1]

class LinearRegressionStrategy(LearningStrategy):
    '''
    A strategy that uses supervised learning (linear regression) to guess which
    parameter vector would be good to try next.`Tests 5 (or however many
    parameters there are) random vectors first.
    '''

    def _getNext(self):
        '''Learn model on X and Y...'''
        # If we still need to test initial 5 random params:
        if len(self.X) < len(self.ranges):
            ret = copy(self.current)

            # Generate random param.
            if self.bestIter is not None:
                for index in range(0, len(ret)):
                    if isinstance(self.ranges[index][0], bool):
                        ret[index] = (random.uniform(0,1) > .5)
                    else:
                        ret[index] = random.uniform(self.ranges[index][0], \
				                    self.ranges[index][1])

            self.X.append(ret)
            return ret

        # Set the current vector (vector we are adjusting from) to
        # one of the vectors with the furthest distance so far, if
        # this is the first time calculating weights:
        if len(self.theta) == 0:
           self.current = self.X[self.y.index(max(self.y))] 
        
        # If we have enough params to calculate weights:
        self.calculate_weights(self.X, self.y)
        print '        Weights are now ', self.theta     

        # Calculate the magnitude of the weights vector
        total = 0
	for weight in self.theta:
	    total += weight ** 2
        magnitude = math.sqrt(total)
        
        # adjustment vector = normalization of weights * eta
        eta = .1 # size of each iteration
        adjustment = self.theta
	for index in range(len(adjustment)):
   	    adjustment[index] = (adjustment[index] / magnitude) * eta
	    adjustment[index] = adjustment[index] * (self.ranges[index][1] - self.ranges[index][0])
            change = self.current[index] + adjustment[index]
            if change < self.ranges[index][0]:  # Check that we are within range.
                adjustment[index] = self.ranges[index][0] - self.current[index]
            if change > self.ranges[index][1]:
                adjustment[index] = self.ranges[index][1] - self.current[index]
      
        # policy = policy + adjustment
        nextState = [self.current, adjustment]
        self.current = [sum(value) for value in zip(*nextState)]
        self.X.append(self.current)
        return self.current

    def predict_distance_walked(self, inputs):
        '''
        Given a weight vector and an input vector, predicts the distance
        walked by the robot.
        '''
        return sum([self.theta[i]*inputs[i] for i in range(len(self.theta))])

    def calculate_weights(self, training_params, distances_walked):
        '''
        Given matching vectors of training parameter vectors and the distances
        walked by each training param, of length, calculates a 
        guess for the weights using least-squares
        '''
        self.theta = linalg.lstsq(training_params, distances_walked)[0]

    def updateResults(self, dist):
        '''This must be called for the last point that was handed out!'''

        self.y.append(dist)
        self.bestIter = 1
        self.current = self.X[-1] 
        print '        Got update, ', self.X[-1], ' walked ', self.y[-1]



class FileStrategy(OneStepStrategy):
    '''
    Loads commanded positions from a file.
    '''

    def __init__(self, *args, **kwargs):
        super(FileStrategy, self).__init__([], [])

        self.filtFile = kwargs.get('filtFile', None)

        self.junkPoints      = 1000
        # How many lines to expect from HyperNEAT file
        self.expectedLines   = self.junkPoints + 12 * 40


        if self.filtFile is None:
            raise Exception('Need a filtFile')

        ff = open(self.filtFile)
        self.positions = readArray(ff)
        ff.close()

        TOTAL_TIME = 12
        self.times = linspace(0, TOTAL_TIME, self.positions.shape[0])

        self.separateLogInfo = True
        
        self.counter = 0

    def _getNext(self):
        '''just return function of time, same every time'''

        ident = 'file__%s__%d' % (self.filtFile, self.counter)
        self.counter += 1

        print 'returning', lambda time: matInterp(time, self.times, self.positions), ident
        return lambda time: matInterp(time, self.times, self.positions), ident



if __name__ == "__main__":
    import doctest
    doctest.testmod()
            

    # # [JBY] This can be put in a unit test instead
    # # Testing Neighbor.gradient function...
    # ranges = [(0, 400), (.5, 8), (-2, 2), (-1, 1), (-1, 1)]
    # 
    # parameters = []  # List of the chosen values for the parameters
    # for rang in ranges:
    #     # Chooses random values for each parameter (initial state)
    #     if isinstance(rang[0], bool):  # If range is (true, false),
    #         # choose true or false
    #         parameters.append(random.uniform(0,1) > .5)
    #     else:
    #         parameters.append(random.uniform(rang[0], rang[1]))
    # print parameters
    # print Neighbor.gradient(ranges, parameters, .05)
    # print Neighbor.gaussian(ranges, parameters)

    
