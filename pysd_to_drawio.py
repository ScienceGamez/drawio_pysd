"""Convert an abstract model from pysd to a drawio model.

The sturcutre is adapted from the python builder.
"""
from __future__ import annotations


from functools import cache
from dataclasses import dataclass
import subprocess
from xml.dom import minidom
import warnings
from pathlib import Path
import numpy as np
from typing import List
from warnings import warn
from pathlib import Path


from pysd.translators.structures.abstract_model import (
    AbstractComponent,
    AbstractElement,
    AbstractControlElement,
    AbstractModel,
    AbstractSection,
)

from pysd._version import __version__


from pysd.translators.structures.abstract_model import AbstractSubscriptRange
from pysd.translators.structures import abstract_expressions
from pysd.py_backend.external import ExtSubscript

from parse_xml import generate_abstract_model

      
@dataclass
class CellGeometry:
    position: tuple(int, int)
    shape: tuple(int, int)

    def addAttributes(self, xml_root: minidom.Document) -> minidom.Element:
        mx_geometry = xml_root.createElement("mxGeometry")
        mx_geometry.setAttribute("x", str(self.position[0]))
        mx_geometry.setAttribute("y", str(self.position[1]))
        mx_geometry.setAttribute("width", str(self.shape[0]))
        mx_geometry.setAttribute("height", str(self.shape[1]))
        mx_geometry.setAttribute("as", "geometry")

        return mx_geometry



class ModelBuilder:
    """ModelBuilder allows building a PySD Draw.io model from the AbstractModel.

    Parameters
    ----------
    abstract_model: AbstractModel
        The abstract model to build.

    """
    original_path: Path
    sections: list[SectionBuilder]

    def __init__(self, abstract_model: AbstractModel):
        self.original_path = abstract_model.original_path
        # load sections
        self.sections = [SectionBuilder(section) for section in abstract_model.sections]

    def build_model(self) -> Path:
        """
        Build the Python model in a file callled as the orginal model
        but with '.drawio.xml' suffix.

        Returns
        -------
        path: pathlib.Path
            The path to the new PySD model.

        """
        for section in self.sections:
            # add macrospace information to each section and build it
            section.build_section()

        # return the path to the main file
        return self.sections[0].path


