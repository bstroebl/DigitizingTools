# -*- coding: utf-8 -*-
"""
dtmovesidebyarea
````````````````
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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import dt_icons_rc
import math
from dttools import DtSelectSegmentTool
from dtmovesidebyarea_dialog import DtMoveSideByArea_Dialog

class DtMoveSideByArea():
    '''Parallel move polygon side in order to achieve a desired polygon area'''
    def __init__(self, iface, toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.gui = None
        self.multipolygon_detected = False

        # points of the selected segment
        # p1 is always the left point
        self.p1 = None
        self.p2 = None
        self.rb1 = QgsRubberBand(self.canvas,  False)
        self.selected_feature = None

        #create action
        self.side_mover = QtGui.QAction(QtGui.QIcon(":/ParallelMovePolygonSideByArea.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Parallel move of polygon side to target area"), self.iface.mainWindow())

        self.side_mover.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.side_mover)
        self.enable()
        self.tool = DtSelectSegmentTool(self.canvas, self.iface)

    def showDialog(self):
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        self.gui = DtMoveSideByArea_Dialog(self.iface.mainWindow(), flags)
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
        if(layer.dataProvider().geometryType() == 6):
            self.multipolygon_detected = True
        title = QtCore.QCoreApplication.translate("digitizingtools", "Move polygon side by area")

        if layer.selectedFeatureCount() == 0:
            QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please select one polygon to edit."))
        elif layer.selectedFeatureCount() > 1:
	    QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please select only one polygon to edit."))
        else:
            #One selected feature
            self.selected_feature = layer.selectedFeatures()[0]
            self.enableSegmentTool()
            self.showDialog()
            self.gui.writeArea(self.selected_feature.geometry().area())

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
        new_a = -1.0
        try:
            new_a = float(self.gui.targetArea.text())
        except:
            pass

        if (new_a == -1.0):
            QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Target Area not valid."))
            return

        if self.p1 == None or self.p2 == None:
            QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Polygon side not selected."))
        else:
            touch_p1_p2 = self.selected_feature.geometry().touches(QgsGeometry.fromPolyline([self.p1, self.p2]))
            if (not touch_p1_p2):
                QMessageBox.information(None, QCoreApplication.translate("digitizingtools", "Cancel"), QCoreApplication.translate("digitizingtools", "Selected segment should be on the selected polygon."))
            else:
                #Select tool to create new geometry here
                if self.gui.method == "fixed":
                    new_geom = moveFixed(self.selected_feature.geometry(), self.p1, self.p2, new_a, self.multipolygon_detected)
                else:
                    new_geom = moveVariable(self.selected_feature.geometry(), self.p1, self.p2, new_a, self.multipolygon_detected)

                #Store new geometry on the memory buffer
                fid = self.selected_feature.id()
                layer = self.iface.activeLayer()
                layer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Move Side By Area"))
                layer.changeGeometry(fid,new_geom)
                self.canvas.refresh()
                layer.endEditCommand()

def moveFixed(geom, p1, p2, new_area, multipolygon):

    pointList = []
    if(multipolygon):
        pointList = geom.asMultiPolygon()[0][0][0:-1]
    else:
        pointList = geom.asPolygon()[0][0:-1]
    #Read input polygon geometry as a list of QgsPoints

    mul = 1.0
    ind = 0
    p1_indx = -1
    p2_indx = -1

    #find p1 and p2 in the list
    for tmp_point in pointList:
        if (tmp_point == p1):
            p1_indx = ind
        elif (tmp_point == p2):
            p2_indx = ind
        ind += 1

    #Calculate the extra area needed
    area_init = geom.area()
    area_diff = new_area - area_init
    if(area_diff > 0):
        growing = True
    else:
        growing = False

    #Find the distance between p1 and p2
    dist_p1p2 = math.sqrt(p1.sqrDist(p2))

    #Find the initiallizer distance to parallel move
    test_dist1 = area_diff / dist_p1p2
    test_dist2 = (-1.0)*test_dist1
    test_geom1 = getParallelGeomByDistance(geom, p1, p2, p1_indx, p2_indx, test_dist1, multipolygon)
    test_area1 = test_geom1.area()
    test_geom2 = getParallelGeomByDistance(geom, p1, p2, p1_indx, p2_indx, test_dist2, multipolygon)
    test_area2 = test_geom2.area()

    if growing:
        if (test_area1 > test_area2):
            dist_end = 2.0 * test_dist1
            dist_start = 0.0
        else:
            dist_end = 2.0 * test_dist2
            dist_start = 0.0
    else:
        if (test_area1 > test_area2):
            dist_start = 2.0 * test_dist2
            dist_end = 0.0
        else:
            dist_start = 2.0 * test_dist1
            dist_end = 0.0

    EPSILON = 1e-7
    dist_mid = dist_start + (dist_end - dist_start)/2.0

    for i in range(1000):
        dist_mid = dist_start + (dist_end - dist_start)/2.0
        geom_mid = getParallelGeomByDistance(geom, p1, p2, p1_indx, p2_indx, dist_mid, multipolygon)
        area_mid = geom_mid.area()
        if ((math.fabs(area_mid-new_area)) < EPSILON):
            print "wanted area reached"
            print area_mid
            break
        elif (area_mid < new_area):
            dist_start = dist_mid
        else:
            dist_end = dist_mid

    return geom_mid

def getParallelGeomByDistance(geom, p1, p2, p1_indx, p2_indx, dist, multipolygon):

    pointList = []
    if(multipolygon):
        pointList = geom.asMultiPolygon()[0][0][0:-1]
    else:
        pointList = geom.asPolygon()[0][0:-1]
    #Read input polygon geometry as a list of QgsPoints

    (p3, p4) = getParallelLinePointsByDistance(p1, p2, dist)
    pointList[p1_indx] = p3
    pointList[p2_indx] = p4
    new_geom = QgsGeometry.fromPolygon( [ pointList ] )
    return new_geom


def getParallelLinePointsByDistance(p1, p2, dist):
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

def moveVariable(geom, p1, p2, new_area, multipolygon):

    #Read input polygon geometry as a list of QgsPoints
    pointList = []
    if(multipolygon):
        pointList = geom.asMultiPolygon()[0][0][0:-1]
    else:
        pointList = geom.asPolygon()[0][0:-1]

    #indices
    ind = 0
    ind_max = len(pointList)-1
    p1_indx = -1
    p2_indx = -1
    p3_indx = -1
    p4_indx = -1

    #find p1 and p2 in the list
    for tmp_point in pointList:
        if (tmp_point == p1):
            p1_indx = ind
        elif (tmp_point == p2):
            p2_indx = ind
        ind += 1

    #locate p3,p4 index based on positioning of p1 and p2
    if(p2_indx > p1_indx):
        if(p2_indx < ind_max):
            p3_indx = p1_indx - 1
            p4_indx = p2_indx + 1
        elif(p2_indx == ind_max and p1_indx == 0):
            p4_indx = p2_indx - 1
            p3_indx = p1_indx + 1
        elif(p2_indx == ind_max and p1_indx != 0):
            p3_indx = p1_indx - 1
            p4_indx = 0
    elif(p1_indx > p2_indx):
        if(p2_indx > 0):
            p4_indx = p2_indx - 1
            p3_indx = p1_indx + 1
        elif(p2_indx == 0 and p1_indx == ind_max):
            p4_indx = p2_indx + 1
            p3_indx = p1_indx - 1
        elif(p2_indx == 0 and p1_indx != ind_max):
            p4_indx = ind_max
            p3_indx = p1_indx + 1

    x2 = p1.x()
    y2 = p1.y()
    x4 = p2.x()
    y4 = p2.y()
    x1 = pointList[p3_indx].x()
    y1 = pointList[p3_indx].y()
    x3 = pointList[p4_indx].x()
    y3 = pointList[p4_indx].y()
    old_area = geom.area()
    area_diff = new_area-old_area

    (x5,y5,x6,y6) = move_vertex_trapezoid(x1,y1,x2,y2,x3,y3,x4,y4,area_diff)

    p5 = QgsPoint(x5,y5)
    p6 = QgsPoint(x6,y6)
    pointList[p1_indx] = p5
    pointList[p2_indx] = p6

    new_geom = QgsGeometry.fromPolygon( [ pointList ] )

    return new_geom

def move_vertex_trapezoid(x1,y1,x2,y2,x3,y3,x4,y4,area):
    """
    This function moves vertex 2-4 parallel by forming a trapezoid of
    area resulting a new 5-6 vertex. Result is returned as [x5,y5,x6,y6].

    * copyright            : (C) 2013 by Christos Iossifidis
    * email                : chiossif@yahoo.com
    """
    EPSILON=1e-9 #This is approximation accuracy
    AWAY_STEP=1000.0 #This is the beyond step factor. It is too big already ;-)
    k1=(y2-y1)/(x2-x1) #(I)
    k2=(y4-y3)/(x4-x3) #(II)
    k3=(y4-y2)/(x4-x2) #(III)

    #k3=(y6-y5)/(x6-x5) ===>
    #x6 = x5 + (y6-y5)/k3 (IVa)
    #y6 = y5 + k3*(x6-x5) (IVb)

    #k1=(y5-y2)/(x5-x2) ===>
    #x5 = x2 + (y5-y2)/k1 (Va)
    #y5 = y2 + k1*(x5-x2) (Vb)

    #k2=(y6-y4)/(x6-x4) ===>
    #x6 = x4 + (y6-y4)/k1 (VIa)
    #y6 = y4 + k2*(x6-x4) (VIb)

    #2*area=ABS( x5*(y2-y4)+x2*(y4-y5)+x4*(y5-y2) ) + ABS ( x5*(y4-y6)+x4*(y6-y5)+x6*(y5-y4) )  (VII)

    #(VIb)==(IVa)==>
    #y6 = y4 + k2*( x5 + (y6-y5)/k3 - x4)===>
    #y6 = y4 + k2*x5 + k2*y6/k3 - k2*y5/k3 -k2*x4 ===>
    #y6 - k2/k3*y6 = y4 + k2*x5 - k2*y5/k3 -k2*x4 ===>
    #y6 = (y4 + k2*x5 - k2*y5/k3 -k2*x4) / (1.0 - k2/k3) (VIII)

    if (area<0.0):
        area=abs(area)
        start=x1 #starting values
        stop=x2

        for i in range(100):
            x5=(start+stop)/2.0
            #(Vb)===>
            y5= y2 + k1*(x5-x2)
            #(VIII)===>
            y6 = (y4 + k2*x5 - k2*y5/k3 -k2*x4) / (1.0 - k2/k3)
            #(VIa)===>
            x6 = x4 + (y6-y4)/k2

            #(VII)===>
            new_area=(abs( x5*(y2-y4)+x2*(y4-y5)+x4*(y5-y2) ) + abs( x5*(y4-y6)+x4*(y6-y5)+x6*(y5-y4) ))/2.0

            if (abs(area-new_area)<EPSILON):
                break
            elif (area > new_area):
                stop=x5
            else:
                start=x5
    else:
        area=abs(area)
        start=x2 #starting values
        stop=x2 + AWAY_STEP*(x2-x1) #AWAY_STEP times the 2-1 distance plus x2

        for i in range(100):
            x5=(start+stop)/2.0
            #(Vb)===>
            y5= y2 + k1*(x5-x2)
            #(VIII)===>
            y6 = (y4 + k2*x5 - k2*y5/k3 -k2*x4) / (1.0 - k2/k3)
            #(VIa)===>
            x6 = x4 + (y6-y4)/k2

            #(VII)===>
            new_area=(abs( x5*(y2-y4)+x2*(y4-y5)+x4*(y5-y2) ) + abs( x5*(y4-y6)+x4*(y6-y5)+x6*(y5-y4) ))/2.0

            if (abs(area-new_area)<EPSILON):
                break
            elif area<new_area:
                stop=x5
            else:
                start=x5

    return (x5,y5,x6,y6)

