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
from qgis.PyQt import QtCore,  QtGui, QtWidgets
from qgis.core import *
import dt_icons_rc
import dtutils
from dttools import DtDualToolSelectPolygon

class DtCutWithPolygon(DtDualToolSelectPolygon):
    '''Cut out from active editable layer with selected polygon from another layer'''
    def __init__(self, iface,  toolBar):
        super().__init__(iface,  toolBar,
            QtGui.QIcon(":/cutter.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Cut with polygon (interactive)"),
            QtGui.QIcon(":/cutter_batch.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Cut with selected polygons"),
            geometryTypes = [3, 6],  dtName = "dtCutter")
        self.enable()
        self.lastChoice = [None, False]

    def process(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate("digitizingtools", "Cutter")
        showEmptyWarning = True
        choice = None
        fidsToDelete = []
        processLayer = self.iface.activeLayer()

        if processLayer.selectedFeatureCount() == 0:
            msgLst = dtutils.dtGetNoSelMessage()
            noSelMsg1 = msgLst[0]
            noSelMsg2 = msgLst[1]
        else:
            cutterGeoms = []

            for feat in processLayer.selectedFeatures():
                cutterGeom = feat.geometry()

                if not cutterGeom.isGeosValid():
                    thisWarning = dtutils.dtGetInvalidGeomWarning(processLayer)
                    dtutils.dtShowWarning(self.iface, thisWarning)
                    continue
                else:
                    cutterGeoms.append(cutterGeom)

            if len(cutterGeoms) == 0:
                return None # could be only invalid geoms selected

        processLayer.invertSelection()
        idsToProcess = []

        for aFeat in processLayer.selectedFeatures():
            # was:  if isSameLayer:
            #    for aFeat in processLayer.getFeatures()
            idsToProcess.append(aFeat.id())

        processLayer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Cut Features"))
        featuresBeingCut = 0
        noMatchWarning = dtutils.dtGetNotMatchingGeomWarning(processLayer)

        for cutterGeom in cutterGeoms:
            if cutterGeom.wkbType() == 6:
                cutterGeom = QgsGeometry.fromMultiPolygonXY(cutterGeom.asMultiPolygon())
            else:
                cutterGeom = QgsGeometry.fromPolygonXY(cutterGeom.asPolygon())

            bbox = cutterGeom.boundingBox()

            processLayer.selectByRect(bbox) # make a new selection

            for selFeat in processLayer.selectedFeatures():
                if idsToProcess.count(selFeat.id()) == 0:
                    continue

                selGeom = selFeat.geometry()

                if selGeom.isGeosEqual(cutterGeom):
                    continue # do not cut the same geometry

                if not selGeom.isGeosValid():
                    thisWarning = dtutils.dtGetInvalidGeomWarning(processLayer)
                    dtutils.dtShowWarning(self.iface, thisWarning)
                    continue

                if cutterGeom.intersects(selGeom): # we have a candidate
                    newGeom = selGeom.difference(cutterGeom)

                    if newGeom != None:
                        if newGeom.isEmpty() or newGeom.area() == 0:
                            #selGeom is completely contained in cutterGeom
                            if showEmptyWarning:
                                choice = QtWidgets.QMessageBox.question(None,  title,
                                    QtCore.QCoreApplication.translate("digitizingtools",
                                    "A feature would be completely removed by cutting. Delete this feature\'s dataset altogether?"),
                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.YesToAll |
                                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.NoToAll |
                                    QtWidgets.QMessageBox.Cancel)

                                if choice == QtWidgets.QMessageBox.Cancel:
                                    processLayer.destroyEditCommand()
                                    processLayer.removeSelection()
                                    return None
                                else:
                                    showEmptyWarning = (choice == QtWidgets.QMessageBox.Yes or choice == QtWidgets.QMessageBox.No)

                            if choice == QtWidgets.QMessageBox.Yes or choice == QtWidgets.QMessageBox.YesToAll:
                                fidsToDelete.append(selFeat.id())
                        else:
                            if not self.geometryTypeMatchesLayer(processLayer, newGeom):
                                newMsg = QtCore.QCoreApplication.translate(
                                    "digitizingtools", "New geometry")
                                dtutils.dtShowWarning(self.iface, newMsg + ": " + noMatchWarning)

                            selFeat.setGeometry(newGeom)
                            processLayer.updateFeature(selFeat)
                            featuresBeingCut += 1

        if len(fidsToDelete) > 0:
            for fid in fidsToDelete:
                if not processLayer.deleteFeature(fid):
                    processLayer.destroyEditCommand()
                    return None

        if featuresBeingCut > 0 or len(fidsToDelete) > 0:
            processLayer.endEditCommand()
        else: # nothing happened
            processLayer.destroyEditCommand()

        processLayer.removeSelection()
        self.iface.mapCanvas().refresh()

