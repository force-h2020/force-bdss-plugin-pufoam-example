import numpy as np

from force_bdss.api import BaseDataSource, DataValue, Slot

from pufoam_example.utilities import parse_data_values


class CostDataSource(BaseDataSource):
    """Class that calculates cost of chemical materials
    for production of a PU foam"""

    def concentration_convertor(self, volume, concentrations, molar_masses):
        """Converts concentrations from mol/m3 into kg"""

        mols = np.asarray(concentrations) * volume
        masses = np.asarray(molar_masses) * mols

        return masses

    def calculate_cost(self, volume, prices, concentrations, molar_masses):
        """Simple material cost calculation as dot product of prices
        and concentrations"""

        masses = self.concentration_convertor(
            volume, concentrations, molar_masses
        )

        cost = np.sum(np.asarray(prices) * masses)

        return cost

    def run(self, model, parameters):

        formulation = parse_data_values(parameters, "FORMULATION")[0]

        chemical_prices = []
        chemical_concs = []
        chemical_molar_masses = []

        for chemical in formulation.chemicals:
            chemical_prices.append(chemical.price)
            chemical_molar_masses.append(chemical.molecular_weight)
            chemical_concs.append(chemical.concentration)

        total_cost = self.calculate_cost(
            model.PU_volume,
            chemical_prices,
            chemical_concs,
            chemical_molar_masses,
        )

        status = total_cost < model.threshold

        return [
            DataValue(type="COST", value=total_cost),
            DataValue(type="PASS", value=status),
        ]

    def slots(self, model):

        return (
            (Slot(description="PU foam formulation", type="FORMULATION"),),
            (
                Slot(description="Cost of experiment", type="COST"),
                Slot(
                    description="Is cost lower than threshold requirement?",
                    type="PASS",
                ),
            ),
        )
