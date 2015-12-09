# Change Log
All notable changes to this project since Version 0.8.0 will be documented in this file.

## [Unreleased](https://github.com/bstroebl/DigitizingTools/compare/v0.9.0...develop)
### Added
- Exchange geometry button: exchanges the geometries of two selected features. Reasoning: when splitting features in a layer coming from a databse provider
the user can thus control which feature is going to keep the primary key value (important for related tables).

## 0.9.0 - 2015-11-09
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


