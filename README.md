# drawio_pysd
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

### Autosuggestion of variable/units during coding

This seems to be tricky to do directly in drawio. An option 
would be create a branch from the main drawio dedicated to writing 
SD programs. 

## Conclusion

Creating a fork of drawio adding functionality for SD seems like a promising solution.
One could also add direct conversion to pysd and export to python model.
