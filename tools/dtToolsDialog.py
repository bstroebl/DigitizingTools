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

from PyQt4 import QtGui,  QtCore
from ui_dtchooseremaining import Ui_dtchooseremaining
from dtutils import dtGetHighlightSettings
from qgis.core import *
from qgis.gui import QgsHighlight

class DigitizingToolsChooseRemaining(QtGui.QDialog):
    def __init__(self, iface, editLayer, pkValues, featDict, title):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_dtchooseremaining()
        self.ui.setupUi(self)
        self.iface = iface
        self.editLayer = editLayer
        self.pkValues = pkValues
        self.featDict = featDict
        self.ui.chooseId.addItems(self.pkValues)
        self.setWindowTitle(title)
        self.ui.label.setText(QtCore.QCoreApplication.translate(
            "digitizingtools", "Choose which feature should remain"))
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.buttonBox.accepted.connect(self.accept)

    @QtCore.pyqtSlot(int)
    def on_chooseId_currentIndexChanged(self, thisIndex):
        aPkValue = self.ui.chooseId.currentText()
        aGeom = self.featDict[aPkValue].geometry()
        hlColor, hlFillColor, hlBuffer,  hlMinWidth = dtGetHighlightSettings()
        self.hl = QgsHighlight(self.iface.mapCanvas(), aGeom, self.editLayer)
        self.hl.setColor(hlColor)
        self.hl.setFillColor(hlFillColor)
        self.hl.setBuffer(hlBuffer)
        self.hl.setWidth(hlMinWidth)

    @QtCore.pyqtSlot()
    def reject(self):
        self.done(0)

    @QtCore.pyqtSlot()
    def accept(self):
        self.pkValueToKeep = self.ui.chooseId.currentText()
        self.done(1)
