# Change Log
All notable changes to this project since Version 0.8.0 will be documented in this file.

## [Unreleased](https://github.com/bstroebl/DigitizingTools/compare/v0.11.0...develop)
### Changed
- Use Highlight color from settings in split feature

### Fixed
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


