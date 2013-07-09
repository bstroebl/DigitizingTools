# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DigitizingTools
 A QGIS plugin
 Subsumes different tools useful during digitizing sessions
 Tool: SplitMultipart features into single part
 integrated into DigitizingTools by Bernhard Ströbl
                             -------------------
        begin                : 2013-01-17
        copyright            : (C) 2013 by Alexandre Neto
        email                : senhor.neto@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4 import QtCore,  QtGui
from qgis.core import *
import icons_rc

class DtSplitMultiPartTool():
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        
        #create action
         #":/plugins/digitizingtools/icons/multi_to_single.png"),  
        self.act_splitmultipart = QtGui.QAction(QtGui.QIcon(":/multi_to_single.png"),  
                                             QtCore.QCoreApplication.translate("digitizingtools", "Split multi part to single part"),  self.iface.mainWindow()) 
        self.act_splitmultipart.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act_splitmultipart)
        self.enable()
        
    def run(self):
        layer = self.iface.mapCanvas().currentLayer()
        provider = layer.dataProvider()
        new_features = []
        n_of_splitted_features = 0
        n_of_new_features = 0

        ## IMPROVE Check if Layer is selected and if is in edit mode

        layer.beginEditCommand("Split features")
        for feature in layer.selectedFeatures():
            geom = feature.geometry()
            # if feature geometry is multipart starts split processing
            if geom.isMultipart():
                n_of_splitted_features += 1
                #remove_list.append(feature.id())
                
                # Get attributes from original feature
                new_attributes = layer.pendingFields()
                for j in new_attributes:
                    if provider.defaultValue(j).isNull():
                        new_attributes[j] = feature.attributeMap()[j]
                    else:
                        new_attributes[j] = provider.defaultValue(j)
                        
                ## temp_feature.setAttributeMap(new_attributes)
                
                # Get parts from original feature
                parts = geom.asGeometryCollection ()
                        
                # from 2nd to last part create a new features using their
                # single geometry and the attributes of the original feature
                temp_feature = QgsFeature()
                temp_feature.setAttributeMap(new_attributes)
                for i in range(1,len(parts)):
                    temp_feature.setGeometry(parts[i])
                    new_features.append(QgsFeature(temp_feature))
                # update feature geometry to hold first part single geometry
                # (this way one of the output feature keeps the original Id)
                feature.setGeometry(parts[0])
                layer.updateFeature(feature)

        # add new features to layer
        n_of_new_features = len(new_features)
        if n_of_new_features > 0:
            layer.addFeatures(new_features, False)
            layer.endEditCommand()
        else:
            layer.destroyEditCommand()

        #print ("Splited " + str(n_of_splitted_features) + " feature(s) into " +
        #str(n_of_new_features + n_of_splitted_features) + " new ones.")
        
    
    def enable(self):
       # Disable the Button by default
        self.act_splitmultipart.setEnabled(False) 
        layer = self.iface.mapCanvas().currentLayer()
        
        if layer <> None:
            ## Only for vector layers.
            if layer.type() == 0:
                # enable if editable
                self.act_splitmultipart.setEnabled(layer.isEditable()) 
                layer.editingStarted.connect(self.enable)
                layer.editingStopped.connect(self.enable)
           
            
