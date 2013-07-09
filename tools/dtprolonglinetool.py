# -*- coding: utf-8 -*-
"""
dtprolonglinetool
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions
some code adopted/adapted from:
 'CadTools Plugin', Copyright (C) Stefan Ziegler

* begin                : 2013-02-25
* copyright          : (C) 2013 by Bernhard Ströbl
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

class DtProlongLineTool(QgsMapTool):
    startedDigitizing = QtCore.pyqtSignal(QgsVectorLayer,  QgsFeature,  QgsPoint,  QgsRubberBand)
    finishedDigitizing = QtCore.pyqtSignal(QgsGeometry)
    stoppedDigitizing = QtCore.pyqtSignal()

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas=canvas
        self.marker = None
        self.rubberBand = None
        self.cursor = QtGui.QCursor(QtGui.QPixmap(["16 16 3 1",
                                  "      c None",
                                  ".     c #000000",
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
        self.reset()

    def reset(self,  emitStopped = False):
        self.lineFeature = None

        if self.rubberBand != None:
            self.rubberBand.reset()
            self.rubberBand = None

        if self.marker != None:
            self.canvas.scene().removeItem(self.marker)
            self.marker = None
            # only emit signal if digitizing has already started
            if emitStopped:
                self.stoppedDigitizing.emit()

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        # move the last point
        if self.rubberBand != None:
            x = event.pos().x()
            y = event.pos().y()
            thisPoint = QtCore.QPoint(x, y)
            # try to snap
            snapper = QgsMapCanvasSnapper(self.canvas)
            # snap to any layer within snap tolerance
            (retval, result) = snapper.snapToBackgroundLayers(thisPoint)

            if result == []:
                mapToPixel = self.canvas.getCoordinateTransform()
                self.rubberBand.movePoint(self.rubberBand.numberOfVertices() -1,  mapToPixel.toMapCoordinates(thisPoint))
            else:
                self.rubberBand.movePoint(self.rubberBand.numberOfVertices() -1,  result[0].snappedVertex)

    def canvasReleaseEvent(self, event):
        layer = self.canvas.currentLayer()

        if layer <> None:
            #Get the click
            x = event.pos().x()
            y = event.pos().y()
            thisPoint = QtCore.QPoint(x, y)
            #we need a snapper, so we use the MapCanvas snapper
            snapper = QgsMapCanvasSnapper(self.canvas)
            #QgsMapToPixel instance
            mapToPixel = self.canvas.getCoordinateTransform()

            if event.button() == QtCore.Qt.LeftButton:
                if self.lineFeature == None:
                    # step 1: snap to a start/end point of an existing line
                    #we snap to the current layer (we don't have exclude points and use the tolerances from the qgis properties)
                    (retval, result) = snapper.snapToCurrentLayer (thisPoint, QgsSnapper.SnapToVertex)

                    if result != []:
                        #check if this is the start/end vertex of the line
                        if result[0].afterVertexNr == -1 or result[0].beforeVertexNr == -1:
                            # get the snapped feature
                            fid = result[0].snappedAtGeometry
                            self.lineFeature = QgsFeature()
                            featureFound = layer.getFeatures(QgsFeatureRequest().setFilterFid(fid)).nextFeature(self.lineFeature)

                            if featureFound:
                                #mark the vertex
                                startPoint = QgsPoint()
                                startPoint.setX( result[0].snappedVertex.x() )
                                startPoint.setY( result[0].snappedVertex.y() )
                                self.marker = QgsVertexMarker(self.canvas)
                                self.marker.setIconType(1)
                                self.marker.setColor(QtGui.QColor(255,0,0))
                                self.marker.setIconSize(12)
                                self.marker.setPenWidth (3)
                                self.marker.setCenter(startPoint)
                                # step 2: create a QgsRubberBand
                                self.rubberBand = QgsRubberBand(self.canvas)
                                self.rubberBand.addPoint(startPoint)
                                self.rubberBand.addPoint(startPoint) # second point to be moved
                                self.startedDigitizing.emit(layer, self.lineFeature,  startPoint,  self.rubberBand)
                            else:
                                self.lineFeature = None
                    else:
                        #warn about missing snapping tolerance if appropriate
                        dtutils.showSnapSettingsWarning()
                else: # step 3: have user digitize line
                    self.rubberBand.addPoint(mapToPixel.toMapCoordinates(thisPoint))
            else: # right click
                if self.lineFeature != None: # step 4: end digitizing merge rubbber band and existing geometry
                    rbGeom = self.rubberBand.asGeometry()
                    self.finishedDigitizing.emit(rbGeom)
                    self.reset()
                    self.canvas.refresh()

    def keyPressEvent(self,  event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.reset(True )

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.reset(True)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True


