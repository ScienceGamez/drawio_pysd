"""Parsing xml produced by draw.io to create a PySD model."""
import argparse
from datetime import datetime
import logging
from os import PathLike
import subprocess

from typing import NewType
from xml.sax.handler import feature_namespaces
from xml.sax import make_parser
from pathlib import Path
from xml.sax.handler import ContentHandler
import pysd
from pysd.translators.structures import abstract_expressions, abstract_model
from pysd.builders.python.python_model_builder import ModelBuilder


from drawio_pysd.equations_parsing import equation_2_ast, var_name_to_safe_name
from drawio_pysd.custom_asts import LinearDependencyStructure


ElementId = NewType("ElementId", str)


class PysdElementsHandler(ContentHandler):
    """Content handler for the xml file from drawio."""

    subscripts: dict[ElementId, abstract_model.AbstractSubscriptRange]
    elements: dict[ElementId, abstract_model.AbstractElement]
    references: dict[ElementId, str]
    connexions: list[tuple[ElementId, ElementId]]
    safe_names: dict[str, ElementId]

    def __init__(self):
        super().__init__()
        self.elements = {}
        self.subscripts = {}
        self.connexions = []
        self.references = {}
        self.safe_names = {}

    def startElementNS(self, name, qname, attrs):
        """Start reading a element from the xml."""
        match name[1]:
            case "UserObject":
                # User objects are the general cells from drawio dedicated to PySD
                self.create_element(attrs)
            case "mxCell":
                try:
                    # These are other cells or edges
                    is_edge = bool(int(attrs.getValueByQName("edge")))
                except KeyError:
                    try:
                        # These are other cells or edges
                        is_edge = not bool(int(attrs.getValueByQName("vertex")))
                    except KeyError:
                        is_edge = False
                if is_edge:
                    self.process_mxCell_edge(attrs)
                else:
                    self.process_mxCell_vertex(attrs)

    def process_mxCell_edge(self, attrs):
        """Process the mxCell edges.

        edges connect elements
        """
        try:
            source = attrs.getValueByQName("source")
            target = attrs.getValueByQName("target")
            self.connexions.append((source, target))
        except KeyError:
            pass

    def process_mxCell_vertex(self, attrs):
        """Process the mxCell vertices.

        vertices can be parts of subscripts (values of the subscripts)
        """
        try:
            parent = attrs.getValueByQName("parent")
            if parent in self.subscripts:
                self.subscripts[parent].subscripts.append(
                    attrs.getValueByQName("value")
                )
        except KeyError:
            pass

    def create_element(self, attrs):
        """Create an element from the xml attributes."""

        name = attrs.getValueByQName("Name").strip()
        try:
            equation = attrs.getValueByQName("_equation")
        except KeyError:
            equation = ""
        # Check if a key is in the attrs
        try:
            pysd_type = attrs.getValueByQName("_pysd_type")
        except KeyError:
            pysd_type = "AbstractElement"

        id = attrs.getValueByQName("id")

        if pysd_type == "Reference":
            # Reference dont have ast but they have to point to
            # the correct element
            self.references[id] = name
            return

        try:
            ast = self.create_ast(pysd_type, equation, attrs)
            if ast is None:
                return
        except Exception as exp:
            raise ValueError(
                f"Error while creating the abstract structure"
                f" for '{pysd_type}: {name}': {exp}"
            ) from exp

        if isinstance(ast, abstract_model.AbstractSubscriptRange):
            self.subscripts[id] = ast
            return

        try:
            units = attrs.getValueByQName("Units")
        except KeyError:
            units = ""
        try:
            doc = attrs.getValueByQName("Doc")
        except KeyError:
            doc = ""

        # Check that the name is unique in safe_name space
        safe_name = var_name_to_safe_name(name)
        if safe_name in self.safe_names:
            raise ValueError(
                f"Variables '{name}' and '{self.safe_names[safe_name]}' "
                f"have the same safe name '{safe_name}'.\n"
                "Please change one of the names."
            )
        self.safe_names[safe_name] = name

        element = abstract_model.AbstractElement(
            name=name,
            components=[
                abstract_model.AbstractComponent(
                    subscripts=([], []),
                    ast=ast,
                )
            ],
            documentation=doc,
            units=units,
        )
        self.elements[id] = element

    def create_ast(self, pysd_type, equation, attrs):
        match pysd_type:
            case "IntegStructure":
                return abstract_expressions.IntegStructure(
                    initial=equation_2_ast(attrs.getValueByQName("_initial")),
                    flow=equation_2_ast(equation),
                )
            case "AbstractElement" | "AbstractComponent":
                return equation_2_ast(equation)
            case "AbstractUnchangeableConstant" | "ControlVar":
                return float(attrs.getValueByQName("_initial"))
            case "Subscript":
                ast = abstract_model.AbstractSubscriptRange(
                    name=attrs.getValueByQName("Name"), subscripts=[], mapping=[]
                )

                return ast
            case "LinearDependencyStructure":
                return LinearDependencyStructure(
                    initial=equation_2_ast(attrs.getValueByQName("_initial")),
                    variable=equation_2_ast(equation),
                )
            case "Sink":
                return None
            case _:
                raise NotImplementedError(f"pysd_type '{pysd_type}' not implemented.")

    def _add_subscripts_from_connexions(self):
        """Add the subscripts to the elements based on the connexions."""
        for source, target in self.connexions:
            if source in self.subscripts and target in self.elements:
                for c in self.elements[target].components:
                    c.subscripts[0].append(self.subscripts[source].name)

    def post_parsing(self):
        """Modify some elements after the parsing.

        Must be called after the parsing.
        """
        # create a mapping variable name -> id
        # to replace the references
        mapping = {v.name: k for k, v in self.elements.items()}

        # replaces references in the connexions
        for i, (source, target) in enumerate(self.connexions):
            if source in self.references:
                self.connexions[i] = (mapping[self.references[source]], target)
            if target in self.references:
                self.connexions[i] = (source, mapping[self.references[target]])

        self._add_subscripts_from_connexions()


