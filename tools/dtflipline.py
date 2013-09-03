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
        self.canvas = self.iface.mapCanvas()
        self.tool = DtSelectFeatureTool(self.canvas)
        #create action
        self.act_flipLine = QtGui.QAction(QtGui.QIcon(":/flipLine.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Flip line"),  self.iface.mainWindow())
        self.act_flipLine.setCheckable(True)
        self.canvas.mapToolSet.connect(self.toolChanged)
        self.act_flipLine.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act_flipLine)
        self.enable()

    def toolChanged(self,  thisTool):
        if thisTool != self.tool:
            self.deactivate()

    def deactivate(self):
        self.act_flipLine.setChecked(False)
        try:
            self.tool.featureSelected.disconnect(self.featureSelectedSlot)
        except:
            pass

    def run(self):
        '''Function that does all the real work'''
        self.title = QtCore.QCoreApplication.translate("digitizingtools", "Flip line")
        self.canvas.setMapTool(self.tool)
        layer = self.iface.activeLayer()
        try:
            self.tool.featureSelected.disconnect(self.featureSelectedSlot)
            # disconnect if it was already connectedd, so slot gets called only once!
        except:
            pass

        self.act_flipLine.setChecked(True)
        self.tool.featureSelected.connect(self.featureSelectedSlot)

        if layer.selectedFeatureCount() > 0:
            reply = QtGui.QMessageBox.question(None, self.title,  QtCore.QCoreApplication.translate("digitizingtools",
                "Flip all selected lines?"),  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)

            if reply == QtGui.QMessageBox.Yes:
                self.flipLines()
            elif reply == QtGui.QMessageBox.No:
                layer.removeSelection()

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
            QtGui.QMessageBox.warning(None, self.title,  QtCore.QCoreApplication.translate("digitizingtools",
                "An error occured during flipping"))
            layer.destroyEditCommand()
        else:
            layer.endEditCommand()
            self.canvas.refresh()

    def enable(self):
        ''''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.act_flipLine.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for line layers
                if layer.geometryType() == 1:
                    if not layer.isEditable():
                        self.deactivate()

                    self.act_flipLine.setEnabled(layer.isEditable())

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
