import sys, pickle, pdb
from SineModel import SineModel5
from simrun import simrun
from ExternalStrategy import NEATStrategy
from util import randUniformPoint


def SimOptimize():
    strategy = NEATStrategy(SineModel5.typicalRanges,restartHN = False)
    print 'NEATStrategy'
    sim = simrun()
    trial = 0
    for ii in range(10000):
        nextGait = strategy.getNext()
        # Run the gait 
        thisIdentifier = '%s_%05d_%03d' % (strategy.identifier, strategy.genId, strategy.orgId)
        dist = sim.runSim(nextGait, '%s_gait' % thisIdentifier)
        strategy.updateResults(dist)
        trial += 1
        print 'Trial', trial, 'moved', dist
        print

def main(limit = 10):
#    sim = simrun.simrun()
 #   if limit is None:
  #      limit = 10000
   # 
   # for ii in xrange(limit):
    #    SimOptimize(sim)
     #   sim.getDist()
#        print currentState
      #  print sim.getDist()
      SimOptimize()

if __name__ == '__main__':
    main()
