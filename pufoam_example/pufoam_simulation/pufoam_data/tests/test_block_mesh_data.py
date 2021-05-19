import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pufoam_example.pufoam_simulation.pufoam_data.block_mesh_data import (
    BlockMeshData)
from osp.wrappers.gmsh_wrapper.gmsh_engine import extent
from pufoam_example.tests.fixtures import fixtures_path


class TestMeshData(TestCase):

    control_file_path = fixtures_path.get("blockMeshDict")

    def setUp(self):
        self.data_dict = BlockMeshData()

    def test_write_file(self):

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
            control_data = "".join(control_data).replace(" ", "")
            test_data = "".join(test_data).replace(" ", "")
            self.assertEqual(control_data, test_data)

    def test_update_data(self):
        is_updated = self.data_dict.update_data(
            "boundary.Wall.type", "not_a_wall"
        )
        self.assertTrue(is_updated)
        self.assertEqual(
            "not_a_wall", self.data_dict.data["boundary"][0]["Wall"]["type"]
        )

        is_updated = self.data_dict.update_data(
            "boundary.atmosphere.type", "not_a_patch"
        )
        self.assertTrue(is_updated)
        self.assertEqual(
            "not_a_patch",
            self.data_dict.data["boundary"][0]["atmosphere"]["type"],
        )
        self.assertEqual(
            "not_a_wall", self.data_dict.data["boundary"][0]["Wall"]["type"]
        )

        is_updated = self.data_dict.update_data(
            "mergePatchPairs.not_a_label", 42
        )
        self.assertFalse(is_updated)

    def test_update_mesh_dimensions(self):
        blockmesh_extent = extent([0, 0, 0], [5, 10, 20])
        self.data_dict.update_mesh_dimensions(blockmesh_extent)
        for ax in blockmesh_extent.keys():
            for direction in blockmesh_extent[ax].keys():
                self.assertEqual(
                    self.data_dict.data[ax+direction],
                    blockmesh_extent[ax][direction]
                )
