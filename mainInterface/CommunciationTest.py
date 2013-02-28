import serial
import time

class Tester:
    def __init__(self):
        self.startTime = time.clock()
        self.bytesToRead = 4
        
        self.failedPackets = 0
        self.successfulPackets = 0
        
        self.data = ["a", "b", "c", "d", "e"]
        
        self.initialStartCode = chr(0xff) + chr(0xff) + chr(0xfe)
        
        self.ser = serial.Serial("COM7",38400, timeout=0.015)
    
    '''Prints the runtime in seconds'''    
    def tic(self):
        self.startTime = time.clock()
    def toc(self):
        print str(time.clock() - self.startTime)
    
    '''This one works pretty fast'''
    def onlyRead(self):
        while True:
            self.tic()
            print self.ser.read(3)
            self.toc()
    
    '''This one works fast if the timeout on the serial
    connection is set. If it's not set, it gets stuck.'''
    def writeAndRead(self):
        while True:
            print "here"
            self.ser.write("a")
            print self.ser.read(3)
        
    def main(self):
        '''Establishes a two-way (handshaking) connection with the
        ArbotiX board. The current communication rate is ~60Hz.'''
        
        #Write many packets until we establish an actual connection
        while self.successfulPackets < 1:
            #self.sendAndRecieve()
            self.ser.write(self.initialStartCode)
            input = self.ser.read(len(self.initialStartCode))
            
            if input == self.initialStartCode:
                self.successfulPackets += 1
            else:
                self.failedPackets += 1
        
        #Connection established. Wait forever for future packets.
        self.ser.setTimeout(None)
        
        #Write the rest of the packets. None should be dropped.
        self.tic()
        while self.successfulPackets < 1000:
            self.sendAndRecieve()
        self.toc()

    def sendAndRecieve(self):
        '''Send and try to read a packet from the ArbotiX'''
        
        self.ser.write(self.data[(self.successfulPackets) % len(self.data)])
        input = self.ser.read(self.bytesToRead)
        
        if input == "":    
           input = "0"
           self.failedPackets += 1
        if "1" in input:
            self.successfulPackets += 1
         
        print input + ", " + str(self.successfulPackets) + ", " +\
        str(self.failedPackets)

if __name__ == '__main__':
    Tester().main()
#    Tester().onlyRead()
#    Tester().writeAndRead()