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

from PyQt4 import QtGui,  QtCore
from ui_about import Ui_about

class DigitizingToolsAbout(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_about()
        self.ui.setupUi(self)
        # keep reference to QGIS interface
        self.iface = iface
        
        aboutText = QtCore.QCoreApplication.translate("dtAbout", "Subsumes different tools useful during digitizing sessions")
        aboutText.append(QtCore.QString("\n\n"))
        aboutText.append(QtCore.QCoreApplication.translate("dtAbout", "List of Contributors:"))
        aboutText.append(QtCore.QString("\n"))
        aboutText.append(QtCore.QString("Alexandre Neto"))
        aboutText.append(QtCore.QString("\n"))
        aboutText.append(QtCore.QString(u"Bernhard Ströbl"))
        aboutText.append(QtCore.QString("\n\n"))
        aboutText.append(QtCore.QString(u"DigitizingTools is copyright (C) 2013 Bernhard Ströbl bernhard.stroebl@jena.de\n\n"))
        aboutText.append(QtCore.QString(u"Licensed under the terms of the GNU GPL V 2:\n"))
        aboutText.append(QtCore.QString(u"This program is free software; you can redistribute it and/or modify it under the"))
        aboutText.append(QtCore.QString(" terms of the GNU General Public License as published by the Free Software Foundation;"))
        aboutText.append(QtCore.QString(" either version 2 of the License, or (at your option) any later version."))
        #QtGui.QMessageBox.information(None, "", aboutText)
        self.ui.textArea.setPlainText(aboutText)
        
        
        
        
        
        
        
