/**
 * Plugin for creating pysd models in drawio.
 *
 * - Create custom mxcells for pysd
 * - Helps writing equations
 * - Double click opens equation menu
 * - Automatically design the cells
 *
 *
 */
Draw.loadPlugin(function (ui) {

    var default_style = 'html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;overflow=hidden;';


    function createPysdCell(pysdType, name, initial = false, equation = false, h = 20, w = 80) {
        var style = 'text;' + default_style;
        var cell = new mxCell('%Name%', new mxGeometry(0, 0, w, h), style);
        cell.vertex = true;
        ui.sidebar.graph.setAttributeForCell(cell, 'placeholders', '1');
        ui.sidebar.graph.setAttributeForCell(cell, 'Name', name);
        ui.sidebar.graph.setAttributeForCell(cell, 'Doc', '');
        ui.sidebar.graph.setAttributeForCell(cell, 'Units', '-');
        if (initial) {
            ui.sidebar.graph.setAttributeForCell(cell, '_initial', '0');
        }
        if (equation) {
            ui.sidebar.graph.setAttributeForCell(cell, '_equation', '');
        }
        // matching component type in pysd
        // https://github.com/SDXorg/pysd/blob/master/pysd/translators/structures/abstract_model.py
        ui.sidebar.graph.setAttributeForCell(cell, '_pysd_type', pysdType);
        return cell;
    }

    function createFluxCell() {
        // The flux is a collate shape to which we add a point in the middle for aestetics
        // we set the text at the bottom
        var cell = createPysdCell('AbstractElement', 'flux', false, true);
        cell.setStyle("shape=collate;whiteSpace=wrap;html=1;points=[[0,0,0,0,0],[0,0.5,0,0,0],[0,1,0,0,0],[0.5,0,0,0,0],[0.5,0.5,0,0,0],[0.5,1,0,0,0],[1,0,0,0,0],[1,0.5,0,0,0],[1,1,0,0,0]];labelPosition=center;verticalLabelPosition=bottom;align=center;verticalAlign=top;")
        return cell;
    }

    function createEdge() {
        var edge = new mxCell('', new mxGeometry(0, 0, 0, 0), 'endArrow=classic;html=1;rounded=0;');
        edge.edge = true;
        return edge;
    }

    // Reusable cells for subscripts lists
    var field = new mxCell('List Item', new mxGeometry(0, 0, 80, 30),
        'text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;' +
        'spacingLeft=4;spacingRight=4;overflow=hidden;points=[[0,0.5],[1,0.5]];' +
        'portConstraint=eastwest;rotatable=0;whiteSpace=wrap;html=1');
    field.vertex = true;

    // Sidebar is null in lightbox
    if (ui.sidebar != null) {
        var fns = [
            ui.sidebar.createVertexTemplateEntry('shape=image;image=https://raw.githubusercontent.com/SDXorg/pysd/master/docs/images/PySD_Logo.svg;editable=0;resizable=1;movable=1;rotatable=0', 100, 100, '', 'PySD Logo', null, null, 'text heading title'),
            ui.sidebar.addEntry('pysd template', mxUtils.bind(ui.sidebar, function () {
                // control variables
                var controlVariables = new Array("INITIAL TIME", "FINAL TIME", "TIME STEP", "SAVEPER");
                // create a list to store the cells
                var cells = [];
                // iterate over the names of the control variables
                for (var i = 0; i < controlVariables.length; i++) {
                    // create a cell for each control variable
                    var cell = createPysdCell('ControlVar', controlVariables[i], true, false);
                    // add the cell to the list
                    cells.push(cell);
                    // put the cell next to the previous one
                    cell.geometry.x = i * cell.geometry.width;
                    // set the attribute for the value of the control variable
                    cell.setAttribute('Name', controlVariables[i]);
                }
                // set the doc of the variables
                cells[0].setAttribute('Doc', 'Initial time of the simulation');
                cells[1].setAttribute('Doc', 'Final time of the simulation');
                cells[2].setAttribute('Doc', 'Time step of the simulation');
                cells[3].setAttribute('Doc', 'The frequency with which output is stored.');
                // set default values
                cells[0].setAttribute('_initial', '0');
                cells[1].setAttribute('_initial', '10');
                cells[2].setAttribute('_initial', '0.25');
                cells[3].setAttribute('_initial', '1');

                return ui.sidebar.createVertexTemplateFromCells(cells, cell.geometry.width, cell.geometry.height, 'Control Variables');
            })),
            ui.sidebar.addEntry('pysd template', mxUtils.bind(ui.sidebar, function () {
                var cell = createPysdCell('AbstractComponent', "new_variable", false, true);
                return ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, 'Variable');
            })),
            ui.sidebar.addEntry('pysd template', mxUtils.bind(ui.sidebar, function () {
                var cell = createPysdCell('AbstractUnchangeableConstant', 'new_constant', true, false);
                return ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, 'Constant');
            })),
            ui.sidebar.addEntry('pysd template', mxUtils.bind(ui.sidebar, function () {
                var cell = createPysdCell('IntegStructure', 'new_integ', true, true);
                cell.setStyle('rounded=0;whiteSpace=wrap;html=1;');
                return ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, 'Integ/Stock');
            })),
            ui.sidebar.addEntry('pysd template', mxUtils.bind(ui.sidebar, function () {
                var cell = createFluxCell();
                return ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, 'Element');
            })),
            ui.sidebar.addEntry('pysd template', mxUtils.bind(ui.sidebar, function () {
                var cell_integ = createPysdCell('IntegStructure', 'new_integ', true, true);
                // make the cell a rectangle instead of a text keeping the same other style
                cell_integ.setStyle('rounded=0;whiteSpace=wrap;html=1;');
                // add a text box to the edge
                var flux_cell = createFluxCell();
                // add another cell and an arrow to it
                var cell_to = createPysdCell('Sink');
                cell_to.setAttribute('Name', '');
                // cell_to is an ellipse
                cell_to.setStyle('ellipse;shape=cloud;whiteSpace=wrap;html=1;');
                // It is located at the right of the cell connected by an arrow
                // The offset is the same as the cell
                // Set the position of the cell_to to the right of the cell
                flux_cell.geometry.x = 2 * cell_integ.geometry.width + cell_integ.geometry.x;
                cell_to.geometry.x = 4 * cell_integ.geometry.width + cell_integ.geometry.x;
                flux_cell.geometry.height = 2 * cell_integ.geometry.height;
                cell_integ.geometry.y = flux_cell.geometry.y + cell_integ.geometry.height / 2;
                cell_to.geometry.y = flux_cell.geometry.y + cell_integ.geometry.height / 2;
                // add a visible arrow
                var edge_integ_flux = createEdge();
                edge_integ_flux.setStyle('shape=flexArrow;entryX=0.5;entryY=0.5;entryDx=0;entryDy=0;entryPerimeter=0;')
                var edge_flux_to = createEdge();
                edge_flux_to.setStyle('shape=flexArrow;exitX=0.5;exitY=0.5;exitDx=0;exitDy=0;exitPerimeter=0;')
                // connect the edge to the cells
                edge_integ_flux.setTerminal(cell_integ, true);
                edge_integ_flux.setTerminal(flux_cell, false);
                edge_flux_to.setTerminal(flux_cell, true);
                edge_flux_to.setTerminal(cell_to, false);


                // add the cells to the graph
                var cells = [cell_integ, cell_to, edge_integ_flux, edge_flux_to, flux_cell];
                return ui.sidebar.createVertexTemplateFromCells(cells, 5 * cell_integ.geometry.width, cell_integ.geometry.height, 'Integ Structure');

            })),
            ui.sidebar.addEntry('pysd template', mxUtils.bind(ui.sidebar, function () {
                var cell = createPysdCell('Subscript', 'new_subscript', false, false, h = 30, w = 100);
                cell.setStyle(
                    'swimlane;fontStyle=0;childLayout=stackLayout;horizontal=1;startSize=30;horizontalStack=0;' +
                    'resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;');
                cell.vertex = true;
                cell.insert(ui.sidebar.cloneCell(field, 'Dim 1'));
                cell.insert(ui.sidebar.cloneCell(field, 'Dim 2'));
                cell.insert(ui.sidebar.cloneCell(field, 'Dim 3'));



                return ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, 'Subscript');

            })),
            ui.sidebar.addEntry('pysd template', mxUtils.bind(ui.sidebar, function () {
                var cell = new mxCell('< %Name% >', new mxGeometry(0, 0, 110, 30), 'text;' + default_style + 'textOpacity=70;');
                cell.vertex = true;
                ui.sidebar.graph.setAttributeForCell(cell, 'placeholders', '1');
                ui.sidebar.graph.setAttributeForCell(cell, 'Name', 'new_reference');

                ui.sidebar.graph.setAttributeForCell(cell, '_pysd_type', 'Reference');
                return ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, 'Reference to Variable');
            })),
            //ui.sidebar.createVertexTemplateFromCells([createPysdCell()], cell.geometry.width, cell.geometry.height, 'Variable'),
        ]
        ui.sidebar.addPaletteFunctions('pysd', 'PySD', true, fns)
        // Adds custom sidebar entry

        // Collapses default sidebar entry and inserts this before
        var c = ui.sidebar.container;
        c.firstChild.click();
        c.insertBefore(c.lastChild, c.firstChild);

        // Adds logo to footer
        ui.footerContainer.innerHTML = '<img width=50px height=17px align="right" style="margin-top:14px;margin-right:12px;" ' + 'src="http://download.esolia.net.s3.amazonaws.com/img/eSolia-Logo-Color.svg"/>';

        // Adds placeholder for %today% and %filename%
        var graph = ui.editor.graph;
        var graphGetGlobalVariable = graph.getGlobalVariable;

        graph.getGlobalVariable = function (name) {
            if (name == 'today') {
                return new Date().toLocaleString();
            }
            else if (name == 'filename') {
                var file = ui.getCurrentFile();

                return (file != null && file.getTitle() != null) ? file.getTitle() : '';
            }

            return graphGetGlobalVariable.apply(this, arguments);
        };

        // Adds support for exporting PDF with placeholders
        var graphGetExportVariables = graph.getExportVariables;

        Graph.prototype.getExportVariables = function () {
            var vars = graphGetExportVariables.apply(this, arguments);
            var file = ui.getCurrentFile();

            vars['today'] = new Date().toLocaleString();
            vars['filename'] = (file != null && file.getTitle() != null) ? file.getTitle() : '';

            return vars;
        };

        // Adds resource for action
        mxResources.parse('helloWorldAction=Hello, World!');

        // Adds action
        ui.actions.addAction('helloWorldAction', function () {
            var ran = Math.floor((Math.random() * 100) + 1);
            mxUtils.alert('A random number is ' + ran);
        });

        // Adds menu
        ui.menubar.addMenu('Hello, World Menu', function (menu, parent) {
            ui.menus.addMenuItem(menu, 'helloWorldAction');
        });

        // Reorders menubar
        ui.menubar.container.insertBefore(ui.menubar.container.lastChild,
            ui.menubar.container.lastChild.previousSibling.previousSibling);

        // Adds toolbar button
        ui.toolbar.addSeparator();
        var elt = ui.toolbar.addItem('', 'helloWorldAction');

        // Cannot use built-in sprites
        elt.firstChild.style.backgroundImage = 'url(https://www.draw.io/images/logo-small.gif)';
        elt.firstChild.style.backgroundPosition = '2px 3px';
    }
});




