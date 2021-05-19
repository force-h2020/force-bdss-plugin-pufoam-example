import logging

from traits.api import HasStrictTraits, Float, List, Property, on_trait_change

from pufoam_example.chemical import Chemical


log = logging.getLogger(__name__)


class Formulation(HasStrictTraits):
    """ Polyurethane Foam chemical formulation"""

    # --------------------
    #  Required Attributes
    # --------------------

    #: Chemical ingredients
    chemicals = List(Chemical)

    # ---------------------
    #  Dependent Attributes
    # ---------------------

    #: List of polyol chemicals
    polyols = List(Chemical)

    #: List of isocyanate chemicals
    isocyanates = List(Chemical)

    #: List of surfactant chemicals
    surfactants = List(Chemical)

    #: List of catalyst chemicals
    catalysts = List(Chemical)

    #: List of solvent chemicals
    solvents = List(Chemical)

    #: List of blowing agent chemicals
    blowing_agents = List(Chemical)

    # --------------------
    #      Properties
    # --------------------

    #: Density of the liquid polymer mixture at ambient conditions in [kg m-3].
    #: This is the density of the liquid formulation containing all reactants.
    density = Property(Float, depends_on="chemicals.[density,concentration]")

    #: Isocyanate index (ISO) of formulation
    iso_index = Property(Float, depends_on="chemicals.[concentration]")

    #: Specific heat capacity of formulation in J/kg K
    heat_capacity = Property(Float, depends_on="chemicals")

    #: Averaged molecular weight of the formulation [g/mol]
    mixture_molecular_weight = Property(
        Float, depends_on="chemicals.[concentration,molecular_weight]"
    )

    # --------------------
    #      Listeners
    # --------------------

    def _get_iso_index(self):
        """ Return the formulation ISO index: ratio of isocyanate
        concentrations to non-isocyanate concentrations"""

        isocyanate_concentration = sum(
            [
                chemical.concentration
                for chemical in self.chemicals
                if chemical.role == "Isocyanate"
            ]
        )
        non_isocyanate_concentration = sum(
            [
                chemical.concentration
                for chemical in self.chemicals
                if chemical.role != "Isocyanate"
            ]
        )

        try:
            iso_index = isocyanate_concentration / non_isocyanate_concentration
        except ZeroDivisionError:
            log.error(
                "Can't calculate ISO index of the formulation consisting "
                "only of isocyanate"
            )
            raise

        return iso_index

    def _set_iso_index(self, value):
        """ Set the formulation ISO index to `value` by adjusting the
        concentration(s) of the isocyanate chemicals"""

        if len(self.isocyanates) > 1:
            # If we have multiple entries of isocyanates, we update
            # their concentrations proportionally
            try:
                for chemical in self.isocyanates:
                    chemical.concentration *= value / self.iso_index
            except ZeroDivisionError:
                log.error(
                    "Can't change zero ISO index of the formulation "
                    "consisting of multiple isocyanate chemicals."
                )
            raise
        elif len(self.isocyanates) == 1:
            # If only one isocyanate is present, we calculate the
            # appropriate concentration
            non_isocyanate_concentration = sum(
                [
                    chemical.concentration
                    for chemical in self.chemicals
                    if chemical.role != "Isocyanate"
                ]
            )
            self.isocyanates[0].concentration = (
                non_isocyanate_concentration * value
            )

    def _get_density(self):
        """ Returns total density of formulation based on individual
        chemical densities and their relative concentration by weight."""
        return self.group_density(self.chemicals)

    def _get_mixture_molecular_weight(self):
        return self.group_molecular_weight(self.chemicals)

    def _get_heat_capacity(self):
        """Returns heat capacity of formulation"""
        return 0

    @on_trait_change("chemicals.[role]")
    def _sort_chemicals(self):
        """Updated lists of each chemical role"""
        polyols = []
        isocyanates = []
        solvents = []
        surfactants = []
        catalysts = []
        blowing_agents = []

        for chemical in self.chemicals:
            if chemical.role == "Polyol":
                polyols.append(chemical)
            elif chemical.role == "Isocyanate":
                isocyanates.append(chemical)
            elif chemical.role == "Solvent":
                solvents.append(chemical)
            elif chemical.role == "Surfactant":
                surfactants.append(chemical)
            elif chemical.role == "Catalyst":
                catalysts.append(chemical)
            elif chemical.role == "Blowing Agent":
                blowing_agents.append(chemical)

        self.polyols[:] = polyols
        self.isocyanates[:] = isocyanates
        self.solvents[:] = solvents
        self.surfactants[:] = surfactants
        self.catalysts[:] = catalysts
        self.blowing_agents[:] = blowing_agents

    def _update_functionalities(self):
        pass

    def group_weight_fraction(self, group):
        """Returns total weight fraction of given group"""
        total_concentration = sum(
            chemical.concentration for chemical in self.chemicals
        )
        if total_concentration == 0:
            return 0
        return (
                sum(chemical.concentration for chemical in group) /
                total_concentration
        )

    def group_molar_concentration(self, group):
        """ Calculate the concentration [mol m-3] of *active* components in a
        `group` of chemicals in the formulation. Only accounts for chemicals
        with non-zero molecular weight. The group can be polyols, isocyanates,
        etc., and any combination of those. *Active* refers to components of
        each chemical that is involved in a chemical reaction.

        Example
        ----------
        A polyol with molecular weight of 1000 [g/mol] and functionality of 5,
        is mixed with isocyanate with molecular weight of 500 [g/mol].
        The density of polyol is 1 [g/cm3], and the density of isocyanate is
        1.6 [g/cm3]. The relative mass fraction ("concentration") of the polyol
        is 10, and of the isocyanate is 20. Then, the relative volume per gram
        of the mixture is
            volume = 10 / 1 + 20 / 1.2 = 22.5 [cm3]
        The number of moles of polyol active components per unit weight is
            polyol moles of active component = 10 / (1000 / 5) = 0.05 [mol]
        The molar concentration of polyol active components is
            molar concentration of polyol active components
                = 0.05 / 22.5 = 0.00(2) [mol/cm3] == 2222.(2) [mol/m3]

        Parameters
        ----------
        group: List[Chemical]
            Mix of chemicals
        """
        moles = sum(
            chemical.concentration / chemical.equivalent_weight
            for chemical in group
            if chemical.molecular_weight > 0
        )
        weighted_volume = sum(
            chemical.concentration / chemical.density
            for chemical in self.chemicals
            if chemical.density > 0
        )
        return moles / weighted_volume * 1.0e6

    def group_density(self, group):
        """ Calculates the density of a group of chemicals in kg/m3,
        based on their concentration by weight proportions.

        Parameters
        ----------
        group: List[Chemical]
            Mix of chemicals
        """

        total_concentration = sum(chemical.concentration for chemical in group)

        if total_concentration == 0:
            return 0

        weighted_volume = sum(
            chemical.concentration / chemical.density for chemical in group
        )

        return total_concentration / weighted_volume

    def group_molecular_weight(self, group):
        """ Calculates the average molecular weight of `group` of
        chemicals with *non-zero* molecular weight in formulation.

        Parameters
        ----------
        group: List[Chemical]
            Mix of chemicals
        """

        concentrations = [
            chemical.concentration
            for chemical in group
            if chemical.molecular_weight > 0
        ]
        molecular_weights = [
            chemical.molecular_weight
            for chemical in group
            if chemical.molecular_weight > 0
        ]

        group_mass = sum(concentrations)

        if group_mass == 0:
            return 0

        total_moles = [
            concentration / molecular_weight
            for concentration, molecular_weight in zip(
                concentrations, molecular_weights
            )
        ]

        return group_mass / sum(total_moles)
