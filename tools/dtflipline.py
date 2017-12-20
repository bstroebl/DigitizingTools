# -*- coding: utf-8 -*-
"""
dtflipline
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
from qgis.PyQt import QtCore,  QtGui
from qgis.core import *
from qgis.gui import *
import dt_icons_rc
from dttools import DtDualToolSelectFeature

class DtFlipLine(DtDualToolSelectFeature):
    '''Flip line direction tool'''
    def __init__(self, iface,  toolBar):
        super().__init__(iface,  toolBar,
            QtGui.QIcon(":/flipLine.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Flip line (interactive mode)"),
            QtGui.QIcon(":/flipLineBatch.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Flip selected lines"),
            geometryTypes = [2, 5],  dtName = "dtFlipLine")

    def process(self):
        '''algorythm taken from Nathan Woodrow's Swap Line Direction see
       http://gis.stackexchange.com/questions/9261/how-can-i-switch-line-direction-in-qgis
       adapted to use with MultiPolylines '''
        layer = self.iface.activeLayer()

        if layer.selectedFeatureCount() == 1:
            layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Flip line"))
        elif layer.selectedFeatureCount() > 1:
            layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Flip lines"))
        else:
            return None

        hadError = False

        for feat in layer.selectedFeatures():
            geom = QgsGeometry(feat.geometry())

            if not geom.isGeosValid():
                thisWarning = dtutils.dtGetInvalidGeomWarning(layer)
                dtutils.dtShowWarning(self.iface, thisWarning)
                continue

            if layer.wkbType() == 2 or layer.wkbType() == -2147483646:
                nodes = geom.asPolyline()
                rNodes = self.reverse(nodes)
                newNodes = rNodes
            elif layer.wkbType() == 5 or layer.wkbType() ==-2147483643:
                newNodes = []

                for aLine in geom.asGeometryCollection():
                    aNodes = aLine.asPolyline()
                    rNodes = self.reverse(aNodes)
                    newNodes.append(rNodes)
            else: # should not happen as tool is deactivated in all other cases
                newNodes = []

            if layer.wkbType() == 2 or layer.wkbType() == -2147483646:
                newGeom = QgsGeometry.fromPolyline(newNodes)
            else:
                newGeom = QgsGeometry.fromMultiPolyline(newNodes)

            if not layer.changeGeometry(feat.id(),  newGeom):
                hadError = True

        if hadError:
            self.iface.messageBar().pushMessage(QtCore.QCoreApplication.translate("digitizingtools",
                "An error occured during flipping", level=QgsMessageBar.CRITICAL))
            layer.destroyEditCommand()
        else:
            layer.endEditCommand()
            self.canvas.refresh()

    def reverse(self,  nodes):
        '''reverse the order in array nodes
        nodes.reverse does not work with 25D geometries'''
        rNodes = []
        while len(nodes) > 0:
            rNodes.append(nodes.pop())

        return rNodes
