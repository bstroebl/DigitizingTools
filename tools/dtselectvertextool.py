# -*- coding: utf-8 -*-
"""
selectevertextool
`````````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

 This vertex selection tool is adopted/adapted from:
 'CadTools Plugin', Copyright (C) Stefan Ziegler

* begin                : 2013-08-11
* copyright            : (C) 2013 by Angelos Tzotsos
* revision             : Bernhard Ströbl (2013-08-25)
* email                : tzotsos@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from PyQt4 import QtCore,  QtGui
from qgis.core import *
from qgis.gui import *

# Vertex Select Tool class
class DtSelectVertexTool(QgsMapTool):
    '''select and mark numVertices vertices in the active layer'''
    vertexFound = QtCore.pyqtSignal(list)

    def __init__(self, canvas,  numVertices = 1):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        # desired number of marked vertex until signal
        self.numVertices = numVertices
        # number of marked vertex
        self.count = 0
        # arrays to hold markers and vertex points
        self.markers = []
        self.points = []
        self.fids = []
        #custom cursor
        self.cursor = QtGui.QCursor(QtGui.QPixmap(["16 16 3 1",
                                        "      c None",
                                        ".     c #FF0000",
                                        "+     c #FFFFFF",
                                        "                ",
                                        "       +.+      ",
                                        "      ++.++     ",
                                        "     +.....+    ",
                                        "    +.     .+   ",
                                        "   +.   .   .+  ",
                                        "  +.    .    .+ ",
                                        " ++.    .    .++",
                                        " ... ...+... ...",
                                        " ++.    .    .++",
                                        "  +.    .    .+ ",
                                        "   +.   .   .+  ",
                                        "   ++.     .+   ",
                                        "    ++.....+    ",
                                        "      ++.++     ",
                                        "       +.+      "]))

    def canvasPressEvent(self,event):
        pass

    def canvasMoveEvent(self,event):
        pass

    def canvasReleaseEvent(self,event):
        if self.count < self.numVertices: #not yet enough
            #Get the click
            x = event.pos().x()
            y = event.pos().y()

            layer = self.canvas.currentLayer()

            if layer <> None:
                #the clicked point is our starting point
                startingPoint = QtCore.QPoint(x,y)

                #we need a snapper, so we use the MapCanvas snapper
                snapper = QgsMapCanvasSnapper(self.canvas)

                #we snap to the current layer (we don't have exclude points and use the tolerances from the qgis properties)
                (retval,result) = snapper.snapToCurrentLayer (startingPoint,QgsSnapper.SnapToVertex)

                if result == []:
                    #warn about missing snapping tolerance if appropriate
                    #self.showSettingsWarning()
                    pass

                if result <> []:
                    #mark the vertex
                    p = QgsPoint()
                    p.setX( result[0].snappedVertex.x() )
                    p.setY( result[0].snappedVertex.y() )
                    m = QgsVertexMarker(self.canvas)
                    m.setIconType(1)

                    if self.count == 0:
                        m.setColor(QtGui.QColor(255,0,0))
                    else:
                        m.setColor(QtGui.QColor(0, 0, 255))

                    m.setIconSize(12)
                    m.setPenWidth (3)
                    m.setCenter(p)
                    self.points.append(p)
                    self.markers.append(m)
                    fid = result[0].snappedAtGeometry # QgsFeatureId of the snapped geometry
                    self.fids.append(fid)
                    self.count += 1

                    if self.count == self.numVertices:
                        self.vertexFound.emit([self.points,  self.markers,  self.fids])
                        #self.emit(SIGNAL("vertexFound(PyQt_PyObject)"), [self.points,  self.markers])

    def showSettingsWarning(self):
        m = QgsMessageViewer()
        m.setWindowTitle("Snap tolerance")
        m.setCheckBoxText("Don't show this message again")
        m.setCheckBoxVisible(True)
        m.setCheckBoxQSettingsLabel(settingsLabel)
        m.setMessageAsHtml( "<p>Could not snap vertex.</p><p>Have you set the tolerance in Settings > Project Properties > General?</p>")
        m.showMessage()

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        #self.canvas.setCursor(QtCore.Qt.ArrowCursor)
        self.clear()

    def clear(self):
        for m in self.markers:
            self.canvas.scene().removeItem(m)

        self.markers = []
        self.points = []
        self.fids = []
        self.count = 0

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
