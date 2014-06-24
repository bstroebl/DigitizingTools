# -*- coding: utf-8 -*-
"""
dtprolongline
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-02-25
* copyright          : (C) 2013 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
from PyQt4 import QtCore,  QtGui
from qgis.core import *
from qgis.gui import *
import icons_rc
from dtprolonglinetool import DtProlongLineTool
from dttools import DtSingleEditTool

class DtProlongLine(DtSingleEditTool):
    '''Prolong an existing line'''
    def __init__(self, iface,  toolBar):
        DtSingleEditTool.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/prolongline.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Prolong Line"),
            geometryTypes = [2, 5],  dtName = "dtProlongLine")

        self.tool = DtProlongLineTool(self.canvas)
        self.tool.startedDigitizing.connect(self.digitizingStarted)
        self.tool.finishedDigitizing.connect(self.digitizingFinished)
        self.tool.stoppedDigitizing.connect(self.digitizingStopped)
        self.reset()
        self.enable()

    def reset(self):
        self.editLayer = None
        self.lineFeature = None
        self.rubberBand = None

    def digitizingStarted(self,  layer,  feature,  startPoint,  rubberBand):
        self.editLayer = layer
        self.lineFeature = feature

    def digitizingFinished(self, digitizedGeom):
        lineGeom = self.lineFeature.geometry()
        newGeom = lineGeom.combine(digitizedGeom)
        # step 5 change geometry in layer
        self.editLayer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Prolong Line"))
        self.lineFeature.setGeometry(newGeom)
        self.editLayer.updateFeature(self.lineFeature)
        self.editLayer.endEditCommand()
        self.reset()

    def digitizingStopped(self):
        self.reset()

    def process(self):
        self.canvas.setMapTool(self.tool)
        self.act.setChecked(True)


