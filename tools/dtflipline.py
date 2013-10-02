# -*- coding: utf-8 -*-
"""
dtflipline
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
import dtutils
from dtselectfeaturetool import DtSelectFeatureTool

class DtFlipLine():
    '''Flip line direction'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.iface.currentLayerChanged.connect(self.enable)
        self.canvas = self.iface.mapCanvas()
        self.tool = DtSelectFeatureTool(self.canvas)
        self.canvas.mapToolSet.connect(self.toolChanged)
        #create button
        self.button = QtGui.QToolButton(toolBar)
        self.button.clicked.connect(self.run)
        self.button.toggled.connect(self.hasBeenToggled)
        #create menu
        self.menu = QtGui.QMenu(toolBar)
        self.menu.triggered.connect(self.menuTriggered)
        self.button.setMenu(self.menu)
        self.button.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        # create actions
        self.act_flipLine = QtGui.QAction(QtGui.QIcon(":/flipLine.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Flip line"),  self.iface.mainWindow())
        self.act_flipLineBatch = QtGui.QAction(QtGui.QIcon(":/flipLineBatch.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Flip selected lines"),  self.iface.mainWindow())
        # add actions to menu
        self.menu.addAction(self.act_flipLine)
        self.menu.addAction(self.act_flipLineBatch)
        # set the interactive action as default action, user needs to click the button to activate it
        self.button.setIcon(self.act_flipLine.icon())
        self.button.setCheckable(True)
        self.batchMode = False
        # add button to toolBar
        toolBar.addWidget(self.button)
        # run the enable slot
        self.enable()

    def menuTriggered(self,  thisAction):
        if thisAction == self.act_flipLine:
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

            self.run(False)

        self.button.setIcon(thisAction.icon())

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

    def toolChanged(self,  thisTool):
        if thisTool != self.tool:
            self.deactivate()

    def deactivate(self):
        if self.button.isChecked():
            self.button.toggle()

    def run(self,  isChecked):
        '''Function that does all the real work'''

        if self.batchMode:
            layer = self.iface.activeLayer()

            if layer.selectedFeatureCount() > 0:
                self.flipLines()
        else:
            if not isChecked:
                self.button.toggle()


    def featureSelectedSlot(self,  fids):
        if len(fids) >0:
            self.flipLines()

    def flipLines(self):
        '''algorythm taken from Nathan Woodrow's Swap Line Direction see
       http://gis.stackexchange.com/questions/9261/how-can-i-switch-line-direction-in-qgis '''
        layer = self.iface.activeLayer()

        if layer.selectedFeatureCount() == 1:
            layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Flip line"))
        elif layer.selectedFeatureCount() > 1:
            layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Flip lines"))
        else:
            return None

        hadError = False

        for feat in layer.selectedFeatures():
            geom = feat.geometry()
            nodes = geom.asPolyline()
            nodes.reverse()
            newGeom = QgsGeometry.fromPolyline(nodes)

            if not layer.changeGeometry(feat.id(),  newGeom):
                hadError = True

        if hadError:
            self.iface.messageBar().pushMessage(QtCore.QCoreApplication.translate("digitizingtools",
                "An error occured during flipping", level=QgsMessageBar.CRITICAL))
            layer.destroyEditCommand()
        else:
            layer.endEditCommand()
            self.canvas.refresh()

    def enable(self):
        ''''Enables/disables the corresponding button.'''
        # Disable the Button by defaultself.button.setCheckable(thisAction == self.act_flipLine)
        self.button.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for line layers
                if layer.geometryType() == 1:
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
