"""
Python model 'greenhouse.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

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


@component.add(name="Initial Time", comp_type="Constant", comp_subtype="Normal")
def initial_time():
    return __data["time"].initial_time()


@component.add(name="Final Time", comp_type="Constant", comp_subtype="Normal")
def final_time():
    return __data["time"].final_time()


@component.add(name="Time Step", comp_type="Constant", comp_subtype="Normal")
def time_step():
    return __data["time"].time_step()


@component.add(name="Saveper", comp_type="Constant", comp_subtype="Normal")
def saveper():
    return __data["time"].saveper()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Athmospheric CO2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_athmospheric_co2": 1},
    other_deps={
        "_integ_athmospheric_co2": {
            "initial": {"initial_athmospheric_co2": 1},
            "step": {
                "vegetation_to_athmosphere_co2": 1,
                "soil_to_athmosphere_co2": 1,
                "athmosphere_to_vegetation_co2": 1,
                "athmosphere_to_upper_ocean_co2": 1,
                "total_human_emissions": 1,
            },
        }
    },
)
def athmospheric_co2():
    """
    Quantity of CO2 in the athmosphere
    """
    return _integ_athmospheric_co2()


_integ_athmospheric_co2 = Integ(
    lambda: vegetation_to_athmosphere_co2()
    + soil_to_athmosphere_co2()
    - athmosphere_to_vegetation_co2()
    - athmosphere_to_upper_ocean_co2()
    + total_human_emissions(),
    lambda: initial_athmospheric_co2(),
    "_integ_athmospheric_co2",
)


@component.add(
    name="Athmospheric Decay CO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"athmospheric_co2": 1, "decay_t_co2": 1},
)
def athmospheric_decay_co2():
    """
    Decay of CO2 induced by the athmospheric chemistry.
    """
    return athmospheric_co2() / decay_t_co2()


@component.add(name="Decay T CO2", comp_type="Constant", comp_subtype="Normal")
def decay_t_co2():
    """
    Time constant for athmosperic decay
    """
    return 42.0


@component.add(
    name="Upper Ocean CO2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_upper_ocean_co2": 1},
    other_deps={
        "_integ_upper_ocean_co2": {
            "initial": {},
            "step": {
                "athmosphere_to_upper_ocean_co2": 1,
                "upper_ocean_to_lower_ocean_co2": 1,
            },
        }
    },
)
def upper_ocean_co2():
    """
    Quantity of CO2 in the upper part of the ocean
    """
    return _integ_upper_ocean_co2()


_integ_upper_ocean_co2 = Integ(
    lambda: athmosphere_to_upper_ocean_co2() - upper_ocean_to_lower_ocean_co2(),
    lambda: 20.0,
    "_integ_upper_ocean_co2",
)


@component.add(
    name="Lower Ocean CO2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_lower_ocean_co2": 1},
    other_deps={
        "_integ_lower_ocean_co2": {
            "initial": {},
            "step": {"upper_ocean_to_lower_ocean_co2": 1},
        }
    },
)
def lower_ocean_co2():
    """
    Quantity of CO2 in the Lower part of the ocean
    """
    return _integ_lower_ocean_co2()


_integ_lower_ocean_co2 = Integ(
    lambda: upper_ocean_to_lower_ocean_co2(), lambda: 20.0, "_integ_lower_ocean_co2"
)


@component.add(name="H Conc", comp_type="Constant", comp_subtype="Normal")
def h_conc():
    """
    Concentration of hydrogen ions
    """
    return 7.943282347242822e-09


@component.add(
    name="Ph Ocean",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h_conc": 1},
)
def ph_ocean():
    """
    pH of the ocean
    """
    return -(np.log(h_conc()) / np.log(10.0))


@component.add(name="Am", comp_type="Constant", comp_subtype="Normal")
def am():
    """
    Number of moles in athmosphere
    """
    return 1.77e20


@component.add(
    name="Athmosphere To Upper Ocean CO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"k_a": 1, "athmospheric_co2": 1, "a": 1, "b": 1, "upper_ocean_co2": 1},
)
def athmosphere_to_upper_ocean_co2():
    """
    Transfer of CO2 from athmosphere to upper_ocean
    """
    return k_a() * athmospheric_co2() + a() * b() * upper_ocean_co2()


@component.add(
    name="Upper Ocean To Lower Ocean CO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"k_d": 1, "upper_ocean_co2": 1, "lower_ocean_co2": 1, "delta": 1},
)
def upper_ocean_to_lower_ocean_co2():
    """
    Transfer of CO2 from upper_ocean to lower_ocean
    """
    return k_d() * upper_ocean_co2() - lower_ocean_co2() / delta()


@component.add(name="K A", comp_type="Constant", comp_subtype="Normal")
def k_a():
    """
    inverse exchange timescales between athmosphere and upper ocean
    """
    return 0.2


@component.add(name="K D", comp_type="Constant", comp_subtype="Normal")
def k_d():
    """
    inverse exchange timescales between Lower and upper ocean
    """
    return 0.05


@component.add(name="K 1", comp_type="Constant", comp_subtype="Normal")
def k_1():
    """
    dissociation constant
    """
    return 8e-07


@component.add(name="K 2", comp_type="Constant", comp_subtype="Normal")
def k_2():
    """
    dissociation constant
    """
    return 4.53e-10


@component.add(
    name="A",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"k_h": 1, "am": 1, "om": 1, "delta": 1},
)
def a():
    """
    ratio ofatmosphere to ocean concentration at equilibrium, which is weakly dependent ontemperature: a warmer ocean holds less dissolved CO2
    """
    return k_h() * am() / om() * 1.0 + delta()


@component.add(
    name="B",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"k_1": 2, "h_conc": 2, "k_2": 1},
)
def b():
    """
    ratio of dissolved CO2 tototal ocean inorganic carbon at equilibrium, a strong function of aciditymore acidic seawater stores less inorganic carbon. Variation in b in particular alters uptakerates dramatically
    """
    return 1.0 / 1.0 + k_1() / h_conc() + k_1() * k_2() / h_conc() ** 2.0


@component.add(name="Delta", comp_type="Constant", comp_subtype="Normal")
def delta():
    """
    the ratio of Lower to upper ocean volume (∼ 50),
    """
    return 50.0


@component.add(name="Om", comp_type="Constant", comp_subtype="Normal")
def om():
    """
    Number of moles in ocean
    """
    return 7.8e22


@component.add(name="K H", comp_type="Constant", comp_subtype="Normal")
def k_h():
    """
    ratio of the molar concentrations of CO2 in atmosphere and ocean.
    """
    return 1230.0


@component.add(
    name="Vegetation CO2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_vegetation_co2": 1},
    other_deps={
        "_integ_vegetation_co2": {
            "initial": {},
            "step": {"athmosphere_to_vegetation_co2": 1, "vegetation_to_soil_co2": 1},
        }
    },
)
def vegetation_co2():
    """
    Quantity of CO2 stored in the surface Vegetation
    """
    return _integ_vegetation_co2()


_integ_vegetation_co2 = Integ(
    lambda: athmosphere_to_vegetation_co2() - vegetation_to_soil_co2(),
    lambda: 20.0,
    "_integ_vegetation_co2",
)


@component.add(
    name="Soil CO2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_soil_co2": 1},
    other_deps={
        "_integ_soil_co2": {
            "initial": {},
            "step": {"vegetation_to_soil_co2": 1, "soil_to_athmosphere_co2": 1},
        }
    },
)
def soil_co2():
    """
    Quantity of CO2 stored in the soil
    """
    return _integ_soil_co2()


_integ_soil_co2 = Integ(
    lambda: vegetation_to_soil_co2() - soil_to_athmosphere_co2(),
    lambda: 20.0,
    "_integ_soil_co2",
)


@component.add(
    name="Vegetation To Soil CO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "vegetation_decay_to_soil_ratio": 1,
        "vegetation_decay_ratio": 1,
        "vegetation_co2": 1,
    },
)
def vegetation_to_soil_co2():
    """
    Transfer of CO2 from Vegetation to soil
    """
    return (
        vegetation_decay_to_soil_ratio() * vegetation_decay_ratio() * vegetation_co2()
    )


@component.add(
    name="Soil To Athmosphere CO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"soil_co2": 1, "soil_to_athmoshere_ratio": 1},
)
def soil_to_athmosphere_co2():
    """
    Transfer of CO2 from soil to athmosphere
    """
    return soil_co2() * soil_to_athmoshere_ratio()


@component.add(
    name="Vegetation Decay",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"vegetation_co2": 1, "vegetation_decay_ratio": 1},
)
def vegetation_decay():
    """
    net primary production by terrestrial plants
    """
    return vegetation_co2() * vegetation_decay_ratio()


@component.add(
    name="Vegetation Decay Ratio", comp_type="Constant", comp_subtype="Normal"
)
def vegetation_decay_ratio():
    """
    proportion of Vegetation that decays
    """
    return 0.087


@component.add(
    name="Soil To Athmoshere Ratio", comp_type="Constant", comp_subtype="Normal"
)
def soil_to_athmoshere_ratio():
    """
    proportion of the soil carbon that goes in athmosphere
    """
    return 0.6


@component.add(
    name="Vegetation Production",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "initial_vegetation_production": 1,
        "athmospheric_co2": 1,
        "a_2": 1,
        "initial_athmospheric_co2": 1,
    },
)
def vegetation_production():
    """
    net primary production by terrestrial plants
    """
    return initial_vegetation_production() * (
        1.0 - a_2() * (athmospheric_co2() - initial_athmospheric_co2())
    )


@component.add(
    name="Initial Vegetation Production", comp_type="Constant", comp_subtype="Normal"
)
def initial_vegetation_production():
    """
    Vegetation production at the start of the simulation
    """
    return 0.00047


@component.add(name="A_2", comp_type="Constant", comp_subtype="Normal")
def a_2():
    """
    constant of Vegetation
    """
    return 0.00047


@component.add(
    name="Athmosphere To Vegetation CO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"vegetation_production": 1},
)
def athmosphere_to_vegetation_co2():
    """
    Transfer of CO2 from athmosphere to Vegetation
    """
    return vegetation_production()


@component.add(
    name="Vegetation To Athmosphere CO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "vegetation_decay_to_soil_ratio": 1,
        "vegetation_decay_ratio": 1,
        "vegetation_co2": 1,
    },
)
def vegetation_to_athmosphere_co2():
    """
    Transfer of CO2 from Vegetation to athmosphere
    """
    return (
        (1.0 - vegetation_decay_to_soil_ratio())
        * vegetation_decay_ratio()
        * vegetation_co2()
    )


@component.add(
    name="Vegetation Decay To Soil Ratio", comp_type="Constant", comp_subtype="Normal"
)
def vegetation_decay_to_soil_ratio():
    """
    proportion from the decaying Vegetation that goes to the soil
    """
    return 0.6


@component.add(
    name="Initial Athmospheric CO2", comp_type="Constant", comp_subtype="Normal"
)
def initial_athmospheric_co2():
    """
    Initial Quantity of CO2 in the athmosphere
    """
    return 1200.0


@component.add(name="Emissions CO2", comp_type="Constant", comp_subtype="Normal")
def emissions_co2():
    """
    Emission of Green house Gas from human activities
    """
    return 42.0


@component.add(name="Capture CO2", comp_type="Constant", comp_subtype="Normal")
def capture_co2():
    """
    Capture of CO2 from human activities
    """
    return 12.0


@component.add(
    name="Total Human Emissions",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"capture_co2": 1, "emissions_co2": 1},
)
def total_human_emissions():
    """
    The sum of all human activites
    """
    return capture_co2() - emissions_co2()


@component.add(
    name="Surface Energy Variation",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_surface_energy_variation": 1},
    other_deps={
        "_integ_surface_energy_variation": {
            "initial": {},
            "step": {
                "absorbed_solar_radiation": 1,
                "irradiated_surface": 1,
                "greenhouse_absorbed_radiation": 1,
                "earth_surface": 1,
                "upper_ocean_to_lower_ocean_energy": 1,
            },
        }
    },
)
def surface_energy_variation():
    """
    Total variation of the surface energy
    """
    return _integ_surface_energy_variation()


_integ_surface_energy_variation = Integ(
    lambda: absorbed_solar_radiation() * irradiated_surface()
    + greenhouse_absorbed_radiation() * earth_surface()
    - upper_ocean_to_lower_ocean_energy(),
    lambda: 20.0,
    "_integ_surface_energy_variation",
)


@component.add(
    name="Surface Temperature",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_surface_temperature": 1},
    other_deps={
        "_integ_surface_temperature": {
            "initial": {},
            "step": {"c_surface": 1, "surface_energy_variation": 1},
        }
    },
)
def surface_temperature():
    """
    Average Temperature of the upper ocean and surface
    """
    return _integ_surface_temperature()


_integ_surface_temperature = Integ(
    lambda: c_surface() * surface_energy_variation(),
    lambda: 288.0,
    "_integ_surface_temperature",
)


@component.add(
    name="C_Surface", units="J/K", comp_type="Constant", comp_subtype="Normal"
)
def c_surface():
    """
    Heat capacity of the surface
    """
    return 200000.0


@component.add(
    name="Absorbed Solar Radiation",
    units="W/m2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"energy_sun": 1, "surface_reflection_ratio": 1},
)
def absorbed_solar_radiation():
    return energy_sun() * (1.0 - surface_reflection_ratio())


@component.add(
    name="Energy Sun", units="W/m2", comp_type="Constant", comp_subtype="Normal"
)
def energy_sun():
    """
    Energy that is received from the sun.
    """
    return 342.0


@component.add(
    name="Reflected solar radiation",
    units="W/m2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"energy_sun": 1, "surface_reflection_ratio": 1},
)
def reflected_solar_radiation():
    """
    A portion of the incoming solar radiation is reflected back into space by the Earth's atmosphere and surface.
    """
    return energy_sun() * surface_reflection_ratio()


@component.add(
    name="Surface Reflection Ratio", comp_type="Constant", comp_subtype="Normal"
)
def surface_reflection_ratio():
    """
    Proportion of sun energy that is reflected by the athmosphere, this is also known as albedo
    """
    return 0.3


@component.add(
    name="Surface Radiation",
    units="W/m2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "base_surface_radiation": 1,
        "surface_radiation_increase_from_t": 1,
        "surface_temperature": 1,
    },
)
def surface_radiation():
    """
    This is the thermal radiation emitted by the Earth's surface and atmosphere, also known as infrared radiation
    """
    return (
        base_surface_radiation()
        + surface_radiation_increase_from_t() * surface_temperature()
    )


@component.add(
    name="Greenhouse Absorbed Radiation",
    units="W/m2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"absorbed_radiation_ratio": 1, "surface_radiation": 1},
)
def greenhouse_absorbed_radiation():
    """
    Greenhouse gases in the Earth's atmosphere absorb a portion of the infrared radiation emitted by the surface and re-radiate it in all directions. This causes the Earth's surface and atmosphere to warm up.
    """
    return absorbed_radiation_ratio() * surface_radiation()


@component.add(
    name="Absorbed Radiation Ratio", comp_type="Constant", comp_subtype="Normal"
)
def absorbed_radiation_ratio():
    """
    Proportion of the earth radiation absorbed by the athmosphere.
    This varies based on the concentration of Greenhouse Gases in the Athmosphere.
    """
    return 0.65


@component.add(
    name="Outgoing Infrared Radiation",
    units="W/m2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"surface_radiation": 1, "absorbed_radiation_ratio": 1},
)
def outgoing_infrared_radiation():
    """
    The remaining infrared radiation that is not absorbed by greenhouse gases is emitted back into space.
    """
    return surface_radiation() * (1.0 - absorbed_radiation_ratio())


@component.add(
    name="Base Surface Radiation",
    units="W/m2",
    comp_type="Constant",
    comp_subtype="Normal",
)
def base_surface_radiation():
    """
    Surface Radiation at time 0
    """
    return 230.0


@component.add(
    name="Surface Radiation Increase From T",
    units="W/m2/K",
    comp_type="Constant",
    comp_subtype="Normal",
)
def surface_radiation_increase_from_t():
    """
    Constant of the increase of surface radiation based on the temperature
    """
    return 5.0


@component.add(
    name="Earth Radius", units="m", comp_type="Constant", comp_subtype="Normal"
)
def earth_radius():
    return 6371000.0


@component.add(
    name="Earth Surface",
    units="m2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"earth_radius": 1},
)
def earth_surface():
    """
    The surface of the earth
    """
    return 4.0 * np.pi * earth_radius() ** 2.0


@component.add(
    name="Irradiated Surface",
    units="m2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"earth_surface": 1},
)
def irradiated_surface():
    """
    Only the facing sun part of the earth is irradiated
    """
    return earth_surface() / 2.0


@component.add(
    name="Upper Ocean To Lower Ocean Energy",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"b_1": 1, "surface_temperature": 1, "lower_ocean_temperature": 1},
)
def upper_ocean_to_lower_ocean_energy():
    """
    Transfer of energy from upper_ocean to lower_ocean
    """
    return b_1() * (surface_temperature() - lower_ocean_temperature())


@component.add(name="b", units="-", comp_type="Constant", comp_subtype="Normal")
def b_1():
    """
    Constant of energy mixing between higher and Lower ocean
    """
    return 0.05


@component.add(
    name="Lower Ocean Temperature",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_lower_ocean_temperature": 1},
    other_deps={
        "_integ_lower_ocean_temperature": {
            "initial": {},
            "step": {"upper_ocean_to_lower_ocean_energy": 1, "c_lower": 1},
        }
    },
)
def lower_ocean_temperature():
    """
    AVerage Temperature of the Lower ocean
    """
    return _integ_lower_ocean_temperature()


_integ_lower_ocean_temperature = Integ(
    lambda: upper_ocean_to_lower_ocean_energy() / c_lower(),
    lambda: 288.0,
    "_integ_lower_ocean_temperature",
)


@component.add(name="C_Lower", units="J/K", comp_type="Constant", comp_subtype="Normal")
def c_lower():
    """
    Heat capacity of the Lower ocean
    """
    return 200000.0
