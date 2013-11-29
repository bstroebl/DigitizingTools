# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DigitizingTools
 A QGIS plugin
 Subsumes different tools useful during digitizing sessions
 Tool: SplitMultipart features into single part
 integrated into DigitizingTools by Bernhard Ströbl
                             -------------------
        begin                : 2013-01-17
        copyright            : (C) 2013 by Alexandre Neto
        email                : senhor.neto@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4 import QtCore,  QtGui
from qgis.core import *
import dtutils
import icons_rc
from dttools import DtDualToolSelectFeature

class DtSplitMultiPartTool(DtDualToolSelectFeature):
    def __init__(self, iface,  toolBar):
        DtDualToolSelectFeature.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/MultiToSingle.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Split multi-part feature to single part (interactive mode)"),
            QtGui.QIcon(":/MultiToSingleBatch.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Split selected multi-part features to single part"),  dtName = "dtSplitMultiPart")

    def process(self):
        layer = self.iface.mapCanvas().currentLayer()
        newFeatures = []

        if layer.selectedFeatureCount() == 1:
            editCommand = QtCore.QCoreApplication.translate("editcommand", "Split feature")
        elif layer.selectedFeatureCount() > 1:
            editCommand = QtCore.QCoreApplication.translate("editcommand", "Split features")

        for feature in layer.selectedFeatures():
            geom = feature.geometry()
            # if feature geometry is multipart starts split processing
            if geom.isMultipart():
                if len(newFeatures) == 0:
                    layer.beginEditCommand(editCommand)

                # Get parts from original feature
                parts = geom.asGeometryCollection ()
                # update feature geometry to hold first part single geometry
                # (this way one of the output feature keeps the original Id)
                feature.setGeometry(parts.pop(0))
                layer.updateFeature(feature)
                # create new features from parts and add them to the list of newFeatures
                newFeatures = newFeatures + dtutils.dtMakeFeaturesFromGeometries(layer,  feature,  parts)

        # add new features to layer
        if len(newFeatures) > 0:
            layer.addFeatures(newFeatures, False)
            layer.endEditCommand()
