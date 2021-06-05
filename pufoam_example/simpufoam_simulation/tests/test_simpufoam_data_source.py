from unittest import TestCase

from pufoam_example.tests.probe_classes import ProbeFormulation
from pufoam_example.SimPhonyUtils import CudsBuilder, CudsFinder
from pufoam_example.simpufoam_simulation.simpufoam_factory import (
    SimPUFoamFactory)
from pufoam_example.simpufoam_simulation.simpufoam_model import (
    SimPUFoamModel, SimPUFoamCommand)


class TestSimPUFoamDataSource(TestCase):

    def setUp(self):
        self.factory = SimPUFoamFactory(
            plugin={'id': '0', 'name': 'test'})
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()
        self.cuds = CudsBuilder("OPEN_FOAM_DATA")

    def test_model_getstate(self):
        state = self.model.__getstate__()
        commands_state = state['model_data']['commands']
        self.assertEqual(3, len(commands_state))

        # Assert default values are correctly serialized
        for command_state in commands_state:
            self.assertDictEqual(
                {'command': 'blockMesh', 'log_file': ''},
                command_state
            )

    def test_from_json(self):
        json_data = {'n_commands': 1,
                     'commands': [{'command': 'PUFoam',
                                   'log_file': 'someLog'}],
                     'input_slot_info': [],
                     'output_slot_info': [],
                     }
        model = SimPUFoamModel.from_json(self.factory, json_data)
        self.assertEqual(1, len(model.commands))

        command = model.commands[0]
        self.assertIsInstance(command, SimPUFoamCommand)
        self.assertEqual('PUFoam', command.command)
        self.assertEqual('someLog', command.log_file)

    def test_update_kinetic_data(self):

        formulation = ProbeFormulation()

        self.data_source.update_kinetic_data(self.cuds, formulation)

        mapping = {
            "initCOH": formulation.polyols,
            "initCNCO": formulation.isocyanates,
            "initCW": formulation.solvents
        }

        for key, value in mapping.items():
            test_conc = formulation.group_molar_concentration(value)
            conc = CudsFinder(self.cuds, key)
            self.assertEqual(test_conc, conc.float_value)

    def test_update_mesh_data(self):
        class DummyMesh:
            resolution = 10

        self.data_source.update_mesh_data(self.cuds, DummyMesh())

        n_cells = CudsFinder(self.cuds, "cell_numbers")
        self.assertListEqual([10, 20, 1], list(n_cells.int_vector))

    def test_update_reaction_data(self):

        gelling_reaction = {
            "A_OH": 10, "E_OH": 5, "deltaOH": 1, "gellingPoint": 2.5
        }
        blowing_reaction = {
            "A_W": 10, "E_W": 5, "deltaW": 1, "latentHeat": 2.5
        }

        self.data_source.update_reaction_data(self.cuds, gelling_reaction)
        self.data_source.update_reaction_data(self.cuds, blowing_reaction)

        mapping = {**gelling_reaction, **blowing_reaction}
        for key, value in mapping.items():
            self.assertEqual(
                value,
                CudsFinder(
                    self.cuds, key
                ).float_value
            )

    def test_update_tmax(self):
        new_val = 1

        self.data_source.update_t_max(self.cuds, new_val)

        tmax = CudsFinder(self.cuds, "endTime")
        self.assertEqual(new_val, tmax.float_value)
