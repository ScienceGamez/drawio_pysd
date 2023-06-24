"""Contains my custom made ASTs for PySD"""
from typing import Union, Optional
from dataclasses import dataclass

import xarray as xr

from pysd.translators.structures.abstract_expressions import AbstractSyntax
from pysd.builders.python.python_expressions_builder import StructureBuilder, BuildAST, ASTVisitor
from pysd.builders.python.imports import ImportsManager

from pysd.py_backend.statefuls import Stateful


class LinearDependency(Stateful):
    """
    Implements LinearDependency function.

    Parameters
    ----------
    initial_value: callable
        Initial value this function should give.
    dependent_variable: callable
        The variable on which this depends.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: float or xarray.DataArray
        Current state of the object. Value of the stock.

    """
    def __init__(self, initial_value, dependent_variable, py_name):
        super().__init__()
        self.init_func = initial_value
        self.variable_func = dependent_variable


        self.shape_info = None
        self.py_name = py_name

    def initialize(self, init_val=None):

        if init_val is None:
            init_val = self.init_func() 

        # Get ratio from the intial conditions
        self._ratio = init_val / self.variable_func()
        self.state = self._ratio * self.variable_func()

        if isinstance(self.state, xr.DataArray):
            self.shape_info = {'dims': self.state.dims,
                               'coords': self.state.coords}
            
    def __call__(self):
        self.state = self._ratio * self.variable_func()
        return self.state

    def export(self):
        return {'state': self.state, 'ratio': self._ratio, 'shape_info': self.shape_info}


@dataclass
class LinearDependencyStructure(AbstractSyntax):
    """
    Dataclass for a linear dependency structure.

    A linear dependency structure is simply a linear function of another parameter.

    :math:`y = r * x`

    However sometimes the r parameter is not known, but can be calculated based 
    on the initial conditions: :math:`y_0 = r * x_0 \Rightarrow r = y_0 / x_0`

    Parameters
    ----------
    flow: AST
        The flow of the stock.
    initial: AST
        The initial value of the stock.
    non_negative: bool (optional)
        If True the stock cannot be negative. Default is False.

    """
    initial: Union[AbstractSyntax, float]
    variable: Union[AbstractSyntax, str]

    def __str__(self) -> str:  # pragma: no cover
        return "LinearDependencyStructure:\n\t%s,\n\t%s" % (
            self.initial,
            self.variable)
    

class LinearDependencyBuilder(StructureBuilder):
    """Builder for LinearDependencyStructure."""
    def __init__(self, lin_str: LinearDependencyStructure, component: object):
        super().__init__(None, component)
        self.arguments = {
            "variable": lin_str.variable,
            "initial": lin_str.initial
        }

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        print(arguments)
        self.component.type = "Auxiliary"
        self.component.subtype = "LinearDependency"

        arguments["initial"].reshape(
            self.section.subscripts, self.def_subs, True)
        arguments["variable"].reshape(
            self.section.subscripts, self.def_subs, True)


        arguments["name"] = self.section.namespace.make_python_identifier(
            self.element.identifier, prefix="_linear_dep")

        # Create the object

        # Regular stocks
        self.section.imports.add("drawio_pysd", "LinearDependency")
        self.element.objects[arguments["name"]] = {
            "name": arguments["name"],
            "expression": "%(name)s = LinearDependency(initial_value=lambda: %(initial)s, "
                            "dependent_variable=lambda: %(variable)s, py_name='%(name)s')" % arguments
        }

        # Add other dependencies
        self.element.other_dependencies[arguments["name"]] = {
            "initial": arguments["initial"].calls,
            "step": arguments["variable"].calls
        }

        return BuildAST(
            expression=arguments["name"] + "()",
            calls={arguments["name"]: 1},
            subscripts=self.def_subs,
            order=0)


# Add this to the builders 
ASTVisitor._builders[LinearDependencyStructure] = LinearDependencyBuilder

ImportsManager._external_submodules.append('drawio_pysd')
ImportsManager._drawio_pysd = set()