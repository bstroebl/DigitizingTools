# -*- coding: utf-8 -*-
"""
dtextractpart
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions
Tool: Extract an part of a multifart feature and add it as new feature

* begin                : 2014-07-09
* copyright          : (C) 2014 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from PyQt4 import QtCore,  QtGui
from qgis.core import *
import dtutils
import icons_rc
from dttools import DtSingleTool,  DtSelectPartTool

class DtExtractPartTool(DtSingleTool):
    def __init__(self, iface,  toolBar):
        DtSingleTool.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/ExtractPart.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Delete part and add it as a new feature"),
            geometryTypes = [4, 5, 6], dtName = "dtExtractPart")

        self.tool = DtSelectPartTool(self.canvas, self.iface)
        self.tool.partSelected.connect(self.partSelected)
        self.enable()

    def process(self):
        self.canvas.setMapTool(self.tool)
        self.act.setChecked(True)

    def partSelected(self, part):
        fid = part[0]
        partNumber = part[1]
        aPart = part[2]
        layer = self.iface.mapCanvas().currentLayer()
        feature = dtutils.dtGetFeatureForId(layer,  fid)
        geom = QgsGeometry(feature.geometry())

        if geom.deletePart(partNumber):
            layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Extract part"))
            aFeat = dtutils.dtCopyFeature(layer,  feature)
            aFeat.setGeometry(aPart)
            layer.addFeature(aFeat)
            feature.setGeometry(geom)
            layer.updateFeature(feature)
            layer.endEditCommand()
            self.canvas.refresh()

        self.tool.reset()
