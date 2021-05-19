from traits.api import (
    HasStrictTraits,
    Enum,
    Unicode,
    Float,
    Property,
)

from force_bdss.api import DataValue


class Chemical(HasStrictTraits):
    """Contains all properties values for each chemical in a
    formulation"""

    # --------------------
    #  Required Attributes
    # --------------------

    # Name of chemical
    name = Unicode()

    # Role of chemical in formulation
    role = Enum(
        "Polyol",
        "Isocyanate",
        "Catalyst",
        "Surfactant",
        "Solvent",
        "Blowing Agent",
    )

    # Molecular weight of chemical in g/mol
    molecular_weight = Float()

    # Density in kg/m3
    density = Float()

    # Price of chemical in USD/kg
    price = Float()

    # --------------------
    #  Regular Attributes
    # --------------------

    #: Molarity of active chemical in formulation, number of
    #: OH groups in polyol, or NCO groups in isocyanate
    functionality = Float(default_value=1)

    # Concentration by mass of chemical in formulation
    concentration = Float()

    # --------------------
    #     Properties
    # --------------------

    # Equivalent weight [g/mol] of chemical, or the molecular weight of
    # chemical active components, taking into account functionality,
    equivalent_weight = Property(
        Float, depends_on="[molecular_weight, functionality]"
    )

    # --------------------
    #      Listeners
    # --------------------

    def _get_equivalent_weight(self):
        return self.molecular_weight / self.functionality

    # --------------------
    #    Public Methods
    # --------------------

    def get_data_values(self):
        """Return a list containing all DataValues stored in class"""

        return [
            DataValue(type="NAME", value=self.name),
            DataValue(type="ROLE", value=self.role),
            DataValue(type="MASS", value=self.molecular_weight),
            DataValue(type="DENSITY", value=self.density),
            DataValue(type="PRICE", value=self.price),
            DataValue(type="CONCENTRATION", value=self.concentration),
        ]
