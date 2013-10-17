# -*- coding: utf-8 -*-
"""
dttools
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
from PyQt4 import QtGui
from qgis.core import *
from qgis.gui import *
from dtselectfeaturetool import DtSelectFeatureTool
from dtselectvertextool import DtSelectVertexTool

class DtSingleButton():
    '''Abstract class for a single button
    icon [QtGui.QIcon]
    tooltip [str]
    geometryTypes [array:integer] 0=point, 1=line, 2=polygon'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes = [0, 1, 2]):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.act = QtGui.QAction(icon, tooltip, self.iface.mainWindow())
        self.act.triggered.connect(self.process)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act)
        self.geometryTypes = geometryTypes

    def process(self):
        raise NotImplementedError("Should have implemented process")

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.act.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for layers of
                if self.geometryTypes.count(layer.geometryType()) == 1:
                    #check if this layer'S geometry type is within the list of allowed types
                    self.act.setEnabled(layer.isEditable())
                    try:
                        layer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable) # when it becomes active layer again
                    except:
                        pass
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)

class DtSingleEditTool(DtSingleButton):
    '''Abstract class for a tool for interactive editing'''
    def __init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes = [0, 1, 2]):
        DtSingleButton.__init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes)
        self.editLayer = None
        self.tool = None
        self.act.setCheckable(True)
        self.canvas.mapToolSet.connect(self.toolChanged)

    def toolChanged(self,  thisTool):
        if thisTool != self.tool:
            self.deactivate()

    def deactivate(self):
        if self.tool != None:
            self.tool.reset()

        self.reset()
        self.act.setChecked(False)

    def reset(self):
        self.editLayer = None

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        doEnable = False
        layer = self.iface.activeLayer()

        if layer <> None:
            if layer.type() == 0: #Only for vector layers.
                if self.geometryTypes.count(layer.geometryType()) == 1:
                    doEnable = layer.isEditable()
                    try:
                        layer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable) # when it becomes active layer again
                    except:
                        pass
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)

        if self.editLayer != None: # we have a current edit session, activeLayer may have changed or editing status of self.editLayer
            try:
                self.editLayer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
            except:
                pass
            try:
                self.editLayer.editingStopped.disconnect(self.enable) # when it becomes active layer again
            except:
                pass

            self.tool.reset()
            self.reset()

        if not doEnable:
            self.deactivate()

        self.act.setEnabled(doEnable)

class DtDualTool():
    '''Abstract class for a tool with interactive and batch mode
    icon [QtGui.QIcon] for interactive mode
    tooltip [str] for interactive mode
    iconBatch [QtGui.QIcon] for batch mode
    tooltipBatch [str] for batch mode
    geometryTypes [array:integer] 0=point, 1=line, 2=polygon'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes = [0,  1, 2]):
        # Save reference to the QGIS interface
        self.iface = iface
        self.iface.currentLayerChanged.connect(self.enable)
        self.canvas = self.iface.mapCanvas()
        self.canvas.mapToolSet.connect(self.toolChanged)
        #create button
        self.button = QtGui.QToolButton(toolBar)
        self.button.clicked.connect(self.runSlot)
        self.button.toggled.connect(self.hasBeenToggled)
        #create menu
        self.menu = QtGui.QMenu(toolBar)
        self.menu.triggered.connect(self.menuTriggered)
        self.button.setMenu(self.menu)
        self.button.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        # create actions
        self.act = QtGui.QAction(icon, tooltip,  self.iface.mainWindow())
        self.act.setToolTip(tooltip)
        self.act_batch = QtGui.QAction(iconBatch, tooltipBatch,  self.iface.mainWindow())
        self.act_batch.setToolTip(tooltipBatch)
        self.menu.addAction(self.act)
        self.menu.addAction(self.act_batch)
        # set the interactive action as default action, user needs to click the button to activate it
        self.button.setIcon(self.act.icon())
        self.button.setToolTip(self.act.toolTip())
        self.button.setCheckable(True)
        self.batchMode = False
        # add button to toolBar
        toolBar.addWidget(self.button)
        self.geometryTypes = geometryTypes
        # run the enable slot
        self.enable()

    def menuTriggered(self,  thisAction):
        if thisAction == self.act:
            self.batchMode = False
            self.button.setCheckable(True)
            if not self.button.isChecked():
                self.button.toggle()
        else:
            self.batchMode = True
            if self.button.isCheckable():
                if self.button.isChecked():
                    self.button.toggle()
                self.button.setCheckable(False)

            self.runSlot(False)

        self.button.setIcon(thisAction.icon())
        self.button.setToolTip(thisAction.toolTip())

    def toolChanged(self,  thisTool):
        if thisTool != self.tool:
            self.deactivate()

    def hasBeenToggled(self,  isChecked):
        raise NotImplementedError("Should have implemented hasBeenToggled")

    def deactivate(self):
        if self.button.isChecked():
            self.button.toggle()

    def runSlot(self,  isChecked):
        if self.batchMode:
            layer = self.iface.activeLayer()

            if layer.selectedFeatureCount() > 0:
                self.process()
        else:
            if not isChecked:
                self.button.toggle()

    def process(self):
        raise NotImplementedError("Should have implemented process")

    def enable(self):
       # Disable the Button by default
        self.button.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for certain layers
                if self.geometryTypes.count(layer.geometryType()) == 1:
                    if not layer.isEditable():
                        self.deactivate()

                    self.button.setEnabled(layer.isEditable())

                    try:
                        layer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable) # when it becomes active layer again
                    except:
                        pass
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)
                else:
                    self.deactivate()

class DtDualToolSelectFeature(DtDualTool):
    '''Abstract class for a DtDualToo which uses the DtSelectFeatureTool for interactive mode'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes = [0,  1, 2]):
        DtDualTool.__init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes)
        self.tool = DtSelectFeatureTool(self.canvas)

    def featureSelectedSlot(self,  fids):
        if len(fids) >0:
            self.process()

    def hasBeenToggled(self,  isChecked):
        try:
            self.tool.featureSelected.disconnect(self.featureSelectedSlot)
            # disconnect if it was already connected, so slot gets called only once!
        except:
            pass

        if isChecked:
            self.canvas.setMapTool(self.tool)
            self.tool.featureSelected.connect(self.featureSelectedSlot)
        else:
            self.canvas.unsetMapTool(self.tool)

class DtDualToolSelectVertex(DtDualTool):
    '''Abstract class for a DtDualTool which uses the DtSelectVertexTool for interactive mode
    numVertices [integer] nnumber of vertices to be snapped until vertexFound signal is emitted'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes = [0,  1, 2],  numVertices = 1):
        DtDualTool.__init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes)
        self.tool = DtSelectVertexTool(self.canvas,  numVertices)

    def hasBeenToggled(self,  isChecked):
        try:
            self.tool.vertexFound.disconnect(self.vertexSnapped)
            # disconnect if it was already connected, so slot gets called only once!
        except:
            pass

        if isChecked:
            self.canvas.setMapTool(self.tool)
            self.tool.vertexFound.connect(self.vertexSnapped)
        else:
            self.canvas.unsetMapTool(self.tool)

    def vertexSnapped(self,  snapResult):
        raise NotImplementedError("Should have implemented vertexSnapped")
