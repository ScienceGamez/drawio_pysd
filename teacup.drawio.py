"""
Python model 'teacup.drawio.py'
Translated using PySD
"""

from pathlib import Path

from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.9.0"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0.0,
    "final_time": lambda: 10.0,
    "time_step": lambda: 1.0,
    "saveper": lambda: 1.0,
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="INITIAL TIME", units="-", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    Initial time of the simulation
    """
    return __data["time"].initial_time()


@component.add(
    name="FINAL TIME", units="-", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    Final time of the simulation
    """
    return __data["time"].final_time()


@component.add(name="TIME STEP", units="-", comp_type="Constant", comp_subtype="Normal")
def time_step():
    """
    Time step of the simulation
    """
    return __data["time"].time_step()


@component.add(name="SAVEPER", units="-", comp_type="Constant", comp_subtype="Normal")
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Teacup Temperature",
    units="C",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_teacup_temperature": 1},
    other_deps={
        "_integ_teacup_temperature": {"initial": {}, "step": {"heat_loss_to_room": 1}}
    },
)
def teacup_temperature():
    """
    The temperature of the teacup
    """
    return _integ_teacup_temperature()


_integ_teacup_temperature = Integ(
    lambda: -heat_loss_to_room(), lambda: 100.0, "_integ_teacup_temperature"
)


@component.add(
    name="Heat Loss to Room",
    units="J/s",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "teacup_temperature": 1,
        "room_temperature": 1,
        "characteristic_time": 1,
    },
)
def heat_loss_to_room():
    """
    The loss of heat to room
    """
    return (teacup_temperature() - room_temperature()) / characteristic_time()


@component.add(
    name="Characteristic Time", units="-", comp_type="Constant", comp_subtype="Normal"
)
def characteristic_time():
    """
    The time constant for the teacup
    """
    return 10.0


@component.add(
    name="Room Temperature", units="C", comp_type="Constant", comp_subtype="Normal"
)
def room_temperature():
    return 20.0
