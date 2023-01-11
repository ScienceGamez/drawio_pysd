"""Contains an example of an  green house gas cycle AbstractModel.

This can be used to generate a python model, or to generate a pysd drawio model.
"""
from pathlib import Path
from pysd.translators.structures.abstract_model import (
    AbstractComponent,
    AbstractElement,
    AbstractControlElement,
    AbstractModel,
    AbstractSection,
)
from pysd.translators.structures.abstract_expressions import (
    ReferenceStructure,
    IntegStructure,
    AbstractSyntax,
    ArithmeticStructure,
    SubscriptsReferenceStructure,
    CallStructure,
)
from pysd.builders.python.python_model_builder import ModelBuilder
from pysd import load

path = Path("exemples/ghg.py")
NO_SUBS = ([], [])

# creat simple ref
ref_ast = lambda x: ReferenceStructure(x)
ghg_flow_element = lambda from_, to_, ast: AbstractElement(
    f"{from_}_to_{to_}_ghg",
    components=[AbstractComponent(([], []), ast)],
    units="kg/year",
    documentation=f"Transfer of ghg from {from_} to {to_}",
)


climate_model = AbstractSection(
    name=path.stem,
    path=path,
    type="main",
    params=[],
    returns=[],
    subscripts=(),
    constraints=(),
    test_inputs=(),
    elements=(
        AbstractElement(
            "initial_time",
            components=[AbstractComponent(NO_SUBS, 0)],
        ),
        AbstractElement(
            "final_time",
            components=[AbstractComponent(NO_SUBS, 10)],
        ),
        AbstractElement(
            "time_step",
            components=[AbstractComponent(NO_SUBS, 1)],
        ),
        AbstractElement(
            "saveper",
            components=[AbstractComponent(NO_SUBS, 1)],
        ),
        AbstractElement(
            "emissions_ghg",
            components=[AbstractComponent(NO_SUBS, 42)],
            units="kg/year",
            documentation="Emission of Green house Gas from human activities",
            limits=(0, None),
        ),
        AbstractElement(
            "capture_ghg",
            components=[AbstractComponent(NO_SUBS, 12)],
            units="kg/year",
            documentation="Capture of ghg from human activities",
            limits=(0, None),
        ),
        AbstractElement(
            "athmospheric_ghg",
            [
                AbstractComponent(
                    NO_SUBS,
                    ast=IntegStructure(
                        flow=ArithmeticStructure(
                            ["+", "+", "-", "-", "-"],
                            [
                                ref_ast("emissions_ghg"),
                                ref_ast("vegetation_to_athmosphere_ghg"),
                                ref_ast("soil_to_athmosphere_ghg"),
                                ref_ast("capture_ghg"),
                                ref_ast("athmosphere_to_vegetation_ghg"),
                                ref_ast("athmosphere_to_upper_ocean_ghg"),
                            ],
                        ),
                        initial=ref_ast("initial_athmospheric_ghg"),
                    ),
                )
            ],
            limits=(0, None),
            units="kg",
            documentation="Quantity of ghg in the athmosphere",
        ),
        AbstractElement(
            "initial_athmospheric_ghg",
            [
                AbstractComponent(
                    NO_SUBS,
                    ast=12e2,
                )
            ],
            limits=(0, None),
            units="kg",
            documentation="Initial Quantity of ghg in the athmosphere",
        ),
        AbstractElement(
            "upper_ocean_ghg",
            [
                AbstractComponent(
                    NO_SUBS,
                    ast=IntegStructure(
                        flow=ArithmeticStructure(
                            ["-"],
                            [
                                ref_ast("athmosphere_to_upper_ocean_ghg"),
                                ref_ast("upper_ocean_to_lower_ocean_ghg"),
                            ],
                        ),
                        initial=20,
                    ),
                )
            ],
            limits=(0, None),
            units="kg",
            documentation="Quantity of ghg in the upper part of the ocean",
        ),
        AbstractElement(
            "lower_ocean_ghg",
            [
                AbstractComponent(
                    NO_SUBS,
                    ast=IntegStructure(
                        flow=ref_ast("upper_ocean_to_lower_ocean_ghg"),
                        initial=20,
                    ),
                )
            ],
            limits=(0, None),
            units="kg",
            documentation="Quantity of ghg in the lower part of the ocean",
        ),
        AbstractElement(
            "vegetation_ghg",
            [
                AbstractComponent(
                    NO_SUBS,
                    ast=IntegStructure(
                        flow=ArithmeticStructure(
                            ["-"],
                            [
                                ref_ast("athmosphere_to_vegetation_ghg"),
                                ref_ast("vegetation_to_soil_ghg"),
                            ],
                        ),
                        initial=20,
                    ),
                )
            ],
            limits=(0, None),
            units="kg",
            documentation="Quantity of ghg stored in the surface vegetation",
        ),
        AbstractElement(
            "soil_ghg",
            [
                AbstractComponent(
                    NO_SUBS,
                    ast=IntegStructure(
                        flow=ArithmeticStructure(
                            ["-"],
                            [
                                ref_ast("vegetation_to_soil_ghg"),
                                ref_ast("soil_to_athmosphere_ghg"),
                            ],
                        ),
                        initial=20,
                    ),
                )
            ],
            limits=(0, None),
            units="kg",
            documentation="Quantity of ghg stored in the soil",
        ),
        AbstractElement(
            "h_conc",
            [
                AbstractComponent(
                    NO_SUBS,
                    10**-8.1,
                )
            ],
            limits=(0, None),
            units="mol/kg",
            documentation="Concentration of hydrogen ions",
        ),
        AbstractElement(
            "ph_ocean",
            [
                AbstractComponent(
                    NO_SUBS,
                    ast=ArithmeticStructure(
                        ["negative"],
                        [
                            CallStructure(
                                ReferenceStructure("log"), (ref_ast("h_conc"), 10)
                            )
                        ],
                    ),
                )
            ],
            documentation="pH of the ocean",
        ),
        AbstractElement(
            "am",
            [
                AbstractComponent(
                    NO_SUBS,
                    ast=1.77e20,
                )
            ],
            documentation="Number of moles in athmosphere",
            units="mol",
        ),
        AbstractElement(
            "om",
            [
                AbstractComponent(
                    NO_SUBS,
                    ast=7.8e22,
                )
            ],
            documentation="Number of moles in ocean",
            units="mol",
        ),
        AbstractElement(
            "athmospheric_decay_ghg",
            components=[
                AbstractComponent(
                    NO_SUBS,
                    ast=ArithmeticStructure(
                        ["/"], [ref_ast("athmospheric_ghg"), ref_ast("decay_t_ghg")]
                    ),
                )
            ],
            units="kg/year",
            documentation="Decay of ghg induced by the athmospheric chemistry.",
            limits=(0, None),
        ),
        ghg_flow_element("athmosphere", "vegetation", ref_ast("vegetation_production")),
        ghg_flow_element(
            "vegetation",
            "athmosphere",
            ArithmeticStructure(
                ["*", "*"],
                [
                    ArithmeticStructure(
                        ["-"], [1, ref_ast("vegetation_decay_to_soil_ratio")]
                    ),
                    ref_ast("vegetation_decay_ratio"),
                    ref_ast("vegetation_ghg"),
                ],
            ),
        ),
        ghg_flow_element(
            "vegetation",
            "soil",
            ArithmeticStructure(
                ["*", "*"],
                [
                    ref_ast("vegetation_decay_to_soil_ratio"),
                    ref_ast("vegetation_decay_ratio"),
                    ref_ast("vegetation_ghg"),
                ],
            ),
        ),
        ghg_flow_element("soil", "athmosphere",                     ArithmeticStructure(
                        ["*"],
                        [
                            ref_ast("soil_ghg"),
                            ref_ast("soil_to_athmoshere_ratio"),

                        ],
                    )),
        ghg_flow_element(
            "athmosphere",
            "upper_ocean",
            ArithmeticStructure(
                ["*"],
                [
                    ref_ast("k_a"),
                    ArithmeticStructure(
                        ["+", "*", "*"],
                        [
                            ref_ast("athmospheric_ghg"),
                            ref_ast("a"),
                            ref_ast("b"),
                            ref_ast("upper_ocean_ghg"),
                        ],
                    ),
                ],
            ),
        ),
        ghg_flow_element(
            "upper_ocean",
            "lower_ocean",
            ArithmeticStructure(
                ["*"],
                [
                    ref_ast("k_d"),
                    ArithmeticStructure(
                        [
                            "-",
                            "/",
                        ],
                        [
                            ref_ast("upper_ocean_ghg"),
                            ref_ast("lower_ocean_ghg"),
                            ref_ast("delta"),
                        ],
                    ),
                ],
            ),
        ),
        AbstractElement(
            "athmospheric_decay_ghg",
            components=[
                AbstractComponent(
                    NO_SUBS,
                    ast=ArithmeticStructure(
                        ["/"], [ref_ast("athmospheric_ghg"), ref_ast("decay_t_ghg")]
                    ),
                )
            ],
            units="kg/year",
            documentation="Decay of ghg induced by the athmospheric chemistry.",
            limits=(0, None),
        ),
        AbstractElement(
            "decay_t_ghg",
            components=[AbstractComponent(NO_SUBS, 42)],
            units="year",
            documentation="Time constant for athmosperic decay",
            limits=(0, None),
        ),
        AbstractElement(
            "vegetation_decay",
            components=[
                AbstractComponent(
                    NO_SUBS,
                    ast=ArithmeticStructure(
                        ["*"],
                        [
                            ref_ast("vegetation_ghg"),
                            ref_ast("vegetation_decay_ratio"),
                        ],
                    ),
                )
            ],
            units="kg/year",
            documentation="net primary production by terrestrial plants",
        ),
        AbstractElement(
            "vegetation_decay_ratio",
            components=[AbstractComponent(NO_SUBS, 0.087)],
            units="-",
            limits=(0, 1),
            documentation="proportion of vegetation that decays",
        ),
        AbstractElement(
            "vegetation_decay_to_soil_ratio",
            components=[AbstractComponent(NO_SUBS, 0.6)],
            units="-",
            limits=(0, 1),
            documentation="proportion from the decaying vegetation that goes to the soil",
        ),
        AbstractElement(
            "soil_to_athmoshere_ratio",
            components=[AbstractComponent(NO_SUBS, 0.6)],
            units="-",
            limits=(0, 1),
            documentation="proportion of the soil carbon that goes in athmosphere",
        ),
        AbstractElement(
            "vegetation_production",
            components=[
                AbstractComponent(
                    NO_SUBS,
                    ast=ArithmeticStructure(
                        ["*"],
                        [
                            ref_ast("vegetation_production_0"),
                            ArithmeticStructure(
                                ["-", "*"],
                                [
                                    1,
                                    ref_ast("a_2"),
                                    ArithmeticStructure(
                                        ["-"],
                                        [
                                            ref_ast("athmospheric_ghg"),
                                            ref_ast("initial_athmospheric_ghg"),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
            ],
            units="kg/year",
            documentation="net primary production by terrestrial plants",
        ),
        AbstractElement(
            "vegetation_production_0",
            components=[AbstractComponent(NO_SUBS, 0.00047)],
            units="kg/year",
            documentation="vegetation production at time 0",
        ),
        AbstractElement(
            "a_2",
            components=[AbstractComponent(NO_SUBS, 0.00047)],
            units="mol/kg",
            documentation="constant of vegetation",
        ),
        AbstractElement(
            "k_a",
            components=[AbstractComponent(NO_SUBS, 0.2)],
            units="???",
            documentation="inverse exchange timescales between athmosphere and upper ocean",
            limits=(0, None),
        ),
        AbstractElement(
            "k_d",
            components=[AbstractComponent(NO_SUBS, 0.05)],
            units="???",
            documentation="inverse exchange timescales between lower and upper ocean",
            limits=(0, None),
        ),
        AbstractElement(
            "k_1",
            components=[AbstractComponent(NO_SUBS, 8e-7)],
            units="mol/kg",
            documentation="dissociation constant",
        ),
        AbstractElement(
            "k_2",
            components=[AbstractComponent(NO_SUBS, 4.53e-10)],
            units="mol/kg",
            documentation="dissociation constant",
        ),
        AbstractElement(
            "a",
            components=[
                AbstractComponent(
                    NO_SUBS,
                    ast=ArithmeticStructure(
                        ["*", "/", "*"],
                        [
                            ref_ast("k_h"),
                            ref_ast("am"),
                            ref_ast("om"),
                            ArithmeticStructure(["+"], [1, ref_ast("delta")]),
                        ],
                    ),
                )
            ],
            units="-",
            # DICE  10.1007/s10584-014-1224-y
            documentation="ratio of"
            "atmosphere to ocean concentration at equilibrium, which is weakly dependent on"
            "temperature: a warmer ocean holds less dissolved CO2",
            limits=(0, None),
        ),
        AbstractElement(
            "b",
            components=[
                AbstractComponent(
                    NO_SUBS,
                    ArithmeticStructure(
                        ["/"],
                        [
                            1.0,
                            ArithmeticStructure(
                                ["+", "/", "+"],
                                [
                                    1.0,
                                    ref_ast("k_1"),
                                    ref_ast("h_conc"),
                                    ArithmeticStructure(
                                        ["*", "/", "^"],
                                        [
                                            ref_ast("k_1"),
                                            ref_ast("k_2"),
                                            ref_ast("h_conc"),
                                            2,
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
            ],
            units="-",
            # DICE  10.1007/s10584-014-1224-y
            documentation="ratio of dissolved CO2 to"
            "total ocean inorganic carbon at equilibrium, a strong function of acidity"
            "more acidic seawater stores less inorganic carbon. Variation in b in particular alters uptake"
            "rates dramatically",
            limits=(0, None),
        ),
        AbstractElement(
            "delta",
            components=[AbstractComponent(NO_SUBS, 50)],
            units="-",
            # DICE  10.1007/s10584-014-1224-y
            documentation="the ratio of lower to upper ocean volume (∼ 50),",
            limits=(0, None),
        ),
        AbstractElement(
            "k_h",
            components=[AbstractComponent(NO_SUBS, 1230)],
            units="-",
            # DICE  10.1007/s10584-014-1224-y
            documentation="ratio of the molar concentrations of CO2 in atmosphere and ocean.",
            limits=(0, None),
        ),
    ),
    split=False,
    views_dict=None,
)
model = AbstractModel(original_path=path, sections=(climate_model,))

if __name__ == "__main__":
    print(climate_model)



    original_model = ModelBuilder(model)
    f_name = original_model.build_model()

    model = load(f_name)
    df = model.run()
    print(df)