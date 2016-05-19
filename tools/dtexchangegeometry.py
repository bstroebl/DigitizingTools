# -*- coding: utf-8 -*-
"""
dtexchangegeometry
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions
Tool: Exchange the geometry between two features

* begin                : 2015-12-09
* copyright          : (C) 2015 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from PyQt4 import QtCore,  QtGui
from qgis.core import *
import dtutils
import dt_icons_rc
from dttools import DtSingleButton

class DtExchangeGeometry(DtSingleButton):
    def __init__(self, iface, toolBar):
        DtSingleButton.__init__(self, iface, toolBar,
            QtGui.QIcon(":/exchangeGeometry.png"),
            QtCore.QCoreApplication.translate("digitizingtools",
                "Exchange the geomteries between selected features"),
            geometryTypes = [1, 2, 3, 4, 5, 6], dtName = "dtExchangeGeometry")

        self.enable()

    def process(self):
        layer = self.iface.mapCanvas().currentLayer()
        feats = layer.selectedFeatures()
        feature1 = feats[0]
        geom1 = QgsGeometry(feature1.geometry())
        feature2 = feats[1]
        geom2 = QgsGeometry(feature2.geometry())
        layer.beginEditCommand(QtCore.QCoreApplication.translate(
            "editcommand", "Exchange geometries"))
        feature1.setGeometry(geom2)
        layer.updateFeature(feature1)
        feature2.setGeometry(geom1)
        layer.updateFeature(feature2)
        layer.endEditCommand()
        self.canvas.refresh()

    def enable(self):
        '''Enables/disables the corresponding button.'''
        DtSingleButton.enable(self) # call parent's method

        if self.act.isEnabled():
            layer = self.iface.activeLayer()
            try:
                layer.selectionChanged.disconnect(self.enable) # disconnect, will be reconnected
            except:
                pass

            doEnable = layer.selectedFeatureCount() == 2
            self.act.setEnabled(doEnable)
            layer.selectionChanged.connect(self.enable)
