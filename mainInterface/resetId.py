#! /usr/bin/env python

import sys

from Robot import *
from dynamixel import defs



USAGE = '''Resets ID of the single connected motor to the supplied ID.
There must be only one connected motor when this is run!

Usage: ./resetId.py <ID>
Example:
  ./resetID.py 4    # resets ID of connected motor to 4
'''



def main():
    if len(sys.argv) != 2:
        print USAGE
        sys.exit(1)

    idNew = int(sys.argv[1])

    print 'Scanning dynamixel network, could take a little while...'
    rr = Robot(silentNetFail = True)

    if len(rr.actuators) != 1:
        raise Exception('Expected to find a single servo on the network, but found %d (%s)'
                        % len(rr.actuators), repr(rr.actuatorIds))
    idOld = rr.actuatorIds[0]
    
    print 'Reasigning from ID %d to ID %d' % (idOld, idNew)
    rr.actuators[0]._dyn_net.write_instruction( idOld, defs.INSTRUCTION.WriteData, [3, idNew] )
    print 'Done'



if __name__ == '__main__':
    main()
