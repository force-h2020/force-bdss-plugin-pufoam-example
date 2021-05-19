from unittest import TestCase

from pufoam_example.mesh_builder.mesh_builder_factory import (
    MeshBuilderFactory)
from osp.wrappers.gmsh_wrapper.gmsh_engine import (
    RectangularMesh, CylinderMesh
)


class TestMeshBuilder(TestCase):

    def setUp(self):
        self.factory = MeshBuilderFactory(plugin={'id': '0', 'name': 'test'})
        self.data_source = self.factory.create_data_source()

    def test_basic_function(self):

        model = self.factory.create_model()

        slots = self.data_source.slots(model)

        self.assertEqual(2, len(slots))

        data_values = []
        res = self.data_source.run(model, data_values)
        self.assertEqual("MESH", res[0].type)

        mesh = res[0].value
        self.assertIsInstance(mesh, RectangularMesh)
        self.assertEqual('cm', mesh.units)
        self.assertEqual(5, mesh.length)
        self.assertEqual(10, mesh.width)
        self.assertEqual(20, mesh.height)
        self.assertEqual(5, mesh.resolution)

        model.mesh_type = 'Cylinder'
        res = self.data_source.run(model, data_values)
        self.assertEqual("MESH", res[0].type)

        mesh = res[0].value
        self.assertIsInstance(mesh, CylinderMesh)
        self.assertEqual('cm', mesh.units)
        self.assertEqual(5, mesh.radius)
        self.assertEqual(20, mesh.height)
