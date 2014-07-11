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
from dttools import DtDualToolSelectVertex

class DtFillRing(DtDualToolSelectVertex):
    '''Fill selected ring/all rings in selected feature in active polygon layer'''
    def __init__(self, iface,  toolBar):
        DtDualToolSelectVertex.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/fillRing.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Fill ring with a new feature (interactive mode)"),
            QtGui.QIcon(":/fillRingBatch.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Fill all rings in selected polygons with new features"),
            geometryTypes = [3, 6],  dtName = "dtFillRing")
        self.newFid = None

    def vertexSnapped(self,  snapResult):
        snappedVertex = snapResult[0][0]
        snappedFid = snapResult[2][0]
        layer = self.iface.activeLayer()
        feat = dtutils.dtGetFeatureForId(layer,  snappedFid)

        if feat != None:
            geom = feat.geometry()
            rings = dtutils.dtExtractRings(geom)
            thisRing = None

            for aRing in rings:
                for aPoint in dtutils.dtExtractPoints(aRing):
                    if aPoint.x() == snappedVertex.x() and aPoint.y() == snappedVertex.y():
                        thisRing = aRing
                        break

            if thisRing != None:
                defaultAttributeMap = dtutils.dtGetDefaultAttributeMap(layer)
                layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Fill ring"))

                if self.iface.vectorLayerTools().addFeature(layer, defaultValues = defaultAttributeMap, defaultGeometry = thisRing):
                    layer.endEditCommand()
                    self.canvas.refresh()
                else:
                    layer.destroyEditCommand()

        self.tool.reset()

    def process(self):
        layer = self.iface.activeLayer()
        layer.featureAdded.connect(self.featureAdded)
        numRingsFilled = 0
        aborted = False

        for featureToFill in layer.selectedFeatures():
            geom = featureToFill.geometry()
            rings = dtutils.dtExtractRings(geom)

            for aRing in rings:

                if numRingsFilled == 0:
                    defaultAttributeMap = dtutils.dtGetDefaultAttributeMap(layer)
                    layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Fill rings"))

                    if self.iface.vectorLayerTools().addFeature(layer, defaultValues = defaultAttributeMap, defaultGeometry = aRing):
                        layer.featureAdded.disconnect(self.featureAdded)
                    else:
                        layer.featureAdded.disconnect(self.featureAdded)
                        layer.destroyEditCommand()
                        aborted = True
                        break
                else:
                    aFeat = dtutils.dtCopyFeature(layer,  srcFid = self.newFid)
                    aFeat.setGeometry(aRing)
                    layer.addFeature(aFeat)

                numRingsFilled += 1

                if aborted:
                    break

        layer.endEditCommand()
        self.canvas.refresh()

    def featureAdded(self,  newFid):
        self.newFid = newFid



