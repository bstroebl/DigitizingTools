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
 This script initializes the plugin, making it known to QGIS.
"""
from PyQt4 import QtCore

def name():
    return "Digitizing Tools"

def description():
    return QtCore.QCoreApplication.translate("dtAbout", "Subsumes different tools useful during digitizing sessions")

def version():
    return "Version 0.1"

def icon():
    return "icons/icon.png"

def qgisMinimumVersion():
    return "1.8"

def author():
    return "see list of contributors"

def classFactory(iface):
    # load RectOvalDigit class from file RectOvalDigit
    from digitizingtools import DigitizingTools
    return DigitizingTools(iface)

