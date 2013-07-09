# -*- coding: utf-8 -*-
"""
dtutils
---------
Contains various utitlity functions

some code from fTools plugin contained.
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions.

* begin                : 2013-02-25
* copyright          : (C) 2013 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

license
````````
This program is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by 
the Free Software Foundation; either version 2 of the License, or  
(at your option) any later version.
"""

from PyQt4 import QtCore,  QtGui
from qgis.core import *

def dtGetFeatureForId(layer,  fid):
    '''Function that returns the QgsFeature with FeatureId *fid* in QgsVectorLayer *layer*'''
    feat = QgsFeature()
    
    if QGis.QGIS_VERSION_INT >= 10900:
        if layer.getFeatures(QgsFeatureRequest().setFilterFid(fid)).nextFeature(feat):
            return feat
        else:
            return None
    else:
        if layer.featureAtId(fid, feat, True, True):
            return feat
        else:
            return None

def dtCreateFeature(layer):
    '''Create an empty feature for the *layer*'''
    if isinstance(layer, QgsVectorLayer):
        newFeature = QgsFeature() 
        provider = layer.dataProvider()
        fields = layer.pendingFields()
        
        if QGis.QGIS_VERSION_INT >= 10900:
            newFeature.initAttributes(fields.count())			
            for i in range(fields.count()):
                newFeature.setAttribute(i, provider.defaultValue(i))
        else:
            for i in fields:
                newFeature.addAttribute(i,  provider.defaultValue(i))

        return newFeature
    else:
        return None

def dtCopyFeature(layer,  srcFid):
    '''Copy the QgsFeature with FeatureId *srcFid* in *layer* and return it. The feature is not added to the layer!'''
    srcFeature = dtGetFeatureForId(layer,  srcFid)
    
    if srcFeature:
        newFeature = dtCreateFeature(layer)
        
        #copy the attribute values#
        if QGis.QGIS_VERSION_INT >= 10900:
            pkFields = layer.dataProvider().pkAttributeIndexes()
            fields = layer.pendingFields()
            for i in range(fields.count()):
                # do not copy the PK value if there is a PK field
                if i in pkFields:
                    continue
                else:
                    newFeature.setAttribute(i, srcFeature.attribute(i))
            else:
                newFeature.setAttributeMap(srcFeature.attributeMap())

            return newFeature
        else:
            return None
    else:
        return None
    
def dtGetVectorLayersByType(iface,  geomType = None,  skipActive = False):
    '''Returns a dict of layers [name: id] in the project for the given
    *geomType*; geomTypes are 0: point, 1: line, 2: polygon
    If *skipActive* is True the active Layer is not included.'''
    layerList = {}
    for aLayer in iface.legendInterface().layers():
        if 0 == aLayer.type():   # vectorLayer
            if  skipActive and (iface.mapCanvas().currentLayer().id() == aLayer.id()):
                continue
            else:
                if geomType:
                    if isinstance(geomType,  int):
                        if aLayer.geometryType() == geomType:
                            layerList[aLayer.name()] =  aLayer.id()
                    else:
                        layerList[aLayer.name()] =  aLayer.id()
    return layerList
    
def dtChooseVectorLayer(iface, geomType = None,   skipActive = True,  msg = None):
    '''Offers a QInputDialog where the user can choose a Layer of type *geomType*. 
    If *skipActive* is True the active Layer can not be chosen. *msg* is displayed as the dialog's message.'''
    layerList = dtGetVectorLayersByType(iface,  geomType,  skipActive)
    chooseFrom = QtCore.QStringList()
    retValue = None
    
    if len(layerList) > 0:
        for aName in layerList:
            chooseFrom.append(aName)
        
        if not msg:
            msg = ""
            
        selectedLayer,  ok = QtGui.QInputDialog.getItem(None,  QtGui.QApplication.translate("dtutils",  "Choose Layer"), 
                                                        msg,  chooseFrom,  editable = False)
        
        if ok:
            for aLayer in iface.legendInterface().layers():
                if 0 == aLayer.type():
                    if aLayer.id() == layerList[selectedLayer]:
                        retValue = aLayer
                        break
            
    return retValue
    
def dtGetNoSelMessage():
    '''Returns an array of QStrings (default messages)'''
    noSelMsg1 = QtCore.QCoreApplication.translate("digitizingtools", "No Selection in layer")
    noSelMsg2 = QtCore.QCoreApplication.translate("digitizingtools", "Use all features for process?")
    return [noSelMsg1,  noSelMsg2]
    
def dtGetErrorMessage():
    '''Returns a QString (default error message which can be appended)'''
    return QtCore.QCoreApplication.translate("digitizingtools", "Error occured during")
    
# code taken from fTools plugin
def dtExtractPoints( geom ):
    '''Generate list of QgsPoints from QgsGeometry *geom* ( can be point, line, or polygon )'''
    multi_geom = QgsGeometry()
    temp_geom = []
    if geom.type() == 0: # it's a point
        if geom.isMultipart():
            temp_geom = geom.asMultiPoint()
        else:
            temp_geom.append(geom.asPoint())
    if geom.type() == 1: # it's a line
        if geom.isMultipart():
            multi_geom = geom.asMultiPolyline() #multi_geog is a multiline
            for i in multi_geom: #i is a line
                temp_geom.extend( i )
        else:
            temp_geom = geom.asPolyline()
    elif geom.type() == 2: # it's a polygon
        if geom.isMultipart():
            multi_geom = geom.asMultiPolygon() #multi_geom is a multipolygon
            for i in multi_geom: #i is a polygon
                for j in i: #j is a line
                    temp_geom.extend( j )
        else:
            multi_geom = geom.asPolygon() #multi_geom is a polygon
            for i in multi_geom: #i is a line
                temp_geom.extend( i )
    return temp_geom
