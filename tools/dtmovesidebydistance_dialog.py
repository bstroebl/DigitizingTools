# -*- coding: utf-8 -*-
"""
dtmovesidebydistance_dialog
```````````````````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-08-15
* copyright            : (C) 2013 by Angelos Tzotsos
* email                : tzotsos@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt import QtWidgets, QtCore, uic
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_dtmovesidebydistance.ui'))

class DtMoveSideByDistance_Dialog(QtWidgets.QDialog, FORM_CLASS):
    unsetTool = QtCore.pyqtSignal()
    moveSide = QtCore.pyqtSignal()

    def __init__(self, parent, flags):
        super().__init__(parent, flags)
        self.setupUi(self)

    def initGui(self):
        pass

    @QtCore.pyqtSlot()
    def on_buttonClose_clicked(self):
        self.unsetTool.emit()
        self.close()

    @QtCore.pyqtSlot()
    def on_moveButton_clicked(self):
        self.moveSide.emit()
        pass
