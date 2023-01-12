"""Code to parse equations from drawio files."""

import re
import logging

from pysd.translators.structures import abstract_expressions


logger = logging.getLogger("drawio_pysd.equations_parsing")


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
            return abstract_expressions.ReferenceStructure(splitted[0])
        # If the equation is a function, return the function
        elif re.match(r"^[a-zA-Z_][a-zA-Z0-9_ ]*\([a-zA-Z0-9_ ,]*\)$", splitted[0]):
            # Get the function name
            function_name = splitted[0].split("(")[0]
            # Get the arguments
            arguments = splitted[0].split("(")[1][:-1].split(",")
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

    return abstract_expressions.ArithmeticStructure(
        # operators are the odd elements
        operators=splitted[1::2],
        arguments=[equation_2_ast(element) for element in splitted[::2]],
    )


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
        logger.debug(f"split_equation: {char=}, {element=}")
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
