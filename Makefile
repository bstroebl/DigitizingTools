#/***************************************************************************
# DigitizingTools
#
# Subsumes different tools neded during digitizing sessions
#                             -------------------
#        begin                : 2013-02-25
#        copyright            : (C) 2013 by Bernhard Ströbl / Kommunale Immobilien Jena
#        email                : bernhard.stroebl@jena.de
# ***************************************************************************/
#
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

# CONFIGURATION
PLUGIN_UPLOAD = $(CURDIR)/plugin_upload.py

# Makefile for a PyQGIS plugin

#Add iso code for any locales you want to support here (space separated)
# default is no locales
# LOCALES = af
LOCALES = digitizingtools_de digitizingtools_fr

# If locales are enabled, set the name of the lrelease binary on your system. If
# you have trouble compiling the translations, you may have to specify the full path to
# lrelease
LRELEASE = lrelease
#LRELEASE = lrelease-qt4

# translation
SOURCES = digitizingtools.py __init__.py dtDialog.py tools/dtutils.py
#TRANSLATIONS = i18n/digitizingtools_de.ts i18n/digitizingtools_pt.ts

# global

PLUGINNAME = DigitizingTools

PY_FILES = digitizingtools.py __init__.py dtDialog.py

TOOLS = tools/dtutils.py tools/dtsplitmultipart.py tools/dtcutter.py tools/dtclipper.py \
	tools/dtfillring.py tools/dtfillgap.py tools/dtsplitter.py tools/dtsplitfeature.py \
	tools/dtsplitfeaturetool.py tools/dtmovenodebyarea.py tools/dtmovesidebydistance.py \
	tools/dtmovenodebyarea_dialog.py tools/dtmovesidebydistance_dialog.py \
	tools/dtmovesidebyarea.py tools/dtmovesidebyarea_dialog.py \
	tools/dtflipline.py tools/dttools.py tools/dtmedianline.py tools/dtmedianlinetool.py \
	tools/dtextractpart.py tools/dtmerge.py tools/dtexchangegeometry.py tools/dtToolsDialog.py \
	tools/ui_dtmovenodebyarea.ui tools/ui_dtmovesidebydistance.ui tools/ui_dtmovesidebyarea.ui \
	tools/ui_dtchooseremaining.ui

EXTRAS = metadata.txt license.txt digitizingtools.png

UI_FILES = ui_about.ui

RESOURCE_SRC=$(shell grep '^ *<file' dt_icons_rc.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')
COMPILED_RESOURCE_FILES = dt_icons_rc.py

HELP = help/build/html

QGISDIR=.local/share/QGIS/QGIS3/profiles/default

default: compile

compile: $(COMPILED_RESOURCE_FILES)

%.py : %.qrc $(RESOURCES_SRC)
	pyrcc5 -o $*.py  $<

%.qm : %.ts
	$(LRELEASE) $<

#compile: $(UI_FILES) $(RESOURCE_FILES)
#compile: $(UI_FILES)
#compile3:

#%_rc.py : %.qrc
#	pyrcc5 -o $*_rc.py -py2 $<

#%.py : %.ui
#	pyuic5 -o $@ $<

%.qm : %.ts
	lrelease $<

# The deploy target only works on unix like operating system where
deploy: compile transcompile
	@echo
	@echo "------------------------------------------"
	@echo "Deploying plugin to your .qgis3 directory."
	@echo "------------------------------------------"
	# The deploy  target only works on unix like operating system where
	# the Python plugin directory is located at:
	# $HOME/$(QGISDIR)/python/plugins
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(TOOLS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(COMPILED_RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vfr i18n $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	#cp -vfr $(HELP) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	@echo
	@echo "-----------------------------------"
	@echo "Removing any compiled python files."
	@echo "-----------------------------------"
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".git" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	@echo
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean
	@echo
	@echo "---------------------------"
	@echo "Creating plugin zip bundle."
	@echo "---------------------------"
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content. You can then upload the zip file on http://plugins.qgis.org
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

# Create a zip package of the plugin named $(PLUGINNAME).zip.
# This requires use of git (your plugin development directory must be a
# git repository).
# To use, pass a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
package: compile
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
	echo "Created package: $(PLUGINNAME).zip"

upload: zip
	@echo
	@echo "-------------------------------------"
	@echo "Uploading plugin to QGIS Plugin repo."
	@echo "-------------------------------------"
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

transup:
	@echo
	@echo "------------------------------------------------"
	@echo "Updating translation files with any new strings."
	@echo "------------------------------------------------"
	@chmod +x scripts/update-strings.sh
	@scripts/update-strings.sh $(LOCALES)

transcompile:
	@echo
	@echo "----------------------------------------"
	@echo "Compiled translation files to .qm files."
	@echo "----------------------------------------"
	@chmod +x scripts/compile-strings.sh
	@scripts/compile-strings.sh $(LRELEASE) $(LOCALES)

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f i18n/*.qm

clean:
	@echo
	@echo "------------------------------------"
	@echo "Removing uic and rcc generated files"
	@echo "------------------------------------"
	rm $(COMPILED_UI_FILES) $(COMPILED_RESOURCE_FILES)

doc:
	@echo
	@echo "------------------------------------"
	@echo "Building documentation using sphinx."
	@echo "------------------------------------"
	cd help; make html
