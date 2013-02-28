#! /usr/bin/env python

'''
Dummy simulator for integration testing that outputs garbage.

Provides randomly generated, equivalently formatted data to the real
robot and the simulator.
'''

import sys
import random



def main():
    if len(sys.argv) <= 1:
        print 'Error: not enough arguments'
        print 'Usage: %s [infile] outfile' % sys.argv[0]
        sys.exit(1)

    if len(sys.argv) == 3:
        inFilename = sys.argv[1]
        outFilename = sys.argv[2]
    else:
        inFilename = None
        outFilename = sys.argv[1]

    NN = 100
    ff = open (outFilename, 'w')
    ff.write('# simtime (joint_commanded joint_actual_pos)x9 pos.x pos.y pos.z\n')
    for ii in xrange(NN):
        line = '%.3f' % (float(ii) / 10)
        for ss in xrange(9):
            line += ' %d %d' % (random.randint(0, 1023), -999)
        line += ' %f %f %d' % (random.uniform(-100, 100), random.uniform(-100, 100), -999)
        ff.write(line + '\n')
    ff.close()



if __name__ == '__main__':
    main()
