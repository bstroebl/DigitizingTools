# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DigitizingTools
 A QGIS plugin
 Subsumes different tools useful during digitizing sessions
                             -------------------
        begin                : 2013-02-25
        copyright          : (C) 2013 by Bernhard Ströbl
        email                : bernhard.stroebl@jena.de
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

from qgis.PyQt import QtWidgets, QtCore, uic
import os
from dtutils import dtGetVectorLayersByType

ABOUT_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_about.ui'))

CUTTER_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_dtcutter.ui'))

class DigitizingToolsAbout(QtWidgets.QDialog, ABOUT_CLASS):
    def __init__(self, iface):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        # keep reference to QGIS interface
        self.iface = iface

        aboutText = QtCore.QCoreApplication.translate("dtAbout", "Subsumes different tools useful during digitizing sessions")
        aboutText += "\n\n"
        aboutText += QtCore.QCoreApplication.translate("dtAbout", "List of Contributors:")
        aboutText +="\n"
        aboutText += "Sandra Lopes (Portugese translation)"
        aboutText +="\n"
        aboutText += "Alexandre Neto"
        aboutText += "\n"
        aboutText += "Jean-Cyrille Notter (French translation)"
        aboutText += "\n"
        aboutText += u"Bernhard Ströbl"
        aboutText += "\n"
        aboutText += u"Angelos Tzotsos"
        aboutText += "\n\n"
        aboutText += u"DigitizingTools is copyright (C) 2013 Bernhard Ströbl bernhard.stroebl[at]jena.de\n\n"
        aboutText += u"Licensed under the terms of the GNU GPL V 2:\n"
        aboutText += u"This program is free software; you can redistribute it and/or modify it under the"
        aboutText += " terms of the GNU General Public License as published by the Free Software Foundation;"
        aboutText += " either version 2 of the License, or (at your option) any later version."
        #QtGui.QMessageBox.information(None, "", aboutText)
        self.textArea.setPlainText(aboutText)

class DtChooseCutterLayer(QtWidgets.QDialog, CUTTER_CLASS):
    def __init__(self, iface, isPolygonLayer, lastChoice):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        # keep reference to QGIS interface
        self.iface = iface
        self.isPolygonLayer = isPolygonLayer
        self.setWindowTitle(QtCore.QCoreApplication.translate("dtCutterDialog",
            "Choose Layer"))
        self.lblCutter.setText(QtCore.QCoreApplication.translate("dtCutterDialog",
            "cutter layer"))
        self.chkCopy.setText(QtCore.QCoreApplication.translate("dtCutterDialog",
            "add cutter polygon to edit layer"))
        self.cutterLayer = lastChoice[0]
        self.copyPoly = lastChoice[1]
        self.initialize()

    def initialize(self):
        self.cbxLayer.clear()
        layerList = dtGetVectorLayersByType(self.iface,  2,  False)

        for keyValue, valueArray in list(layerList.items()):
            self.cbxLayer.addItem(keyValue, valueArray)

            if self.cutterLayer != None:
                if self.cutterLayer.id() == valueArray[0]:
                    self.cbxLayer.setCurrentText(keyValue)

        if not self.isPolygonLayer:
            self.chkCopy.setChecked(False)
        else:
            self.chkCopy.setChecked(self.copyPoly)

        self.chkCopy.setEnabled(self.isPolygonLayer)

    def accept(self):
        self.cutterLayer = self.cbxLayer.currentData()[1]
        self.copyPoly = self.chkCopy.isChecked()
        self.done(1)
