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
from PyQt4 import QtCore,  QtGui
from qgis.core import *
from qgis.gui import *
import icons_rc
from dttools import DtDualToolSelectFeature

class DtFlipLine(DtDualToolSelectFeature):
    '''Flip line direction tool'''
    def __init__(self, iface,  toolBar):
        DtDualToolSelectFeature.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/flipLine.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Flip line (interactive mode)"),
            QtGui.QIcon(":/flipLineBatch.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Flip selected lines"),
            geometryTypes = [1],  dtName = "dtFlipLine")

    def process(self):
        '''algorythm taken from Nathan Woodrow's Swap Line Direction see
       http://gis.stackexchange.com/questions/9261/how-can-i-switch-line-direction-in-qgis '''
        layer = self.iface.activeLayer()

        if layer.selectedFeatureCount() == 1:
            layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Flip line"))
        elif layer.selectedFeatureCount() > 1:
            layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Flip lines"))
        else:
            return None

        hadError = False

        for feat in layer.selectedFeatures():
            geom = feat.geometry()
            nodes = geom.asPolyline()
            nodes.reverse()
            newGeom = QgsGeometry.fromPolyline(nodes)

            if not layer.changeGeometry(feat.id(),  newGeom):
                hadError = True

        if hadError:
            self.iface.messageBar().pushMessage(QtCore.QCoreApplication.translate("digitizingtools",
                "An error occured during flipping", level=QgsMessageBar.CRITICAL))
            layer.destroyEditCommand()
        else:
            layer.endEditCommand()
            self.canvas.refresh()