/**
 * Constructs a new equation dialog.
 * This is taken from drawio EditDataDialog and moodified
 */
var EquationDialog = function (ui, cell) {

    // Top level element
    var top = document.createElement('section');
    top.style.position = 'absolute';
    top.style.top = '30px';
    top.style.left = '30px';
    top.style.right = '30px';
    top.style.bottom = '80px';
    top.style.overflowY = 'auto';
    // create a title for top
    var topTitle = document.createElement('h3');
    // The title depend on the pysd type of the cell
    title = cell.getAttribute('_pysd_type', 'variable');
    // Add spaces between the words
    title = title.replace(/([A-Z])/g, ' $1').trim();
    // Remove the first word if it is abstract
    title = title.replace('Abstract', '');
    topTitle.innerHTML = title;
    top.appendChild(topTitle);


    var div = document.createElement('div');
    var graph = ui.editor.graph;

    var value = graph.getModel().getValue(cell);

    // Converts the value to an XML node
    if (!mxUtils.isNode(value)) {
        var doc = mxUtils.createXmlDocument();
        var obj = doc.createElement('object');
        obj.setAttribute('label', value || '');
        value = obj;
    }

    var meta = {};

    try {
        var temp = mxUtils.getValue(ui.editor.graph.getCurrentCellStyle(cell), 'metaData', null);

        if (temp != null) {
            meta = JSON.parse(temp);
        }
    }
    catch (e) {
        // ignore
    }

    // Creates the dialog contents
    var propertiesForm = new mxForm('properties');
    propertiesForm.table.style.width = '100%';



    var attrs = value.attributes;
    var names = [];
    var texts = [];
    var count = 0;
    var variable_names = [];
    var variable_count = 0;
    var equationNode = null;


    var id = (EditDataDialog.getDisplayIdForCell != null) ?
        EditDataDialog.getDisplayIdForCell(ui, cell) : null;

    // create an area for the equation
    var equationAreaDiv = document.createElement('div');
    var equationArea = document.createElement('textarea');
    // remeber the last cursor position
    var equationAreaCursorPosition = 0;
    // update last cursor position
    equationArea.addEventListener('click', function () {
        equationAreaCursorPosition = equationArea.selectionStart;
    });
    // when dragging a variable, it will be added to the equation at the drop location
    equationArea.addEventListener('dragover', function (event) {
        event.preventDefault();
    });
    equationArea.addEventListener('drop', function (event) {
        event.preventDefault();
        var data = event.dataTransfer.getData("text");
        // find text index at the mouse position
        var text_index = equationAreaCursorPosition;
        // add the variable to the equation at the mouse position
        var equation = equationArea.value;
        // surround the data with spaces
        equationArea.value = equation.substring(0, text_index) + " " + data + " " + equation.substring(text_index);

    });
    // when selecting text and writing any kind of bracket, the brackets will be added around the selected text
    equationArea.addEventListener('keydown', function (event) {
        var key = event.key;
        var equation = equationArea.value;
        var selectionStart = equationArea.selectionStart;
        var selectionEnd = equationArea.selectionEnd;
        var selectedText = equation.substring(selectionStart, selectionEnd);
        if (selectedText.length > 0) {
            if (key == "(" || key == "[" || key == "{") {
                event.preventDefault();
                // get the clsoing bracket
                var closingBracket = "";
                if (key == "(") {
                    closingBracket = ")";
                }
                else if (key == "[") {
                    closingBracket = "]";
                }
                else if (key == "{") {
                    closingBracket = "}";
                }

                equationArea.value = equation.substring(0, selectionStart) + key + selectedText + closingBracket + equation.substring(selectionEnd);
                equationArea.selectionStart = selectionStart + 1;
                equationArea.selectionEnd = selectionEnd + 1;
            }
        }
    });


    equationArea.style.width = '100%';
    equationArea.style.height = '100%';
    equationAreaDiv.appendChild(equationArea);
    equationAreaDiv.style.textAlign = 'center';

    // set default text in equation area
    // the equation is stored in the property xml
    equationArea.value = "";


    var addRemoveButton = function (text, name, form) {
        var wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.paddingRight = '20px';
        wrapper.style.boxSizing = 'border-box';
        wrapper.style.width = '100%';

        var removeAttr = document.createElement('a');
        var img = mxUtils.createImage(Dialog.prototype.closeImage);
        img.style.height = '9px';
        img.style.fontSize = '9px';
        img.style.marginBottom = (mxClient.IS_IE11) ? '-1px' : '5px';

        removeAttr.className = 'geButton';
        removeAttr.setAttribute('title', mxResources.get('delete'));
        removeAttr.style.position = 'absolute';
        removeAttr.style.top = '4px';
        removeAttr.style.right = '0px';
        removeAttr.style.margin = '0px';
        removeAttr.style.width = '9px';
        removeAttr.style.height = '9px';
        removeAttr.style.cursor = 'pointer';
        removeAttr.appendChild(img);

        var removeAttrFn = (function (name) {
            return function () {
                var count = 0;

                for (var j = 0; j < names.length; j++) {
                    if (names[j] == name) {
                        texts[j] = null;
                        form.table.deleteRow(count + ((id != null) ? 1 : 0));

                        break;
                    }

                    if (texts[j] != null) {
                        count++;
                    }
                }
            };
        })(name);

        mxEvent.addListener(removeAttr, 'click', removeAttrFn);

        var parent = text.parentNode;
        wrapper.appendChild(text);
        wrapper.appendChild(removeAttr);
        parent.appendChild(wrapper);
    };

    var addTextArea = function (index, name, value) {
        names[index] = name;
        texts[index] = propertiesForm.addTextarea(names[count] + ':', value, 2);
        texts[index].style.width = '100%';

        if (value.indexOf('\n') > 0) {
            texts[index].setAttribute('rows', '2');
        }

        // addRemoveButton(texts[index], name, propertiesForm);

        if (meta[name] != null && meta[name].editable == false) {
            texts[index].setAttribute('disabled', 'disabled');
        }
    };

    var equationVariablesDiv = document.createElement('div');
    // add a title in the div
    var equationVariablesTitle = document.createElement('h3');
    equationVariablesTitle.innerHTML = "Variables";
    equationVariablesDiv.appendChild(equationVariablesTitle);

    // area containing the the variables
    var addVariables = function (index, cell) {

        var button = document.createElement('button');

        var name = cell.getAttribute('Name', 'new_variable');
        button.name = name;
        button.innerText = name;
        // When clicking on the button, add the variable to the equation area at the position of the cursor
        button.addEventListener('click', function (event) {
            var dropLocation = equationArea.selectionStart;
            equationArea.value = equationArea.value.slice(0, dropLocation) + " " + button.name + " " + equationArea.value.slice(dropLocation);
        });
        // When dragging the button in the equation area, add the variable to the equation area, at the position of the drop
        button.draggable = true;
        button.addEventListener('dragstart', function (event) {
            event.dataTransfer.setData("text", " " + button.name + " ");
        });


        variable_names[index] = name;
        equationVariablesDiv.appendChild(button);
        // addRemoveButton(variable_texts[index], name, variablesForm);

    };

    var temp = [];
    var isLayer = graph.getModel().getParent(cell) == graph.getModel().getRoot();
    for (var i = 0; i < attrs.length; i++) {
        if ((attrs[i].nodeName != 'label' || Graph.translateDiagram ||
            isLayer) && attrs[i].nodeName != 'placeholders'
            && !attrs[i].nodeName.startsWith('_')) {
            temp.push({ name: attrs[i].nodeName, value: attrs[i].nodeValue });
        }

    }

    // Sorts by name
    /* 	temp.sort(function (a, b)
        {
            if (a.name < b.name) {
                return -1;
            }
            else if (a.name > b.name) {
                return 1;
            }
            else {
                return 0;
            }
        });
    */

    // for editing the id
    if (id != null) {
        var text = document.createElement('div');
        text.style.width = '100%';
        text.style.fontSize = '11px';
        text.style.textAlign = 'center';
        mxUtils.write(text, id);

        var idInput = propertiesForm.addField(mxResources.get('id') + ':', text);

        mxEvent.addListener(text, 'dblclick', function (evt) {
            if (mxEvent.isShiftDown(evt)) {
                var dlg = new FilenameDialog(ui, id, mxResources.get('apply'), mxUtils.bind(this, function (value) {
                    if (value != null && value.length > 0 && value != id) {
                        if (graph.getModel().getCell(value) == null) {
                            graph.getModel().cellRemoved(cell);
                            cell.setId(value);
                            id = value;
                            idInput.innerHTML = mxUtils.htmlEntities(value);
                            graph.getModel().cellAdded(cell);
                        }
                        else {
                            ui.handleError({ message: mxResources.get('alreadyExst', [value]) });
                        }
                    }
                }), mxResources.get('id'));
                ui.showDialog(dlg.container, 300, 80, true, true);
                dlg.init();
            }
        });

        text.setAttribute('title', 'Shift+Double Click to Edit ID');
    }

    top.appendChild(propertiesForm.table);


    // If the cell is of a type that need an inital value,
    // create a text area for editing the _initial value
    var initialArea = document.createElement('textarea');
    if (
        value.getAttribute('_pysd_type') == 'IntegStructure'
        || value.getAttribute('_pysd_type') == 'AbstractUnchangeableConstant'
        || value.getAttribute('_pysd_type') == 'ControlVar'
    ) {
        var initialAreaDiv = document.createElement('div');
        // add a title in the div
        var initialAreaTitle = document.createElement('h3');

        if( value.getAttribute('_pysd_type') == 'IntegStructure') {
            initialAreaTitle.innerHTML = "Initial Value";
        } else {
            initialAreaTitle.innerHTML = "Value";
        }
        initialAreaDiv.appendChild(initialAreaTitle);
        initialAreaDiv.appendChild(initialArea);

        initialArea.value = value.getAttribute('_initial');
        // add to top
        top.appendChild(initialAreaDiv);
    }


    for (var i = 0; i < temp.length; i++) {
        addTextArea(count, temp[i].name, temp[i].value);
        count++;
    }







    function getChildrenOfCell(cell) {
        if (cell != undefined) {
            let children = [];
            let edges = cell.edges;
            if (edges != null) {
                for (let i = 0; i < edges.length; i++) {
                    if (edges[i].target.value == cell.value) {
                        let cellCopy = edges[i].source.clone();
                        children.push(cellCopy);
                    }
                }
            }
            return children;
        }
        else {
            return [];
        }
    }

    // Will return the equation of the cell
    function guessEquation(cell){
        var equation = "";

        // check if the arrow connecting the children is in or out
        var edges = cell.edges;
        for (var j = 0; j < edges.length; j++) {
            var edge = edges[j];
            if (edge.target.value == cell.value) {
                equation += " + ";
                // add the variable name
                equation += edge.source.value.getAttribute('Name');
            } else {
                equation += " - ";
                // add the variable name
                equation += edge.target.value.getAttribute('Name');
            }
        }

        return equation;
    }




    var parents = getChildrenOfCell(cell);
    for (var i = 0; i < parents.length; i++) {
        addVariables(variable_count, parents[i]);
        variable_count++;
    }


    // only add the equation if the cell contains an _equation parameter
    if (cell.getAttribute('_equation') != null) {
        var equationTitleDiv = document.createElement('div');
        // set title string
        var equationTitle = document.createElement('h3');
        equationTitle.innerHTML = "Equation";
        equationTitleDiv.appendChild(equationTitle);

        // if Integ, we want to have a guess button to guess what is the equation
        if (value.getAttribute('_pysd_type') == 'IntegStructure') {
            equationTitle.innerHTML = "Flux";

            var guessButton = document.createElement('button');
            guessButton.innerHTML = "Guess";
            guessButton.onclick = function () {
                equationArea.value = guessEquation(cell);
            }
            equationTitleDiv.appendChild(guessButton);
        }


        // set initial value in the equation area
        equationArea.value = cell.getAttribute('_equation');

        top.appendChild(equationTitleDiv);
        top.appendChild(equationAreaDiv);
    }
    top.appendChild(equationVariablesDiv);

    // var newProp = document.createElement('div');
    // newProp.style.boxSizing = 'border-box';
    // newProp.style.paddingRight = '160px';
    // newProp.style.whiteSpace = 'nowrap';
    // newProp.style.marginTop = '6px';
    // newProp.style.width = '100%';

    // var nameInput = document.createElement('input');
    // nameInput.setAttribute('placeholder', mxResources.get('enterPropertyName'));
    // nameInput.setAttribute('type', 'text');
    // nameInput.setAttribute('size', (mxClient.IS_IE || mxClient.IS_IE11) ? '36' : '40');
    // nameInput.style.boxSizing = 'border-box';
    // nameInput.style.marginLeft = '2px';
    // nameInput.style.width = '100%';

    // newProp.appendChild(nameInput);
    // top.appendChild(newProp);
    div.appendChild(top);

    // var addBtn = mxUtils.button(mxResources.get('addProperty'), function ()
    // {
    // 	var name = nameInput.value;

    // 	// Avoid ':' in attribute names which seems to be valid in Chrome
    // 	if (name.length > 0 && name != 'label' && name != 'placeholders' && name.indexOf(':') < 0) {
    // 		try {
    // 			var idx = mxUtils.indexOf(names, name);

    // 			if (idx >= 0 && texts[idx] != null) {
    // 				texts[idx].focus();
    // 			}
    // 			else {
    // 				// Checks if the name is valid
    // 				var clone = value.cloneNode(false);
    // 				clone.setAttribute(name, '');

    // 				if (idx >= 0) {
    // 					names.splice(idx, 1);
    // 					texts.splice(idx, 1);
    // 				}

    // 				names.push(name);
    // 				var text = propertiesForm.addTextarea(name + ':', '', 2);
    // 				text.style.width = '100%';
    // 				texts.push(text);
    // 				addRemoveButton(text, name);

    // 				text.focus();
    // 			}

    // 			addBtn.setAttribute('disabled', 'disabled');
    // 			nameInput.value = '';
    // 		}
    // 		catch (e) {
    // 			mxUtils.alert(e);
    // 		}
    // 	}
    // 	else {
    // 		mxUtils.alert(mxResources.get('invalidName'));
    // 	}
    // });

    // mxEvent.addListener(nameInput, 'keypress', function (e)
    // {
    // 	if (e.keyCode == 13) {
    // 		addBtn.click();
    // 	}
    // });

    this.init = function () {
        if (texts.length > 0) {
            texts[0].focus();
        }
        else {
            //nameInput.focus();
        }
    };

    // addBtn.setAttribute('title', mxResources.get('addProperty'));
    // addBtn.setAttribute('disabled', 'disabled');
    // addBtn.style.textOverflow = 'ellipsis';
    // addBtn.style.position = 'absolute';
    // addBtn.style.overflow = 'hidden';
    // addBtn.style.width = '144px';
    // addBtn.style.right = '0px';
    // addBtn.className = 'geBtn';
    // newProp.appendChild(addBtn);

    var cancelBtn = mxUtils.button(mxResources.get('cancel'), function () {
        ui.hideDialog.apply(ui, arguments);
    });


    cancelBtn.setAttribute('title', 'Escape');
    cancelBtn.className = 'geBtn';

    var applyBtn = mxUtils.button(mxResources.get('apply'), function () {
        try {
            ui.hideDialog.apply(ui, arguments);

            // Clones and updates the value
            value = value.cloneNode(true);
            var removeLabel = false;

            for (var i = 0; i < names.length; i++) {
                if (texts[i] == null) {
                    value.removeAttribute(names[i]);
                }
                else {
                    value.setAttribute(names[i], texts[i].value);
                    removeLabel = removeLabel || (names[i] == 'placeholder' &&
                        value.getAttribute('placeholders') == '1');
                }
            }

            // Removes label if placeholder is assigned
            if (removeLabel) {
                value.removeAttribute('label');
            }
            // TODO add a check that variables are in the equation

            // Save the equation as an attribute
            value.setAttribute('_equation', equationArea.value);

            // Save the initial value as an attribute
            value.setAttribute('_initial', initialArea.value);

            // Updates the value of the cell (undoable)
            graph.getModel().setValue(cell, value);
        }
        catch (e) {
            mxUtils.alert(e);
        }
    });

    applyBtn.setAttribute('title', 'Ctrl+Enter');
    applyBtn.className = 'geBtn gePrimaryBtn';

    mxEvent.addListener(div, 'keypress', function (e) {
        if (e.keyCode == 13 && mxEvent.isControlDown(e)) {
            applyBtn.click();
        }
    });

    // function updateAddBtn()
    // {
    // 	if (nameInput.value.length > 0) {
    // 		addBtn.removeAttribute('disabled');
    // 	}
    // 	else {
    // 		addBtn.setAttribute('disabled', 'disabled');
    // 	}
    // };

    //mxEvent.addListener(nameInput, 'keyup', updateAddBtn);

    // Catches all changes that don't fire a keyup (such as paste via mouse)
    //mxEvent.addListener(nameInput, 'change', updateAddBtn);

    var buttons = document.createElement('div');
    buttons.style.cssText = 'position:absolute;left:30px;right:30px;text-align:right;bottom:30px;height:40px;'

    if (ui.editor.graph.getModel().isVertex(cell) || ui.editor.graph.getModel().isEdge(cell)) {
        var replace = document.createElement('span');
        replace.style.marginRight = '10px';
        var input = document.createElement('input');
        input.setAttribute('type', 'checkbox');
        input.style.marginRight = '6px';

        if (value.getAttribute('placeholders') == '1') {
            input.setAttribute('checked', 'checked');
            input.defaultChecked = true;
        }

        mxEvent.addListener(input, 'click', function () {
            if (value.getAttribute('placeholders') == '1') {
                value.removeAttribute('placeholders');
            }
            else {
                value.setAttribute('placeholders', '1');
            }
        });

        replace.appendChild(input);
        mxUtils.write(replace, mxResources.get('placeholders'));

        if (EditDataDialog.placeholderHelpLink != null) {
            var link = document.createElement('a');
            link.setAttribute('href', EditDataDialog.placeholderHelpLink);
            link.setAttribute('title', mxResources.get('help'));
            link.setAttribute('target', '_blank');
            link.style.marginLeft = '8px';
            link.style.cursor = 'help';

            var icon = document.createElement('img');
            mxUtils.setOpacity(icon, 50);
            icon.style.height = '16px';
            icon.style.width = '16px';
            icon.setAttribute('border', '0');
            icon.setAttribute('valign', 'middle');
            icon.style.marginTop = (mxClient.IS_IE11) ? '0px' : '-4px';
            icon.setAttribute('src', Editor.helpImage);
            link.appendChild(icon);

            replace.appendChild(link);
        }

        buttons.appendChild(replace);
    }

    if (ui.editor.cancelFirst) {
        buttons.appendChild(cancelBtn);
        buttons.appendChild(applyBtn);
    }
    else {
        buttons.appendChild(applyBtn);
        buttons.appendChild(cancelBtn);
    }

    div.appendChild(buttons);
    this.container = div;
};


