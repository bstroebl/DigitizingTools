# -*- coding: utf-8 -*-
"""
selectfeaturetool
`````````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-08-15
* copyright            : (C) 2013 by Bernhard Ströbl
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

class DtSelectFeatureTool(QgsMapTool):
    featureSelected = QtCore.pyqtSignal(list)

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas=canvas
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
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        layer = self.canvas.currentLayer()

        if layer <> None:
            #the clicked point is our starting point
            startingPoint = QtCore.QPoint(x,y)

            #we need a snapper, so we use the MapCanvas snapper
            snapper = QgsMapCanvasSnapper(self.canvas)
            (hasSnapSettings,  snapEnabled,  snapType,  snapUnits,  snapTolerance, avoidInters) = QgsProject.instance().snapSettingsForLayer(layer.id())

            if not hasSnapSettings:
                dtutils.showSnapSettingsWarning()
            elif not snapEnabled:
                dtutils.showSnapSettingsWarning()
            else:
                #we snap to the current layer (we don't have exclude points and use the tolerances from the qgis properties)
                (retval,result) = snapper.snapToCurrentLayer(startingPoint, snapType)

                if result == []:
                    dtutils.showSnapSettingsWarning()
                else:
                    #mehrere fids
                    fids = []
                    for i in range(len(result)):
                        fid = result[i].snappedAtGeometry # QgsFeatureId of the snapped geometry
                        fids.append(fid)

                    layer.removeSelection()
                    layer.setSelectedFeatures(fids)
                    self.featureSelected.emit(fids)

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
       pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

