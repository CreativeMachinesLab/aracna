'''
Creative Machines Lab Aracna Firmware Tester
pyTest.py - General Firmware Tester
Copyright (c) Creative Machines Lab, Cornell University, 2012 - http://www.creativemachines.org
Authored by Jeremy Blum - http://www.jeremyblum.com

LICENSE: GPLv3
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

#import necessary libraries
import serial
import time

#Configuration Variables
sleep_time = 0 #in seconds between movements

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

    print ("Moving all steppers to Position 20:  "),
    ser.write (".c20,20\n")
    print (ser.readline()),
    time.sleep(sleep_time)
    print ("Moving all steppers to Position 500: "),
    ser.write (".c500,500\n")
    print (ser.readline()),
    time.sleep(sleep_time)




