Introduction
============
 
The idea of this QGIS plugin is to subsume different tools useful
during digitizing sessions. Everybody is welcome to add their tools
to this collection.

Currently the following tools are contained:

#.  SplitMultipart: Splits multipart features into singlepart in the
    active editable layer; taken from Alexandre Neto's SplitMultipart
    plugin.
#.  Cutter: cut out from active editable layer with selected polygon from
    another layer
#.  Splitter: split selected features in active editable layer with
    selected line from another layer
#.  MoveNodeByArea: modifies a selected polygon, by selecting a stable 
    node (red) and a node to move (blue). The plugin moves the 
    second node automatically (along a stable side) to achieve the polygon
    area as provided by the user  
#.  MoveSideByDistance: modifies a selected polygon, by selecting a single 
    polygon side (segment) and by providing a distance to move the selected side.
#.  MoveSideByArea: modifies a selected polygon, by selecting a single 
    polygon side (segment). The plugin moves the second node automatically
    to achieve the polygon area as requested by the user. This tool has two
    options: (1) moving selected side by keeping it's length (fixed) and 
    (2) moving selected side along the direction of the two touching sides,
    forming a trapezoid along the process. The second option modifies the 
    selected side length (variable).

Planned/discussed tools can be found here http://osgeo-org.1560.x6.nabble.com/more-advanced-editing-tools-td5019552.html

This plugin is supposed to have no CAD-like tools which should go into
the CADTools plugin, see also http://osgeo-org.1560.x6.nabble.com/Make-QGIS-interact-with-LibreCAD-td5048565.html

Source
------

The source code can be found here: https://github.com/bstroebl/advancedDigitizingTools

Acknowledgements
----------------

Thanks to everybody joining the discussion and to Stefan Ziegler for
CADTools from where I took some code for the management of the plugin.
