from traits.api import List, Float, Int, Enum, File
from traitsui.api import View, Item

from force_bdss.api import BaseDataSourceModel

SUPPORTED_UNITS = ['mm', 'cm', 'm']
SUPPORTED_MESH_TYPES = ['Rectangular', 'Cylinder', 'Complex']


class MeshBuilderDataSourceModel(BaseDataSourceModel):
    """Class that constructs a domain mesh for an OpenFOAM simulation
    At the moment this is restricted to rectangular geometries for
    testing purposes
    NOTE: For the moment, only integers are supported for the dimensions
    of the domain. This is related to the observations that the solver
    as well as the snappyHexMesh-generator are failing when the extent
    of the blockMesh is heavily disharmonising with the number of cells
    into each direction. In order to work around this issue, the resolution
    shall be proportionally to the dimensions in each direction. Therefore,
    integers for the width, length and height of the blockMesh shall be
    required so that the amount of cells in x-, y- and z-direction
    shall also result into integers as well.
    """

    mesh_type = Enum(SUPPORTED_MESH_TYPES)

    units = Enum('cm', SUPPORTED_UNITS,
                 desc='Unit length for mesh dimensions')

    x_length = Int(5, desc='X-Length of rectangular domain mesh')

    y_length = Int(10, desc='Y-Length of rectangular domain mesh')

    xy_radius = Int(5, desc='Radius of cylinder domain mesh')

    z_length = Int(20, desc='Z-Length of domain mesh')

    resolution = Int(5, desc="Number of mesh elements per unit length")

    path = File(desc='File path to stl-file')

    inside_location = List(
        Float, value=[0, 0, 0], maxlen=3, minlen=3,
        desc="Declare a point within the uploaded geometry"
        " which is inside the desired volume"
    )

    traits_view = View(
        Item('mesh_type'),
        Item('units'),
        Item('x_length', visible_when="mesh_type=='Rectangular'"),
        Item('y_length', visible_when="mesh_type=='Rectangular'"),
        Item('xy_radius', visible_when="mesh_type=='Cylinder'"),
        Item('z_length', visible_when="mesh_type!='Complex'"),
        Item('resolution'),
        Item('path', visible_when="mesh_type=='Complex'"),
        Item('inside_location', visible_when="mesh_type=='Complex'")
    )
