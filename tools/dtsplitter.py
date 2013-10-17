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

from PyQt4 import QtCore,  QtGui
from qgis.core import *
import icons_rc
import dtutils
from dttools import DtSingleButton

class DtSplitWithLine(DtSingleButton):
    '''Split selected features in active editable layer with selected line from another layer'''
    def __init__(self, iface,  toolBar):
        DtSingleButton.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/splitter.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Split selected features with selected line(s) from another layer"),
            geometryTypes = [1, 2])

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
            noSelMsg2 = msgLst[1]

            if splitterLayer.selectedFeatureCount() == 0:

                reply = QtGui.QMessageBox.question(None,  title,
                                                   noSelMsg1 + " " + splitterLayer.name() + "\n" + noSelMsg2,
                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No )

                if reply == QtGui.QMessageBox.Yes:
                    splitterLayer.invertSelection()
                else:
                    return None

            if splitterLayer.selectedFeatureCount() > 0:
                if passiveLayer.selectedFeatureCount() == 0:
                    self.iface.messageBar().pushMessage(title,  noSelMsg1  + " " + passiveLayer.name() + ".\n" + \
                        QtCore.QCoreApplication.translate("digitizingtools", "Please select the features to be splitted."))
                    return None

               # determine srs, we work in the project's srs
                splitterCRSSrsid = splitterLayer.crs().srsid()
                passiveCRSSrsid = passiveLayer.crs().srsid()
                mc = self.iface.mapCanvas()
                renderer = mc.mapRenderer()
                projectCRSSrsid = renderer.destinationCrs().srsid()
                passiveLayer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Split features"))
                featuresBeingSplit = 0
                featuresToAdd = []

                for feat in splitterLayer.selectedFeatures():
                    splitterGeom = feat.geometry()

                    if splitterCRSSrsid != projectCRSSrsid:
                        splitterGeom.transform(QgsCoordinateTransform(splitterCRSSrsid,  projectCRSSrsid))

                    for selFeat in passiveLayer.selectedFeatures():
                        selGeom = selFeat.geometry()

                        if passiveCRSSrsid != projectCRSSrsid:
                            selGeom.transform(QgsCoordinateTransform(passiveCRSSrsid,  projectCRSSrsid))

                        if splitterGeom.intersects(selGeom): # we have a candidate
                            splitterPList = dtutils.dtExtractPoints(splitterGeom)

                            try:
                                result,  newGeometries,  topoTestPoints = selGeom.splitGeometry(splitterPList,  False) #QgsProject.instance().topologicalEditing())
                            except:
                                self.iface.messageBar().pushMessage(title,
                                    dtutils.dtGetErrorMessage() + QtCore.QCoreApplication.translate("digitizingtools", "splitting of feature") + " " + str(selFeat.id()),
                                    level=QgsMessageBar.CRITICAL)
                                return None

                            if result == 0:
                                selFeat.setGeometry(selGeom)
                                passiveLayer.updateFeature(selFeat)

                                if len(newGeometries) > 0:
                                    featuresBeingSplit += 1
                                    newFeatures = dtutils.dtMakeFeaturesFromGeometries(passiveLayer,  selFeat,  newGeometries)

                                    for newFeat in newFeatures:
                                        newGeom = newFeat.geometry()

                                        if passiveCRSSrsid != projectCRSSrsid:
                                            newGeom.transform(QgsCoordinateTransform( projectCRSSrsid,  passiveCRSSrsid))
                                            newFeat.setGeometry(newGeom)

                                        featuresToAdd.append(newFeat)

                if featuresBeingSplit > 0:
                    passiveLayer.addFeatures(featuresToAdd,  False)
                    passiveLayer.endEditCommand()
                    passiveLayer.removeSelection()
                else:
                    passiveLayer.destroyEditCommand()
