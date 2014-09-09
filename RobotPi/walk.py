#! /usr/bin/env python

import argparse

from commonGaits import *
from RobotPi import *




def run_gait(gait_name, time_scale = 1.0, run_time = 10.0):
    robot = RobotPi()

    gait_function = get_gait(gait_name)
    #scaled_gait_function = scaleTime(gait_function, 1.0 / gait_speed)
    
    robot.run(gait_function,
              runSeconds = run_time,
              resetFirst = False,
              #interpBegin = 2.0,
              #interpEnd = 2.0,
              interpBegin = 0.0,
              interpEnd = 0.0,
              timeScale = time_scale)



def main():
    parser = argparse.ArgumentParser(description='Plays a gait on the Aracna robot.')
    parser.add_argument('-s', '--speed', type = float, default = 1.0,
                        help = 'Speed, higher is slower (default: 1.0)')
    parser.add_argument('-t', '--time', type = float, default = 10.0,
                        help = 'Total length of time (default: 10.0)')
    parser.add_argument('gait', type = str, default = 'star60', choices = ['jumpingjacks','swagger','gaita','lubricate','gait1','gait2','swagger','sine','wave', 'star6', 'star0', 'star2', 'star4', 'star60', 'star24', 'star6_2', 'star60_24', 'packing_slow', 'stand'], nargs='?',
                        help = 'Which gait to play, options are: swagger. Default: swagger')
    args = parser.parse_args()

    run_gait(args.gait, args.speed, args.time)
    
    print 'done'



if __name__ == '__main__':
    main()
