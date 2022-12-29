# drawio_pysd

Note: This is currently in developement.

Investigating the possiblity to build graphically pysd models using drawio

Drawio allows to create charts in a very customizable way, which can make
more beautiful/customizable charts than the tradiction SD software allow.

Drawio is also open source which is a plus: https://github.com/jgraph/drawio

## Principles


The plugin is a simple javascript file that is loaded by drawio.

The plugins creates new elements in the drawio shapes menu.

Draw.io has *Data* parameters that can be assigned to each shape.
The elements for pysd have special data fields that contain the relevant 
pysd information. 

Double clicking on the shape opens a menu where the user can edit
the fields for the SD element (name, doc, equation, units, ... ).
(One can modify which fields are available by right clicking on the shape and
selecting *Edit Data*. )

Once the model is built, draw.io can export the model to a xml file.

The xml file is then read by the parse_xml module which creates a pysd AbstractModel.

This AbstractModel can then be built to any pysd supported format.

### Conversion from drawio to pysd


Draw.io saves by default the diagrams to a compressed xml format 
which is impossible to parse.
To convert a file from the compressed to uncompressed: https://drawio-app.com/extracting-the-xml-from-mxfiles/
or:
You can to : File-> Export as.. -> XML ...
Then untick *compressed*

### Autosuggestion of variable/units during coding

If a pysd shape is connected to another pysd shape using an arrow,
the variable name of the target shape is automatically suggested
in the menu of the equation of the source shape.

## Plugins with drawio

plugins can be added to drawio in a quite easily fashion.
One should understand javascript and how electron works.

Example can be found at https://github.com/jgraph/drawio/tree/dev/src/main/webapp/plugins

The plugin can simply be imported in drawio.

### Enabling plugins on linux

Add the option to the command line:

`drawio --enable-plugins`

On windows, it seems to be enabled by default sometimes but not always.
You find the exectuable there: 

`C:\Program Files\draw.io\draw.io.exe`

Then launch it with the option:

`drawio.exe --enable-plugins`

### Location of the plugin file

Once you load the plugin for the first time on the menu, it will be loaded to:

On linux if you installed with snap:

~/snap/drawio/current/.config/draw.io/plugins

Then you can modify the plugin file directly there so you don't need to load it every time.

On windows:

C:\Users\ *username* \AppData\Roaming\draw.io\plugins

## For developers

If you want to develop this plugins, please contact us before via github issues.

### Convenience tips

Create a symbolic link to the plugin file in the drawio plugin folder, so you don't need to load it every time.

