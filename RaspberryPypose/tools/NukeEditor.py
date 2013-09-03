#!/usr/bin/env python

""" 
  PyPose: Bioloid pose system for arbotiX robocontroller
  Nuke: The Nearly Universal Kinematics Engine
  Copyright (c) 2009-2010 Michael E. Ferguson.  All right reserved.

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

import wx, sys, os
import project
from ToolPane import ToolPane
from ax12 import *
import time
from commander import Commander

# Which IK models to load?
from models.manifest import iKmodels

###############################################################################
# nuke editor window
class NukeEditor(ToolPane):
    """ editor for NUKE engine. """
    BT_RELAX = wx.NewId()
    BT_LIMITS = wx.NewId()
    BT_NEUTRAL = wx.NewId()
    BT_SIGN = wx.NewId()
    BT_TUNER = wx.NewId()
    BT_EXPORT = wx.NewId()
    BT_DRIVE = wx.NewId()
    ID_IKTYPE = wx.NewId()
    ID_IKOPT = wx.NewId()
    ID_GAIT_BOX = wx.NewId()
    ID_ANY = wx.NewId()

    def __init__(self, parent, port=None):
        ToolPane.__init__(self, parent, port)
        # default data
        self.signs = "+"*18
        self.curpose = "" 
        self.ikChoice = ""
        self.optChoice = ""
        
        self.sizer = wx.GridBagSizer(10,10)
    
        # IK styles/Config
        temp = wx.StaticBox(self, -1, 'IK Config')
        temp.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        configBox = wx.StaticBoxSizer(temp,orient=wx.VERTICAL) 
        configSizer = wx.GridBagSizer(5,5)
        configSizer.Add(wx.StaticText(self, -1, "IK Type:"),(0,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL|wx.TOP,10)
        self.ikType = wx.ComboBox(self, self.ID_IKTYPE, choices=iKmodels.keys())
        configSizer.Add(self.ikType,(0,1),wx.GBSpan(1,1),wx.TOP,10)   
        
        # IK Option (typical # of legs or # of DOF)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.optLabel = wx.StaticText(self, -1, "# of Legs:")
        configSizer.Add(self.optLabel,(1,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
        self.ikOpt = wx.ComboBox(self, self.ID_IKOPT, choices=["4","6"])
        configSizer.Add(self.ikOpt,(1,1))     
        configBox.Add(configSizer)
        self.sizer.Add(configBox, (0,1), wx.GBSpan(1,1), wx.EXPAND)

        # Actions buttons
        temp = wx.StaticBox(self, -1, 'Actions')
        temp.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        actionBox = wx.StaticBoxSizer(temp,orient=wx.VERTICAL) 
        actionSizer = wx.GridBagSizer(5,5)

        actionSizer.Add(wx.StaticText(self, -1, "Capture Limits:"), (0,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
        actionSizer.Add(wx.StaticText(self, -1, "Capture Neutral:"), (1,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
        actionSizer.Add(wx.StaticText(self, -1, "Set/Test Signs:"), (2,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
                
        actionSizer.Add(wx.Button(self, self.BT_LIMITS, 'Capture'),(0,1))
        actionSizer.Add(wx.Button(self, self.BT_NEUTRAL, 'Capture'),(1,1))
        self.signButton = wx.Button(self, self.BT_SIGN, 'Go')        
        actionSizer.Add(self.signButton,(2,1))
        
        actionBox.Add(actionSizer)
        self.sizer.Add(actionBox, (1,1), wx.GBSpan(1,1), wx.EXPAND)    

        # NUKE Label
        nukeIt = wx.StaticText(self, -1, "NUKE: Get Your IK On")
        nukeIt.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD, wx.ITALIC))
        self.sizer.Add(nukeIt, (2,0), wx.GBSpan(1,2), wx.ALIGN_CENTER_VERTICAL)        

        # Buttons
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        gaitBut = wx.Button(self,-1,'Gait Builder')
        gaitBut.Disable()        
        hbox.Add(gaitBut)
        viewBut = wx.Button(self,-1, 'Viewer/Tuner')
        viewBut.Disable()
        hbox.Add(viewBut)
        hbox.Add(wx.Button(self, self.BT_DRIVE, 'Test Drive'))
        hbox.Add(wx.Button(self,self.BT_EXPORT, 'Export'))
        self.sizer.Add(hbox, (2,2), wx.GBSpan(1,1), wx.ALIGN_CENTER) 

        # Load Data (if possible)
        self.loadData()
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

        # event handling
        wx.EVT_BUTTON(self, self.BT_LIMITS, self.doLimits)                
        wx.EVT_BUTTON(self, self.BT_NEUTRAL, self.doNeutral)
        wx.EVT_BUTTON(self, self.BT_SIGN, self.doSignTest) 
        wx.EVT_BUTTON(self, self.BT_DRIVE, self.doWalkTest) 
        wx.EVT_BUTTON(self, self.BT_EXPORT, self.doExport) 

        wx.EVT_COMBOBOX(self, self.ID_IKTYPE, self.doIKType)
        wx.EVT_COMBOBOX(self, self.ID_IKOPT, self.doIkOpt) 
        wx.EVT_SPINCTRL(self, self.ID_ANY, self.save)         
    
    
    ###########################################################################
    # draw buttons, etc. 
    def getModel(self):
        modelClassName = iKmodels[self.ikChoice].folder
        if "tools/models/"+modelClassName not in sys.path:
            sys.path.append("tools/models/"+modelClassName)
        modelModule = __import__(modelClassName, globals(), locals(), [modelClassName])
        modelClass = getattr(modelModule, modelClassName)
        # make instance            
        self.model = modelClass(int(self.optChoice),True)    # dofORlegs/debug/GaitGen
        return self.model

    def makePanel(self):
        if self.ikChoice == "":
            return            
        self.getModel()
        try:
            self.servoBox.Clear(True)
            self.bodyBox.Clear(True)
            self.sizer.Remove(self.servoBox)
            self.sizer.Remove(self.bodyBox)
        except:
            pass

        # Body Dimensions 
        temp = wx.StaticBox(self, -1, 'Body Dimensions')
        temp.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.bodyBox = wx.StaticBoxSizer(temp,orient=wx.VERTICAL) 
        bodySizer = wx.GridBagSizer(5,5)
        index = 0
        self.vars = list()
        for group in self.model.vars_layout:
            # each group has [label, elements, image] 
            bodySizer.Add(wx.StaticText(self, -1, group[0]), (index,0), wx.GBSpan(1,1), wx.EXPAND | wx.TOP, 10)
            index = index + 1
            count = 0
            for field in group[1:-1]:
                d = self.model.vars[field]
                bodySizer.Add(wx.StaticText(self, -1, d[0]), (index,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
                self.vars.append(wx.SpinCtrl(self, self.ID_ANY, str(d[1]), min=-5000, max=5000))
                bodySizer.Add(self.vars[-1], (index,1))
                index = index + 1
                count = count + 1
            if group[-1] != "":
                picture = wx.StaticBitmap(self, bitmap=wx.Bitmap("tools/models/"+iKmodels[self.ikChoice].folder+"/"+group[-1]))
                bodySizer.Add(picture, (index - count,2), wx.GBSpan(count,1))
        self.bodyBox.Add(bodySizer)
        self.sizer.Add(self.bodyBox, (0,0), wx.GBSpan(2,1), wx.EXPAND)

        # Servo ID Selections
        temp = wx.StaticBox(self, -1, 'Servo Assignments')
        temp.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.servoBox = wx.StaticBoxSizer(temp,orient=wx.VERTICAL) 
        servoSizer = wx.GridBagSizer(5,5)
        self.servos = list()
        index = 0
        for servo_name in self.model.servo_layout:
            if servo_name != "":
                servoSizer.Add(wx.StaticText(self, -1, servo_name), (index/2,(index%2)*2), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
                new_servo = wx.SpinCtrl(self, self.ID_ANY, str(self.model.servos[servo_name]), min=1, max=self.parent.project.count)
                self.servos.append(new_servo)
                servoSizer.Add(new_servo, (index/2,(index%2)*2+1), wx.GBSpan(1,1), wx.EXPAND)
            index = index + 1
        self.servoBox.Add(servoSizer)
        self.sizer.Add(self.servoBox, (0,2), wx.GBSpan(2,1), wx.EXPAND)

        self.model.config(self.optChoice)
        self.model.adjustPanel(self)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.parent.sizer.Fit(self.parent)
        self.Refresh()


    ###########################################################################
    # sitrep checks
    def doChecks(self, checks):
        for c in checks:
            if c == "project":
                if self.parent.project.name == "":   
                    self.parent.sb.SetBackgroundColour('RED')
                    self.parent.sb.SetStatusText('please create a project')
                    self.parent.timer.Start(30)
                    return 0
            elif c == "port":
                if self.port == None:
                    self.parent.sb.SetBackgroundColour('RED')
                    self.parent.sb.SetStatusText('No Port Open...')
                    self.parent.timer.Start(30)
                    return 0
            elif c == "ik":
                 if self.ikOpt.GetValue() == "":
                    self.parent.sb.SetBackgroundColour('RED')
                    self.parent.sb.SetStatusText('Please fill in IK variables...')
                    self.parent.timer.Start(30)
                    return 0    
            else:
                print "Unknown System Check:", c
        # all systems go!        
        return 1 

    ###########################################################################
    # data management
    def loadData(self):        
        """ Load the NUKE string from our project, configure screen/model. """
        if self.parent.project.name == "":
            # Disable it all
            self.ikType.Disable()
            self.ikOpt.Disable()
        elif self.parent.project.nuke == "":
            self.ikOpt.Disable()     # Allow selection of ikType
        else:
            nukeStr = self.parent.project.nuke.rstrip()
            # primary data
            self.ikChoice = nukeStr[0:nukeStr.find(",")]
            self.ikType.SetValue(self.ikChoice)
            self.ikType.Disable()   # Can't change type - breaks templates
            nukeStr = nukeStr[nukeStr.find(",")+1:]
            self.optChoice = nukeStr[0:nukeStr.find(",")]
            self.ikOpt.SetValue(self.optChoice)            
            nukeStr = nukeStr[nukeStr.find(",")+1:]
            self.signs = nukeStr[0:nukeStr.find(",")]
            nukeStr = nukeStr[nukeStr.find(",")+1:]
            self.makePanel()
            # load vars
            for i in range(len(self.vars)):
                self.vars[i].SetValue(int(nukeStr[0:nukeStr.find(",")]))
                nukeStr = nukeStr[nukeStr.find(",")+1:]
            # load servos
            for i in range(len(self.servos)-1):
                self.servos[i].SetValue(int(nukeStr[0:nukeStr.find(",")]))
                nukeStr = nukeStr[nukeStr.find(",")+1:]
            self.servos[len(self.servos)-1].SetValue(int(nukeStr))
            # Data loaded, now Enable/Disable as needed
            if self.ikType.GetValue() == "": 
                self.ikOpt.Disable()
            else:
                self.ikOpt.SetItems([str(c) for c in iKmodels[self.ikType.GetValue()].options])
                self.ikOpt.Enable()        
            if self.ikType.GetValue() == "" or self.ikOpt.GetValue() == "":
                # Disable it all
                for var in self.vars:  
                    var.Disable()
                for servo in self.servos:        
                    servo.Disable()
            else:
                self.model.opt = int(self.optChoice)
                self.model.adjustPanel(self)

    def save(self, e=None):     
        """ Export the NUKE string to our project, mark project as needing a save. """
        if self.ikType.GetValue() == "" or self.ikOpt.GetValue() == "":
            return
        nukeStr = self.ikChoice + "," + str(self.ikOpt.GetValue()) + "," + self.signs + ","
        # vars
        for var in self.vars:
            nukeStr = nukeStr + str(var.GetValue()) + ","
        # servos
        for servo in self.servos:
            nukeStr = nukeStr + str(servo.GetValue()) + ","
        nukeStr = nukeStr[0:-1]  # trim last ','
        self.parent.project.nuke = nukeStr
        self.parent.project.save = True
    
    def configModel(self):
        """ Load the model for our IK solution. """
        modelClassName = iKmodels[self.ikChoice].folder
        if "tools/models/"+modelClassName not in sys.path:
            sys.path.append("tools/models/"+modelClassName)
        modelModule = __import__(modelClassName, globals(), locals(), [modelClassName])
        modelClass = getattr(modelModule, modelClassName)
        # make instance            
        model = modelClass(int(self.optChoice),True)    # dofORlegs/debug/GaitGen
        model.config( [int(v.GetValue()) for v in self.vars], [int(s.GetValue()) for s in self.servos])
        model.mins = [512,] + self.parent.project.poses["ik_min"]
        model.maxs = [512,] + self.parent.project.poses["ik_max"]
        model.resolution = [1024,] + self.parent.project.resolution
        model.neutrals = [512,] + self.parent.project.poses["ik_neutral"]
        model.signs = [1,] + [1+(-2*(t=="-")) for t in self.signs]    
        self.model = model

    ###########################################################################
    # holla back -- the simple callbacks 
    def writePose(self, pose, dt):
        # set pose size -- IMPORTANT!
        self.port.execute(253, 7, [self.parent.project.count])
        # download the pose
        self.port.execute(253, 8, [0] + project.extract(pose))                 
        self.port.execute(253, 9, [0, dt%256, dt>>8,255,0,0])                
        self.port.execute(253, 10, list())
    def doSignTest(self, e=None):
        """ Do the sign test, let's hope we pass. This is handled by the model. """
        if self.doChecks(["project","port","ik"]) > 0:
            self.loadModel()
            self.signs = self.model.doSignTest(self) 
            self.save()
    def doWalkTest(self, e=None):
        """ Load a virtual commander, to drive around. """
        # TODO: Popup box telling you not to do this with the PyPose sketch!
        if self.doChecks(["port"]) > 0:
            comm = Commander(self, self.port.ser)    
            comm.Center()    
    def doIKType(self, e=None):
        """ Set IKType, make leg box visible """
        self.ikChoice = self.ikType.GetValue()
        self.optLabel.SetLabel(iKmodels[self.ikChoice].optiondesc)
        self.ikOpt.SetItems([str(c) for c in iKmodels[self.ikChoice].options])
        self.ikOpt.Enable()
        self.optChoice = "4"
        self.makePanel()
    def doIkOpt(self, e=None):
        """ Set the # of legs (or DOF), make everything else visible. """
        self.ikType.Disable()        
        self.optChoice = self.ikOpt.GetValue()
        self.model.config(self.optChoice)
        self.makePanel()
        self.model.adjustPanel(self)
        self.save()

    ###########################################################################
    # Limit & Neutral capture
    def doLimits(self, e=None):
        if self.doChecks(["project","port"]) == 0:
            return
        else:
            print "Relax servos for capture..."
            self.parent.doRelax()
            print "Capturing limits..."
            self.parent.project.poses["ik_min"] = project.pose("",self.parent.project.count)
            self.parent.project.poses["ik_max"] = project.pose("",self.parent.project.count)
            self.parent.project.save = True
            self.captureLimits(1)
    def captureLimits(self, servoID, end=0, prev=0, error=0):
        """ Capture the limits of this servo, recursively call next. """
        if servoID <= self.parent.project.count:
            if end == 0:
                result = wx.ID_OK
                if error == 0:      # first time through, ask user to prepare
                    dlg = NukeDialog(self.parent, 'Capture Limits', 'Click OK when you have moved\n   servo ' + str(servoID) + ' to one extreme')
                    result = dlg.ShowModal()      
                    dlg.Destroy()                 
                if result == wx.ID_OK:
                    try:
                        # read in servo position
                        a = self.port.getReg(servoID,P_PRESENT_POSITION_L, 2)
                        a = a[0] + (a[1]<<8) 
                        # get other limit
                        self.captureLimits(servoID,1,a)
                    except:
                        if error < 3:   # try again
                            self.captureLimits(servoID, 0, 0, error+1)
                        else:           # fail and move on
                            dlg = wx.MessageDialog(self.parent, 'Unable to read servo ' + str(servoID), 'Capture Error', wx.OK)
                            dlg.ShowModal()
                            self.captureLimits(servoID+1)  
                elif result == 42:
                    self.captureLimits(servoID-1)
            else:
                result = wx.ID_OK
                if error == 0:      # first time through, ask user to prepare
                    dlg = NukeDialog(self.parent, 'Capture Limits', 'Click OK when you have moved\n    servo ' + str(servoID) + ' to the other extreme')
                    result = dlg.ShowModal()                   
                    dlg.Destroy()               
                if result == wx.ID_OK:
                    # read in other position
                    try:
                        a = self.port.getReg(servoID,P_PRESENT_POSITION_L, 2)
                        a = a[0] + (a[1]<<8)
                        # do our update to pose
                        if prev > a:
                            self.parent.project.poses["ik_max"][servoID-1] = prev
                            self.parent.project.poses["ik_min"][servoID-1] = a  
                            print "Capture Limits", servoID, ":", a, " to ", prev                
                        else:
                            self.parent.project.poses["ik_max"][servoID-1] = a
                            self.parent.project.poses["ik_min"][servoID-1] = prev
                            print "Capture Limits", servoID, ":", prev, ",", a  
                        self.captureLimits(servoID+1)
                    except:
                        if error < 3:   # try again
                            self.captureLimits(servoID, 1, prev, error+1)
                        else:           # fail and move on
                            dlg = wx.MessageDialog(self.parent, 'Unable to read servo ' + str(servoID), 'Capture Error', wx.OK)
                            dlg.ShowModal()
                            self.captureLimits(servoID+1)  
                elif result == 42:
                    self.captureLimits(servoID)
    def doNeutral(self, e = None):
        """ Capture the Neutral Position. """
        if self.doChecks(["project","port"]) > 0:
            print "Relax servos for capture..."
            self.parent.doRelax()
            print "Capturing neutral..."
            # show dialog with what neutral should like for this bot
            modelClassName = iKmodels[self.ikType.GetValue()].folder
            dlg = NeutralDialog(self.parent, 'Capture Neutral Position', "tools/models/"+modelClassName+"/neutral.jpg")
            #dlg = wx.MessageDialog(self.parent, 'Click OK when ready!', 'Capture Neutral Position', wx.OK | wx.CANCEL)
            if dlg.ShowModal() == wx.ID_OK:
                self.parent.project.poses["ik_neutral"] = project.pose("",self.parent.project.count)
                errors = "could not read servos: "
                for servo in range(self.parent.project.count):
                    pos = self.port.getReg(servo+1,P_PRESENT_POSITION_L, 2)
                    if pos != -1:
                        self.parent.project.poses["ik_neutral"][servo] = pos[0] + (pos[1]<<8)
                    else: 
                        errors = errors + str(servo+1) + ", "
                if errors != "could not read servos: ":
                    self.parent.sb.SetStatusText(errors[0:-2],0)  

    ###########################################################################
    # export
    def doExport(self, e=None):
        if self.doChecks(["project","ik"]) == 0:
            return
        else:
            # get directory name to save to
            dlg = wx.DirDialog(self,'Directory for Sketch Export' )
            if dlg.ShowModal() == wx.ID_OK:
                skDir = dlg.GetPath()
            else:
                return
            print "Writing a NUKE sketch to:",skDir

            # map servo name to ID
            servoMap = dict()
            servoMap["LF_COXA"] = int(self.servos[0].GetValue())
            servoMap["LF_FEMUR"] = int(self.servos[1].GetValue())
            servoMap["LF_TIBIA"] = int(self.servos[2].GetValue())
            servoMap["RF_COXA"] = int(self.servos[3].GetValue())
            servoMap["RF_FEMUR"] = int(self.servos[4].GetValue())
            servoMap["RF_TIBIA"] = int(self.servos[5].GetValue())
            if str(self.ikOpt.GetValue()) == "6":
                servoMap["LM_COXA"] = int(self.servos[6].GetValue())
                servoMap["LM_FEMUR"] = int(self.servos[7].GetValue())
                servoMap["LM_TIBIA"] = int(self.servos[8].GetValue())
                servoMap["RM_COXA"] = int(self.servos[9].GetValue())
                servoMap["RM_FEMUR"] = int(self.servos[10].GetValue())
                servoMap["RM_TIBIA"] = int(self.servos[11].GetValue())
            servoMap["LR_COXA"] = int(self.servos[12].GetValue())
            servoMap["LR_FEMUR"] = int(self.servos[13].GetValue())
            servoMap["LR_TIBIA"] = int(self.servos[14].GetValue())
            servoMap["RR_COXA"] = int(self.servos[15].GetValue())
            servoMap["RR_FEMUR"] = int(self.servos[16].GetValue())
            servoMap["RR_TIBIA"] = int(self.servos[17].GetValue())
            
            # setup model parameters
            params = dict()
            params["legs"] = str(self.ikOpt.GetValue())
            params["dof"] = str(self.ikOpt.GetValue())
            params["@VAL_LCOXA"] = str(self.vars[0].GetValue())
            params["@VAL_LFEMUR"] = str(self.vars[1].GetValue())
            params["@VAL_LTIBIA"] = str(self.vars[2].GetValue())
            params["@VAL_XCOXA"] = str(self.vars[3].GetValue())
            params["@VAL_YCOXA"] = str(self.vars[4].GetValue())
            params["@VAL_MCOXA"] = str(self.vars[5].GetValue())
            params["@SERVO_COUNT"] = str(self.parent.project.count)
            params["@SERVO_INDEXES"] = ""
            for k,v in servoMap.items():
                params["@SERVO_INDEXES"] = params["@SERVO_INDEXES"] + "#define " + k + " " + str(v) + "\n"
            params["@SERVO_MINS"] = "int mins[] = {"+str(self.parent.project.poses["ik_min"])+"};"
            params["@SERVO_MAXS"] = "int maxs[] = {"+str(self.parent.project.poses["ik_max"])+"};"
            # Simple Heuristics (TODO: Replace with a gait builder) 
            params["@X_STANCE"] = str(self.vars[0].GetValue()) 
            params["@Y_STANCE"] = str(self.vars[0].GetValue() + self.vars[1].GetValue())
            params["@Z_STANCE"] = str(int(0.75*self.vars[2].GetValue())) 
            params["@LIFT_HEIGHT"] = str(int(0.2*self.vars[2].GetValue()))
            # 10 or 12-bit?
            if self.parent.project.resolution[0] == 1024:
                params["@RAD_TO_SERVO_RESOLUTION"] = str(100)
            elif self.parent.project.resolution[0] == 4096:
                params["@RAD_TO_SERVO_RESOLUTION"] = str(25)

            # load general parameters 
            template = open("tools/models/core/template.ik").readlines()
            code = dict()
            current = ""
            for line in template:
                if line.find("@") == 0 and current == "":
                    current = line.strip().rstrip()
                elif line.find("@END_SECTION") > -1:                
                    current = ""
                else:
                    try:
                        code[current] = code[current] + line
                    except:
                        code[current] = line
            # load the parameters for our particular model
            modelDir = iKmodels[self.ikType.GetValue()].folder         
            template = open("tools/models/"+modelDir+"/template.ik").readlines()
            current = ""
            for line in template:
                if line.find("@") == 0 and current == "":
                    current = line.strip().rstrip()
                elif line.find("@END_SECTION") > -1:                
                    current = ""
                else:
                    try:
                        code[current] = code[current] + line
                    except:
                        code[current] = line
            code.pop("")

            templates = dict()
            # load default templates
            templates["gaits.h"] = open("tools/models/core/gaits.h").read()
            templates["nuke.h"] = open("tools/models/core/nuke.h").read()
            templates["nuke.cpp"] = open("tools/models/core/nuke.cpp").read() 
            sketch = os.path.split(skDir)[1]        
            templates[sketch+".ino"] = open("tools/models/core/default.pde").read()     
            # for each file
            for fileName in templates.keys():
                # insert code blocks
                for var, val in code.items():
                    templates[fileName] = templates[fileName].replace(var,val)
                # search and replace variables
                for var, val in params.items():
                    if var.find("@") == 0:
                        templates[fileName] = templates[fileName].replace(var,val)
                for k,v in servoMap.items():
                    templates[fileName] = templates[fileName].replace("@NEUTRAL_"+k, str(self.parent.project.poses["ik_neutral"][v-1]))        
                    templates[fileName] = templates[fileName].replace("@SIGN_"+k, self.signs[v-1:v])
                # save and reopen as lines                
                open(skDir+"/temp","w").write(templates[fileName])
                template = open(skDir+"/temp").readlines()
                # process IF/ELSE/END            
                i = 0
                out = None
                if fileName.endswith(".pde"):
                    if os.path.exists(skDir+"/"+fileName):
                        # open a different file, not the actual sketch
                        out = open(skDir+"/sketch.NEW","w")
                    else:
                        out = open(skDir+"/"+fileName,"w")
                else:
                    out = open(skDir+"/"+fileName,"w")
                while i < len(template):
                    if template[i].find("@IF") >= 0:
                        # do we include this?
                        line = template[i][template[i].find("@IF")+3:].strip().rstrip()
                        var = line[0:line.find(" ")].rstrip()
                        val = line[line.find(" ")+1:].strip().rstrip().split()
                        i = i + 1   
                        if params[var] in val:
                            while template[i].find("@ELSE") < 0 and template[i].find("@END_IF") < 0:
                                print>>out, template[i].rstrip()
                                i = i + 1
                            while template[i].find("@END_IF") < 0:
                                i = i + 1
                        else:
                            while template[i].find("@ELSE") < 0 and template[i].find("@END_IF") < 0:
                                i = i + 1
                            if template[i].find("@ELSE") >= 0:
                                i = i + 1 # don't output @ELSE
                            while template[i].find("@END_IF") < 0:
                                print>>out, template[i].rstrip()
                                i = i + 1
                    else:
                        print>>out, template[i].rstrip()
                    i = i + 1
                out.close()

        
