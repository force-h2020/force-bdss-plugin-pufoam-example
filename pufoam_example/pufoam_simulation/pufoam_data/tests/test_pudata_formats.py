import os
from unittest import TestCase
from tempfile import TemporaryDirectory

from pufoam_example.pufoam_simulation.pufoam_data.data_format import (
    PUFoamDataDict,
    update_nested_dict,
    instance_of,
    foam_format,
)
from pufoam_example.tests.fixtures import fixtures_path


class TestFoamFormat(TestCase):

    def test_instance_of(self):
        self.assertEqual("dict", instance_of(dict()))
        self.assertEqual("dict", instance_of({1: [{1: []}]}))

        self.assertEqual("list", instance_of([]))
        self.assertEqual("list", instance_of(tuple()))
        self.assertEqual("list", instance_of([1, 2, 3]))

    def test_foam_format_primitives(self):
        # Dict entry
        data = {"a": 1}
        formatted = "{:30}{};".format("a", 1)
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # Multiple dict entries
        data = {"a": 1, "b": 2, "c": 3}
        formatted = "{:30}{};\n{:30}{};\n{:30}{};".format(
            "a", 1, "b", 2, "c", 3
        )
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # Dict group with dict entry
        data = {"a": {"b": 1}}
        formatted = "{}\n{{\n\t{:30}{};\n}}\n".format("a", "b", 1)
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # Dict group with multiple dict entries
        data = {"a": {"b": 1, "c": 2}}
        formatted = "{}\n{{\n\t{:30}{};\n\t{:30}{};\n}}\n".format(
            "a", "b", 1, "c", 2
        )
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # List group with list entry
        data = {"a": [["b", 1]]}
        formatted = "{}\n(\n\t{} {} \n);".format("a", "b", 1)
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # List group with multiple list entries
        data = {"a": [["b", 1], ["c", 2]]}
        formatted = "{}\n(\n\t{} {} \n\t{} {} \n);".format("a", "b", 1, "c", 2)
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # List group with list entry with sequence
        data = {"a": [["b", [1, 2], "c"]]}
        formatted = "{}\n(\n\t{} ({} {}) {} \n);".format("a", "b", 1, 2, "c")
        self.assertEqual(formatted, "\n".join(foam_format(data)))

    def test_foam_format_mixed(self):
        # Dict group with list group with one entry
        data = {"a": {"b": [[1]]}}
        formatted = "{}\n{{\n\t{}\n\t(\n\t\t{} \n\t);\n}}\n".format(
            "a", "b", 1
        )
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # Dict group with a list group with multiple entries
        data = {"a": {"b": [["c", 1], ["d", 2]]}}
        formatted = (
            "{}\n{{\n\t{}\n\t(\n\t\t{} {} \n\t\t{} {} \n\t);\n}}\n"
        ).format("a", "b", "c", 1, "d", 2)
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # Dict group with a dict group with one entry
        data = {"a": {"b": {"c": 1, "d": 2}}}
        formatted = (
            "{}\n{{\n\t{}\n\t{{\n\t\t{}{:30};\n\t\t{}{:30};\n\t}}\n\n}}\n"
        ).format("a", "b", "c", 1, "d", 2)
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # List group with dict entry
        data = {"a": [{"b": 1}]}
        formatted = "{}\n(\n\t{}{:30};\n);".format("a", "b", 1)
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # List group with multiple dict entries
        data = {"a": [{"b": 1, "c": 2}]}
        formatted = "{}\n(\n\t{}{:30};\n\t{}{:30};\n);".format(
            "a", "b", 1, "c", 2
        )
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # List group with dict group with dict entry
        data = {"a": [{"b": {"c": 1}}]}
        formatted = "{}\n(\n\t{}\n\t{{\n\t\t{}{:30};\n\t}}\n\n);".format(
            "a", "b", "c", 1
        )
        self.assertEqual(formatted, "\n".join(foam_format(data)))

        # List group with list group with single entry
        data = {"a": [{"b": [[1]]}]}
        formatted = "{}\n(\n\t{}\n\t(\n\t\t{} \n\t);\n);".format("a", "b", 1)
        self.assertEqual(formatted, "\n".join(foam_format(data)))


