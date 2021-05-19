import os
from unittest import TestCase
from tempfile import TemporaryDirectory

from pufoam_example.pufoam_simulation.pufoam_data.snappy_hex_mesh_data import (
    SnappyHexMeshData)
from osp.wrappers.gmsh_wrapper.gmsh_engine import extent
from pufoam_example.tests.fixtures import fixtures_path


class TestSnappyHexMeshData(TestCase):
    control_file_path = fixtures_path.get("snappyHexMeshDict")

    def setUp(self):
        self.data_dict = SnappyHexMeshData()

    def test_update_stl_data(self):
        stl_extent = extent([-1]*3, [1]*3)
        location = [100, 55, -3]

        surface_dict = self.data_dict.data['geometry']
        controls_dict = self.data_dict.data['castellatedMeshControls']

        self.data_dict.update_stl_data(stl_extent, location)
        surface_dict = self.data_dict.data['geometry']
        controls_dict = self.data_dict.data['castellatedMeshControls']
        self.assertListEqual(
            [-1, -1, -1], surface_dict["refinementBox"]["min"]
        )
        self.assertListEqual(
            [1, 1, 1], surface_dict["refinementBox"]["max"]
        )
        self.assertListEqual(controls_dict['locationInMesh'], location)

    def test_write_file(self):

        with TemporaryDirectory() as temp_dir:
            self.data_dict.write_to_file(path=temp_dir)

            file_path = os.path.join(
                temp_dir, self.data_dict.file_localpath
            )

            with open(self.control_file_path) as control_file:
                control_data = control_file.readlines()
            with open(file_path) as test_file:
                test_data = test_file.readlines()

            # Update control_data info with location of temporary file used
            # for testing
            control_data[5] = test_data[5]
            self.assertEqual(control_data, test_data)
