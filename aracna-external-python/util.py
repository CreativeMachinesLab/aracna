'''
Created on Oct 16, 2012

@author: Eric Gold
'''

from random import randint
from constants import *

def randomFunction(f, startTime, endTime, variance=1, dt = 2):
    '''Takes in an existing function and perturbs it a little to make a new one'''
    t = randint(startTime-dt, endTime+dt)
    y0 = f(t)
    y = randint(-variance,variance)+y0
    y = y if y <= MAX_SERVO_POS else MAX_SERVO_POS
    y = y if y >= MIN_SERVO_POS else MIN_SERVO_POS
    return smoothPoint(f,y,t,dt) #XXX: what if we go out of the domain or range?
         
def smoothPoint(f, y, t, dt):
    '''Uses a straight-line approximation to bring points within
    distance dt closer to y=f(t).'''
    dt = dt/2.0
    y1 = f(t-dt)
    y2 = f(t+dt)
    t1 = t - dt
    t2 = t + dt
    
    # h(x) is the new function middle we will substitute
    h = lambda x : y1 + ((y-y1)/(t-t1)) * (x-t1) if x < t else y + ((y2-y)/(t2-t)) * (x-t)
    
    # g(x) is the old function with the new part substituted in
    g = lambda x : f(x) if x > t2 or x < t1 else h(x)
    return g

def linearInterpolation(f, x0, xf, stepSize):
    '''Returns a list of tuples of the form ((xGoal,(yGoal)),m), where
            xGoal -- the x-coordinate we want to move to
            yGoal -- the y-coordinate we want to move to
            m     -- the slope of the line (ie. speed)
       f    -- the function to be approximated
       x0   -- the starting value of x to evaluate at
       xf   -- the final value of x to stop at
       stepSize -- the length of each step (ie. xGoal2 - xGoal1)'''
    steps = [((x0,(f(x0))), 0)]
    for x in range(x0+stepSize,xf, stepSize):
        ((xP, yP), mP) = steps[x-1]
        steps.append(((x,f(x)), SPEED_BOOST * abs(f(x)-yP)/(float(stepSize))))
    return steps

def vectorizeFunctions(servoSteps):
    # Convert motion on a servo-by-servo basis to a vectorized form
    steps = []
    for x in range(0,10,1):
        pos = []
        spd = []
        for s in range(8):
            #Get servo data
            ((t, y), m) = servoSteps[s][x]
            #Append to the steps list
            pos.append(y)
            spd.append(m)
        steps.append( ((x, tuple(pos)), tuple(spd)) )
    return steps

def degreesToBytes(angle):
    return int(float(angle) * MAX_BYTE_VAL / MAX_SERVO_POS)
def bytesToDegrees(pos):
    return float(pos) * MAX_SERVO_POS / MAX_BYTE_VAL
def dpsToBytes(degreesPerSecond):
    return int(float(degreesPerSecond) * MAX_BYTE_VAL / (MAX_SERVO_SPEED * 360/60))
def bytesToDPS(speed):
    return float(speed) * (MAX_SERVO_SPEED * 360 / 60) / MAX_BYTE_VAL