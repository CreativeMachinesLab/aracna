#!/usr/bin/env python

""" Manifest of IK Models """

class IkModel:
    def __init__(self, folder, options = [4,6], optiondesc = "# of legs"):
        self.folder = folder
        self.options = options
        self.optiondesc = optiondesc

iKmodels = dict()
iKmodels["Lizard 3DOF"] = IkModel("lizard3")
iKmodels["Mammal 3DOF"] = IkModel("mammal3")
iKmodels["Biped 4/5/6"] = IkModel("biped",[4,5,6], "# of DOF")
#iKmodels["Linear-Lift + 2DOF"] = IkModel("linear2")

