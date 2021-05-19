from traits.api import Int, Enum
from traitsui.api import View, Item, Group

from force_bdss.api import BaseDataSourceModel, VerifierError


class FormulationDataSourceModel(BaseDataSourceModel):
    """ Chemical formulation model of a PU foam"""

    #: Number of chemical formulation
    n_chemicals = Int(4, changes_slots=True)

    #: Dimensionality of molar concentration of chemicals
    molar_concentration = Enum("mol m-3", "mol cm-3", "mol dl-3")

    #: Dimensionality of density
    density = Enum("kg m-3", "g cm-3")

    #: Dimensionality of molecular mass
    molecular_mass = Enum("g mol-1", "kg kmol-1")

    traits_view = View(
        Item("n_chemicals"),
        Group(
            Item("molar_concentration"),
            Item("density"),
            Item("molecular_mass"),
            label="Dimensions",
        )
    )

    def _n_chemicals_check(self):
        """ Makes sure there is at least 4 chemicals in the PU blend"""

        if self.n_chemicals < 4:
            return [
                VerifierError(
                    subject=self,
                    local_error="Number of Chemicals must be at least 4",
                    global_error="The Ingredients pre-processor does not "
                    "have enough Chemicals defined",
                )
            ]
        return []

    def verify(self):
        """ Overloads BaseDataSourceModel verify method to check the
        number of Chemicals during a verify_workflow_event"""

        errors = super().verify()
        errors += self._n_chemicals_check()

        return errors