def generate_abstract_model(file_path: PathLike) -> abstract_model.AbstractModel:
    """Generate an abstract model from the drawio file."""

    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"{file_path}")

    # Create the xml parser
    parser = make_parser()
    parser.setFeature(feature_namespaces, True)
    elements_handler = PysdElementsHandler()
    parser.setContentHandler(elements_handler)

    parser.parse(file_path)

    elements_handler.post_parsing()

    model = abstract_model.AbstractModel(
        file_path,
        sections=(
            abstract_model.AbstractSection(
                name="__main__",
                path=file_path.with_suffix(".py"),
                type="main",
                params=[],
                returns=[],
                subscripts=list(elements_handler.subscripts.values()),
                elements=list(elements_handler.elements.values()),
                constraints=(),
                test_inputs=(),
                split=False,
                views_dict=None,
            ),
        ),
    )

    return model


if __name__ == "__main__":
    # Create an argument reader with one single argument being the path of the file
    arg_parser = argparse.ArgumentParser()
    # Add the docstring of this py file as the description of the argument parser
    arg_parser.description = __doc__
    arg_parser.add_argument("file_path", type=str, help="Path of the file to parse")
    # Add a run option to run the file only if selected
    arg_parser.add_argument(
        "--run", action="store_true", help="Run the file after parsing it"
    )
    # Add argument 'abs' to save the abstract model
    arg_parser.add_argument(
        "--abs", action="store_true", help="Save the abstract model"
    )
    # Add log and debug options
    arg_parser.add_argument(
        "-d",
        "--debug",
        help="Debugging statements",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    arg_parser.add_argument(
        "-v",
        "--verbose",
        "--info",
        help="Write out the output",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    # Add a plot parameters which arguments will be plotted
    arg_parser.add_argument(
        "-p",
        "--plot",
        nargs="+",
        type=str,
        default=[],
        help="Plot parameters",
        dest="plot_params",
        action="append",
    )

    args = arg_parser.parse_args()

    # Set the logging value
    logging.basicConfig()
    logger = logging.getLogger("drawio_pysd")
    logger.setLevel(args.loglevel)
    logger.debug(args)

    file_path = Path(args.file_path)

    model = generate_abstract_model(file_path)

    print(f"File {file_path} parsed and successfully converted to {model}")

    if args.abs:
        abs_file = file_path.with_name(file_path.name + ".abs")
        with open(abs_file, "w", encoding="utf-8") as f:
            # add a header to explain what is in the file
            f.write(
                f"# This file contains the PySD abstract model of the file {file_path}\n"
            )
            # add creation date and time
            f.write(f"# Created on {datetime.now()}\n")
            f.write(str(model.sections))
        # format the file calling black
        # TODO: call directly the black API instead of calling it as a subprocess
        subprocess.run(["black", abs_file])

    py_file = ModelBuilder(model).build_model()

    print(f"File {file_path} parsed and successfully converted to {py_file}")

    if args.run:
        model = pysd.load(py_file)
        results_df = model.run()
        if args.plot_params:

            # Plot all the variables in the results
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots()
            x = results_df.index
            for param_list in args.plot_params:
                for param in param_list:
                    if param not in results_df.columns:
                        logger.warning(f'Parameter {param} not in the simulation outputs')
                        continue
                    ax.plot(x, results_df[param], label=f"{param}")
            # Supress the last created ax that is useless
            ax.legend()
            plt.show()
    else:
        if args.plot_params:
            logger.warning(
                "Cannot plot if the model is not run, add --run in the command line args"
            )
