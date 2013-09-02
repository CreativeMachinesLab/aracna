#!/usr/bin/env python2.6

"""
This is a Python version of the ForestMoon Dynamixel library originally
written in C# by Scott Ferguson.

The Python version was created by Patrick Goebel (mailto:patrick@pirobot.org)
for the Pi Robot Project which lives at http://www.pirobot.org.

The original license for the C# version is as follows:

This software was written and developed by Scott Ferguson.
The current version can be found at http://www.forestmoon.com/Software/.
This free software is distributed under the GNU General Public License.
See http://www.gnu.org/licenses/gpl.html for details.
This license restricts your usage of the software in derivative works.

* * * * * 

Module wide definitions

"""

import enumeration

ERROR_STATUS = enumeration.Enumeration( [
        ('None',0x0,"None"),
        ('InputVoltage', 0x1, "Input Voltage Error"),
        ('AngleLimit', 0x2, "Angle Limit Error"),
        ('Overheating', 0x4, "Overheating Error"),
        ('Range', 0x8,"Range Error"),
        ('Checksum', 0x10,"Checksum Error"),
        ('Overload', 0x20,"Overload Error"),
        ('Instruction', 0x40,"Instruction Error" ) ] )

BAUD_RATE = enumeration.Enumeration( [
        ('Baud_1000000', 1),
        ('Baud_500000', 3),
        ('Baud_400000', 4),
        ('Baud_250000', 7),
        ('Baud_200000', 9),
        ('Baud_115200', 0x10),
        ('Baud_57600', 0x22),
        ('Baud_19200', 0x67),
        ('Baud_9600', 0xcf)
        ])

REGISTER = enumeration.Enumeration( [
   ('ModelNumber',  0, "Model Number"),
   ('FirmwareVersion',  2, "Firmware Version"),
   ('Id', 3, "Id"),
   ('BaudRate',  4, "Baud Rate"),
   ('ReturnDelay',  5, "Return Delay"),
   ('CWAngleLimit',  6, "CW Angle Limit"),
   ('CCWAngleLimit',  8, "CCW Angle Limit"),
   ('TemperatureLimit',  11, "Temperature Limit"),
   ('LowVoltageLimit',  12, "Low Voltage Limit"),
   ('HighVoltageLimit',  13, "High Voltage Limit"),
   ('MaxTorque',  14, "Max Torque"),
   ('StatusReturnLevel',  16, "Status Return Level"),
   ('AlarmLED',  17, "Alarm Led"),
   ('AlarmShutdown',  18, "Alarm Shutdown"),
   ('DownCalibration',  20, "Down Calibration"),
   ('UpCalibration',  22, "Up Calibration"),
   ('TorqueEnable',  24, "Torque Enable"),
   ('LED',  25, "LED"),
   ('CWComplianceMargin',  26, "CW Compliance Margin"),
   ('CCWComplianceMargin',  27, "CCW Compliance Margin"),
   ('CWComplianceSlope',  28, "CW Compliance Slope"),
   ('CCWComplianceSlope',  29, "CCW Compliance Slope"),
   ('GoalPosition', 30, "Goal Position"),
   ('MovingSpeed', 32, "Moving Speed"),
   ('TorqueLimit',  34, "Torque Limit"),
   ('CurrentPosition',  36, "Current Position"),
   ('CurrentSpeed',  38, "Current Speed"),
   ('CurrentLoad',  40, "Current Load"),
   ('CurrentVoltage',  42, "Current Voltage"),
   ('CurrentTemperature',  43, "Current Temperature"),
   ('RegisteredInstruction',  44, "Registered Instruction"),
   ('Moving',  46, "Moving"),
   ('Lock',  47, "Lock"),
   ('Punch',  48, "Punch" )])

STATUS_RETURN_LEVEL = enumeration.Enumeration( [
       ('NoResponse', 0),
       ('RespondToReadData', 1),
       ('RespondToAll', 2 )])

INSTRUCTION = enumeration.Enumeration( [
       ('Ping', 1, "Respond only with a status packet."),
       ('ReadData', 2, "Read register data."),
       ('WriteData', 3, "Write register data."),
       ('RegWrite', 4, "Delay writing register data until an Action \
instruction is received."),
       ('Action', 5, "Perform pending RegWrite instructions."),
       ('Reset', 6, "Reset all registers (including ID) to default values."),
       ('SyncWrite',  0x83, "Write register data to multiple \
Dynamixels at once. ") 
       ] )
