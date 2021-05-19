from unittest import TestCase

from force_bdss.api import DataValue

from pufoam_example.reaction_parameters.reaction_parameters_factory import (
    ReactionParametersFactory
)


class TestReactionParameters(TestCase):

    def setUp(self):
        self.factory = ReactionParametersFactory(
            plugin={'id': '0', 'name': 'Test'})
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()

    def test_basic_function(self):

        self.model.nu_gelling = 0.5
        self.model.E_a_gelling = 1.0
        self.model.delta_H_gelling = 5.0
        self.model.gelling_point = 1.5
        self.model.nu_blowing = 2.0
        self.model.E_a_blowing = 4.0
        self.model.delta_H_blowing = 12.0
        self.model.latent_heat = 10.0

        data_values = []
        res = self.data_source.run(self.model, data_values)

        self.assertEqual("REACTION", res[0].type)
        self.assertEqual("REACTION", res[1].type)
        self.assertEqual(0.5, res[0].value['A_OH'])
        self.assertEqual(1.0, res[0].value['E_OH'])
        self.assertEqual(5.0, res[0].value['deltaOH'])
        self.assertEqual(1.5, res[0].value['gellingPoint'])
        self.assertEqual(2.0, res[1].value['A_W'])
        self.assertEqual(4.0, res[1].value['E_W'])
        self.assertEqual(12.0, res[1].value['deltaW'])
        self.assertEqual(10.0, res[1].value['latentHeat'])

        self.model.input_method = 'Parameter'
        data_values = [
            DataValue(value=[0.5, 1.0, 5.0, 1.5]),
            DataValue(value=[2.0, 4.0, 12.0, 10.0])
        ]
        res = self.data_source.run(self.model, data_values)

        self.assertEqual("REACTION", res[0].type)
        self.assertEqual("REACTION", res[1].type)
        self.assertEqual(0.5, res[0].value['A_OH'])
        self.assertEqual(1.0, res[0].value['E_OH'])
        self.assertEqual(5.0, res[0].value['deltaOH'])
        self.assertEqual(1.5, res[0].value['gellingPoint'])
        self.assertEqual(2.0, res[1].value['A_W'])
        self.assertEqual(4.0, res[1].value['E_W'])
        self.assertEqual(12.0, res[1].value['deltaW'])
        self.assertEqual(10.0, res[1].value['latentHeat'])

    def test_changes_slots(self):
        slots = self.data_source.slots(self.model)
        self.assertEqual(0, len(slots[0]))
        self.assertEqual(2, len(slots[1]))

        self.model.input_method = 'Parameter'
        slots = self.data_source.slots(self.model)
        self.assertEqual(2, len(slots[0]))
        self.assertEqual(2, len(slots[1]))
