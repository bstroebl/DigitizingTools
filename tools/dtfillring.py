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
            QtCore.QCoreApplication.translate("digitizingtools", "Fill ring (interactive mode)"),
            QtGui.QIcon(":/fillRingBatch.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Fill all rings in selected polygons"),
            geometryTypes = [2])

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
                newFeat = dtutils.dtCreateFeature(layer)

                if self.iface.openFeatureForm(layer,  newFeat,  True):
                    # let user edit attributes
                    layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Fill ring"))
                    newFeat.setGeometry(thisRing)
                    layer.addFeature(newFeat)
                    layer.endEditCommand()
                    self.canvas.refresh()

        self.tool.clear()

    def process(self):
        layer = self.iface.activeLayer()
        newFeat = dtutils.dtCreateFeature(layer)
        numRingsFilled = 0

        if self.iface.openFeatureForm(layer,  newFeat):
            for featureToFill in layer.selectedFeatures():
                geom = featureToFill.geometry()
                rings = dtutils.dtExtractRings(geom)

                for aRing in rings:

                    if numRingsFilled == 0:
                        layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Fill rings"))

                    aFeat = dtutils.dtCopyFeature(layer,  newFeat)
                    aFeat.setGeometry(aRing)
                    #for i in range(layer.pendingFields().count()):
                    layer.addFeature(aFeat)
                    numRingsFilled += 1

            layer.endEditCommand()
            self.canvas.refresh()
        else:
            layer.destroyEditCommand()



