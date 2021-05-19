from .data_format import PUFoamDataDict


gelling_data = {
    "A_OH": 1,
    "E_OH": 3.514e4,
    "initCOH": 5140,
    "initCNCO": 4455,
    "initCW": 671,
    "gellingPoint": 0.606,
}

blowing_agent_data = "n-pentane"

blowing_data = {"A_W": 1.050e3, "E_W": 2.704e4}

generic_data = {
    "idealGasCons": 8.3145,
    "rhoPolymer": 1100.0,
    "rhoBlowingAgent": 751.0,
    "molecularMassCO2": 44.0,
    "molecularMassBlowingAgent": 72.15,
    "molecularMassNCO": 615.0,
    "molecularMassLiquidFoam": 378.9,
    "dxdTcons": -0.01162790697,
    "initBlowingAgent": 0.057,
    "surfaceTension": 11.5e-3,
}

enthalpy_data = {
    "deltaOH": -6.85e4,
    "deltaW": -8.15e4,
    "PUspecificHeat": 1800.0,
    "latentHeat": 2.0e5,
}


class KineticData(PUFoamDataDict):
    """ Kinetics data file for the simulation.
    """

    file_location = '"constant"'
    file_name = "kineticsProperties"

    def __init__(self):
        super().__init__()
        self.add_data(
            {
                "GellingConstants": gelling_data.copy(),
                "blowingAgent": blowing_agent_data,
                "BlowingConstants": blowing_data.copy(),
                "GenericConstants": generic_data.copy(),
                "EnthalpyConstants": enthalpy_data.copy(),
            }
        )

    def update_reaction_parameters(self, mapping):

        for key, value in mapping.items():

            if key in ["A_OH", "E_OH", "gellingPoint"]:
                dict_key = "GellingConstants"

            elif key in ["deltaOH", "deltaW", "latentHeat"]:
                dict_key = "EnthalpyConstants"

            elif key in ["A_W", "E_W"]:
                dict_key = "BlowingConstants"

            else:
                continue

            self.data[dict_key][key] = value
