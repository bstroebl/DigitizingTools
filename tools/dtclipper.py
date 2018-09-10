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
from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis.core import *
import dt_icons_rc
import dtutils
from dttools import DtSingleButton

class DtClipWithPolygon(DtSingleButton):
    '''Clip from active editable layer with selected polygon from another layer'''
    def __init__(self, iface,  toolBar):
        super().__init__(iface, toolBar,
            QtGui.QIcon(":/clipper.png"),
            QtCore.QCoreApplication.translate(
                "digitizingtools", "Clip with polygon from another layer"),
            geometryTypes = [2, 3, 5, 6], dtName = "dtClipper")
        self.enable()

    def process(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate(
            "digitizingtools", "Clipper")

        clipperLayer = dtutils.dtChooseVectorLayer(
            self.iface, 2, msg = QtCore.QCoreApplication.translate(
                "digitizingtools", "clipper layer"
            ))

        if clipperLayer == None:
            self.iface.messageBar().pushMessage(
                title, QtCore.QCoreApplication.translate(
                    "digitizingtools", "Please provide a polygon layer to clip with."
                ))
        else:
            passiveLayer = self.iface.activeLayer()
            msgLst = dtutils.dtGetNoSelMessage()
            noSelMsg1 = msgLst[0]
            noSelMsg2 = msgLst[1]

            if clipperLayer.selectedFeatureCount() == 0:
                self.iface.messageBar().pushMessage(
                    title, noSelMsg1 + " " + clipperLayer.name())
                return None
            elif clipperLayer.selectedFeatureCount() != 1:
                numSelSplitMsg = dtutils.dtGetManySelMessage(clipperLayer)
                self.iface.messageBar().pushMessage(title, numSelSplitMsg  + \
                    QtCore.QCoreApplication.translate(
                        "digitizingtools",
                        " Please select only one feature to clip with."
                    ))
            else:
                if passiveLayer.selectedFeatureCount() == 0:
                    msgLst = dtutils.dtGetNoSelMessage()
                    noSelMsg1 = msgLst[0]
                    noSelMsg2 = msgLst[1]
                    reply = QtWidgets.QMessageBox.question(None,  title,
                        noSelMsg1 + " " + passiveLayer.name() + "\n" + noSelMsg2,
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )

                    if reply == QtWidgets.QMessageBox.Yes:
                        passiveLayer.invertSelection()
                    else:
                        return None

                idsToProcess = []

                for aFeat in passiveLayer.selectedFeatures():
                    idsToProcess.append(aFeat.id())

                if clipperLayer.selectedFeatureCount() > 0:
                   # determine srs, we work in the project's srs
                    clipperCRSSrsid = clipperLayer.crs().srsid()
                    passiveCRSSrsid = passiveLayer.crs().srsid()
                    projectCRSSrsid = QgsProject.instance().crs().srsid()
                    passiveLayer.beginEditCommand(
                        QtCore.QCoreApplication.translate(
                            "editcommand", "Clip Features"
                        ))
                    featuresBeingClipped = 0

                    for feat in clipperLayer.selectedFeatures():
                        clipperGeom = QgsGeometry(feat.geometry())

                        if not clipperGeom.isGeosValid():
                            thisWarning = dtutils.dtGetInvalidGeomWarning(clipperLayer)
                            dtutils.dtShowWarning(self.iface, thisWarning)
                            continue

                        if clipperCRSSrsid != projectCRSSrsid:
                            clipperGeom.transform(QgsCoordinateTransform(
                                clipperLayer.crs(), QgsProject.instance().crs(),
                                QgsProject.instance()
                            ))

                        if passiveCRSSrsid != projectCRSSrsid:
                            bboxGeom = QgsGeometry(clipperGeom)
                            bboxGeom.transform(QgsCoordinateTransform(
                                QgsProject.instance().crs(), passiveLayer.crs(),
                                QgsProject.instance()))
                            bbox = bboxGeom.boundingBox()
                        else:
                            bbox = clipperGeom.boundingBox()

                        passiveLayer.selectByRect(bbox) # make a new selection

                        for selFeat in passiveLayer.selectedFeatures():
                            if idsToProcess.count(selFeat.id()) == 0:
                                continue

                            selGeom = QgsGeometry(selFeat.geometry())

                            if not selGeom.isGeosValid():
                                thisWarning = dtutils.dtGetInvalidGeomWarning(passiveLayer)
                                dtutils.dtShowWarning(self.iface, thisWarning)
                                continue

                            if passiveCRSSrsid != projectCRSSrsid:
                                selGeom.transform(
                                    QgsCoordinateTransform(passiveLayer.crs(),
                                    QgsProject.instance().crs(), QgsProject.instance()
                                ))

                            if clipperGeom.intersects(selGeom): # we have a candidate
                                newGeom = selGeom.intersection(clipperGeom)

                                if newGeom != None:
                                    if not newGeom.isEmpty():
                                        if passiveCRSSrsid != projectCRSSrsid:
                                            newGeom.transform(QgsCoordinateTransform(
                                                QgsProject.instance().crs(), passiveLayer.crs(),
                                                QgsProject.instance()))

                                        selFeat.setGeometry(newGeom)
                                        passiveLayer.updateFeature(selFeat)
                                        featuresBeingClipped += 1

                    if featuresBeingClipped == 0:
                        passiveLayer.destroyEditCommand()
                    else:
                        passiveLayer.endEditCommand()

                    passiveLayer.removeSelection()
                    self.iface.mapCanvas().refresh()

