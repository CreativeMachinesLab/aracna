#!/usr/bin/env python

""" 
  PyPose: Bioloid pose system for arbotiX robocontroller
  Copyright (c) 2008-2010 Michael E. Ferguson.  All right reserved.

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software Foundation,
  Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import wx
from math import cos,sin,atan2,sqrt,acos
from NukeEditor import NukeDialog

# Some preliminaries
def sq(x):  
    return x*x
# Convert radians to servo position offset.
def radToServo(rads, resolution = 1024):
    if resolution == 4096:
        val = (rads*100)/51 * 25;
        return int(val)
    else: 
        val = (rads*100)/51 * 100;
        return int(val)

COXA = 0
FEMUR = 1
TIBIA = 2

class lizard3(dict):
    X_COXA = 50     # MM between front and back legs /2
    Y_COXA = 50     # MM between front/back legs /2

    L_COXA = 50     # MM distance from coxa servo to femur servo 
    L_FEMUR = 50    # MM distance from femur servo to tibia servo 
    L_TIBIA = 50    # MM distance from tibia servo to foot 

    bodyRotX = 0.0
    bodyRotY = 0.0
    bodyRotZ = 0.0

    bodyPosX = 0.0
    bodyPosY = 0.0

    def setNextPose(self, servo, pos):
        self.nextPose[servo] = pos

    def __init__(self, opt=4, debug=False, gaitGen = None):
        self.legs = int(opt)    # option here corresponds to leg count
        self.debug = debug      # do we print debug messages or not?
        self.gaitGen = gaitGen  # any gait generation? 

        # Column 1 = Body Dimensions, need both specification of layout and data.
        self.vars_layout = [["Leg", 0, 1, 2, "leg.jpg"], ["Offsets",3,4,5,"body.jpg"], ["COG Offsets",6,7,""]]
        self.vars = { 0:["Coxa(mm)",50],1:["Femur(mm)",50],2:["Tibia(mm)",50],3:["X(mm)",50],4:["Y(mm)",50],5:["Mid-Y(mm)",50],6:["X(mm)",0],7:["Y(mm)",0] }
        
        # Column 3 = Servo Values, need both specification of layout and data. 
        self.servo_layout = ["LF Coxa","RF Coxa","LF Femur","RF Femur","LF Tibia","RF Tibia","","","LM Coxa","RM Coxa","LM Femur","RM Femur","LM Tibia","RM Tibia","","","LR Coxa","RR Coxa","LR Femur","RR Femur","LR Tibia","RR Tibia"]
        self.servos = { "RF Coxa":1, "RF Femur":3, "RF Tibia":5, "LF Coxa":2,"LF Femur": 4,"LF Tibia":6,"RR Coxa":7, "RR Femur":9, "RR Tibia":11, "LR Coxa":8, "LR Femur":10, "LR Tibia":12, "RM Coxa":13,"RM Femur":15,"RM Tibia":17,"LM Coxa":14,"LM Femur":16, "LM Tibia":18}

        # Used for gait generation.
        self["RIGHT_FRONT"] = [60,90,100]
        self["RIGHT_REAR"] = [-60,90,100]
        self["LEFT_FRONT"] = [60,-90,100]
        self["LEFT_REAR"] = [-60,-90,100]
        self["RIGHT_MIDDLE"] = [0,90,100]
        self["LEFT_MIDDLE"] = [0,-90,100]
        self["RF_GAIT"] = [0,0,0,0]
        self["LF_GAIT"] = [0,0,0,0]
        self["RR_GAIT"] = [0,0,0,0]
        self["LR_GAIT"] = [0,0,0,0]
        self["RM_GAIT"] = [0,0,0,0]
        self["LM_GAIT"] = [0,0,0,0]
        self.order = {"RF_GAIT":0,"LR_GAIT":2,"LF_GAIT":4,"RR_GAIT":6}

        # Used to generate servo values for IK
        self.mins = [512 for i in range(3*self.legs+1)]
        self.maxs = [512 for i in range(3*self.legs+1)]
        self.resolution = [1024 for i in range(3*self.legs+1)]
        self.neutrals = [512 for i in range(3*self.legs+1)]
        self.nextPose = [512 for i in range(3*self.legs+1)]
        self.signs = [1 for i in range(3*self.legs+1)]
        self.step = 0

    def config(self, opt, dims=None, servos=None, resolutions=None):
        self.legs = int(opt)

        # VARS = coxaLen, femurLen, tibiaLen, xBody, yBody, midyBody, xCOG, yCOG
        if dims != None:
            self.L_COXA = dims[0]
            self.L_FEMUR = dims[1]
            self.L_TIBIA = dims[2]
            self.X_COXA = dims[3]
            self.Y_COXA = dims[4]
            self.Y_MID = dims[5]
            # cogs? 

        # SERVOS = Coxa, Femur, Tibia (LF, RF, LM, RM, LR, RR)
        if servos != None:
            self.servos["LF Coxa"] = servos[0]
            self.servos["RF Coxa"] = servos[1]
            self.servos["LF Femur"] = servos[2]
            self.servos["RF Femur"] = servos[3]
            self.servos["LF Tibia"] = servos[4]
            self.servos["RF Tibia"] = servos[5]

            self.servos["LM Coxa"] = servos[6]
            self.servos["RM Coxa"] = servos[7]
            self.servos["LM Femur"] = servos[8]
            self.servos["RM Femur"] = servos[9]
            self.servos["LM Tibia"] = servos[10]
            self.servos["RM Tibia"] = servos[11]

            self.servos["LR Coxa"] = servos[12]
            self.servos["RR Coxa"] = servos[13]
            self.servos["LR Femur"] = servos[14]
            self.servos["RR Femur"] = servos[15]
            self.servos["LR Tibia"] = servos[16]
            self.servos["RR Tibia"] = servos[17]

        # set resolution of each servo
        if resolutions != None:
            self.resolutions = resolutions
    
    def adjustPanel(self, panel):
        for var in panel.vars:  
            var.Enable()
        if self.legs > 4:
            for servo in panel.servos:
                servo.Enable()
        else:
            panel.vars[5].Disable()
            for i in range(6):
                panel.servos[i].Enable()
                panel.servos[6+i].Disable()
                panel.servos[12+i].Enable()

    def bodyIK(self, X, Y, Z, Xdisp, Ydisp, Zrot):
        """ Compute offsets based on Body positions. 
          BodyIK based on the work of Xan """    
        ans = [0,0,0]   # (X,Y,Z)
    
        cosB = cos(self.bodyRotX)
        sinB = sin(self.bodyRotX)
        cosG = cos(self.bodyRotY)
        sinG = sin(self.bodyRotY)
        cosA = cos(self.bodyRotZ+Zrot)
        sinA = sin(self.bodyRotZ+Zrot)
    
        totalX = int(X + Xdisp + self.bodyPosX); 
        totalY = int(Y + Ydisp + self.bodyPosY); 
    
        ans[0] = int(totalX - int(totalX*cosG*cosA + totalY*sinB*sinG*cosA + Z*cosB*sinG*cosA - totalY*cosB*sinA + Z*sinB*sinA)) + self.bodyPosX
        ans[1] = int(totalY - int(totalX*cosG*sinA + totalY*sinB*sinG*sinA + Z*cosB*sinG*sinA + totalY*cosB*cosA - Z*sinB*cosA)) + self.bodyPosY
        ans[2] = int(Z - int(-totalX*sinG + totalY*sinB*cosG + Z*cosB*cosG))
        
        if self.debug:        
            print "BodyIK:",ans
        return ans

    def legIK(self, X, Y, Z, resolution):
        """ Compute leg servo positions. """
        ans = [0,0,0,0]    # (coxa, femur, tibia)
       
        try:
            # first, make this a 2DOF problem... by solving coxa
            ans[0] = radToServo(atan2(X,Y), resolution)
            trueX = int(sqrt(sq(X)+sq(Y))) - self.L_COXA
            im = int(sqrt(sq(trueX)+sq(Z)))  # length of imaginary leg
            
            # get femur angle above horizon...
            q1 = -atan2(Z,trueX)
            d1 = sq(self.L_FEMUR)-sq(self.L_TIBIA)+sq(im)
            d2 = 2*self.L_FEMUR*im
            q2 = acos(d1/float(d2))
            ans[1] = radToServo(q1+q2, resolution)  
        
            # and tibia angle from femur...
            d1 = sq(self.L_FEMUR)-sq(im)+sq(self.L_TIBIA)
            d2 = 2*self.L_TIBIA*self.L_FEMUR;
            ans[2] = radToServo(acos(d1/float(d2))-1.57, resolution)
        except:
            if self.debug:
                "LegIK FAILED"
            return [1024,1024,1024,0]

        if self.debug:
            print "LegIK:",ans
        return ans

    def doIK(self):
        fail = 0
        req = [0,0,0,0]     # [x,y,z,r]
        gait = [0,0,0,0]    # [x,y,z,r]
        sol = [0,0,0]       # [coxa,femur,tibia]

        # right front leg
        if self.gaitGen != None:
            gait = self.gaitGen("RF_GAIT")    
        if self.debug:
            print "RIGHT_FRONT: ", [self["RIGHT_FRONT"][i] + gait[i] for i in range(3)]
        servo = self.servos["RF Coxa"]  
        req = self.bodyIK(self["RIGHT_FRONT"][0]+gait[0], self["RIGHT_FRONT"][1]+gait[1], self["RIGHT_FRONT"][2]+gait[2], self.X_COXA, self.Y_COXA, gait[3])
        sol = self.legIK(self["RIGHT_FRONT"][0]+req[0]+gait[0],self["RIGHT_FRONT"][1]+req[1]+gait[1],self["RIGHT_FRONT"][2]+req[2]+gait[2], self.resolutions[servo])
        output = self.neutrals[servo]+self.signs[servo]*sol[COXA]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "RF_COXA FAIL: ", output
            fail = fail + 1
        servo = self.servos["RF Femur"]
        output = self.neutrals[servo]+self.signs[servo]*sol[FEMUR]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "RF_FEMUR FAIL: ", output
            fail = fail + 1
        servo = self.servos["RF Tibia"]
        output = self.neutrals[servo]+self.signs[servo]*sol[TIBIA]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:            
            if self.debug:
                print "RF_TIBIA FAIL: ",output
            fail = fail + 1
        
        # right rear leg 
        if self.gaitGen != None:
            gait = self.gaitGen("RR_GAIT")    
        if self.debug:
            print "RIGHT_REAR: ", [self["RIGHT_REAR"][i] + gait[i] for i in range(3)]
        servo = self.servos["RR Coxa"]
        req = self.bodyIK(self["RIGHT_REAR"][0]+gait[0],self["RIGHT_REAR"][1]+gait[1],self["RIGHT_REAR"][2]+gait[2], -self.X_COXA, self.Y_COXA, gait[3])
        sol = self.legIK(-self["RIGHT_REAR"][0]-req[0]-gait[0],self["RIGHT_REAR"][1]+req[1]+gait[1],self["RIGHT_REAR"][2]+req[2]+gait[2], self.resolutions[servo])
        output = self.neutrals[servo]+self.signs[servo]*sol[COXA]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "RR_COXA FAIL: ", output
            fail = fail + 1
        servo = self.servos["RR Femur"]
        output = self.neutrals[servo]+self.signs[servo]*sol[FEMUR]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "RR_FEMUR FAIL:", output
            fail = fail + 1
        servo = self.servos["RR Tibia"]
        output = self.neutrals[servo]+self.signs[servo]*sol[TIBIA]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "RR_TIBIA FAIL:", output
            fail = fail + 1
        
        # left front leg
        if self.gaitGen != None:
            gait = self.gaitGen("LF_GAIT")    
        if self.debug:
            print "LEFT_FRONT: ", [self["LEFT_FRONT"][i] + gait[i] for i in range(3)]
        servo = self.servos["LF Coxa"]
        req = self.bodyIK(self["LEFT_FRONT"][0]+gait[0],self["LEFT_FRONT"][1]+gait[1],self["LEFT_FRONT"][2]+gait[2], self.X_COXA, -self.Y_COXA, gait[3])
        sol = self.legIK(self["LEFT_FRONT"][0]+req[0]+gait[0],-self["LEFT_FRONT"][1]-req[1]-gait[1],self["LEFT_FRONT"][2]+req[2]+gait[2], self.resolutions[servo])
        output = self.neutrals[servo]+self.signs[servo]*sol[COXA]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "LF_COXA FAIL:", output
            fail = fail + 1
        servo = self.servos["LF Femur"]
        output = self.neutrals[servo]+self.signs[servo]*sol[FEMUR]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print"LF_FEMUR FAIL:", output
            fail = fail + 1
        servo = self.servos["LF Tibia"]
        output = self.neutrals[servo]+self.signs[servo]*sol[TIBIA]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "LF_TIBIA FAIL:", output
            fail = fail + 1

        # left rear leg
        if self.gaitGen != None:
            gait = self.gaitGen("LR_GAIT")   
        if self.debug:
            print "LEFT_REAR: ", [self["LEFT_REAR"][i] + gait[i] for i in range(3)]
        servo = self.servos["LR Coxa"]
        req = self.bodyIK(self["LEFT_REAR"][0]+gait[0],self["LEFT_REAR"][1]+gait[1],self["LEFT_REAR"][2]+gait[2], -self.X_COXA, -self.Y_COXA, gait[3])
        sol = self.legIK(-self["LEFT_REAR"][0]-req[0]-gait[0],-self["LEFT_REAR"][1]-req[1]-gait[1],self["LEFT_REAR"][2]+req[2]+gait[2], self.resolutions[servo])
        output = self.neutrals[servo]+self.signs[servo]*sol[COXA]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "LR_COXA FAIL:", output
            fail = fail + 1
        servo = self.servos["LR Femur"]
        output = self.neutrals[servo]+self.signs[servo]*sol[FEMUR]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "LR_FEMUR FAIL:",output
            fail = fail + 1
        servo = self.servos["LR Tibia"]        
        output = self.neutrals[servo]+self.signs[servo]*sol[TIBIA]
        if output < self.maxs[servo] and output > self.mins[servo]:
            self.setNextPose(servo, output)
        else:
            if self.debug:
                print "LR_TIBIA FAIL:", output
            fail = fail + 1
    
        if self.legs > 4:
            # right middle leg
            if self.gaitGen != None:
                gait = self.gaitGen("RM_GAIT")    
            if self.debug:
                print "RIGHT_MIDDLE: ", [self["RIGHT_MIDDLE"][i] + gait[i] for i in range(3)]
            servo = self.servos["RM Coxa"]
            req = self.bodyIK(self["RIGHT_MIDDLE"][0]+gait[0],self["RIGHT_MIDDLE"][1]+gait[1],self["RIGHT_MIDDLE"][2]+gait[2], 0, self.Y_MID, gait[3])
            sol = self.legIK(+self["RIGHT_MIDDLE"][0]+req[0]+gait[0],self["RIGHT_MIDDLE"][1]+req[1]+gait[1],self["RIGHT_MIDDLE"][2]+req[2]+gait[2], self.resolutions[servo])
            output = self.neutrals[servo]+self.signs[servo]*sol[COXA]
            if output < self.maxs[servo] and output > self.mins[servo]:
                self.setNextPose(servo, output)
            else:
                if self.debug:
                    print "RM_COXA FAIL:", output
                fail = fail + 1
            servo = self.servos["RM Femur"]
            output = self.neutrals[servo]+self.signs[servo]*sol[FEMUR]
            if output < self.maxs[servo] and output > self.mins[servo]:
                self.setNextPose(servo, output)
            else:
                if self.debug:
                    print"RM_FEMUR FAIL:", output
                fail = fail + 1
            servo = self.servos["RM Tibia"]
            output = self.neutrals[servo]+self.signs[servo]*sol[TIBIA]
            if output < self.maxs[servo] and output > self.mins[servo]:
                self.setNextPose(servo, output)
            else:
                if self.debug:
                    print "RM_TIBIA FAIL:", output
                fail = fail + 1

            # left middle leg
            if self.gaitGen != None:
                gait = self.gaitGen("LM_GAIT")    
            if self.debug:
                print "LEFT_MIDDLE: ", [self["LEFT_MIDDLE"][i] + gait[i] for i in range(3)]
            servo = self.servos["LM Coxa"] 
            req = self.bodyIK(self["LEFT_MIDDLE"][0]+gait[0],self["LEFT_MIDDLE"][1]+gait[1],self["LEFT_MIDDLE"][2]+gait[2], 0, -self.Y_MID, gait[3])
            sol = self.legIK(self["LEFT_MIDDLE"][0]+req[0]+gait[0],-self["LEFT_MIDDLE"][1]-req[1]-gait[1],self["LEFT_MIDDLE"][2]+req[2]+gait[2], self.resolutions[servo])
            output = self.neutrals[servo]+self.signs[servo]*sol[COXA]
            if output < self.maxs[servo] and output > self.mins[servo]:
                self.setNextPose(servo, output)
            else:
                if self.debug:
                    print "LM_COXA FAIL:", output
                fail = fail + 1
            servo = self.servos["LM Femur"]
            output = self.neutrals[servo]+self.signs[servo]*sol[FEMUR]
            if output < self.maxs[servo] and output > self.mins[servo]:
                self.setNextPose(servo, output)
            else:
                if self.debug:
                    print "LM_FEMUR FAIL:",output
                fail = fail + 1
            servo = self.servos["LM Tibia"]        
            output = self.neutrals[servo]+self.signs[servo]*sol[TIBIA]
            if output < self.maxs[servo] and output > self.mins[servo]:
                self.setNextPose(servo, output)
            else:
                if self.debug:
                    print "LM_TIBIA FAIL:", output
                fail = fail + 1
       
        self.step = self.step + 1
        if self.step > 7:
            self.step = 0   #gaitStep = (gaitStep+1)%stepsInGait
        return fail

    def defaultGait(self,leg):        
        # just walk forward for now
        travelX = 50
        travelY = 0
        travelRotZ = 0

        if abs(travelX)>5 or abs(travelY)>5 or abs(travelRotZ) > 0.05:   # are we moving?
            if(self.order[leg] == self.step):
                # up, middle position                    
                self[leg][0] = 0        # x
                self[leg][1] = 0        # y
                self[leg][2] = -20      # z
                self[leg][3] = 0        # r
            elif (self.order[leg]+1 == self.step) or (self.order[leg]-7 == self.step):   # gaits in step -1 
                # leg down!                    
                self[leg][0] = travelX/2
                self[leg][1] = travelY/2
                self[leg][2] = 0       
                self[leg][3] = travelRotZ/2      
            else:
                # move body forward 
                self[leg][0] = self[leg][0] - travelX/6
                self[leg][1] = self[leg][1] - travelY/6
                self[leg][2] = 0       
                self[leg][3] = self[leg][3] - travelRotZ/6    
        return self[leg]

    def strRep(self, t):
        if t > 0:
            return "+"
        else:
            return "-"

    def doSignTest(self,parent,step=0):
        if step == 0:
            print "Moving to neutral positions"
            self["RIGHT_FRONT"] = [0,self.L_FEMUR+self.L_COXA,self.L_TIBIA]
            self["RIGHT_REAR"] = [0,self.L_FEMUR+self.L_COXA,self.L_TIBIA]
            self["LEFT_FRONT"] = [0,-self.L_FEMUR-self.L_COXA,self.L_TIBIA]
            self["LEFT_REAR"] = [0,-self.L_FEMUR-self.L_COXA,self.L_TIBIA]
            self["RIGHT_MIDDLE"] = [0,self.L_FEMUR+self.L_COXA,self.L_TIBIA]
            self["LEFT_MIDDLE"] = [0,-self.L_FEMUR-self.L_COXA,self.L_TIBIA]
            self.doIK()
            parent.writePose(self.nextPose, 500)
            dlg = wx.MessageDialog(parent, "Click OK when ready!", 'Sign Test', wx.OK)
            if dlg.ShowModal() == wx.ID_OK:    
                return self.doSignTest(parent,1)
            else:
                return "".join([self.strRep(t) for t in self.signs[1:]])   
        else:
            msg = ""            # message to display to user
            servo = -1          # servo ID to reverse if we get a NCK    
            if step == 1:
                # SET COXAS FIRST
                self["RIGHT_FRONT"][0] = self.L_COXA/2
                msg = "Did my RF leg move forward?"
                servo = "RF Coxa"
            elif step == 2:
                self["LEFT_FRONT"][0] = self.L_COXA/2
                msg = 'Did my LF leg move forward?'
                servo = "LF Coxa"
            elif step == 3:
                self["RIGHT_REAR"][0] = -self.L_COXA/2
                msg = 'Did my RR leg move backward?'
                servo = "RR Coxa"
            elif step == 4:
                self["LEFT_REAR"][0] = -self.L_COXA/2
                msg = 'Did my LR leg move backward?'
                servo = "LR Coxa"
            elif step == 5:
                # Now FEMURs and TIBIAs
                self["RIGHT_FRONT"][2] = self["RIGHT_FRONT"][2] - 20
                msg = 'Did my RF leg move upward?'
                servo = "RF Femur"
            elif step == 6: 
                msg = 'Is my RF tibia still straight up and down?'
                servo = "RF Tibia"
            elif step == 7:
                self["LEFT_FRONT"][2] = self["LEFT_FRONT"][2] - 20
                msg = 'Did my LF leg move upward?'
                servo = "LF Femur"
            elif step == 8:
                msg = 'Is my LF tibia still straight up and down?'
                servo = "LF Tibia"
            elif step == 9:
                self["RIGHT_REAR"][2] = self["RIGHT_REAR"][2] - 20
                msg = 'Did my RR leg move upward?'
                servo = "RR Femur"
            elif step == 10:
                msg = 'Is my RR tibia still straight up and down?'
                servo = "RR Tibia"
            elif step == 11:
                self["LEFT_REAR"][2] = self["LEFT_REAR"][2] - 20
                msg = 'Did my LR leg move upward?'
                servo = "LR Femur"
            elif step == 12:
                msg = 'Is my LR tibia still straight up and down?'
                servo = "LR Tibia"   
            elif step == 13:
                # middle legs
                self["RIGHT_MIDDLE"][0] = self.L_COXA/2
                msg = "Did my RM leg move forward?"
                servo = "RM Coxa"
            elif step == 14:
                self["LEFT_MIDDLE"][0] = self.L_COXA/2
                msg = "Did my LM leg move forward?"
                servo = "LM Coxa"
            elif step == 15:
                self["RIGHT_MIDDLE"][2] = self["RIGHT_MIDDLE"][2] - 20
                msg = 'Did my RM leg move upward?'
                servo = "RM Femur"
            elif step == 16:
                msg = 'Is my RM tibia still straight up and down?'
                servo = "RM Tibia"
            elif step == 17:
                self["LEFT_MIDDLE"][2] = self["LEFT_MIDDLE"][2] - 20
                msg = 'Did my LM leg move upward?'
                servo = "LM Femur"
            elif step == 18:
                msg = 'Is my LM tibia still straight up and down?'
                servo = "LM Tibia"  

            # do IK and display dialog
            self.doIK()
            parent.writePose(self.nextPose, 500)
            dlg = wx.MessageDialog(parent, msg, 'Sign Test', wx.YES | wx.NO)
            result = dlg.ShowModal()    
            if result == wx.ID_CANCEL:
                return "".join([self.strRep(t) for t in self.signs[1:]])            
            elif result == wx.ID_NO:
                print "Reversing", servo, "sign"       
                if self.signs[self.servos[servo]] > 0:
                    self.signs[self.servos[servo]] = -1
                else:
                    self.signs[self.servos[servo]] = 1
                self.doIK()
                parent.writePose(self.nextPose, 500)
            if step < (3*self.legs):
                return self.doSignTest(parent,step+1)
            else:
                return "".join([self.strRep(t) for t in self.signs[1:]])

