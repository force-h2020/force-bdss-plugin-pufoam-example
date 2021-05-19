from copy import deepcopy

from force_bdss.utilities import (
    pop_dunder_recursive
)

from traits.api import (
    HasStrictTraits, Unicode, Int, List, Enum, on_trait_change)
from traitsui.api import (
    View, Item, UItem, HGroup, ListEditor, Label, Group)
from force_bdss.api import BaseDataSourceModel, VerifierError


AVAILABLE_GENERATORS = [
    "blockMesh",
    "setFields",
    "PUFoam"
]
AVAILABLE_CASES = [
    "pufoam_example"
]
HOST = "68.183.77.215"
PORT = 81


class SimPUFoamCommand(HasStrictTraits):
    """Represents all instructions for a SimPUFoam command line
    operation
    """

    # SimPUFoam command line operation
    command = Enum(*AVAILABLE_GENERATORS)

    # File to pipe output log into
    log_file = Unicode()

    def default_traits_view(self):
        return View(
            HGroup(
                UItem('command'),
                Label('with log file'),
                UItem('log_file')
            )
        )

    def build_command(self):
        """Builds a string that can be used as a command line
        operation
        """
        command = self.command
        if self.log_file:
            command += f" >& {self.log_file}"
        return command

    def __getstate__(self):
        """Serializes object to dictionary with only key traits"""
        return pop_dunder_recursive(super().__getstate__())


class SimPUFoamModel(BaseDataSourceModel):

    # --------------------
    #  Required Attributes
    # --------------------

    #: Length of simulation run
    time_steps = Int(50)

    #: Make dropdown from listed cases from above
    case_files = Enum(
        *AVAILABLE_CASES,
        desc='Case files to be used for the Simulation'
    )

    #: host to send the cuds object to
    host = Unicode(HOST)

    #: port to send the cuds object to
    port = Int(PORT)

    #: Edit number of generators/solvers which shall be executed
    n_commands = Int(
        3,
        desc='Number of generators/solvers to execute for the simulation case',
        verify=True
    )

    #: Make list of dropdowns refering to n_commands
    commands = List(
        SimPUFoamCommand,
        desc='Commands to be executed to run the simulation case'
    )

    #: Edit number of output files which shall be regarded
    n_outputs = Int(
        1,
        desc='Number of output files to regard for the post-processing',
        verify=True
    )

    #: Make list of output files which will be regarded for post-processing
    outputs = List(
        Unicode,
        desc='Output files to regard for post-processing'
    )

    # ------------------
    #     Defaults
    # ------------------

    def _commands_default(self):
        return [SimPUFoamCommand()] * self.n_commands

    def _outputs_default(self):
        return [str()] * self.n_outputs

    # ------------------
    #     Listeners
    # ------------------

    @on_trait_change('n_commands')
    def update_commands(self):
        """Updates length of commands list to equal
        n_commands"""

        n = self.n_commands - len(self.commands)

        if n > 0:
            self.commands += [SimPUFoamCommand()] * n
        elif n < 0:
            self.commands = self.commands[:n]

    @on_trait_change('n_outputs')
    def update_outputs(self):
        """Updates length of outputs list to equal
        n_outputs"""

        n = self.n_outputs - len(self.outputs)

        if n > 0:
            self.outputs += [str()] * n
        elif n < 0:
            self.outputs = self.outputs[:n]

    # ------------------
    #   Private Methods
    # ------------------

    def _n_commands_check(self):
        """Makes sure there is at least 1 executable in
        the DataSource"""

        errors = []
        if self.n_commands < 1:
            errors.append(
                VerifierError(
                    subject=self,
                    local_error="Number of generators/solvers must"
                                " be at least 1",
                    global_error="An SimPUFoamDataSource does not "
                                 "have enough generators/solvers defined"
                )
            )

        return errors

    def _n_outputs_check(self):
        """Makes sure there is at least 1 output file in
        the DataSource"""

        errors = []
        if self.n_outputs < 1:
            errors.append(
                VerifierError(
                    subject=self,
                    local_error="Number of output files must"
                                " be at least 1",
                    global_error="An SimPUFoamDataSource does not "
                                 "have enough output files defined"
                )
            )

        return errors

    # --------------------
    #    Public Methods
    # --------------------

    def build_commands(self):
        """Builds a list of string commands that can be used as
        SimPUFoam operations"""
        return [
            command.build_command()
            for command in self.commands
        ]

    @classmethod
    def from_json(cls, factory, json_data):
        """Overloads parent method to instantiate SimPuFoamCommand objects
        from serialised json
        """
        data = deepcopy(json_data)

        if "commands" in data:
            data["commands"] = [
                SimPUFoamCommand(**traits)
                for traits in data["commands"]
            ]

        return super(SimPUFoamModel, cls).from_json(factory, data)

    def verify(self):
        """Overloads BaseDataSourceModel verify method to check the
        number of commands and outfiles during a verify_workflow_event"""

        errors = super(SimPUFoamModel, self).verify()
        errors += self._n_commands_check()
        errors += self._n_outputs_check()

        return errors

    # ------------------
    #       View
    # ------------------

    def default_traits_view(self):
        """Provides view with display information for commands
        trait"""
        command_editor = ListEditor(mutable=False, style="custom")
        output_editor = ListEditor(mutable=False)
        return View(
            Group(
                Item('case_files'),
                Item('time_steps'),
                Item('host'),
                Item('port'),
                label='General'
            ),
            Group(
                Item('n_commands'),
                Item('commands', editor=command_editor),
                label='Generators/Solvers'
            ),
            Group(
                Item('n_outputs'),
                Item('outputs', editor=output_editor),
                label='Output files'
            )
        )
