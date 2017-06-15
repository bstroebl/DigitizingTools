# -*- coding: utf-8 -*-
"""
dtsplitfeaturetool
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions
some code adopted/adapted from:
 'CadTools Plugin', Copyright (C) Stefan Ziegler

* begin                : 2017-06-12
* copyright          : (C) 2017 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
from PyQt4 import QtCore,  QtGui
from qgis.core import *
from qgis.gui import *
import dtutils
from dttools import DtMapTool

class DtSplitFeatureTool(DtMapTool):
    finishedDigitizing = QtCore.pyqtSignal(QgsGeometry)

    def __init__(self, canvas, iface):
        DtMapTool.__init__(self, canvas, iface)
        self.iface = iface
        self.marker = None
        self.rubberBand = None
        settings = QtCore.QSettings()
        settings.beginGroup("Qgis/digitizing")
        a = settings.value("line_color_alpha",200,type=int)
        b = settings.value("line_color_blue",0,type=int)
        g = settings.value("line_color_green",0,type=int)
        r = settings.value("line_color_red",255,type=int)
        lw = settings.value("line_width",1,type=int)
        settings.endGroup()
        self.rubberBandColor = QtGui.QColor(r, g, b, a)
        self.rubberBandWidth = lw
        self.reset()

    def markSnap(self, thisPoint):
        self.marker = QgsVertexMarker(self.canvas)
        self.marker.setIconType(1)
        self.marker.setColor(QtGui.QColor(255,0,0))
        self.marker.setIconSize(12)
        self.marker.setPenWidth (3)
        self.marker.setCenter(thisPoint)

    def removeSnapMarker(self):
        if self.marker != None:
            self.canvas.scene().removeItem(self.marker)
            self.marker = None

    def reset(self):
        if self.rubberBand != None:
            self.rubberBand.reset()
            self.canvas.scene().removeItem(self.rubberBand)
            self.rubberBand = None

        self.removeSnapMarker()

    def canvasMoveEvent(self, event):
        self.removeSnapMarker()
        # show snap
        x = event.pos().x()
        y = event.pos().y()
        thisPoint = QtCore.QPoint(x, y)
        # try to snap
        snapper = self.canvas.snappingUtils()
        # snap to any layer within snap tolerance
        snapMatch = snapper.snapToMap(thisPoint)

        if not snapMatch.isValid():
            if self.rubberBand != None:
                mapToPixel = self.canvas.getCoordinateTransform()
                self.rubberBand.movePoint(self.rubberBand.numberOfVertices() -1,
                    mapToPixel.toMapCoordinates(thisPoint))
        else:
            snapPoint = snapMatch.point()
            self.markSnap(snapPoint)

            if self.rubberBand != None:
                self.rubberBand.movePoint(self.rubberBand.numberOfVertices() -1,
                    snapPoint)

    def canvasReleaseEvent(self, event):
        layer = self.canvas.currentLayer()

        if layer <> None:
            #Get the click
            x = event.pos().x()
            y = event.pos().y()
            thisPoint = QtCore.QPoint(x, y)
            #QgsMapToPixel instance
            mapToPixel = self.canvas.getCoordinateTransform()

            if event.button() == QtCore.Qt.LeftButton:
                if self.rubberBand == None:
                    # create a QgsRubberBand
                    self.rubberBand = QgsRubberBand(self.canvas)
                    self.rubberBand.setColor(self.rubberBandColor)
                    self.rubberBand.setWidth(self.rubberBandWidth)
                    self.rubberBand.addPoint(mapToPixel.toMapCoordinates(thisPoint))
                    #self.startedDigitizing.emit(layer, self.lineFeature,  startPoint,  self.rubberBand)
                else:
                    self.rubberBand.addPoint(mapToPixel.toMapCoordinates(thisPoint))
            else: # right click
                if self.rubberBand.numberOfVertices() > 1:
                    rbGeom = self.rubberBand.asGeometry()
                    self.finishedDigitizing.emit(rbGeom)

                self.reset()
                self.canvas.refresh()

    def keyPressEvent(self,  event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.reset()

    def deactivate(self):
        self.reset()
