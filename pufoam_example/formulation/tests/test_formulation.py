from unittest import TestCase

from force_bdss.api import DataValue

from pufoam_example.pufoam_plugin import PUFoamPlugin
from pufoam_example.tests.probe_classes import (
    probe_chemicals,
    ProbeFormulation,
)


class TestFormulation(TestCase):
    def setUp(self):
        self.formulation = ProbeFormulation()

    def test___init__(self):

        self.assertEqual(1, len(self.formulation.polyols))
        self.assertEqual(1, len(self.formulation.isocyanates))
        self.assertEqual(1, len(self.formulation.solvents))
        self.assertEqual(1, len(self.formulation.blowing_agents))
        self.assertEqual(1, len(self.formulation.surfactants))
        self.assertEqual(1, len(self.formulation.catalysts))

        self.assertAlmostEqual(1.00503, self.formulation.iso_index, 5)
        self.assertAlmostEqual(2.23129, self.formulation.density, 5)

    def test_iso_index(self):
        self.assertAlmostEqual(1.005025, self.formulation.iso_index, places=5)

    def test_set_iso_index(self):
        target_index = 2.0
        old_index = self.formulation.iso_index
        old_concentration = self.formulation.isocyanates[0].concentration
        self.formulation.iso_index = target_index
        self.assertAlmostEqual(
            target_index / old_index * old_concentration,
            self.formulation.isocyanates[0].concentration,
        )
        self.assertAlmostEqual(target_index, self.formulation.iso_index)

    def test_density(self):
        self.assertAlmostEqual(2.23129, self.formulation.density, places=5)

    def test_molar_concentration(self):
        self.assertAlmostEqual(
            1118.44312716,
            self.formulation.group_molar_concentration(
                self.formulation.polyols
            ),
        )

    def test_group_weight_fraction(self):
        self.assertAlmostEqual(
            0.06015037,
            self.formulation.group_weight_fraction(
                self.formulation.polyols
            ),
        )


class TestFormulationDataSource(TestCase):
    def setUp(self):
        self.plugin = PUFoamPlugin()
        self.factory = self.plugin.data_source_factories[1]
        self.data_source = self.factory.create_data_source()
        self.input_values = probe_chemicals()[:4]

    def test_basic_function(self):

        model = self.factory.create_model()
        model.n_chemicals = 4

        in_slots = self.data_source.slots(model)[0]

        self.assertEqual(4, len(in_slots))

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, self.input_values)
        ]

        res = self.data_source.run(model, data_values)

        self.assertEqual("FORMULATION", res[0].type)

    def test_error_handling(self):

        model = self.factory.create_model()
        model.n_chemicals = 4

        values = self.input_values.copy()
        in_slots = self.data_source.slots(model)[0]

        values[1].role = "Polyol"
        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, values)
        ]
        with self.assertRaises(AttributeError):
            self.data_source.run(model, data_values)

        values[0].role = "Isocyanate"
        values[1].role = "Isocyanate"
        values[2].role = "Isocyanate"
        values[3].role = "Isocyanate"
        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, values)
        ]
        with self.assertRaises(AttributeError):
            self.data_source.run(model, data_values)

        values[0].role = "Polyol"
        values[1].role = "Polyol"
        values[2].role = "Isocyanate"
        values[3].role = "Blowing Agent"
        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, values)
        ]
        with self.assertRaises(AttributeError):
            self.data_source.run(model, data_values)

    def test__chemical_check(self):

        model = self.factory.create_model()
        model.n_chemicals = 2
        errors = model.verify()

        messages = [error.local_error for error in errors]
        self.assertIn("Number of Chemicals must be at least 4", messages)
