"""
Python model 'teacup.drawio.py'
Translated using PySD
"""

from pathlib import Path

from pysd import Component

__pysd_version__ = "3.8.0"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################
