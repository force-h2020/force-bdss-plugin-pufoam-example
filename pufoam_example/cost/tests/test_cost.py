from unittest import TestCase

import numpy as np

from force_bdss.api import DataValue

from pufoam_example.pufoam_plugin import PUFoamPlugin
from pufoam_example.tests.probe_classes import (
    ProbeFormulation
)


class TestCost(TestCase):

    def setUp(self):
        self.plugin = PUFoamPlugin()
        self.factory = self.plugin.data_source_factories[4]
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()

        self.formulation = ProbeFormulation()

    def test_basic_function(self):

        self.model.PU_volume = 12
        self.model.threshold = 500

        in_slots = self.data_source.slots(self.model)[0]

        self.assertEqual(1, len(in_slots))

        values = [self.formulation]

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, values)
        ]

        res = self.data_source.run(self.model, data_values)

        self.assertEqual("COST", res[0].type)
        self.assertEqual("PASS", res[1].type)

        self.assertAlmostEqual(res[0].value, 502646.4, 2)
        self.assertEqual(res[1].value, False)

    def test_concentration_convertor(self):

        volume = 12
        concentrations = [3, 0.5, 2]
        molar_masses = [5, 3, 1]

        masses = self.data_source.concentration_convertor(
            volume, concentrations, molar_masses
        )

        self.assertListEqual([180, 18, 24], list(masses))
        self.assertIsInstance(masses, np.ndarray)

    def test_calculate_cost(self):

        volume = 12
        concentrations = [3, 0.5, 2]
        molar_masses = [5, 3, 1]
        prices = [3, 4, 10]

        cost = self.data_source.calculate_cost(
            volume, prices, concentrations, molar_masses
        )

        self.assertEqual(852, cost)
