'''
Aracna Firmware Tester
Copyright (c) Cornell Creative Machines Lab, 2012
http://creativemachines.cornell.edu
Authored by Jeremy Blum
'''

#import necessary libraries
import serial
import time
import msvcrt

#init variables
success = 0

#Connect to the XBEE
port = raw_input('What COM port is your XBEE Radio Connected to (Enter number, ex: 2)? ')
while (not success):
    try:
        ser = serial.Serial("COM%s" % port, 38400)
        success = 1
    except Exception, e:
        port = raw_input("I can't open that Serial port.  Please choose another serial port number: ")


print ("\nThanks!  I'm going run continuously, exercising my functionality.\nI will ACK each command sent from your computer.\n"),
time.sleep(1)

while (1):

    print ("Moving all steppers to Position 20:    "),
    ser.write (".c20,20\n")
    print (ser.readline()),
    time.sleep(3)
    print ("Moving all steppers to Position 500: "),
    ser.write (".c500,500\n")
    print (ser.readline()),
    time.sleep(3)




