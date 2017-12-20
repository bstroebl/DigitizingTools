# -*- coding: utf-8 -*-
"""
dtdigitizemedianline
````````````````````
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

from builtins import range
from builtins import object
from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis.core import *
from qgis.gui import *
from dtmedianlinetool import DtMedianLineTool


class DtMedianLine(object):
    '''Digitize median line by selecting vertices on adjacent polygons'''

    def __init__(self, iface, toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        #self.lineLayer = None
        self.selected_points = 0
        self.side1_x = []
        self.side1_y = []
        self.side2_x = []
        self.side2_y = []
        self.point_list = []

        #create action
        self.median_digitizer = QtWidgets.QAction(QtGui.QIcon(":/medianLine.png"),
            QtCore.QCoreApplication.translate("digitizingtools",
                "Digitize median line between adjacent polygons"),
                self.iface.mainWindow())

        self.median_digitizer.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.median_digitizer)
        self.enable()
        self.tool = DtMedianLineTool(self)
        self.tool.finishedDigitizing.connect(self.digitizingFinished)

    def reset(self):
        self.selected_points = 0
        del self.side1_x[:]
        del self.side1_y[:]
        del self.side2_x[:]
        del self.side2_y[:]
        del self.point_list[:]

    def enableTool(self):
        self.tool.activate()
        self.canvas.setMapTool(self.tool)
        #Connect to the DtSelectVertexTool
        self.tool.vertexFound.connect(self.storePoints)

    def disableTool(self):
        self.reset()
        #self.tool.deactivate()
        self.canvas.unsetMapTool(self.tool)
        self.tool.vertexFound.disconnect(self.storePoints)
        self.tool.deactivate()

    def deactivate(self):
        self.disableTool()
        self.median_digitizer.setChecked(False)

    def run(self):
        '''Function that does all the real work'''
        self.reset()
        layer = self.iface.activeLayer()
        title = QtCore.QCoreApplication.translate("digitizingtools",
            "Digitize median line")

        if layer.selectedFeatureCount() == 0:
            self.enableTool()
            #self.lineLayer = layer
            self.median_digitizer.setChecked(True)
        else:
            QtGui.QMessageBox.information(None, title,
                QtCore.QCoreApplication.translate("digitizingtools",
                "Please clear selection."))

    def storePoints(self, result):
        tmp_x = result[0].x()
        tmp_y = result[0].y()
        modulo = self.selected_points % 2
        if (modulo == 0):                              # Select first vertex
            if ((tmp_x in self.side1_x) and (tmp_y in self.side1_y)):
                #print "Point (%f,%f) already in list1" % (tmp_x, tmp_y)
                self.selected_points = self.selected_points + 1
                return
            else:
                #print "Point (%f,%f) added in list1" % (tmp_x, tmp_y)
                self.side1_x.append(tmp_x)
                self.side1_y.append(tmp_y)
                self.selected_points = self.selected_points + 1
                return
        else:                                         # Select second vertex
            if ((tmp_x in self.side2_x) and (tmp_y in self.side2_y)):
                #print "Point (%f,%f) already in list2" % (tmp_x, tmp_y)
                self.selected_points = self.selected_points + 1
                return
            else:
                #print "Point (%f,%f) added in list2" % (tmp_x, tmp_y)
                self.side2_x.append(tmp_x)
                self.side2_y.append(tmp_y)
                self.selected_points = self.selected_points + 1
                return

    def digitizingFinished(self):
        #print "side1_x"
        #print self.side1_x
        #print "side1_y"
        #print self.side1_y
        #print "side2_x"
        #print self.side2_x
        #print "side2_y"
        #print self.side2_y
        (x, y) = median_polyline(self.side1_x, self.side1_y, self.side2_x,
            self.side2_y)
        #print "x"
        #print x
        #print "y"
        #print y
        for i in range(len(x)):
            p = QgsPoint(x[i], y[i])
            #print "current p is:"
            #print p
            self.point_list.append(p)
        # Debug
        #print "Point list:"
        #print self.point_list
        new_geom = QgsGeometry.fromPolyline(self.point_list)
        addGeometryToCadLayer(new_geom)
        self.canvas.refresh()
        self.reset()
        self.deactivate()

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.reset()
        self.median_digitizer.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer is not None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for polygon layers
                if layer.geometryType() == 2:
                    # enable if editable
                    self.median_digitizer.setEnabled(layer.isEditable())
                    try:
                        layer.editingStarted.disconnect(self.enable)
                        # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable)
                        # when it becomes active layer again
                    except:
                        pass
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)


def getCadLayerByName(cadname):
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in list(layermap.items()):
        if layer.name() == cadname:
            if layer.isValid():
                return layer
            else:
                return None


def addGeometryToCadLayer(g):
    pointName = "CadLayer Points"
    lineName = "CadLayer Lines"
    polygonName = "CadLayer Polygons"

    geom_type = g.type()

    # Points
    if geom_type == 0:
        theName = pointName
        theType = "Point"
    elif geom_type == 1:
        theName = lineName
        theType = "LineString"
    elif geom_type == 2:
        theName = polygonName
        theType = "Polygon"
    else:
        return

    if getCadLayerByName(theName) is None:
        vl = QgsVectorLayer(theType, theName, "memory")
        pr = vl.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(g)
        pr.addFeatures([feat])
        vl.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayer(vl, True)
    else:
        layer = getCadLayerByName(theName)
        pr = layer.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(g)
        pr.addFeatures([feat])
        layer.updateExtents()


def median_polyline(xa, ya, xb, yb):
    """
    This function returns the median polyline of two polylines
    """
    def S(x1, y1, x2, y2):
        return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)
    x = []
    y = []

    m = len(xa)
    if m != len(ya):
        return [], []
    n = len(xb)
    if n != len(yb):
        return [], []
    i = j = k = 0
    while (i < m - 1 and j < n - 1):
        x.append((xa[i] + xb[j]) / 2.0)
        y.append((ya[i] + yb[j]) / 2.0)
        k += 1
        if S(xa[i + 1], ya[i + 1], xb[j], yb[j]) < S(xa[i], ya[i], xb[j + 1],
            yb[j + 1]):
            i += 1
        else:
            j += 1

    if i < m - 1:
        j -= 1
        while i < m:
            i += 1
            if i >= m:
                break
            x.append((xa[i] + xb[j]) / 2.0)
            y.append((ya[i] + yb[j]) / 2.0)
            k += 1

    if j < n - 1:
        i -= 1
        while j < n:
            j += 1
            if j >= n:
                break
            x.append((xa[i] + xb[j]) / 2.0)
            y.append((ya[i] + yb[j]) / 2.0)
            k += 1
    x.append((xa[m - 1] + xb[n - 1]) / 2.0)
    y.append((ya[m - 1] + yb[n - 1]) / 2.0)
    return x, y
