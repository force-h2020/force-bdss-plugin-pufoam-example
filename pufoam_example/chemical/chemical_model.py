from traits.api import Unicode, Enum, Float
from traitsui.api import View, Item

from force_bdss.api import BaseDataSourceModel, VerifierError


class ChemicalDataSourceModel(BaseDataSourceModel):
    """Class containing all parameters for a single chemical
    (molecular species)"""

    name = Unicode(desc="Name of molecular chemical")

    role = Enum(
        "Polyol",
        "Isocyanate",
        "Catalyst",
        "Surfactant",
        "Solvent",
        "Blowing Agent",
        desc="Role of chemical in formulation",
    )

    molecular_weight = Float(desc="Molecular weight of chemical in g/mol")

    density = Float(desc="Density in kg/m3")

    functionality = Float(default_value=1, desc="Molarity of active chemical")

    price = Float(desc="Price of chemical in USD/kg")

    conc_input = Enum(['Model', 'Parameter'], changes_slots=True)

    concentration = Float(desc="Concentration by weight (%)")

    traits_view = View(
        Item("name"),
        Item("role"),
        Item("molecular_weight"),
        Item("density"),
        Item("functionality"),
        Item("price"),
        Item("conc_input"),
        Item("concentration", visible_when="conc_input=='Model'")
    )

    def _property_check(self, key, property, local_error, global_error=None):
        """Generic property check for a chemical

        Parameters
        ----------
        key : str
            Identifier of role to check
        property: HasTraits
            Property of chemical to check
        local_error: str
            Local error message to raise if check fails
        global_error: str (optional)
            Global error message to raise if check fails

        Returns
        -------
        errors: list(VerifierError)
            List of errors raised by check
        """
        errors = []
        if self.role == key and property < 0:
            errors.append(
                VerifierError(
                    subject=self,
                    local_error=local_error,
                    global_error=global_error,
                )
            )

        return errors
