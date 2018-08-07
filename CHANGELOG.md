# Change Log
All notable changes to this project since Version 0.8.0 will be documented in this file. Bug-fix releases are not documented seperately; their changes are listed in the Unreleased section until a new version is released.

## [Unreleased](https://github.com/bstroebl/DigitizingTools/compare/v1.1.0...develop)

### Fixed
- Fix occasional runtime error when trying to identify localization.
- Use new QgsVectorLayerUtils class for creating new features
- Merge new features with sequence value, too
- Adapt messages to new api

### Added
- Enable merge tool for all data providers. If no primary key field is present the internal id is presented as _Feature ID <value>_ to the user.

## [1.1.0](https://github.com/bstroebl/DigitizingTools/compare/v1.0.0...v1.1.0) - 2018-5-17
### Added
- Cut using the same layer as is the current edit layer, selection defines the cutting polygons, cutting will be performed on all polygons

### Fixed
- Activate tools for shape files, too. Reason: wkbType now always returns the multi type whereas in QGIS2 it used to return the single type
- Adapt more code to Qt5 api
- Remove editing command when splitting has been cancelled
- Show snap match in split feature tool before a rubber band exists, so first point of rubber band can snap, too

## [1.0.0] (https://github.com/bstroebl/DigitizingTools/compare/v0.11.3...v1.0.0) - 2018-05-15
### General
- Adapted to QGIS 3

### Added
- Improve split-feature tool: use tracing, fixes #20, show dotted rubberband for sketch, remove last point in rubberBand with backspace

### Changed
- Highlight feature being preserved in merge features tool, fixes #24

### Fixed
- Activate split multi part and extract part tools for any layer (not just for multi layers). In case the user tries to save a multi feature the data provider will deal with this.
- always catch backspace key while tool is active

## [0.11.3] (https://github.com/bstroebl/DigitizingTools/compare/v0.11.0...v0.11.3) - 2017-09-14
### Changed since 0.11.0
- Use Highlight color from settings in split feature
- Rename function "Exchange geometries" into "Exchange Attributes" to make it more in line with the naming of QGIS' standard tools

### Fixed since 0.11.0
- Remove run-time error if user chooses "No to All" in split feature
- Prevent endless loop if no splitting occures in multi-geometry feature

## [0.11.0](https://github.com/bstroebl/DigitizingTools/compare/v0.10.0...v0.11.0) - 2017-06-15
### Added
- Split features tool that replaces core's split features and makes core's split part unnecessary, see [#19](https://github.com/bstroebl/DigitizingTools/issues/19)

### Removed
- Prolong line has been removed because functionality is contained in core since QGIS 2.16

## [0.10.2](https://github.com/bstroebl/DigitizingTools/compare/v0.10.1...v0.10.2) - 2016-06-30
### Fixed
- Renamed icons file so icons do not dissappear, fixes [#14825](http://hub.qgis.org/issues/14825)

## [0.10.1](https://github.com/bstroebl/DigitizingTools/compare/v0.10.0...v0.10.1) - 2016-03-09
### Fixed
- Merge Tool: Single-geometry features are now allowed in multi-geometry layers

## [0.10.0](https://github.com/bstroebl/DigitizingTools/compare/v0.9.0...v0.10.0) - 2016-01-04
### Added
- Exchange geometry button: exchanges the geometries of two selected features. Reasoning: when splitting features in a layer coming from a database provider
the user can thus control which feature is going to keep the primary key value (important for related tables).

### Changed
- get project crs through QgMapSettings instead of deprecated QgsMapRenderer

### Fixed
- crash when selecting features during an editing session (fixes [#13827](http://hub.qgis.org/issues/13827)

## [0.9.0](https://github.com/bstroebl/DigitizingTools/compare/v0.8.0...v0.9.0) - 2015-11-09
### Added
- Merge tool: merges selected features but keeps the data of one of them. QGIS's default merge deletes all features and inserts the result of the merge as a new feature. See [#13490](http://hub.qgis.org/issues/13490)
- api-method geometryTypeMatchesLayer: check if the passed geom's geometry type matches the layer's geometry type

## 0.8.0 - 2015-09-30
### Added
- DtSelectFeatureTool.getFeatureForPoint: optional parameter inRing (default = False), returns (polygon) feature if point is located in a ring, returns the ring as third value

### Changed
- DtSelectFeatureTool.getFeatureForPoint: optional parameter inRing
- Tooltips improved

### Fixed
- Selection of parts and rings


