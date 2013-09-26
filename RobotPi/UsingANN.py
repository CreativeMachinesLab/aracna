'''@author : Rawan Al Ghofaili'''

from RobotPi import *
from PiConstants import POS_READY
from time import sleep

import copy
import sys

from ANN import *
'actuate Aracna using a neural network'
MAX_HIP = 0 
MIN_HIP = 512#extended up

MAX_KNEE = 512 #extended out
MIN_KNEE = 0

MAX_NNKNEE = 20
MIN_NNKNEE = -20

MAX_NNHIP = 10.5
MIN_NNHIP = -10.5

M_PI = 3.14159265358979323846

max_disparity = 0 #maximum disparity allowed between current position and commanded position 


def knee_to_NN(pos):
	'''convert actual servo positions [0, 512] into neural network input/output bounds [-20, 20]'''
	angle = (pos/MAX_KNEE)*(MAX_NNKNEE - MIN_NNKNEE)
	angle = angle + MIN_NNKNEE
	return angle	

def knee_to_POS(angle):
	'''convert neural network input/output angles [0, 1] into servo positions [0,512]'''
	pos = (MAX_KNEE-MIN_KNEE)*angle
	return int(pos)

def hip_to_POS(angle):
	'''converts neural network input/output [0, 1] into servo positions [512,0]'''
	pos = -((angle*MIN_HIP)- MIN_HIP)
	return int(max(min(pos, MIN_HIP), MAX_HIP))


def is_reached(current, commanded):
	'''returns whether or not the commanded position is reached'''
	#commanded is empty
	if not commanded:
		return True

	reached = True
	count = 0
	while(reached and (count< len(current))):
		disparity = abs(commanded[count] - current[count])
		if(disparity > max_disparity):
			reached = False
		count+=1
	return reached


def main(argv):
	
	#parse arguments
	#python UsingANN.py neuralnetworkfile [commandRate(default =40)]
	#check for the right number of arguments
	if (len(argv)<1):
		print"\nMust provide neural network file name"
		sys.exit(2)

	nnfile = argv[0] + '.txt'

	commandRate = -1
	if(len(argv)>2):
		commandRate = float(argv[2])
	
	#open log file for writing
	logfile = 'log'
	if(len(argv)>1):
		logfile = argv[1]+ '.txt'
	f = open(logfile, 'w')
	f.write("Start logging...")

	#Creating the Neural Network using a text file
	testann = ANN(1)
	testann.create_network(nnfile)
	#Loading the ANN with 0s initially
	print "\nLoading the ANN [0, 0, 0, 0]"
	inputvals = [0.0, 0.0, 0.0, 0.0]
	testann.load_NN(inputvals)
	#initilize the neural network using CTRNN_Controller()
	print "\nUsing CTRNN_Controller: dt = .02"
	nnoutput = testann.CTRNN_Controller(.02)

	for node in nnoutput:
		print node.get_output()

	robot = RobotPi()#Query Aracna on current sensors
	if(commandRate>0):
		robot = RobotPi(commandRate)
	
	val  = "\nneural network file: {0}\ncommandRate: {1}".format(nnfile, commandRate)
	line  = str(val)
	f.write(line)
	commanded_pos = []
	first = True
	commanded = False

	while(True):
		#Query Aracna on current sensors
		#old_pos = current_pos
		current_pos = robot.readCurrentPosition()#returns a list of 8 servo positions
		val = "\ncurrent_pos: {0}".format(current_pos)
		line = str(val)
		f.write(line)

		#pos = [right hip, right knee, back hip, back knee, front hip, front knee, left hip, left knee]
		#sensors = [right knee, back knee, front knee, left knee]
		print "\nafter reading current pos\t", current_pos
		if(is_reached(current_pos, commanded_pos)):
		    for ii in range(0, 1):
		      	sensors = []
		        for i in [0, 2, 4, 6]:
			        current_pos[i] = max(min(MAX_HIP, current_pos[i]), MIN_HIP) #restrict servo pos [0, 1024]
			        current_pos[i+1] = max(min(MIN_KNEE, current_pos[i+1]), MAX_KNEE)#restrict servo pos [1024, 0]
			        value  = knee_to_NN(current_pos[i+1])#convert to neural network sensor bounds [-20, 20] degrees
				#sensors.append(value* (M_PI/180.0)) #convert to radian
			sensors.append(knee_to_NN(current_pos[3])*(M_PI/180.0)) #back knee
			sensors.append(knee_to_NN(current_pos[5])*(M_PI/180.0)) #front knee
			sensors.append(knee_to_NN(current_pos[1])*(M_PI/180.0)) #right knee
			sensors.append(knee_to_NN(current_pos[7])*(M_PI/180.0)) #left knee
			#Load sensors into ANN
			testann.load_NN(sensors)
			#Get ANN nnoutput [0, 1] 
	             	#print "\nPropagating the ANN"
			nnoutput = testann.output_NN(.01)

			#Map nnoutput from [0, 1] to actual servo pos
			#print "nnoutput" 
			#for node in nnoutput:
			#print node.get_output()
			desired_pos = []
			#desired_pos[0] = MIN_NNKNEE + (MAX_NNKNEE-MIN_NNKNEE)*nnoutput[0] #right knee [-20, 20]
			#output [back knee, back hip, 0.0, fro
			desired_pos.append(hip_to_POS(nnoutput[7].get_output())*2) #right hip convert from [0, 1] to [0, 1024]
			desired_pos.append(knee_to_POS(nnoutput[6].get_output())*2) #right knee convert from [0, 1] to [1024, 0]
					
			desired_pos.append(hip_to_POS(nnoutput[1].get_output())*2)#back hip 
			desired_pos.append(knee_to_POS(nnoutput[0].get_output())*2) #back knee
					
			desired_pos.append(hip_to_POS(nnoutput[4].get_output())*2) #front hip
			desired_pos.append(knee_to_POS(nnoutput[5].get_output())*2) #front knee
					
			desired_pos.append(hip_to_POS(nnoutput[10].get_output())*2) #left hip
			desired_pos.append(knee_to_POS(nnoutput[11].get_output())*2) #left knee
				
			#if(commanded_pos is empty) 
			#current_pos = desired_pos
			#if(not commanded_pos):
			commanded_pos = []
			for p in desired_pos:
				commanded_pos.append(p)
			#for node in nnoutput:
	                 #       print node.get_output() 
			#Move Aracna using nn output
			#if (is_reached(current_pos, commanded_pos)

			print"desired_pos", desired_pos
			val = "\tdesired_pos: {0}".format( desired_pos)
			line = str(val)
			f.write(line)
			robot.commandPosition(commanded_pos, False)
			first = False

			#sleep(2)


if __name__ == '__main__':
	main(sys.argv[1:])
