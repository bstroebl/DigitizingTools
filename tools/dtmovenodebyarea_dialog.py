# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_dtmovenodebyarea import Ui_DtMoveNodeByArea

class DtMoveNodeByArea_Dialog(QDialog, QObject, Ui_DtMoveNodeByArea):
    
    def __init__(self, parent, flags):
        QDialog.__init__(self, parent,  flags)
        self.setupUi(self)
    
    def initGui(self):
        pass
      
    def writeArea(self, area):
        self.area_label.setText(str(area))
        
    @pyqtSignature("on_buttonClose_clicked()")    
    def on_buttonClose_clicked(self):
        self.emit(SIGNAL("unsetTool()"))         
        self.close()
        
    @pyqtSignature("on_moveButton_clicked()")
    def on_moveButton_clicked(self):
        self.emit(SIGNAL("moveNode()"))
        pass