/**
 * Construct a reference dialog.
 *
 * It should be a very simple dialog with a title and a drop down menu
 * This allows to choose the reference for a variable using the drop down menu
 *
 * The drop down menu should contain all the variables in the model
 */
var ReferenceDialog = function (ui, cell) {
    var div = document.createElement('div');
    // Top level element
    var top = document.createElement('section');
    top.style.position = 'absolute';
    top.style.top = '30px';
    top.style.left = '30px';
    top.style.right = '30px';
    top.style.bottom = '80px';
    top.style.overflowY = 'auto';
    // create a title for top
    var topTitle = document.createElement('h3');
    topTitle.innerHTML = 'Reference to a Variable';
    top.appendChild(topTitle);


    // Adds a drop down menu to choose the referenced variable
    var select = document.createElement('select');

    // Get all the variables on the graph
    // TODO currently this only applies to the current page, we need to get all the variables in the model
    var variables = ui.editor.graph.getChildVertices(ui.editor.graph.getDefaultParent());

    // Add the variables to the drop down menu
    for (var i = 0; i < variables.length; i++) {
        var variable = variables[i];

        // continue the loop if the cell is not a pysd variable
        // look at the _pysd_type attribute
        if (variable.getAttribute('_pysd_type') == null || variable.getAttribute('_pysd_type') == 'Reference') {
            continue;
        }

        var option = document.createElement('option');
        option.innerHTML = variable.getAttribute('Name');
        select.appendChild(option);
        // If the cell has a attribute Name, then it is a pysd variable

    }
    // set the default value in the drop down menu
    // the default value is the current reference of the cell
    select.value = cell.getAttribute('Name');

    // add cancel and apply buttons
    var buttons = document.createElement('div');
    buttons.style.cssText = 'position:absolute;left:30px;right:30px;text-align:right;bottom:30px;height:40px;'
    var cancelBtn = mxUtils.button(mxResources.get('cancel'), function () {
        ui.hideDialog();
    });
    cancelBtn.className = 'geBtn';
    var applyBtn = mxUtils.button(mxResources.get('apply'), function () {
        // add the reference attribute to the cell
        // the value of the reference attribute is the name of the selected variable
        cell.setAttribute('Name', select.value);
        // update what is displayed in the cell
        ui.editor.graph.refresh(cell);
        // close the dialog
        ui.hideDialog();
    })
    applyBtn.className = 'geBtn gePrimaryBtn';


    buttons.appendChild(cancelBtn);
    buttons.appendChild(applyBtn);

    top.appendChild(buttons);

    // Add the drop down menu to the top element
    top.appendChild(select);
    div.appendChild(top);


    this.container = div;

};

