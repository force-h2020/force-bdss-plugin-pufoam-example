from force_bdss.api import BaseDataSource, DataValue, Slot

from .chemical import Chemical


class ChemicalDataSource(BaseDataSource):
    """Class takes in all data required to define each
    separate chemical. Chemical role
    must be either ''Polyol', 'Isocyanate', 'Solvent' or
    'Blowing Agent'.
    """

    def run(self, model, parameters):
        """Stores as UI input data as a Chemical object"""

        chemical = Chemical(
            name=model.name,
            role=model.role,
            molecular_weight=model.molecular_weight,
            density=model.density,
            price=model.price,
            functionality=model.functionality
        )

        if model.conc_input == 'Parameter':
            chemical.concentration = parameters[0].value
        else:
            chemical.concentration = model.concentration

        return [DataValue(type="CHEMICAL", value=chemical)]

    def slots(self, model):
        if model.conc_input == 'Parameter':
            input_slots = (
                Slot(
                    type="CONCENTRATION",
                    description="Concentration by weight (%)",
                ),
            )
        else:
            input_slots = tuple()
        return (
            input_slots,
            (Slot(type="CHEMICAL", description="Chemical data object"),),
        )
