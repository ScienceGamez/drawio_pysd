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

	function createPysdCell() {
		var cell = new mxCell('%Name%', new mxGeometry(0, 0, 80, 20), 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;overflow=hidden;');
		cell.vertex = true;
		ui.sidebar.graph.setAttributeForCell(cell, 'placeholders', '1');
		ui.sidebar.graph.setAttributeForCell(cell, 'Name', 'new_variable');
		ui.sidebar.graph.setAttributeForCell(cell, 'Doc', '');
		ui.sidebar.graph.setAttributeForCell(cell, 'Units', '-');
		return cell;
	}
	var template_cell = createPysdCell();

	// Sidebar is null in lightbox
	if (ui.sidebar != null) {
		var fns = [
			ui.sidebar.createVertexTemplateEntry('shape=image;image=https://raw.githubusercontent.com/SDXorg/pysd/master/docs/images/PySD_Logo.svg;editable=0;resizable=1;movable=1;rotatable=0', 100, 100, '', 'PySD Logo', null, null, 'text heading title'),
			ui.sidebar.addEntry('pysd template', mxUtils.bind(ui.sidebar, function () {
				var cell = createPysdCell();
				return ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, 'Variable');
			})),
			//ui.sidebar.createVertexTemplateFromCells([createPysdCell()], cell.geometry.width, cell.geometry.height, 'Variable'),
		]
		ui.sidebar.addPaletteFunctions('pysd', 'PySD', true, fns)
		// Adds custom sidebar entry
		// ui.sidebar.addPalette('pysd', 'PySD', true, function (content) {

		// 	// content.appendChild(ui.sidebar.createVertexTemplate(null, 120, 60 ));

		// 	content.appendChild(ui.sidebar.addEntry('variable placeholder metadata pysd', mxUtils.bind(ui.sidebar, function () {
		// 		var cell = new mxCell('%Name%', new mxGeometry(0, 0, 80, 20), 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;overflow=hidden;');
		// 		cell.vertex = true;
		// 		ui.sidebar.graph.setAttributeForCell(cell, 'placeholders', '1');
		// 		ui.sidebar.graph.setAttributeForCell(cell, 'Name', '<new_variable>');
		// 		ui.sidebar.graph.setAttributeForCell(cell, 'Doc', '');
		// 		return ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, 'PySD Element');
		// 	})))
		// 	var cell = new mxCell('%Name%', new mxGeometry(0, 0, 80, 20), '');
		// 	content.appendChild(ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, 'PySD Element'));

		// 	var template_element = ui.sidebar.createVertexTemplate('', 120, 60, '%Name%', 'PySD Template Element');
		// 	// content.setAttributeForCell('placeholders', '1');
		// 	// content.setAttributeForCell('Name', '<new_variable>');
		// 	content.appendChild(template_element);
		// 	var integ = ui.sidebar.createVertexTemplate('', 120, 60, '<integ2>', 'Integ');
		// 	content.appendChild(integ);
		// 	content.appendChild(ui.sidebar.createVertexTemplate('text;', 120, 60, '<constant>', 'Constant'));
		//
		// 	content.appendChild(ui.sidebar.createVertexTemplate('text;spacingTop=-5;fontFamily=Courier New;fontSize=8;fontColor=#999999;resizable=0;movable=0;rotatable=0', 100, 100));
		// 	content.appendChild(ui.sidebar.createVertexTemplate('rounded=1;whiteSpace=wrap;gradientColor=none;fillColor=#004C99;shadow=1;strokeColor=#FFFFFF;align=center;fontColor=#FFFFFF;strokeWidth=3;fontFamily=Courier New;verticalAlign=middle', 100, 100));
		// 	content.appendChild(ui.sidebar.createVertexTemplate('curved=1;strokeColor=#004C99;endArrow=oval;endFill=0;strokeWidth=3;shadow=1;dashed=1', 100, 100));
		// });

		// Collapses default sidebar entry and inserts this before
		var c = ui.sidebar.container;
		c.firstChild.click();
		c.insertBefore(c.lastChild, c.firstChild);
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

// Keep int track all the variables and their elements
var variables_dict = {};
Draw.loadPlugin(function (ui) {

});
/**
 * Constructs a new equation dialog.
 * This is taken from drawio EditDataDialog and moodi
 */
var EquationDialog = function (ui, cell) {
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

	var variablesForm = new mxForm('properties');
	variablesForm.table.style.width = '100%';

	var attrs = value.attributes;
	var names = [];
	var texts = [];
	var count = 0;
	var variable_names = [];
	var variable_texts = [];
	var variable_count = 0;

	var id = (EditDataDialog.getDisplayIdForCell != null) ?
		EditDataDialog.getDisplayIdForCell(ui, cell) : null;

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

	// area containing the the variables
	var addVariables = function (index, cell) {
		// TODO change that and make buttons instead
		var name = cell.getAttribute('Name', 'new_variable');
		var value = cell.getAttribute('Name', 'new_variable');
		variable_names[index] = name;
		variable_texts[index] = variablesForm.addTextarea(variable_names[variable_count] + ':', value, 2);
		variable_texts[index].style.width = '100%';

		if (value.indexOf('\n') > 0) {
			variable_texts[index].setAttribute('rows', '2');
		}

		// addRemoveButton(variable_texts[index], name, variablesForm);

		if (meta[name] != null && meta[name].editable == false) {
			variable_texts[index].setAttribute('disabled', 'disabled');
		}
	};

	var temp = [];
	var isLayer = graph.getModel().getParent(cell) == graph.getModel().getRoot();

	for (var i = 0; i < attrs.length; i++) {
		if ((attrs[i].nodeName != 'label' || Graph.translateDiagram ||
			isLayer) && attrs[i].nodeName != 'placeholders') {
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
		}); */

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

	for (var i = 0; i < temp.length; i++) {
		mxLog.info("asdf");
		addTextArea(count, temp[i].name, temp[i].value);
		count++;
	}

	function getChildrenOfCell(cell){
		if(cell != undefined){
			let children = [];
			let edges = cell.edges;
			if(edges != null){
				for(let i = 0; i < edges.length; i++){
					if(edges[i].target.value == cell.value){
						let cellCopy = edges[i].source.clone();
						children.push(cellCopy);
					}
				}
			}
			return children;
		}
		else{
			return [];
		}
		}

	var parents = getChildrenOfCell(cell);

	for (var i = 0; i < parents.length; i++) {
		addVariables(variable_count, parents[i]);
		variable_count++;
	}


	var top = document.createElement('section');
	top.style.position = 'absolute';
	top.style.top = '30px';
	top.style.left = '30px';
	top.style.right = '30px';
	top.style.bottom = '80px';
	top.style.overflowY = 'auto';

	top.appendChild(propertiesForm.table);
	top.appendChild(variablesForm.table);

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

// Checks when a cell is clicked
Draw.loadPlugin(function (ui) {

	var graph = ui.editor.graph;

	// Add a show equation dialog
	ui.showEquationDialog = function (cell) {
		null != cell
			&& (
				cell = new EquationDialog(this, cell),
				// modal, closable, onClose, noScroll, transparent, onResize, ignoreBgClick
				this.showDialog(cell.container, 480, 420, true, true, null, false, false, null, true),
				cell.init()
			)
	};

	function updateOverlays(cell) {
		if (cell != null) {
			ui.showEquationDialog(cell);


		}
	};

	// Check the click handler
	var dblClick = ui.editor.graph.dblClick
	ui.editor.graph.dblClick = function (evt, cell) {
		if (cell != null) {
			updateOverlays(cell);
		} else {
			dblClick.apply(this, arguments);
		}
	};

});
