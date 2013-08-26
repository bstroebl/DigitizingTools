# -*- coding: utf-8 -*-
"""
dtcutter
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
import icons_rc
import dtutils
from dtselectvertextool import DtSelectVertexTool

class DtFillRing():
    '''Fill selected ring/all rings in selected feature in active polygon layer'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        #create action
        self.act_fillRing = QtGui.QAction(QtGui.QIcon(":/fillRing.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Fill ring."),  self.iface.mainWindow())
        self.act_fillRing.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act_fillRing)
        self.enable()
        self.tool = DtSelectVertexTool(self.canvas)

    def run(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate("digitizingtools", "Fill Ring")
        layer = self.iface.activeLayer()

        if layer.selectedFeatureCount() > 0:
            reply = QtGui.QMessageBox.question(None, title,  QtCore.QCoreApplication.translate("digitizingtools",
                "Fill all rings in all selected polygons?"),  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)

            if reply == QtGui.QMessageBox.Yes:
                self.fillRings(layer.selectedFeaturesIds())
                return None
            elif reply == QtGui.QMessageBox.No:
                layer.removeSelection()
                self.canvas.refresh()
            else:
                return None

        self.canvas.setMapTool(self.tool)
        #Connect to the DtSelectVertexTool
        self.tool.vertexFound.connect(self.vertexSnapped)

    def vertexSnapped(self,  snapResult):
        snappedVertex = snapResult[0][0]
        snappedFid = snapResult[2][0]
        layer = self.iface.activeLayer()
        thisRing = None
        feat = dtutils.dtGetFeatureForId(layer,  snappedFid)

        if feat != None:
            geom = feat.geometry()
            rings = dtutils.dtExtractRings(geom)

            for aRing in rings:
                for aPoint in dtutils.dtExtractPoints(aRing):
                    if aPoint.x() == snappedVertex.x() and aPoint.y() == snappedVertex.y():
                        thisRing = aRing
                        break

            if thisRing != None:
                newFeat = dtutils.dtCreateFeature(layer)
                layer.beginEditCommand(QtCore.QCoreApplication.translate("digitizingtools", "Fill ring"))

                if self.iface.openFeatureForm(layer,  newFeat,  True):
                    # let user edit attributes
                    newFeat.setGeometry(aRing)
                    layer.addFeature(newFeat)
                    layer.endEditCommand()
                    self.canvas.refresh()
                else:
                    layer.destroyEditCommand()

        self.tool.clear()
        return None

    def fillRings(self,  forFids):
        layer = self.iface.activeLayer()
        newFeat = dtutils.dtCreateFeature(layer)
        layer.beginEditCommand(QtCore.QCoreApplication.translate("digitizingtools", "Fill rings"))

        if self.iface.openFeatureForm(layer,  newFeat):
            for fid in forFids:
                featureToFill = dtutils.dtGetFeatureForId(layer,  fid)

                if featureToFill != None:
                    geom = featureToFill.geometry()
                    rings = dtutils.dtExtractRings(geom)

                    for aRing in rings:
                        aFeat = dtutils.dtCopyFeature(layer,  newFeat)
                        aFeat.setGeometry(aRing)
                        #for i in range(layer.pendingFields().count()):

                        layer.addFeature(aFeat)

            layer.endEditCommand()
            self.canvas.refresh()
        else:
            layer.destroyEditCommand()

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.act_fillRing.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for polygon layers
                if layer.geometryType() == 2:
                    self.act_fillRing.setEnabled(layer.isEditable())
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

