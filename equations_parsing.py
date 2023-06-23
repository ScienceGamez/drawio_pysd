"""Code to parse equations from drawio files."""

import re
import logging

from pysd.translators.structures import abstract_expressions


logger = logging.getLogger("drawio_pysd.equations_parsing")

_operators_precedence = {
    "^": 4,
    "*": 3,
    "/": 3,
    "+": 2,
    "-": 2,
}


def var_name_to_safe_name(var_name: str) -> str:
    """Convert a variable name to a safe name for pysd.

    This should not be necessary if one would argue that each model
    builder would be responsible for making the names safe.

    But PySD people did not want to do that:
    https://github.com/SDXorg/pysd/pull/399

    So now the abstract model has variable names and 'safe' names in
    the reference structures.
    """

    # Replace spaces with underscores and lower
    safe_name = var_name.strip().replace(" ", "_").lower()

    return safe_name


def equation_2_ast(equation: str) -> abstract_expressions.ArithmeticStructure:
    """Convert the equation from the string to the abstract expression."""

    # Variables of the equations can contain spaces
    # Variables are always separated from each other by an operator
    # The operators are always separated from each other by a variable

    # We will read and translate the elements one by one
    # Get the first element
    # an element can be a variable, a number, a function, a parenthesis, an operator
    # variables can contain spaces but they are always separated from each other by an operator or parenthesis

    logger.debug(f"equation_2_ast({equation})")
    splitted = split_equation(equation)
    logger.debug(f"equation_2_ast({splitted=})")

    if len(splitted) == 0:
        raise ValueError("Equation is empty")
    if len(splitted) == 1:
        # IF the equation is a number, return the number
        if re.match(r"^\d+(\.\d+)?$", splitted[0]):
            return float(splitted[0])
        # Try number with e
        elif re.match(r"^\d+(\.\d+)?e\d+$", splitted[0]):
            return float(splitted[0])
        # number with no digit after the dot
        elif re.match(r"^\d+\.$", splitted[0]):
            return float(splitted[0])
        # If the equation is a variable, return the variable
        elif re.match(r"^[a-zA-Z_][a-zA-Z0-9_ ]*$", splitted[0]):
            # Need to replace spaces by uderscores
            safe_var = var_name_to_safe_name(splitted[0])
            return abstract_expressions.ReferenceStructure(safe_var)
        # If the equation is a function, return the function
        # inside the function parenthesis, there can be anything, also special characters
        elif re.match(
            r"^[a-zA-Z_][a-zA-Z0-9_ ]*\([a-zA-Z0-9_*_ _\-_/_^()+,]*\)$", splitted[0]
        ):
            # Get the function name
            function_name = splitted[0].split("(")[0]
            remaining = "(".join(splitted[0].split("(")[1:])
            # Take only what is inside the parenthesis
            inside_parenthesis = remaining.split(")")
            if len(inside_parenthesis) > 1:
                inside_parenthesis = ")".join(inside_parenthesis[:-1])
            else:
                inside_parenthesis = inside_parenthesis[0]
            # Get the arguments
            arguments = inside_parenthesis.split(",")
            logger.debug(f"equation_2_ast({function_name=}, {arguments=})")
            # Return the function
            return abstract_expressions.CallStructure(
                abstract_expressions.ReferenceStructure(function_name),
                arguments=[equation_2_ast(arg) for arg in arguments if arg],
            )
        else:
            raise ValueError(f"Equation '{equation}' is not valid")

    # Now that we have split around operators we can add the variables
    # in an arithmetic structure

    # If the equation starts with a negative sign, return a negative structure
    if splitted[0] == "-":
        return abstract_expressions.ArithmeticStructure(
            operators=["negative"], arguments=(equation_2_ast(splitted[1:]),)
        )

    # Check that the splitted element lenght is odd
    if len(splitted) % 2 == 0:
        raise ValueError(f"Equation {equation} is not valid")

    operators = splitted[1::2]
    elements = splitted[::2]

    # Check that all the operators have the same precedence
    # Check all operatores are registerd
    for op in operators:
        if op not in _operators_precedence:
            raise ValueError(
                f"Operator {op} is not valid, only {_operators_precedence.keys()} are valid"
            )
    precedences = [_operators_precedence[op] for op in operators]

    if all(precedences[0] == prec for prec in precedences):
        return abstract_expressions.ArithmeticStructure(
            # operators are the odd elements
            operators=operators,
            arguments=[equation_2_ast(el) for el in elements],
        )
    
    # If not all operators have the same precedence, we need to goup the equation
    # we split at the max precedence operator

    idx_max = precedences.index(max(precedences))

    # Create a new equation which will ensure the precedence is respected
    # and splitted, using parenthesis
    equation = ""
    for i in range(len(operators)):
        if i == idx_max or (i==0 and idx_max == 0):
            # Add parenthesis for precedence at the most precendence operator
            equation += "("
        equation += f"({elements[i]})"
        if i == idx_max + 1: 
            equation += ")"
        equation += operators[i]

    equation += f"({elements[-1]})"
    if idx_max == len(operators) - 1:
        equation += ")"

    return equation_2_ast(equation)
        

    



def split_equation(equation: str) -> list[str]:
    """Split the equation in a list by removing parenthesis."""
    # split the equation in a list by removing parenthesis
    # but if parenthesis are inside other parenthesis, keep them
    # This should make sure to remove spaces or parenthesis around the
    # list elements it returns
    # exemple = "38.4 * (7625 +(98.7 - j)) * (1 + ab Lol)"
    # split_equation(exemple) = ['38.4', '*' , '7625 +(98.7 - j)', '*', '1 + ab Lol']
    # example2 = "1 + ab Lol"
    # split_equation(example2) = ['1', '+', 'ab Lol']

    elements = []
    parenthesis = 0
    element = ""

    for char in equation:
        # logger.debug(f"split_equation: {char=}, {element=}")
        if char == "(":
            parenthesis += 1
            element += char

        elif char == ")":
            parenthesis -= 1
            element += char

        elif char in ["+", "-", "*", "/", "^"] and parenthesis == 0:
            # If the parenthesis are closed and the char is an operator, we are at the end of an element
            # Add the element to the list
            elements.append(element.strip())
            # Reset the element
            element = ""
            # Add the operator to the list
            elements.append(char)

        else:
            # If the parenthesis are not closed or the char is not an operator, we are still in the same element
            # Add the char to the element
            element += char

    # Add the last element
    elements.append(element.strip())

    logger.debug(f"split_equation: {elements=}")

    # Remove empty elements
    # If an element is surrounded by parenthesis, remove the parenthesis
    return [
        element[1:-1] if element[0] == "(" and element[-1] == ")" else element
        for element in elements
        if element != ""
    ]


if __name__ == "__main__":
    exemple = "38.4 * (7625 +( 98.7 - j)) *(4)* (1 + ab Lol)"

    print(split_equation(exemple))

    print(equation_2_ast(exemple))
