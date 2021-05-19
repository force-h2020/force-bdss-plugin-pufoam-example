from force_bdss.api import BaseDataSource, DataValue, Slot

from pufoam_example.utilities import parse_data_values

from .formulation import Formulation


class FormulationDataSource(BaseDataSource):
    """ Collates and defines a PU formulation. A formulation contains
    the following chemical classes:

    - Polyol
    - Isocyanate
    - Solvent
    - Blowing Agent
    """

    def check_present_chemical_roles(self, chemical_roles):
        # We check that at least one of each key chemical role is assigned for
        # the experiment (Catalyst and Surfactant roles are optional)
        for chemical_role in (
            "Polyol",
            "Isocyanate",
            "Solvent",
            "Blowing Agent",
        ):
            if chemical_role not in chemical_roles:
                raise AttributeError(
                    f"No {chemical_role} assigned in chemical roles"
                )

    def run(self, model, parameters):
        # Extract all parameters into lists by type.
        # We expect to receive n_chemical values for each formulation
        chemicals = parse_data_values(parameters, "CHEMICAL")

        chemical_roles = set(chemical.role for chemical in chemicals)
        self.check_present_chemical_roles(chemical_roles)

        # Generate Formulation
        formulation = Formulation(chemicals=chemicals)

        return [DataValue(type="FORMULATION", value=formulation)]

    def slots(self, model):

        input_slots = tuple()

        for index in range(model.n_chemicals):
            input_slots += (
                Slot(description="Chemical {} data".format(index + 1),
                     type="CHEMICAL"),
            )

        return (
            input_slots,
            (Slot(description="PU foam formulation", type="FORMULATION"),),
        )
