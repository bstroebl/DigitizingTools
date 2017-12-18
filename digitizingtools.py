# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DigitizingTools
 A QGIS plugin
 Subsumes different tools useful during digitizing sessions
 some code adopted/adapted from:
 'CadTools Plugin', Copyright (C) Stefan Ziegler
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
from __future__ import absolute_import
from builtins import object
# Import the PyQt and QGIS libraries
from qgis.PyQt import QtCore,  QtGui
from qgis.core import *
import os.path,  sys
# Set up current path.
currentPath = os.path.dirname( __file__ )
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/tools'))
from .dtDialog import DigitizingToolsAbout

#import the tools
import dtsplitmultipart
import dtcutter
import dtclipper
import dtfillring
import dtfillgap
import dtsplitter
import dtflipline
import dtsplitfeature
import dtmovenodebyarea
import dtmovesidebydistance
import dtmovesidebyarea
import dtmedianline
import dtextractpart
import dtmerge
import dtexchangegeometry

class DigitizingTools(object):
    """Main class for the plugin"""
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QtCore.QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/DigitizingTools"
        # initialize locale
        localePath = ""
        locale = QtCore.QSettings().value("locale/userLocale", "en",  type=str)[0:2]

        if QtCore.QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/digitizingtools_" + locale + ".qm"

        if QtCore.QFileInfo(localePath).exists():
            self.translator = QtCore.QTranslator()
            self.translator.load(localePath)

            if QtCore.qVersion() > '4.3.3':
                QtCore.QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        """Customize QGIS' GUI"""
        #. Add toolbar
        self.toolBar = self.iface.addToolBar("DigitizingTools")
        self.toolBar.setObjectName("DigitizingTools")

        #. Add a menu
        self.menuLabel = QtGui.QApplication.translate( "DigitizingTools","&DigitizingTools" )
        self.digitizingtools_help = QtGui.QAction( QtGui.QApplication.translate("DigitizingTools", "Help" ), self.iface.mainWindow() )
        self.digitizingtools_about = QtGui.QAction( QtGui.QApplication.translate("DigitizingTools", "About" ), self.iface.mainWindow() )
        self.digitizingtools_about.setObjectName("DtAbout")
        self.digitizingtools_settings = QtGui.QAction( QtGui.QApplication.translate("DigitizingTools", "Settings" ), self.iface.mainWindow() )

        self.iface.addPluginToMenu(self.menuLabel, self.digitizingtools_about)

        #. Add the tools
        self.multiPartSplitter = dtsplitmultipart.DtSplitMultiPartTool(self.iface, self.toolBar)
        self.partExtractor = dtextractpart.DtExtractPartTool(self.iface, self.toolBar)
        self.splitfeature = dtsplitfeature.DtSplitFeature(self.iface, self.toolBar)
        self.merger = dtmerge.DtMerge(self.iface, self.toolBar)
        self.exchangeGeometry = dtexchangegeometry.DtExchangeGeometry(self.iface, self.toolBar)
        self.cutter = dtcutter.DtCutWithPolygon(self.iface, self.toolBar)
        self.clipper = dtclipper.DtClipWithPolygon(self.iface, self.toolBar)
        self.ringFiller = dtfillring.DtFillRing(self.iface, self.toolBar)
        self.gapFiller = dtfillgap.DtFillGap(self.iface, self.toolBar)
        self.gapFillerAll = dtfillgap.DtFillGapAllLayers(self.iface, self.toolBar)
        self.splitter = dtsplitter.DtSplitWithLine(self.iface, self.toolBar)
        self.flipLine = dtflipline.DtFlipLine(self.iface,  self.toolBar)
        self.moveNodeByArea = dtmovenodebyarea.DtMoveNodeByArea(self.iface, self.toolBar)
        self.moveSideByDistance = dtmovesidebydistance.DtMoveSideByDistance(self.iface, self.toolBar)
        self.moveSideByArea = dtmovesidebyarea.DtMoveSideByArea(self.iface, self.toolBar)
        self.medianLine = dtmedianline.DtMedianLine(self.iface, self.toolBar)

        self.digitizingtools_about.triggered.connect(self.doAbout)
        #QObject.connect( self.digitizingtools_help, SIGNAL("triggered()"), self.doHelp )
        #QObject.connect( self.digitizingtools_settings, SIGNAL("triggered()"), self.doSettings )


    def doAbout(self):
        d = DigitizingToolsAbout(self.iface)
        d.exec_()

    def doHelp(self):
        webbrowser.open(currentPath + "/help/build/html/intro.html")

    def doSettings(self):
        settings = CadToolsSettingsGui(self.iface.mainWindow())
        settings.show()

    def unload(self):
        # remove toolbar and menu
        del self.toolBar
        self.iface.removePluginMenu(self.menuLabel, self.digitizingtools_about)

