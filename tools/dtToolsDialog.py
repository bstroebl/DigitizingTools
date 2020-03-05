# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DigitizingTools
 A QGIS plugin
 Subsumes different tools useful during digitizing sessions
                             -------------------
        begin                : 2017-12-12
        copyright          : (C) 2017 by Bernhard Ströbl
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
from dtutils import dtGetHighlightSettings
from qgis.core import *
from qgis.gui import QgsHighlight
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_dtchooseremaining.ui'))

class DigitizingToolsChooseRemaining(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, editLayer, pkValues, featDict, title):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.editLayer = editLayer
        self.pkValues = pkValues
        self.featDict = featDict
        self.chooseId.addItems(list(self.pkValues.keys()))
        self.setWindowTitle(title)
        self.label.setText(QtWidgets.QApplication.translate(
            "digitizingtools", "Choose which already existing feature should remain"))
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)

    def clearHighlight(self):
        try:
            self.hl.hide()
        except:
            pass

    @QtCore.pyqtSlot(int)
    def on_chooseId_currentIndexChanged(self, thisIndex):
        self.clearHighlight()
        aPkValue = self.chooseId.currentText()
        aGeom = self.featDict[self.pkValues[aPkValue]].geometry()
        hlColor, hlFillColor, hlBuffer,  hlMinWidth = dtGetHighlightSettings()
        self.hl = QgsHighlight(self.iface.mapCanvas(), aGeom, self.editLayer)
        self.hl.setColor(hlColor)
        self.hl.setFillColor(hlFillColor)
        self.hl.setBuffer(hlBuffer)
        self.hl.setWidth(hlMinWidth)
        self.hl.show()

    @QtCore.pyqtSlot()
    def reject(self):
        self.clearHighlight()
        self.done(0)

    @QtCore.pyqtSlot()
    def accept(self):
        self.clearHighlight()
        self.pkValueToKeep = self.chooseId.currentText()
        self.done(1)
