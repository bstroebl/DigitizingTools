# -*- coding: utf-8 -*-
"""
dtmovenodebyarea
````````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-02-25
* copyright            : (C) 2013 by Angelos Tzotsos
* email                : tzotsos@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
from PyQt4 import QtCore,  QtGui
from qgis.core import *
import icons_rc
from dtselectvertextool import DtSelectVertexTool
from ui_dtselectvertextool import Ui_DtMoveNodeByArea
from dtmovenodebyarea_dialog import DtMoveNodeByArea_Dialog

class DtMoveNodeByArea():
    '''Automatically move polygon node (along a given side of polygon) in order to achieve a desired polygon area'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface

        #create action
        self.node_mover = QtGui.QAction(QtGui.QIcon(":/MovePolygonNodeByArea.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Automatically move polygon node along a side to achieve desired area"),  self.iface.mainWindow())
        self.node_mover.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.node_mover)
        self.enable()

    def run(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate("digitizingtools", "Move polygon node by area")
        layer = self.iface.activeLayer()
        
        if layer.selectedFeatureCount() == 0:
            QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please select one polygon to edit."))
        elif layer.selectedFeatureCount() > 1:
	    QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please select only one polygon to edit."))
        else:
            QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Works!"))
            #Enable vertex selection tool
            #Show GUI
            #Save changes to geometry

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.node_mover.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for polygon layers
                if layer.geometryType() == 2:
                    # enable if editable
                    self.node_mover.setEnabled(layer.isEditable())
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