class TestUpdateNestedDict(TestCase):
    def setUp(self):
        self.dict = {"a": 1, "b": {"c": 2, "d": 3}, "e": {"f": {"g": 5}}}

    def assert_n_elements(self, dictionary):
        self.assertEqual(3, len(dictionary))
        self.assertEqual(2, len(dictionary["b"]))
        self.assertEqual(1, len(dictionary["e"]))
        self.assertEqual(1, len(dictionary["e"]["f"]))

    def test_update(self):
        update_nested_dict(self.dict, "a", -1)
        self.assertEqual(self.dict["a"], -1)
        self.assert_n_elements(self.dict)

        update_nested_dict(self.dict, "c", -1)
        self.assertEqual(self.dict["b"]["c"], -1)
        self.assert_n_elements(self.dict)

        update_nested_dict(self.dict, "g", -1)
        self.assertEqual(self.dict["e"]["f"]["g"], -1)
        self.assert_n_elements(self.dict)

        self.assertFalse(update_nested_dict(self.dict, "h", -1))
        self.assert_n_elements(self.dict)


class TestPUFoamDataDict(TestCase):
    updates = (
        ("Entry", "new"),
        ("dispersion", -1),
        ("entry_2", -1),
        ("Group", {"new_entry": "new_data"}),
        ("ListGroup", 42),
        ("dict_entry", -41),
    )
    control_file_path = fixtures_path.get("control_file")

    def setUp(self):
        self.data_dict = PUFoamDataDict()
        self.data_dict.data = {
            **self.data_dict.data,
            "Group": {"entry_1": 1, "entry_2": 2},
            "Entry": 42,
            "Group2": {"entry_1": 100, "entry_2": 200},
            "ListGroup": [[1, 2, 3], {"dict_entry": 41}],
        }

    def test_update_by_label(self):
        is_updated = self.data_dict.update_data(*self.updates[0])
        self.assertTrue(is_updated)
        self.assertEqual("new", self.data_dict.data["Entry"])

        is_updated = self.data_dict.update_data(*self.updates[1])
        self.assertFalse(is_updated)

        is_updated = self.data_dict.update_data(*self.updates[2])
        self.assertTrue(is_updated)
        self.assertEqual(-1, self.data_dict.data["Group"]["entry_2"])
        self.assertEqual(200, self.data_dict.data["Group2"]["entry_2"])

        is_updated = self.data_dict.update_data(*self.updates[3])
        self.assertTrue(is_updated)
        self.assertEqual(
            {"new_entry": "new_data"}, self.data_dict.data["Group"]
        )

        is_updated = self.data_dict.update_data(*self.updates[5])
        self.assertTrue(is_updated)
        self.assertEqual(
            -41, self.data_dict.data["ListGroup"][1]["dict_entry"]
        )

        is_updated = self.data_dict.update_data(*self.updates[4])
        self.assertTrue(is_updated)
        self.assertEqual(42, self.data_dict.data["ListGroup"])

    def test_update_by_sequence(self):
        is_updated = self.data_dict.update_data("Group.entry_1", -1)
        self.assertTrue(is_updated)
        self.assertEqual(-1, self.data_dict.data["Group"]["entry_1"])
        self.assertEqual(100, self.data_dict.data["Group2"]["entry_1"])

        is_updated = self.data_dict.update_data("Group2.entry_1", -100)
        self.assertTrue(is_updated)
        self.assertEqual(-1, self.data_dict.data["Group"]["entry_1"])
        self.assertEqual(-100, self.data_dict.data["Group2"]["entry_1"])

        is_updated = self.data_dict.update_data("Group2.entry_3", -100)
        self.assertFalse(is_updated)

    def test_file_location(self):
        self.assertEqual('default', self.data_dict.file_localpath)

        directory = os.path.join("some", "path")

        self.data_dict.data["FoamFile"]["location"] = directory
        self.assertEqual(directory, self.data_dict.file_dir)
        self.assertEqual(
            os.path.join(directory, 'default'),
            self.data_dict.file_localpath
        )

    def test_write_to_file(self):

        with TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, 'temporary')

            self.data_dict.data["FoamFile"]["location"] = temp_file
            self.data_dict.write_to_file()

            with open(self.control_file_path) as control_file:
                control_data = control_file.readlines()
            with open(self.data_dict.file_localpath) as test_file:
                test_data = test_file.readlines()

            # Update control_data info with location of temporary file used
            # for testing
            control_data[5] = test_data[5]
            self.assertListEqual(control_data, test_data)
