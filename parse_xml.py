import re
from xml.sax.handler import feature_namespaces
from xml.sax import make_parser
from pathlib import Path
from xml.sax.handler import ContentHandler
from pysd.translators.structures import abstract_expressions, abstract_model
from pysd.builders.python.python_model_builder import ModelBuilder

# re match variables that can contain spaces but they are always separated from each other by an operator or parenthesis
# The current code does not work with variables that contain spaces





def equation_2_ast(equation: str) -> abstract_expressions.ArithmeticStructure:
    """Convert the equation from the string to the abstract expression."""

    # Variables of the equations can contain spaces
    # Variables are always separated from each other by an operator
    # The operators are always separated from each other by a variable

    # We will read and translate the elements one by one
    # Get the first element
    # an element can be a variable, a number, a function, a parenthesis, an operator
    # variables can contain spaces but they are always separated from each other by an operator or parenthesis






exemple = "38.4 * (7625 +( 98.7 - j)) *(4)* (1 + ab Lol)"


def split_equation(equation: str) -> list[str]:
    """Split the equation in a list by removing parenthesis."""
    # split the equation in a list by removing parenthesis
    # but if parenthesis are inside other parenthesis, keep them
    # exemple = "38.4 * (7625 +( 98.7 - j)) * (1 + ab Lol)"
    # split_equation(exemple) = ['38.4 *', , '7625 + (98.7 - j)', '*', 1 + ab Lol']
    split_equation = []

    def collect_element(element: str) -> None:
        """Collect the element and add it to the list."""
        if element == "":
            return
        if element[0] == "(" and element[-1] == ")":
            element = element[1:-1]
        split_equation.append(element)

    parenthesis = 0
    current_element = ""
    for char in equation:
        if char == "(":
            parenthesis += 1
        elif char == ")":
            parenthesis -= 1
        # If element is an operator and it is not inside parenthesis
        # collect the current element and start a new one
        elif char in "+-*/" and parenthesis == 0:
            collect_element(current_element)
            current_element = ""
            split_equation.append(char)
            continue
        elif char == " " and parenthesis == 0:

            collect_element(current_element)
            current_element = ""
            continue
        current_element += char

    # If the current element is surrounded by parenthesis, remove them


    collect_element(current_element)
    return split_equation


print(split_equation(exemple))


print(equation_2_ast(exemple))
raise SystemExit()



class PysdElementsHandler(ContentHandler):
    def __init__(self):
        super().__init__()
        self.elements = []

    def startElementNS(self, name, qname, attrs):
        if name[1] == "UserObject":
            print(f"Name: {attrs.getValueByQName('Name')=}")
            print(f"Doc: {attrs.getValueByQName('Doc')=}")
            print(f"Units: {attrs.getValueByQName('Units')=}")
            print(f"_equation: {attrs.getValueByQName('_equation')=}")
            print(f"_pysd_type: {attrs.getValueByQName('_pysd_type')=}")
            self.create_element(attrs)

    def create_element(self, attrs):

        equation = attrs.getValueByQName('_equation')
        pysd_type = attrs.getValueByQName('_pysd_type')
        element = abstract_model.AbstractElement(
            name=attrs.getValueByQName('Name'),
            components=[abstract_model.AbstractComponent(
                subscripts=([], []),
                ast=self.create_ast(pysd_type, equation, attrs),
            )],
            documentation=attrs.getValueByQName('Doc'),
            units=attrs.getValueByQName('Units'),
        )
        self.elements.append(element)

    def create_ast(self, pysd_type, equation, attrs):
        match pysd_type:
            case "constant":
                return float(equation)
            case "IntegStructure":
                return abstract_expressions.IntegStructure(
                    initial=attrs.getValueByQName('_initial'),
                    flow=equation_2_ast(equation),
                )

            case _:
                raise NotImplementedError(f"pysd_type {pysd_type} not implemented")

parser = make_parser()
parser.setFeature(feature_namespaces, True)
elements_handler = PysdElementsHandler()
parser.setContentHandler(elements_handler)

file_path = Path("teacup.drawio.xml")
parser.parse(file_path)


model = abstract_model.AbstractModel(
    file_path,
    sections=(
        abstract_model.AbstractSection(
            name="__main__",
            path=file_path.with_suffix(".py"),
            type="main",
            params=[],
            returns=[],
            subscripts=[],
            elements=elements_handler.elements,
            split=False,
            views_dict=None,
        ),
    ),
)

ModelBuilder(model).build_model()
