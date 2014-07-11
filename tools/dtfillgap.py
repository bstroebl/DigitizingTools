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
from qgis.gui import *
import icons_rc
import dtutils
from dttools import DtDualToolSelectVertex

class DtFillGap(DtDualToolSelectVertex):
    '''Fill gaps between selected features of the active layer with new features'''
    def __init__(self, iface,  toolBar):
        DtDualToolSelectVertex.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/fillGap.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Fill gap with a new feature (interactive mode)"),
            QtGui.QIcon(":/fillGapBatch.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Fill all gaps between selected polygons with new features"),
            geometryTypes = [3, 6],  dtName = "dtFillGap")

        self.newFid = None

    def vertexSnapped(self,  snapResult):
        snappedVertex = snapResult[0][0]
        self.fillGaps(snappedVertex)
        self.tool.reset()

    def process(self):
        self.fillGaps()

    def fillGaps(self, snappedVertex = None):
        title = QtCore.QCoreApplication.translate("digitizingtools", "Fill gap")
        layer = self.iface.activeLayer()
        hasNoSelection = (layer.selectedFeatureCount() == 0)

        if hasNoSelection:
            layer.invertSelection()

        multiGeom = None

        for aFeat in layer.selectedFeatures():
            aGeom = aFeat.geometry()

            if not aGeom.isGeosValid():
                self.iface.messageBar().pushMessage(title,  dtutils.dtGetInvalidGeomWarning(layer), level=QgsMessageBar.CRITICAL)
                return None

            # fill rings contained in the polygon
            if aGeom.isMultipart():
                tempGeom = None

                for poly in aGeom.asMultiPolygon():
                    noRingGeom = dtutils.dtDeleteRings(poly)

                    if tempGeom == None:
                        tempGeom = noRingGeom
                    else:
                        tempGeom = tempGeom.combine(noRingGeom)
            else:
                tempGeom = dtutils.dtDeleteRings(aGeom.asPolygon())

            # make a large polygon from all selected
            if multiGeom == None:
                multiGeom = tempGeom
            else:
                multiGeom = multiGeom.combine(tempGeom)

        rings = dtutils.dtExtractRings(multiGeom)

        if len(rings) == 0:
            self.iface.messageBar().pushMessage(title,  QtCore.QCoreApplication.translate("digitizingtools",
                "There are no gaps between the polygons."), level=QgsMessageBar.CRITICAL)
        else:
            defaultAttributeMap = dtutils.dtGetDefaultAttributeMap(layer)

            if snappedVertex != None:
                thisRing = None

                for aRing in rings:
                    for aPoint in dtutils.dtExtractPoints(aRing):
                        if aPoint.x() == snappedVertex.x() and aPoint.y() == snappedVertex.y():
                            thisRing = aRing
                            break

                if thisRing != None:
                    layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Fill gap"))

                    if self.iface.vectorLayerTools().addFeature(layer, defaultValues = defaultAttributeMap, defaultGeometry = thisRing):
                        layer.endEditCommand()
                        self.canvas.refresh()
                    else:
                        layer.destroyEditCommand()
                else:
                    self.iface.messageBar().pushMessage(title,  QtCore.QCoreApplication.translate("digitizingtools",
                        "The selected gap is not closed."), level=QgsMessageBar.CRITICAL)
            else:
                layer.featureAdded.connect(self.featureAdded)
                numRingsFilled = 0
                aborted = False

                for aRing in rings:
                    if numRingsFilled == 0:
                        layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Fill gaps"))

                        if self.iface.vectorLayerTools().addFeature(layer, defaultValues = defaultAttributeMap, defaultGeometry = aRing):
                            layer.featureAdded.disconnect(self.featureAdded)
                        else:
                            layer.featureAdded.disconnect(self.featureAdded)
                            aborted = True
                            break
                    else:
                        aFeat = dtutils.dtCopyFeature(layer,  srcFid = self.newFid)
                        aFeat.setGeometry(aRing)
                        layer.addFeature(aFeat)

                    numRingsFilled += 1

                if aborted:
                    layer.destroyEditCommand()
                else:
                    layer.endEditCommand()

            if hasNoSelection:
                layer.removeSelection()

            self.canvas.refresh()

    def featureAdded(self,  newFid):
        self.newFid = newFid
