from unittest import TestCase

import numpy as np

from pufoam_example.pufoam_plugin import PUFoamPlugin
from pufoam_example.mco.mco import parameter_grid_generator


class TestMCO(TestCase):

    def assertArrayAlmostEqual(self, array_1, array_2):
        self.assertTrue(np.allclose(array_1, array_2))

    def setUp(self):
        self.plugin = PUFoamPlugin()
        self.factory = self.plugin.mco_factories[0]
        self.mco = self.factory.create_optimizer()
        self.model = self.factory.create_model()

        self.parameters = [
            self.factory.parameter_factories[0].create_model(
                data_values={'value': 12.0}
            ),
            self.factory.parameter_factories[1].create_model(
                data_values={'levels': [0.1, 2.5]}
            ),
            self.factory.parameter_factories[2].create_model(
                data_values={'upper_bound': 1.5, 'n_samples': 2}
            ),
            self.factory.parameter_factories[3].create_model(
                data_values={'dimension': 2,
                             'upper_bound': [1, 2],
                             'lower_bound': [0, 0],
                             'initial_value': [0, 0],
                             'n_samples': 2}
            )
        ]

    def test_parameter_grid_generator(self):
        expected = [
            (12, 0.1, 0.1, [0, 0]),
            (12, 0.1, 0.1, [0, 2.0]),
            (12, 0.1, 0.1, [1.0, 0.0]),
            (12, 0.1, 0.1, [1.0, 2.0]),
            (12, 0.1, 1.5, [0, 0]),
            (12, 0.1, 1.5, [0, 2.0]),
            (12, 0.1, 1.5, [1.0, 0.0]),
            (12, 0.1, 1.5, [1.0, 2.0]),
            (12, 2.5, 0.1, [0, 0]),
            (12, 2.5, 0.1, [0, 2.0]),
            (12, 2.5, 0.1, [1.0, 0.0]),
            (12, 2.5, 0.1, [1.0, 2.0]),
            (12, 2.5, 1.5, [0, 0]),
            (12, 2.5, 1.5, [0, 2.0]),
            (12, 2.5, 1.5, [1.0, 0.0]),
            (12, 2.5, 1.5, [1.0, 2.0]),
        ]

        for index, parameter in enumerate(
                parameter_grid_generator(self.parameters)
        ):
            self.assertEqual(expected[index][:2], parameter[:2])
            self.assertAlmostEqual(expected[index][-2], parameter[-2])
            self.assertArrayAlmostEqual(expected[index][-1], parameter[-1])
