#! /usr/bin/env python

#import math, pdb, sys
#from numpy import *
#from numpy.linalg import *
#import random
#from copy import copy


from random import choice
from numpy import array, random, ones, zeros, sin, vstack, hstack, argmax, diag, linalg, dot, exp
#from sg import sg           # Import shogun
import string, os
import pickle
import pdb

from Strategy import Strategy, OneStepStrategy
from util import *
from SineModel import SineModel5



#    NOT USING THIS ANY MORE
#
#    '''
#    A strategy that uses the Support Vector Machine regression to
#    guess which parameter vector would be good to try next.  Requires
#    the installation of "pysvmlight", an interface to SVM Light by
#    Thorsten Joachims (http://svmlight.joachims.org/).  pysvmlight is
#    available here:
#
#    http://bitbucket.org/wcauchois/pysvmlight
#    '''


class SVMLearningStrategy(OneStepStrategy):
    '''
    A strategy that uses the Support Vector Machine regression to
    guess which parameter vector would be good to try next.  Requires
    the installation of shogun-python, a python machine learning
    library offering, among other things, access to libsvr.

    http://www.shogun-toolbox.org/

    http://www.csie.ntu.edu.tw/~cjlin/libsvm/    
    '''

    def __init__(self, *args, **kwargs):
        # call this only after popping 'ranges' arg
        super(SVMLearningStrategy, self).__init__(*args, **kwargs)

        self.pickle = True
        if 'pickle' in kwargs:
            self.pickle = kwargs['pickle']
        if self.pickle:
            self.randStr = ''.join(choice(string.ascii_letters) for ii in range(6))
            filename = 'svmstate_%s_000.pkl' % (self.randStr)
            print 'SVMLearningStrategy saving itself as files like', filename


        ########################
        # Strategy parameters
        ########################

        # Number of points to add to the initial point to try before learning
        N_init_neighborhood = 7

        # Initial noise to add to the inital point to generate the
        # N_init_neighborhood points
        initialNoise = .1

        # How close to search around the best point, in terms of a
        # fraction of the range in each dimension
        self.exploreScale = .01

        # How many nearby points to check        
        self.numNearby = 100

        # How much random noise to add to the next trial (might
        # prevent model collapse)
        self.bumpBy = .01

        # If the best predicted distance is below this, the bump by
        # self.lowDistBump instead of self.bumpBy
        self.lowDistThresh = 5.0
        
        # How much random noise to add to the next trial if we're getting nowhere
        self.lowDistBump = .1

        # Only use the last trainOnLast runs for training, instead of
        # training on all data.
        self.trainOnLast = 6


        ########################
        # SVR parameters
        ########################

        self.width = 2.1
        #self.width = .1
        #self.width = .03

        #self.C=1.2
        #self.C=.5         # tried this a few times, repetitive runs
        #self.C=.04
        self.C=500.       # barely gets training on 8 perfect
        self.C=1000.      # maybe try this?

        # SVR termination criteria
        self.tube_epsilon=1e-3


        # self.current is defined in Strategy constructor
        # Populate toTry with some points
        self.toTry = array(self.current)
        for ii in range(N_init_neighborhood):
            #row = randUniformPoint(self.ranges)
            row = randGaussianPoint(self.current, self.ranges, initialNoise)
            self.toTry = vstack((self.toTry, row))
        
        self.X = None
        self.y = None


    def _getNext(self):
        '''Get the next point to try.  The first few times this will
        return a random point near the initialPoint, and after that it
        will return the best predicted point by the learning model,
        perhaps with some added noise.'''

        if self.toTry.shape[0] == 0:
            # We're out of things to try.  Make more.
            
            # 1. Learn
            self.train()

            # 2. Try some nearby values
            for ii in xrange(self.numNearby):
                row = array(randGaussianPoint(self.bestState, self.ranges, self.exploreScale))
                if ii == 0:
                    nearbyPoints = row
                else:
                    nearbyPoints = vstack((nearbyPoints, row))
            predictions = self.predict(nearbyPoints)
            #print 'nearbyPoints', nearbyPoints
            #print 'predicitons', predictions
            
            
            # 3. Pick best one
            iiMax = argmax(predictions)
            self.toTry = array([nearbyPoints[iiMax, :]])

            # Testing hack... this should be disabled
            #self.toTry = array([randUniformPoint(self.ranges)])

            # Prints the most promising vector found and its predicted value
            print '     value for best', prettyVec(self.bestState),
            print 'p: %.2f, a: %.2f' % (self.predict(self.bestState),
                                         self.bestDist)
            print '     most promising', prettyVec(self.toTry[0,:]), 'pred: %.2f' % predictions[iiMax]
            
            # 4. (optional) Add a little noise (or a lot of noise)
            if predictions[iiMax] < self.lowDistThresh:
                extraStr = '+'
                bumpBy = self.lowDistBump
            else:
                extraStr = ' '
                bumpBy = self.bumpBy
            bump = randGaussianPoint(zeros(self.toTry.shape[1]),
                                     self.ranges, bumpBy, crop=False)
            self.toTry += bump

            print '   %snoisy promising' % extraStr, prettyVec(self.toTry[0,:]),
            print 'pred: %.2f' % self.predict(self.toTry[0,:])

        self.current = self.toTry[0,:]
        return self.current


    def updateResults(self, dist):
        '''This must be called for the last point that was handed out!

        Once called, we remove the first point from self.toTry and add
        it to self.X and add the distance to self.y
        '''

        # MAKE SURE TO CALL super().updateResults!
        super(SVMLearningStrategy, self).updateResults(dist)

        dist = float(dist)
        justTried = self.toTry[0,:]
        self.toTry = self.toTry[1:,:]
        if self.X == None:
            self.X = justTried
            self.y = array(dist)
        else:
            self.X = vstack((self.X, justTried))
            self.y = hstack((self.y, array(dist)))

        if self.pickle:
            self.saveAndCleanup()
            


    def train(self):
        '''Learn a model from self.X and self.y'''

        # Constants pulled from <shogun>/examples/documented/python/regression_libsvr.py
        size_cache=10

        # map each dimension of self.X to [0,1]
        unif = phys2unif(self.X, self.ranges)

        train_X = unif.T
        train_y = self.y

        train_X = train_X[:,-self.trainOnLast:]
        train_y = train_y[-self.trainOnLast:]
        
        sg('set_features', 'TRAIN', train_X)
        #sg('set_kernel', 'GAUSSIAN', 'REAL', size_cache, self.width)
        sg('set_kernel', 'LINEAR', 'REAL', size_cache)

        sg('set_labels', 'TRAIN', train_y)
        sg('new_regression', 'LIBSVR')
        sg('svr_tube_epsilon', self.tube_epsilon)
        sg('c', self.C)
        sg('train_regression')


    def predict(self, testPoints):
        '''Predicts performance using previously learned model.
        self.train() must be called before this!'''

        if len(testPoints.shape) < 2:
            testPoints = array([testPoints])

        sg('set_features', 'TEST', phys2unif(testPoints,self.ranges).T)
        predictions = sg('classify')

        return predictions


    def plot(self):
        from matplotlib.pyplot import plot, show, savefig, xlabel, ylabel
        plot(self.y)
        xlabel('Iteration')
        ylabel('Fitness (arbitrary units)')
        savefig('svm_sim_results.eps')
        savefig('svm_sim_results.png')
        show()

    def saveAndCleanup(self):
        filename = 'svmstate_%s_%03d.pkl' % (self.randStr, self.iterations)
        ff = open(filename, 'w')
        pickle.dump(self, ff)
        ff.close()
        if self.iterations > 1:
            lastIt = self.iterations-1
            if (lastIt & (lastIt - 1)) != 0:
                # if last one wasn't a power of two
                filenameLast = 'svmstate_%s_%03d.pkl' % (self.randStr, lastIt)
                os.remove(filenameLast)

    def logHeader(self):
        filename = 'svmstate_%s_000.pkl' % (self.randStr)
        return '# SVMLearningStrategy saving itself as files like %s\n' % filename



