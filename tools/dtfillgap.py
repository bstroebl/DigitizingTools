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

class DtFillGap():
    '''Fill gaps between selected features of the active layer with new features'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.tool = DtSelectVertexTool(self.canvas)
        self.doIgnoreTool = False
        #create action
        self.act_fillGap = QtGui.QAction(QtGui.QIcon(":/fillGap.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Fill gap"),  self.iface.mainWindow())
        self.act_fillGap.setCheckable(True)
        self.canvas.mapToolSet.connect(self.deactivate)
        self.act_fillGap.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act_fillGap)
        self.enable()

    def deactivate(self,  thisTool):
        if thisTool != self.tool:
            self.tool.clear()
            self.act_fillGap.setChecked(False)
            try:
                self.tool.vertexFound.disconnect(self.vertexSnapped)
            except:
                pass


    def run(self):
        '''Function that does all the real work'''
        self.title = QtCore.QCoreApplication.translate("digitizingtools", "Fill gap")
        self.canvas.setMapTool(self.tool)
        layer = self.iface.activeLayer()
        self.doIgnoreTool = True
        try:
            self.tool.vertexFound.disconnect(self.vertexSnapped)
            # disconnect if it was already connectedd, so slot gets called only once!
        except:
            pass
        self.tool.vertexFound.connect(self.vertexSnapped)
        self.act_fillGap.setChecked(True)

        if layer.selectedFeatureCount() == 0:
            QtGui.QMessageBox.information(None,  self.title,  dtutils.dtGetNoSelMessage()[0] + " " + layer.name() + ".\n" + \
                                          QtCore.QCoreApplication.translate("digitizingtools", "Please select all features that surround the gap to be filled."))
            return None
        else:
            reply = QtGui.QMessageBox.question(None, self.title,  QtCore.QCoreApplication.translate("digitizingtools",
                "Fill all gaps between selected polygons?"),  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)

            if reply == QtGui.QMessageBox.Yes:
                self.fillGaps()
                return None
            elif reply == QtGui.QMessageBox.No:
                self.doIgnoreTool = False


    def vertexSnapped(self,  snapResult):
        if not self.doIgnoreTool:
            snappedVertex = snapResult[0][0]
            self.fillGaps(snappedVertex)

        self.tool.clear()

    def fillGaps(self, snappedVertex = None):
        layer = self.iface.activeLayer()
        if layer.selectedFeatureCount() == 0:
            layer.invertSelection()

        multiGeom = None

        for aFeat in layer.selectedFeatures():
            aGeom = aFeat.geometry()

            if not aGeom.isGeosValid():
                QtGui.QMessageBox.warning(None,  self.title,  dtutils.dtGetInvalidGeomWarning())
                return None

            # fill rings contained in the polygon
            if aGeom.isMultipart():
                tempGeom = None

                for poly in aGeom.asMultiPolygon():
                    noRingGeom = self.deleteRings(poly)

                    if tempGeom == None:
                        tempGeom = noRingGeom
                    else:
                        tempGeom = tempGeom.combine(noRingGeom)
            else:
                tempGeom = self.deleteRings(aGeom.asPolygon())

            # make a large polygon from all selected
            if multiGeom == None:
                multiGeom = tempGeom
            else:
                multiGeom = multiGeom.combine(tempGeom)

        rings = dtutils.dtExtractRings(multiGeom)

        if len(rings) == 0:
            QtGui.QMessageBox.warning(None,  self.title,  QtCore.QCoreApplication.translate("digitizingtools",
                "There are no gaps between the polygons.") )
        else:
            if snappedVertex != None:
                thisRing = None

                for aRing in rings:
                    for aPoint in dtutils.dtExtractPoints(aRing):
                        if aPoint.x() == snappedVertex.x() and aPoint.y() == snappedVertex.y():
                            thisRing = aRing
                            break

                if thisRing != None:
                    newFeat = dtutils.dtCreateFeature(layer)
                    layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Fill gap"))

                    if self.iface.openFeatureForm(layer,  newFeat,  True):
                        newFeat.setGeometry(thisRing)
                        layer.addFeature(newFeat)
                        layer.endEditCommand()

                    else:
                        layer.destroyEditCommand()
                else:
                    QtGui.QMessageBox.warning(None,  self.title,  QtCore.QCoreApplication.translate("digitizingtools",
                        "The selected gap is not closed.") )
            else:
                newFeat = dtutils.dtCreateFeature(layer)
                layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Fill gaps"))

                if self.iface.openFeatureForm(layer,  newFeat):
                    for aRing in rings:
                        aFeat = dtutils.dtCopyFeature(layer,  newFeat)
                        aFeat.setGeometry(aRing)
                        layer.addFeature(aFeat)

                    layer.endEditCommand()
            self.canvas.refresh()

    def deleteRings(self,  poly):
        outGeom = QgsGeometry.fromPolygon(poly)

        if len(poly) > 1:
            # we have rings
            rings = dtutils.dtExtractRings(outGeom)
            for aRing in rings:
                outGeom = outGeom.combine(aRing)

        return outGeom


    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.act_fillGap.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for polygon layers
                if layer.geometryType() == 2:
                    self.act_fillGap.setEnabled(layer.isEditable())
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

