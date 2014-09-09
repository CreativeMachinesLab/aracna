#! /usr/bin/env python

import argparse

from RobotPi import *




def runGait(gait_name, time_scale = 1.0):
    robot = RobotPi()
    runTime = 10.0

    gait_function = get_gait(gait_name)
    #scaled_gait_function = scaleTime(gait_function, 1.0 / gait_speed)
    
    robot.run(gait_function,
              runSeconds = 10,
              resetFirst = False,
              interpBegin = 1.0,
              interpEnd = 1.0,
              timeScale = time_scale)



def main():
    parser = argparse.ArgumentParser(description='Plays a gait on the Aracna robot.')
    parser.add_argument('-s', '--speed', type = float, default = 1.0,
                        help = 'Speed (default: 1.0)')
    parser.add_argument('gait', type = str, default = 'swagger', choices = ['swagger', 'other'], nargs='?',
                        help = 'Which gait to play, options are: swagger. Default: swagger')
    args = parser.parse_args()

    runGait(args.gait, args.speed)
    
    print 'done'



if __name__ == '__main__':
    main()
