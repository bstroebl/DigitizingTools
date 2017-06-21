# -*- coding: utf-8 -*-
"""
dtsplitfeature
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2017-06-12
* copyright          : (C) 2017 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
from PyQt4 import QtCore,  QtGui
from qgis.core import *
from qgis.gui import *
import dt_icons_rc
from dtsplitfeaturetool import DtSplitFeatureTool
from dttools import DtSingleEditTool
import dtutils

class DtSplitFeature(DtSingleEditTool):
    '''Split feature'''
    def __init__(self, iface,  toolBar):
        DtSingleEditTool.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/splitfeature.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Split Features"),
            geometryTypes = [2, 3, 5, 6],  dtName = "dtSplitFeature")

        self.tool = DtSplitFeatureTool(self.canvas, self.iface)
        self.tool.finishedDigitizing.connect(self.digitizingFinished)
        self.reset()
        self.enable()

    def reset(self):
        self.editLayer = None
        self.feature = None
        self.rubberBand = None

    def digitizingFinished(self, splitGeom):
        title = QtCore.QCoreApplication.translate("digitizingtools", "Split Features")
        hlColor, hlFillColor, hlBuffer,  hlMinWidth = dtutils.dtGetHighlightSettings()
        selIds = self.editLayer.selectedFeaturesIds()
        self.editLayer.removeSelection()
        splitterPList = dtutils.dtExtractPoints(splitGeom)
        featuresToAdd = [] # store new features in this array
        featuresToKeep = {} # store geoms that will stay with their id as key
        featuresToSplit = {}

        for aFeat in self.editLayer.getFeatures(QgsFeatureRequest(splitGeom.boundingBox())):
            anId = aFeat.id()

            # work either on selected or all features if no selection exists
            if len(selIds) == 0 or selIds.count(anId) != 0:
                aGeom = aFeat.geometry()

                if splitGeom.intersects(aGeom):
                    featuresToSplit[anId] = aFeat

        if len(featuresToSplit) > 0:
            self.editLayer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Features split"))

        for anId, aFeat in featuresToSplit.iteritems():
            aGeom = aFeat.geometry()
            wasMultipart = aGeom.isMultipart()
            splitResult = []
            geomsToSplit = []

            if wasMultipart:
                keepGeom = None

                for aPart in aGeom.asGeometryCollection():
                    if splitGeom.intersects(aPart):
                        geomsToSplit.append(aPart)
                    else:
                        if keepGeom == None:
                            keepGeom = aPart
                        else:
                            keepGeom = keepGeom.combine(aPart)
            else:
                geomsToSplit.append(aGeom)

            for thisGeom in geomsToSplit:
                try:
                    result,  newGeometries,  topoTestPoints = thisGeom.splitGeometry(splitterPList,  False)
                except:
                    self.iface.messageBar().pushMessage(title,
                        dtutils.dtGetErrorMessage() + QtCore.QCoreApplication.translate(
                            "digitizingtools", "splitting of feature") + " " + str(aFeat.id()),
                        level=QgsMessageBar.CRITICAL)
                    return None

                if result == 0: # success
                    if len(newGeometries) > 0:
                        splitResult = newGeometries

                        if wasMultipart:
                            splitResult.append(thisGeom)

                if wasMultipart and len(splitResult) > 1:
                    takeThisOne = -1

                    while takeThisOne == -1:
                        for i in range(len(splitResult)):
                            aNewGeom = splitResult[i]
                            hl = QgsHighlight(self.iface.mapCanvas(), aNewGeom, self.editLayer)
                            hl.setColor(hlColor)
                            hl.setFillColor(hlFillColor)
                            hl.setBuffer(hlBuffer)
                            hl.setWidth(hlMinWidth)
                            answer = QtGui.QMessageBox.question(
                                None, QtCore.QCoreApplication.translate("digitizingtools", "Split Multipart Feature"),
                                QtCore.QCoreApplication.translate("digitizingtools", "Create new feature from this part?"),
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel | QtGui.QMessageBox.NoToAll)

                            if answer == QtGui.QMessageBox.Yes:
                                takeThisOne = i
                                break
                            elif answer == QtGui.QMessageBox.NoToAll:
                                keepGeom = aGeom
                                newGeoms = []
                                takeThisOne = -2
                                break
                            elif answer == QtGui.QMessageBox.Cancel:
                                return None

                    if takeThisOne == -2:
                        break
                    elif takeThisOne >= 0:
                        newGeoms = [splitResult.pop(takeThisOne)]

                        if len(splitResult) > 0: #should be
                            for aNewGeom in splitResult:
                                if keepGeom == None:
                                    keepGeom = aNewGeom
                                else:
                                    keepGeom = keepGeom.combine(aNewGeom)
                else: # singlePart
                    keepGeom = thisGeom
                    newGeoms = newGeometries

                newFeatures = dtutils.dtMakeFeaturesFromGeometries(self.editLayer,  aFeat,  newGeoms)
                featuresToAdd = featuresToAdd + newFeatures

            aFeat.setGeometry(keepGeom)
            featuresToKeep[anId] = aFeat

        for anId,  aFeat in featuresToKeep.iteritems():
            aGeom = aFeat.geometry()
            self.editLayer.updateFeature(aFeat)

        if len(featuresToAdd) > 0:
            self.editLayer.addFeatures(featuresToAdd,  False)
            self.editLayer.endEditCommand()
        else:
            self.editLayer.destroyEditCommand()

        if hasattr(self.editLayer, "selectByIds"): # since QGIS 2.16
            self.editLayer.selectByIds(selIds)
        else:
            self.editLayer.setSelectedFeatures(selIds)

    def process(self):
        self.canvas.setMapTool(self.tool)
        self.act.setChecked(True)
        self.editLayer = self.iface.activeLayer()


