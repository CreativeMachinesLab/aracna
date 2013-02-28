from Robot import *
from dynamixel import defs
N = 0
rr = Robot(expectedIds = range(8)) # replace N with the id  of the servo to be changed
N = rr.actuatorIds[0]
rr.actuators[0]._dyn_net.write_instruction( N, defs.INSTRUCTION.WriteData, [3, 7] ) %ibid

#if you don't know the ID, do this rr = Robot(expectedIds = range(234)) to scan for all possible id numbers
