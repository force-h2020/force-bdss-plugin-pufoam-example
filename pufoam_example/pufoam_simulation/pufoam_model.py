from traits.api import Enum, Str, Int, Float, Bool
from traitsui.api import View, Item, RangeEditor, Group

from force_bdss.api import BaseDataSourceModel, VerifierError


class PUFoamModel(BaseDataSourceModel):

    #: Name of experiment
    name = Str("experiment")

    #: Toggle between input of foam volume fraction or mass (g)
    use_mass = Bool(False)

    #: Whether to toggle initial conditions input as fixed or variable
    #: in the MCO as a parameter
    input_method = Enum(['Model', 'Parameter'], changes_slots=True)

    #: Initial volume fraction of PUFoam in domain if fixed
    foam_volume = Float(0.1)

    #: Initial mass of PUFoam in domain if fixed (g)
    foam_mass = Float(100)

    #: Length of simulation run
    time_steps = Int(100)

    #: File path containing the simulation data files
    simulation_directory = Str(
        desc="Path to the simulation folder"
    )

    #: File path for the simulation output data
    output_file = Str(
        desc="File name to store simulation output data"
    )

    #: This should allow the user to either choose the existing docker
    #: implementation of the PUFoam executable, or provide a custom
    #: command to run the simulation, i.e. with local PUFoam installation
    simulation_executable = Enum(["docker", "custom"])

    #: Name of the docker image used to run the PUFoam simulation
    image_name = Str(
        "registry.gitlab.cc-asp.fraunhofer.de:4567/force/pufoam:latest"
    )

    # Name of Docker container running PUFoam image
    container_name = Str('BDSS_PUFOAM')

    # Host of Docker container running PUFoam image
    host = Str('0.0.0.0')

    # Port used to connect to Docker container running PUFoam image
    port = Int(5000)

    traits_view = View(
        Group(
            Item('input_method'),
            Item("use_mass"),
            Item("foam_volume",
                 editor=RangeEditor(low=0, high=1, is_float=True),
                 visible_when="not use_mass and input_method=='Model'"),
            Item("foam_mass",
                 visible_when="use_mass and input_method=='Model'"),
            label='Initial Conditions'
        ),
        Group(
            Item("time_steps"),
            Item("simulation_directory"),
            Item("output_file"),
            Item("simulation_executable"),
            Item("image_name",
                 visible_when="simulation_executable == 'docker'"),
            Item("container_name",
                 visible_when="simulation_executable == 'docker'"),
            Item("host", visible_when="simulation_executable == 'docker'"),
            Item("port", visible_when="simulation_executable == 'docker'"),
            label='Simulation Parameters'
        )
    )

    def verify(self):
        """Overloads parent method to include check for initial PUFoam
        volume fraction
        """
        errors = super(PUFoamModel, self).verify()

        if self.foam_volume < 0 or self.foam_volume > 1:
            errors.append(
                VerifierError(
                    subject=self,
                    severity='warning',
                    local_error="PuFoam initial volume is not a fraction",
                    global_error=(
                        "PUFoam initial volume must be between 0 - 1"
                    ),
                )
            )

        return errors