###########################################################################
# A message box, with backup ability
class NukeDialog(wx.Dialog):
    def __init__(self, parent, title, msg):
        wx.Dialog.__init__(self, parent, 0, title, size=(390, 120))  

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, -1, msg, (340,100)), 1, wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, 10) 

        # Cancel | Backup | OK
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        closeButton = wx.Button(self, wx.ID_CANCEL, 'Cancel', size=(100, 50))
        backupButton = wx.Button(self, 42, 'Oops, Back Up', size=(120, 50))
        okButton = wx.Button(self, wx.ID_OK, 'Ok', size=(80, 50))
        hbox.Add(closeButton, 1)
        hbox.Add(backupButton, 1, wx.LEFT, 5)
        hbox.Add(okButton, 1, wx.LEFT, 5)
        vbox.Add(hbox, 1, wx.ALIGN_CENTER | wx.BOTTOM, 25)

        self.SetSizer(vbox) 
        wx.EVT_BUTTON(self, 42, self.doBackUp) 

    def doBackUp(self, e=None):
        self.EndModal(42)

###########################################################################
# A message box, that can display an image
class NeutralDialog(wx.Dialog):
    # TODO: This crap was generated by wxGlade, should probably be cleaned up...
    def __init__(self, parent, title, image):
    #def __init__(self, *args, **kwds):
        #kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent, 0, title, style=wx.DEFAULT_DIALOG_STYLE) #*args, **kwds)
        self.label_3 = wx.StaticText(self, -1, "Click OK when you've positioned the robot as shown:")
        self.bitmap_1 = wx.StaticBitmap(self, -1, wx.Bitmap(image, wx.BITMAP_TYPE_ANY))
        self.button_1 = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.button_2 = wx.Button(self, wx.ID_OK, "OK")

        #self.SetTitle("dialog_2")
        self.label_3.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.label_3, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        sizer_2.Add(self.bitmap_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_3.Add(self.button_1, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        sizer_3.Add(self.button_2, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT, 5)
        sizer_2.Add(sizer_3, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        self.Layout()
    
NAME = "NUKE editor"
STATUS = "starting NUKE..."
