# -*- coding: utf-8 -*-
"""
dtfillgap
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-02-25
* copyright          : (C) 2013 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
from qgis.PyQt import QtCore,  QtGui
from qgis.core import *
from qgis.gui import *
import dt_icons_rc
import dtutils
from dttools import DtDualToolSelectGap, DtSingleTool, DtSelectGapTool

class DtFillGap(DtDualToolSelectGap):
    '''Fill gaps between selected features of the active layer with new features'''
    def __init__(self, iface,  toolBar):
        DtDualToolSelectGap.__init__(self,  iface,  toolBar,
            QtGui.QIcon(":/fillGap.png"),
            QtCore.QCoreApplication.translate("digitizingtools",
                "Fill gap with a new feature (interactive mode)"),
            QtGui.QIcon(":/fillGapBatch.png"),
            QtCore.QCoreApplication.translate("digitizingtools",
                "Fill all gaps between selected polygons with new features"),
            geometryTypes = [3, 6],  dtName = "dtFillGap")

        self.newFid = None
        self.title = QtCore.QCoreApplication.translate("digitizingtools", "Fill gap")

    def gapFound(self, result):
        layer = self.iface.activeLayer()
        gap = result[0]
        defaultAttributeMap = dtutils.dtGetDefaultAttributeMap(layer)
        layer.beginEditCommand(QtCore.QCoreApplication.translate(
            "editcommand", "Fill gap"))

        if self.iface.vectorLayerTools().addFeature(layer,
                defaultValues = defaultAttributeMap, defaultGeometry = gap):
            layer.endEditCommand()
            self.canvas.refresh()
        else:
            layer.destroyEditCommand()

        self.tool.reset()

    def process(self):
        # DtDualTool makes sure a selection exists
        layer = self.iface.activeLayer()
        multiGeom = dtutils.dtCombineSelectedPolygons(layer, self.iface)

        if multiGeom != None:
            rings = dtutils.dtExtractRings(multiGeom)

            if len(rings) == 0:
                self.iface.messageBar().pushMessage(self.title,
                    QtCore.QCoreApplication.translate("digitizingtools",
                    "There are no gaps between the polygons."),
                    level=QgsMessageBar.WARNING, duration = 10)
            else:
                defaultAttributeMap = dtutils.dtGetDefaultAttributeMap(layer)
                layer.featureAdded.connect(self.featureAdded)
                numRingsFilled = 0
                aborted = False

                for aRing in rings:
                    if numRingsFilled == 0:
                        layer.beginEditCommand(QtCore.QCoreApplication.translate(
                            "editcommand", "Fill gaps"))

                        if self.iface.vectorLayerTools().addFeature(
                                layer, defaultValues = defaultAttributeMap, defaultGeometry = aRing):
                            layer.featureAdded.disconnect(self.featureAdded)
                        else:
                            layer.featureAdded.disconnect(self.featureAdded)
                            aborted = True
                            break
                    else:
                        aFeat = dtutils.dtCopyFeature(layer, srcFid = self.newFid)
                        aFeat.setGeometry(aRing)
                        layer.addFeature(aFeat)

                    numRingsFilled += 1

                if aborted:
                    layer.destroyEditCommand()
                else:
                    layer.endEditCommand()

            self.canvas.refresh()

    def featureAdded(self,  newFid):
        self.newFid = newFid

class DtFillGapAllLayers(DtSingleTool):
    '''Fill gaps between the polygons of all visible layers with new features'''
    def __init__(self, iface, toolBar):
        DtSingleTool.__init__(self, iface, toolBar,
            QtGui.QIcon(":/fillGapAll.png"),
            QtCore.QCoreApplication.translate("digitizingtools",
                "Fill gap between polygons of all visible layers with a new feature"),
            geometryTypes = [3, 6], dtName = "dtFillGapAll")

        self.tool = DtSelectGapTool(self.canvas, self.iface, True)
        self.tool.gapSelected.connect(self.gapFound)
        self.enable()

    def process(self):
        self.canvas.setMapTool(self.tool)
        self.act.setChecked(True)

    def gapFound(self, result):
        layer = self.iface.activeLayer()
        gap = result[0]
        defaultAttributeMap = dtutils.dtGetDefaultAttributeMap(layer)
        layer.beginEditCommand(QtCore.QCoreApplication.translate(
            "editcommand", "Fill gap"))

        if self.iface.vectorLayerTools().addFeature(layer,
                defaultValues = defaultAttributeMap, defaultGeometry = gap):
            layer.endEditCommand()
            self.canvas.refresh()
        else:
            layer.destroyEditCommand()

        self.tool.reset()
