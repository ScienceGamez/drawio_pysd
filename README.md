# drawio_pysd

Note: This is currently in developement.

Investigating the possiblity to build graphically pysd models using drawio

Drawio allows to create charts in a very customizable way, which can make
more beautiful/customizable charts than the tradiction SD software allow.

Drawio is also open source which is a plus: https://github.com/jgraph/drawio

## Principles

### Elements creation

Drawio is very flexible for creating custom elements.
This should really not be an issue as any shape or any container can be used.


### Conversion from drawio to pysd

This would be relatively easy as drawio saves as a xml format.
This xml format should contain xml headers that directly connect
the xml values to pysd values. Example (name, doc, equation, units, ... )

Note that there is also a compressed xml format which might be impossible to parse.
To convert a file from the compressed to uncompressed: https://drawio-app.com/extracting-the-xml-from-mxfiles/
or:
You can to : File-> Export as.. -> XML ...
Then untick *compressed*

### Autosuggestion of variable/units during coding

This seems to be tricky to do directly in drawio. An option
would be create a branch from the main drawio dedicated to writing
SD programs.

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

## Conclusion

Creating a fork of drawio adding functionality for SD seems like a too complex solution.
One should simply create one or many plugins that take care of that.
One shouuld also add direct conversion to pysd and export to python model.
