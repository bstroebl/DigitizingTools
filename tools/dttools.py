# -*- coding: utf-8 -*-
"""
dttools
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

from builtins import range
from builtins import object
from qgis.PyQt import QtGui,  QtCore, QtWidgets
from qgis.core import *
from qgis.gui import *
import dtutils

class DtTool(object):
    '''Abstract class; parent for any Dt tool or button'''
    def __init__(self,  iface,  geometryTypes, **kw):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

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

        self.geometryTypes = []
        self.shapeFileGeometryTypes = []

        # ESRI shapefile does not distinguish between single and multi geometries
        # source of wkbType numbers: http://gdal.org/java/constant-values.html
        for aGeomType in geometryTypes:
            if aGeomType == 1: # wkbPoint
                self.geometryTypes.append(1)
                self.shapeFileGeometryTypes.append(1)
                self.geometryTypes.append(-2147483647) #wkbPoint25D
                self.shapeFileGeometryTypes.append(-2147483647)
            elif aGeomType == 2: # wkbLineString
                self.geometryTypes.append(2)
                self.shapeFileGeometryTypes.append(2)
                self.geometryTypes.append(-2147483646) #wkbLineString25D
                self.shapeFileGeometryTypes.append(-2147483646)
            elif aGeomType == 3: # wkbPolygon
                self.geometryTypes.append(3)
                self.shapeFileGeometryTypes.append(3)
                self.geometryTypes.append(-2147483645) #wkbPolygon25D
                self.shapeFileGeometryTypes.append(-2147483645)
            elif aGeomType == 4: # wkbMultiPoint
                self.geometryTypes.append(4)
                self.shapeFileGeometryTypes.append(1) # wkbPoint
                self.geometryTypes.append(-2147483644) #wkbMultiPoint25D
                self.shapeFileGeometryTypes.append(-2147483647) #wkbPoint25D
            elif aGeomType == 5: # wkbMultiLineString
                self.geometryTypes.append(5)
                self.shapeFileGeometryTypes.append(2) # wkbLineString
                self.geometryTypes.append(-2147483643) #wkbMultiLineString25D
                self.shapeFileGeometryTypes.append(-2147483646) #wkbLineString25D
            elif aGeomType == 6: # wkbMultiPolygon
                self.geometryTypes.append(6)
                self.shapeFileGeometryTypes.append(3) # wkbPolygon
                self.geometryTypes.append(-2147483642) #wkbMultiPolygon25D
                self.shapeFileGeometryTypes.append(-2147483645) #wkbPolygon25D

    def allowedGeometry(self,  layer):
        '''check if this layer's geometry type is within the list of allowed types'''
        if layer.dataProvider().storageType() == u'ESRI Shapefile': # does not distinguish between single and multi
            result = self.shapeFileGeometryTypes.count(layer.wkbType()) >= 1
        else:
            result = self.geometryTypes.count(layer.wkbType()) == 1

        return result

    def geometryTypeMatchesLayer(self, layer, geom):
        '''check if the passed geom's geometry type matches the layer's type'''
        match = layer.wkbType() == geom.wkbType()

        if not match:
            if layer.dataProvider().storageType() == u'ESRI Shapefile':
                # does not distinguish between single and multi
                match = (layer.wkbType() == 1 and geom.wkbType() == 4) or \
                    (layer.wkbType() == 2 and geom.wkbType() == 5) or \
                    (layer.wkbType() == 3 and geom.wkbType() == 6)
            else:
                # are we trying a single into a multi layer?
                match = (layer.wkbType() == 4 and geom.wkbType() == 1) or \
                    (layer.wkbType() == 5 and geom.wkbType() == 2) or \
                    (layer.wkbType() == 6 and geom.wkbType() == 3)

        return match

    def isPolygonLayer(self, layer):
        ''' check if this layer is a polygon layer'''
        polygonTypes = [3, 6, -2147483645, -2147483642]
        result = layer.wkbType() in polygonTypes

        return result

    def debug(self, str):
        title = "DigitizingTools Debugger"
        QgsMessageLog.logMessage(title + "\n" + str)

class DtSingleButton(DtTool):
    '''Abstract class for a single button
    icon [QtGui.QIcon]
    tooltip [str]
    geometryTypes [array:integer] 0=point, 1=line, 2=polygon'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes = [1, 2, 3],  dtName = None):
        super().__init__(iface,  geometryTypes)

        self.act = QtWidgets.QAction(icon, tooltip, self.iface.mainWindow())
        self.act.triggered.connect(self.process)

        if dtName != None:
            self.act.setObjectName(dtName)

        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act)
        self.geometryTypes = geometryTypes

    def process(self):
        raise NotImplementedError("Should have implemented process")

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.act.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer != None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                if self.allowedGeometry(layer):
                    self.act.setEnabled(layer.isEditable())
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

class DtSingleTool(DtSingleButton):
    '''Abstract class for a tool'''
    def __init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes = [0, 1, 2],  crsWarning = True,  dtName = None):
        super().__init__(iface,  toolBar,  icon,  tooltip,  geometryTypes,  dtName)
        self.tool = None
        self.act.setCheckable(True)
        self.canvas.mapToolSet.connect(self.toolChanged)

    def toolChanged(self,  thisTool):
        if thisTool != self.tool:
            self.deactivate()

    def deactivate(self):
        if self.tool != None:
            self.tool.reset()

        self.reset()
        self.act.setChecked(False)

    def reset(self):
        pass

class DtSingleEditTool(DtSingleTool):
    '''Abstract class for a tool for interactive editing'''
    def __init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes = [0, 1, 2],  crsWarning = True,  dtName = None):
        super().__init__(iface,  toolBar,  icon,  tooltip,  geometryTypes,  dtName)
        self.crsWarning = crsWarning
        self.editLayer = None

    def reset(self):
        self.editLayer = None

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        doEnable = False
        layer = self.iface.activeLayer()

        if layer != None:
            if layer.type() == 0: #Only for vector layers.
                if self.allowedGeometry(layer):
                    doEnable = layer.isEditable()
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

        if self.editLayer != None: # we have a current edit session, activeLayer may have changed or editing status of self.editLayer
            try:
                self.editLayer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
            except:
                pass
            try:
                self.editLayer.editingStopped.disconnect(self.enable) # when it becomes active layer again
            except:
                pass

            self.tool.reset()
            self.reset()

        if not doEnable:
            self.deactivate()

        if doEnable and self.crsWarning:
            layerCRSSrsid = layer.crs().srsid()
            mapSet = self.canvas.mapSettings()
            projectCRSSrsid = mapSet.destinationCrs().srsid()

            if layerCRSSrsid != projectCRSSrsid:
                self.iface.messageBar().pushMessage("DigitizingTools",  self.act.toolTip() + " " +
                    QtWidgets.QApplication.translate("DigitizingTools",
                    "is disabled because layer CRS and project CRS do not match!"),
                    level=QgsMessageBar.WARNING, duration = 10)
                doEnable = False

        self.act.setEnabled(doEnable)

class DtDualTool(DtTool):
    '''Abstract class for a tool with interactive and batch mode
    icon [QtGui.QIcon] for interactive mode
    tooltip [str] for interactive mode
    iconBatch [QtGui.QIcon] for batch mode
    tooltipBatch [str] for batch mode
    geometryTypes [array:integer] 0=point, 1=line, 2=polygon'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes = [1, 2, 3],  dtName = None):
        super().__init__(iface,  geometryTypes)

        self.iface.currentLayerChanged.connect(self.enable)
        self.canvas.mapToolSet.connect(self.toolChanged)
        #create button
        self.button = QtWidgets.QToolButton(toolBar)
        self.button.clicked.connect(self.runSlot)
        self.button.toggled.connect(self.hasBeenToggled)
        #create menu
        self.menu = QtWidgets.QMenu(toolBar)

        if dtName != None:
            self.menu.setObjectName(dtName)

        self.menu.triggered.connect(self.menuTriggered)
        self.button.setMenu(self.menu)
        self.button.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        # create actions
        self.act = QtWidgets.QAction(icon, tooltip,  self.iface.mainWindow())

        if dtName != None:
            self.act.setObjectName(dtName + "Action")

        self.act.setToolTip(tooltip)
        self.act_batch = QtWidgets.QAction(iconBatch, tooltipBatch,  self.iface.mainWindow())

        if dtName != None:
            self.act_batch.setObjectName(dtName + "BatchAction")

        self.act_batch.setToolTip(tooltipBatch)
        self.menu.addAction(self.act)
        self.menu.addAction(self.act_batch)
        # set the interactive action as default action, user needs to click the button to activate it
        self.button.setIcon(self.act.icon())
        self.button.setToolTip(self.act.toolTip())
        self.button.setCheckable(True)
        self.batchMode = False
        # add button to toolBar
        toolBar.addWidget(self.button)
        self.geometryTypes = geometryTypes
        # run the enable slot
        self.enable()

    def menuTriggered(self,  thisAction):
        if thisAction == self.act:
            self.batchMode = False
            self.button.setCheckable(True)
            if not self.button.isChecked():
                self.button.toggle()
        else:
            self.batchMode = True
            if self.button.isCheckable():
                if self.button.isChecked():
                    self.button.toggle()
                self.button.setCheckable(False)

            self.runSlot(False)

        self.button.setIcon(thisAction.icon())
        self.button.setToolTip(thisAction.toolTip())

    def toolChanged(self,  thisTool):
        if thisTool != self.tool:
            self.deactivate()

    def hasBeenToggled(self,  isChecked):
        raise NotImplementedError("Should have implemented hasBeenToggled")

    def deactivate(self):
        if self.button != None:
            if self.button.isChecked():
                self.button.toggle()

    def runSlot(self,  isChecked):
        if self.batchMode:
            layer = self.iface.activeLayer()

            if layer.selectedFeatureCount() > 0:
                self.process()
        else:
            if not isChecked:
                self.button.toggle()

    def process(self):
        raise NotImplementedError("Should have implemented process")

    def enable(self):
       # Disable the Button by default
        self.button.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer != None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:

                # only for certain layers
                if self.allowedGeometry(layer):
                    if not layer.isEditable():
                        self.deactivate()

                    self.button.setEnabled(layer.isEditable())

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
                else:
                    self.deactivate()

class DtDualToolSelectFeature(DtDualTool):
    '''Abstract class for a DtDualToo which uses the DtSelectFeatureTool for interactive mode'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes = [1, 2, 3],  dtName = None):
        super().__init__(iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes,  dtName)
        self.tool = DtSelectFeatureTool(iface)

    def featureSelectedSlot(self,  fids):
        if len(fids) >0:
            self.process()

    def hasBeenToggled(self,  isChecked):
        try:
            self.tool.featureSelected.disconnect(self.featureSelectedSlot)
            # disconnect if it was already connected, so slot gets called only once!
        except:
            pass

        if isChecked:
            self.canvas.setMapTool(self.tool)
            self.tool.featureSelected.connect(self.featureSelectedSlot)
        else:
            self.canvas.unsetMapTool(self.tool)

class DtDualToolSelectVertex(DtDualTool):
    '''Abstract class for a DtDualTool which uses the DtSelectVertexTool for interactive mode
    numVertices [integer] nnumber of vertices to be snapped until vertexFound signal is emitted'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes = [1, 2, 3],  numVertices = 1,  dtName = None):
        super().__init__(iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes,  dtName)
        self.tool = DtSelectVertexTool(self.iface, numVertices)

    def hasBeenToggled(self,  isChecked):
        try:
            self.tool.vertexFound.disconnect(self.vertexSnapped)
            # disconnect if it was already connected, so slot gets called only once!
        except:
            pass

        if isChecked:
            self.canvas.setMapTool(self.tool)
            self.tool.vertexFound.connect(self.vertexSnapped)
        else:
            self.canvas.unsetMapTool(self.tool)

    def vertexSnapped(self,  snapResult):
        raise NotImplementedError("Should have implemented vertexSnapped")

class DtDualToolSelectRing(DtDualTool):
    '''
    Abstract class for a DtDualTool which uses the DtSelectRingTool for interactive mode
    '''

    def __init__(self, iface, toolBar, icon, tooltip, iconBatch,
        tooltipBatch, geometryTypes = [1, 2, 3], dtName = None):
        super().__init__(iface, toolBar, icon, tooltip,
            iconBatch, tooltipBatch, geometryTypes, dtName)
        self.tool = DtSelectRingTool(self.iface)

    def hasBeenToggled(self,  isChecked):
        try:
            self.tool.ringSelected.disconnect(self.ringFound)
            # disconnect if it was already connected, so slot gets called only once!
        except:
            pass

        if isChecked:
            self.canvas.setMapTool(self.tool)
            self.tool.ringSelected.connect(self.ringFound)
        else:
            self.canvas.unsetMapTool(self.tool)

    def ringFound(self, selectRingResult):
        raise NotImplementedError("Should have implemented ringFound")

class DtDualToolSelectGap(DtDualTool):
    '''
    Abstract class for a DtDualTool which uses the DtSelectGapTool for interactive mode
    '''

    def __init__(self, iface, toolBar, icon, tooltip, iconBatch,
            tooltipBatch, geometryTypes = [1, 2, 3], dtName = None,
            allLayers = False):
        super().__init__(iface, toolBar, icon, tooltip,
            iconBatch, tooltipBatch, geometryTypes, dtName)
        self.tool = DtSelectGapTool(self.iface, allLayers)

    def hasBeenToggled(self, isChecked):
        try:
            self.tool.gapSelected.disconnect(self.gapFound)
            # disconnect if it was already connected, so slot gets called only once!
        except:
            pass

        if isChecked:
            self.canvas.setMapTool(self.tool)
            self.tool.gapSelected.connect(self.gapFound)
        else:
            self.canvas.unsetMapTool(self.tool)

    def gapFound(self, selectGapResult):
        raise NotImplementedError("Should have implemented gapFound")

class DtMapToolEdit(QgsMapToolEdit, DtTool):
    '''abstract subclass of QgsMapToolEdit'''
    def __init__(self, iface, **kw):
        super().__init__(canvas = iface.mapCanvas(), iface = iface,  geometryTypes = [])

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.reset()

    def reset(self,  emitSignal = False):
        pass

class DtSelectFeatureTool(DtMapToolEdit):
    featureSelected = QtCore.pyqtSignal(list)

    def __init__(self, iface):
        super().__init__(iface)

    def getFeatureForPoint(self, layer, startingPoint, inRing = False):
        '''
        return the feature this QPoint is in (polygon layer)
        or this QPoint snaps to (point or line layer)
        '''
        result = []

        if self.isPolygonLayer(layer):
            mapToPixel = self.canvas.getCoordinateTransform()
            thisQgsPoint = mapToPixel.toMapCoordinates(startingPoint)
            spatialIndex = dtutils.dtSpatialindex(layer)
            featureIds = spatialIndex.nearestNeighbor(thisQgsPoint, 0)
            # if we use 0 as neighborCount then only features that contain the point
            # are included

            for fid in featureIds:
                feat = dtutils.dtGetFeatureForId(layer, fid)

                if feat != None:
                    geom = QgsGeometry(feat.geometry())

                    if geom.contains(thisQgsPoint):
                        result.append(feat)
                        result.append([])
                        return result
                        break
                    else:
                        if inRing:
                            rings = dtutils.dtExtractRings(geom)

                            if len(rings) > 0:
                                for aRing in rings:
                                    if aRing.contains(thisQgsPoint):
                                        result.append(feat)
                                        result.append([])
                                        result.append(aRing)
                                        return result
                                        break
        else:
            #we need a snapper, so we use the MapCanvas snapper
            snapper = self.canvas.snappingUtils()
            snapper.setCurrentLayer(layer)
            # snapType = 0: no snap, 1 = vertex, 2 vertex & segment, 3 = segment
            snapMatch = snapper.snapToCurrentLayer(startingPoint, QgsPointLocator.All)

            if not snapMatch.isValid():
                dtutils.showSnapSettingsWarning(self.iface)
            else:
                feat = dtutils.dtGetFeatureForId(layer, snapMatch.featureId())

                if feat != None:
                    result.append(feat)

                    if snapMatch.hasVertex():
                        result.append([snapMatch.point(), None])

                    if snapMatch.hasEdge():
                        result.append(snapMatch.edgePoints())

                    return result

        return result

    def canvasReleaseEvent(self,event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        layer = self.canvas.currentLayer()

        if layer != None:
            #the clicked point is our starting point
            startingPoint = QtCore.QPoint(x,y)
            found = self.getFeatureForPoint(layer, startingPoint)

            if len(found) > 0:
                feat = found[0]
                layer.removeSelection()
                layer.select(feat.id())
                self.featureSelected.emit([feat.id()])

class DtSelectRingTool(DtSelectFeatureTool):
    '''
    a map tool to select a ring in a polygon
    '''
    ringSelected = QtCore.pyqtSignal(list)

    def __init__(self, iface):
        super().__init__(iface)

    def canvasReleaseEvent(self,event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        layer = self.canvas.currentLayer()

        if layer != None:
            #the clicked point is our starting point
            startingPoint = QtCore.QPoint(x,y)
            found = self.getFeatureForPoint(layer, startingPoint, inRing = True)

            if len(found) == 3:
                aRing = found[2]
                self.ringSelected.emit([aRing])

    def reset(self, emitSignal = False):
        pass

class DtSelectGapTool(DtMapToolEdit):
    '''
    a map tool to select a gap between polygons, if allLayers
    is True then the gap is searched between polygons of
    all currently visible polygon layers
    '''
    gapSelected = QtCore.pyqtSignal(list)

    def __init__(self, iface, allLayers):
        super().__init__(iface)
        self.allLayers = allLayers

    def canvasReleaseEvent(self,event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        layer = self.canvas.currentLayer()
        visibleLayers = []

        if self.allLayers:
            for aLayer in self.iface.layerTreeCanvasBridge().rootGroup().checkedLayers():
                if 0 == aLayer.type():
                    if self.isPolygonLayer(aLayer):
                        visibleLayers.append(aLayer)
        else:
            if layer != None:
                visibleLayers.append(layer)

        if len(visibleLayers) > 0:
            #the clicked point is our starting point
            startingPoint = QtCore.QPoint(x,y)
            mapToPixel = self.canvas.getCoordinateTransform()
            thisQgsPoint = mapToPixel.toMapCoordinates(startingPoint)
            multiGeom = None

            for aLayer in visibleLayers:
                if not self.allLayers and aLayer.selectedFeatureCount() > 0:
                    #we assume, that the gap is between the selected polyons
                    hadSelection = True
                else:
                    hadSelection = False
                    spatialIndex = dtutils.dtSpatialindex(aLayer)
                    # get the 100 closest Features
                    featureIds = spatialIndex.nearestNeighbor(thisQgsPoint, 100)
                    aLayer.select(featureIds)

                multiGeom = dtutils.dtCombineSelectedPolygons(aLayer, self.iface, multiGeom)

                if self.allLayers or not hadSelection:
                    aLayer.removeSelection()

                if multiGeom == None:
                    return None

            if multiGeom != None:
                rings = dtutils.dtExtractRings(multiGeom)

                if len(rings) > 0:
                    for aRing in rings:
                        if aRing.contains(thisQgsPoint):
                            self.gapSelected.emit([aRing])
                            break

    def reset(self, emitSignal = False):
        pass

class DtSelectPartTool(DtSelectFeatureTool):
    '''signal sends featureId of clickedd feature, number of part selected and geometry of part'''
    partSelected = QtCore.pyqtSignal(list)

    def __init__(self, iface):
        super().__init__(iface)

    def canvasReleaseEvent(self,event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        layer = self.canvas.currentLayer()

        if layer != None:
            #the clicked point is our starting point
            startingPoint = QtCore.QPoint(x,y)
            found = self.getFeatureForPoint(layer, startingPoint)

            if len(found) > 0:
                feat = found[0]
                snappedPoints = found[1]

                if len(snappedPoints) > 0:
                    snappedVertex = snappedPoints[0]
                else:
                    snappedVertex = None

                geom = QgsGeometry(feat.geometry())

                # if feature geometry is multipart start split processing
                if geom.isMultipart():
                    # Get parts from original feature
                    parts = geom.asGeometryCollection()
                    mapToPixel = self.canvas.getCoordinateTransform()
                    thisQgsPoint = mapToPixel.toMapCoordinates(startingPoint)

                    for i in range(len(parts)):
                        # find the part that was snapped
                        aPart = parts[i]

                        if self.isPolygonLayer(layer):
                            if aPart.contains(thisQgsPoint):
                                self.partSelected.emit([feat.id(), i, aPart])
                                break
                        else:
                            points = dtutils.dtExtractPoints(aPart)

                            for j in range(len(points)):
                                aPoint = points[j]

                                if snappedVertex != None:
                                    if aPoint.x() == snappedVertex.x() and \
                                            aPoint.y() == snappedVertex.y():
                                        self.partSelected.emit([feat.id(), i, aPart])
                                        break
                                else:
                                    try:
                                        nextPoint = points[j + 1]
                                    except:
                                        break

                                    if aPoint.x() == snappedPoints[0].x() and \
                                            aPoint.y() == snappedPoints[0].y() and \
                                            nextPoint.x() == snappedPoints[1].x() and \
                                            nextPoint.y() == snappedPoints[1].y():
                                        self.partSelected.emit([feat.id(), i, aPart])
                                        break


class DtSelectVertexTool(DtMapToolEdit):
    '''select and mark numVertices vertices in the active layer'''
    vertexFound = QtCore.pyqtSignal(list)

    def __init__(self, iface, numVertices = 1):
        super().__init__(iface)

        # desired number of marked vertex until signal
        self.numVertices = numVertices
        # number of marked vertex
        self.count = 0
        # arrays to hold markers and vertex points
        self.markers = []
        self.points = []
        self.fids = []

    def canvasReleaseEvent(self,event):
        if self.count < self.numVertices: #not yet enough
            #Get the click
            x = event.pos().x()
            y = event.pos().y()

            layer = self.canvas.currentLayer()

            if layer != None:
                #the clicked point is our starting point
                startingPoint = QtCore.QPoint(x,y)

                #we need a snapper, so we use the MapCanvas snapper
                snapper = self.canvas.snappingUtils()
                snapper.setCurrentLayer(layer)

                # snapType = 0: no snap, 1 = vertex, 2 = segment, 3 = vertex & segment
                snapMatch = snapper.snapToCurrentLayer(startingPoint, QgsPointLocator.Vertex)

                if not snapMatch.isValid():
                    #warn about missing snapping tolerance if appropriate
                    dtutils.showSnapSettingsWarning(self.iface)
                else:
                    #mark the vertex
                    p = snapMatch.point()
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
                    fid = snapMatch.featureId() # QgsFeatureId of the snapped geometry
                    self.fids.append(fid)
                    self.count += 1

                    if self.count == self.numVertices:
                        self.vertexFound.emit([self.points,  self.markers,  self.fids])
                        #self.emit(SIGNAL("vertexFound(PyQt_PyObject)"), [self.points,  self.markers])

    def reset(self,  emitSignal = False):
        for m in self.markers:
            self.canvas.scene().removeItem(m)

        self.markers = []
        self.points = []
        self.fids = []
        self.count = 0

class DtSelectSegmentTool(DtMapToolEdit):
    segmentFound = QtCore.pyqtSignal(list)

    def __init__(self, iface):
        super().__init__(iface)
        self.rb1 = QgsRubberBand(self.canvas,  False)

    def canvasReleaseEvent(self,event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        layer = self.canvas.currentLayer()

        if layer != None:
            #the clicked point is our starting point
            startingPoint = QtCore.QPoint(x,y)

            #we need a snapper, so we use the MapCanvas snapper
            snapper = self.canvas.snappingUtils()
            snapper.setCurrentLayer(layer)

            # snapType = 0: no snap, 1 = vertex, 2 = segment, 3 = vertex & segment
            snapType = 2
            snapMatch = snapper.snapToCurrentLayer(startingPoint, QgsPointLocator.Edge)

            if not snapMatch.isValid():
                #warn about missing snapping tolerance if appropriate
                dtutils.showSnapSettingsWarning(self.iface)
            else:
                #if we have found a linesegment
                edge = snapMatch.edgePoints()
                p1 = edge[0]
                p2 = edge[1]
                # we like to mark the segment that is choosen, so we need a rubberband
                self.rb1.reset()
                color = QtGui.QColor(255,0,0)
                self.rb1.setColor(color)
                self.rb1.setWidth(2)
                self.rb1.addPoint(p1)
                self.rb1.addPoint(p2)
                self.rb1.show()
                self.segmentFound.emit([self.rb1.getPoint(0, 0),  self.rb1.getPoint(0, 1),  self.rb1])

    def reset(self,  emitSignal = False):
        self.rb1.reset()

class DtSplitFeatureTool(QgsMapToolAdvancedDigitizing, DtTool):
    finishedDigitizing = QtCore.pyqtSignal(QgsGeometry)

    def __init__(self, iface):
        super().__init__(canvas = iface.mapCanvas(), cadDockWidget = iface.cadDockWidget(),
            iface = iface, geometryTypes = [])
        self.marker = None
        self.rubberBand = None
        self.sketchRubberBand = self.createRubberBand()
        self.sketchRubberBand.setLineStyle(QtCore.Qt.DotLine)
        self.rbPoints = [] # array to store points in rubber band because
        # api to access points does not work properly or I did not figure it out :)
        self.currentMousePosition = None
        self.snapPoint = None
        self.reset()

    def activate(self):
        super().activate()
        self.canvas.setCursor(self.cursor)
        self.canvas.installEventFilter(self)
        self.snapPoint = None
        self.rbPoints = []

    def eventFilter(self, source, event):
        '''
        we need an eventFilter here to filter out Backspace key presses
        as otherwise the selected objects in the edit layer get deleted
        if user hits Backspace
        The eventFilter() function must return true if the event should be filtered,
        (i.e. stopped); otherwise it must return false, see
        http://doc.qt.io/qt-5/qobject.html#installEventFilter
        '''

        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Backspace:
                if self.rubberBand != None:
                    if self.rubberBand.numberOfVertices() >= 2: # QgsRubberBand has always 2 vertices
                        if self.currentMousePosition != None:
                            self.removeLastPoint()
                            self.redrawSketchRubberBand([self.toMapCoordinates(self.currentMousePosition)])
                return True
            else:
                return False
        else:
            return False

    def eventToQPoint(self, event):
        x = event.pos().x()
        y = event.pos().y()
        thisPoint = QtCore.QPoint(x, y)
        return thisPoint

    def initRubberBand(self, firstPoint):
        if self.rubberBand == None:
            # create a QgsRubberBand
            self.rubberBand = self.createRubberBand()
            self.rubberBand.addPoint(firstPoint)
            self.rbPoints.append(firstPoint)

    def removeLastPoint(self):
        ''' remove the last point in self.rubberBand'''
        if len (self.rbPoints) > 1: #first point will not be removed
            self.rbPoints.pop()
            #we recreate rubberBand because it contains doubles
            self.rubberBand.reset()

            for aPoint in self.rbPoints:
                self.rubberBand.addPoint(QgsPointXY(aPoint))


    def trySnap(self, event):
        self.removeSnapMarker()
        self.snapPoint = None
        # try to snap
        thisPoint = self.eventToQPoint(event)
        snapper = self.canvas.snappingUtils()
        # snap to any layer within snap tolerance
        snapMatch = snapper.snapToMap(thisPoint)

        if not snapMatch.isValid():
            return False
        else:
            self.snapPoint = snapMatch.point()
            self.markSnap(self.snapPoint)
            return True

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

    def clear(self):
        if self.rubberBand != None:
            self.rubberBand.reset()
            self.canvas.scene().removeItem(self.rubberBand)
            self.rubberBand = None

        if self.snapPoint != None:
            self.removeSnapMarker()
            self.snapPoint = None

        self.sketchRubberBand.reset()
        self.rbPoints = []

    def reset(self):
        self.clear()
        self.canvas.removeEventFilter(self)

    def redrawSketchRubberBand(self, points):
        if self.rubberBand != None and len(self.rbPoints) > 0:
            self.sketchRubberBand.reset()
            sketchStartPoint = self.rbPoints[len(self.rbPoints) -1]
            self.sketchRubberBand.addPoint(QgsPointXY(sketchStartPoint))

            if len(points) == 1:
                self.sketchRubberBand.addPoint(QgsPointXY(sketchStartPoint))
                self.sketchRubberBand.movePoint(
                    self.sketchRubberBand.numberOfVertices() -1, points[0])
            #for p in range(self.rubberBand.size()):
            #    self.debug("Part " + str(p))
            #    for v in range(self.rubberBand.partSize(p)):
            #        vertex = self.rubberBand.getPoint(0,j=v)
            #        self.debug("Vertex " + str(v) + " = "+ str(vertex.x()) + ", " + str(vertex.y()))



            #startPoint = self.rubberBand.getPoint(0, self.rubberBand.partSize(0) -1)
            #self.debug("StartPoint " + str(startPoint))
            #self.sketchRubberBand.addPoint(startPoint)
            #self.sketchRubberBand.addPoint(points[len(points) - 1])
            else:
                for aPoint in points:
                    self.sketchRubberBand.addPoint(aPoint)

    def cadCanvasMoveEvent(self, event):
        pass
        #self.debug("cadCanvasMoveEvent")

    def cadCanvasPressEvent(self, event):
        pass
        #self.debug("cadCanvasPressEvent")

    def cadCanvasReleaseEvent(self, event):
        pass
        #self.debug("cadCanvasReleaseEvent")

    def canvasMoveEvent(self, event):
        if self.rubberBand != None:
            thisPoint = self.eventToQPoint(event)
            hasSnap = self.trySnap(event)

            if hasSnap:
                #if self.canvas.snappingUtils().config().enabled(): # is snapping active?
                tracer = QgsMapCanvasTracer.tracerForCanvas(self.canvas)

                if tracer.actionEnableTracing().isChecked(): # tracing is pressed in
                    tracer.configure()
                    #startPoint = self.rubberBand.getPoint(0, self.rubberBand.numberOfVertices() -1)
                    startPoint = self.rbPoints[len(self.rbPoints) -1]
                    pathPoints,  pathError = tracer.findShortestPath(QgsPointXY(startPoint), self.snapPoint)

                    if pathError == 0: #ErrNone
                        pathPoints.pop(0) # remove first point as it is identical with starPoint
                        self.redrawSketchRubberBand(pathPoints)
                    else:
                        self.redrawSketchRubberBand([self.snapPoint])
                else:
                    self.redrawSketchRubberBand([self.snapPoint])
            else:
                self.redrawSketchRubberBand([self.toMapCoordinates(thisPoint)])

            self.currentMousePosition = thisPoint

    def canvasReleaseEvent(self, event):
        layer = self.canvas.currentLayer()

        if layer != None:
            thisPoint = self.eventToQPoint(event)
            #QgsMapToPixel instance

            if event.button() == QtCore.Qt.LeftButton:
                if self.rubberBand == None:
                    if self.snapPoint == None:
                        self.initRubberBand(self.toMapCoordinates(thisPoint))
                    else: # last mouse move created a snap
                        self.initRubberBand(self.snapPoint)
                        self.snapPoint = None
                        self.removeSnapMarker()
                else: # merge sketchRubberBand into rubberBand
                    sketchGeom = self.sketchRubberBand.asGeometry()
                    verticesSketchGeom = sketchGeom.vertices()
                    self.rubberBand.addGeometry(sketchGeom)
                    # rubberBand now contains a double point because it's former end point
                    # and sketchRubberBand's start point are identical
                    # so we remove the last point before adding new ones
                    self.rbPoints.pop()

                    while verticesSketchGeom.hasNext():
                        # add the new points
                        self.rbPoints.append(verticesSketchGeom.next())

                    self.redrawSketchRubberBand([self.toMapCoordinates(thisPoint)])

                    if self.snapPoint != None:
                        self.snapPoint = None
                        self.removeSnapMarker()
            else: # right click
                if self.rubberBand.numberOfVertices() > 1:
                    rbGeom = self.rubberBand.asGeometry()
                    self.finishedDigitizing.emit(rbGeom)

                self.clear()
                self.canvas.refresh()

    def keyPressEvent(self,  event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.clear()

    def deactivate(self):
        self.reset()
