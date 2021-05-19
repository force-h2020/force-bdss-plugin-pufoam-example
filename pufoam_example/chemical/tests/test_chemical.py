from unittest import TestCase

from force_bdss.api import DataValue

from pufoam_example.chemical import Chemical
from pufoam_example.chemical.chemical_factory import ChemicalFactory


class TestChemicalDataSource(TestCase):
    def setUp(self):
        self.factory = ChemicalFactory(plugin={'id': '0', 'name': 'test'})
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()

    def test_basic_function(self):

        self.model.name = "Water"
        self.model.role = "Solvent"
        self.model.price = 2.0
        self.model.molecular_weight = 18.0
        self.model.density = 1.0

        res = self.data_source.run(self.model, [])
        self.assertEqual("CHEMICAL", res[0].type)

        chemical = res[0].value
        self.assertEqual("Water", chemical.name)
        self.assertEqual("Solvent", chemical.role)
        self.assertEqual(2.0, chemical.price)
        self.assertEqual(18.0, chemical.molecular_weight)
        self.assertEqual(1.0, chemical.density)
        self.assertEqual(1, chemical.functionality)

        self.model.conc_input = 'Parameter'
        data_values = [DataValue(value=100)]
        res = self.data_source.run(self.model, data_values)
        chemical = res[0].value
        self.assertEqual(100, chemical.concentration)

    def test__property_check(self):

        self.model.role = "Solvent"
        self.model.density = -1
        errors = self.model._property_check(
            "Solvent", self.model.density, "Test local error",
            global_error="Test global error")

        self.assertEqual(1, len(errors))
        self.assertEqual("Test local error", errors[0].local_error)
        self.assertEqual("Test global error", errors[0].global_error)

    def test_init_polyol(self):

        self.model.name = "A Polyol"
        self.model.role = "Polyol"
        self.model.price = 10.0
        self.model.molecular_weight = 25.0
        self.model.density = 1.0

        data_values = []
        res = self.data_source.run(self.model, data_values)
        chemical = res[0].value

        self.assertEqual("A Polyol", chemical.name)
        self.assertEqual("Polyol", chemical.role)
        self.assertEqual(10.0, chemical.price)
        self.assertEqual(25.0, chemical.molecular_weight)
        self.assertEqual(1.0, chemical.density)

    def test_changes_slots(self):
        slots = self.data_source.slots(self.model)
        self.assertEqual(0, len(slots[0]))
        self.assertEqual(1, len(slots[1]))

        self.model.conc_input = 'Parameter'
        slots = self.data_source.slots(self.model)
        self.assertEqual(1, len(slots[0]))
        self.assertEqual(1, len(slots[1]))


class TestChemical(TestCase):
    def setUp(self):
        name = "Water"
        role = "Solvent"
        molecular_weight = 18.0
        price = 2.0
        density = 1.1

        self.chemical = Chemical(
            name=name,
            role=role,
            molecular_weight=molecular_weight,
            price=price,
            density=density,
        )

    def test___init__(self):

        self.assertEqual("Water", self.chemical.name)
        self.assertEqual("Solvent", self.chemical.role)
        self.assertEqual(2.0, self.chemical.price)
        self.assertEqual(18.0, self.chemical.molecular_weight)
        self.assertEqual(1.1, self.chemical.density)

    def test_get_data_values(self):

        data = self.chemical.get_data_values()

        self.assertEqual("Water", data[0].value)
        self.assertEqual("NAME", data[0].type)
        self.assertEqual("Solvent", data[1].value)
        self.assertEqual("ROLE", data[1].type)
        self.assertEqual(18.0, data[2].value)
        self.assertEqual("MASS", data[2].type)
        self.assertEqual(1.1, data[3].value)
        self.assertEqual("DENSITY", data[3].type)
        self.assertEqual(2.0, data[4].value)
        self.assertEqual("PRICE", data[4].type)

    def test_molecular_weight(self):

        self.assertEqual(
            self.chemical.molecular_weight, self.chemical.equivalent_weight
        )
        self.chemical.functionality = 2
        self.assertEqual(
            self.chemical.molecular_weight, self.chemical.equivalent_weight * 2
        )
