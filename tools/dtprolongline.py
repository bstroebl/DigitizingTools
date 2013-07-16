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

class DtProlongLine():
    '''Cut out from active editable layer with selected polygon from another layer'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.mapCanvas=self.iface.mapCanvas()
        #create action
        self.title = QtCore.QCoreApplication.translate("digitizingtools", "Prolong Line")
        self.act_prolong = QtGui.QAction(QtGui.QIcon(":/prolongline.png"), self.title,  self.iface.mainWindow())
        self.act_prolong.setCheckable(True)
        self.act_prolong.triggered.connect(self.run)
        self.mapCanvas.mapToolSet.connect(self.deactivate)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act_prolong)
        self.tool = DtProlongLineTool(self.mapCanvas)
        self.tool.startedDigitizing.connect(self.digitizingStarted)
        self.tool.finishedDigitizing.connect(self.digitizingFinished)
        self.tool.stoppedDigitizing.connect(self.digitizingStopped)

        self.lineLayer = None
        self.reset()
        self.enable()

    def reset(self):
        self.lineLayer = None
        self.lineFeature = None
        self.rubberBand = None

    def digitizingStarted(self,  layer,  feature,  startPoint,  rubberBand):
        self.lineLayer = layer
        self.lineFeature = feature

    def digitizingFinished(self, digitizedGeom):
        lineGeom = self.lineFeature.geometry()
        newGeom = lineGeom.combine(digitizedGeom)
        # step 5 change geometry in layer
        self.lineLayer.beginEditCommand(QtCore.QCoreApplication.translate("digitizingtools", "Prolong Line"))
        self.lineFeature.setGeometry(newGeom)
        self.lineLayer.updateFeature(self.lineFeature)
        self.lineLayer.endEditCommand()
        self.reset()

    def digitizingStopped(self):
        self.reset

    def deactivate(self):
        self.tool.reset()
        self.reset()
        self.act_prolong.setChecked(False)

    def run(self):
        '''Function that does all the real work'''
        self.mapCanvas.setMapTool(self.tool)
        self.act_prolong.setChecked(True)

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        doEnable = False
        doConnect = False
        layer = self.iface.activeLayer()

        if layer <> None:
            if layer.type() == 0: #Only for vector layers.
                if layer.geometryType() == 1: # only line layers
                    doConnect = True
                    doEnable = layer.isEditable()
                    try:
                        layer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable) # when it becomes active layer again
                    except:
                        pass

        if self.lineLayer != None: # we have a current edit session, activeLayer may have changed or editing status of self.lineLayer
            try:
                self.lineLayer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
            except:
                pass
            try:
                self.lineLayer.editingStopped.disconnect(self.enable) # when it becomes active layer again
            except:
                pass

            self.tool.reset()
            self.reset()

        if not doEnable:
            self.deactivate()

        self.act_prolong.setEnabled(doEnable)

        if doConnect:
            layer.editingStarted.connect(self.enable)
            layer.editingStopped.connect(self.enable)

