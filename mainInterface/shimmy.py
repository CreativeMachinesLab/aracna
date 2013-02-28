#! /usr/bin/env python



from Robot import *

rr = Robot()

worked = rr.shimmy()

print 'Worked' if worked else 'Failed'


