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

class DtSplitMultiPartTool():
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface

        #create action
         #":/plugins/digitizingtools/icons/multi_to_single.png"),
        self.act_splitmultipart = QtGui.QAction(QtGui.QIcon(":/multi_to_single.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Split multi part to single part"),  self.iface.mainWindow())
        self.act_splitmultipart.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act_splitmultipart)
        self.enable()

    def run(self):
        layer = self.iface.mapCanvas().currentLayer()
        provider = layer.dataProvider()
        newFeatures = []
        n_of_splitted_features = 0
        layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Split features"))

        for feature in layer.selectedFeatures():
            geom = feature.geometry()
            # if feature geometry is multipart starts split processing
            if geom.isMultipart():
                n_of_splitted_features += 1
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
        else:
            layer.destroyEditCommand()

    def enable(self):
       # Disable the Button by default
        self.act_splitmultipart.setEnabled(False)
        layer = self.iface.mapCanvas().currentLayer()

        if layer <> None:
            ## Only for vector layers.
            if layer.type() == 0:
                if layer.geometryType() < 3: # 3 = unknown, 4=no geometry
                    # enable if editable
                    self.act_splitmultipart.setEnabled(layer.isEditable())
                    try:
                        layer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable) # when it becomes active layer again
                    except:
                        pass
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)


