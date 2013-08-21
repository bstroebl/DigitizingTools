# -*- coding: utf-8 -*-
"""
dtmovesidebydistance
````````````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-08-15
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
from qgis.gui import *

import icons_rc
from dtselectsegmenttool import DtSelectSegmentTool
from ui_dtmovesidebydistance import Ui_DtMoveSideByDistance
from dtmovesidebydistance_dialog import DtMoveSideByDistance_Dialog

class DtMoveSideByDistance():
    '''Automatically move polygon node (along a given side of polygon) in order to achieve a desired polygon area'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.gui = None
    
        # points of the selected segment
        # p1 is always the left point
        self.p1 = None
        self.p2 = None
        self.rb1 = QgsRubberBand(self.canvas,  False)
        #self.m1 = None
        self.selected_feature = None

        #create action
        self.side_mover = QtGui.QAction(QtGui.QIcon(":/ParallelMovePolygonSideByDistance.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Parallel move of polygon side to given distance"),  self.iface.mainWindow())
        
        self.side_mover.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.side_mover)
        self.enable()
        
        self.tool = DtSelectSegmentTool(self.canvas)

    def showDialog(self):
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        self.gui = DtMoveSideByDistance_Dialog(self.iface.mainWindow(),  flags)
        self.gui.initGui()
        self.gui.show()
        QObject.connect(self.gui, SIGNAL("unsetTool()"), self.unsetTool)
        QObject.connect(self.gui, SIGNAL("moveSide()"), self.moveSide)
    
    def enableSegmentTool(self):
        self.canvas.setMapTool(self.tool)
        #Connect to the DtSelectVertexTool
        QObject.connect(self.tool, SIGNAL("segmentFound(PyQt_PyObject)"), self.storeSegmentPoints)
        
    def unsetTool(self):
        self.p1 = None
        self.p2 = None
        self.selected_feature = None
        self.canvas.unsetMapTool(self.tool) 

    def run(self):
        '''Function that does all the real work'''
        layer = self.iface.activeLayer()
        title = QtCore.QCoreApplication.translate("digitizingtools", "Move polygon side by distance")
        
        if layer.selectedFeatureCount() == 0:
            QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please select one polygon to edit."))
        elif layer.selectedFeatureCount() > 1:
	    QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please select only one polygon to edit."))
        else:
            #One selected feature
            self.selected_feature = layer.selectedFeatures()[0]
            self.enableSegmentTool()
            self.showDialog()

    def storeSegmentPoints(self,  result):
        if result[0].x() < result[1].x():
            self.p1 = result[0]
            self.p2 = result[1]
        elif result[0].x() == result[1].x():
            self.p1 = result[0]
            self.p2 = result[1]
        else:
            self.p1 = result[1]
            self.p2 = result[0]      
       
    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.side_mover.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for polygon layers
                if layer.geometryType() == 2:
                    # enable if editable
                    self.side_mover.setEnabled(layer.isEditable())
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

    def moveSide(self):
        dist = 0.0
        try:
            dist = float(self.gui.targetDistance.text())
        except:
            pass
        
        if (dist == 0.0):
            QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Target Distance not valid."))
            return
        
        if self.p1 == None or self.p2 == None:
            QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Polygon side not selected."))
        else:
            touch_p1_p2 = self.selected_feature.geometry().touches(QgsGeometry.fromPolyline([self.p1, self.p2]))
            if (not touch_p1_p2):
                QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Selected segment should be on the selected polygon."))
            else:
                new_geom = createNewGeometry(self.selected_feature.geometry(), self.p1, self.p2, dist)
                fid = self.selected_feature.id()
                layer = self.iface.activeLayer()
                layer.beginEditCommand(QtCore.QCoreApplication.translate("digitizingtools", "Move Side By Distance"))
                layer.changeGeometry(fid,new_geom)
                self.canvas.refresh()
                layer.endEditCommand()


def createNewGeometry(geom, p1, p2, new_distance):
    
    pointList = geom.asPolygon()[0][0:-1]
    #Read input polygon geometry as a list of QgsPoints
    
    #indices
    ind = 0
    ind_max = len(pointList)-1
    p1_indx = -1
    p2_indx = -1
    
    #find p1 and p2 in the list
    for tmp_point in pointList:
        if (tmp_point == p1):
            p1_indx = ind
        elif (tmp_point == p2):
            p2_indx = ind
        ind += 1
    
    (p3,p4)=getParallelLinePoints(p1,p2,new_distance)
    
    pointList[p1_indx] = p3
    pointList[p2_indx] = p4
    new_geom = QgsGeometry.fromPolygon( [ pointList ] )
    
    return new_geom

def getParallelLinePoints(p1,  p2, dist):
    """
    This function is adopted/adapted from 'CadTools Plugin', Copyright (C) Stefan Ziegler
    """    
    if dist == 0:
        g = (p1, p2)
        return g

    dn = ( (p1.x()-p2.x())**2 + (p1.y()-p2.y())**2 )**0.5
    x3 = p1.x() + dist*(p1.y()-p2.y()) / dn
    y3 = p1.y() - dist*(p1.x()-p2.x()) / dn  
    p3 = QgsPoint(x3,  y3)       
    
    x4 = p2.x() + dist*(p1.y()-p2.y()) / dn
    y4 = p2.y() - dist*(p1.x()-p2.x()) / dn  
    p4 = QgsPoint(x4,  y4)       
    
    g = (p3,p4)
    return g
