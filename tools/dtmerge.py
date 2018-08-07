# -*- coding: utf-8 -*-
"""
dtmerge
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions
Tool: Merge features to a new feature _without deleting all of them_
see http://hub.qgis.org/issues/13490

* begin                : 2015-11-09
* copyright          : (C) 2015 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import str
from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis.core import *
import dt_icons_rc
from dttools import DtSingleButton
from dtToolsDialog import DigitizingToolsChooseRemaining

class DtMerge(DtSingleButton):
    '''Merge selected features of active layer'''
    def __init__(self, iface, toolBar):
        super().__init__(iface,  toolBar,
            QtGui.QIcon(":/Merge.png"),
            QtCore.QCoreApplication.translate("digitizingtools",
                "Merge selected features"),
            geometryTypes = [1, 2, 3, 4, 5, 6],  dtName = "dtMerge")
        self.enable()

    def process(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate("digitizingtools", "Merge")
        processLayer = self.iface.activeLayer()
        pkAtts = processLayer.primaryKeyAttributes()

        if len(pkAtts) == 1:
            pkFld = pkAtts[0]
        else:
            pkFld = None

        pkValues = {}
        featDict = {}
        fidsToDelete = []

        for aFeat in processLayer.selectedFeatures():
            aFid = aFeat.id()
            featDict[aFid] = aFeat

            if aFid >= 0: # only already existing features
                if pkFld == None:
                    pkValues["Feature ID " + str(aFid)] = aFid
                else:
                    aPkValue = aFeat[pkFld]
                    pkValues[str(aPkValue)] = aFid

        if len(pkValues) > 1:
            dlg = DigitizingToolsChooseRemaining(self.iface, processLayer, pkValues, featDict, title)
            doContinue = dlg.exec_()

            if doContinue == 1:
                pkValueToKeep = dlg.pkValueToKeep
        elif len(pkValues) == 1:
            doContinue = 1
            pkValueToKeep = list(pkValues.keys())[0]
        else: # all new features
            doContinue = 1
            pkValueToKeep = None

        if doContinue == 1:
            processLayer.beginEditCommand(
                QtCore.QCoreApplication.translate("editcommand",
                "Merge Features"))

            if pkValueToKeep != None:
                outFeat = featDict.pop(pkValues[pkValueToKeep])
            else:
                outFeat = featDict.popitem()[1] # use any

            outFid = outFeat.id()
            outGeom = QgsGeometry(outFeat.geometry())

            for aFeatVal in list(featDict.values()):
                fidsToDelete.append(aFeatVal.id())
                outGeom = outGeom.combine(QgsGeometry(aFeatVal.geometry()))

            if not self.geometryTypeMatchesLayer(processLayer, outGeom):
                self.iface.messageBar().pushCritical("DigitizingTools",
                    QtWidgets.QApplication.translate("DigitizingTools",
                    "The geometry type of the result is not valid in this layer!"))
                processLayer.destroyEditCommand()
            else:
                processLayer.removeSelection()
                success = processLayer.changeGeometry(outFid, outGeom)

                for aFid in fidsToDelete:
                    if not processLayer.deleteFeature(aFid):
                        processLayer.destroyEditCommand()
                        return None
                processLayer.endEditCommand()
                self.iface.mapCanvas().refresh()

    def enable(self):
        '''Enables/disables the corresponding button.'''
        DtSingleButton.enable(self) # call parent's method

        if self.act.isEnabled():
            layer = self.iface.activeLayer()
            try:
                layer.selectionChanged.disconnect(self.enable) # disconnect, will be reconnected
            except:
                pass

            doEnable = layer.selectedFeatureCount() > 1
            self.act.setEnabled(doEnable)
            layer.selectionChanged.connect(self.enable)


