# -*- coding: utf-8 -*-
"""
dtmovenodebyarea
````````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-08-14
* copyright            : (C) 2013 by Angelos Tzotsos
* email                : tzotsos@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import object
from qgis.PyQt import QtCore,  QtGui, QtWidgets
from qgis.core import *

import dt_icons_rc
from dttools import DtSelectVertexTool
from dtmovenodebyarea_dialog import DtMoveNodeByArea_Dialog

class DtMoveNodeByArea(object):
    '''Automatically move polygon node (along a given side of polygon) in order to achieve a desired polygon area'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.gui = None
        self.multipolygon_detected = False

        # Points and Markers
        self.p1 = None
        self.p2 = None
        self.m1 = None
        self.m2 = None
        self.selected_feature = None

        #create action
        self.node_mover = QtWidgets.QAction(QtGui.QIcon(":/MovePolygonNodeByArea.png"),
            QtWidgets.QApplication.translate("digitizingtools", "Move polygon node (along a side) to achieve target area"),  self.iface.mainWindow())

        self.node_mover.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.node_mover)
        self.enable()

        self.tool = DtSelectVertexTool(self.iface, 2)

    def showDialog(self):
        flags = QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        self.gui = DtMoveNodeByArea_Dialog(self.iface.mainWindow(),  flags)
        self.gui.initGui()
        self.gui.show()
        self.gui.unsetTool.connect(self.unsetTool)
        self.gui.moveNode.connect(self.moveNode)

    def enableVertexTool(self):
        self.canvas.setMapTool(self.tool)
        #Connect to the DtSelectVertexTool
        self.tool.vertexFound.connect(self.storeVertexPointsAndMarkers)

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
        if(layer.dataProvider().wkbType() == 6):
            self.multipolygon_detected = True
        title = QtWidgets.QApplication.translate("digitizingtools", "Move polygon node by area")

        if layer.selectedFeatureCount() == 0:
            QtWidgets.QMessageBox.information(None, title,  QtWidgets.QApplication.translate("digitizingtools", "Please select one polygon to edit."))
        elif layer.selectedFeatureCount() > 1:
            QtWidgets.QMessageBox.information(None, title,  QtWidgets.QApplication.translate("digitizingtools", "Please select only one polygon to edit."))
        else:
            #One selected feature
            self.selected_feature = layer.selectedFeatures()[0]
            self.enableVertexTool()
            self.showDialog()
            self.gui.writeArea(self.selected_feature.geometry().area())


    def storeVertexPointsAndMarkers(self,  result):
        self.p1 = result[0][0]
        self.p2 = result[0][1]
        self.m1 = result[1][0]
        self.m2 = result[1][1]

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.node_mover.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer != None:
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
            QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("digitizingtools", "Cancel"), QtWidgets.QApplication.translate("digitizingtools", "Target Area not valid."))
            return

        if self.p1 == None or self.p2 == None:
            QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("digitizingtools", "Cancel"), QtWidgets.QApplication.translate("digitizingtools", "Not enough vertices selected."))
        else:
            interp1 = self.selected_feature.geometry().intersects(QgsGeometry.fromPointXY(self.p1))
            interp2 = self.selected_feature.geometry().intersects(QgsGeometry.fromPointXY(self.p2))
            touch_p1_p2 = self.selected_feature.geometry().touches(QgsGeometry.fromPolyline([QgsPoint(self.p1), QgsPoint(self.p2)]))
            if (interp1 and interp2):
                if (not touch_p1_p2):
                    QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("digitizingtools", "Cancel"), QtWidgets.QApplication.translate("digitizingtools", "Selected vertices should be consecutive on the selected polygon."))
                else:
                    new_geom = createNewGeometry(self.selected_feature.geometry(), self.p1, self.p2, new_a, self.multipolygon_detected)
                    fid = self.selected_feature.id()
                    layer = self.iface.activeLayer()
                    layer.beginEditCommand(QtWidgets.QApplication.translate("editcommand", "Move Node By Area"))
                    layer.changeGeometry(fid,new_geom)
                    self.canvas.refresh()
                    layer.endEditCommand()
                    #wkt_tmp1 = self.selected_feature.geometry().exportToWkt()
                    #wkt_tmp2 = new_geom.exportToWkt()
                    #tmp_str = wkt_tmp1 + " Initial Area:" + str(self.selected_feature.geometry().area()) + " " + wkt_tmp2 + " Final Area:" + str(new_geom.area())
                    #title = QtWidgets.QApplication.translate("digitizingtools", "Move polygon node by area")
                    #QtGui.QMessageBox.information(None, title,  QtWidgets.QApplication.translate("digitizingtools", tmp_str))
            else:
                QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("digitizingtools", "Cancel"), QtWidgets.QApplication.translate("digitizingtools", "Vertices not on the selected polygon."))

# p1 is the stable node (red) and p2 is the node to move (blue)
def createNewGeometry(geom, p1, p2, new_area, multipolygon):
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

    #find p1 and p2 in the list
    for tmp_point in pointList:
        if (tmp_point == p1):
            p1_indx = ind
        elif (tmp_point == p2):
            p2_indx = ind
        ind += 1

    #locate p3 index based on positioning of p1 and p2
    if(p2_indx > p1_indx):
        if(p2_indx < ind_max):
            p3_indx = p2_indx + 1
        elif(p2_indx == ind_max and p1_indx == 0):
            p3_indx = p2_indx - 1
        elif(p2_indx == ind_max and p1_indx != 0):
            p3_indx = 0
    elif(p1_indx > p2_indx):
        if(p2_indx > 0):
            p3_indx = p2_indx - 1
        elif(p2_indx == 0 and p1_indx == ind_max):
            p3_indx = p2_indx + 1
        elif(p2_indx == 0 and p1_indx != ind_max):
            p3_indx = ind_max

    x1 = p1.x()
    y1 = p1.y()
    x2 = p2.x()
    y2 = p2.y()
    x3 = pointList[p3_indx].x()
    y3 = pointList[p3_indx].y()
    old_area = geom.area()
    area_diff = new_area-old_area

    (x2a,y2a, x2b,y2b)=move_vertex(x1,y1,x2,y2,x3,y3,area_diff)

    p2a = QgsPointXY(x2a,y2a)
    p2b = QgsPointXY(x2b,y2b)

    pointList[p2_indx] = p2a
    geom1 = QgsGeometry.fromPolygonXY( [ pointList ] )

    pointList[p2_indx] = p2b
    geom2 = QgsGeometry.fromPolygonXY( [ pointList ] )

    diff_geom1 = abs(geom1.area() - new_area)
    diff_geom2 = abs(geom2.area() - new_area)

    if(diff_geom1 < diff_geom2):
        return geom1
    else:
        return geom2

def move_vertex(x1,y1,x2,y2,x3,y3,area):
    """
    This function moves point 2 of 1-2 vertex on 2-3 direction resulting
    a new 1-4 vertex. Area is the desired area of the triangle 1-2-4.
    Result is returned as [ xa ya xb yb ] due to absolute value.
    Use resulted area of new polygon is the final criterion.

    * copyright            : (C) 2013 by Christos Iossifidis
    * email                : chiossif@yahoo.com
    """
    k=(y3-y2)/(x3-x2) #(I)

    #k=(y4-y2)/(x4-x2) ===>
    #x4 = x2 + (y4-y2)/k (IIa)
    #y4 = y2 + k*(x4-x2) (IIb)

    #2*area=ABS(x1*(y2-y4)+x2*(y4-y1)+x4*(y1-y2)) (III)

    #(III) ==(IIa)==>
    #2*area=ABS( x1*(y2-y4)+x2*(y4-y1)+(x2+(y4-y2)/k)*(y1-y2) ) ===>
    #2*area=ABS( x1*(y2-y4)+x2*(y4-y1)+ x2*(y1-y2) + (y4-y2)*(y1-y2)/k ) ===>
    #2*area=ABS( x1*y2 -x1*y4 +x2*y4 -x2*y1+ x2*y1-x2*y2 +y4*y1/k -y4*y2/k -y2*y1/k +y2*y2/k ) ===>
    #2*area=ABS( x1*y2 -x2*y1+ x2*y1-x2*y2 -y2*y1/k +y2*y2/k ) ===>
    #x1*y4 -x2*y4 -y4*y1/k +y4*y2/k = +-2*area + ( x1*y2 -x2*y1+ x2*y1-x2*y2 -y2*y1/k +y2*y2/k ) ===>
    #y4 = (+-2*area + ( x1*y2 -x2*y1+ x2*y1-x2*y2 -y2*y1/k +y2*y2/k ) ) / ( x1-x2-y1/k+y2/k ) (IV)

    #(IV)===>
    y4a = ( 2.0*area + ( x1*y2 -x2*y1+ x2*y1-x2*y2 -y2*y1/k +y2*y2/k ) ) / ( x1-x2-y1/k+y2/k )
    #(IIa) ===>
    x4a = x2 + (y4a-y2)/k

    #(IV)===>
    y4b = ( -2.0*area + ( x1*y2 -x2*y1+ x2*y1-x2*y2 -y2*y1/k +y2*y2/k ) ) / ( x1-x2-y1/k+y2/k )
    #(IIa) ===>
    x4b = x2 + (y4b-y2)/k

    return (x4a,y4a, x4b,y4b)

