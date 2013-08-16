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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_dtmovesidebydistance import Ui_DtMoveSideByDistance

class DtMoveSideByDistance_Dialog(QDialog, QObject, Ui_DtMoveSideByDistance):
    
    def __init__(self, parent, flags):
        QDialog.__init__(self, parent,  flags)
        self.setupUi(self)
    
    def initGui(self):
        pass
      
    @pyqtSignature("on_buttonClose_clicked()")    
    def on_buttonClose_clicked(self):
        self.emit(SIGNAL("unsetTool()"))         
        self.close()
        
    @pyqtSignature("on_moveButton_clicked()")
    def on_moveButton_clicked(self):
        self.emit(SIGNAL("moveSide()"))
        pass
