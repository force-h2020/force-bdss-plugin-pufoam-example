from pufoam_example.chemical.chemical_data_source import Chemical
from osp.wrappers.gmsh_wrapper.gmsh_engine import (
    RectangularMesh, CylinderMesh
)


class DummyChemical(Chemical):
    def __init__(self, price=0, mass=0, role="Solvent"):
        super(DummyChemical, self).__init__(
            name="Dummy", role=role, mass=mass, price=price, latent_heat=None
        )


class DummyRectangularMesh(RectangularMesh):

    def __init__(self, *args, **kwargs):
        super().__init__(
            units='cm', x_length=10, y_length=2, z_length=20, resolution=5)


class DummyCylinderMesh(CylinderMesh):

    def __init__(self, *args, **kwargs):
        super().__init__(
            units='cm', base=(0, 0, 0), direction=(0, 0, 1),
            xy_adius=2, z_length=10, resolution=5)
