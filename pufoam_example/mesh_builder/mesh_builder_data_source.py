from force_bdss.api import BaseDataSource, DataValue, Slot

from osp.wrappers.gmsh_wrapper.gmsh_engine import (
    RectangularMesh, CylinderMesh, ComplexMesh
)


class MeshBuilderDataSource(BaseDataSource):
    """Class pre-processes a domain mesh for an OpenFOAM simulation
    """

    def create_cylinder_mesh(self, model):
        """Placeholder for a function that builds a cylindrical
        mesh for an OpenFOAM simulation
        """
        mesh = CylinderMesh(
            units=model.units,
            radius=model.radius,
            height=model.height,
            resolution=model.resolution
        )
        return mesh

    def create_rectangular_mesh(self, model):
        """Placeholder for a function that builds a rectangular
        mesh for an OpenFOAM simulation"""

        mesh = RectangularMesh(
            units=model.units,
            length=model.length,
            width=model.width,
            height=model.height,
            resolution=model.resolution
        )
        return mesh

    def create_complex_mesh(self, model):
        """Placeholder for a function that stores the link
        to an .stl-file for an OpenFOAM simulation
        """

        mesh = ComplexMesh(
            units=model.units,
            resolution=model.resolution,
            source_path=model.path,
            inside_location=model.inside_location
        )
        return mesh

    def run(self, model, parameters):

        if model.mesh_type == 'Rectangular':
            mesh = self.create_rectangular_mesh(model)
        elif model.mesh_type == "Cylinder":
            mesh = self.create_cylinder_mesh(model)
        else:
            mesh = self.create_complex_mesh(model)

        return [DataValue(type="MESH", value=mesh)]

    def slots(self, model):
        return ((), (Slot(type="MESH", description="OpenFOAM Domain mesh"),))
