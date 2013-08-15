# -*- coding: utf-8 -*-
"""
dtmovesidebyarea_dialog
```````````````````````
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_dtmovesidebyarea import Ui_DtMoveSideByArea

class DtMoveSideByArea_Dialog(QDialog, QObject, Ui_DtMoveSideByArea):
    
    def __init__(self, parent, flags):
        QDialog.__init__(self, parent,  flags)
        self.setupUi(self)
        self.method = "fixed"
    
    def initGui(self):
        self.radioFixed.setChecked(True)
        self.radioVariable.setChecked(False)
        pass
    
    def writeArea(self, area):
        self.area_label.setText(str(area))
        self.targetArea.setText(str(area))
    
    @pyqtSignature("on_radioFixed_clicked()")    
    def on_radioFixed_clicked(self):      
        self.method = "fixed"

    @pyqtSignature("on_radioVariable_clicked()")    
    def on_radioVariable_clicked(self):      
        self.method = "variable"
    
    @pyqtSignature("on_buttonClose_clicked()")    
    def on_buttonClose_clicked(self):
        self.emit(SIGNAL("unsetTool()"))         
        self.close()
        
    @pyqtSignature("on_moveButton_clicked()")
    def on_moveButton_clicked(self):
        self.emit(SIGNAL("moveSide()"))
        pass