// Checks when a cell is created
// TODO: this doesn't work at the moment
Draw.loadPlugin(function (ui) {
    // Attribute a name to newly created cells
    ui.editor.graph.addListener(mxEvent.CELLS_ADDED, function (cellsAdded) {
        for (var i = 0; i < cellsAdded.length; i++) {
            var cell = cellsAdded[i];
            // If the cell has a attribute Name, then it is a pysd variable
            if (cell.getAttribute('Name') != null) {
                // add a number at the end of the name if it already exists
                var name = cell.getAttribute('Name');
                var i = 1;
                while (ui.editor.graph.getModel().getCell(name) != null) {
                    name = cell.getAttribute('Name') + i;
                    i++;
                }
                // set the name of the cell
                cell.setId(name);
                cell.setAttribute('Name', name);
                // update the cell
                ui.editor.graph.refresh(cell);
            }
        }
    }
    );

});


// Checks when a cell is clicked
Draw.loadPlugin(function (ui) {

    var graph = ui.editor.graph;

    // Add a show equation dialog
    showEquationDialog = function (cell) {
        null != cell
            && (
                cell = new EquationDialog(ui, cell),
                // modal, closable, onClose, noScroll, transparent, onResize, ignoreBgClick
                ui.showDialog(cell.container, 480, 420, true, true, null, false, false, null, true),
                cell.init()
            )
    };
    // add a show reference dialog
    showReferenceDialog = function (cell) {
        null != cell
            && (
                cell = new ReferenceDialog(ui, cell),
                // modal, closable, onClose, noScroll, transparent, onResize, ignoreBgClick
                ui.showDialog(cell.container, 480, 420, true, true, null, false, false, null, true)
            )
    };

    function updateOverlays(cell) {
        if (cell != null) {
            // if the type of the cell is a refernce show the reference overlay
            if (cell.getAttribute('_pysd_type') == 'Reference') {
                showReferenceDialog(cell);
            } else {
                showEquationDialog(cell);
            }
        };
    };

    // Check the click handler
    var dblClick = ui.editor.graph.dblClick
    ui.editor.graph.dblClick = function (evt, cell) {
        // check if the cell is an edge for pysd
        if (cell != null && !graph.getModel().isEdge(cell) && cell.getAttribute('_pysd_type') != null) {
            updateOverlays(cell);
        } else {
            dblClick.apply(this, arguments);
        }
    };

});
