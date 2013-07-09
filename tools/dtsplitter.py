# -*- coding: utf-8 -*-
"""
dtsplitter
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

class DtSplitWithLine():
    '''Split selected features in active editable layer with selected line from another layer'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        
        #create action
        self.act_splitter = QtGui.QAction(QtGui.QIcon(":/splitter.png"),  
                                             QtCore.QCoreApplication.translate("digitizingtools", "Split selected features with selected line(s) from another layer"),  self.iface.mainWindow()) 
        self.act_splitter.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act_splitter)
        self.enable()
        
    def run(self):
        '''Function that does all the real work'''
        title = QtCore.QCoreApplication.translate("digitizingtools", "Splitter")
        splitterLayer = dtutils.dtChooseVectorLayer(self.iface,  1,  msg = QtCore.QCoreApplication.translate("digitizingtools", "splitter layer"))

        if splitterLayer == None:
            QtGui.QMessageBox.information(None, title,  QtCore.QCoreApplication.translate("digitizingtools", "Please provide a line layer to split with."))
        else:
            passiveLayer = self.iface.activeLayer()
            
            if splitterLayer.selectedFeatureCount() == 0:
                msgLst = dtutils.dtGetNoSelMessage()
                noSelMsg1 = msgLst[0]
                noSelMsg2 = msgLst[1]
                reply = QtGui.QMessageBox.question(None,  title, 
                                                   noSelMsg1 + " " + splitterLayer.name() + "\n" + noSelMsg2, 
                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel )
                
                if reply == QtGui.QMessageBox.Yes:
                    splitterLayer.invertSelection()
                else:
                    return None
                    
            if splitterLayer.selectedFeatureCount() > 0:
                if passiveLayer.selectedFeatureCount() == 0:
                    QtGui.QMessageBox.information(None, title,  noSelMsg1  + " " + passiveLayer.name() + ".\n" + \
                        QtCore.QCoreApplication.translate("digitizingtools", "Please select the features to be splitted."))
                    return None
                    
               # determine srs, we work in the project's srs
                splitterCRSSrsid = splitterLayer.crs().srsid()
                passiveCRSSrsid = passiveLayer.crs().srsid()
                mc = self.iface.mapCanvas()
                renderer = mc.mapRenderer()
                projectCRSSrsid = renderer.destinationCrs().srsid()

                passiveLayer.beginEditCommand(QtCore.QCoreApplication.translate("digitizingtools", "Split Features"))
                featuresBeingSplit = 0
                
                for feat in splitterLayer.selectedFeatures():
                    splitterGeom = feat.geometry()
                    if splitterCRSSrsid != projectCRSSrsid:
                        splitterGeom.transform(QgsCoordinateTransform(splitterCRSSrsid,  projectCRSSrsid))

                    for selFeat in passiveLayer.selectedFeatures():
                        selGeom = selFeat.geometry()
                        if passiveCRSSrsid != projectCRSSrsid:
                            selGeom.transform(QgsCoordinateTransform(passiveCRSSrsid,  projectCRSSrsid))
                        
                        if splitterGeom.intersects(selGeom): # we have a candidate
                            splitterPList = dtutils.dtExtractPoints(splitterGeom)
                            try:
                                result,  newGeometries,  topoTestPoints = selGeom.difference(splitterPList,  QgsProject.instance().topologicalEditing())
                            except:
                                QtGui.QMessageBox.warning(None,  title,  
                                    dtutils.dtGetErrorMessage + QtCore.QCoreApplication.translate("digitizingtools", "splitting of feature") + " " + str(sellFeat.id()))
                                return None
                            if result == 0:
                                if len(newGeometries) > 0:
                                    if passiveCRSSrsid != projectCRSSrsid:
                                        newGeom.transform(QgsCoordinateTransform( projectCRSSrsid,  passiveCRSSrsid))

                                    if passiveLayer.changeGeometry(selFeat.id(),  newGeom):
                                        featuresBeingSplit += 1
                
                if featuresBeingSplit > 0:
                    passiveLayer.endEditCommand()
                    passiveLayer.removeSelection()
                else:
                    passiveLayer.destroyEditCommand()
        
    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.act_splitter.setEnabled(False) 
        layer = self.iface.activeLayer()
        
        if layer <> None:
            ## Only for vector layers.
            if layer.type() == 0:
                # not for point layers
                if layer.geometryType != 0:
                    # enable if editable
                    self.act_splitter.setEnabled(layer.isEditable()) 
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)            
            
