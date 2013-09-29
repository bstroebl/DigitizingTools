# -*- coding: utf-8 -*-
"""
dtdigitizeroad
``````````````
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
from qgis.gui import *
import math
import icons_rc
from dtdigitizeroadtool import DtDigitizeRoadTool

class DtDigitizeRoad():
    '''Digitize road line by selecting block segments on both road sides'''

    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        #self.lineLayer = None
        self.selected_segments = 0
        self.s1a_x = 0.0
        self.s1a_y = 0.0
        self.s1b_x = 0.0
        self.s1b_y = 0.0
        self.s2a_x = 0.0
        self.s2a_y = 0.0
        self.s2b_x = 0.0
        self.s2b_y = 0.0
        self.pp1_x = 0.0
        self.pp1_y = 0.0
        self.pp2_x = 0.0
        self.pp2_y = 0.0
        # points of the selected segment
        # p1 is always the left point
        self.s1a = QgsPoint(0.0, 0.0)
        self.s1b = QgsPoint(0.0, 0.0)
        self.s2a = QgsPoint(0.0, 0.0)
        self.s2b = QgsPoint(0.0, 0.0)
        #self.pp1 = QgsPoint(0.0, 0.0)
        #self.pp2 = QgsPoint(0.0, 0.0)
        self.point_list = []
        self.rb1 = QgsRubberBand(self.canvas,  False)

        #create action
        self.road_digitizer = QtGui.QAction(QtGui.QIcon(":/digitizeRoads.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Digitize road by selecting block segments"), self.iface.mainWindow())

        self.road_digitizer.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.road_digitizer)
        self.enable()
        self.tool = DtDigitizeRoadTool(self.canvas)

    def reset(self):
        #self.lineLayer = None
        self.selected_segments = 0
        self.s1a_x = 0.0
        self.s1a_y = 0.0
        self.s1b_x = 0.0
        self.s1b_y = 0.0
        self.s2a_x = 0.0
        self.s2a_y = 0.0
        self.s2b_x = 0.0
        self.s2b_y = 0.0
        self.pp1_x = 0.0
        self.pp1_y = 0.0
        self.pp2_x = 0.0
        self.pp2_y = 0.0
        del self.point_list[:]
        #self.point_list = []

    def enableTool(self):
        self.canvas.setMapTool(self.tool)
        #Connect to the DtSelectVertexTool
        QObject.connect(self.tool, SIGNAL("segmentFound(PyQt_PyObject)"), self.storeSegmentPoints)
        self.tool.finishedDigitizing.connect(self.digitizingFinished)

    def disableTool(self):
        self.reset()
        self.canvas.unsetMapTool(self.tool)

    def deactivate(self):
        self.disableTool()
        self.road_digitizer.setChecked(False)

    def run(self):
        '''Function that does all the real work'''
        layer = self.iface.activeLayer()
        title = QtCore.QCoreApplication.translate("digitizingtools", "Digitize road")

        if layer.selectedFeatureCount() == 0:
            self.enableTool()
            #self.lineLayer = layer
            self.road_digitizer.setChecked(True)
        else:
            QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please clear selection."))

    def storeSegmentPoints(self,  result):
        modulo = self.selected_segments % 2
        if (modulo == 0): # Select first segment
            if result[0].x() < result[1].x():
                self.s1a = result[0]
                self.s1b = result[1]
            elif result[0].x() == result[1].x():
                self.s1a = result[0]
                self.s1b = result[1]
            else:
                self.s1a = result[1]
                self.s1b = result[0]
            self.selected_segments = self.selected_segments + 1
            self.s1a_x = self.s1a.x()
            self.s1a_y = self.s1a.y()
            self.s1b_x = self.s1b.x()
            self.s1b_y = self.s1b.y()
            # Dubugging mode
            print self.selected_segments
            print "First point in side 1 (%f,%f)" % (self.s1a.x(),self.s1a.y())
            print "Second point in side 1 (%f,%f)" % (self.s1b.x(),self.s1b.y())
        else: # Select second segment
            if result[0].x() < result[1].x():
                self.s2a = result[0]
                self.s2b = result[1]
            elif result[0].x() == result[1].x():
                self.s2a = result[0]
                self.s2b = result[1]
            else:
                self.s2a = result[1]
                self.s2b = result[0]

            self.selected_segments = self.selected_segments + 1
            self.s2a_x = self.s2a.x()
            self.s2a_y = self.s2a.y()
            self.s2b_x = self.s2b.x()
            self.s2b_y = self.s2b.y()
            # Dubugging mode
            print self.selected_segments
            print "First point in side 2 (%f,%f)" % (self.s2a.x(),self.s2a.y())
            print "Second point in side 2 (%f,%f)" % (self.s2b.x(),self.s2b.y())
            # Now we have to calculate the road segment and add it to list of points...
            if (self.selected_segments == 2):
                self.create_first_line()
            else:
                self.create_next_line()

    def create_first_line(self):
        (x1,y1,x2,y2)=median_vertex(self.s1a_x,self.s1a_y,self.s1b_x,self.s1b_y,self.s2a_x,self.s2a_y,self.s2b_x,self.s2b_y)
        self.pp1_x = x1
        self.pp1_y = y1
        self.pp2_x = x2
        self.pp2_y = y2

    def create_next_line(self):
        (x3,y3,x4,y4)=median_vertex(self.s1a_x,self.s1a_y,self.s1b_x,self.s1b_y,self.s2a_x,self.s2a_y,self.s2b_x,self.s2b_y)
        (x1,y1,x5,y5,x4,y4)=twovertices_to_polyline(self.pp1_x,self.pp1_y,self.pp2_x,self.pp2_y,x3,y3,x4,y4)
        tmp_x1=0.0
        tmp_y1=0.0
        if abs(x1-x5)<1e-4:
            tmp_x1=self.pp2_x
            tmp_y1=self.pp2_y
        else:
            tmp_x1=self.pp1_x
            tmp_y1=self.pp1_y
        p1 = QgsPoint(tmp_x1, tmp_y1)
        self.pp1_x = x5
        self.pp1_y = y5
        self.pp2_x = x4
        self.pp2_y = y4
        self.point_list.append(p1)

    def digitizingFinished(self):
        tmp_pp1 = QgsPoint(self.pp1_x, self.pp1_y)
        self.point_list.append(tmp_pp1)
        tmp_pp2 = QgsPoint(self.pp2_x, self.pp2_y)
        self.point_list.append(tmp_pp2)
        # Debug
        print "Point list:"
        print self.point_list
        new_geom = QgsGeometry.fromPolyline( self.point_list )
        addGeometryToCadLayer(new_geom)
        self.canvas.refresh()
        #Previous implementation
        #caps = self.lineLayer.dataProvider().capabilities()
        #if caps & QgsVectorDataProvider.AddFeatures:
            #self.lineLayer.beginEditCommand(QtCore.QCoreApplication.translate("editcommand", "Digitize Road"))
            #feat = QgsFeature()
            ##feat.addAttribute(0,"hello")
            #feat.setGeometry(new_geom)
            #(res, outFeats) = self.lineLayer.dataProvider().addFeatures( [ feat ] )
            #self.lineLayer.endEditCommand()
            #self.mapCanvas.refresh()
        self.reset()

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.road_digitizer.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for polygon layers
                if layer.geometryType() == 2:
                    # enable if editable
                    self.road_digitizer.setEnabled(layer.isEditable())
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

def median_vertex(x1,y1,x2,y2,x3,y3,x4,y4):
    """
    This function calculates the best median vertex 5-6 of vetrices 1-2
    and 3-4.
    """
    # Dubugging mode
    print "into median_vertex"
    #print "x1,y1,x2,y2=(%f,%f,%f,%f)" % (x1,y1,x2,y2)
    #print "x3,y3,x4,y4=(%f,%f,%f,%f)" % (x3,y3,x4,y4)

    x5a=x1+x3
    y5a=y1+y3
    x6a=x2+x4
    y6a=y2+y4
    a=abs(x6a-x5a)+abs(y6a-y5a)

    x5b=x1+x4
    y5b=y1+y4
    x6b=x2+x3
    y6b=y2+y3
    b=abs(x6b-x5b)+abs(y6b-y5b)

    if (a>b):
        print "a x5,y5,x6,y6=(%f,%f,%f,%f)" % (x5a/2.0, y5a/2.0, x6a/2.0, y6a/2.0)
        return ( x5a/2.0, y5a/2.0, x6a/2.0, y6a/2.0)
    else:
        print "b x5,y5,x6,y6=(%f,%f,%f,%f)" % (x5b/2.0, y5b/2.0, x6b/2.0, y6b/2.0)
        return ( x5b/2.0, y5b/2.0, x6b/2.0, y6b/2.0)

def twovertices_to_polyline(x1,y1,x2,y2,x3,y3,x4,y4):
    """
    This function calculates the polyline 1-5-4 of vetrices 1-2 and 3-4.
    """
    def swap(a,b,c,d):
        x=a
        a=c
        c=x
        x=b
        b=d
        d=x
        return (a,b,c,d)

    if (x1>x2):
        (x1,y1,x2,y2)=swap(x1,y1,x2,y2)
    if (x3>x4):
        (x3,y3,x4,y4)=swap(x3,y3,x4,y4)
    if (x1-x4)<1e-4:
        (x3,y3,x4,y4)=swap(x3,y3,x4,y4)

    # Dubugging mode
    print "into twovertices_to_polyline"
    print "x1,y1,x2,y2=(%f,%f,%f,%f)" % (x1,y1,x2,y2)
    print "x3,y3,x4,y4=(%f,%f,%f,%f)" % (x3,y3,x4,y4)

    k1=(y2-y1)/(x2-x1)
    k2=(y4-y3)/(x4-x3)

    #k1=(y5-y1)/(x5-x1)===>
    #y5=y1+k1*(x5-x1) (I)

    #k2=(y5-y3)/(x5-x3)==(I)==>
    #k2*x5-k2*x3=y1+k1*x5-k1*x1-y3 ===>
    x5=(y1-k1*x1-y3+k2*x3)/(k2-k1)
    #(I)===>
    y5=y1+k1*(x5-x1)

    print "a x1,y1,x5,y5,x4,y4=(%f,%f,%f,%f,%f,%f)" % (x1,y1,x5,y5,x4,y4)
    return ( x1, y1, x5, y5, x4, y4 )

def getCadLayerByName(cadname):
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layermap.iteritems():
        if layer.name() == cadname:
            if layer.isValid():
                return layer
            else:
                return None

def addGeometryToCadLayer(g):
    pointName = "CadLayer Points"
    lineName = "CadLayer Lines"
    polygonName = "CadLayer Polygons"

    type = g.type()

    # Points
    if type == 0:
        theName = pointName
        theType = "Point"
    elif type ==1:
        theName = lineName
        theType = "LineString"
    elif type == 2:
        theName = polygonName
        theType = "Polygon"
    else:
        return

    if getCadLayerByName(theName) == None:
        vl = QgsVectorLayer(theType, theName, "memory")
        pr = vl.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(g)
        pr.addFeatures([feat])
        vl.updateExtents()
        QgsMapLayerRegistry().instance().addMapLayer(vl, True)
    else:
        layer = getCadLayerByName(theName)
        pr = layer.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(g)
        pr.addFeatures([feat])
        layer.updateExtents()


def median_vertex2(x1, y1, x2, y2, x3, y3, x4, y4):
    """
    This function calculates the best median vertex 5-6 of vetrices 1-2
    and 3-4.
    """
    d1 = (x1 - x3) ** 2 + (y1 - y3) ** 2
    d2 = (x1 - x4) ** 2 + (y1 - y4) ** 2
    if (d1 < d2):
        return ((x1+x3)/2.0, (y1+y3)/2.0, (x2+x4)/2.0, (y2+y4)/2.0)
    else:
        return ((x1+x4)/2.0, (y1+y4)/2.0, (x2+x3)/2.0, (y2+y3)/2.0)