#
# [JBY] The following is just code for testing the SVM/SVR learning
# capabilities.
#

def dummyObjective(X):
    '''A Dummy objective that can be used to test learning strategies.
    Intended to be used for vector X where each X is in or close to
    [-1, 1].
    '''

    # Promote to float64 datatype
    X = X * ones(len(X))

    ret = 0.0
    ret += sum(X)
    ret += sum(sin(X/20))

    return ret



def dummyObjectiveGauss(X, center, ranges):
    '''A Dummy objective that can be used to test learning strategies.

    fitness is 100 * GaussianPdf(mean, cov)
    '''

    covar = diag([((x[1]-x[0])*.2) ** 2 for x in ranges])
    
    cinv = linalg.inv(covar)
    return 100. * exp(-dot(dot((X-center), cinv), (X-center)))



def syntheticData(points = 10, dim = 3, fn = dummyObjective):
    '''Generate the requested number of data points from a function.

    Returns of the form:
      [
      (<label>, [(<feature>, <value>), ...]),
      (<label>, [(<feature>, <value>), ...]),
      ...
      ]
    '''

    ret = []
    
    for ii in range(points):
        X = random.randn(dim)
        y = fn(X)
        ret.append( (y, [(ii+1, X[ii]) for ii in range(len(X))]) )

    return ret