class SectionBuilder:
    """
    SectionBuilder allows building a section of the PySD model. Each
    section will be a file unless the model has been set to be split
    in modules.

    Parameters
    ----------
    abstract_section: AbstractSection
        The abstract section to build.

    """

    name: str
    path: Path
    xml_root: minidom.Document
    graph_root: minidom.Element

    def __init__(self, abstract_section: AbstractSection):
        self.__dict__ = abstract_section.__dict__.copy()
        self.root = self.path.parent  # the folder where the model is
        self.model_name = self.path.stem  # name of the model
        # Create subscript manager object with subscripts_dict
        self.subscripts = SubscriptManager(abstract_section.subscripts, self.root)
        # Load the elements in the section
        self.elements = [
            ElementBuilder(element, self) for element in abstract_section.elements
        ]

        # Create parameters dict necessary in macros
        self.params = {key: self.namespace.namespace[key] for key in self.params}

        self._init_xml()
        
        


    def _init_xml(self):
        # Create the document
        root = minidom.Document()
        self.xml_root = root
        mxfile = root.createElement("mxfile")
        root.appendChild(mxfile)

        diagram = root.createElement("diagram")
        diagram.setAttribute("id", f"pysd_drawio_section{self.name}")
        diagram.setAttribute("name", self.name)
        mxfile.appendChild(diagram)

        mxGraphModel = root.createElement("mxGraphModel")
        diagram.appendChild(mxGraphModel)

        self.graph_root = root.createElement("root")
        self.mxGraphModel = mxGraphModel

        # Add two cells that seem to always be there
        cell0 = root.createElement("mxCell")
        cell0.setAttribute("id", "0")
        cell1 = root.createElement("mxCell")
        cell1.setAttribute("id", "1")
        cell1.setAttribute("parent", "0")
        self.graph_root.appendChild(cell0)
        self.graph_root.appendChild(cell1)

    def build_section(self) -> None:
        """
        Build the Python section in a file callled as the orginal model
        if the section is main or in a file called as the macro name
        if the section is a macro.
        """
        if self.split:
            # Build modular section
            raise NotImplementedError("Only one file yet")
        else:
            # Build one-file section
            self._build()


    def _build(self) -> None:
        """
        Constructs and writes the drawio.xml representation of a section.

        Returns
        -------
        None

        """
            
        element_by_id: dict[str, ElementBuilder] = {}
        id_of_name: dict[str, str] = {}
        # Build elements
        for i, element in enumerate(self.elements):
            xml_element = element.build_element()

            # Make an id for the element
            element_id = f"pysddrawio-element-{i}"
            element_by_id[element_id] = element
            id_of_name[element.name] = element_id
            xml_element.setAttribute("id", element_id)

            # Add a cell for the graphics
            mx_cell = self.xml_root.createElement("mxCell")
            mx_cell.setAttribute("vertex", "1")
            mx_cell.setAttribute("parent", "1")



            geometry = CellGeometry((0, i * 100), (100, 50))

            
            mx_cell.appendChild(geometry.addAttributes(self.xml_root))
            xml_element.appendChild(mx_cell)
            self.graph_root.appendChild(xml_element)
        
        # Add the edges
        for id, element in element_by_id.items():
            for dep in set(element.dependencies):
                if dep not in id_of_name:
                    # Can be a function or other
                    continue
                edge = self.xml_root.createElement("mxCell")
                edge.setAttribute("id",  f"pysddrawio-edge-{id}-{dep}")
                edge.setAttribute("edge", "1")
                edge.setAttribute("parent", "1")
                edge.setAttribute("source", id_of_name[dep])
                edge.setAttribute("target", id)
                # add a geometry
                geometry = self.xml_root.createElement("mxGeometry")
                geometry.setAttribute("relative", "1")
                geometry.setAttribute("as", "geometry")
                edge.appendChild(geometry)

                self.graph_root.appendChild(edge)

                self.G.add_edge(dep, element.name)


        self.mxGraphModel.appendChild(self.graph_root)


        xml_str = self.xml_root.toprettyxml(indent="\t")

        with self.path.with_suffix(".drawio.xml").open("w", encoding="UTF-8") as out:
            out.write(xml_str)


