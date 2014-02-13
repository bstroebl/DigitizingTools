# -*- coding: utf-8 -*-
"""
digitizemedianlinetool
``````````````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

 This vertex selection tool is adopted/adapted from:
 'CadTools Plugin', Copyright (C) Stefan Ziegler

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


class DtMedianLineTool(QgsMapTool):
    finishedDigitizing = QtCore.pyqtSignal()

    def __init__(self, parent):
        QgsMapTool.__init__(self, parent.canvas)
        self.canvas = parent.canvas
        self.parent = parent
        self.markers = []
        #custom cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
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

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        if event.button() == QtCore.Qt.RightButton:
            self.finishedDigitizing.emit()
            return

        layer = self.canvas.currentLayer()

        if layer is not None:
            #the clicked point is our starting point
            startingPoint = QPoint(x, y)

            #we need a snapper, so we use the MapCanvas snapper
            snapper = QgsMapCanvasSnapper(self.canvas)

            #we snap to the current layer (we don't have exclude points and use
            #the tolerances from the qgis properties)
            (retval, result) = snapper.snapToCurrentLayer(startingPoint,
                QgsSnapper.SnapToVertex)

            #if we don't have found a linesegment we try to find one on the
            #backgroundlayer
            if result == []:
                #(retval, result) = snapper.snapToBackgroundLayers(
                #    startingPoint)
                pass

            #if we have found a vertex
            if result != []:
                # we like to mark the vertex that is choosen
                p = QgsPoint()
                p.setX(result[0].snappedVertex.x())
                p.setY(result[0].snappedVertex.y())
                m = QgsVertexMarker(self.canvas)
                m.setIconType(1)
                modulo = self.parent.selected_points % 2
                if modulo == 0:
                    m.setColor(QtGui.QColor(255, 0, 0))
                else:
                    m.setColor(QtGui.QColor(0, 0, 255))
                m.setIconSize(12)
                m.setPenWidth(3)
                m.setCenter(p)
                self.markers.append(m)
                self.emit(SIGNAL("vertexFound(PyQt_PyObject)"), [p])
            else:
                pass

    def showSettingsWarning(self):
        m = QgsMessageViewer()
        m.setWindowTitle("Snap tolerance")
        m.setCheckBoxText("Don't show this message again")
        m.setCheckBoxVisible(True)
        m.setCheckBoxQSettingsLabel(settingsLabel)
        m.setMessageAsHtml("<p>Could not snap segment.</p><p>Have you set "
          "the tolerance in Settings > Project Properties > General?</p>")
        m.showMessage()

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        for m in self.markers:
            self.canvas.scene().removeItem(m)
        del self.markers[:]

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
