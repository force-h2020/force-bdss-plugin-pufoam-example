from pufoam_example.SimPhonyUtils import CudsBuilder, CudsUpdater, SimProcessor
from force_bdss.api import BaseDataSource, Slot, DataValue


class SimPUFoamDataSource(BaseDataSource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, model, parameters):

        cuds = CudsBuilder("OpenFoamData")

        for parameter in parameters:

            if parameter.type == "FORMULATION":
                self.update_kinetic_data(cuds, parameter.value)

            if parameter.type == "MESH":
                self.update_mesh_data(cuds, parameter.value)

            if parameter.type == "REACTION":
                self.update_reaction_data(cuds, parameter.value)

        self.update_t_max(cuds, model.time_steps)

        outputfiles = SimProcessor(cuds, model)
        volFieldvalue = outputfiles[0]

        return [DataValue(type="SIMULATION_OUTPUT",
                value=volFieldvalue)]

    def update_t_max(self, cuds, tmax):
        CudsUpdater(cuds, "endTime", tmax)

    def update_kinetic_data(self, cuds, formulation):
        """ Extracts polyol and isocyan concentrations from the formulation,
        and updates the KineticData dictionary."""

        mapping = {
            "initCOH": formulation.polyols,
            "initCNCO": formulation.isocyanates,
            "initCW": formulation.solvents
        }

        for key, value in mapping.items():
            # Note: blowing agent concentration is entered in as weight
            # fraction, rather than molar concentration
            if key == "initBlowingAgent":
                conc = formulation.group_weight_fraction(value)
            else:
                conc = formulation.group_molar_concentration(value)
            # Note: functionality of water included in equivalent weight need
            # not be taken into account when calculating molar concentrations
            if key == "initCW":
                conc = conc / sum(
                    [solvent.functionality
                     for solvent in formulation.solvents]
                )

            CudsUpdater(cuds, key, conc)

    def update_mesh_data(self, cuds, mesh):
        """ Extracts polyol and isocyan concentrations from the formulation,
        and updates the KineticData dictionary."""

        arg = [mesh.resolution, mesh.resolution * 2, 1]

        CudsUpdater(cuds, "cell_numbers", arg)

    def update_reaction_data(self, cuds, reaction_parameter):
        """Updates KineticData dictionary parameters for either
        gelling or blowing reactions
        """

        for key, value in reaction_parameter.items():
            CudsUpdater(cuds, key, value)

    def slots(self, model):
        """ These slots are placeholders and need to be updated"""
        chemical_slots = (
            Slot(
                description="PU formulation for a simulation",
                type="FORMULATION",
            ),
        )

        reaction_parameter_slots = (
            Slot(description="Gelling reaction parameters", type="REACTION"),
            Slot(description="Blowing reaction parameters", type="REACTION"),
        )

        mesh_slot = (Slot(description="Simulation domain", type="MESH"),)

        return (
            chemical_slots + reaction_parameter_slots + mesh_slot,
            (
                Slot(
                    description="Simulation output data",
                    type="SIMULATION_OUTPUT",
                ),
            ),
        )