def syntheticData2(points = 10, dim = 3, fn = dummyObjective):
    '''Generate the requested number of data points from a function.

    Returns of the form:
      X, y   both numpy arrays
    '''

    ret = []

    X = []
    y = []
    for ii in range(points):
        X.append(random.randn(dim))
        y.append(fn(X[-1]))

    return array(X), array(y)



def main_svmlight():
    # copied:
    import svmlight
    import pdb
    
    training_data = syntheticData(30, 1)
    test_data     = syntheticData(30, 1)
    #training_data = __import__('data').train0
    #test_data = __import__('data').test0

    print 'HERE 0'
    print 'training_data is', training_data
    print 'test_data is', test_data

    # train a model based on the data
    #pdb.set_trace()
    print 'HERE 1'
    model = svmlight.learn(training_data, type='regression', kernelType=2, verbosity=3)
    print 'HERE 2'

    # model data can be stored in the same format SVM-Light uses, for interoperability
    # with the binaries.
    svmlight.write_model(model, 'my_model.dat')
    print 'HERE 3'

    # classify the test data. this function returns a list of numbers, which represent
    # the classifications.
    #predictions = svmlight.classify(model, test_data)
    pdb.set_trace()
    predictions = svmlight.classify(model, training_data)
    print 'HERE 4'
    
    for p,example in zip(predictions, test_data):
        print 'pred %.8f, actual %.8f' % (p, example[0])



def main_libsvr():
    import pdb
    train_X, train_y = syntheticData2(30, 1)
    test_X,  test_y  = syntheticData2(20, 1)

    train_X = train_X.T
    test_X  = test_X.T

    print 'Trying LibSVR'

    size_cache=10
    width=2.1
    C=1.2
    epsilon=1e-5
    tube_epsilon=1e-2

    from sg import sg
    sg('set_features', 'TRAIN', train_X)
    sg('set_kernel', 'GAUSSIAN', 'REAL', size_cache, width)

    sg('set_labels', 'TRAIN', train_y)
    sg('new_regression', 'LIBSVR')
    sg('svr_tube_epsilon', tube_epsilon)
    sg('c', C)
    sg('train_regression')

    sg('set_features', 'TEST', test_X)
    predictions = sg('classify')

    
    for pred,act in zip(predictions, test_y):
        print 'pred %.8f, actual %.8f' % (pred, act)



def main():
    random.seed(11)

    initialPoint = randUniformPoint(SineModel5.typicalRanges)
    strategy = SVMLearningStrategy(initialPoint, ranges = SineModel5.typicalRanges)

    center = array([100, 2, 0, 0, 0])
    obj = lambda x: dummyObjectiveGauss(x, center, SineModel5.typicalRanges)
    
    for ii in range(120):
        print
        print
        current = strategy.getNext()
        print '   %3d trying' % ii, prettyVec(current),
        simDist = obj(current)
        print simDist
        strategy.updateResults(simDist)

    strategy.plot()



if __name__ == '__main__':
    main()

