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

# translation
SOURCES = digitizingtools.py __init__.py dtDialog.py tools/dtutils.py
TRANSLATIONS = i18n/digitizingtools_de.ts i18n/digitizingtools_pt.ts

# global

PLUGINNAME = DigitizingTools

PY_FILES = digitizingtools.py __init__.py dtDialog.py

TOOLS = tools/dtutils.py tools/dtsplitmultipart.py tools/dtcutter.py tools/dtclipper.py \
	tools/dtfillring.py tools/dtfillgap.py tools/dtsplitter.py tools/dtsplitfeature.py \
	tools/dtsplitfeaturetool.py tools/dtmovenodebyarea.py tools/dtmovesidebydistance.py \
	tools/ui_dtmovenodebyarea.py tools/ui_dtmovesidebydistance.py \
	tools/dtmovenodebyarea_dialog.py tools/dtmovesidebydistance_dialog.py \
	tools/dtmovesidebyarea.py tools/ui_dtmovesidebyarea.py tools/dtmovesidebyarea_dialog.py \
	tools/dtflipline.py tools/dttools.py tools/dtmedianline.py tools/dtmedianlinetool.py \
	tools/dtextractpart.py tools/dtmerge.py tools/dtexchangegeometry.py tools/dtToolsDialog.py \
	tools/ui_dtchooseremaining.py

EXTRAS = metadata.txt license.txt digitizingtools.png

UI_FILES = ui_about.py tools/ui_dtmovenodebyarea.py tools/ui_dtmovesidebydistance.py tools/ui_dtmovesidebyarea.py tools/ui_dtchooseremaining.py

RESOURCE_FILES = tools/dt_icons_rc.py

HELP = help/build/html

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)
#compile: $(UI_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<

%.py : %.ui
	pyuic4 -o $@ $<

%.qm : %.ts
	lrelease $<

#compile: $(UI_FILES) $(RESOURCE_FILES)
#compile: $(UI_FILES)
compile3:

%_rc.py : %.qrc
	pyrcc5 -o $*_rc.py -py2 $<

%.py : %.ui
	pyuic5 -o $@ $<

%.qm : %.ts
	lrelease $<

# The deploy target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/.qgis/python/plugins
deploy: compile transcompile
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(PY_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(TOOLS) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(UI_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(EXTRAS) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vfr i18n $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
#	cp -vfr icons $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)
	cp -vfr $(HELP) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/help

deploy3: compile3 transcompile
	mkdir -p $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(PY_FILES) $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)
	cp -vf $(TOOLS) $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(UI_FILES) $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(EXTRAS) $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)
	cp -vfr i18n $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)
#	cp -vfr icons $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)
	cp -vfr $(HELP) $(HOME)/.qgis3/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/.qgis2/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/.qgis2/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/.qgis2/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

# Create a zip package of the plugin named $(PLUGINNAME).zip.
# This requires use of git (your plugin development directory must be a
# git repository).
# To use, pass a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
package: compile
		rm -f $(PLUGINNAME).zip
		git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
		echo "Created package: $(PLUGINNAME).zip"

upload: zip
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

# transup
# update .ts translation files
transup:
	pylupdate4 Makefile

# transcompile
# compile translation files into .qm binary format
transcompile: $(TRANSLATIONS:.ts=.qm)

# transclean
# deletes all .qm files
transclean:
	rm -f i18n/*.qm

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

# build documentation with sphinx
doc:
	cd help; make html
