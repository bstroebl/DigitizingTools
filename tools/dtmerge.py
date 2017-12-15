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
from PyQt4 import QtCore,  QtGui
from qgis.core import *
from qgis.gui import QgsMessageBar
import dt_icons_rc
from dttools import DtSingleButton
from dtToolsDialog import DigitizingToolsChooseRemaining

class DtMerge(DtSingleButton):
    '''Merge selected features of active layer'''
    def __init__(self, iface, toolBar):
        DtSingleButton.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/Merge.png"),
            QtCore.QCoreApplication.translate("digitizingtools",
                "Merge selected features"),
            geometryTypes = [1, 2, 3, 4, 5, 6],  dtName = "dtMerge")
        self.enable()

    def process(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate("digitizingtools", "Merge")
        processLayer = self.iface.activeLayer()
        pkFld = processLayer.pendingPkAttributesList()[0]
        pkValues = []
        featDict = {}
        fidsToDelete = []

        for aFeat in processLayer.selectedFeatures():
            aPkValue = aFeat[pkFld]
            pkValues.append(str(aPkValue))
            featDict[str(aPkValue)] = aFeat

        dlg = DigitizingToolsChooseRemaining(self.iface, processLayer, pkValues, featDict, title)
        doContinue = dlg.exec_()

        if doContinue == 1:
            pkValueToKeep = dlg.pkValueToKeep
            processLayer.beginEditCommand(
                QtCore.QCoreApplication.translate("editcommand",
                "Merge Features"))

            outFeat = featDict.pop(pkValueToKeep)
            outFid = outFeat.id()
            outGeom = QgsGeometry(outFeat.geometry())

            for aFeatVal in featDict.itervalues():
                fidsToDelete.append(aFeatVal.id())
                outGeom = outGeom.combine(QgsGeometry(aFeatVal.geometry()))

            if not self.geometryTypeMatchesLayer(processLayer, outGeom):
                self.iface.messageBar().pushMessage("DigitizingTools",
                    QtGui.QApplication.translate("DigitizingTools",
                    "The geometry type of the result is not valid in this layer!"),
                    level=QgsMessageBar.CRITICAL, duration = 10)
                processLayer.destroyEditCommand()
            else:
                processLayer.removeSelection()
                processLayer.changeGeometry(outFid, outGeom)

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

            doEnable = len(layer.pendingPkAttributesList()) == 1

            if doEnable:
                doEnable = layer.selectedFeatureCount() > 1

            self.act.setEnabled(doEnable)
            layer.selectionChanged.connect(self.enable)


