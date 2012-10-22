'''
Created on Sep 10, 2012

@author: Eric Gold
'''

__COMMAND_START = '.'
COMMAND_END = '\n'
SEPARATOR = ','

HELLO = __COMMAND_START + 'h'
QUERY = __COMMAND_START + 'q'
POSITION = __COMMAND_START + 'c'
VELOCITY = __COMMAND_START + 'v'
TORQUE = __COMMAND_START + 't'

MIN_BYTE_VAL = 0
MAX_BYTE_VAL = 1023

MIN_SERVO_POS = 0
MAX_SERVO_POS = 300

MIN_SERVO_SPEED = 0 # TODO: this might be incorrect! Must verify through testing
MAX_SERVO_SPEED = 114 # Speed in RPMs
