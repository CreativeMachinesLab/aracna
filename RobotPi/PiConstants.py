#! /usr/bin/env python

# Aracna ranges tuned with Rob
MIN_INNER = 50
MAX_INNER = 600
MIN_OUTER = 0
MAX_OUTER = 550

#MIN_OUTER = 30
#MIN_OUTER = 0
#MAX_OUTER = 940
#MAX_OUTER = 800 # changing because Robot hits antenna
#MAX_OUTER = 680  # changing because screws still interfere
#MAX_OUTER = 550  # changing because screws still interfere
#MIN_CENTER = 512 - 180
#MAX_CENTER = 512 + 180
MIN_CENTER = 512 - 120
MAX_CENTER = 512 + 120
NORM_CENTER = 512

POS_FLAT      = [512] * 8
POS_READY     = [770,  40] * 4
POS_HALFSTAND = [700, 100] * 4
##POS_STAND     = [512, 150] * 4
POS_STAND     = [512, 680] * 4

POS_CHECK_1   = [770, 200] * 4
POS_CHECK_2   = [670, 300] * 4
POS_CHECK_3   = [670, 300] * 4




if __name__ == '__main__':
    toprint = ('MIN_INNER', 'MAX_INNER',
               'MIN_OUTER', 'MAX_OUTER',
               'MIN_CENTER', 'MAX_CENTER',
               'POS_FLAT', 'POS_READY', 'POS_HALFSTAND', 'POS_STAND')

    #pdb.set_trace()
    for var in toprint:
        print '%14s = %s' % (var, repr(eval(var)))