class ElementBuilder:
    """
    ElementBuilder allows building an element of the PySD model.

    Parameters
    ----------
    abstract_element: AbstractElement
        The abstract element to build.
    section: SectionBuilder
        The section where the element is defined. Necessary to give the
        acces to the subscripts and namespace.

    """

    name: str
    components: List[AbstractComponent]
    units: str = ""
    limits: tuple = (None, None)
    documentation: str = ""

    xml_element: minidom.Element
    dependencies: list[str]


    def __init__(self, abstract_element: AbstractElement, section: SectionBuilder):
        self.__dict__ = abstract_element.__dict__.copy()
        self.control_var = isinstance(abstract_element, AbstractControlElement)
        # Set element type and subtype to None
        self.type = None
        self.subtype = None
        # Get the arguments of the element
        self.arguments = getattr(self.components[0], "arguments", "")
        # Load the components of the element
        self.section = section
        # Get the subscripts of the element after merging all the components
        self.subscripts = section.subscripts.make_merge_list(
            [component.subscripts[0] for component in self.components]
        )
        # Get the subscript dictionary of the element
        self.subs_dict = section.subscripts.make_coord_dict(self.subscripts)
        # Save dependencies and objects related to the element
        self.dependencies = []

        self.xml_attributes = {
            "label": "%Name%",
            "placeholders": "1",
            "Name": self.name,
            "Doc": self.documentation,
            "Unit": self.units,
        }

    def _parse_components(self):
        """
        Parse the components of the element.

        Returns
        -------
        None

        """
        for component in self.components:
            component.parse(self.section)

    @cache
    def parse_components(self):
        """
        Parse the components of the element.

        Returns
        -------
        None

        """
        if len(self.components) > 1:
            raise NotImplementedError()
        component = self.components[0]
        match component.ast:
            case int() | float():
                self.xml_attributes["_initial"] = self.ast_to_equation(component.ast)
            case  abstract_expressions.ArithmeticStructure():
                self.xml_attributes["_equation"] = self.ast_to_equation(component.ast)
            # case abstract_expressions.ReferenceStructure():
            #     var_name = component.ast.reference
            #     self.dependencies.append(var_name)
            #     # Add the egde to the graph
            #     self.section.G.add_edge(var_name, self.name)
            case abstract_expressions.IntegStructure():
                self.xml_attributes["_initial"] = self.ast_to_equation( component.ast.initial)
                self.xml_attributes["_equation"] = self.ast_to_equation( component.ast.flow)
                self.xml_attributes["_pysd_type"] = type(component.ast).__name__
            case abstract_expressions.ReferenceStructure():
                self.dependencies.append(component.ast.reference)

            case _:
                raise NotImplementedError(f"Component {component.ast} not implemented")

    def ast_to_equation(self, ast: abstract_expressions.ArithmeticStructure | abstract_expressions.ReferenceStructure | int | float) -> str:
        """Convert an ast to a string equation.
        
        This always return a string.
        It also add new dependencies when necessary.
        """

        match ast:
            case abstract_expressions.ArithmeticStructure():
                if len(ast.operators) == 1 and ast.operators[0] == "negative":
                    assert len(ast.arguments) == 1
                    return f"- {self.ast_to_equation(ast.arguments[0])}"

                assert len(ast.operators) == len(ast.arguments) - 1
                # put the operators in the middle of the arguments
                equation =  " ".join(
                    [
                        f"({self.ast_to_equation(arg)}) {op}"
                        if isinstance(arg, abstract_expressions.ArithmeticStructure)
                        else f"{self.ast_to_equation(arg)} {op}"
                        for arg, op in zip(ast.arguments, ast.operators)
                    ]
                )
                # Add the last argument
                return equation + f" {self.ast_to_equation(ast.arguments[-1])}"
            case int() | float():
                return str(ast)
            case abstract_expressions.ReferenceStructure():
                self.dependencies.append(ast.reference)
                return ast.reference
            case abstract_expressions.CallStructure():
                return f"{self.ast_to_equation(ast.function)}({', '.join(self.ast_to_equation(arg) for arg in ast.arguments)})"
            case _:
                raise NotImplementedError(f"ast_to_equation not implemented for {ast}")            

    def build_element(self) -> minidom.Element:
        """
        Build the element. Returns the string to include in the section which
        will be a decorated function definition and possible objects.
        """

        userobject_xml = self.section.xml_root.createElement("UserObject")

        self.parse_components()


        for key, value in self.xml_attributes.items():

            userobject_xml.setAttribute(key, str(value))

        


        return userobject_xml


