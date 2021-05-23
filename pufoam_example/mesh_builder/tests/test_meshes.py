import os
from tempfile import TemporaryDirectory
from unittest import TestCase
import warnings

import numpy as np

from osp.wrappers.gmsh_wrapper.gmsh_engine import (
    RectangularMesh, CylinderMesh, ComplexMesh, extent
)
from pufoam_example.tests.fixtures.fixtures_path import get


class TestMeshes(TestCase):

    def setUp(self):
        # Define rectangular mesh and its properties
        self.rectangular = RectangularMesh(
            x_length=20,
            y_length=10,
            z_length=150,
            resolution=4,
            filling_fraction=0.5,
            units="mm"
        )
        self.rectangular_block_extent = extent(
            max_extent=[20, 10, 150]
        )
        self.rectangular_filling_extent = [
            [0, 0, 0], [0.02, 0.01, 0.075]
        ]
        self.rectangular_ncells = [80, 40, 600]
        self.rectangular_volume = 30000

        # Define cylindrical mesh and its properties
        self.cylinder = CylinderMesh(
            xy_radius=5,
            z_length=20,
            resolution=7,
            filling_fraction=0.5,
            units="cm"
        )
        self.cylinder_stl_extent = extent(
            [-0.05, -0.05, 0], [0.05, 0.05, 0.2]
        )
        self.cylinder_block_extent = extent(
            [-5, -5, 0], [5, 5, 20]
        )
        self.cylinder_filling_extent = [0.05, 0.1]
        self.cylinder_ncells = [70, 70, 140]
        self.cylinder_location = [0, 0, 0.1]
        self.cylinder_volume = 25*20*np.pi

        # Define complex mesh and its properties
        self.complex_radius = 5
        self.complex_height = 10
        self.complex_resolution = 10
        self.complex = ComplexMesh(
            source_path=get("cone.stl"),
            inside_location=[0, 0, 5],
            resolution=10,
            filling_fraction=0.5,
            units="cm"
        )
        self.complex_stl_extent = extent(
            [-0.05, -0.05, 0], [0.05, 0.05, 0.1]
        )
        self.complex_block_extent = extent(
            [-5, -5, 0], [5, 5, 10]
        )
        self.complex_filling_extent = [
            [-0.05, -0.05, 0], [0.05, 0.05, 0.05]
        ]
        self.complex_ncells = [100, 100, 100]
        self.complex_location = [0, 0, 0.05]
        self.complex_cutoff = 0.5
        self.complex_volume = 1/3*(
            np.pi*self.complex_radius**2*self.complex_height
        )
        self.complex_volume_cutoff = 1/3*(
            self.complex_radius*(1-self.complex_cutoff)
        )**2*np.pi*(self.complex_height*self.complex_cutoff)

    def test_rectangular(self):
        self.rectangular.write_mesh()
        for ax in self.rectangular_block_extent.keys():
            for direction in self.rectangular_block_extent[ax].keys():
                self.assertEqual(
                    self.rectangular.blockmesh_extent[ax][direction],
                    self.rectangular_block_extent[ax][direction]
                )
        self.assertListEqual(
            self.rectangular.ncells,
            self.rectangular_ncells
        )
        self.assertListEqual(
            self.rectangular_filling_extent,
            self.rectangular.filling_extent
        )
        self.assertEqual(
            self.rectangular_volume,
            self.rectangular.volume
        )

    def test_cylinder(self):
        with TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'new_surface.stl')
            self.cylinder.write_mesh(temp_dir)
            self.assertTrue(os.path.exists(file_path))
            for ax in self.cylinder_stl_extent.keys():
                for direction in self.cylinder_stl_extent[ax].keys():
                    self.assertEqual(
                        self.cylinder.stl_extent[ax][direction],
                        self.cylinder_stl_extent[ax][direction]
                    )
                    self.assertEqual(
                        self.cylinder.blockmesh_extent[ax][direction],
                        self.cylinder_block_extent[ax][direction]
                    )
            self.assertListEqual(
                self.cylinder.ncells,
                self.cylinder_ncells
            )
            self.assertListEqual(
                self.cylinder.inside_location,
                self.cylinder_location
            )
            self.assertListEqual(
                self.cylinder_filling_extent,
                self.cylinder.filling_extent
            )
            self.assertAlmostEqual(
                self.cylinder_volume,
                self.cylinder.volume,
                places=1
            )

    def test_complex(self):
        warnings.warn(
                "The destinction between true and "
                "apparent filling_fractions is currently "
                "not supported for ComplexMesh-geometries"
        )
        # NOTE: in case that ComplexMesh::cutoff_volume() will
        # deliver reasonable values in the future, please uncomment
        # the following code:
        # self.assertAlmostEqual(
        #    self.complex_volume_cutoff,
        #    self.complex.cutoff_volume(self.complex_cutoff),
        #    delta=3
        # )
        with TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'new_surface.stl')
            self.complex.write_mesh(temp_dir)
            self.assertTrue(os.path.exists(file_path))
            for ax in self.complex_stl_extent.keys():
                for direction in self.complex_stl_extent[ax].keys():
                    self.assertAlmostEqual(
                        self.complex.stl_extent[ax][direction],
                        self.complex_stl_extent[ax][direction],
                    )
                    self.assertAlmostEqual(
                        self.complex.blockmesh_extent[ax][direction],
                        self.complex_block_extent[ax][direction]
                    )
            self.assertListEqual(
                self.complex.ncells,
                self.complex_ncells
            )
            self.assertListEqual(
                self.complex.inside_location,
                self.complex_location
            )
            self.assertListEqual(
                self.complex.filling_extent,
                self.complex_filling_extent
            )
            self.assertAlmostEqual(
                self.complex_volume,
                self.complex.volume,
                delta=3
            )
