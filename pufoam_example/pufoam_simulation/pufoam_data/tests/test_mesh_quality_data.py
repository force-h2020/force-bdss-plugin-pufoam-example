import os
from unittest import TestCase
from tempfile import TemporaryDirectory

from pufoam_example.pufoam_simulation.pufoam_data.mesh_quality_data import (
    MeshQualityData)
from pufoam_example.tests.fixtures import fixtures_path


class TestMeshQualityData(TestCase):
    control_file_path = fixtures_path.get("meshQualityDict")

    def setUp(self):
        self.data_dict = MeshQualityData()

    def test_write_file(self):

        with TemporaryDirectory() as temp_dir:
            self.data_dict.write_to_file(path=temp_dir)

            file_path = os.path.join(
                temp_dir, self.data_dict.file_localpath)

            with open(self.control_file_path) as control_file:
                control_data = control_file.readlines()
            with open(file_path) as test_file:
                test_data = test_file.readlines()

            # Update control_data info with location of temporary file used
            # for testing
            control_data[5] = test_data[5]
            self.assertEqual(control_data, test_data)