class SubscriptManager:
    """
    SubscriptManager object allows saving the subscripts included in the
    Section, searching for elements or keys and simplifying them.

    Parameters
    ----------
    abstrac_subscripts: list
        List of the AbstractSubscriptRanges comming from the AbstractModel.

    _root: pathlib.Path
        Path to the model file. Needed to read subscript ranges from
        Excel files.

    """

    def __init__(self, abstract_subscripts: List[AbstractSubscriptRange], _root: Path):
        self._root = _root
        self._copied = []
        self.mapping = {}
        self.subscripts = abstract_subscripts
        self.elements = {}
        self.subranges = self._get_main_subscripts()
        self.subscript2num = self._get_subscript2num()

    @property
    def subscripts(self) -> dict:
        return self._subscripts

    @subscripts.setter
    def subscripts(self, abstract_subscripts: List[AbstractSubscriptRange]):
        self._subscripts = {}
        missing = []
        for sub in abstract_subscripts:
            self.mapping[sub.name] = sub.mapping
            if isinstance(sub.subscripts, list):
                # regular definition of subscripts
                self._subscripts[sub.name] = sub.subscripts
            elif isinstance(sub.subscripts, str):
                # copied subscripts, this will be always a subrange,
                # then we need to prevent them of being saved as a main range
                self._copied.append(sub.name)
                self.mapping[sub.name].append(sub.subscripts)
                if sub.subscripts in self._subscripts:
                    self._subscripts[sub.name] = self._subscripts[sub.subscripts]
                else:
                    missing.append(sub)
            elif isinstance(sub.subscripts, dict):
                # subscript from file
                self._subscripts[sub.name] = ExtSubscript(
                    file_name=sub.subscripts["file"],
                    sheet=sub.subscripts["tab"],
                    firstcell=sub.subscripts["firstcell"],
                    lastcell=sub.subscripts["lastcell"],
                    prefix=sub.subscripts["prefix"],
                    root=self._root,
                ).subscript
            else:
                raise ValueError(
                    f"Invalid definition of subscript '{sub.name}':\n\t"
                    + str(sub.subscripts)
                )

        while missing:
            # second loop for copied subscripts
            sub = missing.pop()
            self._subscripts[sub.name] = self._subscripts[sub.subscripts]

        subs2visit = self.subscripts.keys()
        while subs2visit:
            # third loop for subscripts defined with subranges
            updated = []
            for dim in subs2visit:
                if any(sub in self._subscripts for sub in self._subscripts[dim]):
                    # a subrange name is being used to define the range
                    # subscripts
                    updated.append(dim)
                    new_subs = []
                    for sub in self._subscripts[dim]:
                        if sub in self.subscripts:
                            # append the subscripts of the subrange
                            new_subs += self._subscripts[sub]
                        else:
                            # append the same subscript
                            new_subs.append(sub)
                    self._subscripts[dim] = new_subs
            # visit again the updated ranges as there could be several
            # levels of subranges
            subs2visit = updated.copy()

    def _get_main_subscripts(self) -> dict:
        """
        Reutrns a dictionary with the main ranges as keys and their
        subranges as values.
        """
        subscript_sets = {name: set(subs) for name, subs in self.subscripts.items()}

        subranges = {}
        for range, subs in subscript_sets.items():
            # current subscript range
            subranges[range] = []
            for subrange, subs2 in subscript_sets.items():
                if range == subrange:
                    # pass current range
                    continue
                elif subs == subs2:
                    # range is equal to the subrange, as Vensim does
                    # the main range will be the first one alphabetically
                    # make it case insensitive
                    range_l = range.replace(" ", "_").lower()
                    subrange_l = subrange.replace(" ", "_").lower()
                    if range_l < subrange_l and range not in self._copied:
                        subranges[range].append(subrange)
                    else:
                        # copied subscripts ranges or subscripts ranges
                        # that come later alphabetically
                        del subranges[range]
                        break
                elif subs2.issubset(subs):
                    # subrange is a subset of range, append it to the list
                    subranges[range].append(subrange)
                elif subs2.issuperset(subs):
                    # it exist a range that contents the elements of the range
                    del subranges[range]
                    break

        return subranges

    def _get_subscript2num(self) -> dict:
        """
        Build a dictionary to return the numeric value or values of a
        subscript or subscript range.
        """
        s2n = {}
        for range, subranges in self.subranges.items():
            # a main range is direct to return
            s2n[range.replace(" ", "_").lower()] = (
                f"np.arange(1, len(_subscript_dict['{range}'])+1)",
                {range: self.subscripts[range]},
            )
            for i, sub in enumerate(self.subscripts[range], start=1):
                # a subscript must return its numeric position
                # in the main range
                s2n[sub.replace(" ", "_").lower()] = (str(i), {})
            for subrange in subranges:
                # subranges may return the position of each subscript
                # in the main range
                sub_index = [
                    self.subscripts[range].index(sub) + 1
                    for sub in self.subscripts[subrange]
                ]

                if np.all(
                    sub_index == np.arange(sub_index[0], sub_index[0] + len(sub_index))
                ):
                    # subrange definition can be simplified with a range
                    subsarray = (
                        f"np.arange({sub_index[0]}, "
                        f"len(_subscript_dict['{subrange}'])+{sub_index[0]})"
                    )
                else:
                    # subrange definition cannot be simplified
                    subsarray = f"np.array({sub_index})"

                s2n[subrange.replace(" ", "_").lower()] = (
                    subsarray,
                    {subrange: self.subscripts[subrange]},
                )

        return s2n

    def _find_subscript_name(self, element: str, avoid: List[str] = []) -> str:
        """
        Given a member of a subscript family, return the first key of
        which the member is within the value list.

        Parameters
        ----------
        element: str
            Subscript or subscriptrange name to find.
        avoid: list (optional)
            List of subscripts to avoid. Default is an empty list.

        Returns
        -------
        name: str
            The first key of which the member is within the value list
            in the subscripts dictionary.

        Examples
        --------
        >>> sm = SubscriptManager([], Path(''))
        >>> sm._subscripts = {
        ...     'Dim1': ['A', 'B', 'C'],
        ...     'Dim2': ['A', 'B', 'C', 'D']}
        >>> sm._find_subscript_name('D')
        'Dim2'
        >>> sm._find_subscript_name('B')
        'Dim1'
        >>> sm._find_subscript_name('B', avoid=['Dim1'])
        'Dim2'

        """
        for name, elements in self.subscripts.items():
            if element in elements and name not in avoid:
                return name

    def make_coord_dict(self, subs: List[str]) -> dict:
        """
        This is for assisting with the lookup of a particular element.

        Parameters
        ----------
        subs: list of strings
            Coordinates, either as names of dimensions, or positions within
            a dimension.

        Returns
        -------
        coordinates: dict
            Coordinates needed to access the xarray quantities we are
            interested in.

        Examples
        --------
        >>> sm = SubscriptManager([], Path(''))
        >>> sm._subscripts = {
        ...     'Dim1': ['A', 'B', 'C'],
        ...     'Dim2': ['A', 'B', 'C', 'D']}
        >>> sm.make_coord_dict(['Dim1', 'D'])
        {'Dim1': ['A', 'B', 'C'], 'Dim2': ['D']}
        >>> sm.make_coord_dict(['A'])
        {'Dim1': ['A']}
        >>> sm.make_coord_dict(['A', 'B'])
        {'Dim1': ['A'], 'Dim2': ['B']}
        >>> sm.make_coord_dict(['A', 'Dim1'])
        {'Dim2': ['A'], 'Dim1': ['A', 'B', 'C']}

        """
        sub_elems_list = [y for x in self.subscripts.values() for y in x]
        coordinates = {}
        for sub in subs:
            if sub in sub_elems_list:
                name = self._find_subscript_name(sub, avoid=subs + list(coordinates))
                coordinates[name] = [sub]
            else:
                if sub.endswith("!"):
                    coordinates[sub] = self.subscripts[sub[:-1]]
                else:
                    coordinates[sub] = self.subscripts[sub]
        return coordinates

    def make_merge_list(
        self, subs_list: List[List[str]], element: str = ""
    ) -> List[str]:
        """
        This is for assisting when building xrmerge. From a list of subscript
        lists returns the final subscript list after merging. Necessary when
        merging variables with subscripts comming from different definitions.

        Parameters
        ----------
        subs_list: list of lists of strings
            Coordinates, either as names of dimensions, or positions within
            a dimension.
        element: str (optional)
            Element name, if given it will be printed with any error or
            warning message. Default is "".

        Returns
        -------
        dims: list
            Final subscripts after merging.

        Examples
        --------
        >>> sm = SubscriptManager([], Path(''))
        >>> sm._subscripts = {"upper": ["A", "B"], "all": ["A", "B", "C"]}
        >>> sm.make_merge_list([['A'], ['B']])
        ['upper']
        >>> sm.make_merge_list([['A'], ['B'], ['C']])
        ['all']
        >>> sm.make_merge_list([['upper'], ['C']])
        ['all']
        >>> sm.make_merge_list([['A'], ['C']])
        ['all']

        """
        coords_set = [set() for i in range(len(subs_list[0]))]
        coords_list = [self.make_coord_dict(subs) for subs in subs_list]

        # update coords set
        [
            [coords_set[i].update(coords[dim]) for i, dim in enumerate(coords)]
            for coords in coords_list
        ]

        dims = [None] * len(coords_set)
        # create an array with the name of the subranges for all
        # merging elements
        dims_list = np.array([list(coords) for coords in coords_list]).transpose()
        indexes = np.arange(len(dims))

        for i, coord2 in enumerate(coords_set):
            dims1 = [
                dim
                for dim in dims_list[i]
                if dim is not None and set(self.subscripts[dim]) == coord2
            ]
            if dims1:
                # if the given coordinate already matches return it
                dims[i] = dims1[0]
            else:
                # find a suitable coordinate
                other_dims = dims_list[indexes != i]
                for name, elements in self.subscripts.items():
                    if coord2 == set(elements) and name not in other_dims:
                        dims[i] = name
                        break

                if not dims[i]:
                    # the dimension is incomplete use the smaller
                    # dimension that completes it
                    for name, elements in self.subscripts.items():
                        if coord2.issubset(set(elements)) and name not in other_dims:
                            dims[i] = name
                            warnings.warn(
                                element
                                + "\nDimension given by subscripts:"
                                + "\n\t{}\nis incomplete ".format(coord2)
                                + "using {} instead.".format(name)
                                + "\nSubscript_dict:"
                                + "\n\t{}".format(self.subscripts)
                            )
                            break

                if not dims[i]:
                    for name, elements in self.subscripts.items():
                        if coord2 == set(elements):
                            j = 1
                            while name + str(j) in self.subscripts.keys():
                                j += 1
                            self.subscripts[name + str(j)] = elements
                            dims[i] = name + str(j)
                            warnings.warn(
                                element
                                + "\nAdding new subscript range to"
                                + " subscript_dict:\n"
                                + name
                                + str(j)
                                + ": "
                                + ", ".join(elements)
                            )
                            break

        return dims

    def simplify_subscript_input(
        self, coords: dict, merge_subs: List[str] = None
    ) -> tuple:
        """
        Simplifies the subscripts input to avoid printing the coordinates
        list when the _subscript_dict can be used. Makes model code more
        simple.

        Parameters
        ----------
        coords: dict
            Coordinates to write in the model file.

        merge_subs: list of strings or None (optional)
            List of the final subscript range of the Python array after
            merging with other objects. If None the merge_subs will be
            taken from coords. Default is None.

        Returns
        -------
        final_subs, coords: dict, str
            Final subscripts and the equations to generate the coord
            dicttionary in the model file.

        Examples
        --------
        >>> sm = SubscriptManager([], Path(''))
        >>> sm._subscripts = {
        ...     "dim": ["A", "B", "C"],
        ...     "dim2": ["A", "B", "C", "D"]}
        >>> sm.simplify_subscript_input({"dim": ["A", "B", "C"]})
        ({"dim": ["A", "B", "C"]}, "{'dim': _subscript_dict['dim']}"
        >>> sm.simplify_subscript_input({"dim": ["A", "B", "C"]}, ["dim2"])
        ({"dim2": ["A", "B", "C"]}, "{'dim2': _subscript_dict['dim']}"
        >>> sm.simplify_subscript_input({"dim": ["A", "B"]})
        ({"dim": ["A", "B"]}, "{'dim': ['A', 'B']}"

        """
        if merge_subs is None:
            merge_subs = list(coords)

        coordsp = []
        final_subs = {}
        for ndim, (dim, coord) in zip(merge_subs, coords.items()):
            # find dimensions can be retrieved from _subscript_dict
            final_subs[ndim] = coord
            if not dim.endswith("!") and coord == self.subscripts[dim]:
                # use _subscript_dict
                coordsp.append(f"'{ndim}': _subscript_dict['{dim}']")
            else:
                # write whole dict
                coordsp.append(f"'{ndim}': {coord}")

        return final_subs, "{" + ", ".join(coordsp) + "}"


if __name__ == "__main__":



    from examples.ghg_abstract import model as abs_model
    #abs_model = generate_abstract_model("examples/teacup.drawio.xml")


    # save the abs model to a file
    abs_fname = abs_model.original_path.with_suffix('.xmlabs')
    with open(abs_fname, "w", encoding="UTF-8") as f:
        f.write(repr(abs_model))
        # format with black 
    subprocess.run(["black", str(abs_fname)])

    m = ModelBuilder(abs_model)
    m.sections[0].path = m.sections[0].path.with_stem("generated")
    print(m.build_model())
