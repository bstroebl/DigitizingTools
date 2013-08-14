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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import icons_rc
from dtselectvertextool import DtSelectVertexTool
from ui_dtmovenodebyarea import Ui_DtMoveNodeByArea
from dtmovenodebyarea_dialog import DtMoveNodeByArea_Dialog

class DtMoveNodeByArea():
    '''Automatically move polygon node (along a given side of polygon) in order to achieve a desired polygon area'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.gui = None
        
        # Points and Markers
        self.p1 = None
        self.p2 = None
        self.m1 = None
        self.m2 = None
        self.selected_feature = None

        #create action
        self.node_mover = QtGui.QAction(QtGui.QIcon(":/MovePolygonNodeByArea.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Automatically modify polygon to target area moving one node"),  self.iface.mainWindow())
        
        self.node_mover.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.node_mover)
        self.enable()
        
        self.tool = DtSelectVertexTool(self.canvas)

    def showDialog(self):
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        self.gui = DtMoveNodeByArea_Dialog(self.iface.mainWindow(),  flags)
        self.gui.initGui()
        self.gui.show()
        QObject.connect(self.gui, SIGNAL("unsetTool()"), self.unsetTool)
        QObject.connect(self.gui, SIGNAL("moveNode()"), self.moveNode)
    
    def enableVertexTool(self):
        self.canvas.setMapTool(self.tool)
        #Connect to the DtSelectVertexTool
        QObject.connect(self.tool, SIGNAL("vertexFound(PyQt_PyObject)"), self.storeVertexPointsAndMarkers)
        
    def unsetTool(self):
        self.m1 = None
        self.m2 = None
        self.p1 = None
        self.p2 = None
        self.selected_feature = None
        self.canvas.unsetMapTool(self.tool) 

    def run(self):
        '''Function that does all the real work'''
        layer = self.iface.activeLayer()
        title = QtCore.QCoreApplication.translate("digitizingtools", "Move polygon node by area")
        
        if layer.selectedFeatureCount() == 0:
            QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please select one polygon to edit."))
        elif layer.selectedFeatureCount() > 1:
	    QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please select only one polygon to edit."))
        else:
            #One selected feature
            self.selected_feature = layer.selectedFeatures()[0]
            self.enableVertexTool()
            self.showDialog()
            self.gui.writeArea(self.selected_feature.geometry().area())

            
    def storeVertexPointsAndMarkers(self,  result):
        self.p1 = result[0]
        self.p2 = result[1]
        self.m1 = result[2]
        self.m2 = result[3]

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

    
    def moveNode(self):
        new_a = -1.0
        try:
            new_a = float(self.gui.targetArea.text())
        except:
            pass
        
        if (new_a == -1.0):
            QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Target Area not valid."))
            return
        
        if self.p1 == None or self.p2 == None:
            QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Not enough vertices selected."))
        else:
            interp1 = self.selected_feature.geometry().intersects(QgsGeometry.fromPoint(self.p1))
            interp2 = self.selected_feature.geometry().intersects(QgsGeometry.fromPoint(self.p2))
            touch_p1_p2 = self.selected_feature.geometry().touches(QgsGeometry.fromPolyline([self.p1, self.p2]))
            if (interp1 and interp2):
                if (not touch_p1_p2):
                    QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Selected vertices should be consecutive on the selected polygon."))
                else:
                    title = QtCore.QCoreApplication.translate("digitizingtools", "Move polygon node by area")
                    wkt_tmp = self.selected_feature.geometry().exportToWkt()
                    tmp_str = wkt_tmp + " p1:" + str(self.p1.x()) + ", " + str(self.p1.y()) + " p2:" + str(self.p2.x()) + ", " + str(self.p2.y())
                    QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", tmp_str))
            else:
                QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Vertices not on the selected polygon."))

def createNewGeometry(geom, p1, p2, new_area):
    x1 = p1.x()
    y1 = p1.y()
    x2 = p2.x()
    y2 = p2.y()
    old_area = geom.area()
    area_diff = new_area-old_area
    
    x3 = 0.0
    y3 = 0.0
    return
