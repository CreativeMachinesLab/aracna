import os, dynamixel, time, random

# The number of Dynamixels on our bus.
nServos = 11

# Set your serial port accordingly.
if os.name == "posix":
    portName = "/dev/ttyUSB0"
else:
    portName = "COM11"
    
# Default baud rate of the USB2Dynamixel device.
baudRate = 1000000

serial = dynamixel.SerialStream( port=portName, baudrate=baudRate, timeout=1)
net = dynamixel.DynamixelNetwork( serial )
net.scan( 1, nServos )

myActuators = list()

print "Scanning for Dynamixels...",
for dyn in net.get_dynamixels():
    print dyn.id,
    myActuators.append(net[dyn.id])
print "...Done"

        
for actuator in myActuators:
    actuator.moving_speed = 50
    actuator.synchronized = True
    actuator.torque_enable = True
    actuator.torque_limit = 800
    actuator.max_torque = 800

while True:
    for actuator in myActuators:
        actuator.goal_position = random.randrange(450, 600)
    net.synchronize()
    for actuator in myActuators:
        actuator.read_all()
        time.sleep(0.01)
    for actuator in myActuators:
        print actuator.cache[dynamixel.defs.REGISTER['Id']], actuator.cache[dynamixel.defs.REGISTER['CurrentPosition']]
    time.sleep(2)

    

        
        