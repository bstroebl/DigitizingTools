# -*- coding: utf-8 -*-
"""
dtclipper
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2015-01-29
* copyright            : (C) 2015 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
from qgis.PyQt import QtCore, QtGui
from qgis.core import *
import dt_icons_rc
import dtutils
from dttools import DtDualToolSelectPolygon

class DtClipWithPolygon(DtDualToolSelectPolygon):
    '''Clip from active editable layer with selected polygon from another layer'''
    def __init__(self, iface,  toolBar):
        super().__init__(iface, toolBar,
            QtGui.QIcon(":/clipper.png"),
            QtCore.QCoreApplication.translate(
                "digitizingtools", "Clip with polygon (interactive)"),
            QtGui.QIcon(":/clipper_batch.png"),
            QtCore.QCoreApplication.translate(
                "digitizingtools", "Clip with selected polygons"),
            geometryTypes = [3, 6], dtName = "dtClipper")
        self.enable()

    def process(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate(
            "digitizingtools", "Clipper")

        processLayer = self.iface.activeLayer()
        msgLst = dtutils.dtGetNoSelMessage()
        noSelMsg1 = msgLst[0]

        if processLayer.selectedFeatureCount() == 0:
            self.iface.messageBar().pushMessage(
                title, noSelMsg1 + " " + processLayer.name())
            return None
        else:
            clipperGeoms = []

            for feat in processLayer.selectedFeatures():
                clipperGeom = feat.geometry()

                if not clipperGeom.isGeosValid():
                    thisWarning = dtutils.dtGetInvalidGeomWarning(processLayer)
                    dtutils.dtShowWarning(self.iface, thisWarning)
                    continue
                else:
                    clipperGeoms.append(clipperGeom)

            if len(clipperGeoms) == 0:
                return None # could be only invalid geoms selected

            processLayer.invertSelection()
            idsToProcess = []
            processLayer.beginEditCommand(
                    QtCore.QCoreApplication.translate(
                        "editcommand", "Clip Features"
                    ))
            featuresBeingClipped = 0

            for aFeat in processLayer.selectedFeatures():
                idsToProcess.append(aFeat.id())

            for clipperGeom in clipperGeoms:
                bbox = clipperGeom.boundingBox()
                processLayer.selectByRect(bbox) # make a new selection

                for selFeat in processLayer.selectedFeatures():
                    if idsToProcess.count(selFeat.id()) == 0:
                        continue

                    selGeom = selFeat.geometry()

                    if not selGeom.isGeosValid():
                        thisWarning = dtutils.dtGetInvalidGeomWarning(processLayer)
                        dtutils.dtShowWarning(self.iface, thisWarning)
                        continue

                    if clipperGeom.intersects(selGeom): # we have a candidate
                        newGeom = selGeom.intersection(clipperGeom)

                        if newGeom != None:
                            if not newGeom.isEmpty():
                                if newGeom.area() > 0:
                                    selFeat.setGeometry(newGeom)
                                    processLayer.updateFeature(selFeat)
                                    featuresBeingClipped += 1

            processLayer.removeSelection()
            self.iface.mapCanvas().refresh()

            if featuresBeingClipped == 0:
                processLayer.destroyEditCommand()
            else:
                processLayer.endEditCommand()

