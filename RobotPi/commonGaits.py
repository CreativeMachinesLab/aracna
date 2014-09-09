#! /usr/bin/env python

'''
Gaits pulled from aaron.ppr:

Aracna:8:1024:1024:1024:1024:1024:1024:1024:1024
Pose=neutral-extend:0, 0, 0, 0, 0, 0, 0, 0
Pose=max:1023, 1023, 1023, 1023, 1023, 1023, 1023, 1023
Pose=neutral-contract:1023, 512, 1023, 512, 1023, 512, 1023, 512
Pose=mid:512, 512, 512, 512, 512, 512, 512, 512
Pose=1:769, 254, 347, 986, 639, 267, 37, 372
Pose=zero:0, 0, 0, 0, 0, 0, 0, 0
Pose=beta:0, 508, 0, 521, 515, 0, 515, 0
Pose=levelextend:1023, 409, 806, 1017, 955, 1023, 1023, 688
Pose=alpha:515, 0, 515, 0, 0, 515, 0, 515
Pose=2:12, 608, 930, 174, 1023, 973, 701, 1011
Pose=nope:1023, 521, 1023, 521, 1023, 515, 1023, 533
Seq=jumpingjacks: neutral-extend|750, neutral-contract|750
Seq=swag: alpha|800, beta|800
Seq=gaita: 1|500, 2|500, 1|500, 2|500, 1|500, 2|500
Seq=lubricate: zero|1000, max|1000
Seq=gait1: zero|500, max|500, mid|500, p3|500, mid|500
Seq=gait2: max|500, p1|500, zero|500, p3|500
'''

from numpy import *
from Motion import lInterp
from PiConstants import *

# Define poses used in gaits
pose_neutral_extend = [0, 0, 0, 0, 0, 0, 0, 0]
pose_max = [1023, 1023, 1023, 1023, 1023, 1023, 1023, 1023]
pose_neutral_contract = [1023, 512, 1023, 512, 1023, 512, 1023, 512]
pose_mid = [512, 512, 512, 512, 512, 512, 512, 512]
pose_1 = [769, 254, 347, 986, 639, 267, 37, 372]
pose_zero = [0, 0, 0, 0, 0, 0, 0, 0]
pose_beta = [0, 508, 0, 521, 515, 0, 515, 0]
pose_level_extend = [1023, 409, 806, 1017, 955, 1023, 1023, 688]
pose_alpha = [515, 0, 515, 0, 0, 515, 0, 515]
pose_2 = [12, 608, 930, 174, 1023, 973, 701, 1011]
pose_nope = [1023, 521, 1023, 521, 1023, 515, 1023, 533]

  # changing because screws still interfere
s0 = [300, 300, 300, 300, 300, 300, 300, 300]
#s1 = [100, 500, 300, 000, 100, 500, 300, 600]

#Works
#s1 = s0 + array([-100, 0, 0, 0, -100, 0, 0, 0])
#s2 = s0 + array([-100, 0, 0, 300, -100, 0, 0, -300])
#s3 = s0 + array([0, 0, -100, 300, 0, 0, -100, -300])
#s4 = s0 + array([0, 0, -100, -300, 0, 0, -100, 300])

s1 = s0 + array([-200, 0, 0, 0, -200, 0, 0, 0])
s2 = s0 + array([-200, 0, 0, 300, -200, 0, 0, -300])
s3 = s0 + array([0, 0, -200, 300, 0, 0, -200, -300])
s4 = s0 + array([0, 0, -200, -300, 0, 0, -200, 300])

s1b = s0 + array([-200, 0, 0, 0, -200, 0, 0, 0])
s2b = s0 + array([-200, 0, 0, -300, -200, 0, 0, 300])
s3b = s0 + array([0, 0, -200, -300, 0, 0, -200, 300])
s4b = s0 + array([0, 0, -200, 300, 0, 0, -200, -300])






def repeating_motion(time, intervals, poses):
    '''Return position assumign repeated motion between the given
    poses where each segment takes a length of time given by
    intervals.
    '''
    
    assert len(intervals) == len(poses)
    time_points = cumsum([0] + intervals)
    total_duration = time_points[-1]
    relative_time = time % total_duration
    for ii in xrange(len(time_points) - 1):
        if (relative_time < time_points[ii+1]):
            return lInterp(relative_time,
                           [time_points[ii], time_points[ii+1]],
                           poses[ii],
                           poses[(ii+1)%len(poses)])
    raise Exception('Logic error; should not get here')

# Define gaits
def jumpingjacks(time):
    return repeating_motion(time, [.75, .75], [pose_neutral_extend, pose_neutral_contract])

def swagger(time):
    return repeating_motion(time, [.8, .8], [pose_alpha, pose_beta])

def star6(time):
    return repeating_motion(time, [.5, .2, .5, .2], [s1, s2, s3, s4])

def star2(time):
    return repeating_motion(time, [.5, .2, .5, .2], [s1b, s2b, s3b, s4b])

def star62(time):
    if time < 1:
        return s0
    elif time < 11:
        return star6(time)
    else:
        return star2(time)

def gaita(time):
    return repeating_motion(time, [.5, .5], [pose_1, pose_2])

def lubricate(time):
    return repeating_motion(time, [1.0, 1.0], [pose_zero, pose_max])

def gait1(time):
    #return repeating_motion(time, [.5, .5, .5, .5, .5], [pose_zero, pose_max, pose_mid, pose_p3, pose_mid])
    return repeating_motion(time, [.5, .5, .5, .5, .5], [pose_zero, pose_max, pose_mid, pose_2, pose_mid])

def gait2(time):
    #return repeating_motion(time, [.5, .5, .5, .5], [pose_max, pose_p1, pose_zero, pose_p3])
    return repeating_motion(time, [.5, .5, .5, .5], [pose_max, pose_1, pose_zero, pose_2])

def sine(time):
    '''Just a sine wave on all motors.'''
    return array([512 + 100*sin(time) for ss in range(8)])

def wave(time):
    '''Wave with one motor.'''
    vv = 512 + 100*sin(time)
    ret = array(POS_READY)
    ret[1] = vv
    return ret



# Get git based on name
def get_gait(gait_name):
    if (gait_name == 'jumpingjacks'):
        return jumpingjacks
    elif (gait_name == 'swagger'):
        return swagger
    elif (gait_name == 'gaita'):
        return gaita
    elif (gait_name == 'lubricate'):
        return lubricate
    elif (gait_name == 'gait1'):
        return gait1
    elif (gait_name == 'gait2'):
        return gait2
    elif (gait_name == 'sine'):
        return sine
    elif (gait_name == 'wave'):
        return wave
    elif (gait_name == 'star6'):
        return star6
    elif (gait_name == 'star2'):
        return star2
    elif (gait_name == 'star62'):
        return star62
    elif (gait_name == 'wave'):
        return wave
    elif (gait_name == 'wave'):
        return wave
    else:
        raise Exception('Unknown gait name: "%s"' % gait_name)


        
