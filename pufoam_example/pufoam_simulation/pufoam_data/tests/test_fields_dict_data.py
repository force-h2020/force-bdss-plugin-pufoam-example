import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pufoam_example.pufoam_simulation.pufoam_data.fields_dict_data import (
    FieldsDictData, field_values_list, format_regions, format_cell_data
)
from pufoam_example.tests.fixtures import fixtures_path


class TestFieldsDictData(TestCase):

    def setUp(self):
        self.control_file_path = fixtures_path.get("setFieldsDict_box")
        self.data_dict = FieldsDictData()

    def test_mesh_type(self):
        self.assertEqual('Box', self.data_dict.mesh_type)
        self.assertEqual('Box', self.data_dict._mesh_type)

        self.data_dict.mesh_type = 'Cylinder'
        self.assertEqual('Cylinder', self.data_dict.mesh_type)
        self.assertEqual('Cylinder', self.data_dict._mesh_type)

        with self.assertRaises(ValueError):
            self.data_dict.mesh_type = 'Not Supported'

    def test_update_box_volume(self):
        extent = [[0, 0, 0], [0.1, 0.2, 0.01]]
        self.data_dict.update_box_volume(extent)

        self.assertListEqual(
            extent[0],
            self.data_dict.regions[0]['boxToCell']['box'][0]
        )
        self.assertListEqual(
            extent[1],
            self.data_dict.regions[0]['boxToCell']['box'][1]
        )

    def test_update_cylinder_volume(self):
        radius = 10
        filling_height = 40

        self.data_dict.update_cylinder_volume(
            [radius, filling_height]
        )

        self.assertEqual(
            filling_height,
            self.data_dict.regions[1]['cylinderToCell']['p2'][-1]
        )
        self.assertEqual(
            radius,
            self.data_dict.regions[1]['cylinderToCell']['radius']
        )

    def test_format_cell_data(self):
        test_box = [[0, 0, 0], [1, 1, 1]]

        self.assertEqual(
            '0',
            format_cell_data(test_box[0][0])
        )
        self.assertEqual(
            '(0 0 0)',
            format_cell_data(test_box[0])
        )
        self.assertEqual(
            '(0 0 0) (1 1 1)',
            format_cell_data(test_box)
        )

    def test_field_values_list(self):
        test_dict = {'key #1': 0, 'key #2': 1}

        self.assertListEqual(
            [["volScalarFieldValue key #1 0"],
             ["volScalarFieldValue key #2 1"]],
            field_values_list(test_dict)
        )

    def test_format_regions(self):
        test_regions = [{
            'Region1': {
                'box': [[0, 0, 0], [1, 1, 1]],
                'fieldValues': {'key #1': 0, 'key #2': 1}
            },
            'Region2': {
                'p1': [0, 0, 0],
                'p2': [0, 0, 20],
                'radius': 150,
                'fieldValues': {'key #1': 0, 'key #2': 1}
            }
        }]

        self.assertDictEqual(
            {
                'regions': [
                    {
                        "Region1": {
                            'box': "(0 0 0) (1 1 1)",
                            'fieldValues': [
                                ["volScalarFieldValue key #1 0"],
                                ["volScalarFieldValue key #2 1"]
                            ]
                        },
                        "Region2": {
                            'p1': "(0 0 0)",
                            'p2': "(0 0 20)",
                            'radius': "150",
                            'fieldValues': [
                                ["volScalarFieldValue key #1 0"],
                                ["volScalarFieldValue key #2 1"]
                            ]
                        }
                    }
                ]
            },
            format_regions(test_regions)
        )

    def test_write_file(self):

        for mesh_type, control_dict in zip(
                ('Box', 'Cylinder'),
                ("setFieldsDict_box", "setFieldsDict_cylinder")
        ):
            self.data_dict.mesh_type = mesh_type
            self.control_file_path = fixtures_path.get(control_dict)
            with TemporaryDirectory() as temp_dir:
                self.data_dict.write_to_file(path=temp_dir)

                file_path = os.path.join(
                    temp_dir, self.data_dict.file_localpath)

                with open(self.control_file_path) as control_file:
                    control_data = control_file.readlines()
                with open(file_path) as test_file:
                    test_data = test_file.readlines()

                # Update control_data info with location of temporary file
                # used for testing
                control_data[5] = test_data[5]
                self.assertEqual(control_data, test_data)
