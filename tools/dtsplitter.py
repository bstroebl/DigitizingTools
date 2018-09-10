# -*- coding: utf-8 -*-
"""
dtsplitter
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

from builtins import str
from qgis.PyQt import QtCore,  QtGui
from qgis.core import *
import dt_icons_rc
import dtutils
from dttools import DtSingleButton

class DtSplitWithLine(DtSingleButton):
    '''Split selected features in active editable layer with selected line from another layer'''
    def __init__(self, iface,  toolBar):
        super().__init__(iface,  toolBar,
            QtGui.QIcon(":/splitter.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Split selected features with selected line from another layer"),
            geometryTypes = [2, 3, 5, 6],  dtName = "dtSplitWithLine")

        self.enable()

    def process(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate("digitizingtools", "Splitter")
        splitterLayer = dtutils.dtChooseVectorLayer(self.iface,  1,  msg = QtCore.QCoreApplication.translate("digitizingtools", "splitter layer"))

        if splitterLayer == None:
            self.iface.messageBar().pushMessage(title,  QtCore.QCoreApplication.translate("digitizingtools", "Please provide a line layer to split with."))
        else:
            passiveLayer = self.iface.activeLayer()
            msgLst = dtutils.dtGetNoSelMessage()
            noSelMsg1 = msgLst[0]

            if splitterLayer.selectedFeatureCount() == 0:
                self.iface.messageBar().pushMessage(title, noSelMsg1 + " " + splitterLayer.name())
                return None
            elif splitterLayer.selectedFeatureCount() != 1:
                numSelSplitMsg = dtutils.dtGetManySelMessage(splitterLayer)
                self.iface.messageBar().pushMessage(title, numSelSplitMsg  + \
                    QtCore.QCoreApplication.translate("digitizingtools", " Please select only one feature to split with."))
            else:
                if passiveLayer.selectedFeatureCount() == 0:
                    self.iface.messageBar().pushMessage(title,  noSelMsg1  + " " + passiveLayer.name() + ".\n" + \
                        QtCore.QCoreApplication.translate("digitizingtools", " Please select the features to be splitted."))
                    return None

               # determine srs, we work in the project's srs
                splitterCRSSrsid = splitterLayer.crs().srsid()
                passiveCRSSrsid = passiveLayer.crs().srsid()
                projectCRSSrsid = QgsProject.instance().crs().srsid()
                passiveLayer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Split features"))
                featuresBeingSplit = 0
                featuresToAdd = []

                for feat in splitterLayer.selectedFeatures():
                    splitterGeom = QgsGeometry(feat.geometry())

                    if not splitterGeom.isGeosValid():
                        thisWarning = dtutils.dtGetInvalidGeomWarning(splitterLayer)
                        dtutils.dtShowWarning(self.iface, thisWarning)
                        continue

                    if splitterCRSSrsid != projectCRSSrsid:
                        splitterGeom.transform(QgsCoordinateTransform(
                            splitterLayer.crs(),  QgsProject.instance().crs(),
                            QgsProject.instance()
                        ))

                    for selFeat in passiveLayer.selectedFeatures():
                        selGeom = QgsGeometry(selFeat.geometry())

                        if not selGeom.isGeosValid():
                            thisWarning = dtutils.dtGetInvalidGeomWarning(passiveLayer)
                            dtutils.dtShowWarning(self.iface, thisWarning)
                            continue

                        if passiveCRSSrsid != projectCRSSrsid:
                            selGeom.transform(QgsCoordinateTransform(
                                passiveLayer.crs(),  QgsProject.instance().crs(),
                                QgsProject.instance()
                            ))

                        if splitterGeom.intersects(selGeom): # we have a candidate
                            splitterPList = dtutils.dtExtractPoints(splitterGeom)

                            try:
                                result,  newGeometries,  topoTestPoints = selGeom.splitGeometry(splitterPList,  False) #QgsProject.instance().topologicalEditing())
                            except:
                                self.iface.messageBar().pushCritical(title,
                                    dtutils.dtGetErrorMessage() + QtCore.QCoreApplication.translate(
                                        "digitizingtools", "splitting of feature") + " " + str(selFeat.id()))
                                return None

                            if result == 0:
                                if passiveCRSSrsid != projectCRSSrsid:
                                    selGeom.transform(QgsCoordinateTransform(
                                        QgsProject.instance().crs(),  passiveLayer.crs(),
                                        QgsProject.instance()
                                    ))

                                selFeat.setGeometry(selGeom)
                                passiveLayer.updateFeature(selFeat)

                                if len(newGeometries) > 0:
                                    featuresBeingSplit += 1
                                    newFeatures = dtutils.dtMakeFeaturesFromGeometries(passiveLayer,  selFeat,  newGeometries)

                                    for newFeat in newFeatures:
                                        newGeom = QgsGeometry(newFeat.geometry())
                                        if passiveCRSSrsid != projectCRSSrsid:
                                            newGeom.transform(QgsCoordinateTransform(
                                                QgsProject.instance().crs(),  passiveLayer.crs(),
                                                QgsProject.instance()
                                            ))
                                            newFeat.setGeometry(newGeom)

                                        featuresToAdd.append(newFeat)

                if featuresBeingSplit > 0:
                    passiveLayer.addFeatures(featuresToAdd)
                    passiveLayer.endEditCommand()
                    passiveLayer.removeSelection()
                else:
                    passiveLayer.destroyEditCommand()
