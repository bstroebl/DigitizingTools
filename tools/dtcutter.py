# -*- coding: utf-8 -*-
"""
dtcutter
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
from PyQt4 import QtCore,  QtGui
from qgis.core import *
import icons_rc
import dtutils

class DtCutWithPolygon():
    '''Cut out from active editable layer with selected polygon from another layer'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface

        #create action
        self.act_cutter = QtGui.QAction(QtGui.QIcon(":/cutter.png"),
            QtCore.QCoreApplication.translate("digitizingtools", "Cut with polygon from another layer"),  self.iface.mainWindow())
        self.act_cutter.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act_cutter)
        self.enable()

    def run(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate("digitizingtools", "Cutter")
        showEmptyWarning = True
        choice = None
        fidsToDelete = []
        cutterLayer = dtutils.dtChooseVectorLayer(self.iface,  2,  msg = QtCore.QCoreApplication.translate("digitizingtools", "cutter layer"))

        if cutterLayer == None:
            QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please provide a polygon layer to cut with."))
        else:
            passiveLayer = self.iface.activeLayer()

            if cutterLayer.selectedFeatureCount() == 0:
                msgLst = dtutils.dtGetNoSelMessage()
                noSelMsg1 = msgLst[0]
                noSelMsg2 = msgLst[1]
                reply = QtGui.QMessageBox.question(None,  title,
                                                   noSelMsg1 + " " + cutterLayer.name() + "\n" + noSelMsg2,
                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel )

                if reply == QtGui.QMessageBox.Yes:
                    cutterLayer.invertSelection()
                else:
                    return None

            if cutterLayer.selectedFeatureCount() > 0:
               # determine srs, we work in the project's srs
                cutterCRSSrsid = cutterLayer.crs().srsid()
                passiveCRSSrsid = passiveLayer.crs().srsid()
                mc = self.iface.mapCanvas()
                renderer = mc.mapRenderer()
                projectCRSSrsid = renderer.destinationCrs().srsid()
                passiveLayer.beginEditCommand(QtCore.QCoreApplication.translate("digitizingtools", "Cut Features"))
                featuresBeingCut = 0

                for feat in cutterLayer.selectedFeatures():
                    cutterGeom = feat.geometry()

                    if cutterCRSSrsid != projectCRSSrsid:
                        cutterGeom.transform(QgsCoordinateTransform(cutterCRSSrsid,  projectCRSSrsid))

                    bbox = cutterGeom.boundingBox()
                    passiveLayer.select(bbox, False) # make a new selection

                    for selFeat in passiveLayer.selectedFeatures():
                        selGeom = selFeat.geometry()

                        if passiveCRSSrsid != projectCRSSrsid:
                            selGeom.transform(QgsCoordinateTransform(passiveCRSSrsid,  projectCRSSrsid))

                        if cutterGeom.intersects(selGeom): # we have a candidate
                            newGeom = selGeom.difference(cutterGeom)

                            if newGeom != None:
                                if newGeom.isGeosEmpty():
                                    #selGeom is completely contained in cutterGeom
                                    if showEmptyWarning:
                                        choice = QtGui.QMessageBox.question(None,  title,
                                            QtCore.QCoreApplication.translate("digitizingtools",
                                            "A feature would be completely removed by cutting. Delete this feature\'s dataset altogether?"),
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.YesToAll | QtGui.QMessageBox.No | QtGui.QMessageBox.NoToAll | QtGui.QMessageBox.Cancel)

                                        if choice == QtGui.QMessageBox.Cancel:
                                            passiveLayer.destroyEditCommand()
                                            return None
                                        else:
                                            showEmptyWarning = (choice == QtGui.QMessageBox.Yes or choice == QtGui.QMessageBox.No)

                                    if choice == QtGui.QMessageBox.Yes or choice == QtGui.QMessageBox.YesToAll:
                                        fidsToDelete.append(selFeat.id())

                                else:
                                    if passiveCRSSrsid != projectCRSSrsid:
                                        newGeom.transform(QgsCoordinateTransform( projectCRSSrsid,  passiveCRSSrsid))

                                    selFeat.setGeometry(newGeom)
                                    passiveLayer.updateFeature(selFeat)
                                    #if passiveLayer.changeGeometry(selFeat.id(),  newGeom):
                                    featuresBeingCut += 1

                if featuresBeingCut > 0:
                    passiveLayer.endEditCommand()
                else:
                    passiveLayer.destroyEditCommand()

                passiveLayer.removeSelection()

                if len(fidsToDelete) > 0:
                    passiveLayer.beginEditCommand(QtCore.QCoreApplication.translate("digitizingtools", "Delete Features"))
                    for fid in fidsToDelete:
                        if not passiveLayer.deleteFeature(fid):
                            passiveLayer.destroyEditCommand()
                            return None

                    passiveLayer.endEditCommand()

                self.iface.mapCanvas().refresh()

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.act_cutter.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.

            if layer.type() == 0:
                # not for point layers

                if layer.geometryType() != 0:
                    # enable if editable
                    self.act_cutter.setEnabled(layer.isEditable())
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

